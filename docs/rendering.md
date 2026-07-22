# Rendering and normalization

Rendering receives an already validated structured context. Templates support only exact named
placeholders; attribute access, indexing, conversions, and format specifications are rejected.
Missing optional sections become empty text, while missing required placeholders raise a
`RenderError` before any prompt is returned.

Option wording prefers a weighted deterministic variant, then `sentence`, then `text`. Variant
selection derives a stable seed below the option's group. Fragments are deduplicated by normalized
exact text and optional `semantic_key`, preserving the first section in profile order.

The English normalizer conservatively collapses spaces, fixes spacing around punctuation, removes
duplicate punctuation and sentences, capitalizes sentence starts, optionally converts textual `+`
to `and`, and corrects basic `a`/`an` cases. It is intentionally not presented as a universal
grammar engine.
