# Parte 5 — Conclusão + Q&A  (2 minutos · slides 10–12)

Você fecha a apresentação. Suas responsabilidades:
1. **Consolidar a história** em 1 minuto: o achado central que conecta as duas propostas.
2. **Listar trabalhos futuros** concretos em 30 segundos.
3. **Encerrar e abrir para perguntas** em 30 segundos.

E depois você (junto com o grupo) responde 5 minutos de perguntas.

## Visão geral
Cobre:
- Recap em uma frase do projeto inteiro.
- Síntese dos três métodos como um espectro (não como competidores).
- Trabalhos futuros priorizados.
- Encerramento e Q&A.

## O que você precisa internalizar

### Conceito 1 — A frase-resumo do projeto inteiro
Memorize esta frase — ela é o que liga as duas propostas:

> "Mostramos empiricamente que a formulação multiobjetivo do TSPTW domina a formulação penalizada em janelas estreitas (90% vs 30% de factibilidade em n20w20.001), tem um ponto cego em janelas médias (n20w80.001: 20% vs 80%), e que a hibridização memetic com 2-opt Pareto corrige esse ponto cego (dobra para 40%) sem custo computacional perceptível."

Você não precisa decorar palavra por palavra, mas precisa ter os **três fatos** memorizados:
1. **MO domina SO em janelas estreitas** (90% vs 30%).
2. **MO tem ponto cego em n20w80** (20% vs 80%).
3. **D1 corrige o ponto cego** (dobra para 40%) sem custo extra.

### Conceito 2 — Os três métodos formam um espectro, não competidores
- **AG (SO-λ)**: simples, robusto onde a região factível é fácil de encontrar.
- **NSGA-II puro (MO)**: dispensa o ajuste de λ, dá toda a fronteira de Pareto, dominante em janelas estreitas.
- **NSGA-II memetic (MO+LS)**: preserva a vantagem do MO e recupera robustez de viabilidade onde o crowding distance espalha demais.

A contribuição do projeto **não é dizer "X é o melhor"** — é **mapear o trade-off** entre as três formulações em diferentes regimes de dificuldade.

### Conceito 3 — Trabalhos futuros priorizados (4 itens)
1. **D1 v2 — seleção dirigida:** trocar a escolha aleatória dos 5 pontos da fronteira para priorizar pontos com violação pequena mas positiva. Hipótese: converte o ganho marginal de HV em ganho concreto de viabilidade.
2. **Expansão experimental:** todas as 25 instâncias `n20w*` do conjunto Dumas para reduzir viés de instância individual.
3. **HPO via Optuna (D3 do enunciado):** afinar `pop_size`, `n_generations`, parâmetros do memetic.
4. **Escalabilidade:** repetir o protocolo para n=40 e n=60. Hipótese: ganho do memetic cresce com a dimensão.

### Conceito 4 — Limitações reconhecidas (importante para R3 "discussão crítica")
- $n = 20$ é pequeno. Em problemas maiores o memetic costuma ser ainda mais importante.
- 10 sementes dão poder estatístico para o Wilcoxon ($p_{\min} \approx 10^{-3}$), mas variabilidade em medidas categóricas (factibilidade pontual) ainda é alta.
- Usamos apenas a primeira instância de cada largura — viés de instância individual.

## Números-chave (memorize)

A tabela final em uma forma compacta para citação:

| | AG-λ | MO puro | MO+LS |
|---|---:|---:|---:|
| n20w20.001 (estreita) | 30% | **90%** | 80% |
| n20w80.001 (média) | **80%** | 20% | **40%** ↑↑ |
| Demais (n20w40, 60, 100) | 80–100% | 90–100% | 100% |

## Roteiro sugerido (slide a slide)

### Slide 10 — Conclusões
**Tempo: 1 min**

O que falar:
1. **Abra com a frase-resumo (30 s)**:
   - "Em uma frase, o projeto mostrou empiricamente três fatos: (1) a formulação multiobjetivo é mais robusta que a penalizada em janelas estreitas, (2) ela tem um ponto cego específico em janelas médias por causa do mecanismo de crowding distance, e (3) a hibridização memetic com 2-opt sob dominância de Pareto corrige esse ponto cego — dobra a factibilidade exatamente onde foi desenhada para ajudar, sem custo computacional perceptível."
2. **Reframe o resultado como espectro (30 s)**:
   - "Vale notar: nenhum dos três métodos é universalmente o melhor. Eles formam um espectro. AG é a baseline confiável; NSGA-II puro é dominante em janelas estreitas e dá toda a fronteira de Pareto para o decisor; memetic recupera robustez em casos onde o NSGA-II puro falha."
   - "**A contribuição do projeto não é eleger um vencedor — é mapear esse trade-off**."

### Slide 11 — Trabalhos futuros
**Tempo: 30 s**

O que falar (rápido, sem detalhar cada um):
- **D1 v2** — seleção dirigida dos pontos para 2-opt (priorizar violação pequena mas positiva). Hipótese: converte ganho marginal de HV em ganho concreto de viabilidade.
- **Expansão para as 25 instâncias** n=20 do conjunto Dumas.
- **HPO via Optuna** — diferencial D3 do enunciado.
- **Escalabilidade para n=40 e n=60** — testar se o ganho do memetic cresce com a dimensão.
- Frase de fechamento: "O trabalho futuro mais natural é o D1 v2: usar o que aprendemos aqui para focar a busca local exatamente onde ela ajuda."

### Slide 12 — Encerramento e perguntas
**Tempo: 30 s**

