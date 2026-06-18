"""Medidas de tamanho de efeito para comparação entre algoritmos.

Cliff's delta é não-paramétrico e adequado para amostras pequenas
(R3 da rubrica pede "tamanho do efeito, não apenas significância").
Hedges' g é a versão de Cohen's d com correção de bias para n pequeno.

Convenções:
    cliffs_delta(x, y) ∈ [-1, 1]
        Negativo  → valores de x tendem a ser menores que os de y.
        Positivo  → valores de x tendem a ser maiores que os de y.
        Em otimização (minimização), preferimos delta negativo: x melhor que y.

    Magnitudes (Romano et al., 2006):
        |δ| < 0.147  negligenciável
        |δ| < 0.330  pequeno
        |δ| < 0.474  médio
        senão        grande
"""

from __future__ import annotations

import numpy as np


def cliffs_delta(x, y) -> float:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    nx, ny = x.size, y.size
    if nx == 0 or ny == 0:
        return float("nan")
    diff = x[:, None] - y[None, :]
    gt = int(np.sum(diff > 0))
    lt = int(np.sum(diff < 0))
    return (gt - lt) / (nx * ny)


def cliffs_magnitude(d: float) -> str:
    ad = abs(d)
    if ad < 0.147:
        return "negligível"
    if ad < 0.330:
        return "pequeno"
    if ad < 0.474:
        return "médio"
    return "grande"


def hedges_g(x, y) -> float:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    nx, ny = x.size, y.size
    if nx + ny <= 2:
        return float("nan")
    sx2 = float(x.var(ddof=1)) if nx > 1 else 0.0
    sy2 = float(y.var(ddof=1)) if ny > 1 else 0.0
    pooled = np.sqrt(((nx - 1) * sx2 + (ny - 1) * sy2) / (nx + ny - 2))
    diff = float(x.mean() - y.mean())
    if pooled == 0.0:
        return 0.0 if diff == 0.0 else (np.sign(diff) * float("inf"))
    d = diff / pooled
    J = 1.0 - 3.0 / (4.0 * (nx + ny) - 9.0)
    return d * J


if __name__ == "__main__":
    ag = [377, 378, 374, 378, 378]
    rnd = [610, 590, 605, 620, 615]
    d = cliffs_delta(ag, rnd)
    g = hedges_g(ag, rnd)
    print(f"AG vs Random  Cliff's delta = {d:+.3f} ({cliffs_magnitude(d)})  "
          f"Hedges' g = {g:+.3f}")
