# Determinism and selection

Prompt Architect never uses the module-level random generator or Python's process-randomized
`hash()`. It derives unsigned 64-bit subseeds from SHA-256 over `<seed>:<namespace>` and creates a
dedicated `random.Random` instance for each section.

Group seeds are independent namespaces. An explicit seed on a locked group wins; otherwise the
group seed derives from the master seed. Section and explicit batch indexes derive below the group,
so selection order and unrelated groups cannot change an existing result. Candidates and tags are
sorted before deterministic operations.

Weighted choice rejects negative, NaN, and infinite weights. Zero-weight options are disabled, and
an all-zero candidate set raises an explicit selection error so a higher layer can apply a declared
fallback. Fixed option IDs and custom user text are resolved before random fields and are never
replaced silently. Required
fields cannot be disabled.
