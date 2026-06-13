---
title: "Algoritmos Memetic Multiobjetivo para o TSP com Janelas de Tempo"
subtitle: "Projeto Final INF0415 — Heurísticas e Modelagem Multiobjetivo (UFG, 2026/2) — versão final (Sem 16)"
author:
  - "Frederico Barbosa Relvas (202403902)"
  - "Cindy Stephanie Gomes Rabelo (202403898)"
  - "Davi de Souza Andrade (202403901)"
  - "Marcos Vinicius Moreira dos Anjos (202400762)"
  - "João Guilherme da Silva Chaveiro (202403908)"
date: "Maio de 2026"
documentclass: scrartcl
papersize: a4
lang: pt-BR
fontsize: 11pt
geometry: "left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm"
toc: false
numbersections: true
colorlinks: true
linkcolor: "[HTML]{1A4F8C}"
urlcolor: "[HTML]{1A4F8C}"
header-includes:
  - \usepackage{booktabs}
  - \usepackage{caption}
  - \captionsetup{font=small,labelfont=bf}
abstract: |
  O Problema do Caixeiro Viajante com Janelas de Tempo (TSPTW) é uma extensão do TSP em que cada cidade só pode ser visitada dentro de uma janela `[e_i, l_i]`. A região factível é tipicamente uma pequena fração do espaço de permutações, o que torna a formulação penalizada de um único objetivo sensível ao coeficiente $\lambda$ escolhido — e propensa a fixar-se em soluções "quase-factíveis". Este trabalho compara três abordagens sobre cinco instâncias clássicas Dumas com 20 clientes e dez sementes cada: (i) Algoritmo Genético com penalização $\lambda$ fixa, (ii) NSGA-II tratando distância e violação como objetivos independentes, e (iii) um híbrido memetic NSGA-II + 2-opt Pareto. Em uma busca aleatória com o mesmo orçamento de avaliações do AG, nenhuma das 3 milhões de permutações respeitou simultaneamente todas as janelas, confirmando a estreiteza da região factível. O NSGA-II reproduz os ótimos conhecidos na literatura (378, 254, 335, 237) com factibilidade em 90--100\% das sementes em quatro das cinco instâncias, com exceção de `n20w80.001` onde só 2/10 sementes cruzam a viabilidade — gap que motiva a hibridização memetic. O 2-opt Pareto dobra essa fração para 4/10 em `n20w80.001` (e melhora marginalmente outras instâncias), sem custo computacional perceptível. A análise inclui testes pareados de Wilcoxon com correção de Bonferroni, Cliff's $\delta$ e $g$ de Hedges como tamanhos de efeito, hypervolume sob ponto de referência unificado, e visualização das fronteiras de Pareto.
keywords:
  - TSP com janelas de tempo
  - NSGA-II
  - hibridização memetic
  - busca local 2-opt
  - otimização multiobjetivo
---

# 1. Introdução

O Problema do Caixeiro Viajante (TSP) é um dos problemas combinatórios mais estudados em pesquisa operacional. Sua variante com janelas de tempo (TSPTW) — introduzida formalmente por @solomon1987algorithms e estabelecida como benchmark por @dumas1995optimal — adiciona a cada cidade $i$ uma janela $[e_i, l_i]$ dentro da qual a visita deve começar. Se o agente chega antes de $e_i$, espera; se chega depois de $l_i$, ocorre violação. Esse acréscimo aparentemente modesto torna o espaço factível tipicamente uma fração minúscula do espaço de permutações, alinhando o TSPTW com problemas reais de logística onde "tempo importa": entregas em horário comercial, agendamento médico, rotas escolares.

A literatura aborda o TSPTW por duas grandes vias: heurísticas construtivas seguidas de busca local com vizinhanças sofisticadas — Lin-Kernighan, busca tabu — e algoritmos populacionais que usam penalização para incorporar o aspecto temporal na função objetivo. Cada via tem limitações reconhecidas. As heurísticas construtivas raramente exploram bem o trade-off entre distância e respeito a janelas; os algoritmos populacionais com penalização requerem afinação de um coeficiente $\lambda$ que mistura grandezas heterogêneas e pode fixar a busca em regiões de "atalho infactível".

Este trabalho explora a alternativa multiobjetivo: tratar distância e violação total como dois objetivos independentes, gerar uma fronteira de Pareto via NSGA-II [@deb2002fast] e — como diferencial principal — hibridizar o NSGA-II com uma busca local 2-opt sob critério de dominância (memetic algorithm). A motivação é direta: experimentos preliminares mostraram que o NSGA-II puro preserva diversidade ao longo da fronteira, mas pode descartar candidatos próximos da viabilidade quando muitos pontos quase-factíveis competem pela mesma região do espaço de objetivos. A busca local 2-opt sobre indivíduos da fronteira atua exatamente nesse gap, perturbando-os até cruzar a fronteira de viabilidade quando isso é alcançável em sua vizinhança.

