"""Gera as 8 figuras finais do projeto a partir de entregas/final/resultados/.

Pré-requisito:
    python -m src.experiment --instance cp1 --seeds 10 --tag final
    python -m src.experiment_moo --instance cp1 --seeds 10 --tag final
    python -m src.experiment_moo --instance cp1 --seeds 10 \
        --memetic-period 100 --tag final --suffix _memetic

Saídas (em entregas/final/figuras/):
    fig1_convergencia_ag.png     — convergência do AG (CP1)
    fig2_metodos_so.png          — boxplot AG vs NN vs Random
    fig3_pareto_nsga_vs_ag.png   — fronteiras NSGA-II + AG sobreposto
    fig4_hv_evolucao.png         — HV vs gerações, puro vs memetic
    fig5_pareto_puro_vs_mem.png  — fronteiras agregadas, puro vs memetic
    fig6_feasibility.png         — viabilidade dos 3 métodos por instância
    fig7_n20w80_zoom.png         — zoom n20w80
    fig8_rota_otima.png          — melhor tour com Gantt para n20w20
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pymoo.indicators.hv import HV

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.baseline_nn import nearest_neighbor  # noqa: E402
from src.evaluation import evaluate  # noqa: E402
from src.ga import GAConfig, run_ga  # noqa: E402
from src.instance import load_dumas  # noqa: E402

TAG = "final"
RES_DIR = ROOT / "resultados" / TAG
FIG_DIR = ROOT / "figuras" / TAG
FIG_DIR.mkdir(parents=True, exist_ok=True)

INSTANCES = [
    "n20w20.001", "n20w40.001", "n20w60.001",
    "n20w80.001", "n20w100.001",
]


def _load_json(p: Path) -> dict:
    return json.loads(p.read_text())


def _summary_ga(name: str) -> dict:
    """Summary do experimento SO (AG + Random + NN)."""
    return _load_json(RES_DIR / name / f"{name}_summary_so.json")


def _summary_nsga(name: str, suffix: str = "") -> dict:
    """Summary do experimento MO (NSGA-II puro ou memetic)."""
    return _load_json(RES_DIR / name / f"{name}_summary{suffix}.json")


def _csv_rows(p: Path) -> list[dict]:
    with p.open() as fh:
        return list(csv.DictReader(fh))


def _fronts(name: str, suffix: str = "") -> dict[str, np.ndarray]:
    npz = np.load(RES_DIR / name / f"{name}_fronts{suffix}.npz")
    return {k: npz[k] for k in npz.files}


def _aggregate_nondominated(fronts_list: list[np.ndarray]) -> np.ndarray:
    all_F = np.vstack(fronts_list)
    order = np.argsort(all_F[:, 0])
    sorted_F = all_F[order]
    nd = [sorted_F[0]]
    for pt in sorted_F[1:]:
        if pt[1] < nd[-1][1]:
            nd.append(pt)
    return np.array(nd)


# ===========================================================================
# fig 1 — convergência do AG
# ===========================================================================


def fig_convergencia_ag() -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    colors = plt.get_cmap("viridis")(np.linspace(0.05, 0.85, len(INSTANCES)))
    for name, c in zip(INSTANCES, colors):
        h = np.load(RES_DIR / name / f"{name}_history_best.npy")
        mean = h.mean(axis=0)
        std = h.std(axis=0, ddof=1) if h.shape[0] > 1 else np.zeros_like(mean)
        x = np.arange(mean.size)
        w = int(name.split("w")[1].split(".")[0])
        ax.plot(x, mean, color=c, label=f"w={w}", linewidth=1.6)
        ax.fill_between(x, mean - std, mean + std, color=c, alpha=0.15)
    ax.set_yscale("log")
    ax.set_xlabel("Geração")
    ax.set_ylabel("Melhor fitness (log)")
    ax.set_title("Convergência do Algoritmo Genético — 10 sementes")
    ax.legend(title="Largura janela", loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_convergencia_ag.png", dpi=150)
    plt.close(fig)


# ===========================================================================
# fig 2 — AG vs NN vs Random
# ===========================================================================


def fig_metodos_so() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ga_data: list[list[float]] = []
    rs_data: list[list[float]] = []
    nn_dists: list[float] = []
    feas: list[float] = []
    labels: list[str] = []
    for name in INSTANCES:
        ga_rows = _csv_rows(RES_DIR / name / f"{name}_ga.csv")
        rs_rows = _csv_rows(RES_DIR / name / f"{name}_random.csv")
        ga_data.append([float(r["distance"]) for r in ga_rows])
        rs_data.append([float(r["distance"]) for r in rs_rows])
        s = _summary_ga(name)
        nn_dists.append(s["baseline_nn"]["distance"])
        feas.append(s["feasible_rate"])
        labels.append(name.replace("n20w", "w=").split(".")[0])

    positions = np.arange(len(INSTANCES))
    off = 0.22
    bp_ga = ax.boxplot(ga_data, positions=positions - off, widths=0.35,
                       patch_artist=True, showmeans=True)
    bp_rs = ax.boxplot(rs_data, positions=positions + off, widths=0.35,
                       patch_artist=True, showmeans=True)
    for p in bp_ga["boxes"]:
        p.set_facecolor("#3b7dd8")
        p.set_alpha(0.6)
    for p in bp_rs["boxes"]:
        p.set_facecolor("#7f8c8d")
        p.set_alpha(0.5)
    ax.scatter(positions, nn_dists, marker="D", s=85, color="#c0392b", zorder=5)

    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D
    handles = [
        mpatches.Patch(facecolor="#3b7dd8", alpha=0.6, label="AG (SO-λ)"),
        mpatches.Patch(facecolor="#7f8c8d", alpha=0.5, label="Busca aleatória"),
        Line2D([], [], marker="D", color="#c0392b", linestyle="",
               markersize=8, label="NN (urgency)"),
    ]
    y_min, y_max = ax.get_ylim()
    pad = (y_max - y_min) * 0.08
    ax.set_ylim(y_min - pad * 0.5, y_max + pad)
    for x, f in zip(positions, feas):
        ax.annotate(f"{f * 100:.0f}% factíveis",
                    xy=(x, y_max + pad * 0.4),
                    ha="center", fontsize=9, color="#2c3e50",
                    fontweight="bold")
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Largura média da janela (instância n20)")
    ax.set_ylabel("Distância do tour")
    ax.set_title("AG vs. busca aleatória vs. NN — 10 sementes, mesmo orçamento")
    ax.legend(handles=handles, loc="center right", framealpha=0.9)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig2_metodos_so.png", dpi=150)
    plt.close(fig)


# ===========================================================================
# fig 3 — fronteiras NSGA-II + AG sobreposto
# ===========================================================================


def fig_pareto_nsga_vs_ag() -> None:
    fig, axs = plt.subplots(2, 3, figsize=(14, 8))
    axs = axs.flatten()

    for ax, name in zip(axs, INSTANCES):
        fronts = _fronts(name, suffix="")  # puro
        cs = plt.get_cmap("Blues")(np.linspace(0.35, 0.85, 10))
        for seed in range(10):
            F = fronts[f"seed{seed}_F"]
            order = np.argsort(F[:, 0])
            ax.plot(F[order, 0], F[order, 1], "-o", color=cs[seed],
                    markersize=2.5, linewidth=0.9, alpha=0.65,
                    label=f"seed {seed}" if name == "n20w20.001" else None)
        ag_rows = _csv_rows(RES_DIR / name / f"{name}_ga.csv")
        ag_d = [float(r["distance"]) for r in ag_rows]
        ag_v = [float(r["violation"]) for r in ag_rows]
        ax.scatter(ag_d, ag_v, marker="X", s=70, color="#c0392b",
                   edgecolors="white", linewidths=1, zorder=5,
                   label="AG (SO-λ=1000)" if name == "n20w20.001" else None)

        w = int(name.split("w")[1].split(".")[0])
        ax.set_title(f"{name}  (w≈{w})")
        ax.set_xlabel("distância")
        ax.set_ylabel("violação total")
        ax.axhline(0, color="green", linestyle=":", linewidth=1, alpha=0.6)
        ax.grid(True, alpha=0.3)

    axs[-1].axis("off")
    handles, labels = axs[0].get_legend_handles_labels()
    if handles:
        axs[-1].legend(handles, labels, loc="center", fontsize=9,
                       title="Fronteira NSGA-II por semente +\nAG", ncol=2)
    fig.suptitle("Fronteiras de Pareto NSGA-II vs. pontos do AG single-objective",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_pareto_nsga_vs_ag.png", dpi=150)
    plt.close(fig)


# ===========================================================================
# fig 4 — HV vs gerações, puro vs memetic
# ===========================================================================


def fig_hv_evolucao() -> None:
    fig, axs = plt.subplots(1, 5, figsize=(16, 3.6))
    for ax, name in zip(axs, INSTANCES):
        hv_pure = np.load(RES_DIR / name / f"{name}_hv_history.npy")
        hv_mem = np.load(RES_DIR / name / f"{name}_hv_history_memetic.npy")
        x_pure = np.arange(hv_pure.shape[1])
        x_mem = np.arange(hv_mem.shape[1])
        for hv, x, color, label in [
            (hv_pure, x_pure, "#7f8c8d", "puro"),
            (hv_mem,  x_mem,  "#27ae60", "memetic"),
        ]:
            m = hv.mean(axis=0)
            s = hv.std(axis=0, ddof=1)
            ax.plot(x, m, color=color, label=label, linewidth=1.5)
            ax.fill_between(x, m - s, m + s, color=color, alpha=0.15)
        w = int(name.split("w")[1].split(".")[0])
        ax.set_title(f"w={w}", fontsize=10)
        ax.set_xlabel("Geração")
        ax.grid(True, alpha=0.3)
        if name == INSTANCES[0]:
            ax.set_ylabel("HV")
            ax.legend(loc="lower right", fontsize=9)
    fig.suptitle("Hypervolume vs. geração — NSGA-II puro vs. memetic (10 sementes)",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig4_hv_evolucao.png", dpi=150)
    plt.close(fig)


# ===========================================================================
# fig 5 — fronteiras agregadas puro vs memetic
# ===========================================================================


def fig_pareto_puro_vs_mem() -> None:
    fig, axs = plt.subplots(2, 3, figsize=(13.5, 7.5))
    axs = axs.flatten()
    for ax, name in zip(axs, INSTANCES):
        fp = _fronts(name, suffix="")
        fm = _fronts(name, suffix="_memetic")
        ag_p = _aggregate_nondominated([fp[f"seed{s}_F"] for s in range(10)])
        ag_m = _aggregate_nondominated([fm[f"seed{s}_F"] for s in range(10)])
        ax.plot(ag_p[:, 0], ag_p[:, 1], "-o", color="#7f8c8d", markersize=4,
                linewidth=1.5,
                label="NSGA-II puro" if name == "n20w20.001" else None)
        ax.plot(ag_m[:, 0], ag_m[:, 1], "-o", color="#27ae60", markersize=4,
                linewidth=1.5,
                label="NSGA-II + 2-opt (D1)" if name == "n20w20.001" else None)
        ax.axhline(0, color="green", linestyle=":", linewidth=1, alpha=0.5)
        w = int(name.split("w")[1].split(".")[0])
        ax.set_title(f"{name}  (w≈{w})")
        ax.set_xlabel("distância")
        ax.set_ylabel("violação total")
        ax.grid(True, alpha=0.3)
    axs[-1].axis("off")
    h, l = axs[0].get_legend_handles_labels()
    if h:
        axs[-1].legend(h, l, loc="center", fontsize=11,
                       title="Fronteiras agregadas (10 sementes)")
    fig.suptitle("Fronteiras de Pareto: NSGA-II puro vs. memetic (D1)",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig5_pareto_puro_vs_mem.png", dpi=150)
    plt.close(fig)


# ===========================================================================
# fig 6 — viabilidade dos 3 métodos
# ===========================================================================


def fig_feasibility() -> None:
    widths: list[int] = []
    rate_ag: list[float] = []
    rate_pure: list[float] = []
    rate_mem: list[float] = []
    for name in INSTANCES:
        widths.append(int(name.split("w")[1].split(".")[0]))
        s_ag = _summary_ga(name)
        s_pure = _summary_nsga(name)
        s_mem = _summary_nsga(name, suffix="_memetic")
        rate_ag.append(s_ag["feasible_rate"] * 100)
        rate_pure.append(s_pure["feasible_rate"] * 100)
        rate_mem.append(s_mem["feasible_rate"] * 100)

    x = np.arange(len(widths))
    w_bar = 0.27
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(x - w_bar, rate_ag, width=w_bar, color="#3b7dd8", alpha=0.75,
           label="AG (SO-λ)")
    ax.bar(x,         rate_pure, width=w_bar, color="#7f8c8d", alpha=0.75,
           label="NSGA-II puro")
    ax.bar(x + w_bar, rate_mem,  width=w_bar, color="#27ae60", alpha=0.75,
           label="NSGA-II + 2-opt (D1)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"w={w}" for w in widths])
    ax.set_ylim(0, 115)
    ax.set_ylabel("Sementes com solução factível (%)")
    ax.set_title("Viabilidade dos 3 métodos por largura de janela (10 sementes)")
    ax.legend(loc="lower right")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig6_feasibility.png", dpi=150)
    plt.close(fig)


# ===========================================================================
# fig 7 — zoom n20w80
# ===========================================================================


def fig_n20w80_zoom() -> None:
    name = "n20w80.001"
    fp = _fronts(name, suffix="")
    fm = _fronts(name, suffix="_memetic")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for seed in range(10):
        F = fp[f"seed{seed}_F"]
        o = np.argsort(F[:, 0])
        ax1.plot(F[o, 0], F[o, 1], "-o", markersize=3, linewidth=0.9,
                 alpha=0.55, label=f"s{seed}" if seed < 5 else None)
        Fm = fm[f"seed{seed}_F"]
        om = np.argsort(Fm[:, 0])
        ax2.plot(Fm[om, 0], Fm[om, 1], "-o", markersize=3, linewidth=0.9,
                 alpha=0.55, label=f"s{seed}" if seed < 5 else None)
    for ax, title in zip((ax1, ax2),
                         ("NSGA-II puro", "NSGA-II + 2-opt (D1)")):
        ax.axhline(0, color="green", linestyle=":", linewidth=1.2, alpha=0.7)
        ax.set_xlabel("Distância")
        ax.grid(True, alpha=0.3)
        ax.set_title(title)
    ax1.set_ylabel("Violação total")
    ax1.legend(loc="upper right", fontsize=7, ncol=2)
    fig.suptitle(f"{name}: fronteiras por semente — puro vs. memetic",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig7_n20w80_zoom.png", dpi=150)
    plt.close(fig)


# ===========================================================================
# fig 8 — melhor tour para n20w20.001
# ===========================================================================


def fig_rota_otima() -> None:
    name = "n20w20.001"
    inst = load_dumas(ROOT / "data" / "dumas" / f"{name}.txt")
    summary = _summary_ga(name)
    cfg = GAConfig(**{k: v for k, v in summary["ga_config"].items()
                      if k in GAConfig.__dataclass_fields__})
    best_perm = None
    best_eval = None
    for seed in summary["seeds"]:
        res = run_ga(inst, cfg, seed=seed)
        if (best_eval is None
                or (res.best_eval.feasible and not best_eval.feasible)
                or (res.best_eval.feasible == best_eval.feasible
                    and res.best_eval.distance < best_eval.distance)):
            best_perm = res.best_perm
            best_eval = res.best_eval

    from numpy.linalg import eigh
    D = inst.dist.astype(float)
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    vals, vecs = eigh(B)
    idx = np.argsort(-vals)[:2]
    coords = vecs[:, idx] * np.sqrt(np.maximum(vals[idx], 0))

    route = np.concatenate(([inst.depot], best_perm, [inst.depot]))
    ev = best_eval

    fig, (ax_m, ax_t) = plt.subplots(1, 2, figsize=(12, 5))
    ax_m.plot(coords[route, 0], coords[route, 1], "-",
              color="#3b7dd8", linewidth=1.5)
    ax_m.scatter(coords[1:, 0], coords[1:, 1], c="#3b7dd8", s=50, zorder=5)
    ax_m.scatter(coords[0, 0], coords[0, 1], c="#c0392b", s=130, marker="s",
                 zorder=6, label="Depósito")
    for i, (x, y) in enumerate(coords):
        ax_m.annotate(str(i), (x, y), fontsize=7,
                      xytext=(4, 4), textcoords="offset points")
    feas_str = "factível" if ev.feasible else f"{ev.n_violations} violações"
    ax_m.set_title(f"Melhor tour ({name})\ndistância={ev.distance:.0f}  ({feas_str})")
    ax_m.set_aspect("equal")
    ax_m.legend()
    ax_m.grid(True, alpha=0.3)

    arrival = ev.arrival
    e = inst.e
    l = inst.l
    for k in range(1, n + 1):
        node = route[k]
        ax_t.barh(k, l[node] - e[node], left=e[node],
                  color="#bdc3c7", alpha=0.6, edgecolor="#555")
        color = "#27ae60" if arrival[k] <= l[node] else "#c0392b"
        ax_t.scatter(arrival[k], k, color=color, s=40, zorder=5)
    ax_t.set_yticks(np.arange(1, n + 1))
    ax_t.set_yticklabels([f"{k}: nó {route[k]}" for k in range(1, n + 1)])
    ax_t.invert_yaxis()
    ax_t.set_xlabel("Tempo")
    ax_t.set_title("Janelas e instante de chegada por posição")
    ax_t.grid(True, axis="x", alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig8_rota_otima.png", dpi=150)
    plt.close(fig)


def main() -> None:
    fig_convergencia_ag()
    print("ok fig1_convergencia_ag.png")
    fig_metodos_so()
    print("ok fig2_metodos_so.png")
    fig_pareto_nsga_vs_ag()
    print("ok fig3_pareto_nsga_vs_ag.png")
    fig_hv_evolucao()
    print("ok fig4_hv_evolucao.png")
    fig_pareto_puro_vs_mem()
    print("ok fig5_pareto_puro_vs_mem.png")
    fig_feasibility()
    print("ok fig6_feasibility.png")
    fig_n20w80_zoom()
    print("ok fig7_n20w80_zoom.png")
    fig_rota_otima()
    print("ok fig8_rota_otima.png")


if __name__ == "__main__":
    main()
