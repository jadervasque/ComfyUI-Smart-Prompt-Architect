# PLAN0-STATUS — Prompt Architect

> Registro operacional obrigatório da execução de `PLAN0.md`.

## 1. Estado geral

| Campo | Valor |
|---|---|
| Projeto | Prompt Architect |
| Plano | `PLAN0.md` |
| Versão do plano | 1.0 |
| Status geral | `PARTIAL` |
| Etapa atual | ETAPA 14 + Expansão Catálogo V2 concluída localmente |
| Última atualização | 2026-07-23 01:13 -04:00 |
| Responsável atual | Agente IA no VS Code |
| Branch atual | `docs/user-manual` |
| Próximo marco | Revisar o diff e decidir commit/publicação da expansão |
| Bloqueadores | Nenhum; validação Linux/GitHub Actions da expansão ainda não foi executada |

## 2. Legenda

- `PENDING`: não iniciada.
- `IN_PROGRESS`: em execução.
- `BLOCKED`: impedida por dependência ou erro externo.
- `PARTIAL`: entrega parcial; critérios de aceite ainda não atingidos.
- `DONE`: concluída e validada.
- `SKIPPED`: omitida por decisão registrada.
- `FAILED`: tentativa falhou; exige correção.

## 3. Progresso das etapas

| Etapa | Nome | Status | Dependências | Início | Conclusão | Commit/PR | Observações |
|---:|---|---|---|---|---|---|---|
| 0 | Bootstrap e decisões | DONE | — | 2026-07-22 18:32 -04:00 | 2026-07-22 18:38 -04:00 | `02a3977` | Aceite validado; registro final em commit separado |
| 1 | Contratos e modelos | DONE | 0 | 2026-07-22 18:41 -04:00 | 2026-07-22 18:47 -04:00 | `288bc66` | Aceite validado com 12 testes |
| 2 | Loader e cache | DONE | 1 | 2026-07-22 18:48 -04:00 | 2026-07-22 18:51 -04:00 | `778cc94` | Aceite validado com 22 testes acumulados |
| 3 | Seeds e seleção | DONE | 1 | 2026-07-22 18:52 -04:00 | 2026-07-22 18:54 -04:00 | `72d277e` | Golden tests e independência de grupos aprovados |
| 4 | Motor de regras | DONE | 1, 3 | 2026-07-22 18:55 -04:00 | 2026-07-22 18:57 -04:00 | `783be55` | Operadores, conflitos e ciclos validados |
| 5 | Compositor e fallbacks | DONE | 2, 3, 4 | 2026-07-22 18:58 -04:00 | 2026-07-22 19:01 -04:00 | `e0b2cb3` | Seções obrigatórias e fallbacks validados |
| 6 | Renderer e normalização | DONE | 1, 5 | 2026-07-22 19:02 -04:00 | 2026-07-22 19:04 -04:00 | `5ae12ce` | Snapshots e template seguro aprovados |
| 7 | Validação e manifesto | DONE | 5, 6 | 2026-07-22 19:05 -04:00 | 2026-07-22 19:09 -04:00 | `96f28d8` | Pipeline pública e manifesto aprovados |
| 8 | Perfis e bibliotecas | DONE | 2–7 | 2026-07-22 19:09:54 -04:00 | 2026-07-22 19:19 -04:00 | `0bc0575` | 30.000 seeds e determinismo aprovados |
| 9 | Nó ComfyUI V3 | DONE | 7, 8 | 2026-07-22 19:20 -04:00 | 2026-07-22 19:30 -04:00 | `e35b73f` | Nó validado dentro do ComfyUI 0.27.0 local |
| 10 | Frontend mínimo | DONE | 9 | 2026-07-22 19:31 -04:00 | 2026-07-22 19:38 -04:00 | `5a2d503` | Estado serializado e assets servidos no ComfyUI local |
| 11 | Preview e validação API | DONE | 7, 9, 10 | 2026-07-22 19:38 -04:00 | 2026-07-22 19:43 -04:00 | `dac65e1` | Rotas e limites validados no ComfyUI local |
| 12 | Interface avançada | DONE | 10, 11 | 2026-07-22 19:43 -04:00 | 2026-07-22 19:50 -04:00 | `3c98b5e` | Editor completo e estado avançado testado |
| 13 | Qualidade e CI | DONE | 0–12 | 2026-07-22 19:50 -04:00 | 2026-07-22 21:08 -04:00 | `c7a3f87`, `01c8119` | CI run `29970873136` verde nos 7 jobs Linux/Windows |
| 14 | Documentação e exemplos | IN_PROGRESS | 8–13 | 2026-07-22 21:45 -04:00 | — | — | `MANUAL.md` completo e validado; demais entregas da etapa pendentes |
| V2.1 | Expansão do Catálogo V2 | DONE | 0–13 | 2026-07-22 23:10 -04:00 | 2026-07-23 01:13 -04:00 | `5999366` (baseline) | 81 packs, 69 dimensões, 5.184 opções, 15.552 variantes e 15 perfis; gates locais aprovados |
| 15 | Beta público 0.9.0 | PENDING | 0–14 | — | — | — | Requer autorização para publicar |
| 16 | Release 1.0.0 | PENDING | 15 | — | — | — | Requer autorização para publicar |

## 4. Checklist da etapa atual

### ETAPA 0 — Bootstrap e decisões

- [x] Repositório criado.
- [x] Git inicializado.
- [x] Branch de trabalho criada.
- [x] Estrutura mínima criada.
- [x] `PLAN0.md` preservado.
- [x] `PLAN0-STATUS.md` preservado.
- [x] `AGENTS.md` preservado.
- [x] `pyproject.toml` criado.
- [x] Licença criada.
- [x] README inicial criado.
- [x] Documentos comunitários criados.
- [x] Pacote importa.
- [x] `compileall` aprovado.
- [x] Versões do ambiente registradas.
- [x] Commit realizado.

### ETAPA 1 — Contratos, schemas e modelos

- [x] Enums, dataclasses e exceções criados.
- [x] Schemas JSON criados.
- [x] Fixtures válidas e inválidas criadas.
- [x] Parser tipado implementado.
- [x] Campos essenciais ausentes rejeitados.
- [x] Política de campos desconhecidos definida.
- [x] Perfil mínimo válido testado.
- [x] Biblioteca válida testada.
- [x] ID duplicado testado.
- [x] Peso negativo testado.
- [x] Fallback inexistente testado.
- [x] Schema desconhecido testado.
- [x] Lint, tipagem e testes aprovados.
- [x] Documentação atualizada.
- [x] Commit realizado.

### ETAPA 2 — Loader, paths e cache

- [x] Raízes permitidas implementadas.
- [x] IDs normalizados e traversal rejeitado.
- [x] Loader JSON com limite de tamanho implementado.
- [x] Repository tipado implementado.
- [x] Cache por metadados e hash implementado.
- [x] Listagem determinística de perfis implementada.
- [x] Reload após mudança testado.
- [x] Lint, tipagem e testes aprovados.
- [x] Documentação atualizada.
- [x] Commit realizado.

### ETAPA 3 — Seeds e seleção ponderada

- [x] `derive_seed` implementado.
- [x] Seeds por grupo e locks implementados.
- [x] `weighted_choice` implementado.
- [x] Ordem determinística garantida.
- [x] Modos básicos de campo implementados.
- [x] Golden tests criados.
- [x] Independência de grupos testada.
- [x] Lint, tipagem e testes aprovados.
- [x] Documentação atualizada.
- [x] Commit realizado.

### ETAPA 4 — Motor de regras

- [x] Operadores seguros implementados.
- [x] `requires`, `excludes`, `prefer` e `implies` implementados.
- [x] Prioridades e conflitos fixos implementados.
- [x] Ciclos detectados e limitados.
- [x] Eventos registráveis no manifesto produzidos.
- [x] Exemplos e testes reais criados.
- [x] Lint, tipagem e testes aprovados.
- [x] Documentação atualizada.
- [x] Commit realizado.

### ETAPA 5 — Compositor e fallbacks

- [x] Ordem de seções e contexto incremental implementados.
- [x] Limite de tentativas implementado.
- [x] Relaxamento por modo implementado.
- [x] Fallback local/global implementado.
- [x] Tentativas, conflitos e fallbacks registrados.
- [x] Retorno estruturado implementado.
- [x] Seções obrigatórias resolvem ou falham explicitamente.
- [x] Lint, tipagem e testes aprovados.
- [x] Documentação atualizada.
- [x] Commit realizado.

### ETAPA 6 — Renderer e normalização

- [x] Template seguro implementado.
- [x] Frases, variantes e placeholders opcionais implementados.
- [x] Espaços, pontuação e capitalização normalizados.
- [x] Artigos básicos `a`/`an` implementados.
- [x] Deduplicação exata e semântica implementada.
- [x] Snapshots criados.
- [x] Lint, tipagem e testes aprovados.
- [x] Documentação atualizada.
- [x] Commit realizado.