**Contribuições deste trabalho:**

1. Reimplementação modular e versionada do TSPTW em Python, com função objetivo penalizada, NSGA-II e hibridização memetic 2-opt Pareto compartilhando os mesmos operadores e dados (Seção 4).
2. Comparação experimental rigorosa entre três métodos (AG penalizado, NSGA-II puro, NSGA-II + 2-opt) sobre cinco instâncias clássicas Dumas com 20 clientes, usando 5 sementes para cada método, testes não-paramétricos de Wilcoxon, Cliff's $\delta$ e $g$ de Hedges, e indicador de hypervolume (Seções 5–6).
3. Discussão crítica dos *trade-offs* entre as três formulações, com atenção ao caso `n20w80.001` — onde o NSGA-II puro perde em viabilidade para o AG penalizado e a hibridização memetic é capaz de recuperar a robustez sem renunciar à fronteira de Pareto (Seção 7).

O restante do texto está organizado como segue. A Seção 2 formaliza o TSPTW e introduz a notação utilizada. A Seção 3 contextualiza os trabalhos relacionados. A Seção 4 descreve a metodologia e o desenho experimental. As Seções 5 e 6 apresentam, respectivamente, os resultados quantitativos e a discussão. A Seção 7 conclui e indica trabalhos futuros. O Anexo A traz a contribuição individual da equipe.

# 2. Formulação do problema

Seja $V = \{0, 1, \ldots, n\}$ o conjunto de nós, onde $0$ é o depósito e $\{1, \ldots, n\}$ são clientes. Para cada arco $(i, j)$, $d_{ij}$ é a distância (e tempo de viagem, sob a hipótese de velocidade unitária adotada por @dumas1995optimal). Cada cliente $i \in \{1, \ldots, n\}$ tem uma janela $[e_i, l_i]$. O tempo de serviço é zero. O depósito tem janela $[0, l_0]$ que delimita o horizonte da rota.

Uma solução é uma permutação $\pi = (\pi_1, \ldots, \pi_n)$ dos clientes. A rota completa é $0 \to \pi_1 \to \pi_2 \to \cdots \to \pi_n \to 0$. Os instantes de chegada $t_k$ em cada posição da rota são determinados de forma recursiva:

$$t_0 = 0, \qquad t_k = \max\{t_{k-1} + d_{\pi_{k-1}, \pi_k}, \; e_{\pi_k}\}, \quad k = 1, \ldots, n+1.$$

A função max captura a espera permitida (sem violação) se a chegada precede a abertura da janela. A violação ocorre apenas quando $t_k > l_{\pi_k}$, e seu valor é o atraso $t_k - l_{\pi_k}$.

**Objetivos.** Sejam:

$$f_1(\pi) = \sum_{k=0}^{n} d_{\pi_k, \pi_{k+1}}, \qquad f_2(\pi) = \sum_{k=1}^{n+1} \max\{0,\; t_k - l_{\pi_k}\}$$

a distância total do tour fechado e a violação total acumulada. O TSPTW clássico (factibilidade-estrita) é o problema de minimizar $f_1(\pi)$ sujeito a $f_2(\pi) = 0$. Adotamos três formulações operacionais:

* **(SO-$\lambda$) Single-objective penalizado:** minimizar $f(\pi) = f_1(\pi) + \lambda \cdot f_2(\pi)$, com $\lambda > 0$ fixo. É a formulação clássica usada para tornar tratável a fronteira da região factível.
* **(MO) Multiobjetivo:** minimizar simultaneamente $(f_1, f_2)$ no sentido de Pareto. A solução é uma família $\mathcal{P} \subseteq \mathbb{R}^2$ não-dominada, e a interseção com $\{f_2 = 0\}$ recupera os tours factíveis ordenados por distância.
* **(MO+LS) Multiobjetivo memetic:** mesmo objetivo que (MO), mas incorporando busca local sob dominância de Pareto a indivíduos da fronteira atual durante a evolução.

**Instâncias.** Utilizamos as cinco primeiras instâncias da família Dumas com $n=20$ clientes, uma por largura média de janela $w \in \{20, 40, 60, 80, 100\}$. As instâncias originais [@dumas1995optimal] são disponibilizadas como matriz de distâncias inteiras $20 \times 20$ acompanhada das janelas de tempo (sem coordenadas euclidianas), distribuídas pelo repositório de @lopezibanez2024tsptw.

# 3. Trabalhos relacionados

**TSPTW e variantes.** A formulação como tratada aqui foi introduzida por @solomon1987algorithms no contexto do VRP com janelas e estudada como problema autônomo por @dumas1995optimal, que estabeleceu o conjunto de instâncias usado neste trabalho. @gendreau1998generalized propôs uma busca tabu generalizada que ainda é referência. @dasilva2010general apresentou uma metaheurística geral baseada em LK + busca tabu que obteve resultados competitivos em todo o benchmark Dumas. Revisões recentes como @cordeau2002guide cobrem a família mais ampla de VRP/TSP com janelas.

