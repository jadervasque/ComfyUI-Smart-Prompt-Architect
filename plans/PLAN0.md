# PLAN0 — Prompt Architect para ComfyUI

> Plano mestre de implementação para um custom node profissional, determinístico e altamente configurável de composição estruturada de prompts.

## 0. Metadados do projeto

| Campo | Valor inicial |
|---|---|
| Nome público do produto | **Prompt Architect** |
| Nome sugerido do repositório | `ComfyUI-Prompt-Architect` |
| ID sugerido no Comfy Registry | `prompt-architect` |
| Nó principal | `Prompt Architect` |
| Categoria no ComfyUI | `Prompt Architect/Generation` |
| Licença sugerida | Apache-2.0 |
| Versão inicial | `0.1.0-dev` |
| Primeira versão estável | `1.0.0` |
| API de nós | ComfyUI API V3 |
| Backend | Python |
| Frontend | JavaScript |
| Plano | `PLAN0.md` |
| Registro | `PLAN0-STATUS.md` |
| Regras para agentes | `AGENTS.md` |

Os nomes acima são decisões de trabalho. Identificadores dependentes da conta do autor ou Publisher ID devem permanecer como placeholders até serem fornecidos. Alterações arquiteturais devem ser registradas no Decision Log de `PLAN0-STATUS.md`.

---

# 1. Missão

Criar um custom node público para ComfyUI que componha prompts complexos de forma centralizada, estruturada, reproduzível e semanticamente coerente, evitando:

- Teias extensas de nós de string.
- Prompts vazios ou incompletos.
- Combinações incompatíveis.
- Repetições, pontuação quebrada e gramática defeituosa.
- Aleatoriedade não reproduzível.
- Alteração acidental da identidade quando somente cena, pose ou roupa deveria variar.
- Configuração opaca embutida no workflow.
- Dependência obrigatória de outros custom nodes.

O produto deve oferecer perfis prontos para iniciantes e bibliotecas, regras, pesos, templates e overrides para usuários avançados.

---

# 2. Visão do produto

O workflow ideal utiliza um nó principal:

```text
┌──────────────────────────────────────────────┐
│ Prompt Architect                             │
│                                              │
│ Profile: Virtual Model                       │
│ Seed: 123456                                 │
│ Mode: Balanced                               │
│ Identity Lock: Enabled                       │
│ Strict Validation: Enabled                   │
│                                              │
│ [Open Architect] [Validate] [Preview]        │
└──────────────────────────────────────────────┘
            │
            ├── positive_prompt : STRING
            ├── negative_prompt : STRING
            ├── manifest_json   : STRING
            ├── summary         : STRING
            └── seed_used       : INT
```

O usuário deve poder:

- Carregar um perfil pronto.
- Fixar, desativar, herdar ou randomizar qualquer campo.
- Bloquear grupos como identidade e cabelo.
- Variar grupos como roupa, pose, expressão, cenário, iluminação e câmera.
- Definir pesos e regras de compatibilidade.
- Visualizar e validar o prompt antes da geração.
- Reproduzir o mesmo resultado com a mesma seed e configuração.
- Salvar um manifesto JSON de todas as escolhas.
- Gerar em lote sem prompts vazios.
- Compartilhar perfis e bibliotecas.

---

# 3. Princípios obrigatórios

## 3.1 Selecionar antes de renderizar

A ordem do motor deve ser:

1. Carregar configuração.
2. Resolver modos e locks.
3. Selecionar valores compatíveis.
4. Aplicar implicações e preferências.
5. Validar o contexto estruturado.
6. Renderizar frases.
7. Normalizar gramática e pontuação.
8. Validar o prompt final.
9. Retornar prompt e manifesto.

Nunca concatenar textos aleatórios antes de validar compatibilidade.

## 3.2 Nenhum prompt vazio

O nó principal nunca deve retornar silenciosamente um prompt positivo vazio. Deve tentar candidatos, aplicar fallbacks e, caso ainda não haja resultado válido, interromper a execução com erro claro.

## 3.3 Determinismo

A mesma versão do perfil, bibliotecas, configuração, seed e motor deve produzir o mesmo manifesto e prompt.

## 3.4 Core independente

A lógica de composição não pode depender de ComfyUI, aiohttp ou JavaScript. Deve ser importável e testável como biblioteca Python pura.

## 3.5 Segurança e portabilidade

- Proibido `eval` e `exec`.
- Proibido instalar pacotes em runtime.
- Proibido executar comandos de shell no motor.
- Proibido carregar código Python de perfis.
- Dados de usuário devem ser JSON validado.
- Core preferencialmente somente com biblioteca padrão.
- Nenhum acesso de rede durante a execução.
- Nenhum segredo no repositório.

---

# 4. Escopo da versão 1.0

## 4.1 Incluído

- Nó principal `Prompt Architect`.
- API V3.
- Perfis e bibliotecas JSON.
- Modos `disabled`, `fixed`, `random` e `inherit`.
- Seleção aleatória ponderada.
- Seeds determinísticas e locks por grupo.
- Regras `requires`, `excludes`, `implies` e `prefer`.
- Grupos mutuamente exclusivos.
- Fallbacks por seção e perfil.
- Templates seguros.
- Normalização de espaços, pontuação e artigo básico em inglês.
- Deduplicação exata e por chave semântica.
- Prompt positivo e negativo.
- Manifesto JSON e resumo diagnóstico.
- Interface visual centralizada.
- Pré-visualização e validação.
- Perfis oficiais.
- Testes, CI, documentação e workflows de exemplo.
- Empacotamento para GitHub e Comfy Registry.

## 4.2 Fora do escopo da versão 1.0

- Modelo de linguagem para reescrever prompts.
- Tradução automática por IA.
- Download automático de bibliotecas.
- Marketplace de perfis.
- Sincronização em nuvem.
- Treinamento de LoRA.
- Análise ou geração de imagem no nó.
- Programação arbitrária de regras.
- Execução de expressões do usuário.
- Banco de dados ou telemetria.

