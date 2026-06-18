# Pré-final — Código autocontido

Este diretório contém todo o necessário para reproduzir o pré-final do
projeto TSPTW (INF0415, UFG 2026/2) sem depender do repositório
principal. O diferencial implementado é o **D1 — hibridização memetic
NSGA-II + 2-opt Pareto**.

## Conteúdo

```
codigo/
├── README.md
├── requirements.txt
├── data/dumas/*.txt
├── src/
│   ├── instance.py
│   ├── evaluation.py
│   ├── operators.py
│   ├── baseline_nn.py
│   ├── baseline_random.py
│   ├── ga.py
│   ├── stats.py
│   ├── experiment.py
│   ├── nsga.py                # NSGA-II + suporte a modo memetic
│   ├── experiment_moo.py      # runner com --memetic-period
│   └── local_search.py        # 2-opt Pareto (D1)                       ← NOVO
└── notebooks/
    ├── checkpoint1_figures.py
    ├── checkpoint2_figures.py
    └── pre_final_figures.py   # 4 figuras de comparação puro vs memetic
```

## Como reproduzir (3 comandos)

```bash
pip install -r requirements.txt
python -m src.experiment_moo --instance cp1 --seeds 5 \
    --memetic-period 100 --memetic-top-k 5 --tag pre_final
python notebooks/pre_final_figures.py
```

> Para a comparação **puro vs memetic** (figuras), você precisa também
> dos resultados do NSGA-II puro do CP2:
> `python -m src.experiment_moo --instance cp1 --seeds 5 --tag cp2`

## Como o D1 funciona

A cada `--memetic-period` gerações (default = 100), o NSGA-II:
1. Seleciona `--memetic-top-k` (default = 5) indivíduos aleatórios da
   fronteira não-dominada atual.
2. Aplica busca local 2-opt sob critério de dominância de Pareto
   (`src/local_search.py`).
3. Substitui os indivíduos no pool com versões dominantes encontradas.

Para desabilitar o memetic (rodar NSGA-II puro), basta omitir a flag
`--memetic-period` ou passar `--memetic-period 0`.

## Resultados esperados
Ver `entregas/pre_final/relatorio.md` no repositório principal. Com 5
sementes o ganho foi modesto e assimétrico (~+3,7% HV em n20w80.001,
menos nas outras). A entrega final reexecutou com 10 sementes e
revelou que o D1 **dobra a viabilidade em n20w80.001** (de 20% para
40% das sementes).
