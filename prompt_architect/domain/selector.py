"""Deterministic weighted choice and basic section mode resolution."""

import math
import random
from collections.abc import Sequence
from typing import Protocol, TypeVar

from prompt_architect.domain.enums import FieldMode, SelectionSource
from prompt_architect.domain.exceptions import ConfigurationError, SelectionError
from prompt_architect.domain.models import (
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
        for option in sorted(options, key=lambda candidate: candidate.id)
        if not include.difference(option.tags) and not exclude.intersection(option.tags)
    )


def select_basic_option(
    section: SectionDefinition,
    library: LibraryDefinition,
    profile: ProfileDefinition,
    configuration: NodeConfiguration,
) -> SelectedValue | None:
    """Resolve disabled, fixed, random, and inherited modes before compatibility rules."""
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
