"""Safe compatibility rules without an expression language."""

import math
from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from types import MappingProxyType

from prompt_architect.domain.enums import GenerationMode, RuleOperator, RuleType, SelectionSource
from prompt_architect.domain.exceptions import RuleConflictError
from prompt_architect.domain.models import (
    LibraryDefinition,
    PromptOption,
    Rule,
    RuleCondition,
    SelectedValue,
    SelectionContext,
)


@dataclass(frozen=True, slots=True)
class RuleApplicationResult:
    """Updated context plus stable diagnostic events."""

    context: SelectionContext
    applied_rules: tuple[str, ...]
    resolved_conflicts: tuple[str, ...]


def evaluate_condition(condition: RuleCondition, context: SelectionContext) -> bool:
    """Evaluate one allowlisted operator against safe structured sources."""
    present, value, tags = _context_value(condition.field, context)
    expected = condition.value
    if condition.operator is RuleOperator.MISSING:
        return not present
    if condition.operator is RuleOperator.PRESENT:
        return present
    if condition.operator is RuleOperator.CONTAINS_TAG:
        return isinstance(expected, str) and expected in tags
    if condition.operator is RuleOperator.EQUALS:
        return present and value == expected
    if condition.operator is RuleOperator.NOT_EQUALS:
        return not present or value != expected
    if condition.operator is RuleOperator.IN:
        return present and _contains(expected, value)
    if condition.operator is RuleOperator.NOT_IN:
        return not present or not _contains(expected, value)
    raise RuleConflictError(f"unsupported rule operator {condition.operator!s}")


def option_violations(option: PromptOption, context: SelectionContext) -> tuple[str, ...]:
    """Return failed requirements and active exclusions for one candidate."""
    violations: list[str] = []
    for rule in option.rules:
        if rule.condition is None:
            continue
        matched = evaluate_condition(rule.condition, context)
        if rule.type is RuleType.REQUIRES and not matched:
            violations.append(
                f"{option.id}: unmet requirement {_describe_condition(rule.condition)}"
            )
        elif rule.type is RuleType.EXCLUDES and matched:
            violations.append(f"{option.id}: excluded by {_describe_condition(rule.condition)}")
    return tuple(violations)


def compatible_options(
    options: Sequence[PromptOption], context: SelectionContext
) -> tuple[PromptOption, ...]:
    """Filter absolute rules and apply deterministic preference multipliers."""
    ordered = tuple(options)
    if not all(ordered[index - 1].id <= ordered[index].id for index in range(1, len(ordered))):
        ordered = tuple(sorted(ordered, key=lambda item: item.id))
    if not any(option.rules for option in ordered):
        return ordered
    compatible: list[PromptOption] = []
    for option in ordered:
        if option_violations(option, context):
            continue
        multiplier = preference_multiplier(option, context)
        compatible.append(replace(option, weight=option.weight * multiplier))
    return tuple(compatible)


def preference_multiplier(option: PromptOption, context: SelectionContext) -> float:
    """Combine matching preferences with mode-specific influence."""
    multiplier = 1.0
    for rule in option.rules:
        if (
            rule.type is RuleType.PREFER
            and rule.condition is not None
            and evaluate_condition(rule.condition, context)
        ):
            influence = rule.multiplier
            if context.generation_mode is GenerationMode.CREATIVE:
                influence = math.sqrt(influence)
            elif context.generation_mode in {
                GenerationMode.DATASET,
                GenerationMode.SEQUENTIAL,
            }:
                influence = 1.0
            elif context.generation_mode is GenerationMode.STRICT:
                influence = influence**1.25
            multiplier *= influence
    return multiplier


def apply_implications(
    context: SelectionContext,
    libraries_by_section: Mapping[str, LibraryDefinition],
    *,
    max_depth: int = 32,
    initial_fields: Sequence[str] | None = None,
) -> RuleApplicationResult:
    """Apply implications transitively, preserving fixed fields and detecting cycles."""
    if max_depth <= 0:
        raise ValueError("max_depth must be positive")
    selections = dict(context.selections)
    queue = deque(initial_fields if initial_fields is not None else selections)
    unknown_initial = set(queue) - set(selections)
    if unknown_initial:
        raise RuleConflictError(
            "implication sources are unresolved: " + ", ".join(sorted(unknown_initial))
        )
    applied: list[str] = []
    conflicts: list[str] = []
    history = {(field, selected.option.id) for field, selected in selections.items()}
    depth = 0
    while queue:
        source_field = queue.popleft()
        source = selections[source_field]
        for rule in source.option.rules:
            if rule.type is not RuleType.IMPLIES:
                continue
            depth += 1
            if depth > max_depth:
                raise RuleConflictError(f"implication depth exceeds safe limit {max_depth}")
            target_field, target_value = _implication_target(rule, source.option.id)
            target_option = _target_option(libraries_by_section, target_field, target_value)
            existing = selections.get(target_field)
            event = f"{source_field}:{source.option.id} implies {target_field}:{target_value}"
            if existing is not None and existing.option.id == target_value:
                applied.append(f"{event} (already satisfied)")
                continue
            if existing is not None and target_field in context.fixed_fields:
                raise RuleConflictError(
                    f"{event} conflicts with user-locked value {existing.option.id!r}"
                )
            if (target_field, target_value) in history:
                raise RuleConflictError(f"implication cycle detected while applying {event}")
            if existing is not None:
                conflicts.append(
                    f"{target_field}:{existing.option.id} replaced by implied {target_value}"
                )
            selections[target_field] = SelectedValue(
                section_id=target_field,
                option=target_option,
                source=SelectionSource.IMPLIED,
            )
            history.add((target_field, target_value))
            queue.append(target_field)
            applied.append(event)
    updated = SelectionContext(
        selections=MappingProxyType(selections),
        fixed_fields=context.fixed_fields,
        profile_metadata=context.profile_metadata,
        generation_mode=context.generation_mode,
    )
    return RuleApplicationResult(updated, tuple(applied), tuple(conflicts))


def validate_context_rules(context: SelectionContext) -> tuple[str, ...]:
    """Return absolute rule violations remaining in a resolved context."""
    violations: list[str] = []
    for field in sorted(context.selections):
        option = context.selections[field].option
        if option.rules:
            violations.extend(option_violations(option, context))
    return tuple(violations)


def _context_value(
    field: str, context: SelectionContext
) -> tuple[bool, object | None, tuple[str, ...]]:
    if field == "generation-mode":
        return True, context.generation_mode.value, ()
    selected = context.selections.get(field)
    if selected is not None:
        return True, selected.option.id, selected.option.tags
    if field in context.profile_metadata:
        return True, context.profile_metadata[field], ()
    return False, None, ()


def _contains(container: object, value: object) -> bool:
    if isinstance(container, (tuple, list, frozenset, set)):
        return value in container
    return False


def _describe_condition(condition: RuleCondition) -> str:
    return f"{condition.field} {condition.operator.value} {condition.value!r}"


def _implication_target(rule: Rule, source_id: str) -> tuple[str, str]:
    if rule.target_field is None or rule.target_value is None:
        raise RuleConflictError(f"option {source_id!r} contains an incomplete implication")
    return rule.target_field, rule.target_value


def _target_option(
    libraries: Mapping[str, LibraryDefinition], field: str, value: str
) -> PromptOption:
    library = libraries.get(field)
    if library is None:
        raise RuleConflictError(f"implication targets unknown field {field!r}")
    option = library.option_by_id(value)
    if option is None:
        raise RuleConflictError(f"implication targets unknown option {value!r} in field {field!r}")
    return option
