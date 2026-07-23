# Dados empacotados

- `catalogs/index.json`: índice Catalog V2.
- `catalogs/packs/<domínio>/*.json`: 81 packs oficiais segmentados.
- `profiles/*.json`: 15 perfis oficiais.
- `schemas/*-2.0.schema.json`: contratos públicos V2.
- `libraries/*.json`: bibliotecas legadas 1.0 mantidas apenas para leitura compatível.

Os dados V2 são gerados de vocabulários autorais revisáveis em `scripts/generate_catalog.py`.
Geração é uma ação offline de desenvolvimento; nunca ocorre durante a execução do nó.

Valide com:

```console
python -m scripts.validate_data
python -m scripts.validate_catalog_semantics
python -m scripts.catalog_stats
python -m scripts.find_catalog_duplicates
```
