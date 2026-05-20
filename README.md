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
| 13 | Checkpoint 2 — NSGA-II multiobjetivo | em andamento |
| 15 | Pré-final — diferencial + relatório 70% | pendente |
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
    └── cp1/                # Semana 11 — Checkpoint 1
        ├── checkpoint1.md  # relatório
        ├── figuras/        # 4 figuras PNG
        └── resultados/     # CSVs, summaries, históricos de convergência
```

O código (`src/`, `data/`, `notebooks/`) é uma única fonte de verdade que evolui ao longo do projeto. Cada entrega vira uma pasta congelada em `entregas/` e uma tag Git (`cp1`, `cp2`, ...) que permite recuperar o estado exato do código naquele momento via `git checkout <tag>`.

## Como reproduzir o Checkpoint 1

```bash
git clone https://github.com/DavideSouzaAndrade/heuristica_proj.git
cd heuristica_proj
git checkout cp1                       # opcional: snapshot exato da entrega
pip install -r requirements.txt
python -m src.experiment --instance cp1 --seeds 5
python notebooks/checkpoint1_figures.py
```

Saídas vão direto para `entregas/cp1/resultados/` e `entregas/cp1/figuras/`.

## Referência

- Enunciado oficial da disciplina: `heuristica_trab_final.pdf` (na raiz, não é entrega nossa)
- Proposta inicial (Semana 9): [`entregas/proposta/proposta_tsptw.md`](entregas/proposta/proposta_tsptw.md)
