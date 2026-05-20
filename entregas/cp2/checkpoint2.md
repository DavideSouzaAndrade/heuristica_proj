# Checkpoint 2 — TSPTW Multiobjetivo com NSGA-II

**Disciplina:** INF0415 — Heurísticas e Modelagem Multiobjetivo · UFG · 2026/2
**Marco:** Semana 13 (peso 20%)
**Equipe:** Frederico Barbosa Relvas (202403902); Cindy Stephanie Gomes Rabelo (202403898); Davi de Souza Andrade (202403901); Marcos Vinicius Moreira dos Anjos (202400762); João Guilherme da Silva Chaveiro (202403908)
**Repositório:** https://github.com/DavideSouzaAndrade/heuristica_proj — tag `cp2`

## 1. Recap do CP1 e motivação para o multiobjetivo

No Checkpoint 1 tratamos o TSPTW com uma única função penalizada `f(π) = dist(π) + λ · Σ max(0, t_i − l_i)`, com λ=1000. Essa formulação produz **um** ponto no espaço (distância, violação) — o que minimiza a soma ponderada. A discussão crítica do CP1 já antecipou o problema: para `n20w20.001` o AG converge para 374 (com violações) em três das cinco sementes em vez do ótimo factível 378, porque a redução de distância "vale a pena" sob a soma escalar.

O Checkpoint 2 substitui essa soma por uma formulação multiobjetivo: distância e violação total são tratadas como **dois objetivos independentes**, e usamos NSGA-II para obter uma fronteira de Pareto que expõe todo o conjunto de *trade-offs* — não apenas o ponto privilegiado por um λ específico. Essa é exatamente a transição prometida na proposta da Semana 9 e o foco do enunciado para este checkpoint.

## 2. Formulação multiobjetivo

Minimizar simultaneamente:

* **f₁(π) = dist(π)** — distância total do tour fechado (idêntica ao CP1).
* **f₂(π) = Σ max(0, t_i − l_i)** — violação total acumulada nas chegadas, idêntica à parcela do CP1 dividida por λ.

Mesma representação por permutação dos n−1 clientes, mesmas regras de tempo (chegada com espera permitida antes de eᵢ, violação contada após lᵢ), depósito como nó 0 e tour fechado. A região factível é o subconjunto onde f₂(π) = 0.

A escolha de f₂ como violação **total** (e não cardinal "nº de cidades atrasadas") preserva a comparabilidade direta com o AG do CP1: a função penalizada do CP1 é exatamente `f₁ + λ · f₂`, então cada ponto do AG-λ corresponde ao ponto de tangência entre a fronteira e a reta de inclinação −1/λ no espaço dos objetivos. Isso permite sobrepor visualmente os 5 pontos do AG sobre a fronteira NSGA-II e medir o que se perde por usar um λ fixo.

## 3. NSGA-II

Implementado em [`src/nsga.py`](../../src/nsga.py) sobre o framework **pymoo 0.6.1** (encorajado pelo enunciado, sec. 10). Pontos-chave:

* Problema customizado (`TSPTWMOProblem`) — `ElementwiseProblem` com 2 objetivos e variáveis inteiras de 1 a n−1.
* **Operadores reusados do CP1:** Order Crossover (OX) e mutação por inversão, embrulhados em `Crossover`/`Mutation` do pymoo. A semente da `minimize(...)` do pymoo controla o estado global do numpy; cada operador deriva sua RNG dessa fonte para reprodutibilidade.
* **Eliminação de duplicatas** exata sobre as permutações (`ElementwiseDuplicateElimination`).
* **Hiperparâmetros:** `pop_size = 100`, `n_generations = 1500`, `p_mutation = 0,3`. O `pop_size` é menor que o do AG do CP1 (200) porque o NSGA-II tem custo O(N²) por geração no non-dominated sorting; com pop=100 mantemos cerca de 150 000 avaliações por semente, mesma ordem de grandeza por execução. Crossover é sempre aplicado (default do pymoo: probabilidade efetiva = 1,0 com seleção por torneio binário interna).
* **Hypervolume:** indicador padrão para MOO. Para cada instância calculamos um **ponto de referência global**: máximo de (distância, violação) observado entre todas as 5 sementes e todas as gerações, multiplicado por 1,1. Isso garante HV comparável entre sementes para a mesma instância.

## 4. Plano experimental

* Mesmas 5 instâncias do CP1 (`n20w{20,40,60,80,100}.001`), 5 sementes (0–4).
* Para cada semente: NSGA-II 1500 gerações → fronteira final + histórico de HV.
* Comparação direta: os 5 pontos `(distância, violação)` do AG do CP1 (λ=1000) são sobrepostos à fronteira para cada instância.
* Resultados salvos em `entregas/cp2/resultados/<instância>/`.

## 5. Resultados

### 5.1 Síntese por instância

