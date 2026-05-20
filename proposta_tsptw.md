**Proposta de Projeto Final**

Problema P5 — TSP com Janelas de Tempo (TSPTW)

# **1\. Equipe**

| Nome | Matrícula |
| ----- | ----- |
| Frederico Barbosa Relvas | 202403902 |
| Cindy Stephanie Gomes Rabelo | 202403898 |
| Davi de Souza Andrade | 202403901 |
| Marcos Vinicius Moreira dos Anjos | 202400762 |
| João Guilherme da Silva Chaveiro | 202403908 |

# **2\. Problema Escolhido**

O problema escolhido é o Travelling Salesman Problem with Time Windows (TSPTW), identificado como P5 no enunciado do projeto. Trata-se de uma extensão do clássico Problema do Caixeiro Viajante (TSP) em que cada cidade deve ser visitada dentro de um intervalo de tempo definido — a chamada janela de tempo — tornando o problema significativamente mais restrito e desafiador do ponto de vista de otimização.

# **3\. Justificativa**

A escolha do TSPTW é motivada por três razões principais. Primeiro, o TSP é um dos problemas combinatórios mais estudados da literatura, o que garante ampla disponibilidade de referências, instâncias padronizadas e métricas de comparação bem estabelecidas. Acreditamos que dominar versões mais complexas de problemas clássicos é fundamental para desenvolver a capacidade de abordar problemas inéditos com rigor.

Segundo, há valor significativo em aprofundar fundamentos: entender bem o TSPTW e suas restrições temporais prepara o grupo para lidar com variantes ainda mais complexas, como o VRP com janelas de tempo (VRPTW), amplamente utilizado em logística real. A adição das janelas de tempo transforma o TSP em um problema com restrições ativas, o que torna o projeto das heurísticas e dos operadores evolutivos o principal desafio intelectual da atividade.

Terceiro, o grupo já possui código funcional de TSP implementado nas semanas 5 e 6 da disciplina — Hill Climbing com 2-opt e Simulated Annealing — o que permite reutilizar essa base de forma legítima e focar o esforço no que é novo: modelar as janelas de tempo, adaptar os operadores e comparar os algoritmos de forma estatisticamente válida.

# **4\. Formulação Preliminar**

## **4.1 Variáveis de decisão**

Uma solução é representada por uma permutação π \= (π₁, π₂, …, πₙ) das n cidades, que define a ordem de visita. A partir dessa permutação, os instantes de chegada tᵢ em cada cidade são determinados deterministicamente: o agente parte da cidade π₁ no instante zero e, ao chegar à cidade πᵢ antes de sua janela abrir, aguarda até o instante de abertura eᵢ antes de prosseguir.

## **4.2 Função objetivo**

O objetivo primário é minimizar a distância total percorrida no tour fechado. Violações de janela de tempo são tratadas como penalização aditiva na função objetivo, evitando descartar soluções infactíveis durante a busca:

**f(π) \= dist(π) \+ λ · Σ max(0, tᵢ − lᵢ)**

onde dist(π) é a distância total do tour, lᵢ é o instante de fechamento da janela da cidade πᵢ, tᵢ é o instante de chegada calculado, e λ é o coeficiente de penalização. Essa abordagem permite que o algoritmo aprenda a evitar violações naturalmente ao longo das gerações, sem tornar o espaço de busca desconexo.

Na fase multiobjetivo (Checkpoint 2), distância total e número de violações de janela serão tratados como dois objetivos independentes no NSGA-II, gerando uma fronteira de Pareto entre tours curtos e tours factíveis.

## **4.3 Restrições**

* Cada cidade deve ser visitada exatamente uma vez (restrição de permutação).

* Se o agente chegar antes de eᵢ (abertura), ele espera — sem violação.

* Se chegar após lᵢ (fechamento), ocorre violação penalizada por λ.

* O tour é fechado: o agente retorna à cidade de origem ao final.

## **4.4 Metaheurísticas planejadas**

* Algoritmo Genético com crossover Order Crossover (OX) e penalização de violações — método populacional principal.

* Simulated Annealing com vizinhança 2-opt — método de busca local para comparação.

* Busca Tabu com 2-opt — se inspirando na implementação da Semana 6\.

## **4.5 Instâncias e baseline**

Serão utilizadas instâncias clássicas dos benchmarks de Dumas et al. (1995) e Pesant et al. (1998), amplamente usadas na literatura. O baseline será a heurística construtiva do vizinho mais próximo com respeito às janelas de tempo, comparada com busca aleatória como referência inferior.

# **5\. Referências Iniciais**

1. DUMAS, J.-Y.; DESROSIERS, J.; SOUMIS, F. The pickup and delivery problem with time windows. European Journal of Operational Research, v. 54, n. 1, p. 7–22, 1991\.

2. GENDREAU, M.; HERTZ, A.; LAPORTE, G. A tabu search heuristic for the vehicle routing problem. Management Science, v. 40, n. 10, p. 1276–1290, 1994\.

3. POTVIN, J.-Y.; BENGIO, S. The vehicle routing problem with time windows — Part II: Genetic search. INFORMS Journal on Computing, v. 8, n. 2, p. 165–172, 1996\.

4. GAMBARDELLA, L. M.; DORIGO, M. Solving symmetric and asymmetric TSPs by ant colonies. Proceedings of IEEE ICEC, p. 622–627, 1996\.

5. CORDEAU, J.-F. et al. A guide to vehicle routing heuristics. Journal of the Operational Research Society, v. 53, n. 5, p. 512–522, 2002\.