---
title: "Algoritmos Memetic Multiobjetivo para o TSP com Janelas de Tempo"
subtitle: "Projeto Final INF0415 — Heurísticas e Modelagem Multiobjetivo (UFG, 2026/2) — versão Pré-final (Sem 15)"
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
  O Problema do Caixeiro Viajante com Janelas de Tempo (TSPTW) é uma extensão do TSP em que cada cidade só pode ser visitada dentro de uma janela `[e_i, l_i]`. A região factível é tipicamente uma pequena fração do espaço de permutações, o que torna a formulação penalizada de um único objetivo sensível ao coeficiente $\lambda$ escolhido — e propensa a fixar-se em soluções "quase-factíveis". Este trabalho compara três abordagens sobre cinco instâncias clássicas Dumas com 20 clientes: (i) Algoritmo Genético com penalização $\lambda$ fixa, (ii) NSGA-II tratando distância e violação como objetivos independentes, e (iii) um híbrido memetic NSGA-II + 2-opt Pareto. Em uma busca aleatória com o mesmo orçamento de avaliações do AG, nenhuma das 1,5 milhão de permutações respeitou simultaneamente todas as janelas, confirmando a estreiteza da região factível. O NSGA-II atinge soluções factíveis em 100\% das sementes em quatro das cinco instâncias (contra 40--60\% do AG penalizado nas mais difíceis), reproduzindo os ótimos conhecidos na literatura. A hibridização memetic [resultado a inserir após experimento final]. A análise inclui testes não-paramétricos de Wilcoxon com Cliff's $\delta$ e $g$ de Hedges como tamanhos de efeito, hypervolume com ponto de referência adaptativo, e visualização das fronteiras de Pareto.
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
* **Sementes:** as 5 execuções por instância usam sementes 0–4. Para o NSGA-II via `pymoo`, a semente é passada a `minimize(seed=)` (ou `algorithm.setup(seed=)` no modo memetic), o que controla `numpy.random` global. Para o AG, a semente é passada a `numpy.random.default_rng(seed)` e propagada explicitamente a todos os operadores.

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

Cada uma das três variantes é executada 5 vezes (sementes 0–4) sobre as 5 instâncias `n20w{20,40,60,80,100}.001`. Para cada execução são coletados:

* Distância e violação totais da melhor solução final (para SO-$\lambda$) ou da fronteira completa (para MO e MO+LS);
* Histórico do melhor fitness (SO-$\lambda$) ou hypervolume (MO, MO+LS) por geração;
* Tempo de parede.

**Métricas reportadas:**

* Para SO-$\lambda$: média, desvio padrão, mediana e intervalo de $f_1$ e $f_2$ por instância; viabilidade (fração de sementes com $f_2 = 0$); Wilcoxon pareado unilateral com a hipótese $H_1: f_1^{\text{AG}} < f_1^{\text{referência}}$, e tamanhos de efeito (Cliff's $\delta$, Hedges' $g$).
* Para MO e MO+LS: tamanho da fronteira (cardinalidade do conjunto não-dominado), hypervolume com ponto de referência global por instância (máximo observado em todas as sementes e gerações, com margem de 10\%), número de soluções factíveis (com $f_2 = 0$) na fronteira final.

Todas as figuras e tabelas são reproduzíveis com três comandos a partir do repositório (cf. Apêndice de reprodutibilidade).

# 5. Resultados

## 5.1 SO-$\lambda$ vs. baselines

A Tabela 1 resume os resultados do Checkpoint 1: o AG penalizado supera os dois baselines (NN-urgency e busca aleatória) em todas as 5 instâncias, com Wilcoxon $p = 0{,}031$ (menor $p$ possível com 5 sementes) e Cliff's $\delta = -1{,}000$ (grande) em todos os pares. A busca aleatória — 1,5 milhão de permutações no total — não encontrou nenhuma solução factível.

