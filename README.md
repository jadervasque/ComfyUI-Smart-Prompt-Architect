# Prompt Architect

[![CI](https://github.com/jadervasque/ComfyUI-Smart-Prompt-Architect/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/jadervasque/ComfyUI-Smart-Prompt-Architect/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-0B7285.svg)](LICENSE)

Prompt Architect is a ComfyUI API V3 custom node for deterministic, structured prompt composition.
It turns validated profiles and catalogs into coherent positive and negative prompts, preserves
user-fixed values, and records every decision in a reproducible manifest.

The project includes a visual editor, local preview API, 15 official profiles, five generation
modes, and Catalog V2: 81 segmented packs, 69 dimensions, 5,184 semantic options, and 15,552
deterministic text variants. Selection, compatibility, rendering, and validation run in a
framework-independent Python core.

> New here? Start with the [complete user manual in Portuguese](MANUAL.md), or follow the quick
> start below.

## Why Prompt Architect

- **Reproducible:** the same data version, profile, configuration, seed, and batch index produce
	the same result.
- **Coherent:** values are selected and checked for compatibility before text is rendered.
- **Controllable:** fields can be inherited, randomized, fixed, customized, disabled, or grouped
	under deterministic locks.
- **Observable:** each composition returns a manifest, summary, effective seed, and diagnostics.
- **Safe by design:** no network access, package installation, dynamic code execution, or arbitrary
	filesystem access occurs while the node composes a prompt.
- **Self-contained:** no other custom node is required for the composition engine.

## Installation

Clone the repository into the ComfyUI `custom_nodes` directory:

```console
cd ComfyUI/custom_nodes
git clone https://github.com/jadervasque/ComfyUI-Smart-Prompt-Architect.git
```

Restart ComfyUI after installation. To update an existing checkout:

```console
cd ComfyUI/custom_nodes/ComfyUI-Smart-Prompt-Architect
git pull --ff-only
```

The node has no third-party runtime dependency. Python 3.10 or newer is required by the package
metadata.

## Quick Start

1. Open ComfyUI and add **Prompt Architect** from `Prompt Architect -> Generation`.
2. Select the `portrait-core` profile and keep `balanced` mode for a first composition.
3. Choose a non-negative seed and open **Open Architect**.
4. In **Preview & JSON**, select **Generate preview** and review both prompts.
5. Select **Save configuration** to persist the editor state in the workflow.
6. Connect `positive_prompt` and `negative_prompt` to the corresponding CLIP text encoders.

The node returns five outputs:

| Output | Purpose |
|---|---|
| `positive_prompt` | Final structured positive prompt. |
| `negative_prompt` | Context-aware negative prompt. |
| `manifest_json` | Machine-readable record of selections and diagnostics. |
| `summary` | Compact human-readable composition summary. |
| `seed_used` | Effective master seed used by the composition. |

For every input, editor tab, connection recipe, advanced JSON option, and troubleshooting path,
see the [user manual](MANUAL.md).

## Profiles And Generation Modes

The 15 included profiles cover general and professional portraits, virtual models, balanced
datasets, editorial and full-body fashion, lifestyle, street and studio photography, cinematic
and fine-art portraits, historical scenes, fantasy, atmospheric horror, and conceptual work.

| Mode | Best suited for |
|---|---|
| `strict` | Conservative output with no optional-filter relaxation. |
| `balanced` | General use with weighted hierarchical selection. |
| `creative` | Deterministically increasing the relative chance of rare options. |
| `dataset` | Uniform coverage for dataset generation. |
| `sequential` | Stable traversal controlled by the batch index. |

Read [official profiles](docs/official-profiles.md) and [generation modes](docs/generation-modes.md)
for their complete contracts and recommendations.

## How It Works

The pipeline resolves field modes and locks, selects compatible structured values, applies rules,
validates the context, renders and normalizes text, validates the final prompt, and produces the
manifest. It never silently discards a fixed user value or returns an empty positive prompt.

Catalog and profile data are validated JSON. The core remains independent from ComfyUI and the
frontend, which keeps the engine testable and allows integrations to share the same behavior.
See [architecture](docs/architecture.md), [determinism](docs/determinism.md), and
[configuration](docs/configuration.md) for the detailed model.

## Documentation

The README is the project entry point; the following guides provide complete reference material.

### Users

| Guide | Contents |
|---|---|
| [User manual](MANUAL.md) | Installation, first workflow, all controls, recipes, and troubleshooting. |
| [Configuration](docs/configuration.md) | Configuration contract, field modes, locks, seeds, and overrides. |
| [Official profiles](docs/official-profiles.md) | Included profiles, intended use, and recommendations. |
| [Generation modes](docs/generation-modes.md) | Strict, balanced, creative, dataset, and sequential behavior. |
| [Generated examples](docs/generated-examples.md) | Representative deterministic outputs and manifests. |
| [Content safety](docs/content-safety.md) | Safety model, limits, and catalog policy. |
| [Manifest and diagnostics](docs/manifest.md) | Output schema, provenance, decisions, and diagnostics. |

### Architecture And Data

| Guide | Contents |
|---|---|
| [Architecture](docs/architecture.md) | Components, boundaries, and composition pipeline. |
| [Catalog V2](docs/catalog-v2.md) | Catalog structure, packs, dimensions, and selection model. |
| [Catalog compatibility](docs/catalog-compatibility.md) | V1/V2 compatibility and migration guarantees. |
| [Catalog metrics](docs/catalog-metrics.md) | Audited catalog size, coverage, and quality metrics. |
| [Data loading](docs/data-loading.md) | Offline repository, validation, cache, and path restrictions. |
| [Creating packs](docs/creating-packs.md) | Authoring and validating reusable catalog packs. |
| [Rules](docs/rules.md) | Compatibility, exclusion, preference, and implication rules. |
| [Rendering](docs/rendering.md) | Templates, text variants, normalization, and output constraints. |
| [Determinism](docs/determinism.md) | Seed derivation and reproducibility guarantees. |

### Integration And Development

| Guide | Contents |
|---|---|
| [Preview API](docs/API.md) | Local preview and validation endpoints. |
| [Development guide](docs/DEVELOPMENT.md) | Environment, validation commands, CI, and project structure. |
| [Examples](examples/README.md) | Example assets and their intended use. |
| [Contributing](CONTRIBUTING.md) | Contribution workflow, commits, tests, and pull requests. |
| [Security policy](SECURITY.md) | Supported versions and private vulnerability reporting. |
| [Changelog](CHANGELOG.md) | Version history and notable changes. |

## Development

Create a development environment and install the optional tooling:

```console
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

Run the principal quality gates before opening a pull request:

```console
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest
python -m scripts.validate_data
python -m scripts.validate_catalog_semantics
python -m tests.property_profiles
```

Additional audits, benchmark commands, package validation, and platform notes are documented in
the [development guide](docs/DEVELOPMENT.md). Contributions are welcome through focused branches
and pull requests; review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

## Project Status

The core engine, ComfyUI API V3 node, visual editor, local preview API, official profiles, Catalog
V2, tests, and cross-platform CI are implemented in the public repository. Tagged releases and
Comfy Registry distribution are announced separately when available; the repository does not
claim an unpublished release.

## Security

Do not disclose vulnerabilities in a public issue. Follow [SECURITY.md](SECURITY.md) for supported
versions and private reporting instructions.

## License

Licensed under the [Apache License 2.0](LICENSE).