### ETAPA 7 — Validação final e manifesto

- [x] Issues estruturadas e severidades implementadas.
- [x] Contexto e resultado final validados.
- [x] Manifesto e hash canônicos implementados.
- [x] Summary implementado.
- [x] Prompt negativo implementado.
- [x] Prefixos e sufixos preservados.
- [x] Prompt positivo vazio impossível silenciosamente.
- [x] Snapshots e integração criados.
- [x] Lint, tipagem e testes aprovados.
- [x] Documentação atualizada.
- [x] Commit realizado.

### ETAPA 8 — Perfis e bibliotecas oficiais

- [x] Perfis `portrait`, `virtual-model` e `dataset` criados.
- [x] Vinte bibliotecas mínimas criadas.
- [x] Regras de cabelo, roupa e cenário incluídas.
- [x] Pesos e fallbacks revisados.
- [x] Conteúdo e licença revisados.
- [x] 10.000 seeds por perfil aprovadas.
- [x] Lint, tipagem e testes aprovados.
- [x] Documentação atualizada.
- [x] Commit realizado.

### ETAPA 9 — Nó ComfyUI API V3

- [x] Extensão V3 versionada implementada.
- [x] Schema, inputs, outputs e tooltips implementados.
- [x] Conversão clara de erros implementada.
- [x] Frontend exportado via `WEB_DIRECTORY`.
- [x] Fingerprint/cache estável implementado.
- [x] Adapter testado sem GPU dentro do ComfyUI local.
- [x] Help page criada.
- [x] Lint, tipagem e testes aprovados.
- [x] Commit realizado.

### ETAPA 10 — Frontend mínimo

- [x] Extensão JavaScript registrada.
- [x] Botão `Open Architect` implementado.
- [x] Modal e formulário básico implementados.
- [x] Persistência em `configuration_json` implementada.
- [x] Dirty state do workflow implementado.
- [x] Erros e preview implementados.
- [x] CSS compatível com tema implementado.
- [x] Persistência ao salvar e reabrir workflow validada.
- [x] Lint, testes e documentação aprovados.
- [x] Commit realizado.

### ETAPA 11 — Rotas de preview e validação

- [x] Rotas GET seguras implementadas.
- [x] Rotas POST de preview e validação implementadas.
- [x] Limite de payload implementado.
- [x] Respostas e erros HTTP padronizados.
- [x] ID inválido, payload excessivo e concorrência testados.
- [x] Nenhuma escrita persistente realizada.
- [x] Lint, tipagem, testes e documentação aprovados.
- [x] Commit realizado.

### ETAPA 12 — Interface avançada

- [x] Abas implementadas.
- [x] Modos, valores e tags por campo implementados.
- [x] Locks e seeds por grupo implementados.
- [x] Preview do manifesto implementado.
- [x] Advanced JSON sincronizado.
- [x] Reset, import e export implementados.
- [x] Acessibilidade, loading e erros implementados.
- [x] Configuração completa sem JSON manual validada.
- [x] Lint, testes e documentação aprovados.
- [x] Commit realizado.

### ETAPA 13 — Qualidade, CI e integração

- [x] Ruff, mypy, pytest e coverage configurados.
- [x] CI Linux/Windows implementada.
- [x] Property e smoke tests integrados.
- [x] Validação de dados integrada.
- [x] Pre-commit opcional configurado.
- [x] Performance medida.
- [x] Matriz suportada documentada.
- [x] Cobertura alvo e 10.000 seeds aprovadas.
- [x] Workflow remoto verde em Linux e Windows.
- [x] Commit realizado.

### ETAPA 14 — Documentação e exemplos

- [x] `MANUAL.md` completo para o nó e editor visual.
- [ ] README completo.
- [ ] Screenshots.
- [ ] Workflows básico e modelo virtual.
- [ ] Exemplo de perfil.
- [ ] Regras e troubleshooting revisados.
- [ ] Desenvolvimento, contribuição e segurança revisados.
- [ ] Inglês e links revisados.
- [ ] Instalação e primeiro prompt validados somente pelo README.
- [ ] Commit realizado.

## 5. Registro de trabalho

Adicionar uma entrada por sessão relevante. Não apagar entradas antigas.

### Modelo

```markdown
## YYYY-MM-DD HH:MM — ETAPA N

- Status anterior:
- Status novo:
- Branch:
- Objetivo:
- Arquivos alterados:
- Implementação:
- Testes executados:
- Resultado dos testes:
- Pendências:
- Bloqueadores:
- Decisões:
- Commit/PR:
- Próxima ação:
```

### 2026-07-22 22:25 -04:00 — EXTENSÃO DO MODO DE CAMPO CUSTOM

- Status anterior: ETAPA 14 `IN_PROGRESS`.
- Status novo: ETAPA 14 `IN_PROGRESS`; extensão funcional solicitada em execução.
- Branch: `docs/user-manual`.
- Objetivo: adicionar o modo `custom` aos campos do editor, com texto livre específico por seção e composição independente das opções da biblioteca.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: contrato versionado, core, frontend dinâmico, testes, documentação e validação completa.
- Bloqueadores: nenhum.
- Decisões: preservar `fixed` como ID de opção e representar texto livre por um modo distinto, sem acesso a rede, arquivos ou execução de código.
- Commit/PR: pendente.
- Próxima ação: implementar o contrato compatível e a seleção sintética segura para texto customizado.

### 2026-07-22 22:37 -04:00 — CONCLUSÃO DO MODO DE CAMPO CUSTOM

- Status anterior: extensão funcional em execução; ETAPA 14 `IN_PROGRESS`.
- Status novo: extensão funcional concluída; ETAPA 14 permanece `IN_PROGRESS` por suas entregas documentais originais.
- Branch: `docs/user-manual`.
- Objetivo: concluir o modo `custom` por campo com editor dinâmico, persistência, composição, manifesto e compatibilidade versionada.
- Arquivos alterados: enums, modelos, parser, selector, engine, regras, adapter ComfyUI, frontend JS/CSS, schemas 1.0/1.1, versão do pacote, testes, `MANUAL.md`, documentação técnica, changelog e este registro.
- Implementação: `custom` adicionado ao combobox; `Custom text` aparece somente nesse modo; texto livre não vazio de até 4.096 caracteres é armazenado no workflow, resolvido antes dos campos aleatórios, protegido contra implicações e registrado como `source: custom`; schema de configuração evoluído para `1.1`, mantendo leitura de `1.0`; versão evoluída para `0.2.0.dev0`.
- Testes executados: Ruff format/check; mypy; pytest completo com cobertura; gate de cobertura do core; Node test/check; validação dos dados; 10.000 seeds por perfil; benchmark; build; composição direta com perfil oficial; verificação HTTP dos assets servidos pelo ComfyUI local.
- Resultado dos testes: PASS — 94 testes Python; cobertura geral 91,90%; cobertura core/application 92,91%; 7 testes frontend; 30.000 seeds; 3.000 composições de benchmark em 4,608 s; wheel e sdist `0.2.0.dev0` construídos; assets HTTP 200 contendo `custom`; prompt e manifesto oficiais confirmados. A tentativa de automação visual pelo navegador integrado não obteve conexão nesta sessão.
- Pendências: reiniciar o ComfyUI e recarregar a página para substituir o backend Python já carregado em memória e então conferir visualmente o modal; continuar screenshots e workflows da ETAPA 14.
- Bloqueadores: nenhum no código; validação visual depende apenas do reinício/reload da instância local.
- Decisões: usar `value` como texto no modo `custom`, distinguido semanticamente pelo modo; limitar texto a 4.096 caracteres; preservar schema legado em `configuration-1.0.schema.json`; não reiniciar automaticamente a instância ativa do usuário.
- Commit/PR: pendente.
- Próxima ação: reiniciar o ComfyUI, validar visualmente `Fields > Mode > custom` e retomar as entregas documentais da ETAPA 14.

### 2026-07-22 22:41 -04:00 — CORREÇÃO DE SINCRONIZAÇÃO IDENTITY LOCK

- Status anterior: ETAPA 14 `IN_PROGRESS`; `identity_lock` do nó e `Groups > identity > Lock group` podiam divergir ao abrir o editor.
- Status novo: correção de regressão em execução; ETAPA 14 permanece `IN_PROGRESS`.
- Branch: `docs/user-manual`.
- Objetivo: tornar o valor visível de `identity_lock` a fonte inicial do editor e manter os controles Basic/Groups vinculados em ambos os sentidos.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: helper de sincronização do estado do nó, teste frontend, documentação e validação.
- Bloqueadores: nenhum.
- Decisões: preservar os demais campos avançados de `configuration_json`; aplicar a precedência pública já usada pelo backend também ao abrir o modal.
- Commit/PR: pendente.
- Próxima ação: sincronizar o estado serializado com os widgets visíveis antes de renderizar o editor.

