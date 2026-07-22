# PLAN0-STATUS — Prompt Architect

> Registro operacional obrigatório da execução de `PLAN0.md`.

## 1. Estado geral

| Campo | Valor |
|---|---|
| Projeto | Prompt Architect |
| Plano | `PLAN0.md` |
| Versão do plano | 1.0 |
| Status geral | `NOT_STARTED` |
| Etapa atual | ETAPA 0 |
| Última atualização | Não iniciada |
| Responsável atual | Agente IA no VS Code |
| Branch atual | Não criada |
| Próximo marco | Bootstrap do repositório |
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
| 0 | Bootstrap e decisões | PENDING | — | — | — | — | Primeira etapa |
| 1 | Contratos e modelos | PENDING | 0 | — | — | — | — |
| 2 | Loader e cache | PENDING | 1 | — | — | — | — |
| 3 | Seeds e seleção | PENDING | 1 | — | — | — | — |
| 4 | Motor de regras | PENDING | 1, 3 | — | — | — | — |
| 5 | Compositor e fallbacks | PENDING | 2, 3, 4 | — | — | — | — |
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

- [ ] Repositório criado.
- [ ] Git inicializado.
- [ ] Branch de trabalho criada.
- [ ] Estrutura mínima criada.
- [ ] `PLAN0.md` preservado.
- [ ] `PLAN0-STATUS.md` preservado.
- [ ] `AGENTS.md` preservado.
- [ ] `pyproject.toml` criado.
- [ ] Licença criada.
- [ ] README inicial criado.
- [ ] Documentos comunitários criados.
- [ ] Pacote importa.
- [ ] `compileall` aprovado.
- [ ] Versões do ambiente registradas.
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

## 6. Testes executados

| Data | Etapa | Comando | Resultado | Evidência/observação |
|---|---:|---|---|---|
| — | — | — | — | Nenhum teste executado |

Nunca registrar `PASS` sem executar o comando.

## 7. Métricas de qualidade

| Métrica | Meta | Atual | Status |
|---|---:|---:|---|
| Cobertura do core | >= 90% | Não medida | PENDING |
| Cobertura total | >= 80% | Não medida | PENDING |
| Ruff | 0 erros | Não executado | PENDING |
| Mypy | 0 erros relevantes | Não executado | PENDING |
| Perfis oficiais | 3 | 0 | PENDING |
| Seeds testadas por perfil | 10.000 | 0 | PENDING |
| Prompts vazios | 0 | Não medido | PENDING |
| Placeholders residuais | 0 | Não medido | PENDING |
| Windows | Suportado | Não testado | PENDING |
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

## 11. Dívida técnica

| ID | Origem | Descrição | Prioridade | Etapa alvo | Estado |
|---|---|---|---|---|---|
| — | — | Nenhuma registrada | — | — | — |

## 12. Compatibilidade validada

| Componente | Versão | Sistema | Resultado | Data |
|---|---|---|---|---|
| Python | Não registrada | — | PENDING | — |
| ComfyUI | Não registrada | — | PENDING | — |
| ComfyUI Frontend | Não registrada | — | PENDING | — |

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

Executar a **ETAPA 0 — Bootstrap e decisões de projeto**, seguindo integralmente `PLAN0.md`.
