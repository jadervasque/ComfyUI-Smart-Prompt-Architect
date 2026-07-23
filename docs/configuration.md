# Configuration contracts

Prompt Architect uses strict, versioned JSON for profiles, libraries, node configuration, and
manifests. Unknown fields are rejected so misspellings and future semantic changes cannot be
silently ignored. The executable parser uses only the Python standard library; JSON Schema files
under `prompt_architect/data/schemas` document the interoperable shape.

All IDs use lowercase kebab-case. Profiles, libraries, and manifests use schema `1.0`. New node
configurations use schema `1.1`; legacy configuration `1.0` remains readable and is upgraded by the
visual editor. Profile and library versions use semantic version syntax. Weights must be finite and
non-negative; zero disables an option during random selection. Library fallback IDs must resolve
inside the same library.

Node configuration is portable JSON. It stores a profile ID and version, generation mode, master
seed, optional group locks/seeds, per-field modes and tag filters, and prompt prefix/suffix
overrides. It does not contain absolute filesystem paths.

Configuration schema `1.1` adds field mode `custom`. In this mode, `value` is user-authored prompt
text instead of a library option ID. The text must be non-empty, is trimmed, is limited to 4,096
characters, and is stored directly in the workflow. Custom values are deterministic, appear in the
manifest with source `custom`, and cannot be silently replaced by implications. Tag filters do not
select or rewrite custom text.

```json
{
  "schema_version": "1.1",
  "profile_id": "virtual-model",
  "profile_version": "1.0.0",
  "mode": "balanced",
  "master_seed": 42,
  "fields": {
    "outfit": {
      "mode": "custom",
      "value": "They wear a bespoke emerald coat with brass buttons"
    }
  }
}
```

The parser rejects unknown schema versions, missing required fields, duplicate option IDs,
unresolved local fallbacks, invalid operators, non-finite weights, and unsupported template
placeholders. Cross-library references are validated by the repository after all required data has
been loaded.