### 2026-07-22 22:43 -04:00 — CONCLUSÃO DA SINCRONIZAÇÃO IDENTITY LOCK

- Status anterior: correção de regressão em execução; ETAPA 14 `IN_PROGRESS`.
- Status novo: correção concluída; ETAPA 14 permanece `IN_PROGRESS`.
- Branch: `docs/user-manual`.
- Objetivo: eliminar a divergência entre o widget `identity_lock` e os controles de identidade do editor.
- Arquivos alterados: `prompt_architect/web/prompt_architect_state.js`, `prompt_architect/web/prompt_architect.js`, `tests/frontend/state.test.mjs`, `MANUAL.md`, `CHANGELOG.md` e este registro.
- Implementação: novo helper valida e aplica o valor booleano visível de `identity_lock` sobre o estado serializado antes da renderização; Basic e Groups passam a iniciar com esse valor, mantêm o vínculo já existente durante a edição e gravam o mesmo estado no widget e no JSON ao salvar.
- Testes executados: Node test; Node syntax check; Ruff format/check; mypy; pytest completo; verificação HTTP do asset servido pelo ComfyUI local.
- Resultado dos testes: PASS — 8 testes frontend, incluindo regressão `configuration_json=true`/widget visível `false`; 94 testes Python; zero erros de lint/tipagem; asset atualizado servido com HTTP 200. A automação visual pelo navegador integrado continuou indisponível por falha de conexão da ferramenta.
- Pendências: recarregar completamente a página do ComfyUI para substituir o módulo JavaScript já importado pelo navegador; continuar ETAPA 14.
- Bloqueadores: nenhum no código.
- Decisões: o widget público visível mantém a mesma precedência que já possui no backend; nenhum estado avançado ou seed do grupo é descartado ao sincronizar apenas `locked`.
- Commit/PR: pendente.
- Próxima ação: hard reload no ComfyUI e conferir o fluxo desmarcar `identity_lock` → abrir editor → Groups → salvar.

### 2026-07-22 18:32 -04:00 — ETAPA 0

- Status anterior: `PENDING` / projeto `NOT_STARTED`.
- Status novo: `IN_PROGRESS`.
- Branch: `chore/bootstrap`.
- Objetivo: criar a estrutura profissional mínima, metadados, documentação comunitária e pacote Python importável da versão de desenvolvimento.
- Arquivos alterados: pacote `prompt_architect`, `tests`, `docs`, `examples`, documentos comunitários, `pyproject.toml`, `requirements.txt`, `.gitignore` e este registro.
- Implementação: estrutura de camadas criada; pacote independente importável; metadados PEP 440; licença Apache-2.0; documentação inicial; configuração de Ruff, mypy, unittest/pytest, coverage e build; nenhuma dependência de runtime.
- Testes executados: compilação, importação, parse TOML, Ruff, mypy, unittest e build de wheel.
- Resultado dos testes: validação final aprovada; falhas intermediárias e respectivas correções registradas na seção 6.
- Pendências: realizar o commit da etapa e registrar sua referência antes de marcar `DONE`.
- Bloqueadores: nenhum.
- Decisões: preservar Git existente; usar `0.1.0.dev0`; adiar scaffold específico do ComfyUI para a ETAPA 9.
- Commit/PR: preparado com mensagem `chore: bootstrap Prompt Architect project`.
- Próxima ação: revisar e realizar o commit da ETAPA 0.

### 2026-07-22 18:38 -04:00 — CONCLUSÃO DA ETAPA 0

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `chore/bootstrap`.
- Objetivo: confirmar o aceite e registrar o commit real da etapa.
- Arquivos alterados: `plans/PLAN0-STATUS.md`.
- Implementação: checklist integral da ETAPA 0 conferido; ETAPA 1 selecionada como próxima elegível.
- Testes executados: usados os resultados finais registrados na seção 6; nenhum teste adicional após o commit de código.
- Resultado dos testes: todos os checks disponíveis e o build alternativo aprovados.
- Pendências: `pytest`, `pytest-cov` e `build` continuam declarados como dependências opcionais e não estavam instalados no interpretador global; cobertura ainda não medida.
- Bloqueadores: nenhum para o aceite da ETAPA 0.
- Decisões: etapa marcada `DONE` porque os testes explícitos, lint, tipagem, teste unitário e wheel foram validados sem dependência de runtime.
- Commit/PR: `02a3977` (`chore: bootstrap Prompt Architect project`).
- Próxima ação: executar a ETAPA 1 — Contratos, schemas e modelos.

### 2026-07-22 18:41 -04:00 — ETAPA 1

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/contracts`.
- Objetivo: definir modelos imutáveis, enums, exceções, schemas JSON e parser tipado estrito antes dos algoritmos.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: contratos, schemas, fixtures, parser, testes, documentação e commit.
- Bloqueadores: nenhum.
- Decisões: política inicial de campos desconhecidos será rejeição estrita para evitar mudanças silenciosas de semântica.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 1.

### 2026-07-22 18:47 -04:00 — CONCLUSÃO DA ETAPA 1

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/contracts`.
- Objetivo: concluir e validar contratos versionados antes dos algoritmos.
- Arquivos alterados: modelos, enums, exceções, parser, quatro schemas JSON, fixtures, testes e `docs/configuration.md`.
- Implementação: parser estrito stdlib, objetos tipados imutáveis, pesos finitos, IDs/versionamento, referências locais de fallback e política de campos desconhecidos.
- Testes executados: compileall, parse de todos os JSON, Ruff check/format, mypy, unittest e wheel sem isolamento.
- Resultado dos testes: PASS; 12 testes, zero erros de lint e tipagem.
- Pendências: referências entre perfil e bibliotecas serão validadas pelo repository na ETAPA 2.
- Bloqueadores: nenhum.
- Decisões: schemas documentam interoperabilidade; parser stdlib é a validação executável para não adicionar dependência de runtime.
- Commit/PR: `288bc66` (`feat: define prompt data contracts`).
- Próxima ação: executar a ETAPA 2 — Loader, paths e cache.

### 2026-07-22 18:48 -04:00 — ETAPA 2

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/repository`.
- Objetivo: carregar dados JSON somente de raízes autorizadas, com precedência, limite, cache e invalidação determinística.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: paths, loader, cache, repository, testes, documentação e commit.
- Bloqueadores: nenhum.
- Decisões: IDs serão convertidos apenas em nomes de arquivo validados, nunca em caminhos fornecidos pelo usuário.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 2.

### 2026-07-22 18:51 -04:00 — CONCLUSÃO DA ETAPA 2

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/repository`.
- Objetivo: concluir carregamento seguro, precedência, referências e cache invalidável.
- Arquivos alterados: infrastructure paths, loader, hashing, cache, repository, testes e documentação.
- Implementação: raízes autorizadas, IDs allowlist, JSON limitado a 1 MiB, precedência override/usuário/interno, hash SHA-256 e mensagens sem caminho absoluto.
- Testes executados: Ruff, mypy, 22 unittests acumulados, compileall, format, wheel e scan de APIs proibidas.
- Resultado dos testes: PASS; zero erros e nenhum uso proibido no Python.
- Pendências: nenhuma da ETAPA 2.
- Bloqueadores: nenhum.
- Decisões: conteúdo sempre é hasheado para detectar alteração mesmo quando metadados do arquivo são preservados.
- Commit/PR: `778cc94` (`feat: add secure prompt data repository`).
- Próxima ação: executar a ETAPA 3 — Seeds e seleção ponderada.

### 2026-07-22 18:52 -04:00 — ETAPA 3

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/deterministic-selection`.
- Objetivo: implementar subseeds SHA-256, locks, ordem estável e escolha ponderada reproduzível sem RNG global.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: seeds, selector, modos básicos, golden tests, documentação e commit.
- Bloqueadores: nenhum.
- Decisões: cada seção derivará uma seed própria a partir da seed do grupo para evitar correlação por ordem de execução.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 3.

### 2026-07-22 18:54 -04:00 — CONCLUSÃO DA ETAPA 3

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/deterministic-selection`.
- Objetivo: concluir seeds isoladas e seleção ponderada reproduzível.
- Arquivos alterados: `seeds.py`, `selector.py`, testes, documentação e configuração Ruff.
- Implementação: SHA-256 de 64 bits, RNG por seção, locks, modos básicos, filtros de tags, ordenação estável e pesos validados.
- Testes executados: Ruff, mypy, 33 unittests acumulados, compileall e wheel.
- Resultado dos testes: PASS; zero erros.
- Pendências: nenhuma da ETAPA 3.
- Bloqueadores: nenhum.
- Decisões: `random.Random` é deliberadamente não criptográfico e usado somente para conteúdo determinístico; S311 foi documentado/limitado.
- Commit/PR: `72d277e` (`feat: implement deterministic weighted selection`).
- Próxima ação: executar a ETAPA 4 — Motor de regras.