---

# 5. Personas e casos de uso

## 5.1 Criador de modelo virtual

Mantém identidade, face e atributos principais; varia expressão, pose, roupa, cenário, iluminação e câmera. Mudar a seed de cena não pode mudar a identidade bloqueada.

## 5.2 Criador de dataset para LoRA

Precisa de cobertura equilibrada, manifesto, reprodutibilidade, ausência de combinações inválidas e modo sequencial ou orientado à cobertura.

## 5.3 Usuário casual

Escolhe perfil e seed e recebe prompt válido sem editar JSON.

## 5.4 Autor de perfil

Cria bibliotecas, opções, tags, pesos, regras, fallbacks e templates; valida antes de publicar.

---

# 6. Requisitos funcionais

## RF-001 — Perfil

- Listar somente perfis válidos.
- Erros devem indicar arquivo relativo e motivo.
- Todo perfil possui ID, versão e `schema_version`.

## RF-002 — Modos de campo

- `disabled`: não participa.
- `fixed`: usa valor escolhido.
- `random`: seleciona candidato elegível.
- `inherit`: herda do perfil, grupo ou entrada conectada.

## RF-003 — Seleção ponderada

- `weight >= 0`.
- Peso zero desativa a opção.
- Peso negativo, NaN ou infinito são inválidos.
- Soma zero aciona fallback ou erro.

## RF-004 — Regras

Suportar `requires`, `excludes`, `implies` e `prefer`.

## RF-005 — Fallback

Toda seção obrigatória deve possuir fallback local ou do perfil. O manifesto registra cada fallback utilizado.

## RF-006 — Locks por grupo

Grupos mínimos:

- `identity`
- `appearance`
- `outfit`
- `pose`
- `scene`
- `lighting`
- `camera`
- `quality`
- `negative`

## RF-007 — Manifesto

Deve conter:

- Versões do schema, motor, perfil e bibliotecas.
- Seed mestre e subseeds.
- Configuração efetiva e hash.
- Seleções por seção.
- Regras aplicadas.
- Conflitos resolvidos.
- Fallbacks, tentativas e avisos.
- Prompts finais.

## RF-008 — Diagnóstico

O output `summary` deve informar seções geradas, campos desativados, fallbacks, tentativas, avisos, seed e perfil.

## RF-009 — Prompt positivo válido

Impedir execução quando:

- Perfil não possui seções suficientes.
- Template não pode ser resolvido.
- Restam placeholders.
- Resultado está abaixo do mínimo.
- Seção obrigatória não possui valor nem fallback.

## RF-010 — Prompt negativo

O perfil pode definir fragmentos globais, condicionais e overrides do usuário.

## RF-011 — Prefixos e sufixos

Permitir prefixo e sufixo positivos e negativos sem apagar conteúdo do usuário.

## RF-012 — Preview

Gerar preview sem enfileirar geração de imagem.

## RF-013 — Validação

Validar perfil, bibliotecas, configuração e resultado.

## RF-014 — Persistência no workflow

A configuração efetiva deve ser serializável no workflow e não depender de caminho absoluto da máquina do autor.

## RF-015 — Dados de usuário

Aceitar diretório opcional autorizado, sem traversal e sem sobrescrever dados internos.

---

# 7. Requisitos não funcionais

## RNF-001 — Compatibilidade

- API V3.
- Versão mínima do ComfyUI documentada.
- Evitar imports internos não documentados.
- Testar Windows e Linux.

## RNF-002 — Performance

Metas orientativas:

- Load em cache < 25 ms.
- Composição < 10 ms.
- Validação < 10 ms.
- Sem GPU e sem rede.

## RNF-003 — Qualidade

- Type hints em APIs públicas.
- Docstrings públicas.
- Funções preferencialmente menores que 60 linhas.
- Core com cobertura >= 90%.
- Projeto com cobertura >= 80%.
- Zero falhas de lint no branch principal.

## RNF-004 — Confiabilidade

Para cada perfil oficial, testar pelo menos 10.000 seeds sem prompt vazio, placeholder residual ou conflito absoluto.

## RNF-005 — Observabilidade

- Logger com namespace.
- Níveis adequados.
- Não registrar prompts completos em `info` por padrão.
- Não expor caminhos sensíveis desnecessários.

## RNF-006 — Evolução

- Schema versionado.
- Migrações explícitas.
- Semantic Versioning.
- Nenhuma mudança silenciosa de semântica.

---

# 8. Arquitetura

## 8.1 Camadas

```text
┌───────────────────────────────────────────────────────┐
│ Frontend ComfyUI                                      │
│ editor, preview, validação, widgets, modal            │
└─────────────────────────┬─────────────────────────────┘
                          │ HTTP local / dados do nó
┌─────────────────────────▼─────────────────────────────┐
│ Adapter ComfyUI                                       │
│ schema V3, inputs, outputs, rotas e erros             │
└─────────────────────────┬─────────────────────────────┘
                          │ objetos tipados
┌─────────────────────────▼─────────────────────────────┐
│ Application Service                                   │
│ load → select → rules → render → validate             │
└───────────────┬───────────────┬───────────────────────┘
                │               │
┌───────────────▼──────┐ ┌──────▼───────────────────────┐
│ Domain/Core          │ │ Infrastructure               │
│ modelos e engine     │ │ JSON, cache, paths e hashing │
└──────────────────────┘ └──────────────────────────────┘
```

## 8.2 Dependências

- `domain` não importa ComfyUI, aiohttp ou frontend.
- `application` importa `domain` e interfaces.
- `infrastructure` implementa repositórios e cache.
- `comfy` adapta o serviço à API V3.
- `web` não contém lógica de composição.

## 8.3 Fluxo

```text
Node.execute()
  → parse_node_configuration()
  → repository.load_profile()
  → repository.load_libraries()
  → engine.compose()
      → resolve_modes()
      → derive_group_seeds()
      → select_sections()
      → apply_rules()
      → resolve_fallbacks()
      → validate_context()
      → render_positive()
      → render_negative()
      → normalize()
      → validate_final()
      → build_manifest()
  → NodeOutput(...)
```

