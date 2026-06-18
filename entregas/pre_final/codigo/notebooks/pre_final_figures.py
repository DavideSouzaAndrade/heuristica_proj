"""Gera figuras de comparação NSGA-II puro vs NSGA-II memetic.

Pré-requisitos:
    python -m src.experiment_moo --instance cp1 --seeds 5 --tag cp2
    python -m src.experiment_moo --instance cp1 --seeds 5 --memetic-period 100 --tag pre_final

Saídas (em entregas/pre_final/figuras/):
    fig1_fronts_compare.png  — fronteiras puro vs memetic por instância (5 painéis)
    fig2_hv_compare.png      — HV vs gerações, puro vs memetic
    fig3_feasibility.png     — viabilidade na fronteira (boxplot), puro vs memetic
    fig4_n20w80_zoom.png     — zoom em n20w80.001: o caso onde D1 mais agrega
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PURE_DIR = ROOT / "entregas" / "cp2" / "resultados"
MEM_DIR = ROOT / "entregas" / "pre_final" / "resultados"
FIG_DIR = ROOT / "entregas" / "pre_final" / "figuras"
FIG_DIR.mkdir(parents=True, exist_ok=True)

INSTANCES = [
    "n20w20.001", "n20w40.001", "n20w60.001",
    "n20w80.001", "n20w100.001",
]


def _load_summary(d: Path, name: str) -> dict:
    return json.loads((d / name / f"{name}_summary.json").read_text())


def _load_fronts(d: Path, name: str) -> dict[str, np.ndarray]:
    npz = np.load(d / name / f"{name}_fronts.npz")
    return {k: npz[k] for k in npz.files}


def _aggregate_nondominated(fronts_seeds: list[np.ndarray]) -> np.ndarray:
    """União dos pontos de várias sementes, filtrada para não-dominados."""
    all_F = np.vstack(fronts_seeds)
    order = np.argsort(all_F[:, 0])
    F_sorted = all_F[order]
    nd = [F_sorted[0]]
    for pt in F_sorted[1:]:
        if pt[1] < nd[-1][1]:
            nd.append(pt)
    return np.array(nd)


# ---------------------------------------------------------------------------
# fig 1 — fronteiras agregadas puro vs memetic
# ---------------------------------------------------------------------------


def fig_fronts_compare() -> None:
    fig, axs = plt.subplots(2, 3, figsize=(13.5, 7.5))
    axs = axs.flatten()

    for ax, name in zip(axs, INSTANCES):
        fronts_pure = _load_fronts(PURE_DIR, name)
        fronts_mem = _load_fronts(MEM_DIR, name)
        agg_pure = _aggregate_nondominated(
            [fronts_pure[f"seed{s}_F"] for s in range(5)])
        agg_mem = _aggregate_nondominated(
            [fronts_mem[f"seed{s}_F"] for s in range(5)])

        ax.plot(agg_pure[:, 0], agg_pure[:, 1], "-o",
                color="#7f8c8d", markersize=4, linewidth=1.5,
                label="NSGA-II puro (CP2)" if name == "n20w20.001" else None)
        ax.plot(agg_mem[:, 0], agg_mem[:, 1], "-o",
                color="#27ae60", markersize=4, linewidth=1.5,
                label="NSGA-II + 2-opt (D1)" if name == "n20w20.001" else None)
        ax.axhline(0, color="green", linestyle=":", linewidth=1, alpha=0.5)

        w = int(name.split("w")[1].split(".")[0])
        ax.set_title(f"{name}  (w≈{w})")
        ax.set_xlabel("distância")
        ax.set_ylabel("violação total")
        ax.grid(True, alpha=0.3)

    axs[-1].axis("off")
    handles, labels = axs[0].get_legend_handles_labels()
    if handles:
        axs[-1].legend(handles, labels, loc="center", fontsize=11,
                       title="Fronteiras agregadas (5 sementes)")

    fig.suptitle(
        "Fronteiras de Pareto: NSGA-II puro vs NSGA-II + 2-opt (memetic)",
        fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_fronts_compare.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# fig 2 — HV vs gerações, puro vs memetic
# ---------------------------------------------------------------------------


def fig_hv_compare() -> None:
    fig, axs = plt.subplots(1, 5, figsize=(16, 3.6), sharey=False)

    for ax, name in zip(axs, INSTANCES):
        hv_pure = np.load(PURE_DIR / name / f"{name}_hv_history.npy")
        hv_mem = np.load(MEM_DIR / name / f"{name}_hv_history.npy")
        x_pure = np.arange(hv_pure.shape[1])
        x_mem = np.arange(hv_mem.shape[1])

        m_pure = hv_pure.mean(axis=0)
        s_pure = hv_pure.std(axis=0, ddof=1)
        m_mem = hv_mem.mean(axis=0)
        s_mem = hv_mem.std(axis=0, ddof=1)

        ax.plot(x_pure, m_pure, color="#7f8c8d", label="puro", linewidth=1.5)
        ax.fill_between(x_pure, m_pure - s_pure, m_pure + s_pure,
                        color="#7f8c8d", alpha=0.15)
        ax.plot(x_mem, m_mem, color="#27ae60", label="memetic", linewidth=1.5)
        ax.fill_between(x_mem, m_mem - s_mem, m_mem + s_mem,
                        color="#27ae60", alpha=0.15)

        w = int(name.split("w")[1].split(".")[0])
        ax.set_title(f"w={w}", fontsize=10)
        ax.set_xlabel("Geração")
        ax.grid(True, alpha=0.3)
        if name == INSTANCES[0]:
            ax.set_ylabel("HV (ref global)")
            ax.legend(loc="lower right", fontsize=9)

    fig.suptitle(
        "Hypervolume vs geração — puro (cinza) vs memetic (verde)",
        fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig2_hv_compare.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# fig 3 — Sementes factíveis e nº soluções factíveis por instância
# ---------------------------------------------------------------------------


def fig_feasibility() -> None:
    widths: list[int] = []
    rate_pure: list[float] = []
    rate_mem: list[float] = []
    n_feas_pure: list[float] = []
    n_feas_mem: list[float] = []

    for name in INSTANCES:
        widths.append(int(name.split("w")[1].split(".")[0]))
        s_pure = _load_summary(PURE_DIR, name)
        s_mem = _load_summary(MEM_DIR, name)
        rate_pure.append(s_pure["feasible_rate"] * 100)
        rate_mem.append(s_mem["feasible_rate"] * 100)
        n_feas_pure.append(s_pure["n_feasible_solutions"]["mean"])
        n_feas_mem.append(s_mem["n_feasible_solutions"]["mean"])

    x = np.arange(len(widths))
    off = 0.2
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    ax1.bar(x - off, rate_pure, width=0.38, color="#7f8c8d", alpha=0.7,
            label="NSGA-II puro (CP2)")
    ax1.bar(x + off, rate_mem, width=0.38, color="#27ae60", alpha=0.75,
            label="NSGA-II + 2-opt (D1)")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"w={w}" for w in widths])
    ax1.set_ylabel("Sementes com fronteira factível (%)")
    ax1.set_ylim(0, 115)
    ax1.legend(loc="lower right")
    ax1.set_title("Robustez da viabilidade")
    ax1.grid(True, axis="y", alpha=0.3)

    ax2.bar(x - off, n_feas_pure, width=0.38, color="#7f8c8d", alpha=0.7,
            label="NSGA-II puro (CP2)")
    ax2.bar(x + off, n_feas_mem, width=0.38, color="#27ae60", alpha=0.75,
            label="NSGA-II + 2-opt (D1)")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"w={w}" for w in widths])
    ax2.set_ylabel("Nº médio de soluções factíveis na fronteira")
    ax2.set_title("Densidade de soluções factíveis")
    ax2.legend(loc="upper right")
    ax2.grid(True, axis="y", alpha=0.3)

    fig.suptitle("Efeito do operador 2-opt sobre a região factível",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_feasibility.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# fig 4 — zoom em n20w80.001
# ---------------------------------------------------------------------------


def fig_n20w80_zoom() -> None:
    name = "n20w80.001"
    fronts_pure = _load_fronts(PURE_DIR, name)
    fronts_mem = _load_fronts(MEM_DIR, name)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)

    for seed in range(5):
        F = fronts_pure[f"seed{seed}_F"]
        o = np.argsort(F[:, 0])
        ax1.plot(F[o, 0], F[o, 1], "-o", markersize=3, linewidth=1,
                 alpha=0.6, label=f"seed {seed}")
        Fm = fronts_mem[f"seed{seed}_F"]
        om = np.argsort(Fm[:, 0])
        ax2.plot(Fm[om, 0], Fm[om, 1], "-o", markersize=3, linewidth=1,
                 alpha=0.6, label=f"seed {seed}")

    for ax, title in zip((ax1, ax2),
                         ("NSGA-II puro (CP2)", "NSGA-II + 2-opt (D1)")):
        ax.axhline(0, color="green", linestyle=":", linewidth=1.2, alpha=0.7)
        ax.set_xlabel("Distância")
        ax.grid(True, alpha=0.3)
        ax.set_title(title)
    ax1.set_ylabel("Violação total")
    ax1.legend(loc="upper right", fontsize=8, title="Por semente")

    fig.suptitle(
        f"{name}: fronteiras por semente — onde o memetic mais agrega",
        fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig4_n20w80_zoom.png", dpi=150)
    plt.close(fig)


def main() -> None:
    fig_fronts_compare()
    print("ok fig1_fronts_compare.png")
    fig_hv_compare()
    print("ok fig2_hv_compare.png")
    fig_feasibility()
    print("ok fig3_feasibility.png")
    fig_n20w80_zoom()
    print("ok fig4_n20w80_zoom.png")


if __name__ == "__main__":
    main()
