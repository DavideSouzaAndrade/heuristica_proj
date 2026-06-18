"""Operadores genéticos para representações por permutação.

Implementa:
    * Order Crossover (OX) — preserva ordem relativa do segmento de um
      pai e completa com os elementos restantes na ordem em que aparecem
      no outro pai.
    * Mutação por swap (troca de dois elementos).
    * Mutação por inversão (inverte um subsegmento).
    * Seleção por torneio de tamanho k.
"""

from __future__ import annotations

import numpy as np


def order_crossover(
    p1: np.ndarray, p2: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    n = p1.size
    a, b = sorted(rng.integers(0, n, size=2).tolist())
    if a == b:
        b = min(n - 1, a + 1)

    child = np.full(n, -1, dtype=p1.dtype)
    child[a : b + 1] = p1[a : b + 1]
    taken = set(child[a : b + 1].tolist())

    pos = (b + 1) % n
    for k in range(n):
        gene = int(p2[(b + 1 + k) % n])
        if gene in taken:
            continue
        child[pos] = gene
        pos = (pos + 1) % n
    return child


def swap_mutation(perm: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    n = perm.size
    out = perm.copy()
    i, j = rng.integers(0, n, size=2).tolist()
    out[i], out[j] = out[j], out[i]
    return out


def inversion_mutation(perm: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    n = perm.size
    a, b = sorted(rng.integers(0, n, size=2).tolist())
    if a == b:
        b = min(n - 1, a + 1)
    out = perm.copy()
    out[a : b + 1] = out[a : b + 1][::-1]
    return out


def tournament_selection(
    fitness: np.ndarray, k: int, rng: np.random.Generator
) -> int:
    idx = rng.integers(0, fitness.size, size=k)
    return int(idx[np.argmin(fitness[idx])])