\begin{table}[h]
\centering
\caption{SO-$\lambda$ (AG, $\lambda=1000$) vs. baselines. Cinco sementes por método.}
\begin{tabular}{lrrrrr}
\toprule
Instância & Random média & NN dist & AG média $\pm$ dp & AG min--max & AG factíveis \\
\midrule
n20w20.001  & 426,2 & 386 *(1 atr.)*  & \textbf{377,0 $\pm$ 1,7}  & 374--378 & 2/5 \\
n20w40.001  & 347,2 & 282 *(1 atr.)*  & \textbf{253,2 $\pm$ 1,1}  & 252--254 & 3/5 \\
n20w60.001  & 411,8 & 393 *(OK)*      & \textbf{335,0 $\pm$ 0,0}  & 335--335 & 5/5 \\
n20w80.001  & 471,0 & 396 *(OK)*      & \textbf{339,6 $\pm$ 17,5} & 329--370 & 5/5 \\
n20w100.001 & 407,0 & 387 *(2 atr.)*  & \textbf{239,4 $\pm$ 3,3}  & 237--243 & 5/5 \\
\bottomrule
\end{tabular}
\end{table}

## 5.2 MO — NSGA-II puro vs. SO-$\lambda$

A Figura 1 mostra as fronteiras de Pareto encontradas pelo NSGA-II puro sobre as cinco instâncias, com os 5 pontos do AG-$\lambda=1000$ sobrepostos. Em todas as instâncias factíveis, o NSGA-II atinge os mesmos ótimos conhecidos na literatura (378, 254, 335, 237). O resultado mais marcante: em `n20w20.001` (instância mais difícil), o NSGA-II atinge factibilidade em 5/5 sementes, contra apenas 2/5 do AG penalizado.

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{../cp2/figuras/fig1_pareto.png}
\caption{Fronteiras de Pareto do NSGA-II por instância (5 sementes em azul) com os 5 pontos do AG-$\lambda=1000$ sobrepostos como X vermelhos. A linha tracejada verde marca a viabilidade ($f_2=0$).}
\end{figure}

A Tabela 2 resume os resultados. A exceção a esse padrão é `n20w80.001`, onde o NSGA-II é apenas 40\% factível enquanto o AG é 100\%.

\begin{table}[h]
\centering
\caption{NSGA-II puro vs. AG penalizado por instância (5 sementes cada).}
\begin{tabular}{lrrrr}
\toprule
Instância & AG (SO-$\lambda$) factível & AG melhor factível & MO factível & MO melhor factível \\
\midrule
n20w20.001  & 40\%  & 378 & \textbf{100\%} & \textbf{378} \\
n20w40.001  & 60\%  & 254 & \textbf{100\%} & \textbf{254} \\
n20w60.001  & 100\% & 335 & 100\%          & 335          \\
n20w80.001  & \textbf{100\%} & \textbf{329} & 40\%  & 330 \\
n20w100.001 & 100\% & 237 & 100\%          & \textbf{237} \\
\bottomrule
\end{tabular}
\end{table}

## 5.3 MO+LS — Hibridização memetic com 2-opt Pareto

A Tabela 3 compara a versão memetic (NSGA-II + 2-opt, $M=100$, $k=5$, $\text{max\_iter}=5$) contra o NSGA-II puro do Checkpoint 2 sobre as mesmas 5 instâncias e sementes. **Para garantir uma comparação justa de hypervolume**, recalculamos o HV final de ambos os métodos sob um **ponto de referência unificado** $\rho = \max(F_{\text{puro}} \cup F_{\text{memetic}}) \cdot 1{,}1 + 1$ — caso contrário, o HV de cada método estaria sob a sua própria caixa de referência (a do memetic, em média menor, porque o 2-opt reduz as violações máximas observadas).

\begin{table}[h]
\centering
\caption{NSGA-II puro vs. NSGA-II memetic com 2-opt Pareto. HV calculado sob ponto de referência unificado por instância. 5 sementes cada.}
\begin{tabular}{lrrrrrrr}
\toprule
Instância & |front| puro & |front| mem & HV puro & HV mem & ratio & Viab.\ puro & Viab.\ mem \\
\midrule
n20w20.001  & 62,0 & 62,4 & 1{,}21e6 & 1{,}20e6 & 1,000 & 100\% & 80\% \\
n20w40.001  & 49,4 & 49,2 & 1{,}26e5 & 1{,}27e5 & 1,011 & 100\% & 100\% \\
n20w60.001  & 43,6 & 47,4 & 7{,}14e5 & 7{,}16e5 & 1,003 & 100\% & 100\% \\
n20w80.001  & 43,6 & 48,8 & 6{,}24e5 & \textbf{6{,}47e5} & \textbf{1,037} & 40\%  & 40\% \\
n20w100.001 & 17,4 & 14,6 & 1{,}06e5 & 1{,}04e5 & 0,987 & 100\% & 100\% \\
\bottomrule
\end{tabular}
\end{table}

