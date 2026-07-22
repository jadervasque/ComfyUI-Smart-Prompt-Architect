# Prompt Architect

Prompt Architect is a planned ComfyUI custom node for deterministic, structured prompt
composition. It will select compatible values before rendering text, preserve user-fixed values,
record every choice in a manifest, and fail clearly instead of returning an empty positive prompt.

The project is in pre-alpha bootstrap development. The ComfyUI node and user interface are not
implemented yet.

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

The public product name, repository name, Registry ID, and publisher metadata remain working names
or placeholders until the owner confirms them. No release or Registry publication is authorized by
this repository state.

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE).