---

# 9. Estrutura de diretórios alvo

```text
ComfyUI-Prompt-Architect/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── release.yml
│   │   └── publish-registry.yml
│   ├── dependabot.yml
│   └── pull_request_template.md
├── docs/
│   ├── architecture.md
│   ├── configuration.md
│   ├── profile-authoring.md
│   ├── rules.md
│   ├── troubleshooting.md
│   └── development.md
├── examples/
│   ├── workflows/
│   ├── manifests/
│   └── profiles/
├── prompt_architect/
│   ├── __init__.py
│   ├── extension.py
│   ├── version.py
│   ├── application/
│   │   ├── compose_service.py
│   │   ├── preview_service.py
│   │   └── validation_service.py
│   ├── comfy/
│   │   ├── nodes.py
│   │   ├── routes.py
│   │   ├── errors.py
│   │   └── schemas.py
│   ├── domain/
│   │   ├── models.py
│   │   ├── enums.py
│   │   ├── exceptions.py
│   │   ├── seeds.py
│   │   ├── selector.py
│   │   ├── rules.py
│   │   ├── renderer.py
│   │   ├── normalizer.py
│   │   ├── validator.py
│   │   ├── manifest.py
│   │   └── engine.py
│   ├── infrastructure/
│   │   ├── json_loader.py
│   │   ├── repository.py
│   │   ├── cache.py
│   │   ├── hashing.py
│   │   ├── paths.py
│   │   └── atomic_write.py
│   ├── data/
│   │   ├── schemas/
│   │   ├── profiles/
│   │   └── libraries/
│   └── web/
│       ├── prompt_architect.js
│       ├── api.js
│       ├── modal.js
│       ├── state.js
│       ├── validation.js
│       └── prompt_architect.css
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── property/
│   └── fixtures/
├── AGENTS.md
├── PLAN0.md
├── PLAN0-STATUS.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── .gitignore
```

O scaffold e a documentação oficial atual prevalecem sobre detalhes de localização de arquivos exigidos pelo ComfyUI, sem alterar a separação de responsabilidades.

---

# 10. Modelo de dados

## 10.1 Perfil

```json
{
  "schema_version": "1.0",
  "id": "virtual-model",
  "version": "1.0.0",
  "display_name": "Virtual Model",
  "language": "en",
  "minimum_sections": 5,
  "minimum_prompt_characters": 80,
  "max_selection_attempts": 30,
  "section_order": [
    "subject", "identity", "face", "hair", "body", "outfit",
    "expression", "pose", "location", "lighting", "camera", "quality"
  ],
  "sections": {
    "subject": {
      "required": true,
      "library": "subjects",
      "mode": "fixed",
      "default": "adult-woman",
      "group": "identity",
      "fallback": "adult-woman"
    },
    "hair": {
      "required": true,
      "library": "hair",
      "mode": "random",
      "group": "appearance",
      "fallback": "natural-long-brown-hair"
    }
  },
  "templates": {
    "positive": "{subject}. {identity} {face} {hair}. {body}. {outfit}. {expression} {pose}. {location}. {lighting}. {camera}. {quality}.",
    "negative": "{negative_global} {negative_conditional}"
  }
}
```

## 10.2 Biblioteca

```json
{
  "schema_version": "1.0",
  "id": "hair",
  "version": "1.0.0",
  "display_name": "Hair",
  "options": [
    {
      "id": "messy-top-knot",
      "text": "Her long chestnut-brown hair is styled in a loose, slightly messy top knot",
      "weight": 1.0,
      "tags": ["feminine", "casual", "long-hair"],
      "requires": [
        {
          "field": "hair_length",
          "operator": "in",
          "value": ["medium", "long", "very-long"]
        }
      ],
      "excludes": [],
      "implies": [],
      "prefer": []
    }
  ],
  "fallback_option_id": "natural-long-brown-hair"
}
```

## 10.3 Configuração do nó

```json
{
  "schema_version": "1.0",
  "profile_id": "virtual-model",
  "profile_version": "1.0.0",
  "mode": "balanced",
  "master_seed": 123456,
  "groups": {
    "identity": {"locked": true, "seed": 99001},
    "appearance": {"locked": true, "seed": 99002},
    "outfit": {"locked": false},
    "pose": {"locked": false},
    "scene": {"locked": false}
  },
  "fields": {
    "hair_color": {"mode": "fixed", "value": "chestnut-brown"},
    "outfit": {
      "mode": "random",
      "include_tags": ["casual"],
      "exclude_tags": ["fantasy"]
    },
    "jewelry": {"mode": "disabled"}
  },
  "overrides": {
    "positive_prefix": "",
    "positive_suffix": "",
    "negative_prefix": "",
    "negative_suffix": ""
  }
}
```

## 10.4 Manifesto

```json
{
  "schema_version": "1.0",
  "engine_version": "0.1.0",
  "profile": {"id": "virtual-model", "version": "1.0.0"},
  "configuration_hash": "sha256:...",
  "master_seed": 123456,
  "group_seeds": {"identity": 99001, "appearance": 99002},
  "selections": {
    "subject": {
      "option_id": "adult-woman",
      "source": "fixed",
      "fallback": false
    }
  },
  "applied_rules": [],
  "resolved_conflicts": [],
  "fallbacks": [],
  "warnings": [],
  "positive_prompt": "...",
  "negative_prompt": "..."
}
```

---

# 11. Modelos de domínio

Implementar com `dataclasses`, `Enum`, type hints e imutabilidade quando adequada.

Modelos mínimos:

- `ProfileDefinition`
- `SectionDefinition`
- `LibraryDefinition`
- `PromptOption`
- `Rule`
- `RuleCondition`
- `NodeConfiguration`
- `FieldConfiguration`
- `GroupConfiguration`
- `SelectionContext`
- `SelectionResult`
- `RenderedPrompt`
- `ValidationIssue`
- `CompositionResult`
- `PromptManifest`

