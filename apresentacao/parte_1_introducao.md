# Parte 1 — Introdução  (2 minutos · slides 1–2)

Você abre a apresentação. Sua responsabilidade é **enganchar a plateia em 2 minutos**: explicar o problema, dar uma motivação concreta e deixar claro o que o grupo vai mostrar nos próximos 13 minutos.

## Visão geral
Cobre:
- Quem é o grupo e qual é a equipe (rápido).
- O que é o TSPTW e por que ele importa (motivação prática).
- A pergunta central do projeto que será respondida nas próximas partes.

## O que você precisa internalizar

### Conceito 1 — O que é TSPTW (em 1 frase)
> "O Problema do Caixeiro Viajante com Janelas de Tempo é uma extensão do TSP onde cada cidade tem um intervalo de tempo `[e_i, l_i]` dentro do qual a visita precisa começar — se você chega cedo, espera; se chega tarde, viola."

### Conceito 2 — Por que importa (analogia prática)
Escolha **uma** destas para usar (não as três, escolha a que te sentir mais natural):
- Entrega: "uma transportadora não pode entregar uma encomenda às 3 da manhã."
- Saúde: "consulta médica agendada não pode chegar 2 horas atrasada."
- Logística: "um caminhão de coleta de lixo tem que passar nos bairros em janelas combinadas."

### Conceito 3 — A pergunta do projeto (em 1 frase)
> "Como otimizar simultaneamente a distância total da rota E o respeito às janelas de tempo, quando esses dois objetivos podem se conflitar?"

A resposta dessa pergunta é o que os próximos 4 colegas vão construir — **não responda ela na intro**, apenas plante a curiosidade.

## Números-chave (memorize)
- O problema é o **P5** do enunciado da disciplina.
- O grupo tem **5 integrantes**.
- A apresentação cobre **5 instâncias** de teste do conjunto Dumas.
- Total de execuções controladas no projeto: **200** (5 instâncias × 10 sementes × 4 métodos).

## Roteiro sugerido (slide a slide)

### Slide 1 — Roteiro (capa)
**Tempo: 30 s**

O que falar:
- Cumprimente brevemente.
- Diga o título: "Algoritmos memetic multiobjetivo para o TSP com janelas de tempo."
- Diga que é o projeto final da disciplina INF0415.
- Apresente a divisão da apresentação rapidamente — "vamos passar por contextualização, duas propostas de solução e a conclusão."

Frase de abertura sugerida:
> "Bom dia/tarde a todos. Vou apresentar com o grupo o projeto final da disciplina INF0415, onde atacamos o problema do Caixeiro Viajante com Janelas de Tempo — TSPTW. A apresentação está dividida em cinco partes: começo agora com a introdução, depois meu colega explica a formulação, e em seguida apresentamos as duas propostas de solução e a conclusão."

### Slide 2 — Problema e motivação
**Tempo: 1 min 30 s**

O que falar:
1. **Defina o TSPTW** usando a frase do Conceito 1 acima.
2. **Dê a motivação** com **uma** das analogias práticas (escolha antes do dia).
3. **Plante a pergunta do projeto**.

Frase de fechamento sugerida:
> "A pergunta central do nosso trabalho é: como otimizar simultaneamente o tamanho da rota E o respeito às janelas, quando esses dois critérios podem se conflitar? Nas próximas partes vocês vão ver duas formas distintas de responder isso e o que aprendemos sobre cada uma."

## Transição para o próximo apresentador
> "Passo a palavra para o(a) [colega da Parte 2], que vai explicar a formulação matemática que adotamos e as instâncias de teste."

## Perguntas que você pode receber

**P: Por que escolheram o TSPTW e não outro problema?**
> "Três razões: (1) é uma extensão de um problema clássico, então temos muito material de comparação e ótimos conhecidos na literatura para validar nossa implementação; (2) tem aplicação real direta em logística com restrições temporais; (3) a restrição de janelas torna o espaço de busca muito mais difícil — a região factível é uma fração minúscula do espaço total de permutações, e essa dificuldade é o interesse central do projeto."

**P: O que torna o TSPTW diferente do TSP clássico?**
> "A janela de tempo. No TSP padrão, a única restrição é visitar cada cidade uma vez. No TSPTW, cada cidade tem um intervalo `[e_i, l_i]`. Isso adiciona uma dimensão temporal ao problema — agora a ordem das cidades importa não só pela distância, mas pelo *quando* você chega em cada uma."

**P: Vocês trabalharam em quantas instâncias?**
> "Usamos 5 instâncias representativas do conjunto Dumas com 20 clientes cada — uma para cada largura média de janela (20, 40, 60, 80, 100). Cada uma foi rodada com 10 sementes diferentes em quatro métodos, totalizando 200 execuções controladas."

## Dicas de execução

- **Olhe para a plateia, não para o slide.** O slide 2 é seu apoio, não seu script.
- **Cuide do tempo.** Se você passar de 2 min, está roubando tempo dos colegas.
- **Não entre em formalismo matemático aqui.** Quem faz isso é a Parte 2.
- **Cuide do tom.** A intro é onde a plateia decide se vai prestar atenção. Fale com energia.

## Materiais de apoio

- Slides do reveal.js: [`../entregas/final/slides.html`](../entregas/final/slides.html) (abra no navegador, use seta direita)
- Resumo (abstract) do paper: primeira página de [`../entregas/final/relatorio.pdf`](../entregas/final/relatorio.pdf) — leia para internalizar a linha narrativa.
