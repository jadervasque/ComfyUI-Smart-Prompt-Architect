# Validation, manifests, and diagnostics

The final pipeline validates required structured sections and absolute rules before rendering, then
checks the final positive and negative prompts. A positive prompt must contain meaningful text,
meet profile character and section thresholds, contain no residual placeholders or null-like
sentinels, and never consist only of punctuation. A profile may require a non-empty negative
prompt. Errors are returned as structured issues and raised as one clear
`FinalPromptValidationError` before output.

Positive and negative prefix/suffix overrides are joined around generated content; they never
replace it. Unknown override keys fail as configuration errors. All parts are normalized after
joining.

Every successful composition produces canonical JSON with schema/engine/profile/library versions,
the complete effective configuration and SHA-256 hash, master and group seeds, per-section option
and provenance, rule/conflict/fallback events, attempts, warnings, and both final prompts. Keys are
sorted and NaN is forbidden, so identical inputs produce byte-identical manifest JSON. The summary
reports profile, seed, section/attempt/fallback/warning counts without including full prompt text.
