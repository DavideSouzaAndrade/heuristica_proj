"""Carregamento de instâncias TSPTW no formato Dumas et al. (1995).

Formato Dumas:
    linha 1: N (número total de nós, incluindo o depósito 0)
    linhas 2..N+1: matriz NxN de distâncias inteiras (travel time = distância)
    linhas N+2..2N+1: pares "e_i l_i" (janela de tempo de cada nó)

O tempo de serviço é zero. O nó 0 é o depósito; o tour parte de 0 no
instante 0 e deve retornar a 0 ao final.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class TSPTWInstance:
    name: str
    n: int
    dist: np.ndarray
    tw: np.ndarray
    depot: int = 0

    @property
    def e(self) -> np.ndarray:
        return self.tw[:, 0]

    @property
    def l(self) -> np.ndarray:
        return self.tw[:, 1]

    def horizon(self) -> float:
        return float(self.tw[self.depot, 1])


def load_dumas(path: str | Path) -> TSPTWInstance:
    path = Path(path)
    tokens = path.read_text().split()
    it = iter(tokens)
    n = int(next(it))

    dist = np.empty((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            dist[i, j] = int(next(it))

    tw = np.empty((n, 2), dtype=np.int64)
    for i in range(n):
        tw[i, 0] = int(next(it))
        tw[i, 1] = int(next(it))

    return TSPTWInstance(name=path.stem, n=n, dist=dist, tw=tw)


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "data/dumas/n20w20.001.txt"
    inst = load_dumas(path)
    print(f"instance: {inst.name}")
    print(f"nodes (incl. depot): {inst.n}")
    print(f"horizon (depot l_0): {inst.horizon()}")
    print(f"window widths min/max/mean: "
          f"{(inst.l - inst.e).min()}/{(inst.l - inst.e).max()}/{(inst.l - inst.e).mean():.1f}")
