# Catálogo V2

O catálogo `2.0.0` contém 5.184 opções semânticas e 15.552 variantes textuais distribuídas em 81
packs, 69 bibliotecas lógicas e nove domínios.

| Domínio | Opções |
|---|---:|
| identity | 896 |
| hair | 320 |
| body | 64 |
| wardrobe | 1.088 |
| performance | 384 |
| scene | 896 |
| cinematography | 832 |
| style | 448 |
| negative | 256 |

Cada opção é uma combinação atômica de duas facets controladas. Por exemplo, `eye-color` combina
família cromática e subtom; `lighting-setup` combina arranjo e contraste; `tops` combina tipo de
peça e construção. Isso evita frases monolíticas misturando sujeito, roupa, pose e câmera.

## Índice e packs

O índice declara:

- ID, versão, idioma e estado;
- biblioteca lógica e domínio;
- caminho relativo seguro;
- classe de segurança;
- tags, dependências e prioridade.

O pack repete metadados críticos para detecção de adulteração e contém opções com `semantic_key`,
texto, sentença, variantes, peso, família, facets, intensidade, segurança, tags e regras.

As classes são `general`, `fashion-mature`, `dark-atmospheric` e `experimental`. Perfis só carregam
classes expressamente permitidas.

## Autoria

`scripts/generate_catalog.py` é a fonte autoral revisável e gera JSON determinístico. Os eixos foram
redigidos para o projeto e podem ser auditados em diff. A coleção local de wildcards foi usada
somente para identificar ramos taxonômicos ausentes. Nenhuma linha externa foi importada.

O audit descartou nomes próprios, artistas, celebridades, marcas, personagens, conteúdo explícito,
horror gráfico, idade ambígua e frases longas multi-dimensionais.

## Validação

Use:

```console
python -m scripts.catalog_stats
python -m scripts.find_catalog_duplicates
python -m scripts.validate_catalog_semantics
python -m scripts.audit_wildcards
```

Os validadores cobrem colisões globais, fallbacks, dependências cíclicas, variantes, pesos, facets,
tags, regras, segurança, duplicatas, alcance por perfil e mínimo de 4.000 opções.