### 2026-07-22 18:55 -04:00 — ETAPA 4

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/rules-engine`.
- Objetivo: avaliar regras declarativas, aplicar preferências/implicações e falhar claramente em conflitos fixos ou ciclos.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: rules engine, testes, exemplos, documentação e commit.
- Bloqueadores: nenhum.
- Decisões: operadores consultarão somente seleção resolvida, tags, metadado seguro e modo de geração.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 4.

### 2026-07-22 18:57 -04:00 — CONCLUSÃO DA ETAPA 4

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/rules-engine`.
- Objetivo: concluir regras declarativas seguras e determinísticas.
- Arquivos alterados: `rules.py`, testes e `docs/rules.md`.
- Implementação: sete operadores, quatro tipos de regra, prioridades de fixed, eventos, substituições e ciclos limitados.
- Testes executados: Ruff, mypy, 40 unittests acumulados, compileall, format e wheel.
- Resultado dos testes: PASS; zero erros.
- Pendências: integração incremental das regras ao compositor na ETAPA 5.
- Bloqueadores: nenhum.
- Decisões: creative reduz influência de preferências por raiz quadrada sem relaxar regras absolutas.
- Commit/PR: `783be55` (`feat: add compatibility rules engine`).
- Próxima ação: executar a ETAPA 5 — Compositor e fallbacks.

### 2026-07-22 18:58 -04:00 — ETAPA 5

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/compositor`.
- Objetivo: selecionar seções incrementalmente, aplicar regras/fallbacks e produzir contexto estruturado completo.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: engine de seleção, fallbacks, tentativas, testes, documentação e commit.
- Bloqueadores: nenhum.
- Decisões: fallbacks serão validados pelas mesmas regras absolutas; nenhum fallback poderá encobrir conflito fixed.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 5.

### 2026-07-22 19:01 -04:00 — CONCLUSÃO DA ETAPA 5

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/compositor`.
- Objetivo: concluir seleção incremental, retries e fallbacks.
- Arquivos alterados: `engine.py`, testes e arquitetura.
- Implementação: preflight fixed, contexto incremental, tentativas sem reposição, relaxamento controlado e cascata de fallback validada.
- Testes executados: Ruff, mypy, 48 unittests acumulados, compileall, format e wheel.
- Resultado dos testes: PASS; zero erros.
- Pendências: renderização textual começa na ETAPA 6.
- Bloqueadores: nenhum.
- Decisões: implicações incompatíveis de candidatos random são rejeitadas; conflitos entre valores fixed falham imediatamente.
- Commit/PR: `e0b2cb3` (`feat: compose structured prompt contexts`).
- Próxima ação: executar a ETAPA 6 — Renderer e normalização.

### 2026-07-22 19:02 -04:00 — ETAPA 6

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/renderer`.
- Objetivo: renderizar templates permitidos e normalizar texto sem placeholders ou pontuação quebrada.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: renderer, normalizer, snapshots, documentação e commit.
- Bloqueadores: nenhum.
- Decisões: deduplicação ocorrerá por texto normalizado e `semantic_key`, preservando a primeira seção na ordem do perfil.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 6.

### 2026-07-22 19:04 -04:00 — CONCLUSÃO DA ETAPA 6

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/renderer`.
- Objetivo: concluir renderização segura e normalização conservadora.
- Arquivos alterados: renderer, normalizer, testes e documentação.
- Implementação: substituição segura, variantes ponderadas, deduplicação exata/semântica e gramática básica.
- Testes executados: Ruff, mypy, 57 unittests acumulados, compileall, format e wheel.
- Resultado dos testes: PASS; zero erros.
- Pendências: validação final, overrides e manifesto na ETAPA 7.
- Bloqueadores: nenhum.
- Decisões: underscores são permitidos em placeholders oficiais, sem permitir acesso a atributos ou índices.
- Commit/PR: `5ae12ce` (`feat: render and normalize natural prompts`).
- Próxima ação: executar a ETAPA 7 — Validação final e manifesto.

### 2026-07-22 19:05 -04:00 — ETAPA 7

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/manifest`.
- Objetivo: validar contexto/texto, preservar overrides e gerar manifesto/summary canônicos.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: validator, manifest, compose service, testes, documentação e commit.
- Bloqueadores: nenhum.
- Decisões: configuration hash usará JSON canônico da configuração efetiva, nunca `repr` ou ordem de dict.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 7.

### 2026-07-22 19:09 -04:00 — CONCLUSÃO DA ETAPA 7

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/manifest`.
- Objetivo: concluir validação final, overrides, manifesto e diagnóstico.
- Arquivos alterados: validator, manifest, compose service, schema, modelos, testes e documentação.
- Implementação: pipeline pública, issues, prompt negativo, overrides, JSON canônico e hash da configuração efetiva.
- Testes executados: Ruff, mypy, 65 unittests acumulados, compileall, schemas JSON, format e wheel.
- Resultado dos testes: PASS; zero erros.
- Pendências: nenhuma da ETAPA 7.
- Bloqueadores: nenhum.
- Decisões: manifesto inclui versões de bibliotecas e configuração efetiva além do exemplo mínimo do plano, conforme RF-007.
- Commit/PR: `96f28d8` (`feat: validate outputs and build prompt manifest`).
- Próxima ação: executar a ETAPA 8 — Perfis e bibliotecas oficiais.

### 2026-07-22 19:09:54 -04:00 — ETAPA 8

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/official-profiles`.
- Objetivo: entregar três perfis e bibliotecas oficiais seguras com 10.000 seeds validadas por perfil.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: dados, regras, property runner, documentação e commit.
- Bloqueadores: nenhum.
- Decisões: IDs de campos do plano serão normalizados para kebab-case no JSON oficial.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 8.

### 2026-07-22 19:19 -04:00 — CONCLUSÃO DA ETAPA 8

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/official-profiles`.
- Objetivo: concluir conteúdo oficial e validar 10.000 seeds por perfil.
- Arquivos alterados: 20 bibliotecas, 3 perfis, testes, runner de propriedade e documentação.
- Implementação: conteúdo original Apache-2.0 para adultos, fallbacks, pesos e regras de cabelo/roupa/cenário.
- Testes executados: Ruff, mypy, 69 unittests, compileall, parse JSON, wheel e `python -m tests.property_profiles`.
- Resultado dos testes: PASS; 10.000 seeds em cada perfil, compostas duas vezes para determinismo (60.000 composições).
- Pendências: nenhuma da ETAPA 8.
- Bloqueadores: nenhum.
- Decisões: runner de propriedade pré-carrega dados imutáveis para medir o core, mantendo teste separado do repository real.
- Commit/PR: `0bc0575` (`feat: add official prompt profiles and libraries`).
- Próxima ação: executar a ETAPA 9 — Nó ComfyUI API V3.

### 2026-07-22 19:20 -04:00 — ETAPA 9

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/comfy-v3-node`.
- Objetivo: expor a pipeline como nó ComfyUI V3 versionado, sem GPU e com cinco outputs.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada após consulta à documentação oficial e ao código local do ComfyUI 0.27.0.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: extension, schema, parsing do nó, fingerprint, smoke test, help e commit.
- Bloqueadores: nenhum.
- Decisões: importar `comfy_api.v0_0_2` explicitamente, evitando `latest` mutável.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 9.

### 2026-07-22 19:30 -04:00 — CONCLUSÃO DA ETAPA 9

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/comfy-v3-node`.
- Objetivo: concluir o adapter público V3 e validá-lo no ComfyUI local sem GPU.
- Arquivos alterados: adapter ComfyUI, extensão V3, schema do nó, help page, export do frontend e testes.
- Implementação: nó `PromptArchitect_PromptArchitect` com 13 inputs, cinco outputs, erros de domínio traduzidos e fingerprint canônico.
- Testes executados: Ruff, mypy, 75 unittests, compileall, wheel e smoke test com `comfy_api.v0_0_2` do ComfyUI 0.27.0 local.
- Resultado dos testes: PASS; nó registrado, schema 13/5 confirmado e execução real retornou cinco outputs válidos.
- Pendências: nenhuma da ETAPA 9.
- Bloqueadores: nenhum.
- Decisões: manter import versionado `comfy_api.v0_0_2` e carregar o adapter apenas no entrypoint do ComfyUI para preservar o core independente.
- Commit/PR: `e35b73f` (`feat: expose Prompt Architect ComfyUI node`).
- Próxima ação: executar a ETAPA 10 — Frontend mínimo.

