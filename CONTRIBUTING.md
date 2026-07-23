# Contributing

Thank you for helping build Prompt Architect. Before starting substantial work, open or reference
an issue that defines the problem, expected behavior, and acceptance criteria. Keep each change
focused enough to review and validate independently.

## Development

1. Create a short branch such as `feat/weighted-selection`.
2. Create a virtual environment with Python 3.10 or newer.
3. Install development tools with `python -m pip install -e ".[dev]"`.
4. Keep the domain core independent of ComfyUI and frontend modules.
5. Add tests and update documentation with behavior changes.
6. Run lint, formatting, typing, tests, and build checks before opening a pull request.

Use Conventional Commits. Do not add runtime dependencies without documenting the reason and
tradeoffs in the pull request. Public API or schema behavior changes require explicit versioning.

## Safety constraints

Profile and library data must remain declarative JSON. Do not introduce `eval`, `exec`, `pickle`,
subprocess execution, runtime installation, network access during node execution, or arbitrary
filesystem paths. Fixed user values must never be silently discarded, and a positive prompt must
never be returned empty without an explicit error.

## Pull requests

Describe the problem, implementation, tests, risks, documentation impact, and any frontend visual
changes. Target `master`, wait for all required checks to pass, and merge only after the change is
ready for publication. Do not publish releases or Registry packages without explicit owner
authorization.
