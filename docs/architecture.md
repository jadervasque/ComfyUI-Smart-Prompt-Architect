# Arquitetura

Prompt Architect mantém cinco limites: domínio puro, serviço de aplicação, infraestrutura de dados,
adapter ComfyUI API V3 e frontend. O core não importa ComfyUI, HTTP ou JavaScript.

O pipeline é:

1. carregar e validar o perfil;
2. resolver as bibliotecas lógicas a partir dos packs permitidos pelo perfil;
3. materializar valores `fixed` e `custom`;
4. selecionar famílias e opções com seeds derivadas;
5. aplicar regras declarativas e fallbacks;
6. renderizar conforme verbosidade e densidade;
7. validar os prompts;
8. emitir o manifesto canônico.

Seleção acontece antes da renderização. A execução do nó não usa rede, subprocessos, instalação de
pacotes, código dinâmico ou caminhos fornecidos pelo workflow.

## Catálogo V2

`data/catalogs/index.json` é a fonte de verdade dos 81 packs. O índice relaciona cada pack a uma
biblioteca lógica, domínio, caminho relativo seguro, versão, classe de segurança, dependências e
prioridade. O repository só resolve caminhos POSIX relativos contidos na raiz autorizada.

Uma biblioteca lógica pode unir vários packs. Antes da mesclagem, o perfil filtra `enabled_packs` e
`allowed_safety_classes`. Metadados do pack precisam coincidir com o índice. Colisões de ID ou
`semantic_key`, dependência ausente, fallback desabilitado e pack vazio falham explicitamente.

O formato 1.0 de biblioteca continua legível para dados conectados antigos. Perfis V2, porém,
declaram `catalog_version` e usam exclusivamente a resolução segmentada, tornando a mudança pública
e versionada.

Veja [Catálogo V2](catalog-v2.md), [criação de packs](creating-packs.md) e
[compatibilidade](catalog-compatibility.md).