Enums mínimos:

- `FieldMode`
- `GenerationMode`
- `RuleType`
- `RuleOperator`
- `IssueSeverity`
- `SelectionSource`

Exceções mínimas:

- `PromptArchitectError`
- `ConfigurationError`
- `ProfileLoadError`
- `LibraryLoadError`
- `SchemaValidationError`
- `SelectionError`
- `RuleConflictError`
- `RenderError`
- `FinalPromptValidationError`

O adapter do ComfyUI converte exceções em mensagens claras e não exibe stack trace cru como explicação principal.

---

# 12. Sistema de seeds

## 12.1 Regras

- Utilizar `random.Random(seed)`.
- Não utilizar RNG global.
- Não usar `hash()` nativo para subseeds.
- Derivar subseeds com SHA-256 estável.

```python
import hashlib


def derive_seed(master_seed: int, namespace: str) -> int:
    payload = f"{master_seed}:{namespace}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big", signed=False)
```

## 12.2 Locks

- Grupo bloqueado com seed explícita: usar seed explícita.
- Grupo bloqueado sem seed explícita: derivar e persistir na configuração.
- Grupo não bloqueado: derivar da seed mestre atual.
- Alterar um grupo não deve alterar outros.

## 12.3 Ordem determinística

- Ordenar candidatos por ID.
- Ordenar tags para hashing.
- Serializar JSON com chaves ordenadas.
- Não depender da ordem do filesystem.

---

# 13. Motor de seleção

## 13.1 Pipeline por seção

1. Resolver configuração efetiva.
2. Carregar candidatos.
3. Remover peso zero.
4. Aplicar filtros de tags.
5. Aplicar `requires`.
6. Aplicar `excludes`.
7. Aplicar multiplicadores de `prefer`.
8. Ordenar candidatos.
9. Selecionar com RNG do grupo.
10. Aplicar `implies`.
11. Revalidar contexto.
12. Repetir se necessário.
13. Aplicar fallback.
14. Registrar no manifesto.

## 13.2 Seleção ponderada

Criar função própria testável:

```python
def weighted_choice(candidates, rng):
    ...
```

Requisitos:

- Validar pesos finitos.
- Rejeitar NaN, infinito e negativos.
- Tratar soma zero.
- Resultado reproduzível.

## 13.3 Modos

### `strict`

Todas as regras e filtros permanecem. Conflito absoluto interrompe ou usa fallback.

### `balanced`

Regras absolutas permanecem; preferências influenciam peso; filtros opcionais podem ser relaxados antes do fallback.

### `creative`

Regras absolutas permanecem; preferências têm menor impacto; diversidade recebe maior peso.

### `dataset`

Seleção orientada à cobertura, sem estado oculto. Índice ou estado deve ser input explícito.

### `sequential`

Opcional para 1.0. Se implementado, usar `batch_index` explícito e resultado reproduzível.

---

# 14. Motor de regras

## 14.1 Operadores permitidos

- `equals`
- `not_equals`
- `in`
- `not_in`
- `contains_tag`
- `missing`
- `present`

Não implementar expressão arbitrária.

## 14.2 Fontes consultáveis

- Campo resolvido.
- Tags de opção resolvida.
- Metadado seguro do perfil.
- Modo de geração.

## 14.3 Prioridade

1. Segurança e integridade.
2. Exclusões absolutas.
3. Requisitos.
4. Valores fixos do usuário.
5. Implicações.
6. Preferências.
7. Aleatoriedade.
8. Fallback.

Conflitos entre valores fixos devem gerar erro explícito.

## 14.4 Implicações

- Campo vazio: preencher.
- Mesmo valor: ignorar.
- Conflito com fixed: erro.
- Conflito com random: substituir e registrar.
- Detectar ciclos e limitar profundidade.

---

# 15. Renderização e normalização

## 15.1 Contexto

Cada seção produz:

- `option_id`
- `raw_text`
- `rendered_text`
- `tags`
- `source`
- `fallback_used`

## 15.2 Template seguro

- Placeholders permitidos por nome.
- Sem `eval`.
- Usar `string.Formatter` ou substituição segura.
- Placeholder opcional vazio não deve quebrar pontuação.
- Placeholder obrigatório ausente deve falhar antes de renderizar.

## 15.3 Frases

Bibliotecas podem possuir `text`, `sentence`, variantes ponderadas e `join_hint`. A primeira versão deve preferir frases completas.

## 15.4 Normalização

- Colapsar espaços.
- Remover espaço antes de pontuação.
- Inserir espaço após pontuação.
- Remover pontuação duplicada.
- Capitalizar início de frase.
- Converter `+` textual para `and`, quando configurado.
- Remover sentenças vazias.
- Deduplicar texto exato e `semantic_key`.
- Tratar `a`/`an` em casos básicos.

Não prometer correção linguística universal.

---

# 16. Validação ant prompt vazio

## 16.1 Dados

Validar:

- JSON.
- `schema_version`.
- IDs únicos.
- Referências.
- Fallbacks.
- Pesos.
- Operadores.
- Placeholders.
- Seções obrigatórias.

## 16.2 Contexto

Antes de renderizar:

- Todas as seções obrigatórias resolvidas.
- Nenhuma exclusão absoluta violada.
- Nenhum requisito pendente.
- Nenhum ciclo.
- Nenhum fixed descartado silenciosamente.

## 16.3 Resultado final

- `positive_prompt.strip()` não vazio.
- Comprimento e número de seções mínimos.
- Sem placeholders residuais.
- Sem `None`, `null` ou `undefined` sentinela.
- Sem conteúdo somente de pontuação.
- Prompt negativo vazio somente se permitido pelo perfil.

## 16.4 Fallback em cascata

```text
candidatos válidos
  ↓ nenhum
relaxar preferências
  ↓ nenhum
relaxar filtros opcionais em balanced/creative
  ↓ nenhum
fallback da seção
  ↓ inválido
fallback do perfil
  ↓ inválido
erro explícito
```

