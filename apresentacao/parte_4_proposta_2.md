# Parte 4 — Proposta 2: NSGA-II multiobjetivo + diferencial D1 memetic  (5 minutos · slides 7–9)

Você apresenta a **parte mais importante e original do projeto**: a abordagem multiobjetivo via NSGA-II e o diferencial D1 (hibridização memetic com 2-opt Pareto). É também a parte mais longa (5 min) e cobre 3 slides. Sua função narrativa é mostrar como a Proposta 2 resolve o gargalo da Proposta 1, identificar um novo problema que ela introduz, e mostrar como o D1 corrige esse novo problema.

## Visão geral
Cobre:
- A formulação multiobjetivo: distância vs violação como **dois objetivos independentes**.
- O NSGA-II via `pymoo`: o que muda em relação ao AG.
- O resultado dramático: factibilidade dispara em janelas estreitas.
- O paradoxo identificado: em n20w80.001, NSGA-II é **pior** que o AG.
- O diferencial D1 (memetic): 2-opt Pareto + seleção de pontos da fronteira.
- A confirmação da hipótese: D1 dobra a factibilidade exatamente onde foi desenhado para ajudar.

## O que você precisa internalizar

### Conceito 1 — Por que multiobjetivo (em 1 frase)
> "Em vez de pré-decidir a 'taxa de câmbio' λ entre distância e violação, deixamos o algoritmo construir TODA a fronteira de Pareto — a família de soluções não-dominadas — e quem decide qual usar é o decisor humano, em vez do código."

### Conceito 2 — O que é dominância de Pareto
Uma solução A **domina** B se A é ≤ B em todos os objetivos E A é < B em pelo menos um. A fronteira de Pareto é o conjunto de soluções que **ninguém domina** — cada uma representa um trade-off legítimo.

### Conceito 3 — NSGA-II em 3 frases
1. Mantém uma população, faz crossover e mutação como qualquer AG.
2. Em vez de selecionar pelo fitness escalar, **ordena por rank de não-dominância** (fronteiras de Pareto).
3. Dentro de cada fronteira, prefere indivíduos com maior **crowding distance** (mais isolados, contribuindo para diversidade).

### Conceito 4 — O paradoxo do n20w80.001
- AG (penalização): **80% factível** (8 de 10 sementes).
- NSGA-II puro: **20% factível** (2 de 10 sementes).
- **NSGA-II perde para o AG aqui.** Por quê? O crowding distance prioriza diversidade. Em n20w80.001 há muitos pontos "quase-factíveis" (violação 1–10) competindo pelo mesmo nicho. O algoritmo descarta candidatos próximos da viabilidade em favor de espalhamento. **Resultado contra-intuitivo, mas estrutural.**

### Conceito 5 — O diferencial D1 (memetic com 2-opt Pareto)
- A cada **100 gerações**, escolhe **5 indivíduos aleatórios** da fronteira atual.
- Aplica **2-opt** (inverte um subsegmento) sob critério de **dominância estrita** — só aceita um vizinho que melhora pelo menos um objetivo sem piorar o outro.
- Reinjeta o melhorado na população do NSGA-II.
- **Resultado:** em n20w80.001, a factibilidade **dobra**, de 2/10 para **4/10 sementes** que cruzam viol=0. Sem custo computacional perceptível.

## Números-chave (memorize)

### Tabela principal — factibilidade dos 3 métodos com 10 sementes

| Instância | AG (SO-λ) | NSGA-II puro | **NSGA-II + 2-opt (D1)** |
|---|---:|---:|---:|
| n20w20.001 | 3/10 (30%) | **9/10 (90%)** | 8/10 (80%) |
| n20w40.001 | 8/10 (80%) | 9/10 (90%) | **10/10 (100%)** |
| n20w60.001 | 10/10 (100%) | 10/10 (100%) | 10/10 (100%) |
| n20w80.001 | 8/10 (80%) | **2/10 (20%)** | **4/10 (40%)** |
| n20w100.001 | 10/10 (100%) | 10/10 (100%) | 10/10 (100%) |

### Hiperparâmetros do NSGA-II
- pop_size = **100** (metade do AG — compensa o custo O(N²) da ordenação não-dominada).
- n_generations = **1500** (mesmo do AG).
- Operadores: **mesmos OX e inversão do AG** — comparação justa.
- Framework: **pymoo 0.6.1**.

### Hiperparâmetros do D1 (memetic)
- memetic_period = **100** gerações.
- memetic_top_k = **5** indivíduos por episódio.
- memetic_max_iter = **5** iterações de 2-opt por indivíduo.

### Métrica de hypervolume
- Cálculo com **ponto de referência unificado** entre métodos (max observado × 1,1 + 1).
- HV ratio memetic/puro: entre **0,993 e 1,037** (-0,7% a +1,0%) — **ganho é em factibilidade, não em HV global**.
- Custo computacional: **memetic 98s/seed vs puro 102s/seed** — sem overhead perceptível.

