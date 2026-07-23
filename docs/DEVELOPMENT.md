# Development and quality

Prompt Architect supports CPython 3.10 through 3.13 on current Windows and Linux runners. The
runtime package has no third-party dependencies; development tools are isolated in the `dev`
extra.

```shell
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest --cov=prompt_architect --cov-report=term-missing
node --test tests/frontend/state.test.mjs
python -m scripts.validate_data
python -m tests.property_profiles
python -m scripts.benchmark
python -m build
```

The CI matrix runs Python 3.10, 3.12, and 3.13 on Ubuntu and Windows. It requires at least 80%
coverage for the package and 90% for the core domain/application layers. A separate job composes
10,000 seeds per official profile twice for deterministic property validation. The optional local
pre-commit configuration runs lint, format, type, Python unit, and frontend state checks.

## ComfyUI smoke test

Start a local ComfyUI with this repository under `custom_nodes`, open a workflow containing
`Prompt Architect`, and verify:

1. `/object_info/PromptArchitect_PromptArchitect` returns the node definition.
2. `Open Architect` opens the editor and a server preview succeeds without queueing.
3. Saving and reopening the workflow preserves `configuration_json`.
4. Executing the node without model or GPU connections returns all five outputs.

The development baseline verified here is ComfyUI 0.27.0 with frontend 1.45.20 on Windows. CI
also checks framework-independent code on Linux; a full Linux ComfyUI integration run remains a
release-readiness requirement until performed in a real ComfyUI installation.