## 16.5 Teste de propriedade

Para cada perfil oficial e seeds de 0 a 9999:

- Prompt positivo não vazio.
- Sem placeholders.
- Seções obrigatórias resolvidas.
- Determinismo em repetição.

---

# 17. Nó principal

## 17.1 Inputs

Visíveis:

- `profile`
- `seed`
- `generation_mode`
- `strict_validation`
- `identity_lock`
- `configuration_json`
- `positive_prefix`
- `positive_suffix`
- `negative_prefix`
- `negative_suffix`

Opcionais/conectáveis:

- `profile_override_json`
- `external_context_json`
- `batch_index`

Confirmar na API V3 atual quais tipos aceitam conexão e widget simultaneamente.

## 17.2 Outputs

- `positive_prompt: STRING`
- `negative_prompt: STRING`
- `manifest_json: STRING`
- `summary: STRING`
- `seed_used: INT`

## 17.3 Cache

Invalidar quando inputs, perfil ou biblioteca mudarem. Não usar `IS_CHANGED = NaN`. Usar hash estável ou mecanismo V3 documentado.

## 17.4 Ajuda

Todos os inputs e outputs possuem tooltips. Adicionar documentação Markdown do nó para exibição na interface.

---

# 18. Frontend

## 18.1 Objetivo

Ocultar a complexidade sem esconder o estado real.

## 18.2 Editor

Botão `Open Architect` abre modal com abas:

- General
- Identity
- Face
- Hair
- Body
- Outfit
- Expression
- Pose
- Scene
- Lighting
- Camera
- Negative
- Rules Summary
- Preview
- Advanced JSON

## 18.3 Fonte de verdade

`configuration_json` armazenado no nó é a fonte de verdade. A UI edita esse JSON, mudanças marcam o workflow como modificado e o estado deve sobreviver a salvar/reabrir.

## 18.4 Preview

Rota:

```text
POST /prompt-architect/preview
```

Recebe perfil, seed, configuração e overrides. Retorna prompts, manifesto, summary e issues. Deve limitar payload, aceitar somente JSON, não aceitar caminho arbitrário e não escrever arquivos.

## 18.5 Validação

```text
POST /prompt-architect/validate
```

Valida sem alterar arquivos.

## 18.6 Listagem

```text
GET /prompt-architect/profiles
GET /prompt-architect/libraries/{id}/options
```

IDs devem estar em allowlist.

## 18.7 Escrita

Não implementar escrita persistente de bibliotecas no MVP. Permitir exportar JSON pelo navegador; escrita no servidor só após revisão de segurança.

---

# 19. Perfis oficiais iniciais

## 19.1 `portrait`

- Retratos fotográficos.
- Enquadramentos controlados.
- Fundo simples.
- Iluminação natural.
- Poses de baixa complexidade.

## 19.2 `virtual-model`

- Identidade bloqueável.
- Realismo sem hiperestilização obrigatória.
- Variação de roupa, pose e cenário.
- Câmera controlada.

## 19.3 `dataset`

- Cobertura de ângulos, expressões e enquadramentos.
- Variação moderada.
- Fundo pouco distrativo.
- Manifesto detalhado.

As bibliotecas oficiais devem evitar conteúdo sexual explícito, menores ambíguos e termos de idade indefinida. Para pessoas, usar `adult` quando necessário.

---

# 20. Biblioteca oficial mínima

Campos:

- `subjects`
- `identity`
- `face`
- `eyes`
- `mouth`
- `skin`
- `hair_color`
- `hair_length`
- `hair_texture`
- `hair_style`
- `body`
- `outfit`
- `expression`
- `pose`
- `location`
- `lighting`
- `camera`
- `composition`
- `quality`
- `negative`

Cada opção deve ter:

- ID.
- Texto.
- Peso.
- Tags.
- Status: `active`, `experimental` ou `deprecated`.
- Regras, quando aplicável.
- `semantic_key`, quando houver equivalentes.

Não copiar listas de terceiros sem licença compatível.

---

# 21. Cache e carregamento

## 21.1 Interface de repositório

```python
class PromptDataRepository(Protocol):
    def list_profiles(self) -> Sequence[ProfileSummary]: ...
    def load_profile(self, profile_id: str) -> ProfileDefinition: ...
    def load_library(self, library_id: str) -> LibraryDefinition: ...
```

## 21.2 Cache

Chave baseada em:

- Caminho resolvido dentro da raiz permitida.
- `mtime_ns`.
- Tamanho.
- Hash de conteúdo quando necessário.

O cache deve ser limpável nos testes.

## 21.3 Precedência

1. Override conectado ao nó.
2. Dados de usuário autorizados.
3. Dados internos oficiais.

Overrides nunca modificam arquivos internos.

---

# 22. Segurança

Checklist obrigatório:

- [ ] Sem `eval`.
- [ ] Sem `exec`.
- [ ] Sem `pickle`.
- [ ] Sem desserialização insegura.
- [ ] Sem instalação dinâmica.
- [ ] Sem subprocessos.
- [ ] Sem download automático.
- [ ] Sem caminhos absolutos da UI.
- [ ] Sem traversal `../`.
- [ ] Limite de tamanho para JSON.
- [ ] Erros sem segredos.
- [ ] Rotas com métodos corretos.
- [ ] Escrita atômica se futuramente habilitada.
- [ ] Dependências mínimas.
- [ ] Licenças verificadas.

---

# 23. Testes

## 23.1 Unitários

Cobrir:

- Seeds e subseeds.
- Seleção ponderada.
- Peso zero e inválido.
- Requisitos e exclusões.
- Implicações e preferências.
- Ciclos.
- Fallbacks.
- Renderização e normalização.
- Deduplicação.
- Validação final.
- Hash e manifesto.

## 23.2 Integração

Cobrir:

- Perfil oficial completo.
- Modos fixed/random/disabled/inherit.
- Locks independentes.
- Prompt negativo.
- Override.
- Configuração inválida.
- Reload após arquivo modificado.
- Adapter do nó sem GPU.

