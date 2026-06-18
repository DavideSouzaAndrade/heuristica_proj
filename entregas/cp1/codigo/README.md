# Checkpoint 1 — Código autocontido

Este diretório contém todo o necessário para reproduzir o Checkpoint 1
do projeto TSPTW (INF0415, UFG 2026/2) sem depender do repositório
principal.

## Conteúdo

```
codigo/
├── README.md
├── requirements.txt           # numpy, matplotlib, scipy
├── data/dumas/*.txt           # 135 instâncias Dumas TSPTW
├── src/
│   ├── instance.py            # loader das instâncias
│   ├── evaluation.py          # função objetivo TSPTW (f = dist + λ·violação)
│   ├── operators.py           # OX crossover, mutação por inversão, torneio
│   ├── baseline_nn.py         # Nearest Neighbor com critério urgency
│   ├── baseline_random.py     # busca aleatória (referência inferior)
│   ├── ga.py                  # Algoritmo Genético single-objective
│   ├── stats.py               # Cliff's δ, Hedges' g
│   └── experiment.py          # runner experimental com sementes
└── notebooks/
    └── checkpoint1_figures.py # gera as 4 figuras do CP1
```

## Como reproduzir (3 comandos)

```bash
pip install -r requirements.txt
python -m src.experiment --instance cp1 --seeds 5
python notebooks/checkpoint1_figures.py
```

Saídas:
- Resultados em `results/runs/cp1/<instância>/`
- Figuras em `reports/figures/cp1/`

> Observação: este código autocontido usa os caminhos padrão
> `results/runs/<tag>/` e `reports/figures/<tag>/`, gerados na execução.
> Compare com os artefatos congelados em `entregas/cp1/resultados/` e
> `entregas/cp1/figuras/` do repositório principal.

## Reprodutível?

Com `seeds=5` e os hiperparâmetros default
(`pop_size=200`, `n_generations=1500`, `lam=1000.0`,
`p_mutation=0.3`), os resultados devem ser idênticos aos reportados
em `entregas/cp1/checkpoint1.md`.
