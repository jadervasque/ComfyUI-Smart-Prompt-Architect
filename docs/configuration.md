# Configuration contracts

Prompt Architect 1.0 uses strict, versioned JSON for profiles, libraries, node configuration, and
manifests. Unknown fields are rejected so misspellings and future semantic changes cannot be
silently ignored. The executable parser uses only the Python standard library; JSON Schema files
under `prompt_architect/data/schemas` document the interoperable shape.

All IDs use lowercase kebab-case. Schema version `1.0` is currently the only accepted version.
Profile and library versions use semantic version syntax. Weights must be finite and non-negative;
zero disables an option during random selection. Library fallback IDs must resolve inside the same
library.

Node configuration is portable JSON. It stores a profile ID and version, generation mode, master
seed, optional group locks/seeds, per-field modes and tag filters, and prompt prefix/suffix
overrides. It does not contain absolute filesystem paths.

The parser rejects unknown schema versions, missing required fields, duplicate option IDs,
unresolved local fallbacks, invalid operators, non-finite weights, and unsupported template
placeholders. Cross-library references are validated by the repository after all required data has
been loaded.
