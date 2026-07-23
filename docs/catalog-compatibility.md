# Compatibilidade do catálogo

Schemas usam `major.minor`; conteúdo usa SemVer completo.

- Correção textual sem alterar sentido: patch do pack.
- Nova opção, variante ou pack compatível: minor do catálogo e do perfil afetado.
- Remoção, mudança de ID, mudança de fallback ou semântica: major.
- Mudança de comportamento público do perfil: versão do perfil.
- Mudança de campos do manifesto: novo schema do manifesto.

IDs e `semantic_key` não devem ser reaproveitados com outro significado. Depreque primeiro com
`status: deprecated` e peso `0.0`; remova somente em major.

Perfis V2 fixam `catalog_version`, `enabled_packs` e classes de segurança. Um perfil não carrega
silenciosamente outro catálogo. O manifesto registra todas as versões necessárias para reproduzir
a composição.

Bibliotecas 1.0 ainda podem ser lidas em dados conectados. Elas não são misturadas automaticamente
com packs V2 dentro de um perfil V2.