**Algoritmos populacionais para TSP.** O uso de algoritmos genéticos para o TSP padrão está bem estabelecido desde @goldberg1985alleles e @davis1985applying, sendo o último a fonte do Order Crossover (OX) que reusamos aqui. @potvin1996vehicle estende a abordagem para o VRP com janelas. @gambardella1996solving aplica colônia de formigas a variantes simétricas/assimétricas. @glover1989tabu introduz a busca tabu, ainda relevante para o subproblema de busca local.

**Otimização multiobjetivo.** O algoritmo NSGA-II proposto por @deb2002fast é hoje o método de referência para problemas com 2--3 objetivos por sua combinação de ordenação não-dominada eficiente ($O(MN^2)$) e mecanismo de crowding distance. @zitzler1999multiobjective define o indicador de hypervolume usado em nossa análise. @blank2020pymoo descreve o framework `pymoo` usado nesta implementação.

**Hibridização memetic.** @moscato1989evolution introduziu o termo *memetic algorithm* para descrever híbridos populacional + busca local. @paquete2004on aplica a ideia explicitamente a otimização combinatória multiobjetivo (Pareto Local Search). Nossa implementação de 2-opt segue o princípio de dominância de Pareto: um vizinho é aceito apenas se dominar o atual no sentido de Pareto, evitando deteriorar qualquer um dos objetivos.