## 23.3 Propriedade

- 10.000 seeds por perfil.
- Determinismo.
- Não vazio.
- Sem placeholder.
- Sem conflito absoluto.
- Sem exceção inesperada.

`hypothesis` pode ser dependência somente de desenvolvimento.

## 23.4 Frontend

- Funções puras de estado.
- Serialização/deserialização.
- Validação de formulário.
- Roteiro manual documentado no ComfyUI.

## 23.5 Smoke test

- Carregar workflow de exemplo.
- Executar sem modelo de difusão, conectando a nó de exibição quando possível.
- Confirmar registro do nó, outputs e preview.

---

# 24. Ferramentas de qualidade

Configurar:

- `ruff` para lint e formatação.
- `mypy` para tipagem.
- `pytest` e `coverage`.
- `build` para empacotamento.
- `hypothesis` e `pre-commit` como opcionais de desenvolvimento.

Regras:

- Dependências de runtime mínimas.
- Dependências de desenvolvimento separadas.
- `requirements.txt` vazio ou mínimo se o core usar stdlib.
- Não assumir ferramentas de desenvolvimento no ambiente do usuário.

---

# 25. Git e contribuição

## 25.1 Fluxo

Preferir trunk-based simples:

1. Branch curta.
2. PR.
3. CI.
4. Squash merge.

Nomes:

- `feat/<nome>`
- `fix/<nome>`
- `docs/<nome>`
- `test/<nome>`

## 25.2 Commits

Conventional Commits:

- `feat:`
- `fix:`
- `docs:`
- `test:`
- `refactor:`
- `chore:`
- `ci:`

## 25.3 Pull requests

Toda PR deve incluir:

- Problema.
- Solução.
- Testes.
- Riscos.
- Screenshots para frontend.
- Documentação afetada.
- Atualização do status durante a fase inicial.

---

# 26. CI/CD

## 26.1 `ci.yml`

Executar em push e PR:

- Checkout.
- Matriz de Python suportada.
- Instalação de dev dependencies.
- `ruff check`.
- `ruff format --check`.
- `mypy`.
- `pytest` com cobertura.
- Build.
- Validação de todos os JSON.
- Teste de 10.000 seeds em job dedicado ou noturno se necessário.

Matriz inicial:

- Ubuntu.
- Windows.
- Versões de Python compatíveis com ComfyUI atual.

## 26.2 `release.yml`

Ao criar tag `v*`:

- Conferir tag e versão.
- Executar CI.
- Gerar artefato.
- Criar GitHub Release.
- Anexar changelog.

## 26.3 `publish-registry.yml`

- Inicialmente somente `workflow_dispatch`.
- Secret `REGISTRY_ACCESS_TOKEN`.
- Publicar apenas após tag aprovada.
- Não publicar automaticamente qualquer mudança no `pyproject.toml` durante desenvolvimento.

---

# 27. Documentação pública

## README

- Problema resolvido.
- Screenshot ou GIF.
- Recursos.
- Instalação pelo Manager/Registry e manual.
- Uso rápido.
- Inputs e outputs.
- Perfis.
- Exemplo de prompt e manifesto.
- Compatibilidade e limitações.
- Contribuição e licença.

## CONTRIBUTING

- Setup.
- Testes.
- Formato de dados.
- Commits e PRs.
- Segurança.

## SECURITY

- Canal de vulnerabilidade.
- Versões suportadas.
- Orientação para não publicar exploit em issue pública.

## CHANGELOG

Keep a Changelog e Semantic Versioning.

## Guia de perfil

Explicar IDs, pesos, tags, regras, fallbacks, templates, versionamento e testes.

---

# 28. Versionamento

- `engine_version` acompanha o pacote.
- `schema_version` evolui separadamente.
- Campo opcional novo: minor do schema.
- Remoção ou mudança semântica: major.
- Dados oficiais sempre declaram versão.
- Não criar framework complexo de migração antes de surgir schema novo; definir interface e erro para versão desconhecida.

---

# 29. Plano de implementação por etapas

A execução deve seguir esta ordem. Não pular etapa sem registrar justificativa e dependências em `PLAN0-STATUS.md`.

## ETAPA 0 — Bootstrap e decisões de projeto

### Objetivo

Criar o repositório profissional e validar o ambiente.

### Ações

1. Criar repositório local e inicializar Git.
2. Confirmar nomes como placeholders.
3. Executar scaffold oficial, se aplicável.
4. Preservar os três arquivos de planejamento.
5. Criar estrutura mínima.
6. Adicionar `.gitignore`, licença, README, changelog, contribuição, segurança e código de conduta.
7. Criar `pyproject.toml`.
8. Definir `0.1.0-dev`.
9. Registrar versões de Python, ComfyUI e frontend.

### Testes

- `python -m compileall prompt_architect`
- `python -c "import prompt_architect"`
- Validação do TOML.

### Aceite

Projeto clonável e core importável sem ComfyUI.

### Commit

`chore: bootstrap Prompt Architect project`

---

## ETAPA 1 — Contratos, schemas e modelos

### Objetivo

Definir dados antes dos algoritmos.

### Ações

1. Criar enums, dataclasses e exceções.
2. Criar schemas JSON.
3. Criar fixtures válidas e inválidas.
4. Implementar parser tipado.
5. Rejeitar campos essenciais ausentes.
6. Definir política de campos desconhecidos.

### Testes

- Perfil mínimo válido.
- Biblioteca válida.
- ID duplicado.
- Peso negativo.
- Fallback inexistente.
- Schema desconhecido.

### Aceite

Dados válidos viram objetos tipados; inválidos falham com erro específico.

### Commit

`feat: define prompt data contracts`

---

## ETAPA 2 — Loader, paths e cache

### Objetivo

Carregar dados com segurança e invalidação.

### Ações