## Roteiro sugerido (slide a slide)

### Slide 7 — MO vs SO: a vantagem nas janelas estreitas
**Tempo: 1 min 30 s**

O que falar:
1. **Apresente a formulação multiobjetivo (30 s)**:
   - "Em vez de somar distância e violação com um λ pré-fixado, o NSGA-II trata os dois como objetivos independentes."
   - "Cada solução é avaliada pelo **rank de não-dominância** — quantos indivíduos a dominam — e pelo **crowding distance** que prefere espalhamento na fronteira."
2. **Mostre o resultado dramático em n20w20.001 (30 s)**:
   - Aponte para a comparação: "AG era 30% factível em janelas estreitas. NSGA-II é **90%**."
   - "O motivo é estrutural: na formulação penalizada, o ponto '374 com pequena violação' tem fitness menor que '378 factível' — o algoritmo prefere o atalho infactível. No NSGA-II essas duas soluções são mutuamente **não-dominadas** e ambas são preservadas na fronteira."
3. **Mostre a fronteira de Pareto (30 s)** (figura 3 do relatório):
   - "Esse gráfico mostra a fronteira de Pareto para n20w20.001 com os 10 pontos do AG sobrepostos como X vermelhos."
   - "Onde o AG conseguiu o ótimo factível, ele coincide com a fronteira. Onde ele falhou, está **dominado** pela fronteira NSGA-II. Em outras palavras: o NSGA-II encontra tudo que o AG encontra, e muito mais."

### Slide 8 — O paradoxo de n20w80.001 (motiva o D1)
**Tempo: 1 min 30 s**

O que falar:
1. **Anuncie o paradoxo (20 s)**:
   - "Em quatro das cinco instâncias, NSGA-II é igual ou melhor que o AG."
   - "Mas em n20w80.001 acontece o oposto: **AG é 80% factível, NSGA-II puro é apenas 20%**."
   - **Pause para a plateia processar**.
2. **Explique a causa (40 s)**:
   - "A causa é o próprio mecanismo de **crowding distance**, que prioriza diversidade. Quando há muitas soluções quase-factíveis na fronteira — com violação 1 a 10 — elas competem pelo mesmo nicho, e o NSGA-II descarta algumas em favor de espalhamento."
   - "Em contraste, a formulação penalizada do AG **empurra** tudo para viol=0 por causa do λ alto. Cada método tem um viés diferente."
3. **Anuncie o D1 como resposta (30 s)**:
   - "Esse é o gap que motivou nosso diferencial. Implementamos hibridização memetic: a cada 100 gerações, escolhemos 5 indivíduos aleatórios da fronteira de Pareto e aplicamos busca local 2-opt sob critério de dominância estrita."
   - "Cita explicitamente: 'a hipótese pré-registrada era — o 2-opt vai empurrar pontos quase-factíveis para a fronteira de viabilidade.'"

### Slide 9 — D1 valida a hipótese
**Tempo: 2 min**

O que falar:
1. **O resultado em n20w80.001 (45 s)**:
   - "Resultado com 10 sementes: NSGA-II puro tem 2 de 10 sementes factíveis. NSGA-II + 2-opt tem **4 de 10** — **dobra** a factibilidade."
   - "Mais que isso: os pares de sementes que cruzaram a fronteira de viabilidade são justamente aqueles onde, na versão pura, a violação remanescente era pequena (entre 1 e 188). O 2-opt resolveu os 'casos fáceis' e revelou os 'casos difíceis'."
2. **Análise crítica honesta (45 s)**:
   - "**Foi exatamente o que a hipótese previa — não mais, não menos.** O ganho de hypervolume global é pequeno (entre −1% e +1%); o ganho concreto é em **factibilidade pontual em n20w80.001**."
   - "Em n20w20.001 perdemos uma semente factível (9/10 → 8/10) — variação dentro da margem de ruído estatístico com 10 sementes."
   - "A interpretação metodológica é importante: **a seleção aleatória dos 5 pontos da fronteira é o gargalo do D1**. Uma versão dirigida — focar 2-opt nos pontos com violação pequena mas positiva — é o trabalho futuro mais natural."
3. **Custo computacional (30 s)**:
   - "Surpreendentemente, o memetic não custa mais. Tempo médio: 98 segundos por seed contra 102 do puro. A intuição é que o 2-opt concentra a fronteira, e isso acelera ligeiramente a ordenação não-dominada interna do pymoo."

## Transição para o próximo apresentador
> "Resumindo: NSGA-II resolve a fragilidade da Proposta 1 em janelas estreitas, mas tem um ponto cego em janelas médias. O D1 memetic corrige esse ponto cego — não dramaticamente, mas direcionado. Passo para o(a) [colega da Parte 5], que fecha com as conclusões e implicações."

