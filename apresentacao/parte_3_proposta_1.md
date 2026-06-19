# Parte 3 — Proposta 1: AG single-objective com penalização  (3 minutos · slide 6)

Você apresenta a **primeira abordagem** que o grupo testou: um Algoritmo Genético que trata os dois objetivos como uma soma ponderada (`f = distância + λ × violação`). Você mostra que funciona razoavelmente bem na maioria dos casos, mas tem uma limitação estrutural — e é essa limitação que motiva a Proposta 2.

## Visão geral
Cobre:
- A formulação SO-λ (single-objective com penalização) e por que ela é uma escolha "óbvia" mas problemática.
- O Algoritmo Genético implementado: hiperparâmetros e por que esses valores.
- Os baselines com que comparamos (NN-urgency e busca aleatória).
- Os resultados quantitativos com 10 sementes.
- A limitação reconhecida que motiva a próxima proposta.

## O que você precisa internalizar

### Conceito 1 — A formulação SO-λ
> "A ideia é combinar os dois objetivos em uma soma ponderada: `f(π) = distância + λ × Σ(atraso)`. O λ é o coeficiente de penalização: alto demais distorce a busca, baixo demais permite 'atalhos infactíveis'."

### Conceito 2 — Por que λ = 1000
Fizemos um *sweep* informal (λ ∈ {100, 500, 1000, 5000}). Abaixo de 1000, o AG aceita soluções "374 com pequenas violações" como melhores que "378 factível" — porque a soma penalizada do quase-factível é menor. Acima de 1000, o comportamento satura.

### Conceito 3 — A limitação estrutural
**Mesmo com λ = 1000, em janelas estreitas (n20w20.001) o AG só atinge factibilidade em 3 de 10 sementes.** A causa é que a penalização escalar é míope: não consegue distinguir entre "perto da factibilidade" e "longe da factibilidade" de forma confiável quando os ganhos de distância são pequenos. **Essa é a porta de entrada para o multiobjetivo.**

### Conceito 4 — Por que dois baselines?
- **NN-urgency** (heurística construtiva): mostra o que uma estratégia simples consegue. Determinístico — 1 execução por instância.
- **Busca aleatória** com **mesmo orçamento de avaliações do AG** (300 000 por seed): mostra o "piso" do espaço de busca. Em **3 milhões de permutações geradas, nenhuma foi factível** — quantifica empiricamente a estreiteza da região factível.

## Números-chave (memorize)

### Tabela principal — AG (SO-λ) com 10 sementes

| Instância | Random média | NN dist | AG média ± dp | AG factíveis |
|---|---:|---:|---:|---:|
| n20w20.001 | 419 | 386 | **380,4 ± 6,45** | 3/10 (30%) |
| n20w40.001 | 356 | 282 | **253,6 ± 0,84** | 8/10 (80%) |
| n20w60.001 | 412 | 393 | **337,2 ± 4,64** | 10/10 (100%) |
| n20w80.001 | 462 | 396 | **332,4 ± 14,41** | 8/10 (80%) |
| n20w100.001 | 405 | 387 | **242,1 ± 12,17** | 10/10 (100%) |

### Estatística (10 sementes)
- **Wilcoxon AG vs Random: p ≤ 0,001** em todas as 5 instâncias (após Bonferroni para 5 comparações, limiar α/5 = 0,01 — passa).
- **Wilcoxon AG vs NN: p ≤ 0,023** em todas (n20w20 fica marginal sob Bonferroni; demais com p ≤ 0,001).
- **Cliff's δ: −1,000 (grande)** em 9 das 10 comparações; em n20w20 vs NN é δ = −0,600 (grande mas não máxima).
- **Hedges' g: |g| entre 0,79 e 30,79** — todas magnitude grande.

### Hiperparâmetros do AG
- pop_size = **200**
- n_generations = **1500**
- λ = **1000** (penalização)
- p_mutation = **0,3**
- tournament k = **3**
- elite = **2**
- Operador de crossover: **OX** (Order Crossover, Davis 1985)
- Operador de mutação: **inversão de subsegmento**

## Roteiro sugerido (slide a slide)

### Slide 6 — Resultados SO-λ vs baselines
**Tempo: 3 minutos**

Estrutura recomendada (em quatro blocos):

#### Bloco A — A formulação e o algoritmo (40 s)
- "A primeira proposta foi a abordagem clássica: combinar os dois objetivos em uma soma ponderada `f = distância + λ × violação`. Usamos λ = 1000, escolhido por *sweep* informal."
- "Implementamos um AG canônico: crossover OX, mutação por inversão, torneio binário, elitismo, pop=200, gens=1500."
- Aponte para os componentes no slide.

