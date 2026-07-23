"""Deterministic weighted choice and basic section mode resolution."""

import math
import random
from collections.abc import Sequence
from dataclasses import replace
from typing import Protocol, TypeVar

from prompt_architect.domain.enums import (
    FieldMode,
    GenerationMode,
    OptionStatus,
    SelectionSource,
)
from prompt_architect.domain.exceptions import ConfigurationError, SelectionError
from prompt_architect.domain.models import (
    MAX_CUSTOM_TEXT_CHARACTERS,
    FieldConfiguration,
    LibraryDefinition,
    NodeConfiguration,
    ProfileDefinition,
    PromptOption,
    SectionDefinition,
    SelectedValue,
)
from prompt_architect.domain.seeds import derive_section_seed, resolve_group_seeds


class WeightedCandidate(Protocol):
    """Minimum stable contract accepted by weighted choice."""

    @property
    def id(self) -> str:
        """Stable candidate ID."""
        ...

    @property
    def weight(self) -> float:
        """Finite non-negative selection weight."""
        ...


_Candidate = TypeVar("_Candidate", bound=WeightedCandidate)


def weighted_choice(candidates: Sequence[_Candidate], rng: random.Random) -> _Candidate:
    """Select by finite non-negative weight after stable ID sorting."""
    ordered = sorted(candidates, key=lambda candidate: candidate.id)
    if not ordered:
        raise SelectionError("weighted choice requires at least one candidate")
    for candidate in ordered:
        if not math.isfinite(candidate.weight) or candidate.weight < 0:
            raise SelectionError(
                f"candidate {candidate.id!r} has invalid weight {candidate.weight!r}"
            )
    enabled = [candidate for candidate in ordered if candidate.weight > 0]
    total = sum(candidate.weight for candidate in enabled)
    if not enabled or not math.isfinite(total) or total <= 0:
        raise SelectionError("weighted choice has no candidate with positive finite weight")
    threshold = rng.random() * total
    cumulative = 0.0
    for candidate in enabled:
        cumulative += candidate.weight
        if threshold < cumulative:
            return candidate
    return enabled[-1]