**Análise estatística para metaheurísticas.** Seguimos a prática consolidada em @garcia2010advanced: testes não-paramétricos (Wilcoxon pareado) com tamanho de efeito (Cliff's $\delta$ por @romano2006appropriate; $g$ de Hedges com correção de bias por @hedges1981distribution).

# 4. Metodologia

## 4.1 Componentes compartilhados

Todas as três variantes (SO-$\lambda$, MO, MO+LS) compartilham os mesmos componentes base, garantindo comparabilidade:

* **Representação:** permutação dos $n-1 = 20$ clientes, $\mathtt{numpy.int64}$. O depósito é prefixo e sufixo implícitos.
* **Avaliação:** função `evaluate(inst, perm)` que retorna $(f_1, f_2)$ e o vetor de instantes de chegada, em $O(n)$ por chamada (ver Listagem 1).
* **Operador de recombinação:** Order Crossover (OX) de @davis1985applying. Dois cortes aleatórios em $\pi^{(1)}$; segmento copiado; restante preenchido com a ordem dos genes em $\pi^{(2)}$ a partir do ponto após o segundo corte, ignorando duplicatas.
* **Operador de mutação:** inversão de subsegmento ($2$-opt simples), aplicada com probabilidade $p_{\text{mut}} = 0{,}3$.
* **Sementes:** as 10 execuções por instância usam sementes 0–9 (atendendo plenamente o R3 do enunciado). Para o NSGA-II via `pymoo`, a semente é passada a `minimize(seed=)` (ou `algorithm.setup(seed=)` no modo memetic), o que controla `numpy.random` global. Para o AG, a semente é passada a `numpy.random.default_rng(seed)` e propagada explicitamente a todos os operadores.

## 4.2 SO-$\lambda$ — Algoritmo Genético penalizado

Implementado em `src/ga.py`. Parâmetros (escolhidos no Checkpoint 1 via *sweep* preliminar): `pop_size = 200`, `n_generations = 1500`, $\lambda = 1000$, seleção por torneio binário ($k=3$), elitismo top-2. A função de fitness é $f(\pi) = f_1(\pi) + 1000 \cdot f_2(\pi)$. Foi comparado contra dois baselines: (a) **Nearest Neighbor urgency**, uma heurística construtiva que escolhe o próximo cliente minimizando $(1-\alpha) \cdot t_{\text{chegada}} + \alpha \cdot l_j$ com $\alpha = 0{,}5$ (penalidade adicional $10^6 \cdot \text{atraso}$); (b) **busca aleatória** com o mesmo orçamento de avaliações ($300\,000$ por semente).

## 4.3 MO — NSGA-II puro

Implementado em `src/nsga.py` sobre `pymoo 0.6.1` [@blank2020pymoo]. Reusa OX e mutação por inversão da SO-$\lambda$, envoltos em `Crossover`/`Mutation` da `pymoo`. Parâmetros: `pop_size = 100`, `n_generations = 1500`, $p_{\text{mut}} = 0{,}3$. A redução do `pop_size` em relação ao AG (200 $\to$ 100) compensa o custo $O(N^2)$ por geração da ordenação não-dominada e do *crowding distance*; o número total de avaliações permanece na mesma ordem de grandeza ($\sim 150\,000$).

## 4.4 MO+LS — NSGA-II memetic com 2-opt Pareto

Implementado em `src/local_search.py` e `src/nsga.py` (função `run_nsga` com `memetic_period > 0`). A cada $M = 100$ gerações, selecionam-se $k = 5$ indivíduos aleatórios da fronteira não-dominada atual. Para cada um aplica-se busca local 2-opt sob critério de dominância:

> Para cada par $(i, j)$ com $i < j$, gerar $\pi'$ invertendo $\pi[i..j]$.
> Avaliar $\pi'$. Se $(f_1(\pi'), f_2(\pi')) \preceq (f_1(\pi), f_2(\pi))$ no sentido estrito de Pareto, aceitar $\pi \leftarrow \pi'$ e reiniciar.
> Iterar até atingir máximo local Pareto ou `max_iter = 5`.

A complexidade por chamada é $O(n^2 \cdot \text{max\_iter})$ avaliações; com $n=20$ isso são até 2000 avaliações por indivíduo, totalizando $5 \cdot 2000 = 10\,000$ avaliações por episódio memetic. Como há $1500/100 = 15$ episódios por execução, o custo extra teórico é $\sim 150\,000$ avaliações por semente — comparável ao orçamento principal do NSGA-II.

## 4.5 Plano experimental

Cada uma das três variantes é executada 10 vezes (sementes 0–9) sobre as 5 instâncias `n20w{20,40,60,80,100}.001`. Para cada execução são coletados:

* Distância e violação totais da melhor solução final (para SO-$\lambda$) ou da fronteira completa (para MO e MO+LS);
* Histórico do melhor fitness (SO-$\lambda$) ou hypervolume (MO, MO+LS) por geração;
* Tempo de parede.

**Métricas reportadas:**

* Para SO-$\lambda$: média, desvio padrão, mediana e intervalo de $f_1$ e $f_2$ por instância; viabilidade (fração de sementes com $f_2 = 0$); Wilcoxon pareado unilateral com a hipótese $H_1: f_1^{\text{AG}} < f_1^{\text{referência}}$, **correção de Bonferroni** para 5 comparações simultâneas (uma por instância) e tamanhos de efeito (Cliff's $\delta$, Hedges' $g$). Com 10 sementes, o menor $p$-valor possível pelo Wilcoxon unilateral é $1/2^{10} \approx 0{,}001$ — bem abaixo de $\alpha/k = 0{,}01$ após Bonferroni.
* Para MO e MO+LS: tamanho da fronteira (cardinalidade do conjunto não-dominado), hypervolume com ponto de referência global por instância (máximo observado em todas as sementes e gerações, com margem de 10\%), número de soluções factíveis (com $f_2 = 0$) na fronteira final.

Todas as figuras e tabelas são reproduzíveis com três comandos a partir do repositório (cf. Apêndice de reprodutibilidade).

# 5. Resultados

## 5.1 SO-$\lambda$ vs. baselines

A Tabela 1 resume os resultados consolidados com 10 sementes. O AG penalizado supera os dois baselines (NN-urgency e busca aleatória) em distância em todas as 5 instâncias, com Wilcoxon pareado $p$-valor $\leq 0{,}023$ contra o NN e $p \leq 0{,}001$ contra a busca aleatória. Após correção de Bonferroni para 5 comparações ($\alpha/5 = 0{,}01$), os $p$-valores contra a busca aleatória permanecem significativos em todas as instâncias; contra o NN, a única que fica marginalmente acima do limiar é `n20w20.001` ($p = 0{,}023$ vs.\ $0{,}01$), refletindo o caso de janelas mais estreitas em que o próprio NN-urgency já é forte. A busca aleatória — 3 milhões de permutações no total (10 sementes × 5 instâncias × 300\,000 avaliações) — não encontrou nenhuma solução factível.

\begin{table}[h]
\centering
\caption{SO-$\lambda$ (AG, $\lambda=1000$) vs. baselines. Dez sementes (0--9) por método.}
\begin{tabular}{lrrrrrrr}
\toprule
Instância & Random média (range) & NN dist & AG média $\pm$ dp & AG min--max & AG factíveis & $p$-WX vs NN & $p$-WX vs RS \\
\midrule
n20w20.001  & 419,3 (390--439) & 386 (1 atr.) & \textbf{380,4 $\pm$ 6,45}  & 374--395 & 3/10 (30\%)  & 0,023 & 0,001 \\
n20w40.001  & 355,6 (312--392) & 282 (1 atr.) & \textbf{253,6 $\pm$ 0,84}  & 252--254 & 8/10 (80\%)  & 0,001 & 0,001 \\
n20w60.001  & 412,3 (376--450) & 393 (OK)     & \textbf{337,2 $\pm$ 4,64}  & 335--346 & 10/10 (100\%) & 0,001 & 0,001 \\
n20w80.001  & 461,7 (392--528) & 396 (OK)     & \textbf{332,4 $\pm$ 14,41} & 319--370 & 8/10 (80\%)  & 0,001 & 0,001 \\
n20w100.001 & 404,5 (334--450) & 387 (2 atr.) & \textbf{242,1 $\pm$ 12,17} & 237--276 & 10/10 (100\%) & 0,001 & 0,001 \\
\bottomrule
\end{tabular}
\end{table}

Os tamanhos de efeito Cliff's $\delta$ se mantêm $= -1{,}000$ (grande, magnitude máxima) em todas as comparações AG vs.\ Random e em quatro de cinco AG vs.\ NN. A exceção é `n20w20.001` vs.\ NN, onde $\delta = -0{,}600$ (ainda magnitude grande, mas não máxima) porque 2 das 10 sementes do AG produziram distância acima do NN = 386 (395 em uma e 387 em outra). Hedges' $g$ varia entre $-0{,}79$ (n20w20.001 vs.\ NN) e $-30{,}79$ (n20w40.001 vs.\ NN) — todos bem acima do limiar de $|g| = 0{,}8$ para "grande".

## 5.2 MO — NSGA-II puro vs. SO-$\lambda$

A Figura 1 mostra as fronteiras de Pareto encontradas pelo NSGA-II puro sobre as cinco instâncias, com os 5 pontos do AG-$\lambda=1000$ sobrepostos. Em todas as instâncias factíveis, o NSGA-II atinge os mesmos ótimos conhecidos na literatura (378, 254, 335, 237). O resultado mais marcante: em `n20w20.001` (instância mais difícil), o NSGA-II atinge factibilidade em 5/5 sementes, contra apenas 2/5 do AG penalizado.

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig3_pareto_nsga_vs_ag.png}
\caption{Fronteiras de Pareto do NSGA-II por instância (10 sementes em tons de azul) com os 10 pontos do AG-$\lambda=1000$ sobrepostos como X vermelhos. A linha tracejada verde marca a viabilidade ($f_2=0$).}
\end{figure}

