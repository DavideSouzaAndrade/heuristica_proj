# Parte 2 — Contextualização  (3 minutos · slides 3–5)

Você apresenta a "régua" do projeto: como o problema foi modelado matematicamente, quais instâncias foram usadas para testar e qual foi o protocolo experimental. Sem isso, a plateia não consegue interpretar os resultados das próximas partes.

## Visão geral
Cobre:
- Formulação matemática do TSPTW (variáveis, objetivos, restrições).
- Instâncias usadas (família Dumas) e seus parâmetros (largura de janela).
- Plano experimental: número de sementes, métricas, baselines.

## O que você precisa internalizar

### Conceito 1 — Representação e dinâmica temporal

Uma solução é uma **permutação** π = (π₁, π₂, ..., π₂₀) das 20 cidades. O depósito (nó 0) é prefixo e sufixo implícitos.

O tempo de chegada em cada cidade é calculado recursivamente:

> t_k = max(t_{k-1} + d_{π_{k-1}, π_k}, e_{π_k})

A parte importante é o `max`. Ele captura a **espera permitida sem penalidade**: se você chega antes de e_i, espera. Violação só acontece quando t_k > l_{π_k}.

### Conceito 2 — Os dois objetivos
- **f₁ = distância total** do tour fechado (volta ao depósito).
- **f₂ = violação total** = Σ max(0, t_k − l_{π_k}) — soma dos atrasos em cada cidade.

O TSPTW clássico minimiza f₁ sujeito a f₂ = 0 (factibilidade estrita). Nós usamos três formulações operacionais para esses dois objetivos — esse é o ponto que vai ser explorado nas Partes 3 e 4.

### Conceito 3 — Instâncias
- Família **Dumas** (Dumas et al., 1995) — benchmark padrão na literatura.
- Usamos as 5 primeiras instâncias com **n=20 clientes**, uma para cada largura média de janela: **w ∈ {20, 40, 60, 80, 100}**.
- Janelas mais estreitas (w=20) = problema **mais difícil**; janelas largas (w=100) = mais fácil.
- O dataset **não tem coordenadas** — vem como matriz NxN de distâncias inteiras + janelas (e_i, l_i) por cidade. Tempo de serviço = 0.

### Conceito 4 — Protocolo experimental (R3 do enunciado)
- **10 sementes** por configuração (R3 plenamente atendido).
- **5 instâncias × 4 métodos × 10 sementes = 200 execuções controladas**.
- Métricas: média, desvio, mediana, intervalo; **Wilcoxon pareado** com correção de **Bonferroni**; **Cliff's δ** e **Hedges' g** como tamanhos de efeito.
- Para multiobjetivo: **hypervolume** com ponto de referência **unificado**.

## Números-chave (memorize)
- Instâncias: **Dumas** n=20, w∈{20, 40, 60, 80, 100}.
- Sementes: **10** por método (R3 do enunciado).
- Métodos comparados: **4** — AG, busca aleatória, NSGA-II puro, NSGA-II memetic.
- Ótimos conhecidos na literatura (importante para validação): **378, 254, 335, ?, 237** para n20w{20, 40, 60, 80, 100}.001 — atingimos todos eles em pelo menos uma das nossas execuções.

## Roteiro sugerido (slide a slide)

### Slide 3 — Formulação
**Tempo: 1 min 30 s**

O que falar:
1. Comece pela **representação**: "Uma solução é uma permutação das 20 cidades. O depósito é prefixo e sufixo implícitos."
2. Passe para o **cálculo de tempo**: aponte a fórmula `t_k = max(...)` e explique o `max` — "se chegamos cedo, esperamos sem penalidade; se chegamos tarde, ocorre violação."
3. Defina os **dois objetivos**: f₁ é distância, f₂ é a soma dos atrasos.
4. **Plante a pergunta de novo**: "Como otimizar f₁ e f₂ simultaneamente?"

Frase de transição interna:
> "Esses dois objetivos podem se conflitar: um tour mais curto pode chegar cedo demais em algumas cidades e tarde demais em outras. As próximas partes mostram duas formas de lidar com isso."