### 2026-07-22 19:31 -04:00 — ETAPA 10

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/frontend-editor`.
- Objetivo: criar editor centralizado com estado serializado no próprio nó.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada após revisão da API JavaScript oficial e do frontend local.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: extensão, modal, formulário, persistência, dirty state, preview, CSS e teste no navegador.
- Bloqueadores: nenhum.
- Decisões: `configuration_json` será a única fonte persistente de verdade do editor.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 10.

### 2026-07-22 19:38 -04:00 — CONCLUSÃO DA ETAPA 10

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/frontend-editor`.
- Objetivo: concluir o editor centralizado persistente no workflow.
- Arquivos alterados: extensão JavaScript, módulo puro de estado, CSS, documentação frontend e testes Node.
- Implementação: modal acessível, formulário básico, preview local de estado, sincronização de widgets, JSON canônico e dirty state.
- Testes executados: `node --test`, `node --check`, Ruff, mypy, 75 unittests e verificação HTTP no ComfyUI 0.27.0.
- Resultado dos testes: PASS; três testes frontend, assets e definição do nó servidos em uma inicialização completa do ComfyUI.
- Pendências: preview autoritativo do servidor pertence à ETAPA 11; screenshot final pertence à ETAPA 14.
- Bloqueadores: automação visual in-app indisponível por falha de metadados no runtime da ferramenta; round-trip persistente coberto por teste automatizado de estado.
- Decisões: usar JavaScript sem dependências e CSS carregado programaticamente conforme API oficial.
- Commit/PR: `5a2d503` (`feat: add centralized prompt editor UI`); correção de bootstrap `b8eae98`.
- Próxima ação: executar a ETAPA 11 — Rotas de preview e validação.

### 2026-07-22 19:38 -04:00 — ETAPA 11

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/preview-api`.
- Objetivo: fornecer preview e validação imediatos, locais e sem enfileirar workflow.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada após consulta à documentação oficial de rotas do ComfyUI.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: GETs, POSTs, limites, erros, concorrência, documentação e commit.
- Bloqueadores: nenhum.
- Decisões: manter operações no application service puro e limitar o adapter aiohttp ao transporte.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 11.

### 2026-07-22 19:43 -04:00 — CONCLUSÃO DA ETAPA 11

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/preview-api`.
- Objetivo: concluir feedback imediato sem fila e sem persistência no servidor.
- Arquivos alterados: service puro de API, adapter aiohttp, bootstrap, testes, tipagem e documentação.
- Implementação: dois GETs seguros, POST preview/validate, payload de 256 KiB, respostas versionadas e erros padronizados.
- Testes executados: Ruff, format, mypy, 80 unittests, compileall, wheel, scan de APIs proibidas e requests HTTP reais.
- Resultado dos testes: PASS; preview/validate 200, ID inválido 400, excesso 413 e 32 previews concorrentes idênticos.
- Pendências: nenhuma da ETAPA 11.
- Bloqueadores: nenhum.
- Decisões: validar por composição autoritativa para que o preview não divirja da execução do nó.
- Commit/PR: `dac65e1` (`feat: add prompt preview and validation API`).
- Próxima ação: executar a ETAPA 12 — Interface avançada.

### 2026-07-22 19:43 -04:00 — ETAPA 12

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `feat/advanced-editor`.
- Objetivo: permitir configuração completa por controles visuais sincronizados.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada sobre o editor mínimo e as rotas versionadas.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: abas, campos, grupos, manifesto, JSON, import/export, acessibilidade e testes.
- Bloqueadores: nenhum.
- Decisões: obter opções somente da rota local read-only e manter JSON do widget como fonte de verdade.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 12.

### 2026-07-22 19:50 -04:00 — CONCLUSÃO DA ETAPA 12

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `feat/advanced-editor`.
- Objetivo: concluir configuração visual completa sem edição manual de JSON.
- Arquivos alterados: editor, estado frontend, CSS, API de preview, testes JS/Python e documentação frontend.
- Implementação: abas Basic/Fields/Groups/Preview, tags, locks/seeds, manifesto, JSON, reset, import/export, foco, loading e erros.
- Testes executados: `node --check`, cinco testes Node, Ruff, mypy, 81 unittests e requests reais no ComfyUI 0.27.0.
- Resultado dos testes: PASS; assets 200, profile 200 e preview de campo fixo 200 com seleção preservada.
- Pendências: screenshot documental na ETAPA 14.
- Bloqueadores: automação visual in-app permaneceu indisponível por falha do runtime da ferramenta; integração de estado, assets e API foi validada automaticamente.
- Decisões: exigir confirmação antes de trocar perfil ou resetar quando isso puder descartar overrides; limitar import a 256 KiB.
- Commit/PR: `3c98b5e` (`feat: complete Prompt Architect visual editor`); paridade de preview corrigida em `e21991c`.
- Próxima ação: executar a ETAPA 13 — Qualidade, CI e integração.

### 2026-07-22 19:50 -04:00 — ETAPA 13

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `ci/quality-matrix`.
- Objetivo: criar gates reproduzíveis de qualidade, cobertura, dados, frontend e plataformas.
- Arquivos alterados: inicialmente apenas `plans/PLAN0-STATUS.md`.
- Implementação: iniciada sobre a suíte acumulada e property runner existentes.
- Testes executados: pendentes.
- Resultado dos testes: pendente.
- Pendências: workflow CI, coverage, smoke, data validator, pre-commit, performance e matriz.
- Bloqueadores: `pytest-cov`/`coverage` não estão instalados no Python de desenvolvimento; CI instalará extras de dev e a validação local usará ferramentas disponíveis sem instalação em runtime.
- Decisões: separar job caro de 10.000 seeds da matriz rápida e manter frontend sem dependências npm.
- Commit/PR: pendente.
- Próxima ação: implementar o menor conjunto completo da ETAPA 13.

### 2026-07-22 19:58 -04:00 — PAUSA DA ETAPA 13

- Status anterior: `IN_PROGRESS`.
- Status novo: `DONE`.
- Branch: `ci/quality-matrix`.
- Objetivo: validar todos os gates locais e preparar execução multiplataforma reproduzível.
- Arquivos alterados: workflow CI, configuração de coverage/pre-commit, scripts de dados/performance, bootstrap testável e guia de desenvolvimento.
- Implementação: matriz Python 3.10/3.12/3.13 em Ubuntu/Windows, job property, cobertura 80%/90%, Node sem npm e build.
- Testes executados: Ruff, format, mypy, unittest, pytest, trace coverage, cinco testes Node, data validator, benchmark, property 10.000 seeds, wheel e smoke ComfyUI.
- Resultado dos testes: PASS no Windows; 81 testes/316 subtests, core acima de 90% por line trace, 60.000 composições property e 3.000 composições em 4,235 s.
- Pendências: executar o workflow hospedado e obter resultado Linux/Windows verde; ETAPA 14 permanece inelegível até fechar esta dependência.
- Bloqueadores: o repositório remoto ainda não estava configurado nesta pausa.
- Decisões: não inventar compatibilidade Linux nem marcar a etapa `DONE` sem uma execução real; dependências Hypothesis e pre-commit são somente do extra `dev`.
- Commit/PR: `c7a3f87` (`ci: enforce cross-platform quality checks`).
- Próxima ação: configurar um remote autorizado, publicar a branch e executar a CI hospedada.

### 2026-07-22 20:57 -04:00 — RETOMADA DA ETAPA 13

- Status anterior: `PARTIAL`.
- Status novo: `PARTIAL`.
- Branch: `ci/quality-matrix`, acompanhando `origin/ci/quality-matrix`.
- Objetivo: concluir a validação multiplataforma somente pelo GitHub Actions e eliminar a dependência de ambiente Linux local.
- Arquivos alterados: este registro e testes de parser, API de preview e seeds/seleção.
- Implementação: remote público confirmado; run `29970353368` inspecionado no GitHub Actions; testes direcionados adicionados para contratos inválidos, limites de seed e shapes inválidos da API.
- Testes executados: matriz remota com Ubuntu/Windows e Python 3.10/3.12/3.13; localmente Ruff, format, mypy, dois gates coverage.py, Node, validação de dados, build, 10.000 seeds por perfil e benchmark.
- Resultado dos testes: a run remota anterior falhou no core com 87,93%; após a correção, 87 testes passam, cobertura total é 91,70% e cobertura do core é 92,69%; cinco testes frontend, 60.000 composições determinísticas e build aprovados.
- Pendências: nenhuma da ETAPA 13.
- Bloqueadores: nenhum.
- Decisões: GitHub Actions é a única fonte de validação Linux; toda troca com o repositório será feita por `git remote`.
- Commit/PR: `01c8119` (`test: raise core coverage above quality gate`); GitHub Actions run `29970873136`.
- Próxima ação: iniciar a ETAPA 14 — Documentação e exemplos.

