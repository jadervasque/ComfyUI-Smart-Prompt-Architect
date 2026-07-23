"""Application service for the complete deterministic composition pipeline."""

from collections.abc import Mapping

from prompt_architect.domain.engine import compose_selection
from prompt_architect.domain.exceptions import ConfigurationError
from prompt_architect.domain.manifest import build_manifest, build_summary, manifest_json
from prompt_architect.domain.models import (
    CompositionResult,
    LibraryDefinition,
    NodeConfiguration,
    ProfileDefinition,
    RenderedPrompt,
)
from prompt_architect.domain.normalizer import normalize_prompt
from prompt_architect.domain.renderer import render_selection
from prompt_architect.domain.validator import raise_for_errors, validate_context, validate_final
from prompt_architect.infrastructure.repository import PromptDataRepository

_OVERRIDE_KEYS = frozenset(
    {"positive_prefix", "positive_suffix", "negative_prefix", "negative_suffix"}
)


def compose_prompt(
    profile: ProfileDefinition,
    libraries: Mapping[str, LibraryDefinition],
    configuration: NodeConfiguration,
) -> CompositionResult:
    """Compose, render, validate, and manifest one prompt without framework dependencies."""
    selection = compose_selection(profile, libraries, configuration)
    context_issues = validate_context(profile, selection)
    raise_for_errors(context_issues)
    rendered = _apply_overrides(render_selection(profile, selection), configuration)
    final_issues = validate_final(profile, rendered)
    issues = (*context_issues, *final_issues)
    raise_for_errors(issues)
    manifest = build_manifest(profile, libraries, configuration, selection, rendered)
    return CompositionResult(
        rendered=rendered,
        manifest=manifest,
        manifest_json=manifest_json(manifest),
        summary=build_summary(profile, configuration, selection),
        seed_used=configuration.master_seed,
        issues=issues,
    )


class ComposeService:
    """Load referenced data and invoke the pure composition pipeline."""

    def __init__(self, repository: PromptDataRepository) -> None:
        self._repository = repository

    def compose(self, configuration: NodeConfiguration) -> CompositionResult:
        """Compose from a validated portable node configuration."""
        profile = self._repository.load_profile(configuration.profile_id)
        library_ids = sorted({section.library for section in profile.sections.values()})
        libraries = {
            library_id: self._repository.load_library_for_profile(profile, library_id)
            for library_id in library_ids
        }
        return compose_prompt(profile, libraries, configuration)


def _apply_overrides(rendered: RenderedPrompt, configuration: NodeConfiguration) -> RenderedPrompt:
    unknown = set(configuration.overrides) - _OVERRIDE_KEYS
    if unknown:
        raise ConfigurationError("unknown prompt overrides: " + ", ".join(sorted(unknown)))
    positive = _join_parts(
        configuration.overrides.get("positive_prefix", ""),
        rendered.positive,
        configuration.overrides.get("positive_suffix", ""),
    )
    negative = _join_parts(
        configuration.overrides.get("negative_prefix", ""),
        rendered.negative,
        configuration.overrides.get("negative_suffix", ""),
    )
    return RenderedPrompt(positive, negative, rendered.rendered_sections)


def _join_parts(*parts: str) -> str:
    return normalize_prompt(". ".join(part.strip(" .") for part in parts if part.strip()))