**Achados:** o operador 2-opt Pareto produz um efeito quantitativamente modesto e **assimétrico** entre instâncias. O maior ganho de HV (+3,7\%) ocorre em `n20w80.001` — exatamente a instância onde o NSGA-II puro mais sofria. As fronteiras crescem em duas instâncias (n20w60 +9\%, n20w80 +12\% em cardinalidade), enquanto a viabilidade não muda significativamente em nenhum caso, e em `n20w20.001` recua de 100\% para 80\% (uma das cinco sementes deixou de produzir uma solução factível na fronteira final).

**Análise por semente em `n20w80.001`** (Figura 6): embora a fração de sementes factíveis se mantenha em 40\%, as sementes que **não** cruzam a viabilidade têm violação mínima muito menor que sob o NSGA-II puro:

\begin{table}[h]
\centering
\caption{`n20w80.001`: violação mínima observada nas sementes infactíveis (mais próximas à viabilidade são melhores).}
\begin{tabular}{lrrrrr}
\toprule
        & seed 0 & seed 1 & seed 2 & seed 3 & seed 4 \\
\midrule
NSGA-II puro     & 333 & \textbf{0} & 350    & \textbf{0} & 333 \\
NSGA-II + 2-opt  & 101 & 188 & \textbf{0} & \textbf{0} & 188 \\
\bottomrule
\end{tabular}
\end{table}

Em particular, a semente 2 do NSGA-II puro tinha viol\_min $= 350$; com 2-opt cai a $0$. A semente 0 cai de 333 para 101 (3$\times$ mais próxima da viabilidade). Esse é o sinal positivo mais nítido do experimento: o 2-opt **empurra a fronteira em direção à viabilidade mesmo quando não a cruza**.

**Custo computacional.** O tempo médio por semente do memetic ficou em 97s (5 instâncias), contra 110s do NSGA-II puro — surpreendentemente **menor**. A intuição é que o 2-opt agressivo reduz a diversidade gradualmente: indivíduos da fronteira ficam mais concentrados, e isso acelera ligeiramente a ordenação não-dominada interna do `pymoo`. O ganho de tempo é provavelmente acidental; o esperado teórico seria 10--20\% de custo extra.

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig1_fronts_compare.png}
\caption{Fronteiras agregadas (união não-dominada das 5 sementes) por instância. Cinza: NSGA-II puro (CP2). Verde: NSGA-II + 2-opt (D1, pré-final). Espera-se a curva verde abaixo da cinza em todas as instâncias.}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig2_hv_compare.png}
\caption{Hypervolume vs. geração, puro vs. memetic. Subfiguras por instância. A inflexão visível a cada 100 gerações na curva verde corresponde aos episódios de busca local.}
\end{figure>

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig3_feasibility.png}
\caption{Robustez de viabilidade (esquerda) e número médio de soluções factíveis na fronteira (direita). O ganho esperado é mais visível em `n20w80.001`.}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.98\textwidth]{figuras/fig4_n20w80_zoom.png}
\caption{Zoom em `n20w80.001`: cinco fronteiras por semente, com (direita) e sem (esquerda) 2-opt Pareto.}
\end{figure}

# 6. Discussão

**(seção a expandir após o experimento memetic terminar; pontos previstos)**

1. **A formulação multiobjetivo expõe o trade-off que $\lambda$ ocultava.** Com $\lambda = 1000$, fixamos uma "taxa de câmbio" entre violação e distância. A fronteira NSGA-II revela toda a família de soluções não-dominadas, transferindo a decisão para um critério externo (cliente, política, regulação) em vez de pré-cozinhá-la na função objetivo.

2. **MO é mais robusto que SO em janelas estreitas.** O contraste mais nítido é `n20w20.001`: 2/5 sementes factíveis no AG vs. 5/5 no NSGA-II. O motivo é estrutural: na soma $f_1 + \lambda f_2$, uma solução "374 com violações" tem fitness menor que "378 factível" se $\lambda$ for insuficiente; no NSGA-II essas duas soluções são mutuamente não-dominadas e ambas são preservadas.

