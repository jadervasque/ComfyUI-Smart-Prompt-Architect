# Criação de packs

Packs oficiais são arquivos JSON V2 sob `prompt_architect/data/catalogs/packs/<domínio>/`.

## Passo a passo

1. Defina uma única dimensão observável.
2. Escolha um ID kebab-case globalmente estável.
3. Declare biblioteca lógica, domínio, categoria, versão, idioma, estado e segurança.
4. Escreva opções originais com uma semântica por item.
5. Forneça de duas a cinco variantes, `semantic_key`, família, facets, tags, peso e fallback.
6. Adicione regras declarativas somente quando a coerência exigir.
7. Registre o pack e seu caminho relativo em `catalogs/index.json`.
8. Habilite-o em pelo menos um perfil compatível.
9. Execute todos os audits.

Exemplo reduzido:

```json
{
  "schema_version": "2.0",
  "id": "scene-example",
  "version": "2.0.0",
  "library": "example-setting",
  "domain": "scene",
  "category": "setting",
  "language": "en",
  "status": "active",
  "safety": "general",
  "tags": ["example"],
  "fallback_option_id": "scene-example-quiet-courtyard",
  "options": [
    {
      "id": "scene-example-quiet-courtyard",
      "semantic_key": "scene-example-quiet-courtyard",
      "text": "a quiet courtyard with balanced depth",
      "sentence": "A quiet courtyard with balanced depth.",
      "variants": [
        { "id": "plain", "text": "a quiet courtyard with balanced depth" },
        { "id": "observed", "text": "showing a quiet courtyard with balanced depth" }
      ],
      "weight": 1.0,
      "status": "active",
      "family": "scene-example-courtyard",
      "tags": ["scene", "setting"],
      "facets": { "place": "courtyard", "layout": "balanced-depth" },
      "subcategory": "courtyard",
      "intensity": "moderate",
      "safety": "general",
      "join_hint": "sentence"
    }
  ]
}
```

Não use nomes de artistas, celebridades, marcas, personagens ou texto copiado. Não crie itens cuja
única diferença seja pontuação ou sinônimo sem mudança semântica.

## Nova dimensão sem mudar o core

Crie o pack, adicione uma biblioteca lógica no índice e uma seção de mesmo propósito no perfil.
O engine trabalha com contratos genéricos; nenhuma alteração Python é necessária enquanto a nova
dimensão usar os operadores e metadados existentes.