| Instância | |fronteira| (média) | HV (média ± dp) | Melhor dist | Melhor dist factível | Sementes c/ factível | Tempo/seed |
|---|---:|---:|---:|---:|---:|---:|
| n20w20.001  | 62,0 (58–70) | 1,16·10⁶ ± 7,5·10³ | 201,4 (198) | **378** | 5/5 (100%) | 107s |
| n20w40.001  | 49,4 (49–51) | 1,26·10⁵ ± 2,4·10³ | 157   (157) | **254** | 5/5 (100%) | 119s |
| n20w60.001  | 43,6 (41–48) | 7,14·10⁵ ± 2,8·10³ | 183,6 (183) | **335** | 5/5 (100%) | 111s |
| n20w80.001  | 43,6 (40–49) | 6,24·10⁵ ± 3,3·10⁴ | 180   (180) | 330–349 | 2/5 (40%)  | 108s |
| n20w100.001 | 17,4 (15–20) | 9,48·10⁴ ± 1,1·10³ | 191   (191) | **237** | 5/5 (100%) | 105s |

* "Melhor dist" é o mínimo de f₁ na fronteira agregada (com violação alta).
* "Melhor dist factível" é o ponto extremo da fronteira em f₂=0 (igual ao ótimo conhecido na literatura para as 4 instâncias factíveis).
* A fronteira encolhe quando a janela alarga — w=100 tem só ~17 pontos porque há poucas soluções intermediárias informativas (a região factível domina o espaço).

### 5.2 Comparação NSGA-II vs AG do CP1

| Instância | AG (CP1): factível | AG (CP1): dist média | NSGA-II: factível | NSGA-II: melhor factível | Verdict |
|---|---|---|---|---|---|
| n20w20.001  | 40% | 377,0 | **100%** | **378** | NSGA-II claramente mais robusto |
| n20w40.001  | 60% | 253,2 | **100%** | **254** | NSGA-II resolve em todas as sementes |
| n20w60.001  | 100% | 335,0 | 100% | 335 | Empate (mesmo ótimo, mesma robustez) |
| n20w80.001  | 100% | 339,6 | 40% | 330–349 | **AG melhor** em garantia de viabilidade |
| n20w100.001 | 100% | 239,4 | 100% | 237 | NSGA-II ligeiramente melhor (237 vs 239,4) |

**Observação central** (visível em `fig3_nsga_vs_ag.png` para n20w20.001): os 5 pontos do AG-λ=1000 ou *coincidem* com a fronteira NSGA-II (2 sementes em (378, 0)) ou são **dominados** por ela (3 sementes em (374, 136), (378, 409), (378, 496) — todos com vizinhos NSGA-II em viol≈0). Não há nenhum ponto do AG fora da fronteira NSGA-II em direção a "menor distância ou menor violação". Ou seja, **o AG-λ=1000 não encontra nada que o NSGA-II também não encontre, mas o NSGA-II encontra muito mais**.

O caso `n20w80.001` é a única reversão: o AG do CP1 era 100% factível (4 sementes em 329–335, 1 outlier em 370), enquanto o NSGA-II só atinge viabilidade em 2/5 sementes. A causa é estrutural — o NSGA-II preserva diversidade ao longo de toda a fronteira; quando muitos pontos quase-factíveis (viol≈5–20) dominam visualmente o último ponto factível, o crowding-distance pode descartar candidatos próximos da fronteira de viabilidade. O AG penalizado, por outro lado, *empurra* tudo para viol=0. Esse é um *trade-off* real entre os dois métodos, e a motivação direta para o diferencial D1 (hibridização AG + 2-opt sobre indivíduos da fronteira).

### 5.3 Figuras

Em `entregas/cp2/figuras/`:

* `fig1_pareto.png` — fronteiras de Pareto por instância (5 painéis), cada um com 5 fronteiras (uma por semente) e os 5 pontos do AG do CP1 sobrepostos como X vermelho. A linha tracejada verde marca f₂=0 (viabilidade).
* `fig2_hypervolume.png` — hypervolume ao longo das gerações (média ± desvio sobre 5 sementes), uma curva por instância. Mostra a velocidade de convergência da fronteira.
* `fig3_nsga_vs_ag.png` — zoom em `n20w20.001` (instância mais difícil): fronteira agregada NSGA-II vs. 5 pontos do AG-λ=1000, com a linha de viabilidade destacada.
* `fig4_front_size.png` — distribuição do tamanho da fronteira (esquerda) e do número de soluções factíveis na fronteira (direita) por largura de janela.

## 6. Discussão de trade-offs

