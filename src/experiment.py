"""Runner experimental do Checkpoint 1.

Para cada instância TSPTW:
    * Calcula o baseline Nearest Neighbor (uma rodada — determinístico).
    * Executa a busca aleatória (referência inferior) em S sementes, com
      o mesmo orçamento de avaliações do AG (pop_size * n_generations).
    * Executa o Algoritmo Genético em S sementes (S=5 no CP1, S=10 final).
    * Coleta para cada semente: distância, violação, viabilidade, fitness,
      histórico de melhor/média e tempo de parede.
    * Calcula efeito (Cliff's delta + Hedges' g) AG vs NN e AG vs Random.
    * Persiste em CSV e JSON sob `results/runs/<tag>/<instance>/`.
    * Imprime no stdout um sumário por instância.

Uso:
    python -m src.experiment --instance data/dumas/n20w20.001.txt --seeds 5
    python -m src.experiment --instance cp1 --seeds 5
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np

from .baseline_nn import nearest_neighbor
from .baseline_random import random_search
from .evaluation import evaluate
from .ga import GAConfig, run_ga
from .instance import load_dumas
from .stats import cliffs_delta, cliffs_magnitude, hedges_g


def _summary(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "median": float(np.median(arr)),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def _effect(ag: list[float], ref: list[float]) -> dict:
    d = cliffs_delta(ag, ref)
    return {
        "cliffs_delta": d,
        "cliffs_magnitude": cliffs_magnitude(d),
        "hedges_g": hedges_g(ag, ref),
    }


def run_one(
    instance_path: Path,
    seeds: list[int],
    config: GAConfig,
    out_dir: Path,
) -> dict:
    inst = load_dumas(instance_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    # baseline determinístico
    nn_perm = nearest_neighbor(inst, criterion="urgency")
    nn_eval = evaluate(inst, nn_perm)

    # busca aleatória (referência inferior, mesmo budget do AG)
    n_evals = config.pop_size * config.n_generations
    rs_rows = []
    rs_history_all = []
    for seed in seeds:
        t0 = time.perf_counter()
        rs = random_search(inst, n_evals=n_evals, lam=config.lam, seed=seed)
        dt = time.perf_counter() - t0
        rs_history_all.append(rs.history_best)
        ev = rs.best_eval
        rs_rows.append(
            {
                "instance": inst.name,
                "seed": seed,
                "distance": ev.distance,
                "violation": ev.violation,
                "n_violations": ev.n_violations,
                "feasible": int(ev.feasible),
                "fitness": rs.best_fitness,
                "time_s": dt,
            }
        )

    # AG em múltiplas sementes
    ga_history_best_all = []
    ga_history_mean_all = []
    rows = []
    for seed in seeds:
        t0 = time.perf_counter()
        res = run_ga(inst, config, seed=seed)
        dt = time.perf_counter() - t0
        ev = res.best_eval
        ga_history_best_all.append(res.history_best)
        ga_history_mean_all.append(res.history_mean)
        rows.append(
            {
                "instance": inst.name,
                "seed": seed,
                "distance": ev.distance,
                "violation": ev.violation,
                "n_violations": ev.n_violations,
                "feasible": int(ev.feasible),
                "fitness": res.best_fitness,
                "time_s": dt,
            }
        )

    # csvs
    for tag, data in (("ga", rows), ("random", rs_rows)):
        with (out_dir / f"{inst.name}_{tag}.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)

    np.save(out_dir / f"{inst.name}_history_best.npy",
            np.array(ga_history_best_all))
    np.save(out_dir / f"{inst.name}_history_mean.npy",
            np.array(ga_history_mean_all))
    np.save(out_dir / f"{inst.name}_random_history_best.npy",
            np.array(rs_history_all))

    ga_dists = [r["distance"] for r in rows]
    rs_dists = [r["distance"] for r in rs_rows]

    summary = {
        "instance": inst.name,
        "n_customers": inst.n - 1,
        "baseline_nn": {
            "distance": nn_eval.distance,
            "violation": nn_eval.violation,
            "n_violations": nn_eval.n_violations,
            "feasible": nn_eval.feasible,
        },
        "random": {
            "n_evals_per_seed": n_evals,
            "feasible_rate": float(np.mean([r["feasible"] for r in rs_rows])),
            "distance": _summary(rs_dists),
            "violation": _summary([r["violation"] for r in rs_rows]),
            "fitness": _summary([r["fitness"] for r in rs_rows]),
            "time_s": _summary([r["time_s"] for r in rs_rows]),
        },
        "ga_config": config.__dict__,
        "seeds": seeds,
        "feasible_rate": float(np.mean([r["feasible"] for r in rows])),
        "distance": _summary(ga_dists),
        "violation": _summary([r["violation"] for r in rows]),
        "fitness": _summary([r["fitness"] for r in rows]),
        "time_s": _summary([r["time_s"] for r in rows]),
        "effect_ga_vs_nn": _effect(ga_dists, [nn_eval.distance]),
        "effect_ga_vs_random": _effect(ga_dists, rs_dists),
    }
    (out_dir / f"{inst.name}_summary.json").write_text(
        json.dumps(summary, indent=2)
    )
    return summary


def _print_summary(s: dict) -> None:
    nn = s["baseline_nn"]
    nn_flag = "OK" if nn["feasible"] else f"{nn['n_violations']} late"
    d = s["distance"]
    rs = s["random"]["distance"]
    e_nn = s["effect_ga_vs_nn"]
    e_rs = s["effect_ga_vs_random"]
    print(f"\n=== {s['instance']}  (n={s['n_customers']}) ===")
    print(f"  Random   dist mean={rs['mean']:7.1f}  median={rs['median']:7.1f}  "
          f"range=[{rs['min']:.0f}, {rs['max']:.0f}]  "
          f"feasible={s['random']['feasible_rate'] * 100:.0f}%")
    print(f"  NN       dist={nn['distance']:.0f}  [{nn_flag}]")
    print(f"  GA       dist mean={d['mean']:7.1f}  std={d['std']:6.1f}  "
          f"median={d['median']:7.1f}  range=[{d['min']:.0f}, {d['max']:.0f}]  "
          f"feasible={s['feasible_rate'] * 100:.0f}%")
    print(f"  Effect GA vs NN     Cliff={e_nn['cliffs_delta']:+.3f} "
          f"({e_nn['cliffs_magnitude']})  Hedges g={e_nn['hedges_g']:+.2f}")
    print(f"  Effect GA vs Random Cliff={e_rs['cliffs_delta']:+.3f} "
          f"({e_rs['cliffs_magnitude']})  Hedges g={e_rs['hedges_g']:+.2f}")
    print(f"  avg time/run  GA={s['time_s']['mean']:.2f}s  "
          f"Random={s['random']['time_s']['mean']:.2f}s")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True,
                        help="caminho .txt da instância, 'cp1' (5 representativas) "
                             "ou 'all' (todas n=20)")
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--pop-size", type=int, default=200)
    parser.add_argument("--n-generations", type=int, default=1500)
    parser.add_argument("--lam", type=float, default=1000.0)
    parser.add_argument("--p-mutation", type=float, default=0.3)
    parser.add_argument("--tag", type=str, default="cp1")
    args = parser.parse_args()

    cfg = GAConfig(
        pop_size=args.pop_size,
        n_generations=args.n_generations,
        lam=args.lam,
        p_mutation=args.p_mutation,
    )
    seeds = list(range(args.seeds))

    if args.instance == "all":
        files = sorted(Path("data/dumas").glob("n20w*.txt"))
    elif args.instance == "cp1":
        names = [
            "n20w20.001", "n20w40.001", "n20w60.001",
            "n20w80.001", "n20w100.001",
        ]
        files = [Path("data/dumas") / f"{n}.txt" for n in names]
    else:
        files = [Path(args.instance)]

    out_root = Path("results/runs") / args.tag
    summaries = []
    for f in files:
        s = run_one(f, seeds, cfg, out_root / f.stem)
        _print_summary(s)
        summaries.append(s)

    (out_root / "all_summary.json").write_text(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
