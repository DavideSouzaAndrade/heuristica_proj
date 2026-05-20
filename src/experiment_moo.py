"""Runner experimental do Checkpoint 2 — NSGA-II multiobjetivo.

Para cada instância TSPTW:
    * Executa o NSGA-II em S sementes (S=5 no CP2, S=10 final).
    * Coleta a fronteira final (F, X) de cada semente, o histórico de
      fronteiras por geração e o hypervolume ao longo das gerações.
    * Calcula um ponto de referência global (max observado entre todas
      as sementes + margem) e recalcula HV final consistente.
    * Persiste em CSV/NPZ/JSON sob `entregas/<tag>/resultados/<instance>/`.

Uso:
    python -m src.experiment_moo --instance cp1 --seeds 5 --tag cp2
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
from pymoo.indicators.hv import HV

from .instance import load_dumas
from .nsga import NSGAConfig, NSGAResult, run_nsga


def _summary(values) -> dict:
    arr = np.asarray(values, dtype=np.float64)
    if arr.size == 0:
        return {"mean": 0.0, "std": 0.0, "median": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "median": float(np.median(arr)),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def run_one(
    instance_path: Path,
    seeds: list[int],
    config: NSGAConfig,
    out_dir: Path,
) -> dict:
    inst = load_dumas(instance_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1ª passada: roda todas as sementes para descobrir o ponto de referência global
    seed_results: list[NSGAResult] = []
    seed_times: list[float] = []
    for seed in seeds:
        t0 = time.perf_counter()
        res = run_nsga(inst, config, seed=seed)
        seed_times.append(time.perf_counter() - t0)
        seed_results.append(res)

    # ref point global = max(dist, viol) sobre todas as fronteiras + 10%
    all_F = np.vstack([r.front_F for r in seed_results])
    ref_global = all_F.max(axis=0) * 1.1 + 1.0
    hv_ind = HV(ref_point=ref_global)

    # recalcula HV final + histórico HV com ref global
    rows = []
    front_blobs = {}
    history_hv_all = []
    for seed, res in zip(seeds, seed_results):
        hv_final = float(hv_ind(res.front_F))
        history_hv = np.array([float(hv_ind(F)) if F.size else 0.0
                               for F in res.history_F])
        # Estatísticas da fronteira
        feasible_mask = res.front_F[:, 1] <= 0.0
        n_feasible = int(feasible_mask.sum())
        best_feasible_dist = (float(res.front_F[feasible_mask, 0].min())
                              if n_feasible > 0 else float("nan"))
        rows.append({
            "instance": inst.name,
            "seed": seed,
            "front_size": int(len(res.front_F)),
            "hypervolume_global_ref": hv_final,
            "dist_min": float(res.front_F[:, 0].min()),
            "dist_max": float(res.front_F[:, 0].max()),
            "viol_min": float(res.front_F[:, 1].min()),
            "viol_max": float(res.front_F[:, 1].max()),
            "n_feasible_solutions": n_feasible,
            "best_feasible_dist": best_feasible_dist,
            "time_s": seed_times[seeds.index(seed)],
        })
        front_blobs[f"seed{seed}_F"] = res.front_F
        front_blobs[f"seed{seed}_X"] = res.front_X
        history_hv_all.append(history_hv)

    # CSV de resumo por semente
    with (out_dir / f"{inst.name}_nsga.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # NPZ com fronteiras
    np.savez(out_dir / f"{inst.name}_fronts.npz", **front_blobs)

    # NPY com histórico HV (n_seeds × n_gens)
    np.save(out_dir / f"{inst.name}_hv_history.npy", np.array(history_hv_all))

    summary = {
        "instance": inst.name,
        "n_customers": inst.n - 1,
        "nsga_config": config.__dict__,
        "seeds": seeds,
        "ref_point_global": ref_global.tolist(),
        "front_size": _summary([r["front_size"] for r in rows]),
        "hypervolume": _summary([r["hypervolume_global_ref"] for r in rows]),
        "best_dist": _summary([r["dist_min"] for r in rows]),
        "n_feasible_solutions": _summary(
            [r["n_feasible_solutions"] for r in rows]
        ),
        "best_feasible_dist": _summary([
            r["best_feasible_dist"] for r in rows
            if not np.isnan(r["best_feasible_dist"])
        ]),
        "feasible_rate": float(np.mean(
            [r["n_feasible_solutions"] > 0 for r in rows]
        )),
        "time_s": _summary([r["time_s"] for r in rows]),
    }
    (out_dir / f"{inst.name}_summary.json").write_text(
        json.dumps(summary, indent=2)
    )
    return summary


def _print_summary(s: dict) -> None:
    print(f"\n=== {s['instance']}  (n={s['n_customers']}) ===")
    print(f"  Front size  mean={s['front_size']['mean']:5.1f}  "
          f"range=[{s['front_size']['min']:.0f}, {s['front_size']['max']:.0f}]")
    print(f"  HV (global) mean={s['hypervolume']['mean']:.3e}  "
          f"std={s['hypervolume']['std']:.2e}")
    print(f"  Best dist   mean={s['best_dist']['mean']:7.1f}  "
          f"range=[{s['best_dist']['min']:.0f}, {s['best_dist']['max']:.0f}]")
    print(f"  Feasible    {s['feasible_rate'] * 100:.0f}% das sementes  "
          f"(n médio={s['n_feasible_solutions']['mean']:.1f})")
    if s["best_feasible_dist"]["mean"] > 0:
        print(f"  Best feas.  mean={s['best_feasible_dist']['mean']:.1f}  "
              f"range=[{s['best_feasible_dist']['min']:.0f}, "
              f"{s['best_feasible_dist']['max']:.0f}]")
    print(f"  ref point   {s['ref_point_global']}")
    print(f"  time/run    {s['time_s']['mean']:.2f}s")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True,
                        help="caminho .txt, 'cp1' (mesmas 5 do CP1) ou 'all'")
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--pop-size", type=int, default=100)
    parser.add_argument("--n-generations", type=int, default=1500)
    parser.add_argument("--p-mutation", type=float, default=0.3)
    parser.add_argument("--memetic-period", type=int, default=0,
                        help="aplica 2-opt Pareto a cada N gerações (0 desabilita)")
    parser.add_argument("--memetic-top-k", type=int, default=5)
    parser.add_argument("--memetic-max-iter", type=int, default=5)
    parser.add_argument("--tag", type=str, default="cp2")
    args = parser.parse_args()

    cfg = NSGAConfig(
        pop_size=args.pop_size,
        n_generations=args.n_generations,
        p_mutation=args.p_mutation,
        memetic_period=args.memetic_period,
        memetic_top_k=args.memetic_top_k,
        memetic_max_iter=args.memetic_max_iter,
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

    out_root = Path("entregas") / args.tag / "resultados"
    out_root.mkdir(parents=True, exist_ok=True)
    summaries = []
    for f in files:
        s = run_one(f, seeds, cfg, out_root / f.stem)
        _print_summary(s)
        summaries.append(s)

    (out_root / "all_summary.json").write_text(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
