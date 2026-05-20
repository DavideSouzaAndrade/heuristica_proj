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
| 9 | Proposta | ✅ entregue ([`entregas/proposta/proposta_tsptw.md`](entregas/proposta/proposta_tsptw.md)) |
| 11 | Checkpoint 1 — single-objective + baseline + 5 sementes | ✅ entregue ([`entregas/cp1/`](entregas/cp1/), tag `cp1`) |
| 13 | Checkpoint 2 — NSGA-II multiobjetivo | ✅ entregue ([`entregas/cp2/`](entregas/cp2/), tag `cp2`) |
| 15 | Pré-final — diferencial + relatório 70% | em andamento |
| 16 | Entrega final | pendente |

## Estrutura do repositório

```
heuristica_final/
├── data/dumas/             # instâncias TSPTW (formato Dumas)
├── src/                    # código-fonte (compartilhado entre checkpoints)
│   ├── instance.py         # carregamento de instâncias
│   ├── evaluation.py       # função objetivo TSPTW penalizada
│   ├── baseline_nn.py      # baseline Nearest Neighbor (urgency)
│   ├── baseline_random.py  # busca aleatória (referência inferior)
│   ├── operators.py        # operadores genéticos (OX, inversão, torneio)
│   ├── ga.py               # algoritmo genético single-objective
│   ├── stats.py            # Cliff's delta + Hedges' g
│   └── experiment.py       # runner experimental
├── notebooks/              # scripts de análise/figuras (um por checkpoint)
│   └── checkpoint1_figures.py
└── entregas/               # artefatos congelados por entrega
    ├── proposta/           # Semana 9 — proposta inicial
    │   └── proposta_tsptw.md
    ├── cp1/                # Semana 11 — Checkpoint 1 (AG + NN + Random)
    │   ├── checkpoint1.md
    │   ├── figuras/        # 4 PNGs
    │   └── resultados/
    └── cp2/                # Semana 13 — Checkpoint 2 (NSGA-II multiobjetivo)
        ├── checkpoint2.md
        ├── figuras/        # 4 PNGs (Pareto, HV, NSGA-II vs AG, |front| vs janela)
        └── resultados/     # fronteiras, HV histórico, summaries
```

O código (`src/`, `data/`, `notebooks/`) é uma única fonte de verdade que evolui ao longo do projeto. Cada entrega vira uma pasta congelada em `entregas/` e uma tag Git (`cp1`, `cp2`, ...) que permite recuperar o estado exato do código naquele momento via `git checkout <tag>`.

## Como reproduzir

```bash
git clone https://github.com/DavideSouzaAndrade/heuristica_proj.git
cd heuristica_proj
git checkout cp1     # ou cp2; opcional: snapshot exato da entrega
pip install -r requirements.txt

# Checkpoint 1 (AG single-objective + baselines)
python -m src.experiment --instance cp1 --seeds 5
python notebooks/checkpoint1_figures.py

# Checkpoint 2 (NSGA-II multiobjetivo)
python -m src.experiment_moo --instance cp1 --seeds 5 --tag cp2
python notebooks/checkpoint2_figures.py
```

Saídas vão direto para `entregas/<tag>/resultados/` e `entregas/<tag>/figuras/`.

## Referência

- Enunciado oficial da disciplina: `heuristica_trab_final.pdf` (na raiz, não é entrega nossa)
- Proposta inicial (Semana 9): [`entregas/proposta/proposta_tsptw.md`](entregas/proposta/proposta_tsptw.md)
