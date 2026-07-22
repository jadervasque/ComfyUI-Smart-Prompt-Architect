# Contributing

Thank you for helping build Prompt Architect. The project is currently driven by
`plans/PLAN0.md`; consult `plans/PLAN0-STATUS.md` before starting work so changes follow the next
eligible stage.

## Development

1. Create a short branch such as `feat/weighted-selection`.
2. Create a virtual environment with Python 3.10 or newer.
3. Install development tools with `python -m pip install -e ".[dev]"`.
4. Keep the domain core independent of ComfyUI and frontend modules.
5. Add tests and update documentation with behavior changes.
6. Run lint, formatting, typing, tests, and build checks before opening a pull request.

Use Conventional Commits. Do not add runtime dependencies without documenting the reason in
`plans/PLAN0-STATUS.md`. Public API or schema behavior changes require explicit versioning.

## Safety constraints

Profile and library data must remain declarative JSON. Do not introduce `eval`, `exec`, `pickle`,
subprocess execution, runtime installation, network access during node execution, or arbitrary
filesystem paths. Fixed user values must never be silently discarded, and a positive prompt must
never be returned empty without an explicit error.

## Pull requests

Describe the problem, implementation, tests, risks, documentation impact, and any frontend visual
changes. Do not publish releases or Registry packages without explicit owner authorization.
