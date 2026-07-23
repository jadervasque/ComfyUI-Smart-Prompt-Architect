"""Canonical configuration serialization, manifest construction, and summaries."""

import json
from collections.abc import Mapping
from types import MappingProxyType

from prompt_architect.domain.models import (
    LibraryDefinition,
    NodeConfiguration,
    ProfileDefinition,
    PromptManifest,
    RenderedPrompt,
    SelectionResult,
)
from prompt_architect.domain.renderer import selected_variant_id
from prompt_architect.infrastructure.hashing import canonical_json_hash
from prompt_architect.version import __version__


def configuration_data(configuration: NodeConfiguration) -> dict[str, object]:
    """Serialize effective configuration to stable JSON-compatible primitives."""
    return {
        "schema_version": configuration.schema_version,
        "profile_id": configuration.profile_id,
        "profile_version": configuration.profile_version,
        "mode": configuration.mode.value,
        "master_seed": configuration.master_seed,
        "batch_index": configuration.batch_index,
        "groups": {
            key: {"locked": value.locked, "seed": value.seed}
            for key, value in sorted(configuration.groups.items())
        },
        "fields": {
            key: {
                "mode": value.mode.value,
                "value": value.value,
                "include_tags": list(value.include_tags),
                "exclude_tags": list(value.exclude_tags),
            }
            for key, value in sorted(configuration.fields.items())
        },
        "overrides": dict(sorted(configuration.overrides.items())),
    }


def build_manifest(
    profile: ProfileDefinition,
    libraries: Mapping[str, LibraryDefinition],
    configuration: NodeConfiguration,
    selection: SelectionResult,
    rendered: RenderedPrompt,
) -> PromptManifest:
    """Build an immutable complete reproducibility record."""
    effective = configuration_data(configuration)
    selections: dict[str, Mapping[str, object]] = {}
    for section_id in profile.section_order:
        selected = selection.context.selections.get(section_id)
        if selected is None:
            continue
        selections[section_id] = MappingProxyType(
            {
                "option_id": selected.option.id,
                "pack_id": selected.option.pack_id,
                "raw_text": selected.option.text,
                "rendered_text": rendered.rendered_sections.get(section_id, ""),
                "rendered": bool(rendered.rendered_sections.get(section_id, "")),
                "tags": selected.option.tags,
                "family": selected.option.family,
                "facets": selected.option.facets,
                "semantic_key": selected.option.semantic_key,
                "variant_id": selected_variant_id(profile, selection, selected),
                "source": selected.source.value,
                "fallback": selected.fallback_used,
            }
        )
    versions = {library.id: library.version for library in libraries.values()}
    catalog_versions = {
        library.catalog_version
        for library in libraries.values()
        if library.catalog_version is not None
    }
    catalog_version = next(iter(catalog_versions)) if len(catalog_versions) == 1 else None
    pack_versions = {
        pack_id: version
        for library in libraries.values()
        for pack_id, version in library.pack_versions.items()
    }
    omitted = tuple(
        section_id
        for section_id in profile.section_order
        if section_id in selection.context.selections
        and not rendered.rendered_sections.get(section_id, "")
    )
    warnings = selection.warnings
    if omitted:
        warnings = (
            *warnings,
            "rendering omitted selected sections: " + ", ".join(omitted),
        )
    return PromptManifest(
        schema_version="2.0" if catalog_version is not None else "1.0",
        engine_version=__version__,
        profile_id=profile.id,
        profile_version=profile.version,
        library_versions=MappingProxyType(dict(sorted(versions.items()))),
        configuration_hash=canonical_json_hash(effective),
        effective_configuration=MappingProxyType(effective),
        master_seed=configuration.master_seed,
        group_seeds=selection.group_seeds,
        selections=MappingProxyType(selections),
        applied_rules=selection.applied_rules,
        resolved_conflicts=selection.resolved_conflicts,
        fallbacks=selection.fallbacks,
        attempts=selection.attempts,
        warnings=warnings,
        positive_prompt=rendered.positive,
        negative_prompt=rendered.negative,
        catalog_version=catalog_version,
        pack_versions=MappingProxyType(dict(sorted(pack_versions.items()))),
    )


def manifest_data(manifest: PromptManifest) -> dict[str, object]:
    """Convert a manifest to stable JSON-compatible primitives."""
    data: dict[str, object] = {
        "schema_version": manifest.schema_version,
        "engine_version": manifest.engine_version,
        "profile": {"id": manifest.profile_id, "version": manifest.profile_version},
        "libraries": dict(manifest.library_versions),
        "configuration_hash": manifest.configuration_hash,
        "effective_configuration": _json_value(manifest.effective_configuration),
        "master_seed": manifest.master_seed,
        "group_seeds": dict(manifest.group_seeds),
        "selections": _json_value(manifest.selections),
        "applied_rules": list(manifest.applied_rules),
        "resolved_conflicts": list(manifest.resolved_conflicts),
        "fallbacks": list(manifest.fallbacks),
        "attempts": dict(manifest.attempts),
        "warnings": list(manifest.warnings),
        "positive_prompt": manifest.positive_prompt,
        "negative_prompt": manifest.negative_prompt,
    }
    if manifest.catalog_version is not None:
        data["catalog_version"] = manifest.catalog_version
        data["packs"] = dict(manifest.pack_versions)
    return data


def manifest_json(manifest: PromptManifest) -> str:
    """Serialize a manifest canonically for deterministic workflow output."""
    return json.dumps(
        manifest_data(manifest),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def build_summary(
    profile: ProfileDefinition, configuration: NodeConfiguration, selection: SelectionResult
) -> str:
    """Build a concise diagnostic summary without logging full prompts."""
    generated = len(selection.context.selections)
    attempts = sum(selection.attempts.values())
    return (
        f"Profile {profile.id}@{profile.version}; seed {configuration.master_seed}; "
        f"sections {generated}/{len(profile.sections)}; attempts {attempts}; "
        f"fallbacks {len(selection.fallbacks)}; warnings {len(selection.warnings)}"
    )


def _json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value