1. Raízes permitidas.
2. Normalização de IDs.
3. Loader JSON.
4. Repository.
5. Cache por metadados/hash.
6. Listagem de perfis.
7. Proteção contra traversal.
8. Reload após mudança.

### Aceite

Perfil carrega e recarrega sem aceitar caminho arbitrário.

### Commit

`feat: add secure prompt data repository`

---

## ETAPA 3 — Seeds e seleção ponderada

### Objetivo

Garantir reprodução e independência por grupo.

### Ações

1. `derive_seed`.
2. Group seeds.
3. `weighted_choice`.
4. Ordem determinística.
5. Modos básicos.
6. Golden tests.
7. Independência de grupos.

### Aceite

Mesma entrada retorna mesma opção; alterar roupa não altera identidade bloqueada.

### Commit

`feat: implement deterministic weighted selection`

---

## ETAPA 4 — Motor de regras

### Objetivo

Impedir combinações incoerentes.

### Ações

1. Operadores.
2. `requires`.
3. `excludes`.
4. `prefer`.
5. `implies`.
6. Prioridades.
7. Ciclos.
8. Registro no manifesto.
9. Conflito entre fixed.
10. Exemplos reais.

### Aceite

Combinações proibidas não aparecem; conflitos fixos falham claramente.

### Commit

`feat: add compatibility rules engine`

---

## ETAPA 5 — Compositor e fallbacks

### Objetivo

Orquestrar seções e impedir lacunas.

### Ações

1. Ordem de seções.
2. Contexto incremental.
3. Limite de tentativas.
4. Relaxamento por modo.
5. Fallback local e global.
6. Registro de tentativas e conflitos.
7. Retorno estruturado.

### Aceite

Toda seção obrigatória é resolvida ou falha explicitamente.

### Commit

`feat: compose structured prompt contexts`

---

## ETAPA 6 — Renderer e normalização

### Objetivo

Gerar texto natural e limpo.

### Ações

1. Template seguro.
2. Frases completas.
3. Placeholders opcionais.
4. Pontuação e espaços.
5. Capitalização.
6. `a`/`an`.
7. Deduplicação.
8. Testes de snapshots.

### Aceite

Prompts oficiais não contêm frases coladas, placeholders ou pontuação quebrada.

### Commit

`feat: render and normalize natural prompts`

---

## ETAPA 7 — Validação final e manifesto

### Objetivo

Garantir integridade e rastreabilidade.

### Ações

1. Issues estruturadas.
2. Severidades.
3. Validação de contexto e resultado.
4. Manifesto e hash.
5. Summary.
6. Prompt negativo.
7. Prefixos e sufixos.
8. Snapshots.

### Aceite

Prompts, manifesto e diagnóstico são válidos; prompt vazio é impossível silenciosamente.

### Commit

`feat: validate outputs and build prompt manifest`

---

## ETAPA 8 — Perfis e bibliotecas oficiais

### Objetivo

Entregar conteúdo funcional para demonstração.

### Ações

1. Perfis `portrait`, `virtual-model` e `dataset`.
2. Bibliotecas mínimas.
3. Regras de cabelo, roupa e cenário.
4. Pesos naturais.
5. Fallbacks.
6. Revisão de licença.
7. Teste de 10.000 seeds.

### Aceite

Cada perfil produz 10.000 prompts válidos sem erro inesperado.

### Commit

`feat: add official prompt profiles and libraries`

---

## ETAPA 9 — Adapter ComfyUI API V3

### Objetivo

Expor o motor como custom node.

### Ações

1. Extensão V3.
2. Schema do nó.
3. Inputs e outputs.
4. Tooltips.
5. Conversão de erros.
6. Export do frontend.
7. Invalidação de cache.
8. Teste dentro do ComfyUI.
9. Help page.

### Aceite

Nó aparece, executa sem GPU e retorna cinco outputs válidos.

### Commit

`feat: expose Prompt Architect ComfyUI node`

---

## ETAPA 10 — Frontend mínimo

### Objetivo

Criar experiência centralizada inicial.

### Ações

1. Registrar extensão JS.
2. Botão `Open Architect`.
3. Modal.
4. Formulário básico.
5. Persistência em `configuration_json`.
6. Dirty state do workflow.
7. Erros e preview.
8. CSS compatível com tema.

### Aceite

Configuração editada no modal sobrevive ao salvar e reabrir workflow.

### Commit

`feat: add centralized prompt editor UI`

---

## ETAPA 11 — Rotas de preview e validação

### Objetivo

Feedback imediato sem enfileirar workflow.

### Ações

1. Rotas GET seguras.
2. Preview e validate POST.
3. Limite de payload.
4. Respostas padronizadas.
5. Erros HTTP.
6. Testes de ID inválido, payload excessivo e concorrência básica.
7. Nenhuma escrita persistente.

### Aceite

Preview e validação funcionam sem alterar arquivos.

### Commit

`feat: add prompt preview and validation API`

---

## ETAPA 12 — Interface avançada

### Objetivo

Expor controle por seção e grupo.

### Ações

1. Abas.
2. Modos por campo.
3. Valores e tags.
4. Locks e seeds.
5. Preview do manifesto.
6. Advanced JSON sincronizado.
7. Reset por perfil.
8. Import/export.
9. Acessibilidade.
10. Loading e erro.

### Aceite

Usuário cria configuração completa sem editar JSON manualmente.

### Commit

`feat: complete Prompt Architect visual editor`

---

## ETAPA 13 — Qualidade, CI e integração

### Objetivo

Tornar o projeto confiável para público e contribuições.

### Ações

1. Ruff, mypy, pytest e coverage.
2. CI Linux/Windows.
3. Property tests.
4. Smoke tests.
5. Validação de dados.
6. Pre-commit opcional.
7. Medição de performance.
8. Matriz suportada.

### Aceite

CI verde, cobertura alvo e 10.000 seeds aprovadas.

### Commit

`ci: enforce cross-platform quality checks`

---

## ETAPA 14 — Documentação e exemplos

### Objetivo

Permitir instalação e uso sem assistência do autor.

