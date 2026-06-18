# Entrega final — Código autocontido

Este diretório contém todo o necessário para reproduzir a entrega final
do projeto TSPTW (INF0415, UFG 2026/2) — incluindo geração do
`relatorio.pdf` via Pandoc + Edge headless.

## Conteúdo

```
codigo/
├── README.md
├── requirements.txt
├── build.ps1                  # pipeline Markdown → HTML → PDF
├── relatorio.css              # CSS de impressão A4
├── data/dumas/*.txt
├── src/                       # código completo (AG + NSGA-II + memetic)
│   ├── instance.py
│   ├── evaluation.py
│   ├── operators.py
│   ├── baseline_nn.py
│   ├── baseline_random.py
│   ├── ga.py
│   ├── stats.py
│   ├── experiment.py          # AG: summary → *_summary_so.json
│   ├── nsga.py
│   ├── experiment_moo.py      # NSGA-II: aceita --suffix _memetic
│   └── local_search.py
└── notebooks/
    ├── checkpoint1_figures.py
    ├── checkpoint2_figures.py
    ├── pre_final_figures.py
    └── final_figures.py       # 8 figuras consolidadas do relatório final
```

## Como reproduzir (1 setup + 4 runs)

```bash
pip install -r requirements.txt

# 1) AG single-objective + busca aleatória (10 sementes)
python -m src.experiment --instance cp1 --seeds 10 --tag final

# 2) NSGA-II puro multiobjetivo (10 sementes)
python -m src.experiment_moo --instance cp1 --seeds 10 --tag final

# 3) NSGA-II + 2-opt Pareto memetic, D1 (10 sementes)
python -m src.experiment_moo --instance cp1 --seeds 10 \
    --memetic-period 100 --tag final --suffix _memetic

# 4) Gerar as 8 figuras consolidadas
python notebooks/final_figures.py
```

Tempo total estimado: ~3,5 horas (sequencial).

## Reconstruir o relatório.pdf (opcional)

Se quiser regerar `relatorio.pdf` a partir do markdown:

```powershell
# Requer pypandoc-binary (em requirements.txt) e Microsoft Edge
cd ..      # voltar para entregas/final/
pwsh build.ps1
```

O `build.ps1` localiza dinamicamente o Pandoc (do pacote pypandoc-binary
do pip) e o Microsoft Edge (em paths padrão do Windows) e gera:
- `relatorio.pdf` (PDF A4 via Edge headless)
- `relatorio.html` (HTML standalone com figuras embarcadas)
- `slides.html` (apresentação reveal.js)

## Achado central
A tabela-chave da entrega final (10 sementes × 5 instâncias × 3 métodos):

| Instância | AG-λ feas | NSGA-II puro feas | NSGA-II memetic feas |
|---|---:|---:|---:|
| n20w20.001 | 30% | 90% | 80% |
| n20w40.001 | 80% | 90% | 100% |
| n20w60.001 | 100% | 100% | 100% |
| n20w80.001 | 80% | **20%** | **40%** |
| n20w100.001 | 100% | 100% | 100% |

O D1 (memetic) **dobra** a viabilidade em `n20w80.001` — exatamente onde
foi desenhado para ajudar, validando a hipótese pré-registrada no CP2.

## Cumprimento dos requisitos
- R1 (modelagem explícita) ✓
- R2 (3 metaheurísticas distintas) ✓
- R3 (10 sementes + Wilcoxon + Bonferroni + Cliff's δ + Hedges' g) ✓
- R4 (2 baselines: NN-urgency + busca aleatória) ✓
- R5 (8 figuras de qualidade publicável) ✓
- R6 (reprodutível em poucos comandos) ✓
- D1 (hibridização memetic NSGA-II + 2-opt) ✓