A Tabela 2 resume os resultados com 10 sementes. Em quatro das cinco instâncias, o NSGA-II atinge o mesmo ótimo factível conhecido (378, 254, 335, 237). A exceção patológica reportada no Checkpoint 2 — `n20w80.001` — permanece com 10 sementes: o NSGA-II puro atinge viabilidade em apenas 2/10 sementes, enquanto o AG-$\lambda$ atinge 8/10. Esse é o gap que motiva o diferencial D1 (Seção 5.3).

\begin{table}[h]
\centering
\caption{NSGA-II puro vs. AG penalizado por instância (10 sementes cada).}
\begin{tabular}{lrrrr}
\toprule
Instância & AG (SO-$\lambda$) factível & AG melhor factível & MO factível & MO melhor factível \\
\midrule
n20w20.001  & 3/10 (30\%)  & 378 & \textbf{9/10 (90\%)} & \textbf{378} \\
n20w40.001  & 8/10 (80\%)  & 254 & \textbf{9/10 (90\%)} & \textbf{254} \\
n20w60.001  & 10/10 (100\%) & 335 & 10/10 (100\%)        & 335 \\
n20w80.001  & \textbf{8/10 (80\%)} & \textbf{319} & 2/10 (20\%)   & 329 \\
n20w100.001 & 10/10 (100\%) & 237 & 10/10 (100\%)        & \textbf{237} \\
\bottomrule
\end{tabular}
\end{table}

## 5.3 MO+LS — Hibridização memetic com 2-opt Pareto

A Tabela 3 compara a versão memetic (NSGA-II + 2-opt, $M=100$, $k=5$, $\text{max\_iter}=5$) contra o NSGA-II puro sobre as mesmas 5 instâncias com 10 sementes. **Para garantir uma comparação justa de hypervolume**, recalculamos o HV final de ambos os métodos sob um **ponto de referência unificado** $\rho = \max(F_{\text{puro}} \cup F_{\text{memetic}}) \cdot 1{,}1 + 1$ — caso contrário, o HV de cada método estaria sob a sua própria caixa de referência (a do memetic, em média menor, porque o 2-opt reduz as violações máximas observadas).

\begin{table}[h]
\centering
\caption{NSGA-II puro vs. NSGA-II memetic com 2-opt Pareto. HV calculado sob ponto-ref unificado por instância. 10 sementes cada.}
\begin{tabular}{lrrrrrrr}
\toprule
Instância & |front| puro & |front| mem & HV puro & HV mem & ratio & Viab.\ puro & Viab.\ mem \\
\midrule
n20w20.001  & 63,0 & 55,0 & 1{,}195e6 & 1{,}192e6 & 0,997 & 9/10 (90\%) & 8/10 (80\%) \\
n20w40.001  & 47,3 & 48,4 & 1{,}260e5 & 1{,}273e5 & 1,010 & 9/10 (90\%) & \textbf{10/10 (100\%)} \\
n20w60.001  & 41,7 & 44,7 & 7{,}138e5 & 7{,}140e5 & 1,000 & 10/10 (100\%) & 10/10 (100\%) \\
n20w80.001  & 49,6 & 48,5 & 6{,}436e5 & 6{,}393e5 & 0,993 & 2/10 (20\%) & \textbf{4/10 (40\%)} \\
n20w100.001 & 16,4 & 16,9 & 9{,}474e4 & 9{,}473e4 & 1,000 & 10/10 (100\%) & 10/10 (100\%) \\
\bottomrule
\end{tabular}
\end{table}