### 2026-07-22 21:45 -04:00 — ETAPA 14

- Status anterior: `PENDING`.
- Status novo: `IN_PROGRESS`.
- Branch: `docs/user-manual`.
- Objetivo: criar `MANUAL.md` passo a passo para o único nó público, todas as configurações, editor visual, entradas avançadas, saídas, integração e troubleshooting.
- Arquivos alterados: `MANUAL.md`, `README.md` e este registro.
- Implementação: manual em português com primeiro uso, ligações no workflow, perfis, 13 entradas, precedência, 5 modos, editor visual, campos/grupos, 5 saídas, receitas, determinismo, erros e segurança; README obsoleto corrigido e ligado ao manual.
- Testes executados: verificador de links Markdown e cobertura dos nomes do schema; Ruff check/format, mypy, pytest, testes Node, validação dos dados e `git diff --check`.
- Resultado dos testes: PASS; links locais válidos, 13 entradas e 5 saídas documentadas, 87 testes/337 subtests Python, 5 testes frontend e 27 JSONs oficiais aprovados.
- Pendências: screenshots, workflows, exemplo de perfil e revisão documental restante continuam pendentes na ETAPA 14.
- Bloqueadores: nenhum.
- Decisões: manual em português, orientado a tarefas, com distinção explícita entre controles visíveis, estado do editor e entradas avançadas.
- Commit/PR: `168d0cb` (`docs: add complete Prompt Architect user manual`), seguido por `6edc562` (normalização de EOF); branch publicada em `origin/docs/user-manual`.
- Próxima ação: publicar a branch e continuar as demais entregas da ETAPA 14.

### 2026-07-22 23:10 -04:00 — EXPANSÃO DO CATÁLOGO V2

- Status anterior: `PENDING`.
- Status novo: `DONE` localmente.
- Branch: `docs/user-manual`.
- Objetivo: implementar integralmente `PROMPT_AGENTE_EXPANSAO_CATALOGO.md` sem publicar release.
- Arquivos alterados: contratos e schemas V2, repository, parser, seletor, regras, renderer, manifesto, 81 packs, 15 perfis, frontend, scripts de auditoria, testes, CI e documentação.
- Implementação: índice e packs modulares versionados; 69 dimensões lógicas; seleção hierárquica por família; cinco modos de geração; variantes determinísticas; densidade adaptativa; negativos modulares; 15 perfis oficiais; manifesto V2; compatibilidade de leitura V1; gerador offline reproduzível.
- Auditoria externa: `E:\ComfyUI\ComfyUI\wildcards` foi usado somente para ampliar a taxonomia. Nomes próprios, artistas, marcas, horror gráfico, linhas sensuais ambíguas, duplicatas e entradas multidimensionais não foram importados literalmente.
- Correção durante a validação: a primeira execução completa revelou 63 opções de `subject-type` inacessíveis porque todos os perfis fixavam o fallback. A dimensão passou a `random`; todas as opções permanecem explicitamente adultas, e o lock do grupo de identidade preserva determinismo.
- Resultado dos testes: 103 testes Python e 193 subtests; 8 testes Node; Ruff, format e mypy aprovados; 126 JSONs validados; 5.184 opções semanticamente únicas; 150.000 prompts com cobertura global integral, 100% de unicidade por perfil e zero fallback; benchmark dentro do limite.
- Empacotamento: `python -m build` indisponível porque o módulo de desenvolvimento `build` não está instalado; a alternativa sem instalação `pip wheel --no-build-isolation` gerou o wheel `0.3.0.dev0`.
- Pendências: execução da CI remota Linux/Windows e eventual commit/publicação dependem de ação posterior; nenhuma release ou Registry foi publicado.
- Bloqueadores: nenhum para a implementação local.
- Commit/PR: baseline pré-implementação `5999366`; alterações da expansão ainda não commitadas.
- Próxima ação: revisar o diff, criar um commit Conventional Commit se autorizado e executar a CI por `git remote`.

## 6. Testes executados

