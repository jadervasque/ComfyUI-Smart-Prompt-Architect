# Exemplos de configuração

Configuração mínima do perfil geral:

```json
{
  "schema_version": "1.1",
  "profile_id": "portrait-core",
  "profile_version": "2.0.0",
  "mode": "balanced",
  "master_seed": 42,
  "batch_index": 0
}
```

Dataset com ciclo reproduzível:

```json
{
  "schema_version": "1.1",
  "profile_id": "dataset-balanced",
  "profile_version": "2.0.0",
  "mode": "dataset",
  "master_seed": 100,
  "batch_index": 100,
  "groups": {
    "identity": { "locked": true, "seed": 9001 }
  }
}
```

Texto livre para um grupo, sem editar o catálogo:

```json
{
  "schema_version": "1.1",
  "profile_id": "editorial-fashion",
  "profile_version": "2.0.0",
  "mode": "balanced",
  "master_seed": 77,
  "fields": {
    "wardrobe-theme": {
      "mode": "custom",
      "value": "adult contemporary tailoring in emerald and charcoal"
    }
  }
}
```

Não inclua caminhos absolutos: configurações são portáteis e referenciam somente IDs.