#### Bloco B — Os baselines (40 s)
- "Comparamos com dois baselines obrigatórios pelo enunciado: Nearest Neighbor com critério `urgency` — uma heurística construtiva que prioriza cidades cuja janela está fechando — e busca aleatória com o mesmo orçamento de avaliações do AG."
- **Citar o número-chave**: "Em 3 milhões de permutações uniformes geradas pela busca aleatória, **nenhuma** respeitou todas as janelas. Esse número quantifica empiricamente a dificuldade do problema: a região factível é uma fração minúscula do espaço de busca."

#### Bloco C — Os resultados (1 min 10 s)
- Aponte para o boxplot/tabela do slide 6.
- "O AG vence ambos os baselines em distância em todas as 5 instâncias, com significância estatística após correção de Bonferroni e tamanho de efeito grande (Cliff's δ entre −0,6 e −1,0)."
- "Em particular, atingimos o ótimo conhecido da literatura — 378 para n20w20.001 — em algumas sementes, o que valida a implementação."
- **Pausa de ênfase aqui**.

#### Bloco D — A limitação que motiva a Proposta 2 (30 s)
- "**Mas existe um problema estrutural.** Em janelas estreitas, o AG só atinge factibilidade em 3 de 10 sementes em n20w20.001 — 30%. O motivo é que a penalização escalar com λ fixo é frágil: ela permite que o algoritmo prefira 'uma rota 4% mais curta com algumas violações' sobre 'a rota factível ótima'. Essa fragilidade é o que motiva a próxima proposta."
- Frase para fechar: "É a deixa para a abordagem multiobjetivo, que o(a) colega da Parte 4 vai apresentar."

## Transição para o próximo apresentador
> "Resumindo: o AG single-objective funciona, mas falha em garantir factibilidade quando as janelas apertam. Passo a palavra para o(a) [colega da Parte 4], que apresenta a abordagem multiobjetivo e o diferencial memetic."

## Perguntas que você pode receber

**P: Como vocês escolheram λ = 1000?**
> "Sweep informal com valores 100, 500, 1000 e 5000. Abaixo de 1000 o AG aceita atalhos infactíveis — uma rota mais curta com pequenas violações tem fitness menor que a rota factível ótima. Acima de 1000 o comportamento satura. Reconhecemos no relatório que um HPO via Optuna (D3 do enunciado) seria a evolução natural — está nos trabalhos futuros."

**P: Por que pop=200 e não outro valor?**
> "Compromisso entre exploração e tempo. Pop pequeno (100) converge cedo demais para a instância difícil n20w20; pop muito grande (500+) duplica o tempo sem ganho proporcional. Importante: para a Parte 4 (NSGA-II), usamos pop=100, porque o custo da ordenação não-dominada é O(N²) — equalizamos o número total de avaliações entre os métodos."

**P: O que é OX e por que escolheram esse crossover?**
> "Order Crossover, proposto por Davis em 1985. Ele copia um segmento aleatório de um pai e completa com os genes do outro pai na ordem em que aparecem, ignorando duplicatas. Preserva a ordem relativa, o que é crucial para permutações. É um padrão clássico para TSP-like problems."

**P: Por que mutação por inversão e não swap simples?**
> "Inversão tem efeito geográfico no tour — é equivalente a um pequeno 2-opt, preserva blocos grandes da permutação. Swap simples (trocar duas posições) é muito disruptivo. A literatura de TSP indica inversão como padrão para permutações de cidades."

**P: O resultado para n20w20.001 (30% factibilidade) não é decepcionante?**
> "Não, é informativo. Mostra que a formulação penalizada tem uma limitação estrutural, e isso é justamente o que motiva a Proposta 2. Se o AG resolvesse tudo, não teríamos uma história. O fato de identificarmos onde ele falha é o que nos leva ao multiobjetivo."

**P: Como sabem que atingiram o ótimo conhecido?**
> "Comparamos contra os ótimos publicados por López-Ibáñez no repositório oficial das instâncias Dumas. Para n20w20.001, o ótimo factível conhecido é 378. Conseguimos atingir 378 em algumas sementes — duas, especificamente. Isso valida que nossa implementação está correta."

## Dicas de execução

- **Não passe muito tempo nos detalhes do operador.** Quem quiser detalhar pergunta depois.
- **O número '3 milhões e zero factíveis' é a frase de ouro.** Pause depois dela.
- **Não venda o AG como ruim.** Ele é bom — só tem uma limitação específica que abre espaço para a Proposta 2.
- **Cuide do tempo: 3 min passam rápido.** Pratique cronometrando.

## Materiais de apoio

- Relatório: Seção 5.1 do [`relatorio.pdf`](../entregas/final/relatorio.pdf) (resultados SO-λ).
- Código do AG: [`../src/ga.py`](../src/ga.py).
- CSV com os resultados: [`../entregas/final/resultados/n20w20.001/n20w20.001_ga.csv`](../entregas/final/resultados/n20w20.001/n20w20.001_ga.csv) (e análogos por instância).
