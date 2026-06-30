# Tabela mestra de benchmark — TSPTW

Consolidação dos 4 métodos comparados + 1 baseline determinístico, 5 instâncias × 10 sementes = 200 execuções controladas.

Ótimos conhecidos da literatura para essas instâncias: **378, 254, 335, 329, 237** (n20w{20,40,60,80,100}.001).

| Instância | Método | dist mean | dist std | min | max | mediana | viol mean | feas | best factível | HV (unif) | tempo/seed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| n20w20.001 | Random | 419.3 | 17.15 | 390 | 439 | 423 | 1348 | 0/10 (0%) | — | — | 27.2s |
| n20w20.001 | NN-urgency | 386 | — | 386 | 386 | 386 | 314 | 0/1 | — | — | <1s (determinístico) |
| n20w20.001 | AG (SO-λ) | 380.4 | 6.45 | 374 | 395 | 378 | 158 | 3/10 (30%) | 378 | — | 31.5s |
| n20w20.001 | NSGA-II puro | 200.1 | 3.78 | 198 | 209 | 198 | — (fronteira) | 9/10 (90%) | 378 | 1.195e+06 | 101.9s |
| n20w20.001 | NSGA-II + 2-opt (D1) | 202.5 | 5.08 | 198 | 209 | 201 | — (fronteira) | 8/10 (80%) | 378 | 1.192e+06 | 91.1s |
| n20w40.001 | Random | 355.6 | 26.09 | 312 | 392 | 364 | 938 | 0/10 (0%) | — | — | 25.3s |
| n20w40.001 | NN-urgency | 282 | — | 282 | 282 | 282 | 71 | 0/1 | — | — | <1s (determinístico) |
| n20w40.001 | AG (SO-λ) | 253.6 | 0.84 | 252 | 254 | 254 | 9 | 8/10 (80%) | 254 | — | 28.5s |
| n20w40.001 | NSGA-II puro | 157.0 | 0.00 | 157 | 157 | 157 | — (fronteira) | 9/10 (90%) | 254 | 1.260e+05 | 104.1s |
| n20w40.001 | NSGA-II + 2-opt (D1) | 157.0 | 0.00 | 157 | 157 | 157 | — (fronteira) | 10/10 (100%) | 254 | 1.273e+05 | 93.0s |
| n20w60.001 | Random | 412.3 | 25.29 | 376 | 450 | 414 | 811 | 0/10 (0%) | — | — | 23.9s |
| n20w60.001 | NN-urgency | 393 | — | 393 | 393 | 393 | 0 | 1/1 | 393 | — | <1s (determinístico) |
| n20w60.001 | AG (SO-λ) | 337.2 | 4.64 | 335 | 346 | 335 | 0 | 10/10 (100%) | 335 | — | 26.0s |
| n20w60.001 | NSGA-II puro | 183.6 | 0.84 | 183 | 185 | 183 | — (fronteira) | 10/10 (100%) | 335 | 7.138e+05 | 100.2s |
| n20w60.001 | NSGA-II + 2-opt (D1) | 183.8 | 0.92 | 183 | 186 | 184 | — (fronteira) | 10/10 (100%) | 335 | 7.140e+05 | 114.7s |
| n20w80.001 | Random | 461.7 | 40.60 | 392 | 528 | 464 | 1067 | 0/10 (0%) | — | — | 23.7s |
| n20w80.001 | NN-urgency | 396 | — | 396 | 396 | 396 | 0 | 1/1 | 396 | — | <1s (determinístico) |
| n20w80.001 | AG (SO-λ) | 332.4 | 14.41 | 319 | 370 | 330 | 38 | 8/10 (80%) | 329 | — | 26.8s |
| n20w80.001 | NSGA-II puro | 180.0 | 0.00 | 180 | 180 | 180 | — (fronteira) | 2/10 (20%) | 329 | 6.436e+05 | 103.4s |
| n20w80.001 | NSGA-II + 2-opt (D1) | 180.0 | 0.00 | 180 | 180 | 180 | — (fronteira) | 4/10 (40%) | 329 | 6.393e+05 | 120.3s |
| n20w100.001 | Random | 404.5 | 32.28 | 334 | 450 | 412 | 593 | 0/10 (0%) | — | — | 23.6s |
| n20w100.001 | NN-urgency | 387 | — | 387 | 387 | 387 | 373 | 0/1 | — | — | <1s (determinístico) |
| n20w100.001 | AG (SO-λ) | 242.1 | 12.17 | 237 | 276 | 237 | 0 | 10/10 (100%) | 237 | — | 25.5s |
| n20w100.001 | NSGA-II puro | 191.4 | 1.26 | 191 | 195 | 191 | — (fronteira) | 10/10 (100%) | 237 | 9.474e+04 | 100.8s |
| n20w100.001 | NSGA-II + 2-opt (D1) | 191.0 | 0.00 | 191 | 191 | 191 | — (fronteira) | 10/10 (100%) | 237 | 9.473e+04 | 99.7s |

## Legenda

- **Random** e **AG (SO-λ)**: distância é a do tour final retornado.
- **NSGA-II puro** e **NSGA-II + 2-opt (D1)**: dist é o mínimo da fronteira (pode ser infactível); coluna `best factível` é o ponto extremo da fronteira com viol = 0 (ou — se inexistente).
- **HV (unif)**: hypervolume sob ponto-ref **unificado** entre puro e memetic, calculado por instância (max observado × 1,1 + 1).
- **feas**: número de sementes (de 10) com pelo menos uma solução factível encontrada. Random vai sempre 0/10 (em 3 milhões de permutações geradas, nenhuma foi factível).
- **NN-urgency**: determinístico (1 execução por instância).

## Como ler em uma frase

Procure a coluna **feas** para robustez de viabilidade. Procure **best factível** para qualidade da melhor solução factível. Procure **HV (unif)** para qualidade global da fronteira (apenas MO).