def hierarchical_choice(
    candidates: Sequence[PromptOption],
    rng: random.Random,
    mode: GenerationMode,
    *,
    sequence_index: int = 0,
) -> PromptOption:
    """Choose a semantic family first so synonym-rich packs cannot dominate."""
    ordered = _stable_options(candidates)
    if not ordered:
        raise SelectionError("hierarchical choice requires at least one candidate")
    if not any(option.family for option in ordered):
        return weighted_choice(ordered, rng)
    families: dict[str, list[PromptOption]] = {}
    for option in ordered:
        families.setdefault(option.family or option.id, []).append(option)
    family_ids = sorted(families)
    if mode is GenerationMode.SEQUENTIAL:
        family_index = sequence_index % len(family_ids)
        family = families[family_ids[family_index]]
        option_index = (sequence_index // len(family_ids)) % len(family)
        return family[option_index]
    if mode is GenerationMode.DATASET:
        family = families[family_ids[rng.randrange(len(family_ids))]]
        return family[rng.randrange(len(family))]
    family_options = tuple(
        PromptOption(
            id=family_id,
            text=family_id,
            weight=_family_weight(families[family_id], mode),
        )
        for family_id in family_ids
    )
    chosen_family = weighted_choice(family_options, rng).id
    transformed = tuple(_with_mode_weight(option, mode) for option in families[chosen_family])
    return weighted_choice(transformed, rng)


def _family_weight(options: Sequence[PromptOption], mode: GenerationMode) -> float:
    enabled = [_mode_weight(option.weight, mode) for option in options if option.weight > 0]
    return sum(enabled) / len(enabled) if enabled else 0.0


def _with_mode_weight(option: PromptOption, mode: GenerationMode) -> PromptOption:
    return replace(option, weight=_mode_weight(option.weight, mode))


def _mode_weight(weight: float, mode: GenerationMode) -> float:
    if mode is GenerationMode.CREATIVE:
        return math.sqrt(weight)
    if mode is GenerationMode.STRICT:
        return math.pow(weight, 1.25)
    return weight


def effective_field_configuration(
    section: SectionDefinition, configuration: NodeConfiguration
) -> FieldConfiguration:
    """Resolve a node override or inherit the profile section defaults."""
    override = configuration.fields.get(section.id)
    if override is None or override.mode is FieldMode.INHERIT:
        return FieldConfiguration(mode=section.mode, value=section.default)
    return override


def eligible_by_tags(
    options: Sequence[PromptOption], field: FieldConfiguration
) -> tuple[PromptOption, ...]:
    """Apply deterministic include/exclude tag filters."""
    include = frozenset(field.include_tags)
    exclude = frozenset(field.exclude_tags)
    return tuple(
        option
        for option in _stable_options(options)
        if option.status is not OptionStatus.DEPRECATED
        and not include.difference(option.tags)
        and not exclude.intersection(option.tags)
    )


def eligible_by_mode(
    options: Sequence[PromptOption], mode: GenerationMode
) -> tuple[PromptOption, ...]:
    """Apply mode-specific lifecycle policy before compatibility rules."""
    return tuple(
        option
        for option in options
        if option.status is not OptionStatus.DEPRECATED
        and not (mode is GenerationMode.STRICT and option.status is OptionStatus.EXPERIMENTAL)
    )


def _stable_options(options: Sequence[PromptOption]) -> tuple[PromptOption, ...]:
    values = tuple(options)
    if all(values[index - 1].id <= values[index].id for index in range(1, len(values))):
        return values
    return tuple(sorted(values, key=lambda candidate: candidate.id))


def custom_option(section_id: str, field: FieldConfiguration) -> PromptOption:
    """Create a safe synthetic option for user-authored section text."""
    value = (field.value or "").strip()
    if not value:
        raise ConfigurationError(f"custom section {section_id!r} requires non-empty text")
    if len(value) > MAX_CUSTOM_TEXT_CHARACTERS:
        raise ConfigurationError(
            f"custom section {section_id!r} cannot exceed {MAX_CUSTOM_TEXT_CHARACTERS} characters"
        )
    return PromptOption(id="custom", text=value)


def select_basic_option(
    section: SectionDefinition,
    library: LibraryDefinition,
    profile: ProfileDefinition,
    configuration: NodeConfiguration,
) -> SelectedValue | None:
    """Resolve disabled, fixed, custom, random, and inherited modes before rules."""
    field = effective_field_configuration(section, configuration)
    if field.mode is FieldMode.DISABLED:
        if section.required:
            raise ConfigurationError(f"required section {section.id!r} cannot be disabled")
        return None
    if field.mode is FieldMode.FIXED:
        if field.value is None:
            raise ConfigurationError(f"fixed section {section.id!r} requires a value")
        option = library.option_by_id(field.value)
        if option is None:
            raise ConfigurationError(
                f"fixed section {section.id!r} references unknown option {field.value!r}"
            )
        return SelectedValue(section.id, option, SelectionSource.FIXED)
    if field.mode is FieldMode.CUSTOM:
        return SelectedValue(
            section.id,
            custom_option(section.id, field),
            SelectionSource.CUSTOM,
        )
    if field.mode is not FieldMode.RANDOM:
        raise ConfigurationError(f"section {section.id!r} has unresolved inherit mode")
    candidates = eligible_by_tags(library.options, field)
    group_seeds = resolve_group_seeds(profile, configuration)
    group_seed = group_seeds[section.group]
    # Reproducible content selection is intentionally non-cryptographic.
    rng = random.Random(  # noqa: S311
        derive_section_seed(group_seed, section.id, configuration.batch_index)
    )
    option = weighted_choice(candidates, rng)
    return SelectedValue(section.id, option, SelectionSource.RANDOM)
