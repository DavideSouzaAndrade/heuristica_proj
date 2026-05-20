# Checkpoint 1 — TSPTW com Algoritmo Genético

**Disciplina:** INF0415 — Heurísticas e Modelagem Multiobjetivo · UFG · 2026/2
**Marco:** Semana 11 (peso 15%)
**Equipe:** Frederico Barbosa Relvas (202403902); Cindy Stephanie Gomes Rabelo (202403898); Davi de Souza Andrade (202403901); Marcos Vinicius Moreira dos Anjos (202400762); João Guilherme da Silva Chaveiro (202403908)

## 1. Modelagem implementada

A modelagem prometida na proposta da Semana 9 foi codificada em Python (3.13). Uma solução é uma permutação π = (π₁, …, πₙ) dos n clientes; o depósito (nó 0) é prefixo e sufixo implícitos. Para cada nó πₖ da rota, o tempo de chegada tₖ é calculado incrementalmente:

> tₖ = max(tₖ₋₁ + travel(πₖ₋₁, πₖ), eπₖ)

— se o agente chega antes da abertura, ele espera (não há violação); o instante de saída do nó é exatamente o início do atendimento. O tempo de serviço é zero (Dumas et al., 1995). O retorno ao depósito é avaliado da mesma forma, e seu fechamento (`l₀`) limita o horizonte da rota.

A função objetivo single-objective com penalização é

> f(π) = dist(π) + λ · Σ max(0, tₖ − lπₖ)

com λ = 1000. Esse valor foi escolhido após um pequeno *sweep* (100, 500, 1000, 5000): valores abaixo de 1000 não dominam ganhos de distância no entorno do ótimo; acima disso o efeito satura. Para o Checkpoint 2 a violação total será tratada como segundo objetivo no NSGA-II em vez de penalização escalar, conforme prometido na proposta.

## 2. Instâncias

Foram usadas as cinco primeiras instâncias da família Dumas n=20 — uma por largura média de janela — obtidas do repositório de López-Ibáñez (`Dumas.tar.gz`, 27 classes × 5 instâncias).

| Instância | Clientes | Largura média de janela |
|---|---|---|
| n20w20.001 | 20 | ~20 |
| n20w40.001 | 20 | ~40 |
| n20w60.001 | 20 | ~60 |
| n20w80.001 | 20 | ~80 |
| n20w100.001 | 20 | ~100 |

O subconjunto cobre o gradiente "muito restrito → folgado" e permite avaliar como o AG se comporta quando a região factível diminui. A entrega final (Semana 16) usará todas as 25 instâncias n=20 e ainda incluirá n=40 e n=60 conforme orçamento computacional permitir.

## 3. Algoritmo

**Baseline.** Nearest Neighbor com critério `urgency` (combinação convexa entre tempo de chegada e fechamento da janela, α = 0.5). A variante por distância pura (`travel`) também foi implementada para comparação interna mas não consegue respeitar janelas estreitas. É um único *run* determinístico.

**Algoritmo Genético** (`src/ga.py`):

* Representação: permutação dos n − 1 = 20 clientes (`numpy.int64`).
* Inicialização: `pop_size` permutações aleatórias (cold-start; warm-start é diferencial D2 e fica para o pré-final).
* Seleção: torneio binário com k = 3.
* Crossover: Order Crossover (OX) com probabilidade 0,9.
* Mutação: inversão de segmento com probabilidade 0,3.
* Elitismo: top-2 indivíduos passam intactos.
* Parâmetros: `pop_size = 200`, `n_generations = 1500`, `λ = 1000`.

A fixação de seed é via `numpy.random.default_rng(seed)`, propagada para população inicial, seleção, crossover e mutação. Cada semente é portanto totalmente reproduzível.

## 4. Plano experimental

Para cada instância são comparados três métodos:

* **Busca aleatória** como referência inferior (cumpre a promessa da proposta da Sem 9), amostrando o mesmo número de avaliações que o AG (`pop_size · n_generations = 300 000` por semente). Reporta o melhor encontrado.
* **NN-urgency** como referência construtiva (R4) — determinístico, uma rodada.
* **AG** com 5 sementes (0–4).

Cinco sementes atendem à exigência mínima do Checkpoint 1; a entrega final usará 10 sementes para cumprir R3 plenamente. Reporta-se distância, violação total, viabilidade, fitness, tempo de parede e dois tamanhos de efeito (R3: "não apenas significância"):