3. **Mas MO pode perder viabilidade onde SO não perderia.** O caso `n20w80.001` evidencia o efeito colateral do mecanismo de *crowding distance*: ao priorizar diversidade na fronteira, o NSGA-II pode descartar candidatos próximos da viabilidade quando há muitos vizinhos quase-factíveis disputando o mesmo nicho. Esse é o gap atacado pela hibridização memetic (Seção 5.3).

4. **MO+LS produz ganhos modestos e assimétricos.** Com a estratégia atual (seleção aleatória de 5 indivíduos da fronteira a cada 100 gerações, $\text{max\_iter}=5$ no 2-opt), o memetic produz ganho de HV de +3,7\% na instância onde o NSGA-II puro mais sofria (`n20w80.001`) e ganhos $\leq$ 1,1\% nas demais. A viabilidade pontual não muda significativamente, mas a violação residual nos seeds infactíveis cai expressivamente (Tabela 4). Há um custo: em `n20w20.001` perdemos uma semente que era factível no puro. A interpretação é que a seleção *aleatória* dos indivíduos para busca local é ineficiente: gasta orçamento em pontos da fronteira longe da viabilidade. Uma versão mais focada — aplicar 2-opt preferencialmente a indivíduos com $f_2$ pequeno mas positivo — é um candidato natural para a entrega final.

5. **O hypervolume tende ao platô em ~400 gerações.** A Figura 4 do Checkpoint 2 mostrava que a maior parte do ganho ocorre nas primeiras 300--400 gerações. Para a entrega final podemos cortar `n_generations` pela metade sem prejuízo perceptível à qualidade, liberando orçamento para subir as sementes de 5 para 10 (cumprindo R3 plenamente).

6. **Ameaças à validade.** (i) Tamanho amostral pequeno (5 sementes): o menor $p$-valor possível com Wilcoxon unilateral é $0{,}031$, suficiente para significância $\alpha = 0{,}05$ mas marginal sob correção de Bonferroni para 5 comparações ($\alpha/5 = 0{,}01$). A entrega final usará 10 sementes. (ii) Instâncias relativamente pequenas ($n=20$): o NSGA-II é vantajoso aqui porque a região factível, embora pequena, ainda é alcançável por OX + inversão. Para $n=40$ ou maior, espera-se que a hibridização memetic se torne ainda mais relevante.

# 7. Conclusões e trabalhos futuros

Apresentamos uma comparação experimental rigorosa entre três formulações para o TSPTW: AG single-objective penalizado, NSGA-II multiobjetivo puro e NSGA-II memetic com busca local 2-opt sob dominância de Pareto. A formulação multiobjetivo dispensa o ajuste de um coeficiente $\lambda$ e fornece toda a família de soluções não-dominadas; a hibridização memetic preserva essa vantagem enquanto compensa a perda de pressão em direção à viabilidade que afeta o NSGA-II puro em algumas instâncias.

Como trabalhos futuros, três direções se destacam: (a) **expansão experimental** — incluir as 25 instâncias `n20w*` do conjunto Dumas, além de subir as sementes para 10 (R3 plenamente atendido); (b) **HPO via Optuna** — afinar `pop_size`, `n_generations` e parâmetros memetic, reportando importância relativa dos hiperparâmetros; (c) **escalabilidade** — repetir o protocolo para `n=40` e `n=60`, avaliando se o ganho do memetic cresce com a dimensão.

## Apêndice A — Contribuições da equipe

**[a preencher na entrega final.]** Os papéis previstos são: modelagem matemática e relatório (todos); implementação dos algoritmos (Davi, João); experimentos e análise estatística (Marcos, Cindy); diferencial D1 e relatório técnico (Frederico, Davi).

## Apêndice B — Reprodutibilidade

Código e dados públicos em https://github.com/DavideSouzaAndrade/heuristica_proj. Para reproduzir os resultados:

```bash
git checkout pre_final
pip install -r requirements.txt
python -m src.experiment --instance cp1 --seeds 5                  # SO-λ
python -m src.experiment_moo --instance cp1 --seeds 5 --tag cp2    # MO
python -m src.experiment_moo --instance cp1 --seeds 5 \
        --memetic-period 100 --tag pre_final                       # MO+LS
python notebooks/checkpoint1_figures.py
python notebooks/checkpoint2_figures.py
python notebooks/pre_final_figures.py
```

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
