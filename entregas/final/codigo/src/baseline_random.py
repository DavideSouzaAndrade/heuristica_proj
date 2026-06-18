"""Busca aleatória — referência inferior para o TSPTW.

Amostra `n_evals` permutações independentes uniformemente sobre o conjunto
de tours, mantém a melhor segundo a função objetivo penalizada e devolve
o histórico do melhor a cada avaliação. O orçamento padrão é igual ao do
AG (pop_size · n_generations), o que torna a comparação por número de
avaliações direta.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .evaluation import Evaluation, evaluate
from .instance import TSPTWInstance


@dataclass
class RandomResult:
    best_perm: np.ndarray
    best_eval: Evaluation
    best_fitness: float
    history_best: np.ndarray


def random_search(
    inst: TSPTWInstance,
    n_evals: int,
    lam: float = 1000.0,
    seed: int | None = None,
) -> RandomResult:
    rng = np.random.default_rng(seed)
    base = np.arange(1, inst.n, dtype=np.int64)

    best_fit = np.inf
    best_perm = None
    best_eval: Evaluation | None = None
    history = np.empty(n_evals, dtype=np.float64)

    for k in range(n_evals):
        perm = rng.permutation(base)
        ev = evaluate(inst, perm)
        fit = ev.penalized(lam)
        if fit < best_fit:
            best_fit = fit
            best_perm = perm
            best_eval = ev
        history[k] = best_fit

    assert best_perm is not None and best_eval is not None
    return RandomResult(
        best_perm=best_perm,
        best_eval=best_eval,
        best_fitness=best_fit,
        history_best=history,
    )


if __name__ == "__main__":
    from .instance import load_dumas

    inst = load_dumas("data/dumas/n20w20.001.txt")
    res = random_search(inst, n_evals=10000, lam=1000.0, seed=0)
    ev = res.best_eval
    flag = "OK" if ev.feasible else f"{ev.n_violations} late"
    print(f"Random n_evals=10000  dist={ev.distance:.0f}  "
          f"fitness={res.best_fitness:.0f}  [{flag}]")
