# TSPTW — Projeto Final INF0415

Resolução do Problema do Caixeiro Viajante com Janelas de Tempo (TSPTW) com metaheurísticas, em cumprimento ao Projeto Final da disciplina **INF0415 — Heurísticas e Modelagem Multiobjetivo** (Bacharelado em Inteligência Artificial, UFG, 2026/2).

Repositório: https://github.com/DavideSouzaAndrade/heuristica_proj

## Equipe

| Nome | Matrícula |
|------|-----------|
| Frederico Barbosa Relvas | 202403902 |
| Cindy Stephanie Gomes Rabelo | 202403898 |
| Davi de Souza Andrade | 202403901 |
| Marcos Vinicius Moreira dos Anjos | 202400762 |
| João Guilherme da Silva Chaveiro | 202403908 |

## Cronograma

| Semana | Marco | Estado |
|---|---|---|
| 9 | Proposta | concluído (`proposta_tsptw.md`) |
| 11 | Checkpoint 1 — single-objective + baseline + 5 sementes | em andamento |
| 13 | Checkpoint 2 — NSGA-II multiobjetivo | pendente |
| 15 | Pré-final — diferencial + relatório 70% | pendente |
| 16 | Entrega final | pendente |

## Estrutura do repositório

```
heuristica_final/
├── data/dumas/           # instâncias TSPTW (formato Dumas)
├── src/                  # código-fonte
│   ├── instance.py       # carregamento das instâncias
│   ├── evaluation.py     # função objetivo TSPTW
│   ├── baseline_nn.py    # baseline Nearest Neighbor com janelas
│   ├── operators.py      # operadores genéticos (OX, mutação, seleção)
│   ├── ga.py             # algoritmo genético
│   └── experiment.py     # runner experimental com sementes
├── notebooks/            # análises e figuras
├── reports/              # entregas dos checkpoints
└── results/              # logs e tabelas geradas
```

## Como reproduzir (Checkpoint 1)

```bash
pip install -r requirements.txt
python -m src.experiment --instance data/dumas/n20w20.001.txt --seeds 5
jupyter notebook notebooks/checkpoint1.ipynb
```

## Referência

- Documento do projeto: `heuristica_trab_final.pdf`
- Proposta entregue (Semana 9): `proposta_tsptw.md`