* **Cliff's δ** — não-paramétrico, ∈ [−1, 1]; magnitude por Romano et al. (2006): |δ|<0,147 negligível, <0,33 pequeno, <0,474 médio, ≥0,474 grande.
* **Hedges' g** — versão de Cohen's d com correção de bias para amostras pequenas; |g|>0,8 é grande.

Resultados salvos em `results/runs/cp1/<instância>/`.

## 5. Resultados

### 5.1 Comparação entre métodos

| Instância | Random média (faixa) | NN | AG média ± dp | AG min–max | AG factíveis |
|---|---:|---:|---:|---:|---:|
| n20w20.001  | 426,2 (413–439) | 386 *(1 atr.)* | **377,0 ± 1,7** | 374–378 | 2/5 (40%) |
| n20w40.001  | 347,2 (312–376) | 282 *(1 atr.)* | **253,2 ± 1,1** | 252–254 | 3/5 (60%) |
| n20w60.001  | 411,8 (379–450) | 393 *(OK)*     | **335,0 ± 0,0** | 335–335 | 5/5 (100%) |
| n20w80.001  | 471,0 (437–528) | 396 *(OK)*     | **339,6 ± 17,5**| 329–370 | 5/5 (100%) |
| n20w100.001 | 407,0 (373–430) | 387 *(2 atr.)* | **239,4 ± 3,3** | 237–243 | 5/5 (100%) |

A busca aleatória (5 sementes × 300 000 avaliações cada, mesmo orçamento que o AG) foi **0% factível em todas as instâncias** — em 1,5 milhão de permutações uniformes nenhuma respeitou as janelas, confirmando que a região factível é minúscula no espaço de busca. O AG supera o NN em distância em todas as instâncias; em `n20w20.001` atinge o ótimo conhecido na literatura (378) em duas das cinco sementes.

### 5.2 Significância e tamanho do efeito

Wilcoxon pareado unilateral H₁: dist(AG) < dist(referência). Com 5 sementes o menor p-valor possível é 1/2⁵ ≈ 0,031.

| Instância | p-Wilcoxon vs NN | Cliff δ vs NN | Hedges g vs NN | p-Wilcoxon vs Random | Cliff δ vs Random | Hedges g vs Random |
|---|---:|---:|---:|---:|---:|---:|
| n20w20.001  | 0,031 | −1,000 (grande) | −4,16  | 0,031 | −1,000 (grande) | −6,26  |
| n20w40.001  | 0,031 | −1,000 (grande) | −21,03 | 0,031 | −1,000 (grande) | −4,67  |
| n20w60.001  | 0,031 | −1,000 (grande) | −∞ *(σ_AG=0)* | 0,031 | −1,000 (grande) | −3,31  |
| n20w80.001  | 0,031 | −1,000 (grande) | −2,58  | 0,031 | −1,000 (grande) | −4,21  |
| n20w100.001 | 0,031 | −1,000 (grande) | −35,93 | 0,031 | −1,000 (grande) | −10,13 |

Em todas as cinco instâncias, **Cliff's δ = −1,000** (grande, magnitude máxima) tanto contra o NN quanto contra o Random: nenhuma semente do AG foi pior que a respectiva referência. Hedges' g está bem acima de 0,8 (limiar de "grande") em todas — em n20w60.001 a variância nula do AG (todas as 5 sementes convergem a 335) gera g → −∞, indicando separação perfeita entre as distribuições. A entrega final reexecutará tudo com 10 sementes e aplicará correção de Bonferroni sobre as 5 comparações.

### 5.3 Figuras

Em `reports/figures/cp1/`:

* `fig1_convergencia.png` — melhor fitness por geração do AG, média ± desvio sobre 5 sementes, uma curva por instância. A escala log evidencia o "degrau" quando o AG empurra a solução para a região factível: o fitness cai de ≈10⁵ (dominado pela penalização Σ violação · λ) para ≈10² (apenas distância).
* `fig2_boxplot.png` — boxplots de AG (azul) vs. busca aleatória (cinza), com NN como losango vermelho. As caixas do AG ficam abaixo de todas as referências em todas as instâncias; a folga até o Random ancora a magnitude do ganho da meta-heurística.
* `fig3_rota.png` — melhor tour para `n20w20.001` (distância 378, factível): à esquerda o circuito sobre layout MDS clássico (o dataset Dumas só traz a matriz de distâncias); à direita um Gantt com as janelas em cinza e a chegada em verde. Todas as chegadas caem dentro das janelas.
* `fig4_viabilidade.png` — taxa de sementes factíveis do AG (barras azuis, esquerda) vs. largura média da janela; sobreposto, distância média do AG (vermelho), do NN (azul-escuro) e do Random (cinza). Random fica sempre acima de NN, que fica sempre acima do AG.

