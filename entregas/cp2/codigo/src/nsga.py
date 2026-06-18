"""NSGA-II multiobjetivo para o TSPTW, via pymoo.

Dois objetivos (a minimizar):
    * f1 = distância total do tour
    * f2 = violação total = Σ max(0, t_i − l_i)

Reusa os operadores genéticos do CP1 (`src/operators.py`) para que a
fronteira de Pareto seja comparável com o AG single-objective:

    * Inicialização: permutações uniformes (Sampling).
    * Recombinação: Order Crossover (2 pais → 2 filhos).
    * Mutação: inversão de subsegmento com probabilidade p_mut.
    * Eliminação de duplicatas exata sobre as permutações.

Retorna a fronteira final (F, X), o histórico de fronteiras por
geração e o hypervolume ao longo das gerações.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import ElementwiseDuplicateElimination
from pymoo.core.mutation import Mutation
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.sampling import Sampling
from pymoo.indicators.hv import HV
from pymoo.optimize import minimize

from .evaluation import evaluate
from .instance import TSPTWInstance
from .operators import inversion_mutation, order_crossover


# ---------------------------------------------------------------------------
# Problema multiobjetivo
# ---------------------------------------------------------------------------


class TSPTWMOProblem(ElementwiseProblem):
    def __init__(self, inst: TSPTWInstance):
        self.inst = inst
        super().__init__(n_var=inst.n - 1, n_obj=2, xl=1, xu=inst.n - 1)

    def _evaluate(self, x, out, *args, **kwargs):
        ev = evaluate(self.inst, np.asarray(x, dtype=np.int64))
        out["F"] = np.array([float(ev.distance), float(ev.violation)])


# ---------------------------------------------------------------------------
# Operadores customizados (delegam para src/operators.py)
# ---------------------------------------------------------------------------


def _new_rng() -> np.random.Generator:
    """RNG seedado a partir do estado global da pymoo (que `minimize(..., seed=)` controla)."""
    return np.random.default_rng(int(np.random.randint(0, 2**31 - 1)))


class PermutationSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        n = problem.n_var
        base = np.arange(1, n + 1, dtype=np.int64)
        X = np.empty((n_samples, n), dtype=np.int64)
        for i in range(n_samples):
            X[i] = np.random.permutation(base)
        return X


class OXCrossover(Crossover):
    def __init__(self):
        super().__init__(n_parents=2, n_offsprings=2)

    def _do(self, problem, X, **kwargs):
        _, n_matings, n_var = X.shape
        rng = _new_rng()
        Y = np.empty((2, n_matings, n_var), dtype=np.int64)
        for k in range(n_matings):
            p1 = X[0, k].astype(np.int64)
            p2 = X[1, k].astype(np.int64)
            Y[0, k] = order_crossover(p1, p2, rng)
            Y[1, k] = order_crossover(p2, p1, rng)
        return Y


class InversionMutationOp(Mutation):
    def __init__(self, prob: float = 0.3):
        super().__init__()
        self.prob = prob

    def _do(self, problem, X, **kwargs):
        rng = _new_rng()
        Y = X.copy().astype(np.int64)
        for i in range(Y.shape[0]):
            if rng.random() < self.prob:
                Y[i] = inversion_mutation(Y[i], rng)
        return Y


class PermutationDup(ElementwiseDuplicateElimination):
    def is_equal(self, a, b):
        return bool(np.array_equal(a.X, b.X))


# ---------------------------------------------------------------------------
# Wrapper de configuração e execução
# ---------------------------------------------------------------------------


@dataclass
class NSGAConfig:
    pop_size: int = 100
    n_generations: int = 1500
    p_mutation: float = 0.3
    # Memetic (D1): aplica 2-opt Pareto a cada `memetic_period` gerações
    # em `memetic_top_k` indivíduos da fronteira atual. Se memetic_period=0,
    # desabilita a hibridização (modo NSGA-II puro do CP2).
    memetic_period: int = 0
    memetic_top_k: int = 5
    memetic_max_iter: int = 5


@dataclass
class NSGAResult:
    front_F: np.ndarray
    front_X: np.ndarray
    history_F: list[np.ndarray]
    hypervolumes: np.ndarray
    ref_point: np.ndarray


def _front_from_pop(pop) -> np.ndarray:
    """Extrai a fronteira não-dominada (rank 0) das opt da geração."""
    F = pop.get("F")
    if F is None or len(F) == 0:
        return np.empty((0, 2))
    return np.asarray(F)


def _apply_local_search(algorithm, inst: TSPTWInstance, cfg: NSGAConfig) -> int:
    """Aplica 2-opt Pareto a indivíduos da fronteira atual da população do pymoo.

    Retorna o número de indivíduos efetivamente modificados (para diagnóstico).
    """
    from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

    from .local_search import two_opt_pareto

    pop = algorithm.pop
    F = pop.get("F")
    if F is None or len(F) == 0:
        return 0

    nds = NonDominatedSorting()
    front_idx = nds.do(F, only_non_dominated_front=True)
    if len(front_idx) == 0:
        return 0

    k = min(cfg.memetic_top_k, len(front_idx))
    chosen = np.random.choice(front_idx, size=k, replace=False)

    n_modified = 0
    for idx in chosen:
        ind = pop[int(idx)]
        x_old = np.asarray(ind.X, dtype=np.int64)
        new_x, new_ev = two_opt_pareto(inst, x_old, max_iter=cfg.memetic_max_iter)
        if not np.array_equal(new_x, x_old):
            ind.set("X", new_x)
            ind.set("F", np.array([new_ev.distance, new_ev.violation],
                                  dtype=np.float64))
            n_modified += 1

    return n_modified


def run_nsga(
    inst: TSPTWInstance,
    config: NSGAConfig | None = None,
    seed: int = 0,
    ref_point: np.ndarray | None = None,
) -> NSGAResult:
    cfg = config or NSGAConfig()
    problem = TSPTWMOProblem(inst)
    algorithm = NSGA2(
        pop_size=cfg.pop_size,
        sampling=PermutationSampling(),
        crossover=OXCrossover(),
        mutation=InversionMutationOp(prob=cfg.p_mutation),
        eliminate_duplicates=PermutationDup(),
    )

    memetic_enabled = cfg.memetic_period > 0

    if not memetic_enabled:
        # Modo puro (CP2) — usa o minimize() do pymoo
        res = minimize(
            problem,
            algorithm,
            ("n_gen", cfg.n_generations),
            seed=int(seed),
            verbose=False,
            save_history=True,
        )
        front_F = np.asarray(res.F)
        front_X = np.asarray(res.X, dtype=np.int64)
        history_F = [
            _front_from_pop(entry.opt) for entry in res.history
        ]
    else:
        # Modo memetic — stepping manual para intercalar 2-opt
        algorithm.setup(
            problem,
            termination=("n_gen", cfg.n_generations),
            seed=int(seed),
            verbose=False,
        )
        history_F = []
        while algorithm.has_next():
            algorithm.next()
            history_F.append(_front_from_pop(algorithm.opt))
            if algorithm.n_gen % cfg.memetic_period == 0:
                _apply_local_search(algorithm, inst, cfg)
        res = algorithm.result()
        front_F = np.asarray(res.F)
        front_X = np.asarray(res.X, dtype=np.int64)

    # Ponto de referência adaptativo: max observado nas fronteiras + margem 10%
    if ref_point is None:
        all_pts = np.vstack([f for f in history_F if f.size > 0] + [front_F])
        ref = all_pts.max(axis=0) * 1.1 + 1.0
    else:
        ref = np.asarray(ref_point, dtype=float)

    hv_ind = HV(ref_point=ref)
    hypervolumes = np.empty(len(history_F), dtype=np.float64)
    for g, F in enumerate(history_F):
        hypervolumes[g] = hv_ind(F) if F.size > 0 else 0.0

    return NSGAResult(
        front_F=front_F,
        front_X=front_X,
        history_F=history_F,
        hypervolumes=hypervolumes,
        ref_point=ref,
    )


if __name__ == "__main__":
    from .instance import load_dumas

    inst = load_dumas("data/dumas/n20w20.001.txt")
    cfg = NSGAConfig(pop_size=50, n_generations=100)
    res = run_nsga(inst, cfg, seed=0)
    print(f"front size: {len(res.front_F)}")
    print(f"distancia min..max: {res.front_F[:, 0].min():.0f}..{res.front_F[:, 0].max():.0f}")
    print(f"violacao min..max:  {res.front_F[:, 1].min():.0f}..{res.front_F[:, 1].max():.0f}")
    print(f"hypervolume final:  {res.hypervolumes[-1]:.2e}")
    print(f"ref point:          {res.ref_point}")