### Ações

1. README completo.
2. Screenshots.
3. Workflows básico e modelo virtual.
4. Exemplo de perfil.
5. Regras e troubleshooting.
6. Desenvolvimento, contribuição e segurança.
7. Revisão de inglês e links.

### Aceite

Pessoa nova instala e gera o primeiro prompt somente com o README.

### Commit

`docs: publish complete user and contributor guides`

---

## ETAPA 15 — Beta público 0.9.0

### Objetivo

Preparar e testar a distribuição pública.

### Ações

1. Revisar `pyproject.toml`.
2. Preencher Publisher ID.
3. Validar licença e metadata.
4. Criar ícone/banner.
5. Changelog e tag beta.
6. GitHub Release.
7. Instalação limpa.
8. Teste Manager/Registry.
9. Corrigir bloqueadores.

### Aceite

Instalação limpa funciona e não há bloqueador conhecido.

### Commit

`chore: prepare 0.9.0 public beta`

---

## ETAPA 16 — Release 1.0.0

### Objetivo

Publicar versão estável.

### Ações

1. Fechar bugs críticos e altos.
2. Congelar schema 1.0.
3. Rodar matriz completa.
4. Rodar 10.000 seeds por perfil.
5. Revisar segurança e docs.
6. Atualizar changelog e versão.
7. Tag `v1.0.0`.
8. GitHub Release.
9. Publicar no Registry.
10. Criar roadmap pós-1.0 separado.

### Aceite

Todos os itens de release readiness estão concluídos.

### Commit

`chore: release Prompt Architect 1.0.0`

---

# 30. Protocolo obrigatório de execução pelo agente

Antes de qualquer alteração:

1. Ler `AGENTS.md`.
2. Ler a etapa relevante de `PLAN0.md`.
3. Ler `PLAN0-STATUS.md`.
4. Selecionar a primeira etapa `PENDING` cujas dependências estejam concluídas.
5. Marcar a etapa como `IN_PROGRESS`.
6. Registrar data, branch e objetivo.
7. Implementar o menor conjunto completo da etapa.
8. Executar testes.
9. Atualizar documentação afetada.
10. Atualizar `PLAN0-STATUS.md`.
11. Marcar `DONE` somente se todos os critérios forem atendidos.
12. Registrar commit ou PR real.

O agente não deve:

- Marcar tarefa como concluída sem teste.
- Alterar o plano para esconder trabalho incompleto.
- Ignorar erro de lint ou tipagem sem registrar justificativa.
- Inserir TODO sem registrar dívida técnica.
- Inventar compatibilidade ou resultado de teste.
- Publicar release sem autorização explícita.
- Adicionar dependência sem justificativa no status.

---

# 31. Definition of Done por etapa

Uma etapa só está `DONE` quando:

- Código implementado.
- Testes relevantes criados.
- Testes executados e registrados.
- Lint executado.
- Tipagem executada quando configurada.
- Documentação atualizada.
- Nenhum erro crítico conhecido.
- Critérios de aceite conferidos.
- `PLAN0-STATUS.md` atualizado.
- Commit preparado ou realizado.

---

# 32. Critérios de release 1.0

## Funcional

- [ ] Nó principal funciona.
- [ ] Preview funciona.
- [ ] Configuração persiste no workflow.
- [ ] Locks funcionam.
- [ ] Seeds são determinísticas.
- [ ] Regras e fallbacks funcionam.
- [ ] Prompt positivo nunca é vazio silenciosamente.
- [ ] Manifesto é completo.
- [ ] Três perfis oficiais funcionam.

## Qualidade

- [ ] CI verde.
- [ ] Core com cobertura >= 90%.
- [ ] Projeto com cobertura >= 80%.
- [ ] 10.000 seeds por perfil.
- [ ] Windows e Linux testados.
- [ ] Sem `eval`/`exec`.
- [ ] Sem instalação em runtime.
- [ ] Sem vulnerabilidade crítica conhecida.

## Público

- [ ] README completo.
- [ ] LICENSE.
- [ ] CONTRIBUTING.
- [ ] SECURITY.
- [ ] CHANGELOG.
- [ ] Workflow de exemplo.
- [ ] Ícone e banner.
- [ ] Metadata do Registry.
- [ ] Instalação limpa validada.

---

# 33. Decisões técnicas fixadas

1. API V3 desde o início.
2. Core Python independente de ComfyUI.
3. JSON como formato oficial.
4. Sem dependências obrigatórias de outros custom nodes.
5. Core preferencialmente stdlib.
6. Seed por grupo.
7. Manifesto sempre gerado.
8. Fallback explícito.
9. Sem linguagem de expressão arbitrária.
10. Interface edita configuração serializada no nó.
11. Preview por rota local somente leitura.
12. Escrita persistente fora do MVP.
13. GitHub público e preparação para Registry.
14. Segurança alinhada aos padrões do ComfyUI.

Qualquer mudança deve ser registrada no Decision Log de `PLAN0-STATUS.md`.

---

# 34. Referências técnicas oficiais

O agente deve verificar a documentação atual antes de implementar assinaturas de API:

- Custom Nodes Overview: `https://docs.comfy.org/custom-nodes/overview`
- V3 Migration: `https://docs.comfy.org/custom-nodes/v3_migration`
- JavaScript Extensions: `https://docs.comfy.org/custom-nodes/js/javascript_overview`
- Routes: `https://docs.comfy.org/development/comfyui-server/comms_routes`
- Node Help Pages: `https://docs.comfy.org/custom-nodes/help_page`
- Registry Specifications: `https://docs.comfy.org/registry/specifications`
- Publishing Nodes: `https://docs.comfy.org/registry/publishing`
- Registry Standards: `https://docs.comfy.org/registry/standards`
- Custom Node CI/CD: `https://docs.comfy.org/registry/cicd`

A documentação atual prevalece quando uma assinatura tiver mudado. A arquitetura, requisitos e critérios de produto deste plano continuam sendo a fonte de verdade.