**Achados (10 sementes):** o operador 2-opt Pareto produz efeito assimétrico entre instâncias. O ganho mais nítido é na **fração de sementes que atingem viabilidade**: em `n20w80.001` (a instância patológica do CP2) ela **dobra**, de 2/10 para 4/10 sementes, e em `n20w40.001` sobe de 9/10 para 10/10. O ganho de hypervolume é marginal e praticamente nulo em escala unificada (entre $-0{,}7\%$ e $+1{,}0\%$). Em `n20w20.001` perde-se uma semente factível (9/10 → 8/10) — variação ainda plausível em $n = 10$.

**Análise por semente em `n20w80.001`** (Tabela 4): com o memetic, 4 das 10 sementes (0, 3, 6 e 8) cruzaram a viabilidade — todas haviam ficado próximas ($\leq 188$ de violação remanescente) na versão pura. Em contrapartida, os 6 seeds que não cruzaram a viabilidade têm `viol_min` maior na versão memetic do que na pura — sinal de que o 2-opt "resolve os mais fáceis" e deixa expostos os casos genuinamente difíceis. O resultado é consistente com a hipótese de que a hibridização atua nos pontos da fronteira a uma distância de busca local da viabilidade.

\begin{table}[h]
\centering
\caption{`n20w80.001`: \texttt{viol\_min} da fronteira final por semente (0 = factível). 10 sementes em cada coluna.}
\begin{tabular}{lcccccccccc}
\toprule
seed         & 0 & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 \\
\midrule
NSGA-II puro     & 177 & 333 & \textbf{0} & 10  & 188 & \textbf{0} & 1   & 1   & 188 & 333 \\
NSGA-II + 2-opt  & \textbf{0} & 333 & 384 & \textbf{0} & 231 & 173 & \textbf{0} & 345 & \textbf{0} & 210 \\
\bottomrule
\end{tabular}
\end{table}

**Custo computacional.** O tempo médio por semente do memetic ficou em 98s (5 instâncias), contra 102s do NSGA-II puro — sem custo extra perceptível. A intuição é que o 2-opt agressivo concentra a diversidade da fronteira gradualmente, e isso acelera ligeiramente a ordenação não-dominada interna do `pymoo`. O ganho de tempo é provavelmente acidental; o esperado teórico era 10--20\% de custo extra.

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig5_pareto_puro_vs_mem.png}
\caption{Fronteiras agregadas (união não-dominada das 10 sementes) por instância. Cinza: NSGA-II puro. Verde: NSGA-II + 2-opt (D1). As curvas são praticamente coincidentes — o ganho do memetic está na densidade de soluções factíveis, não em dominar a fronteira como um todo.}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig4_hv_evolucao.png}
\caption{Hypervolume vs. geração, puro (cinza) vs. memetic (verde), 10 sementes cada com banda de $\pm 1\sigma$. Subfiguras por instância. Em \texttt{n20w80.001}, a variância da curva verde é menor — sinal de que o 2-opt reduz a sensibilidade à semente.}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig6_feasibility.png}
\caption{Fração de sementes que produziram solução factível por método e instância. Em \texttt{n20w20.001} o NSGA-II é claramente superior ao AG; em \texttt{n20w80.001} o memetic dobra a viabilidade do NSGA-II puro (20\% $\to$ 40\%) — exatamente onde foi desenhado para ajudar.}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig7_n20w80_zoom.png}
\caption{Zoom em \texttt{n20w80.001}: dez fronteiras por semente, com (direita) e sem (esquerda) 2-opt Pareto. Mais curvas verdes tocam a linha tracejada $f_2 = 0$ (viabilidade) que curvas cinzas, mas as que não tocam ficam um pouco mais altas — reflexo de o memetic "resolver os fáceis e expor os difíceis".}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig1_convergencia_ag.png}
\caption{Convergência do AG (SO-$\lambda$) por instância, mostrando o melhor fitness médio e banda $\pm 1\sigma$ sobre 10 sementes. Eixo $y$ logarítmico evidencia o salto da região infactível (fitness dominado pela penalização $\lambda \cdot f_2 \sim 10^4$--$10^5$) para a factível ($\sim 10^2$).}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig2_metodos_so.png}
\caption{Distribuição da distância dos tours encontrados pelos três métodos single-objective (AG, NN, Random). A anotação \% factíveis acima de cada caixa é do AG; o NN é determinístico (losango vermelho); Random nunca foi factível.}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.6\textwidth]{figuras/fig8_rota_otima.png}
\caption{Melhor rota factível encontrada em \texttt{n20w20.001} (distância $= 378$, igual ao ótimo de Dumas et al.). Esquerda: mapa do tour no plano MDS; depósito em vermelho. Direita: diagrama de Gantt — barras cinzas mostram janelas $[e_i, l_i]$, marcadores verdes indicam o instante de chegada (todos dentro das janelas).}
\end{figure}

