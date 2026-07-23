"""Structured selection compositor with retries, rule application, and fallbacks."""

import random
from collections.abc import Mapping
from types import MappingProxyType

from prompt_architect.domain.enums import FieldMode, GenerationMode, SelectionSource
from prompt_architect.domain.exceptions import (
    ConfigurationError,
    RuleConflictError,
    SelectionError,
)
from prompt_architect.domain.models import (
    FieldConfiguration,
    LibraryDefinition,
    NodeConfiguration,
    ProfileDefinition,
    SelectedValue,
    SelectionContext,
    SelectionResult,
)
from prompt_architect.domain.rules import (
    apply_implications,
    compatible_options,
    option_violations,
    validate_context_rules,
)
from prompt_architect.domain.seeds import derive_section_seed, resolve_group_seeds
from prompt_architect.domain.selector import (
    custom_option,
    effective_field_configuration,
    eligible_by_mode,
    eligible_by_tags,
    hierarchical_choice,
)


def compose_selection(
    profile: ProfileDefinition,
    libraries: Mapping[str, LibraryDefinition],
    configuration: NodeConfiguration,
) -> SelectionResult:
    """Resolve every section or fail explicitly without rendering text."""
    _validate_configuration_profile(profile, configuration)
    section_libraries = _section_libraries(profile, libraries)
    effective_fields = {
        section_id: effective_field_configuration(profile.sections[section_id], configuration)
        for section_id in profile.section_order
    }
    fixed_fields = frozenset(
        section_id
        for section_id, field in effective_fields.items()
        if field.mode in {FieldMode.FIXED, FieldMode.CUSTOM}
    )
    selections = _resolve_user_values(profile, section_libraries, effective_fields)
    context = _context(profile, configuration, selections, fixed_fields)
    fixed_implications = apply_implications(context, section_libraries)
    context = fixed_implications.context
    group_seeds = resolve_group_seeds(profile, configuration)
    attempts: dict[str, int] = {section_id: 0 for section_id in profile.section_order}
    applied_rules: list[str] = list(fixed_implications.applied_rules)
    resolved_conflicts: list[str] = list(fixed_implications.resolved_conflicts)
    fallbacks: list[str] = []
    warnings: list[str] = []

    for section_id in profile.section_order:
        section = profile.sections[section_id]
        field = effective_fields[section_id]
        existing = context.selections.get(section_id)
        if field.mode is FieldMode.DISABLED:
            if section.required:
                raise ConfigurationError(f"required section {section_id!r} cannot be disabled")
            if existing is not None:
                raise RuleConflictError(
                    f"disabled section {section_id!r} received implied value {existing.option.id!r}"
                )
            warnings.append(f"section {section_id} disabled")
            continue
        if existing is not None:
            if field.mode is FieldMode.FIXED and existing.option.id != field.value:
                raise RuleConflictError(
                    f"fixed section {section_id!r} was changed to {existing.option.id!r}"
                )
            if (
                field.mode is FieldMode.CUSTOM
                and existing.option.text != (field.value or "").strip()
            ):
                raise RuleConflictError(f"custom section {section_id!r} was changed")
            continue
        context, attempt_count, events, conflicts, relaxed = _select_random_section(
            section_id,
            profile,
            section_libraries,
            configuration,
            field,
            context,
            group_seeds[section.group],
        )
        attempts[section_id] = attempt_count
        applied_rules.extend(events)
        resolved_conflicts.extend(conflicts)
        if relaxed:
            warnings.append(f"section {section_id} relaxed optional tag filters")
        if section_id not in context.selections:
            context, fallback_event, events, conflicts = _apply_fallback(
                section_id,
                profile,
                section_libraries,
                context,
            )
            fallbacks.append(fallback_event)
            applied_rules.extend(events)
            resolved_conflicts.extend(conflicts)

    missing = [
        section_id
        for section_id in profile.section_order
        if profile.sections[section_id].required and section_id not in context.selections
    ]
    if missing:
        raise SelectionError(f"required sections unresolved: {', '.join(missing)}")
    violations = validate_context_rules(context)
    if violations:
        raise SelectionError("final context violates absolute rules: " + "; ".join(violations))
    return SelectionResult(
        context=context,
        group_seeds=group_seeds,
        attempts=MappingProxyType(attempts),
        applied_rules=tuple(applied_rules),
        resolved_conflicts=tuple(resolved_conflicts),
        fallbacks=tuple(fallbacks),
        warnings=tuple(warnings),
    )


def _validate_configuration_profile(
    profile: ProfileDefinition, configuration: NodeConfiguration
) -> None:
    if configuration.profile_id != profile.id:
        raise ConfigurationError(
            f"configuration profile {configuration.profile_id!r} does not match {profile.id!r}"
        )
    if configuration.profile_version not in {None, profile.version}:
        raise ConfigurationError(
            f"configuration expects profile version {configuration.profile_version!r}, "
            f"loaded {profile.version!r}"
        )
    unknown_fields = set(configuration.fields) - set(profile.sections)
    if unknown_fields:
        raise ConfigurationError(
            "configuration contains unknown fields: " + ", ".join(sorted(unknown_fields))
        )


def _section_libraries(
    profile: ProfileDefinition, libraries: Mapping[str, LibraryDefinition]
) -> Mapping[str, LibraryDefinition]:
    result: dict[str, LibraryDefinition] = {}
    for section_id in profile.section_order:
        library_id = profile.sections[section_id].library
        library = libraries.get(library_id)
        if library is None:
            raise SelectionError(f"section {section_id!r} requires missing library {library_id!r}")
        result[section_id] = library
    return MappingProxyType(result)


