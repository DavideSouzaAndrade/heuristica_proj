"""Função objetivo do TSPTW.

Uma solução é uma permutação dos n clientes (sem o depósito).
A rota completa é   depósito -> π[0] -> π[1] -> ... -> π[n-1] -> depósito.

Convenções:
    * tempo de viagem entre i e j = inst.dist[i, j]
    * tempo de serviço = 0
    * se a chegada t a um nó for menor que e, o agente espera até e
    * se a chegada t for maior que l, há violação de janela t - l
    * o retorno ao depósito também é considerado: a chegada deve ocorrer
      antes (ou em cima) do fechamento do depósito l_0

A função objetivo penalizada é
        f(π) = dist_total(π) + λ · Σ max(0, t_i − l_i)
onde a soma cobre os clientes e o retorno ao depósito.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .instance import TSPTWInstance


@dataclass(frozen=True)
class Evaluation:
    distance: float
    violation: float
    n_violations: int
    feasible: bool
    arrival: np.ndarray

    def penalized(self, lam: float) -> float:
        return self.distance + lam * self.violation


def evaluate(inst: TSPTWInstance, perm: np.ndarray | list[int]) -> Evaluation:
    perm = np.asarray(perm, dtype=np.int64)
    if perm.shape[0] != inst.n - 1:
        raise ValueError(
            f"permutation has {perm.shape[0]} elements, expected {inst.n - 1}"
        )

    dist = inst.dist
    e = inst.e
    l = inst.l
    depot = inst.depot

    route = np.empty(inst.n + 1, dtype=np.int64)
    route[0] = depot
    route[1:-1] = perm
    route[-1] = depot

    arrival = np.zeros(inst.n + 1, dtype=np.float64)
    departure = 0.0
    total_dist = 0.0
    total_violation = 0.0
    n_violations = 0

    for k in range(1, inst.n + 1):
        i = route[k - 1]
        j = route[k]
        d = float(dist[i, j])
        t = departure + d
        arrival[k] = t
        total_dist += d
        if t > l[j]:
            total_violation += t - l[j]
            n_violations += 1
        start = max(t, float(e[j]))
        departure = start

    feasible = n_violations == 0
    return Evaluation(
        distance=total_dist,
        violation=total_violation,
        n_violations=n_violations,
        feasible=feasible,
        arrival=arrival,
    )


if __name__ == "__main__":
    from .instance import load_dumas

    inst = load_dumas("data/dumas/n20w20.001.txt")
    rng = np.random.default_rng(0)
    perm = rng.permutation(np.arange(1, inst.n))
    ev = evaluate(inst, perm)
    print(f"random permutation: dist={ev.distance:.0f}  "
          f"violation={ev.violation:.0f} ({ev.n_violations} late) "
          f"feasible={ev.feasible}")
    print(f"f (lambda=100) = {ev.penalized(100):.0f}")