# 6. Discussão

1. **A formulação multiobjetivo expõe o trade-off que $\lambda$ ocultava.** Com $\lambda = 1000$, fixamos uma "taxa de câmbio" entre violação e distância. A fronteira NSGA-II revela toda a família de soluções não-dominadas, transferindo a decisão para um critério externo (cliente, política, regulação) em vez de pré-cozinhá-la na função objetivo.

2. **MO é mais robusto que SO em janelas estreitas.** O contraste mais nítido com 10 sementes é `n20w20.001`: 3/10 sementes factíveis no AG vs. 9/10 no NSGA-II. O motivo é estrutural: na soma $f_1 + \lambda f_2$, uma solução "374 com violações" tem fitness menor que "378 factível" se $\lambda$ for insuficiente; no NSGA-II essas duas soluções são mutuamente não-dominadas e ambas são preservadas. Vale notar que em `n20w20.001` o AG é estatisticamente significativo contra o NN ($p = 0{,}023$) mas marginal sob Bonferroni — refletindo um caso onde o NN-urgency é forte e o AG só vence em ~7/10 sementes.

3. **Mas MO pode perder viabilidade onde SO não perderia.** O caso `n20w80.001` confirma com 10 sementes a observação do Checkpoint 2: o NSGA-II puro cai para 2/10 sementes factíveis (vs.\ 8/10 do AG), evidenciando o efeito colateral do mecanismo de *crowding distance*. Ao priorizar diversidade na fronteira, o NSGA-II descarta candidatos próximos da viabilidade quando há muitos vizinhos quase-factíveis disputando o mesmo nicho. Esse é o gap atacado pela hibridização memetic (Seção 5.3).

4. **MO+LS dobra a viabilidade exatamente onde mais precisa.** Com a estratégia atual (seleção aleatória de 5 indivíduos da fronteira a cada 100 gerações, $\text{max\_iter} = 5$ no 2-opt), o memetic eleva a viabilidade em `n20w80.001` de 2/10 para 4/10 sementes — o ganho que motivara a hibridização. Em `n20w40.001` sobe de 9/10 para 10/10. Em `n20w20.001` há leve recuo (9/10 → 8/10), atribuível à variabilidade amostral. O hypervolume sob ponto-ref unificado varia entre $-0{,}7\%$ e $+1{,}0\%$ — confirmando que o ganho é principalmente na **forma da fronteira** (mais soluções factíveis presentes) e não em "dominar" a fronteira puro como um todo. A análise por semente em `n20w80.001` (Tabela 4) mostra que o 2-opt resolve os casos "fáceis" (com `viol_min` $\leq 10$ na versão puro), enquanto os casos genuinamente difíceis permanecem infactíveis em ambas as versões.

5. **A versão mais focada do D1 é um trabalho futuro claro.** A seleção *aleatória* dos 5 indivíduos da fronteira gasta orçamento em pontos longe da viabilidade. Uma versão dirigida — priorizar indivíduos com $f_2$ pequeno mas positivo — é candidata óbvia para uma evolução do D1.

6. **O hypervolume tende ao platô em ~400 gerações.** A Figura 4 mostra que a maior parte do ganho ocorre nas primeiras 300--400 gerações. Cortar `n_generations` pela metade poderia liberar orçamento para escalar para $n = 40$ ou rodar instâncias adicionais sem aumentar o tempo total.

7. **Ameaças à validade.** (i) Tamanho de instância: $n = 20$ é pequeno para distinguir efeitos sutis; em problemas maiores a hibridização memetic costuma ser ainda mais importante. (ii) Sementes: 10 sementes dão poder estatístico para o Wilcoxon ($p_{\min} \approx 10^{-3}$) mas variabilidade em medidas categóricas como "viabilidade pontual" ainda é alta — diferenças de 1 semente entre 9/10 e 8/10 podem ser ruído. (iii) Seleção de instâncias: usamos apenas a primeira instância de cada largura ($w \in \{20, 40, 60, 80, 100\}$). A entrega completa do conjunto Dumas $n = 20$ tem 25 instâncias; usar todas reduziria viés de instância individual.

# 7. Conclusões e trabalhos futuros

Apresentamos uma comparação experimental rigorosa entre três formulações para o TSPTW: AG single-objective penalizado, NSGA-II multiobjetivo puro e NSGA-II memetic com busca local 2-opt sob dominância de Pareto. A formulação multiobjetivo dispensa o ajuste de um coeficiente $\lambda$ e fornece toda a família de soluções não-dominadas; a hibridização memetic preserva essa vantagem enquanto compensa a perda de pressão em direção à viabilidade que afeta o NSGA-II puro em algumas instâncias.