### Slide 4 — Métodos compartilhados (componentes do AG/NSGA-II)
**Tempo: 45 s**

O que falar:
- Os três métodos que vão ser apresentados **compartilham os mesmos operadores**: isso garante que a comparação seja justa.
- Cite rapidamente: **OX (Order Crossover, Davis 1985)**, **mutação por inversão**, **seleção por torneio binário k=3**, **elitismo top-2**.
- Diga: "A única diferença entre os métodos é o critério de seleção e o uso ou não de busca local."

Frase-chave:
> "Reusar os mesmos operadores garante que qualquer diferença nos resultados venha da formulação do problema, não do código."

### Slide 5 — Plano experimental
**Tempo: 45 s**

O que falar:
- Instâncias: 5 Dumas n=20, uma por largura de janela.
- Sementes: 10 por método (atendendo o R3 do enunciado).
- Total: 200 execuções controladas.
- Métricas: significância (Wilcoxon + Bonferroni), tamanho de efeito (Cliff's δ + Hedges' g), hypervolume (com ponto-ref unificado para comparação justa).
- **Reprodutibilidade**: 3 comandos a partir do repositório público.

## Transição para o próximo apresentador
> "Com a formulação e o protocolo no lugar, vamos à primeira proposta de solução. Passo para o(a) [colega da Parte 3], que apresenta o Algoritmo Genético com penalização."

## Perguntas que você pode receber

**P: Por que escolheram justamente essas 5 instâncias?**
> "Cobrir o gradiente de dificuldade. A largura média de janela é a métrica que controla quão difícil é a factibilidade — w=20 são janelas muito estreitas, w=100 são muito folgadas. Pegamos uma instância de cada largura para ver como cada método se comporta nesse gradiente."

**P: Por que não usaram as 25 instâncias n=20 inteiras?**
> "Custo computacional. Cada execução do NSGA-II memetic leva ~100 segundos. 10 sementes × 25 instâncias × 4 métodos = 1000 execuções, mais de 28 horas. Com 5 instâncias representativas mantemos o sinal e cabemos no orçamento. Expandir para 25 instâncias está nos trabalhos futuros."

**P: O que significa exatamente 'tempo de serviço = 0'?**
> "Que o atendimento da cidade é instantâneo no nosso modelo. É a convenção adotada por Dumas et al. 1995 nas instâncias. Se houvesse tempo de serviço não-zero, ele entraria como uma constante somada a cada t_k, mas conceitualmente nada muda."

**P: O que é Bonferroni e por que precisaram?**
> "Bonferroni é uma correção para testes estatísticos múltiplos. Quando você faz 5 comparações (uma por instância), a chance de pelo menos uma dar 'falso positivo' com α=0,05 sobe. A correção divide o limiar: ao invés de p<0,05, exigimos p<0,01. Mantemos a confiança global em 95% mesmo com 5 testes."

**P: Por que hypervolume e não outra métrica multiobjetivo?**
> "Hypervolume é a métrica padrão para qualidade de fronteira em problemas com 2-3 objetivos. Ele mede o volume do espaço dominado pela fronteira em relação a um ponto de referência. Quanto maior, melhor. A sutileza é que precisa de um ponto de referência consistente para comparações justas — por isso usamos um ponto unificado entre métodos."

## Dicas de execução

- **Cuidado com a fórmula no slide 3.** Se você só ler a fórmula, perde a plateia. Apontar e explicar verbalmente o `max` é mais didático.
- **O slide 4 é rápido.** Não pare em cada operador — você só está dizendo "compartilhamos a base, então a comparação é justa".
- **Não confunda f₂ com 'número de violações'.** A nossa f₂ é a **soma dos atrasos** (contínuo). Número de violações é outra métrica possível mas não a que usamos.

## Materiais de apoio

- Relatório: Seções 2 e 4 do [`relatorio.pdf`](../entregas/final/relatorio.pdf) (formulação e metodologia).
- Código que implementa a formulação: [`../src/instance.py`](../src/instance.py) (loader) e [`../src/evaluation.py`](../src/evaluation.py) (função objetivo).
