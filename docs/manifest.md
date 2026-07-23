# Validação, manifesto e diagnósticos

O pipeline valida seções obrigatórias e regras absolutas antes de renderizar. Depois verifica prompt
positivo significativo, comprimento, quantidade de seções, placeholders, sentinelas e negativo
obrigatório. Um erro impede a saída e identifica campo e motivo.

O manifesto V2 registra:

- versões do engine, perfil, catálogo, bibliotecas e packs;
- configuração efetiva e hash SHA-256;
- master seed, group seeds e batch index;
- opção, pack, família, facets, tags, variante e origem por seção;
- se a seção foi realmente renderizada;
- regras, conflitos, fallbacks, tentativas e avisos;
- prompts positivo e negativo finais.

O JSON usa ordenação canônica e proíbe NaN. Mesma versão, configuração e seed produzem bytes
idênticos. Omissões adaptativas são visíveis pelo campo `rendered: false` e por um aviso.

Manifestos antigos sem catálogo permanecem no schema `1.0`; composições Catalog V2 usam schema
`2.0`.
