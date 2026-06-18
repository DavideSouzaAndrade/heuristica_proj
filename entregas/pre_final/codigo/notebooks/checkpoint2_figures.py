"""Gera as figuras do Checkpoint 2 a partir dos resultados do NSGA-II.

Pré-requisito: ter executado
    python -m src.experiment_moo --instance cp1 --seeds 5 --tag cp2

Saídas (em entregas/cp2/figuras/):
    fig1_pareto.png         — fronteiras de Pareto (5 instâncias) + AG do CP1 sobreposto
    fig2_hypervolume.png    — hypervolume ao longo das gerações (média ± desvio)
    fig3_nsga_vs_ag.png     — zoom em n20w20.001: NSGA-II vs AG-λ
    fig4_front_size.png     — tamanho da fronteira por instância
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

TAG = "cp2"
RUNS_DIR = ROOT / "resultados" / TAG
FIG_DIR = ROOT / "figuras" / TAG
FIG_DIR.mkdir(parents=True, exist_ok=True)
CP1_DIR = ROOT / "entregas" / "cp1" / "resultados"

INSTANCES = [
    "n20w20.001", "n20w40.001", "n20w60.001",
    "n20w80.001", "n20w100.001",
]


def _load_summary(name: str) -> dict:
    return json.loads((RUNS_DIR / name / f"{name}_summary.json").read_text())


def _load_fronts(name: str) -> dict[str, np.ndarray]:
    npz = np.load(RUNS_DIR / name / f"{name}_fronts.npz")
    return {k: npz[k] for k in npz.files}


def _load_ag_cp1(name: str) -> list[dict]:
    """Pontos (dist, viol) das 5 sementes do AG single-objective do CP1."""
    with (CP1_DIR / name / f"{name}_ga.csv").open() as fh:
        return list(csv.DictReader(fh))


# ---------------------------------------------------------------------------
# Figura 1 — fronteiras de Pareto por instância
# ---------------------------------------------------------------------------


def fig_pareto() -> None:
    fig, axs = plt.subplots(2, 3, figsize=(13, 7.5))
    axs = axs.flatten()

    for ax, name in zip(axs, INSTANCES):
        fronts = _load_fronts(name)
        # plota fronteira de cada semente em transparência
        colors_seeds = plt.get_cmap("Blues")(np.linspace(0.35, 0.85, 5))
        for seed, c in enumerate(colors_seeds):
            F = fronts[f"seed{seed}_F"]
            order = np.argsort(F[:, 0])
            ax.plot(F[order, 0], F[order, 1], "-o",
                    color=c, markersize=3, linewidth=1, alpha=0.7,
                    label=f"seed {seed}" if name == "n20w20.001" else None)
        # AG do CP1 (5 pontos)
        ag_points = _load_ag_cp1(name)
        ag_d = [float(r["distance"]) for r in ag_points]
        ag_v = [float(r["violation"]) for r in ag_points]
        ax.scatter(ag_d, ag_v, marker="X", s=80, color="#c0392b",
                   edgecolors="white", linewidths=1, zorder=5,
                   label="AG single-obj (λ=1000)" if name == "n20w20.001" else None)

        w = int(name.split("w")[1].split(".")[0])
        ax.set_title(f"{name}  (w≈{w})")
        ax.set_xlabel("distância")
        ax.set_ylabel("violação total")
        ax.grid(True, alpha=0.3)
        ax.axhline(0, color="green", linestyle=":", linewidth=1, alpha=0.6)

    axs[-1].axis("off")
    # legenda unificada
    handles, labels = axs[0].get_legend_handles_labels()
    if handles:
        axs[-1].legend(handles, labels, loc="center", fontsize=10,
                       title="Fronteira NSGA-II por semente +\nAG λ=1000",
                       title_fontsize=10)

    fig.suptitle("Fronteiras de Pareto (distância × violação) — NSGA-II vs AG",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_pareto.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figura 2 — hypervolume ao longo das gerações
# ---------------------------------------------------------------------------


def fig_hypervolume() -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    colors = plt.get_cmap("viridis")(np.linspace(0.05, 0.85, len(INSTANCES)))
    for name, c in zip(INSTANCES, colors):
        hv = np.load(RUNS_DIR / name / f"{name}_hv_history.npy")
        mean = hv.mean(axis=0)
        std = hv.std(axis=0, ddof=1) if hv.shape[0] > 1 else np.zeros_like(mean)
        x = np.arange(mean.size)
        w = int(name.split("w")[1].split(".")[0])
        ax.plot(x, mean, color=c, label=f"w={w}", linewidth=1.6)
        ax.fill_between(x, mean - std, mean + std, color=c, alpha=0.15)
    ax.set_xlabel("Geração")
    ax.set_ylabel("Hypervolume (ponto-ref global por instância)")
    ax.set_title("Evolução do hypervolume do NSGA-II — média ± desvio sobre 5 sementes")
    ax.legend(title="Largura janela", loc="lower right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig2_hypervolume.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figura 3 — zoom NSGA-II vs AG em n20w20.001
# ---------------------------------------------------------------------------


def fig_nsga_vs_ag() -> None:
    name = "n20w20.001"
    fronts = _load_fronts(name)
    ag_points = _load_ag_cp1(name)

    # fronteira agregada: união de todas as sementes, fica não-dominada
    all_F = np.vstack([fronts[f"seed{s}_F"] for s in range(5)])
    # ordena por distância e mantém pontos não-dominados
    order = np.argsort(all_F[:, 0])
    sorted_F = all_F[order]
    nd_F = [sorted_F[0]]
    for pt in sorted_F[1:]:
        if pt[1] < nd_F[-1][1]:
            nd_F.append(pt)
    nd_F = np.array(nd_F)

    fig, ax = plt.subplots(figsize=(8, 5))
    # fronteiras individuais
    colors_seeds = plt.get_cmap("Blues")(np.linspace(0.3, 0.7, 5))
    for seed, c in enumerate(colors_seeds):
        F = fronts[f"seed{seed}_F"]
        o = np.argsort(F[:, 0])
        ax.plot(F[o, 0], F[o, 1], "-", color=c, alpha=0.4, linewidth=1)
        ax.scatter(F[:, 0], F[:, 1], color=c, s=15, alpha=0.5)
    # fronteira agregada (envelope)
    ax.plot(nd_F[:, 0], nd_F[:, 1], "-", color="#1f4e8c", linewidth=2.2,
            label="Fronteira NSGA-II (5 sementes agregadas)")
    # AG single-objective
    ag_d = [float(r["distance"]) for r in ag_points]
    ag_v = [float(r["violation"]) for r in ag_points]
    ax.scatter(ag_d, ag_v, marker="X", s=130, color="#c0392b",
               edgecolors="white", linewidths=1.5, zorder=5,
               label="AG penalizado (λ=1000), 5 sementes")
    # linha de viabilidade
    ax.axhline(0, color="green", linestyle="--", linewidth=1.5,
               alpha=0.7, label="violação = 0 (factível)")

    ax.set_xlabel("Distância")
    ax.set_ylabel("Violação total (Σ atrasos)")
    ax.set_title(f"{name}: fronteira NSGA-II vs AG penalizado")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_nsga_vs_ag.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figura 4 — tamanho da fronteira e viabilidade por instância
# ---------------------------------------------------------------------------


def fig_front_size() -> None:
    widths: list[int] = []
    front_sizes: list[list[int]] = []
    n_feasible: list[list[int]] = []
    for name in INSTANCES:
        w = int(name.split("w")[1].split(".")[0])
        widths.append(w)
        rows = list(csv.DictReader(
            (RUNS_DIR / name / f"{name}_nsga.csv").open()))
        front_sizes.append([int(r["front_size"]) for r in rows])
        n_feasible.append([int(r["n_feasible_solutions"]) for r in rows])

    positions = np.arange(len(widths))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    bp = ax1.boxplot(front_sizes, positions=positions, widths=0.5,
                     patch_artist=True, showmeans=True)
    for patch in bp["boxes"]:
        patch.set_facecolor("#3b7dd8")
        patch.set_alpha(0.6)
    ax1.set_xticks(positions)
    ax1.set_xticklabels([f"w={w}" for w in widths])
    ax1.set_ylabel("|fronteira| (nº de soluções não-dominadas)")
    ax1.set_xlabel("Largura média da janela")
    ax1.set_title("Tamanho da fronteira de Pareto por instância")
    ax1.grid(True, axis="y", alpha=0.3)

    bp2 = ax2.boxplot(n_feasible, positions=positions, widths=0.5,
                      patch_artist=True, showmeans=True)
    for patch in bp2["boxes"]:
        patch.set_facecolor("#27ae60")
        patch.set_alpha(0.55)
    ax2.set_xticks(positions)
    ax2.set_xticklabels([f"w={w}" for w in widths])
    ax2.set_ylabel("nº soluções factíveis na fronteira (viol=0)")
    ax2.set_xlabel("Largura média da janela")
    ax2.set_title("Soluções factíveis encontradas")
    ax2.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig4_front_size.png", dpi=150)
    plt.close(fig)


def main() -> None:
    fig_pareto()
    print("ok fig1_pareto.png")
    fig_hypervolume()
    print("ok fig2_hypervolume.png")
    fig_nsga_vs_ag()
    print("ok fig3_nsga_vs_ag.png")
    fig_front_size()
    print("ok fig4_front_size.png")


if __name__ == "__main__":
    main()