## 6. Discussão

1. **Penalização escalar com λ fixo deixa "tours quase factíveis" na frente do ótimo factível.** O AG converge para distância 374 (com violações) em três das cinco sementes da instância mais difícil, enquanto o ótimo factível é 378. Como λ·violação é da ordem de 10³–10⁵ enquanto a redução de distância é de unidades, a fitness penalizada do quase-factível é alta — mas o AG, ao optar por elitismo + torneio, ainda assim fica preso no platô infactível. Isso é exatamente a motivação para a fronteira de Pareto do Checkpoint 2: tratar violação como segundo objetivo permite enxergar os dois regimes simultaneamente.

2. **Janelas mais largas tornam o problema "fácil" tanto em distância quanto em viabilidade.** Para w ≥ 60 a viabilidade vai a 100% e o ganho sobre o NN cresce de −14% a −38%. O NN-urgency, por privilegiar urgência, ignora *trade-offs* globais que ficam acessíveis quando as janelas relaxam — o AG explora esses *trade-offs* livremente.

3. **O baseline NN-urgency é forte mas frequentemente infactível.** Em três das cinco instâncias o NN viola alguma janela. Isso indica que warm-start (D2) com uma única rodada de NN como semente não é suficiente; valeria a pena perturbar NN com pequenas trocas (NN + 2-opt) — o que se conecta naturalmente ao diferencial D1 (memetic). Esses dois diferenciais são os primeiros candidatos para o pré-final.

4. **Variação entre sementes não é uniforme.** Em `n20w60.001` todas as cinco sementes convergem ao mesmo valor (335). Em `n20w80.001` há um *outlier* persistente (370) — ou seja, uma bacia de atração subótima que o AG não consegue escapar com `p_mutation = 0,3`. Aumentar a pressão de diversificação (reinicialização parcial, mutação adaptativa) ou hibridizar com 2-opt resolveria — material para o pré-final.

5. **Busca aleatória factual = 0%.** Com 300 000 amostras uniformes por semente — o mesmo orçamento computacional do AG — nenhuma das 1,5 milhão de permutações geradas respeitou simultaneamente todas as janelas em qualquer das cinco instâncias. Isso quantifica empiricamente a "estreiteza" da região factível e justifica que a comparação direta de qualidade (distância pura) entre Random, NN e AG só faz sentido sob a função objetivo penalizada que adotamos.

## 7. Próximos passos (Checkpoint 2, Semana 13)

* Substituir a penalização escalar por dois objetivos (distância, violação total) com NSGA-II via `pymoo`.
* Comparar a fronteira de Pareto resultante com o melhor *trade-off* implícito do AG single-objective (variando λ).
* Escolher o diferencial principal: a primeira escolha em discussão é **D1 (hibridização AG + 2-opt)** porque o gap entre as soluções com violação e o ótimo factível é tipicamente uma única troca 2-opt no entorno do nó violado.

## 8. Reprodutibilidade

```bash
pip install -r requirements.txt
python -m src.experiment --instance cp1 --seeds 5
python notebooks/checkpoint1_figures.py
```

Repositório: a ser publicado no GitHub antes do pré-final (Semana 15).

## 9. Declaração de uso de IA generativa

Claude Code (Anthropic) foi usado como assistente de programação para estruturar o esqueleto do projeto, escrever boilerplate e debugar interativamente. Todas as decisões de modelagem, escolha de hiperparâmetros e interpretação dos resultados são da equipe.

## Referências

* Dumas, Y.; Desrosiers, J.; Gélinas, É.; Solomon, M. M. (1995). An optimal algorithm for the traveling salesman problem with time windows. *Operations Research*, 43(2), 367–371.
* López-Ibáñez, M. (s.d.). TSPTW instances. Disponível em https://lopez-ibanez.eu/tsptw-instances.
* Davis, L. (1985). Applying adaptive algorithms to epistatic domains. *IJCAI*, 162–164. (Order Crossover OX.)