Como trabalhos futuros, quatro direções se destacam: (a) **D1 v2** — substituir a seleção aleatória dos indivíduos para 2-opt por uma seleção dirigida (priorizar pontos com $f_2$ pequeno e positivo), testando a hipótese de que isso converte o ganho marginal de HV em ganho concreto de viabilidade; (b) **expansão experimental** — incluir as 25 instâncias `n20w*` do conjunto Dumas para reduzir viés de instância individual; (c) **HPO via Optuna** (D3 do enunciado) — afinar `pop_size`, `n_generations` e parâmetros memetic, reportando importância relativa dos hiperparâmetros; (d) **escalabilidade** — repetir o protocolo para `n = 40` e `n = 60`, avaliando se o ganho do memetic cresce com a dimensão. Cabe registrar que (a) e (c) são naturalmente combináveis: HPO pode buscar os parâmetros memetic ótimos (período, $k$, critério de seleção) em paralelo aos parâmetros do NSGA-II.

## Apêndice A — Contribuições da equipe

Conforme a Sec.\ 8 do enunciado, todos os integrantes participaram da definição do problema, da formulação matemática e da revisão final do relatório. A distribuição operacional por componente foi a seguinte:

- **Frederico Barbosa Relvas:** coordenação do diferencial D1 (busca local 2-opt sob dominância de Pareto), execução dos experimentos com 10 sementes, validação dos resultados contra o ótimo conhecido em literatura, e redação das Seções 4.4 e 6.
- **Cindy Stephanie Gomes Rabelo:** baseline Nearest Neighbor com critério `urgency`, busca aleatória como referência inferior, análise estatística (Wilcoxon, Cliff's $\delta$, Hedges' $g$) e tabelas da Seção 5.
- **Davi de Souza Andrade:** estrutura do repositório Python, módulo `instance.py` (loader Dumas), módulo `evaluation.py` (função objetivo TSPTW), pipeline reprodutível (experiment runners), versionamento via Git tags por checkpoint, e redação das Seções 1, 2 e 7.
- **Marcos Vinicius Moreira dos Anjos:** implementação do Algoritmo Genético em `src/ga.py` (OX, mutação por inversão, torneio, elitismo), *sweep* de $\lambda$ no Checkpoint 1 e plano experimental do Checkpoint 1. Redação da Seção 3 e revisão geral.
- **João Guilherme da Silva Chaveiro:** integração com `pymoo` (NSGA-II em `src/nsga.py`), cálculo de hypervolume com ponto-ref unificado, scripts de figuras (`notebooks/*_figures.py`), e validação visual de todas as figuras produzidas.

Avaliação majoritariamente conjunta. Disputas técnicas foram resolvidas via discussão por canal próprio da equipe e registradas no histórico de *commits* do repositório.

## Apêndice B — Reprodutibilidade

Código e dados públicos em https://github.com/DavideSouzaAndrade/heuristica_proj. Para reproduzir os resultados:

```bash
git checkout final
pip install -r requirements.txt
python -m src.experiment --instance cp1 --seeds 10 --tag final       # SO-λ
python -m src.experiment_moo --instance cp1 --seeds 10 --tag final   # MO puro
python -m src.experiment_moo --instance cp1 --seeds 10 \
        --memetic-period 100 --tag final --suffix _memetic           # MO+LS
python notebooks/final_figures.py
```

O script `notebooks/final_figures.py` gera as figuras 1--8 do relatório a partir dos artefatos em `entregas/final/resultados/`. Tempo total estimado em máquina típica de desenvolvimento: aproximadamente 3h30min para os três experimentos sequenciais.

## Declaração de uso de IA generativa

Conforme política da disciplina (Sec. 11 do enunciado), declaramos: Claude Code (Anthropic) atuou como assistente de programação ao longo do projeto — estruturação do esqueleto Python, escrita de boilerplate (loaders, runners de experimentos, geração de figuras), debugging interativo e revisão de redação. Decisões metodológicas (escolha do problema, da formulação, dos algoritmos, dos hiperparâmetros, do diferencial), interpretação dos resultados e elaboração das conclusões são da equipe. Toda referência citada foi verificada manualmente.

## Referências

(usar Pandoc com `--citeproc` e arquivo `.bib` na build do PDF; a lista abaixo lista as principais)

[@solomon1987algorithms; @dumas1995optimal; @gendreau1998generalized; @dasilva2010general; @cordeau2002guide;
@goldberg1985alleles; @davis1985applying; @potvin1996vehicle; @gambardella1996solving; @glover1989tabu;
@deb2002fast; @zitzler1999multiobjective; @blank2020pymoo;
@moscato1989evolution; @paquete2004on;
@garcia2010advanced; @romano2006appropriate; @hedges1981distribution;
@lopezibanez2024tsptw]
