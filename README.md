# Prompt Architect

Prompt Architect is a ComfyUI API V3 custom node for deterministic, structured prompt composition.
It selects compatible values before rendering text, preserves user-fixed values, records every
choice in a manifest, and fails clearly instead of returning an empty positive prompt.

The node and its visual editor are implemented. Search for **Prompt Architect** under
`Prompt Architect → Generation`. See the step-by-step [Portuguese user manual](MANUAL.md) for every
input, output, editor tab, profile, recipe, and troubleshooting procedure.

## Design goals

- Deterministic output for the same profile, configuration, engine version, and seed.
- A pure-Python core that can be imported and tested without ComfyUI.
- Public ComfyUI API V3 integration.
- Validated JSON profiles and libraries with no runtime code execution.
- No network access, package installation, or arbitrary filesystem access while composing.
- Explicit fallbacks, errors, diagnostics, and manifests.

## Development setup

Python 3.10 or newer is required by the project metadata. The bootstrap was validated locally with
Python 3.12.10, ComfyUI 0.27.0, and the ComfyUI frontend requirement 1.45.20 on Windows. This records
the development environment; it is not yet a complete compatibility claim.

```console
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest
python -m build
```

The core package can be checked independently:

```console
python -m compileall prompt_architect
python -c "import prompt_architect; print(prompt_architect.__version__)"
```

Implementation is governed by [plans/PLAN0.md](plans/PLAN0.md), with execution evidence in
[plans/PLAN0-STATUS.md](plans/PLAN0-STATUS.md).

## Status

The core, ComfyUI node, visual editor, preview API, official profiles, and cross-platform CI are
implemented. Registry publisher metadata and a tagged release remain pending; no Registry or
release publication is authorized by this repository state.

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE).
