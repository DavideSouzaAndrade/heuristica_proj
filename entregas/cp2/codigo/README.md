# Checkpoint 2 — Código autocontido

Este diretório contém todo o necessário para reproduzir o Checkpoint 2
do projeto TSPTW (INF0415, UFG 2026/2) sem depender do repositório
principal.

## Conteúdo

```
codigo/
├── README.md
├── requirements.txt
├── data/dumas/*.txt
├── src/
│   ├── instance.py            # loader Dumas
│   ├── evaluation.py          # f = (dist, violação) — agora multiobjetivo
│   ├── operators.py
│   ├── baseline_nn.py
│   ├── baseline_random.py
│   ├── ga.py                  # AG do CP1, reusado para comparação
│   ├── stats.py
│   ├── experiment.py          # runner SO (CP1)
│   ├── nsga.py                # NSGA-II via pymoo, custom OX/inversão  ← NOVO
│   └── experiment_moo.py      # runner multiobjetivo                    ← NOVO
└── notebooks/
    ├── checkpoint1_figures.py # figuras do CP1 (para contexto)
    └── checkpoint2_figures.py # 4 figuras do CP2: fronteira de Pareto, HV,
                               #                   NSGA-II vs AG, tamanho de fronteira
```

## Como reproduzir (3 comandos)

```bash
pip install -r requirements.txt
python -m src.experiment_moo --instance cp1 --seeds 5 --tag cp2
python notebooks/checkpoint2_figures.py
```

Saídas:
- Fronteiras + HV em `results/runs/cp2/<instância>/`
- Figuras em `reports/figures/cp2/`

> Para comparar com a versão single-objective do CP1, rode antes:
> `python -m src.experiment --instance cp1 --seeds 5 --tag cp1`

## Dependências
`pymoo 0.6.1+` é a única adição em relação ao CP1.

## Resultados esperados
Veja `entregas/cp2/checkpoint2.md` no repositório principal — o NSGA-II
deve atingir os ótimos conhecidos da literatura (378, 254, 335, 237) em
4 das 5 instâncias, com `n20w80.001` como exceção (40% factível) que
motiva o diferencial D1 do pré-final.
