"""Algoritmo Genético single-objective para TSPTW.

* Representação: permutação dos n-1 clientes (depósito fixo no início e fim).
* Fitness: f(π) = dist(π) + λ · Σ max(0, t_i − l_i)   (a minimizar).
* Seleção: torneio (k=3 por padrão).
* Crossover: Order Crossover (OX).
* Mutação: inversão (com probabilidade p_mut por filho).
* Elitismo: os top-`elite` indivíduos sobrevivem intactos a cada geração.

Retorna o melhor indivíduo encontrado e o histórico de melhor/média por geração.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .evaluation import Evaluation, evaluate
from .instance import TSPTWInstance
from .operators import (
    inversion_mutation,
    order_crossover,
    swap_mutation,
    tournament_selection,
)


@dataclass
class GAConfig:
    pop_size: int = 200
    n_generations: int = 1500
    tournament_k: int = 3
    p_crossover: float = 0.9
    p_mutation: float = 0.3
    elite: int = 2
    lam: float = 1000.0
    mutation_op: str = "inversion"


@dataclass
class GAResult:
    best_perm: np.ndarray
    best_eval: Evaluation
    best_fitness: float
    history_best: np.ndarray
    history_mean: np.ndarray


def _initial_population(
    n_customers: int, pop_size: int, rng: np.random.Generator
) -> np.ndarray:
    base = np.arange(1, n_customers + 1, dtype=np.int64)
    pop = np.empty((pop_size, n_customers), dtype=np.int64)
    for i in range(pop_size):
        pop[i] = rng.permutation(base)
    return pop


def _evaluate_population(
    inst: TSPTWInstance, pop: np.ndarray, lam: float
) -> tuple[np.ndarray, list[Evaluation]]:
    evals: list[Evaluation] = [evaluate(inst, ind) for ind in pop]
    fitness = np.array([ev.penalized(lam) for ev in evals], dtype=np.float64)
    return fitness, evals


def run_ga(
    inst: TSPTWInstance,
    config: GAConfig | None = None,
    seed: int | None = None,
    seed_perms: list[np.ndarray] | None = None,
) -> GAResult:
    cfg = config or GAConfig()
    rng = np.random.default_rng(seed)
    n_customers = inst.n - 1

    pop = _initial_population(n_customers, cfg.pop_size, rng)
    if seed_perms:
        for i, sp in enumerate(seed_perms[: cfg.pop_size]):
            pop[i] = np.asarray(sp, dtype=np.int64)

    fitness, evals = _evaluate_population(inst, pop, cfg.lam)
    history_best = np.empty(cfg.n_generations + 1, dtype=np.float64)
    history_mean = np.empty(cfg.n_generations + 1, dtype=np.float64)
    history_best[0] = fitness.min()
    history_mean[0] = fitness.mean()

    mutate = inversion_mutation if cfg.mutation_op == "inversion" else swap_mutation

    for gen in range(1, cfg.n_generations + 1):
        order = np.argsort(fitness)
        new_pop = np.empty_like(pop)
        new_evals: list[Evaluation | None] = [None] * cfg.pop_size
        new_fitness = np.empty_like(fitness)

        # elitismo
        for k in range(cfg.elite):
            new_pop[k] = pop[order[k]]
            new_evals[k] = evals[order[k]]
            new_fitness[k] = fitness[order[k]]

        # gera o resto
        for k in range(cfg.elite, cfg.pop_size):
            i = tournament_selection(fitness, cfg.tournament_k, rng)
            if rng.random() < cfg.p_crossover:
                j = tournament_selection(fitness, cfg.tournament_k, rng)
                child = order_crossover(pop[i], pop[j], rng)
            else:
                child = pop[i].copy()
            if rng.random() < cfg.p_mutation:
                child = mutate(child, rng)
            ev = evaluate(inst, child)
            new_pop[k] = child
            new_evals[k] = ev
            new_fitness[k] = ev.penalized(cfg.lam)

        pop = new_pop
        evals = new_evals  # type: ignore[assignment]
        fitness = new_fitness
        history_best[gen] = fitness.min()
        history_mean[gen] = fitness.mean()

    best_idx = int(np.argmin(fitness))
    return GAResult(
        best_perm=pop[best_idx],
        best_eval=evals[best_idx],
        best_fitness=float(fitness[best_idx]),
        history_best=history_best,
        history_mean=history_mean,
    )


if __name__ == "__main__":
    from .baseline_nn import nearest_neighbor
    from .instance import load_dumas

    inst = load_dumas("data/dumas/n20w20.001.txt")
    cfg = GAConfig(pop_size=80, n_generations=200, lam=100.0)
    res = run_ga(inst, cfg, seed=0)
    ev = res.best_eval
    flag = "OK" if ev.feasible else f"{ev.n_violations} late ({ev.violation:.0f})"
    print(f"GA   dist={ev.distance:.0f}  fitness={res.best_fitness:.0f}  [{flag}]")

    nn = nearest_neighbor(inst)
    from .evaluation import evaluate as ev_fn

    nn_ev = ev_fn(inst, nn)
    flag_nn = "OK" if nn_ev.feasible else f"{nn_ev.n_violations} late"
    print(f"NN   dist={nn_ev.distance:.0f}  "
          f"fitness={nn_ev.penalized(cfg.lam):.0f}  [{flag_nn}]")
