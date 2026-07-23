# Secure data loading

Prompt Architect reads only `<authorized-root>/profiles/<validated-id>.json` and
`<authorized-root>/libraries/<validated-id>.json`. IDs must be lowercase kebab-case and are never
accepted as paths. Categories are allowlisted, resolved paths are checked against their root, JSON
is limited to 1 MiB by default, and duplicate keys, invalid UTF-8, non-finite constants, and
non-object roots are rejected.

Precedence is deterministic: connected in-memory overrides, explicitly authorized user roots in
configuration order, then packaged official data. An invalid higher-precedence file fails clearly;
it does not silently fall back to a different source. Diagnostics use relative source labels and do
not expose absolute host paths.

The cache key includes the resolved authorized path, nanosecond modification time, byte size, and
SHA-256 content hash. This detects content changes even when filesystem metadata is preserved. The
cache stores only immutable parsed objects and can be cleared explicitly.