O que falar:
- "Repositório público em github.com/DavideSouzaAndrade/heuristica_proj. Tag `final` aponta para o snapshot exato desta entrega — reprodutível em poucos comandos."
- "Obrigado pela atenção. Estamos abertos a perguntas."

## Roteiro Q&A — distribuição entre o grupo

Quando vier uma pergunta, **o membro responsável pelo bloco respectivo é o primeiro a responder**. Combinem isso antes:

| Tipo de pergunta | Responde |
|---|---|
| Sobre escolha do problema, motivação | Parte 1 |
| Sobre formulação, instâncias, protocolo experimental, estatística | Parte 2 |
| Sobre AG, hiperparâmetros do AG, baselines, sweep de λ | Parte 3 |
| Sobre NSGA-II, pymoo, crowding distance, D1, 2-opt Pareto, n20w80 | Parte 4 |
| Sobre trabalhos futuros, limitações, decisões de escopo | Parte 5 (você) |

Se a pergunta for "abrangente" (cruza várias partes), Parte 5 (você) decide quem responde.

## Perguntas "abrangentes" que você pode receber diretamente

**P: Se vocês tivessem mais tempo, qual seria o próximo passo?**
> "D1 v2 — versão dirigida da busca local. A evidência empírica que coletamos sugere que o gargalo atual é a seleção aleatória dos 5 pontos da fronteira para 2-opt. Priorizar pontos com violação pequena mas positiva deve converter o ganho marginal de hypervolume que observamos em ganho concreto de factibilidade em mais instâncias."

**P: Qual foi a maior dificuldade do projeto?**
> "Identificar o paradoxo do n20w80.001 e entender que ele era estrutural — não bug. Quando vimos NSGA-II perdendo para o AG em uma instância, a primeira reação foi suspeitar de erro de implementação. Mas validamos contra os ótimos da literatura, repetimos com mais sementes, e concluímos que o crowding distance tinha um viés sistemático. Reconhecer isso foi o que viabilizou o D1 com hipótese pré-registrada."

**P: O resultado de 4/10 em n20w80 é decepcionante?**
> "Não — é um resultado **honesto e direcionado**. O D1 dobrou a factibilidade exatamente na instância onde a hipótese previa que ajudaria. Que não tenha resolvido completamente (não chegou a 10/10) reflete uma limitação metodológica da seleção aleatória, e isso aponta para o D1 v2. Em ciência aplicada, ganhos parciais com explicação clara são mais valiosos que ganhos grandes inexplicáveis."

**P: Vocês validariam a implementação contra mais benchmarks?**
> "Sim, é nosso trabalho futuro #2. Usamos as 5 primeiras instâncias n=20 do Dumas — uma para cada largura média. As outras 20 da família n=20 (5 instâncias × 5 larguras − 5 já usadas = 20) reduziriam viés de instância individual. Também queremos testar n=40 e n=60 para ver como os métodos escalam."

**P: Como o trabalho se compara à literatura?**
> "Atingimos os ótimos conhecidos publicados por López-Ibáñez nas 4 instâncias factíveis: 378, 254, 335, 237. Esse é o teste-padrão de qualidade. A nossa contribuição original não é melhorar esses ótimos, é a comparação sistemática entre SO-λ, MO puro e MO+LS, com hipótese pré-registrada do D1 e validação empírica do paradoxo de crowding distance."

**P: Vocês usaram IA para gerar o código?**
> "Conforme nossa declaração no relatório, usamos Claude Code (Anthropic) como assistente de programação — estruturação do esqueleto Python, boilerplate, debugging interativo, revisão de redação. Todas as decisões metodológicas (escolha do problema, dos algoritmos, dos hiperparâmetros, do diferencial), interpretação dos resultados e conclusões são do grupo. Conforme política da disciplina, declaramos explicitamente o uso no relatório."

**P: Quanto tempo levou o projeto?**
> "Dez semanas, da Semana 7 (lançamento) à Semana 16 (entrega final). Cada checkpoint adicionou uma camada: Semana 9 proposta, Semana 11 AG single-objective, Semana 13 NSGA-II, Semana 15 diferencial memetic, Semana 16 consolidação com 10 sementes e relatório técnico."

**P: Qual a complexidade computacional total?**
> "A entrega final fez 5 instâncias × 10 sementes × 4 métodos = 200 execuções controladas. Tempo total de cerca de 3 horas e meia em hardware comum de laptop. O custo dominante é o NSGA-II (com e sem memetic), que tem O(N²) por geração na ordenação não-dominada."

## Dicas de execução

- **Cuide MUITO do tempo.** Conclusão estourar em 30 s atrasa o Q&A.
- **A frase-resumo é o ponto alto.** Pronuncie-a com calma, com pausa antes e depois.
- **No Q&A, não monopolize.** Se a pergunta é da Parte 3, deixe quem fez a Parte 3 responder primeiro. Você complementa apenas se necessário.
- **"Não sei" é uma resposta válida.** Combinado com "mas posso conferir no relatório e te respondo depois" é melhor que inventar.
- **Não comece a conclusão com 'antes de concluir...' ou 'em poucas palavras...'.** Vá direto para a frase-resumo.

## Materiais de apoio

- Relatório: Seções 6 e 7 do [`relatorio.pdf`](../entregas/final/relatorio.pdf) (discussão e conclusões).
- Tabela-resumo: Tabela 2 do relatório (factibilidade comparada AG vs MO vs MO+LS).
- Apêndice A do relatório: contribuições da equipe — útil para responder "quem fez o quê".
