# Official profiles and content

The bundled `portrait`, `virtual-model`, and `dataset` profiles contain original Prompt Architect
wording released under this repository's Apache-2.0 license. They avoid explicit sexual content,
ambiguous age language, and third-party prompt lists. Human subjects are explicitly adults.

- `portrait` favors controlled photographic portraits, simple settings, natural light, and
  low-complexity poses.
- `virtual-model` exposes a lockable identity group while outfit, pose, location, lighting, camera,
  and composition vary independently.
- `dataset` keeps identity and quality fixed while an explicit seed/batch index varies framing,
  expression, pose, outfit, and background without hidden state.

Twenty field libraries cover subjects, identity, face, eyes, mouth, skin, hair color/length/texture/
style, body, outfit, expression, pose, location, lighting, camera, composition, quality, and
negative terms. Every option declares ID, original text, finite weight, tags, and lifecycle status;
every library and required section has an explicit fallback.

Hair styles can require a compatible prior hair length. A seated pose excludes the evening dress,
an urban location prefers casual clothing, and overcast daylight requires the outdoor location.
These rules demonstrate compatibility without arbitrary expressions or forward-order ambiguity.

Run `python -m tests.property_profiles` for the dedicated 10,000-seed-per-profile determinism and
non-empty prompt check.
