# Local preview API

Prompt Architect exposes a versioned, read-only API on the same ComfyUI origin. It does not queue
workflows, write files, or access the network.

## Endpoints

- `GET /prompt_architect/v1/profiles` lists valid bundled profiles.
- `GET /prompt_architect/v1/profiles/{profile_id}` returns sections and selectable options for one
  validated kebab-case profile ID.
- `POST /prompt_architect/v1/preview` composes a deterministic preview.
- `POST /prompt_architect/v1/validate` validates the same configuration without returning prompt
  text or the complete manifest.

POST bodies are JSON objects containing either a complete configuration directly or under a
`configuration` key. The maximum request size is 262,144 bytes. Successful responses use
`{"ok":true,"data":...}`; errors use
`{"ok":false,"error":{"code":"...","message":"..."}}` with an appropriate HTTP status.

Example:

```json
{
  "configuration": {
    "schema_version": "1.0",
    "profile_id": "portrait",
    "profile_version": "1.0.0",
    "mode": "balanced",
    "master_seed": 7,
    "groups": {"identity": {"locked": true, "seed": 123}},
    "fields": {},
    "overrides": {},
    "batch_index": 0
  }
}
```
