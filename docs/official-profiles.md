# Perfis oficiais do Catálogo V2

Os 15 perfis usam schema `2.0`, catálogo `2.0.0` e conteúdo original do projeto. Todos os sujeitos
humanos são adultos. Cada perfil declara packs habilitados, classes de segurança, grupos de seed,
verbosidade, nível de negativo e modo recomendado.

| Perfil | Uso principal | Modo recomendado | Negativo |
|---|---|---|---|
| `portrait-core` | retrato geral equilibrado | `balanced` | `minimal` |
| `professional-headshot` | headshot limpo e previsível | `strict` | `strict` |
| `virtual-model` | identidade consistente com ampla variação | `balanced` | `standard` |
| `dataset-balanced` | cobertura estratificada para datasets | `dataset` | `strict` |
| `editorial-fashion` | moda editorial e campanha | `balanced` | `standard` |
| `lifestyle` | ambientes cotidianos e naturais | `balanced` | `standard` |
| `street-portrait` | retrato urbano contextual | `balanced` | `standard` |
| `studio-beauty` | beleza de estúdio e close controlado | `balanced` | `standard` |
| `cinematic-portrait` | linguagem cinematográfica | `balanced` | `standard` |
| `fine-art-portrait` | retrato autoral sem nomes de artistas | `balanced` | `standard` |
| `historical-portrait` | coerência visual histórica | `strict` | `strict` |
| `fantasy-portrait` | fantasia original não licenciada | `creative` | `standard` |
| `dark-fantasy-horror` | horror atmosférico não gráfico | `creative` | `strict` |
| `conceptual-portrait` | combinações experimentais controladas | `creative` | `standard` |
| `full-body-fashion` | look completo, pose e acessórios | `balanced` | `standard` |

`dataset-balanced` inclui todas as 69 dimensões para tornar todo item ativo alcançável. Os demais
perfis usam subconjuntos adequados à tarefa, evitando prompts excessivamente densos. Packs
`fashion-mature` só são habilitados nos perfis de moda correspondentes; `dark-atmospheric` só é
habilitado no perfil sombrio.

Execute `python -m tests.property_profiles` para a matriz oficial de 10.000 seeds por perfil. O
runner mede unicidade, cobertura, fallbacks, rejeições, tentativas, entropia e itens nunca
selecionados.