## Perguntas que você pode receber

**P: Por que pop=100 no NSGA-II e pop=200 no AG?**
> "Equalização computacional. O NSGA-II tem custo O(N²) por geração na ordenação não-dominada e crowding distance. Reduzir pop para 100 mantém o número total de avaliações em ~150 000 — mesma ordem do AG — sem dobrar o tempo de execução. É uma escolha de design para garantir comparação justa em tempo de parede."

**P: Por que vocês não usaram operadores específicos do pymoo?**
> "Decisão deliberada: reusamos exatamente o mesmo OX e a mesma mutação por inversão do AG do CP1. Isso garante que qualquer diferença entre AG e NSGA-II venha do critério de seleção, não dos operadores genéticos. Comparação justa."

**P: O ganho de 20% para 40% em uma instância é significativo?**
> "Dobra. É um ganho de 100% na métrica. Com 10 sementes essa diferença não é ruído — a hipótese pré-registrada é claramente confirmada. Mas reconhecemos no relatório que com mais sementes ou mais instâncias dessa família n=20 a magnitude pode ser refinada."

**P: Por que o D1 não tem custo extra esperado?**
> "Esperávamos 10-20% de custo extra teórico — o 2-opt faz O(n²) avaliações por chamada, vezes 5 indivíduos a cada 100 gerações. Na prática o overhead foi nulo. A explicação plausível é que o 2-opt concentra a fronteira (reduz a dispersão dos objetivos), o que acelera o sorting interno do pymoo. Mas não é o ponto central do nosso trabalho."

**P: Por que 2-opt Pareto e não 2-opt simples?**
> "Em multiobjetivo, 'melhor' não é um valor único. O 2-opt simples (que minimiza distância) iria piorar a violação. O 2-opt Pareto exige que o vizinho domine o atual — ≤ em ambos os objetivos, < em pelo menos um. Garante que não desfazemos progresso em nenhum objetivo."

**P: Por que vocês não implementaram a 'versão dirigida' do D1 já?**
> "Escopo. O pré-final pedia 'pelo menos um diferencial bem executado' e o resultado obtido valida a hipótese. A versão dirigida é trabalho futuro número um na nossa Seção 7. A vantagem científica é que reportamos o resultado honesto e a evolução natural — em vez de fingir que o D1 v1 já é a versão final."

**P: O hypervolume não melhorou. O D1 vale a pena?**
> "Pergunta excelente, e a resposta é nuançada. **Para qualidade de fronteira (HV), o ganho é marginal.** Mas para **factibilidade pontual em casos difíceis**, dobrar a taxa de sucesso é prático: significa que um decisor que rode o NSGA-II memetic em n20w80.001 tem duas vezes mais chance de obter uma rota viável. Em produção, isso é o que importa."

**P: Como vocês validaram que o pymoo está implementando NSGA-II corretamente?**
> "Pymoo é um framework consolidado com publicação em IEEE Access 2020 (Blank & Deb), validação empírica em benchmarks DTLZ/ZDT, e usado em centenas de papers. Nossa contribuição é a **integração** com nossos operadores customizados (OX, inversão) via as interfaces `Sampling`, `Crossover`, `Mutation` da pymoo. Validamos visualmente que as fronteiras geradas têm formato esperado (não-dominância) e que atingimos os ótimos conhecidos da literatura."

## Dicas de execução

- **Você tem 5 min — é a parte mais longa.** Pratique para não passar de 5 min 30 s.
- **A frase "dobra a factibilidade" é a mais importante.** Use-a literalmente — pause depois.
- **Não esconda o paradoxo n20w80.** Ele é o que torna a história interessante. Mostre que NSGA-II perde para AG ali — isso só fortalece o D1.
- **Não venda o D1 como milagroso.** Reportar honestamente "ganho dirigido, não geral" é o que o avaliador vai valorizar na rubrica de discussão crítica.
- **Cuidado com termos técnicos:** "rank de não-dominância", "crowding distance" — explique cada um na primeira menção, depois pode usar.

## Materiais de apoio

- Relatório: Seções 4.3, 4.4, 5.2 e 5.3 do [`relatorio.pdf`](../entregas/final/relatorio.pdf).
- Código do NSGA-II: [`../src/nsga.py`](../src/nsga.py).
- Código do 2-opt Pareto: [`../src/local_search.py`](../src/local_search.py).
- Figuras-chave: `fig3_pareto_nsga_vs_ag.png`, `fig5_pareto_puro_vs_mem.png`, `fig6_feasibility.png`, `fig7_n20w80_zoom.png` em [`../entregas/final/figuras/`](../entregas/final/figuras/).