| Data | Etapa | Comando | Resultado | Evidência/observação |
|---|---:|---|---|---|
| 2026-07-22 | 0 | `python -m compileall -q prompt_architect` | PASS | Pacote compilado sem erro. |
| 2026-07-22 | 0 | `python -c "import prompt_architect; assert prompt_architect.__version__ == '0.1.0.dev0'"` | PASS | Core importado sem ComfyUI. |
| 2026-07-22 | 0 | `python -c "import pathlib, tomllib; tomllib.loads(...)"` | PASS | `pyproject.toml` válido para `tomllib`. |
| 2026-07-22 | 0 | `python -m ruff check .` | PASS | Zero erros. |
| 2026-07-22 | 0 | `python -m ruff format --check .` | PASS | Sete arquivos formatados na correção e aprovados na repetição. |
| 2026-07-22 | 0 | `python -m mypy` | PASS | Zero issues em 7 arquivos. |
| 2026-07-22 | 0 | `python -m pytest --cov=prompt_architect --cov-report=term-missing` | UNAVAILABLE | Módulo opcional `pytest` não instalado no Python local; nenhuma instalação global foi feita. |
| 2026-07-22 | 0 | `python -m unittest discover -s tests -v` | PASS | 1 teste executado. |
| 2026-07-22 | 0 | `python -m build --no-isolation` | UNAVAILABLE | Módulo opcional `build` não instalado no Python local. |
| 2026-07-22 | 0 | `python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist` | FAIL/PASS | Primeira execução revelou classificador de licença incompatível com PEP 639; após remoção do classificador redundante, wheel `0.1.0.dev0` construído. |
| 2026-07-22 | 1 | `python -m compileall -q prompt_architect` | PASS | Contratos compilados. |
| 2026-07-22 | 1 | Parse JSON com `json.loads` | PASS | Todos os schemas e fixtures JSON válidos sintaticamente. |
| 2026-07-22 | 1 | `python -m ruff check .` / `python -m ruff format --check .` | PASS | Zero erros; 12 arquivos formatados. |
| 2026-07-22 | 1 | `python -m mypy` | PASS | Zero issues em 12 arquivos. |
| 2026-07-22 | 1 | `python -m unittest discover -s tests -v` | PASS | 12 testes executados. |
| 2026-07-22 | 1 | `python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist` | PASS | Wheel `0.1.0.dev0` construído. |
| 2026-07-22 | 2 | `python -m ruff check .` / `python -m ruff format --check .` | PASS | Zero erros; 18 arquivos formatados. |
| 2026-07-22 | 2 | `python -m mypy` | PASS | Zero issues em 18 arquivos. |
| 2026-07-22 | 2 | `python -m unittest discover -s tests -v` | PASS | 22 testes executados. |
| 2026-07-22 | 2 | `python -m compileall -q prompt_architect` | PASS | Pacote compilado. |
| 2026-07-22 | 2 | `python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist` | PASS | Wheel construído. |
| 2026-07-22 | 2 | Scan `rg` de `eval`, `exec`, `pickle`, `subprocess` em Python | PASS | Nenhuma ocorrência. |
| 2026-07-22 | 3 | `python -m ruff check .` / `python -m ruff format .` | PASS | Zero erros; 21 arquivos estáveis. |
| 2026-07-22 | 3 | `python -m mypy` | PASS | Zero issues em 21 arquivos. |
| 2026-07-22 | 3 | `python -m unittest discover -s tests -v` | PASS | 33 testes executados. |
| 2026-07-22 | 3 | `python -m compileall -q prompt_architect` | PASS | Pacote compilado. |
| 2026-07-22 | 3 | `python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist` | PASS | Wheel construído. |
| 2026-07-22 | 4 | `python -m ruff check .` / `python -m ruff format --check .` | PASS | Zero erros; 23 arquivos formatados. |
| 2026-07-22 | 4 | `python -m mypy` | PASS | Zero issues em 23 arquivos. |
| 2026-07-22 | 4 | `python -m unittest discover -s tests -v` | PASS | 40 testes executados. |
| 2026-07-22 | 4 | `python -m compileall -q prompt_architect` e wheel | PASS | Compilação e empacotamento aprovados. |
| 2026-07-22 | 5 | `python -m ruff check .` / `python -m ruff format --check .` | PASS | Zero erros; 25 arquivos formatados. |
| 2026-07-22 | 5 | `python -m mypy` | PASS | Zero issues em 25 arquivos. |
| 2026-07-22 | 5 | `python -m unittest discover -s tests -v` | PASS | 48 testes executados. |
| 2026-07-22 | 5 | `python -m compileall -q prompt_architect` e wheel | PASS | Compilação e empacotamento aprovados. |
| 2026-07-22 | 6 | `python -m ruff check .` / `python -m ruff format .` | PASS | Zero erros; 28 arquivos formatados. |
| 2026-07-22 | 6 | `python -m mypy` | PASS | Zero issues em 28 arquivos. |
| 2026-07-22 | 6 | `python -m unittest discover -s tests -v` | PASS | 57 testes executados. |
| 2026-07-22 | 6 | `python -m compileall -q prompt_architect` e wheel | PASS | Compilação e empacotamento aprovados. |
| 2026-07-22 | 7 | `python -m ruff check .` / `python -m ruff format .` | PASS | Zero erros; 32 arquivos formatados. |
| 2026-07-22 | 7 | `python -m mypy` | PASS | Zero issues em 32 arquivos. |
| 2026-07-22 | 7 | `python -m unittest discover -s tests -v` | PASS | 65 testes executados. |
| 2026-07-22 | 7 | Compileall, parse dos schemas e wheel | PASS | Compilação, JSON e empacotamento aprovados. |
| 2026-07-22 | 8 | `python -m ruff check .` / `python -m ruff format --check .` | PASS | Zero erros; 35 arquivos formatados. |
| 2026-07-22 | 8 | `python -m mypy` | PASS | Zero issues em 35 arquivos. |
| 2026-07-22 | 8 | `python -m unittest discover -s tests -v` | PASS | 69 testes executados em 1,027 s. |
| 2026-07-22 | 8 | `python -m tests.property_profiles` | PASS | 10.000 seeds por perfil; 60.000 composições determinísticas. |
| 2026-07-22 | 8 | Compileall, parse de dados JSON e wheel | PASS | Compilação, dados e empacotamento aprovados. |
| 2026-07-22 | 9 | `python -m ruff check .` / `python -m ruff format --check .` | PASS | Zero erros. |
| 2026-07-22 | 9 | `python -m mypy` | PASS | Zero issues. |
| 2026-07-22 | 9 | `python -m unittest discover -s tests -v` | PASS | 75 testes executados. |
| 2026-07-22 | 9 | Smoke test no ComfyUI 0.27.0 local | PASS | Extensão V3 carregada; schema 13/5 e cinco outputs confirmados sem GPU. |
| 2026-07-22 | 9 | Compileall e wheel | PASS | Compilação e empacotamento aprovados. |
| 2026-07-22 | 10 | `node --test tests/frontend/state.test.mjs` | PASS | Três testes de parsing, validação e round-trip persistente. |
| 2026-07-22 | 10 | `node --check` nos módulos frontend | PASS | JavaScript sintaticamente válido. |
| 2026-07-22 | 10 | Inicialização completa e verificação HTTP no ComfyUI 0.27.0 | PASS | Nó registrado e três assets frontend retornaram HTTP 200. |
| 2026-07-22 | 11 | `python -m unittest discover -s tests -v` | PASS | 80 testes; inclui 32 previews concorrentes idênticos. |
| 2026-07-22 | 11 | Ruff, format e mypy | PASS | Zero erros em 43 arquivos tipados. |
| 2026-07-22 | 11 | GET/POST reais no ComfyUI 0.27.0 | PASS | 200 para perfil/preview/validate, 400 para ID inválido e 413 para excesso. |
| 2026-07-22 | 11 | Compileall, scan de APIs proibidas e wheel | PASS | Pacote compilado e wheel construído sem dependência nova. |
| 2026-07-22 | 12 | `node --test tests/frontend/state.test.mjs` | PASS | Cinco testes de estado, campos, tags, grupos e proteção de fixed. |
| 2026-07-22 | 12 | Ruff, mypy e 81 unittests | PASS | Zero erros; preview e nó têm paridade de identity lock. |
| 2026-07-22 | 12 | Assets e preview reais no ComfyUI 0.27.0 | PASS | Três assets 200 e seleção fixed preservada no manifesto. |
| 2026-07-22 | 13 | Ruff, format e mypy | PASS | Zero erros em 47 arquivos formatados. |
| 2026-07-22 | 13 | `python -m unittest discover -s tests -q` | PASS | 81 testes no Python 3.12 Windows. |
| 2026-07-22 | 13 | `python_embeded -m pytest -q` | PASS | 81 testes e 316 subtests em 1,92 s. |
| 2026-07-22 | 13 | `python -m trace --count --missing --summary ...` | PASS | Core com cobertura de linhas agregada acima de 90%; adapter Comfy excluído do gate. |
| 2026-07-22 | 13 | `node --test tests/frontend/state.test.mjs` | PASS | Cinco testes frontend sem dependências npm. |
| 2026-07-22 | 13 | `python -m scripts.validate_data` | PASS | 3 perfis, 20 bibliotecas e 27 JSON válidos. |
| 2026-07-22 | 13 | `python -m scripts.benchmark --iterations 1000` | PASS | 3.000 composições em 4,235 s (708,3/s). |
| 2026-07-22 | 13 | `python -m tests.property_profiles` | PASS | 10.000 seeds por perfil; 60.000 composições determinísticas. |
| 2026-07-22 | 13 | Inicialização completa ComfyUI 0.27.0 | PASS | Nó 200 (schema 3.321 bytes) e API de perfis 200 após bootstrap lazy. |
| 2026-07-22 | 13 | GitHub Actions run `29970353368` | FAIL | Property/benchmark passaram; seis jobs de qualidade falharam somente no gate do core: 87,93% < 90%. |
| 2026-07-22 | 13 | Gates locais equivalentes à CI após correção | PASS | 87 testes; cobertura total 91,70%; core 92,69%; Ruff, format, mypy, Node, dados e build aprovados. |
| 2026-07-22 | 13 | `python -m tests.property_profiles` após correção | PASS | 10.000 seeds por perfil e 60.000 composições determinísticas. |
| 2026-07-22 | 13 | `python -m scripts.benchmark --iterations 1000 --max-seconds 30` | PASS | 3.000 composições em 3,619 s (828,9/s). |
| 2026-07-22 | 13 | GitHub Actions run `29970873136` | PASS | 7/7 jobs: Ubuntu/Windows em Python 3.10/3.12/3.13 e property/benchmark; todos os passos aprovados. |
| 2026-07-22 | 14 | Validação de `MANUAL.md` e links locais | PASS | Todas as 13 entradas e 5 saídas do schema documentadas; nenhum link local quebrado. |
| 2026-07-22 | 14 | Ruff, format, mypy, pytest, Node e validação de dados | PASS | 87 testes/337 subtests Python, 5 testes frontend e 27 JSONs aprovados. |
| 2026-07-23 | V2.1 | `python -m ruff check .` / `python -m ruff format --check .` / `python -m mypy` | PASS | Zero erros; 53 arquivos formatados e 44 arquivos tipados. |
| 2026-07-23 | V2.1 | `python -m pytest -q` | UNAVAILABLE | O Python 3.12 do sistema não possui o módulo opcional `pytest`; nenhuma instalação foi feita. |
| 2026-07-23 | V2.1 | `python -m unittest discover -s tests -q` | PASS | 103 testes em 38,011 s no estado final. |
| 2026-07-23 | V2.1 | `E:\ComfyUI\python_embeded\python.exe -m pytest -q` | PASS | 103 testes e 193 subtests em 39,50 s no estado final. |
| 2026-07-23 | V2.1 | Testes Node e `node --check` | PASS | 8 testes frontend e sintaxe dos módulos aprovados. |
| 2026-07-23 | V2.1 | Validadores de dados, semântica, duplicatas e wildcards | PASS | 126 JSONs; 5.184 opções únicas; zero termo proibido; auditoria externa de 48 TXT e 2.486 linhas. |
| 2026-07-23 | V2.1 | `python -m tests.property_profiles --seeds 10000 --determinism-seeds 128 --output reports/catalog-metrics.json` | PASS | 150.000 prompts; 15 perfis; unicidade 100%; cobertura global 5.184/5.184; zero fallback. |
| 2026-07-23 | V2.1 | `python -m scripts.benchmark --iterations 1000 --max-seconds 300` | PASS | Carga em 10,901 s; pico 12,7 MiB; 15.000 composições em 252,853 s (59,3/s). |
| 2026-07-23 | V2.1 | `python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist` | PASS | Wheel `comfyui_prompt_architect-0.3.0.dev0-py3-none-any.whl`, 486.811 bytes, SHA-256 `f4e96c51efeba5d6b2fdbc898a246ae4e88f33fdcb50ab88c048cf4620ee912e`. |
| 2026-07-23 | V2.1 | Scan de APIs proibidas, `compileall` e `git diff --check` | PASS | Nenhum uso de execução dinâmica, subprocesso ou biblioteca de rede no runtime; pacote compila e diff não contém erro de whitespace. |

