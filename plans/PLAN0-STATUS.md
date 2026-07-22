# PLAN0-STATUS — Prompt Architect

> Registro operacional obrigatório da execução de `PLAN0.md`.

## 1. Estado geral

| Campo | Valor |
|---|---|
| Projeto | Prompt Architect |
| Plano | `PLAN0.md` |
| Versão do plano | 1.0 |
| Status geral | `IN_PROGRESS` |
| Etapa atual | ETAPA 5 |
| Última atualização | 2026-07-22 18:58 -04:00 |
| Responsável atual | Agente IA no VS Code |
| Branch atual | `feat/compositor` |
| Próximo marco | Compositor estruturado e fallbacks |
| Bloqueadores | Nenhum identificado |

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
| 5 | Compositor e fallbacks | IN_PROGRESS | 2, 3, 4 | 2026-07-22 18:58 -04:00 | — | — | Compositor em implementação |
| 6 | Renderer e normalização | PENDING | 1, 5 | — | — | — | — |
| 7 | Validação e manifesto | PENDING | 5, 6 | — | — | — | — |
| 8 | Perfis e bibliotecas | PENDING | 2–7 | — | — | — | — |
| 9 | Nó ComfyUI V3 | PENDING | 7, 8 | — | — | — | — |
| 10 | Frontend mínimo | PENDING | 9 | — | — | — | — |
| 11 | Preview e validação API | PENDING | 7, 9, 10 | — | — | — | — |
| 12 | Interface avançada | PENDING | 10, 11 | — | — | — | — |
| 13 | Qualidade e CI | PENDING | 0–12 | — | — | — | Pode começar parcialmente antes |
| 14 | Documentação e exemplos | PENDING | 8–13 | — | — | — | Documentação incremental obrigatória |
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

- [ ] Ordem de seções e contexto incremental implementados.
- [ ] Limite de tentativas implementado.
- [ ] Relaxamento por modo implementado.
- [ ] Fallback local/global implementado.
- [ ] Tentativas, conflitos e fallbacks registrados.
- [ ] Retorno estruturado implementado.
- [ ] Seções obrigatórias resolvem ou falham explicitamente.
- [ ] Lint, tipagem e testes aprovados.
- [ ] Documentação atualizada.
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

Nunca registrar `PASS` sem executar o comando.

## 7. Métricas de qualidade

| Métrica | Meta | Atual | Status |
|---|---:|---:|---|
| Cobertura do core | >= 90% | Não medida | PENDING |
| Cobertura total | >= 80% | Não medida | PENDING |
| Ruff | 0 erros | 0 erros | PASS |
| Mypy | 0 erros relevantes | 0 erros | PASS |
| Perfis oficiais | 3 | 0 | PENDING |
| Seeds testadas por perfil | 10.000 | 0 | PENDING |
| Prompts vazios | 0 | Não medido | PENDING |
| Placeholders residuais | 0 | Não medido | PENDING |
| Windows | Suportado | Bootstrap validado em Windows | PARTIAL |
| Linux | Suportado | Não testado | PENDING |

## 8. Bloqueadores

| ID | Data | Etapa | Descrição | Impacto | Responsável | Estado | Resolução |
|---|---|---:|---|---|---|---|---|
| — | — | — | Nenhum | — | — | — | — |

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
- [ ] Sem dependência dinâmica.
- [ ] Sem `eval`/`exec`.
- [ ] Performance medida.

### Testes

- [ ] Unitários.
- [ ] Integração.
- [ ] Propriedade.
- [ ] Smoke workflow.
- [ ] Windows.
- [ ] Linux.
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

Executar a **ETAPA 5 — Compositor e fallbacks**, seguindo integralmente `PLAN0.md`.