1. **A fronteira expõe o que o λ=1000 do CP1 ocultava.** No CP1, escolher λ=1000 fixou a "preferência" de quem otimiza: cada unidade de violação valia 1000 unidades de distância. No CP2, a fronteira NSGA-II mostra **toda a família de soluções** que esse trade-off poderia gerar, deixando a escolha para depois. Em `n20w20.001`, por exemplo, a fronteira tem 62 pontos cobrindo desde tours de 198 unidades (com violação 5450) até 378 unidades (factíveis). Cada um pode ser o ótimo dependendo de quem decide — um cliente, uma política, um critério de equidade.

2. **NSGA-II é mais robusto para garantir viabilidade em janelas estreitas.** O contraste mais claro é `n20w20.001`: 2/5 sementes factíveis no AG do CP1 (penalização escalar) versus 5/5 no NSGA-II. A formulação multiobjetivo evita o "atalho infactível" (374 com poucas violações domina 378 no AG porque a soma f₁+λ·f₂ é menor com λ insuficiente) — no NSGA-II, esses dois pontos são mutuamente não-dominados e ambos são preservados.

3. **Mas NSGA-II pode perder viabilidade onde o AG penalizado não perderia.** Em `n20w80.001`, o AG (CP1) era 100% factível enquanto o NSGA-II é apenas 40%. O motivo: a diversidade preservada pelo crowding-distance privilegia espalhamento na fronteira sobre concentração na fronteira de viabilidade. Quando muitos pontos têm violação pequena mas positiva (e.g. 5–20), o NSGA-II considera todos eles "interessantes" e não pressiona em direção a viol=0. Esse é exatamente o gap que o **diferencial D1 (memetic: NSGA-II + 2-opt)** preencheria — aplicar busca local sobre indivíduos próximos da viabilidade tipicamente custa pouco e empurra a fronteira para baixo.

4. **A convergência do hypervolume sugere espaço para cortar orçamento.** A `fig2_hypervolume.png` mostra HV próximo do platô em ~400 gerações para todas as instâncias. Reduzir `n_generations` de 1500 para 800 cortaria ~45% do tempo sem perda visível de qualidade. Vale para a entrega final, quando rodaremos 10 sementes.

5. **O tamanho da fronteira é um indicador de "dificuldade" do trade-off.** `fig4_front_size.png` mostra |fronteira| caindo de ~62 (w=20) para ~17 (w=100). Janelas mais largas tornam o problema "quase single-objective": a região factível é grande o suficiente para que o NSGA-II ache poucas soluções intermediárias informativas. Para w=100, a fronteira tem só 15–20 pontos porque qualquer solução modestamente boa já é factível.

6. **A tabela de viabilidade não diz tudo.** Mesmo onde NSGA-II "perdeu" (w=80), o melhor factível encontrado por ele em 2 das 5 sementes (330) é *melhor* que o do AG (média 339,6, mediana 330). Ou seja, *quando* NSGA-II atinge viabilidade, ele tende a atingi-la com tours mais curtos — o que combina com a maior diversidade explorada.

## 7. Próximos passos (Pré-final, Semana 15)

* Escolher um diferencial principal e integrá-lo. Candidato número 1: **D1 (hibridização memetic)** — aplicar 2-opt sobre os indivíduos da fronteira a cada N gerações para empurrar a fronteira para baixo (mais soluções factíveis) e para a esquerda (menos distância).
* Candidato número 2: **D2 (warm-start)** — semear a população inicial com NN-urgency + perturbações para acelerar a convergência inicial.
* Iniciar o relatório técnico longo no formato IEEE/ACM (seção 8 do enunciado).
* Expandir o conjunto de instâncias para 10 sementes e mais instâncias por classe, conforme R3.

## 8. Reprodutibilidade

```bash
git clone https://github.com/DavideSouzaAndrade/heuristica_proj.git
cd heuristica_proj
git checkout cp2
pip install -r requirements.txt
python -m src.experiment_moo --instance cp1 --seeds 5 --tag cp2
python notebooks/checkpoint2_figures.py
```

Saídas em `entregas/cp2/resultados/` e `entregas/cp2/figuras/`. Sementes 0–4 fixadas via `seed=` na chamada do `pymoo.optimize.minimize` (controla `numpy.random` global).

## 9. Declaração de uso de IA generativa

Mantém-se o uso descrito no CP1: Claude Code (Anthropic) atuando como assistente de programação, com decisões metodológicas e interpretação dos resultados feitas pela equipe.

## Referências adicionais (acumuladas com CP1)

* Deb, K.; Pratap, A.; Agarwal, S.; Meyarivan, T. (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. *IEEE Transactions on Evolutionary Computation*, 6(2), 182–197.
* Blank, J.; Deb, K. (2020). pymoo: Multi-Objective Optimization in Python. *IEEE Access*, 8, 89497–89509.
* Zitzler, E.; Thiele, L. (1999). Multiobjective evolutionary algorithms: a comparative case study and the strength Pareto approach. *IEEE Transactions on Evolutionary Computation*, 3(4), 257–271. (Hypervolume indicator.)