def _resolve_user_values(
    profile: ProfileDefinition,
    libraries: Mapping[str, LibraryDefinition],
    fields: Mapping[str, FieldConfiguration],
) -> dict[str, SelectedValue]:
    selections: dict[str, SelectedValue] = {}
    for section_id in profile.section_order:
        field = fields[section_id]
        if field.mode is FieldMode.CUSTOM:
            selections[section_id] = SelectedValue(
                section_id,
                custom_option(section_id, field),
                SelectionSource.CUSTOM,
            )
            continue
        if field.mode is not FieldMode.FIXED:
            continue
        if field.value is None:
            raise ConfigurationError(f"fixed section {section_id!r} requires a value")
        option = libraries[section_id].option_by_id(field.value)
        if option is None:
            raise ConfigurationError(
                f"fixed section {section_id!r} references unknown option {field.value!r}"
            )
        selections[section_id] = SelectedValue(section_id, option, SelectionSource.FIXED)
    return selections


def _select_random_section(
    section_id: str,
    profile: ProfileDefinition,
    libraries: Mapping[str, LibraryDefinition],
    configuration: NodeConfiguration,
    field: FieldConfiguration,
    context: SelectionContext,
    group_seed: int,
) -> tuple[SelectionContext, int, tuple[str, ...], tuple[str, ...], bool]:
    if field.mode not in {FieldMode.RANDOM, FieldMode.INHERIT}:
        return context, 0, (), (), False
    library = libraries[section_id]
    filtered = eligible_by_mode(
        eligible_by_tags(library.options, field),
        configuration.mode,
    )
    candidates = compatible_options(filtered, context)
    candidates = tuple(option for option in candidates if option.weight > 0)
    relaxed = False
    if not candidates and configuration.mode in {GenerationMode.BALANCED, GenerationMode.CREATIVE}:
        candidates = compatible_options(
            eligible_by_mode(library.options, configuration.mode),
            context,
        )
        candidates = tuple(option for option in candidates if option.weight > 0)
        relaxed = bool(field.include_tags or field.exclude_tags)
    if not candidates:
        return context, 0, (), (), relaxed
    # Content composition uses deterministic non-cryptographic pseudo-randomness.
    rng = random.Random(  # noqa: S311
        derive_section_seed(group_seed, section_id, configuration.batch_index)
    )
    remaining = list(candidates)
    attempts = 0
    rejected: list[str] = []
    while remaining and attempts < profile.max_selection_attempts:
        attempts += 1
        candidate = hierarchical_choice(
            remaining,
            rng,
            configuration.mode,
            sequence_index=configuration.batch_index + attempts - 1,
        )
        remaining = [option for option in remaining if option.id != candidate.id]
        tentative_selections = dict(context.selections)
        tentative_selections[section_id] = SelectedValue(
            section_id, candidate, SelectionSource.RANDOM
        )
        tentative = _copy_context(context, tentative_selections)
        try:
            implication = apply_implications(
                tentative,
                libraries,
                initial_fields=(section_id,),
            )
        except RuleConflictError as error:
            rejected.append(f"{section_id}:{candidate.id} rejected: {error}")
            continue
        violations = validate_context_rules(implication.context)
        if violations:
            rejected.append(f"{section_id}:{candidate.id} rejected: {'; '.join(violations)}")
            continue
        return (
            implication.context,
            attempts,
            tuple((*rejected, *implication.applied_rules)),
            implication.resolved_conflicts,
            relaxed,
        )
    return context, attempts, tuple(rejected), (), relaxed


def _apply_fallback(
    section_id: str,
    profile: ProfileDefinition,
    libraries: Mapping[str, LibraryDefinition],
    context: SelectionContext,
) -> tuple[SelectionContext, str, tuple[str, ...], tuple[str, ...]]:
    section = profile.sections[section_id]
    library = libraries[section_id]
    fallback_id = (
        section.fallback or profile.profile_fallbacks.get(section_id) or library.fallback_option_id
    )
    if fallback_id is None:
        if section.required:
            raise SelectionError(
                f"required section {section_id!r} has no valid candidate or fallback"
            )
        return context, f"section {section_id} omitted without fallback", (), ()
    option = library.option_by_id(fallback_id)
    if option is None:
        raise SelectionError(f"fallback {fallback_id!r} for section {section_id!r} does not exist")
    violations = option_violations(option, context)
    if violations:
        raise SelectionError(
            f"fallback {fallback_id!r} for section {section_id!r} violates rules: "
            + "; ".join(violations)
        )
    selections = dict(context.selections)
    selections[section_id] = SelectedValue(
        section_id, option, SelectionSource.FALLBACK, fallback_used=True
    )
    implication = apply_implications(
        _copy_context(context, selections),
        libraries,
        initial_fields=(section_id,),
    )
    return (
        implication.context,
        f"section {section_id} used fallback {fallback_id}",
        implication.applied_rules,
        implication.resolved_conflicts,
    )


def _context(
    profile: ProfileDefinition,
    configuration: NodeConfiguration,
    selections: Mapping[str, SelectedValue],
    fixed_fields: frozenset[str],
) -> SelectionContext:
    return SelectionContext(
        selections=MappingProxyType(dict(selections)),
        fixed_fields=fixed_fields,
        profile_metadata=profile.metadata,
        generation_mode=configuration.mode,
    )


def _copy_context(
    context: SelectionContext, selections: Mapping[str, SelectedValue]
) -> SelectionContext:
    return SelectionContext(
        selections=MappingProxyType(dict(selections)),
        fixed_fields=context.fixed_fields,
        profile_metadata=context.profile_metadata,
        generation_mode=context.generation_mode,
    )
