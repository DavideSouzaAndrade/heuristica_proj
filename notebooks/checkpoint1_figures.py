"""Gera todas as figuras do Checkpoint 1 a partir dos resultados salvos.

Pré-requisito: ter executado
    python -m src.experiment --instance cp1 --seeds 5 --tag cp1

Saídas (em entregas/cp1/figuras/):
    fig1_convergencia.png    — curva de convergência média ± desvio
    fig2_boxplot.png         — distribuição de distância por instância (GA vs NN vs Random)
    fig3_rota.png            — melhor tour encontrado em n20w20.001 + linha do tempo
    fig4_viabilidade.png     — taxa de viabilidade por largura de janela
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.baseline_nn import nearest_neighbor  # noqa: E402
from src.evaluation import evaluate  # noqa: E402
from src.ga import GAConfig, run_ga  # noqa: E402
from src.instance import load_dumas  # noqa: E402

TAG = "cp1"
RUNS_DIR = ROOT / "entregas" / TAG / "resultados"
FIG_DIR = ROOT / "entregas" / TAG / "figuras"
FIG_DIR.mkdir(parents=True, exist_ok=True)

INSTANCES = [
    "n20w20.001", "n20w40.001", "n20w60.001",
    "n20w80.001", "n20w100.001",
]


def _load_summary(name: str) -> dict:
    return json.loads((RUNS_DIR / name / f"{name}_summary.json").read_text())


def _load_history(name: str) -> np.ndarray:
    return np.load(RUNS_DIR / name / f"{name}_history_best.npy")


def fig_convergencia() -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = plt.get_cmap("viridis")(np.linspace(0.05, 0.85, len(INSTANCES)))
    for name, c in zip(INSTANCES, colors):
        h = _load_history(name)
        mean = h.mean(axis=0)
        std = h.std(axis=0, ddof=1) if h.shape[0] > 1 else np.zeros_like(mean)
        x = np.arange(mean.size)
        label = name.replace("n20w", "w=").split(".")[0]
        ax.plot(x, mean, color=c, label=label, linewidth=1.5)
        ax.fill_between(x, mean - std, mean + std, color=c, alpha=0.15)
    ax.set_yscale("log")
    ax.set_xlabel("Geração")
    ax.set_ylabel("Melhor fitness (escala log)")
    ax.set_title("Convergência do AG — média ± desvio sobre 5 sementes")
    ax.legend(title="Largura de janela", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_convergencia.png", dpi=150)
    plt.close(fig)


def fig_boxplot() -> None:
    import csv

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ga_data: list[list[float]] = []
    rs_data: list[list[float]] = []
    nn_dists: list[float] = []
    feasibilities: list[float] = []
    labels: list[str] = []
    for name in INSTANCES:
        with (RUNS_DIR / name / f"{name}_ga.csv").open() as fh:
            ga_rows = list(csv.DictReader(fh))
        with (RUNS_DIR / name / f"{name}_random.csv").open() as fh:
            rs_rows = list(csv.DictReader(fh))
        ga_data.append([float(r["distance"]) for r in ga_rows])
        rs_data.append([float(r["distance"]) for r in rs_rows])
        summary = _load_summary(name)
        nn_dists.append(summary["baseline_nn"]["distance"])
        feasibilities.append(summary["feasible_rate"])
        labels.append(name.replace("n20w", "w=").split(".")[0])

    positions = np.arange(len(INSTANCES))
    off = 0.22
    bp_ga = ax.boxplot(ga_data, positions=positions - off, widths=0.35,
                       patch_artist=True, showmeans=True)
    bp_rs = ax.boxplot(rs_data, positions=positions + off, widths=0.35,
                       patch_artist=True, showmeans=True)
    for patch in bp_ga["boxes"]:
        patch.set_facecolor("#3b7dd8")
        patch.set_alpha(0.6)
    for patch in bp_rs["boxes"]:
        patch.set_facecolor("#7f8c8d")
        patch.set_alpha(0.5)
    ax.scatter(positions, nn_dists, marker="D", s=80, color="#c0392b",
               zorder=5)
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D
    handles = [
        mpatches.Patch(facecolor="#3b7dd8", alpha=0.6, label="AG"),
        mpatches.Patch(facecolor="#7f8c8d", alpha=0.5, label="Busca aleatória"),
        Line2D([], [], marker="D", color="#c0392b", linestyle="",
               markersize=8, label="NN (urgency)"),
    ]
    y_min, y_max = ax.get_ylim()
    pad = (y_max - y_min) * 0.08
    ax.set_ylim(y_min - pad * 0.5, y_max + pad)
    for x, f in zip(positions, feasibilities):
        ax.annotate(f"{f * 100:.0f}% factíveis (AG)",
                    xy=(x, y_max + pad * 0.4),
                    ha="center", fontsize=8.5, color="#2c3e50",
                    fontweight="bold")
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Largura média da janela (instância n20)")
    ax.set_ylabel("Distância do tour")
    ax.set_title(
        "AG vs. busca aleatória vs. NN — 5 sementes, mesmo orçamento de avaliações"
    )
    ax.legend(handles=handles, loc="center right", framealpha=0.9)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig2_boxplot.png", dpi=150)
    plt.close(fig)


def _best_tour(name: str) -> tuple[np.ndarray, dict]:
    summary = _load_summary(name)
    inst = load_dumas(ROOT / "data" / "dumas" / f"{name}.txt")
    cfg = GAConfig(**summary["ga_config"])
    best_perm = None
    best_eval = None
    best_seed = None
    for seed in summary["seeds"]:
        res = run_ga(inst, cfg, seed=seed)
        if (best_eval is None
                or (res.best_eval.feasible and not best_eval.feasible)
                or (res.best_eval.feasible == best_eval.feasible
                    and res.best_eval.distance < best_eval.distance)):
            best_perm = res.best_perm
            best_eval = res.best_eval
            best_seed = seed
    info = {
        "inst": inst,
        "perm": best_perm,
        "eval": best_eval,
        "seed": best_seed,
    }
    return best_perm, info


def fig_rota() -> None:
    name = "n20w20.001"
    _, info = _best_tour(name)
    inst = info["inst"]
    perm = info["perm"]
    ev = info["eval"]

    # como o dataset não tem coordenadas (apenas matriz de distâncias),
    # geramos um layout via MDS clássico
    from numpy.linalg import eigh

    D = inst.dist.astype(float)
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    vals, vecs = eigh(B)
    idx = np.argsort(-vals)[:2]
    coords = vecs[:, idx] * np.sqrt(np.maximum(vals[idx], 0))

    route = np.concatenate(([inst.depot], perm, [inst.depot]))

    fig, (ax_m, ax_t) = plt.subplots(1, 2, figsize=(12, 5))

    # mapa
    ax_m.plot(coords[route, 0], coords[route, 1], "-", color="#3b7dd8", linewidth=1.5)
    ax_m.scatter(coords[1:, 0], coords[1:, 1], c="#3b7dd8", s=50, zorder=5)
    ax_m.scatter(coords[0, 0], coords[0, 1], c="#c0392b", s=130, marker="s",
                 zorder=6, label="Depósito")
    for i, (x, y) in enumerate(coords):
        ax_m.annotate(str(i), (x, y), fontsize=7,
                      xytext=(4, 4), textcoords="offset points")
    feas_str = "factível" if ev.feasible else f"{ev.n_violations} violações"
    ax_m.set_title(
        f"Melhor tour para {name}\n"
        f"distância={ev.distance:.0f}  ({feas_str})"
    )
    ax_m.set_aspect("equal")
    ax_m.legend()
    ax_m.grid(True, alpha=0.3)

    # linha do tempo (gantt-like)
    arrival = ev.arrival
    e = inst.e
    l = inst.l
    for k in range(1, n + 1):
        node = route[k]
        ax_t.barh(k, l[node] - e[node], left=e[node],
                  color="#bdc3c7", alpha=0.6, edgecolor="#555")
        marker_color = "#27ae60" if arrival[k] <= l[node] else "#c0392b"
        ax_t.scatter(arrival[k], k, color=marker_color, s=40, zorder=5)
    ax_t.set_yticks(np.arange(1, n + 1))
    ax_t.set_yticklabels([f"{k}: nó {route[k]}" for k in range(1, n + 1)])
    ax_t.invert_yaxis()
    ax_t.set_xlabel("Tempo")
    ax_t.set_title("Janelas e chegada por posição na rota")
    ax_t.grid(True, axis="x", alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_rota.png", dpi=150)
    plt.close(fig)


def fig_viabilidade() -> None:
    widths: list[int] = []
    rates: list[float] = []
    avg_dist: list[float] = []
    nn_dist: list[float] = []
    rs_dist: list[float] = []
    for name in INSTANCES:
        s = _load_summary(name)
        w = int(name.split("w")[1].split(".")[0])
        widths.append(w)
        rates.append(s["feasible_rate"])
        avg_dist.append(s["distance"]["mean"])
        nn_dist.append(s["baseline_nn"]["distance"])
        rs_dist.append(s["random"]["distance"]["mean"])

    fig, ax1 = plt.subplots(figsize=(8.8, 4.8))
    ax1.bar(np.arange(len(widths)), [r * 100 for r in rates],
            color="#3b7dd8", alpha=0.45, label="Viabilidade do AG (%)")
    ax1.set_xticks(np.arange(len(widths)))
    ax1.set_xticklabels([f"w={w}" for w in widths])
    ax1.set_ylabel("Sementes factíveis (%)", color="#3b7dd8")
    ax1.set_ylim(0, 120)
    ax1.tick_params(axis="y", labelcolor="#3b7dd8")
    ax1.grid(True, axis="y", alpha=0.3)

    ax2 = ax1.twinx()
    x = np.arange(len(widths))
    ax2.plot(x, avg_dist, "o-", color="#c0392b",
             label="AG distância média", linewidth=2)
    ax2.plot(x, nn_dist, "D--", color="#34495e",
             label="NN distância", linewidth=1.5)
    ax2.plot(x, rs_dist, "s:", color="#7f8c8d",
             label="Random distância média", linewidth=1.2)
    ax2.set_ylabel("Distância do tour", color="#444")
    ax2.tick_params(axis="y", labelcolor="#444")

    lines, labs = ax1.get_legend_handles_labels()
    lines2, labs2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labs + labs2,
               loc="upper center", bbox_to_anchor=(0.5, -0.13),
               ncol=4, fontsize=9, frameon=False)

    ax1.set_title("Largura de janela vs. dificuldade — instâncias Dumas n=20")
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.22)
    fig.savefig(FIG_DIR / "fig4_viabilidade.png", dpi=150)
    plt.close(fig)


def main() -> None:
    fig_convergencia()
    print("ok fig1_convergencia.png")
    fig_boxplot()
    print("ok fig2_boxplot.png")
    fig_rota()
    print("ok fig3_rota.png")
    fig_viabilidade()
    print("ok fig4_viabilidade.png")


if __name__ == "__main__":
    main()
