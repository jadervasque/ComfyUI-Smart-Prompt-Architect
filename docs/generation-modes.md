# Modos de geração

Todos os modos são determinísticos para perfil, configuração, seed e batch index idênticos.

## `strict`

Mantém filtros, remove opções experimentais, reforça pesos e preferências de coerência e nunca
relaxa tags. Regras absolutas continuam obrigatórias em todos os modos.

## `balanced`

Seleciona primeiro a família semântica e depois uma opção usando os pesos declarados. Pode relaxar
filtros opcionais de tags quando não existe candidato, registrando aviso.

## `creative`

Usa raiz quadrada dos pesos para elevar a presença relativa de itens raros e reduz a força de
preferências, sem permitir exclusões ou requisitos inválidos.

## `dataset`

Escolhe famílias e opções uniformemente, priorizando cobertura em vez de popularidade. Use
`batch_index` igual ao índice da amostra.

## `sequential`

Percorre famílias e opções em ciclo estável controlado por `batch_index`. É adequado para inspeção
previsível e lotes sem aleatoriedade de distribuição.

`tests/test_catalog_v2.py` mede o aumento de raridade em `creative`, a estratificação de `dataset` e
o ciclo de `sequential`.
