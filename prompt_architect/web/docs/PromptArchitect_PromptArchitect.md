# Prompt Architect

Compose deterministic positive and negative prompts from validated profiles and libraries. The node
runs on CPU, does not load a model, and performs no network or arbitrary filesystem access.

## Inputs

- **profile**: bundled profile ID.
- **seed**: master seed. Group and section seeds derive from it with SHA-256.
- **generation mode**: compatibility/diversity strategy.
- **strict validation**: retained for workflow clarity; mandatory anti-empty checks always run.
- **identity lock**: stabilizes identity with an explicit derived group seed.
- **configuration JSON**: portable advanced state. Unknown fields are rejected.
- **prefix/suffix inputs**: appended around generated positive or negative content.
- **profile override JSON**: optional declarative profile object, never a path or code.
- **external context JSON**: optional object of section ID to fixed option ID.
- **batch index**: explicit index for dataset/sequential workflows.

## Outputs

The node returns positive prompt, negative prompt, canonical manifest JSON, diagnostic summary, and
the master seed used. A positive prompt is never returned empty silently; invalid fixed/custom values,
rules, fallbacks, templates, or final text stop execution with a clear error.