Nunca registrar `PASS` sem executar o comando.

## 7. Métricas de qualidade

| Métrica | Meta | Atual | Status |
|---|---:|---:|---|
| Cobertura do core | >= 90% | 92,69% por coverage.py com branches na CI | PASS |
| Cobertura total | >= 80% | 91,70% por coverage.py com branches na CI | PASS |
| Ruff | 0 erros | 0 erros | PASS |
| Mypy | 0 erros relevantes | 0 erros | PASS |
| Perfis oficiais | >= 15 | 15 | PASS |
| Packs de catálogo | Modular | 81 packs em 9 domínios | PASS |
| Opções semânticas | >= 4.000 | 5.184 únicas | PASS |
| Variantes textuais | 2–5 por opção | 15.552; 3 por opção | PASS |
| Seeds testadas por perfil | 10.000 | 10.000 | PASS |
| Cobertura global do catálogo | 100% | 5.184/5.184 | PASS |
| Prompts vazios | 0 | 0 em 150.000 seeds | PASS |
| Placeholders residuais | 0 | 0 em 150.000 seeds | PASS |
| Windows | Suportado | Core, frontend state e ComfyUI 0.27.0 validados | PASS |
| Linux | Suportado | 87 testes e todos os gates aprovados em Python 3.10/3.12/3.13 | PASS |

## 8. Bloqueadores

| ID | Data | Etapa | Descrição | Impacto | Responsável | Estado | Resolução |
|---|---|---:|---|---|---|---|---|
| B-001 | 2026-07-22 | 13 | Sem Git remote para executar GitHub Actions | Impedia validar CI hospedada e Linux | Usuário | RESOLVIDO | `origin` configurado e branch publicada em 2026-07-22 |
| B-003 | 2026-07-22 | 13 | Cobertura do core na CI em 87,93%, abaixo da meta de 90% | Impedia workflow verde e conclusão da etapa | Projeto | RESOLVIDO | Testes elevaram o gate para 92,69%; run `29970873136` verde |

## 9. Riscos

| ID | Risco | Probabilidade | Impacto | Mitigação | Estado |
|---|---|---|---|---|---|
| R-001 | Mudança na API V3 | Média | Alta | Usar API pública e verificar documentação atual | Aberto |
| R-002 | Estado do frontend não persistir | Média | Alta | JSON no widget como fonte de verdade | Aberto |
| R-003 | Regras criarem ciclos | Média | Alta | Detecção de ciclo e limite de profundidade | Aberto |
| R-004 | Bibliotecas gerarem prompts estranhos | Alta | Média | Frases completas, testes e pesos | Aberto |
| R-005 | Dependências conflitarem | Baixa | Alta | Core stdlib e dev deps separadas | Aberto |
| R-006 | Cache não invalidar dados | Média | Média | mtime, tamanho e hash estável | Aberto |
| R-007 | Configuração muito grande no workflow | Média | Média | IDs, defaults e serialização compacta | Aberto |

## 10. Decision Log

| ID | Data | Decisão | Motivo | Alternativas rejeitadas | Impacto |
|---|---|---|---|---|---|
| D-001 | Inicial | API V3 | Projeto novo e público | API legacy V1 | Arquitetura inicial |
| D-002 | Inicial | JSON oficial | Seguro, portável e validável | YAML, Python, TXT puro | Dados estruturados |
| D-003 | Inicial | Core sem ComfyUI | Testabilidade | Lógica dentro do nó | Separação de camadas |
| D-004 | Inicial | Sem escrita persistente no MVP | Segurança | Editor de arquivos no servidor | Frontend inicial |
| D-005 | 2026-07-22 | Preservar o repositório Git e o commit inicial existentes | O projeto já estava inicializado corretamente | Reinicializar ou apagar histórico | Bootstrap parte do commit `548e757` |
| D-006 | 2026-07-22 | Representar `0.1.0-dev` como `0.1.0.dev0` | Forma canônica e interoperável do PEP 440 | Manter grafia não canônica nos metadados | Versão de pacote normalizada |
| D-007 | 2026-07-22 | Não aplicar scaffold específico do ComfyUI na ETAPA 0 | Adapter público V3 pertence à ETAPA 9 e o core precisa importar sem ComfyUI | Criar adapter provisório ou legado | Bootstrap contém somente limites de pacote vazios |
| D-008 | 2026-07-22 | Manter ETAPA 13 `PARTIAL` até uma execução Linux/Windows real da CI | O plano proíbe inventar compatibilidade ou marcar aceite não executado | Marcar `DONE` apenas com equivalentes Windows locais | Cumprida pela run `29970873136`; ETAPA 14 elegível |
| D-009 | 2026-07-22 | Validar Linux exclusivamente pelo GitHub Actions e operar o repositório por `git remote` | O repositório público e runners hospedados fornecem a matriz reproduzível exigida | Manter uma segunda infraestrutura Linux local | Remove dependências locais do fluxo de CI |
| D-010 | 2026-07-22 | Introduzir `custom` no schema de configuração 1.1 e preservar leitura do schema 1.0 | Texto livre por seção tem semântica distinta de um ID `fixed` e precisa ser portátil, limitado e auditável | Reutilizar `fixed` com IDs inexistentes; aceitar caminhos ou editar bibliotecas em runtime | Novo texto livre é explícito, determinístico, protegido e registrado no manifesto; pacote `0.2.0.dev0` |
| D-011 | 2026-07-22 | Introduzir Catálogo e Manifesto V2 com leitura compatível de dados V1 | Packs independentes, proveniência, variantes e versionamento não cabem no contrato V1 sem ambiguidade | Alterar silenciosamente o schema V1; descartar compatibilidade | Contratos públicos versionados; pacote `0.3.0.dev0` |
| D-012 | 2026-07-22 | Gerar os dados oficiais por script offline determinístico | O volume exige reprodução, revisão estrutural e IDs estáveis sem instalação ou rede em runtime | Arquivos manuais sem fonte reproduzível; geração durante execução do nó | 81 packs e 15 perfis podem ser regenerados e auditados localmente |
| D-013 | 2026-07-22 | Usar `E:\ComfyUI\ComfyUI\wildcards` somente como referência de taxonomia | A fonte contém duplicatas, nomes próprios, marcas, conteúdo inseguro e linhas multidimensionais | Copiar linhas literalmente; ignorar completamente a taxonomia disponível | Conteúdo final é original, atômico, seguro e rastreável por domínio |
| D-014 | 2026-07-23 | Tornar `subject-type` aleatório nos perfis oficiais, mantendo fallback adulto | A auditoria de 150.000 prompts revelou que o modo fixo deixava 63 opções seguras inacessíveis | Reduzir artificialmente o conjunto elegível; remover as opções | Cobertura global integral e maior diversidade, preservando segurança e `identity_lock` |

## 11. Dívida técnica

| ID | Origem | Descrição | Prioridade | Etapa alvo | Estado |
|---|---|---|---|---|---|
| — | — | Nenhuma registrada | — | — | — |

## 12. Compatibilidade validada

| Componente | Versão | Sistema | Resultado | Data |
|---|---|---|---|---|
| Python | 3.12.10 | Windows | Ambiente local identificado | 2026-07-22 |
| ComfyUI | 0.27.0 | Windows | Versão local identificada em `comfyui_version.py` | 2026-07-22 |
| ComfyUI Frontend | 1.45.20 (requisito local) | Windows | Versão fixada no `requirements.txt` do ComfyUI 0.27.0; pacote não instalado neste Python | 2026-07-22 |

## 13. Release readiness

### Código

- [ ] API pública estável.
- [ ] Schemas congelados.
- [ ] Sem TODO crítico.
- [ ] Sem warning crítico.
- [x] Sem dependência dinâmica.
- [x] Sem `eval`/`exec`.
- [x] Performance medida.

### Testes

- [x] Unitários.
- [x] Integração.
- [x] Propriedade.
- [x] Smoke workflow.
- [x] Windows.
- [x] Linux.
- [ ] Instalação limpa.

### Documentação

- [ ] README.
- [ ] Configuração.
- [ ] Regras.
- [ ] Autor de perfil.
- [ ] Troubleshooting.
- [ ] Development.
- [ ] CONTRIBUTING.
- [ ] SECURITY.
- [ ] CHANGELOG.

### Publicação

- [ ] Nome final.
- [ ] Publisher ID.
- [ ] Metadata.
- [ ] Ícone.
- [ ] Banner.
- [ ] GitHub Release.
- [ ] Registry.
- [ ] Workflow de exemplo.

## 14. Próxima ação obrigatória

Revisar o diff da expansão, decidir o commit e executar a CI remota Linux/Windows por `git remote`; a publicação de release/Registry continua condicionada a autorização explícita.
