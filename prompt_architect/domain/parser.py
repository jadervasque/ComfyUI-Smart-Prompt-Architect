"""Strict typed parser for versioned Prompt Architect JSON data."""

import math
import re
from collections.abc import Mapping, Sequence
from string import Formatter
from types import MappingProxyType
from typing import TypeVar

from prompt_architect.domain.enums import (
    FieldMode,
    GenerationMode,
    OptionStatus,
    RuleOperator,
    RuleType,
)
from prompt_architect.domain.exceptions import SchemaValidationError
from prompt_architect.domain.models import (
    FieldConfiguration,
    GroupConfiguration,
    LibraryDefinition,
    NodeConfiguration,
    ProfileDefinition,
    PromptOption,
    Rule,
    RuleCondition,
    SectionDefinition,
    TextVariant,
)

SUPPORTED_SCHEMA_VERSION = "1.0"
_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[.-][0-9A-Za-z.-]+)?$")
_T = TypeVar("_T")


def parse_profile(data: object) -> ProfileDefinition:
    """Parse and validate a strict profile mapping."""
    root = _mapping(data, "profile")
    _reject_unknown(
        root,
        {
            "schema_version",
            "id",
            "version",
            "display_name",
            "language",
            "minimum_sections",
            "minimum_prompt_characters",
            "max_selection_attempts",
            "section_order",
            "sections",
            "templates",
            "profile_fallbacks",
            "allow_empty_negative",
            "metadata",
        },
        "profile",
    )
    schema_version = _schema_version(root, "profile")
    profile_id = _id(root, "id", "profile")
    sections_data = _mapping(_required(root, "sections", "profile"), "profile.sections")
    sections = {
        section_id: _parse_section(section_id, value) for section_id, value in sections_data.items()
    }
    if not sections:
        raise _error("profile.sections", "must contain at least one section")
    order = _string_tuple(_required(root, "section_order", "profile"), "profile.section_order")
    if len(order) != len(set(order)):
        raise _error("profile.section_order", "contains duplicate section IDs")
    if set(order) != set(sections):
        raise _error("profile.section_order", "must list every section exactly once")
    minimum_sections = _positive_int(root, "minimum_sections", "profile")
    if minimum_sections > len(sections):
        raise _error("profile.minimum_sections", "cannot exceed the number of sections")
    templates = _string_mapping(_required(root, "templates", "profile"), "profile.templates")
    positive_template = templates.get("positive", "").strip()
    if not positive_template:
        raise _error("profile.templates.positive", "is required and cannot be empty")
    _validate_template_fields(templates, frozenset(sections))
    return ProfileDefinition(
        schema_version=schema_version,
        id=profile_id,
        version=_version(root, "version", "profile"),
        display_name=_non_empty_string(root, "display_name", "profile"),
        language=_non_empty_string(root, "language", "profile"),
        minimum_sections=minimum_sections,
        minimum_prompt_characters=_positive_int(root, "minimum_prompt_characters", "profile"),
        max_selection_attempts=_positive_int(root, "max_selection_attempts", "profile"),
        section_order=order,
        sections=MappingProxyType(sections),
        templates=MappingProxyType(dict(templates)),
        profile_fallbacks=MappingProxyType(
            dict(_optional_string_mapping(root, "profile_fallbacks", "profile"))
        ),
        allow_empty_negative=_optional_bool(root, "allow_empty_negative", True, "profile"),
        metadata=MappingProxyType(dict(_optional_mapping(root, "metadata", "profile"))),
    )


def parse_library(data: object) -> LibraryDefinition:
    """Parse and validate a strict library mapping."""
    root = _mapping(data, "library")
    _reject_unknown(
        root,
        {"schema_version", "id", "version", "display_name", "options", "fallback_option_id"},
        "library",
    )
    options_data = _sequence(_required(root, "options", "library"), "library.options")
    options = tuple(_parse_option(value, index) for index, value in enumerate(options_data))
    if not options:
        raise _error("library.options", "must contain at least one option")
    option_ids = [option.id for option in options]
    if len(option_ids) != len(set(option_ids)):
        raise _error("library.options", "contains duplicate option IDs")
    fallback = _optional_string(root, "fallback_option_id", "library")
    if fallback is not None and fallback not in set(option_ids):
        raise _error("library.fallback_option_id", f"references unknown option {fallback!r}")
    return LibraryDefinition(
        schema_version=_schema_version(root, "library"),
        id=_id(root, "id", "library"),
        version=_version(root, "version", "library"),
        display_name=_non_empty_string(root, "display_name", "library"),
        options=options,
        fallback_option_id=fallback,
    )


def parse_configuration(data: object) -> NodeConfiguration:
    """Parse and validate serialized node configuration."""
    root = _mapping(data, "configuration")
    _reject_unknown(
        root,
        {
            "schema_version",
            "profile_id",
            "profile_version",
            "mode",
            "master_seed",
            "groups",
            "fields",
            "overrides",
            "batch_index",
        },
        "configuration",
    )
    groups_data = _optional_mapping(root, "groups", "configuration")
    fields_data = _optional_mapping(root, "fields", "configuration")
    groups = {key: _parse_group(key, value) for key, value in groups_data.items()}
    fields = {key: _parse_field(key, value) for key, value in fields_data.items()}
    mode = _enum_value(
        GenerationMode,
        _non_empty_string(root, "mode", "configuration"),
        "configuration.mode",
    )
    master_seed = _integer(root, "master_seed", "configuration")
    if master_seed < 0 or master_seed > (2**64 - 1):
        raise _error("configuration.master_seed", "must be between 0 and 2^64-1")
    batch_index = _optional_int(root, "batch_index", 0, "configuration")
    if batch_index is None:
        raise _error("configuration.batch_index", "must be an integer")
    if batch_index < 0:
        raise _error("configuration.batch_index", "must be non-negative")
    return NodeConfiguration(
        schema_version=_schema_version(root, "configuration"),
        profile_id=_id(root, "profile_id", "configuration"),
        profile_version=_optional_version(root, "profile_version", "configuration"),
        mode=mode,
        master_seed=master_seed,
        groups=MappingProxyType(groups),
        fields=MappingProxyType(fields),
        overrides=MappingProxyType(
            dict(_optional_string_mapping(root, "overrides", "configuration"))
        ),
        batch_index=batch_index,
    )


def _parse_section(section_id: str, data: object) -> SectionDefinition:
    _validate_id_value(section_id, f"profile.sections.{section_id}")
    path = f"profile.sections.{section_id}"
    item = _mapping(data, path)
    _reject_unknown(item, {"required", "library", "mode", "default", "group", "fallback"}, path)
    required = _bool(item, "required", path)
    mode = _enum_value(FieldMode, _non_empty_string(item, "mode", path), f"{path}.mode")
    default = _optional_string(item, "default", path)
    if mode is FieldMode.FIXED and default is None:
        raise _error(f"{path}.default", "is required when mode is fixed")
    if required and mode is FieldMode.DISABLED:
        raise _error(f"{path}.mode", "a required section cannot be disabled by profile default")
    return SectionDefinition(
        id=section_id,
        required=required,
        library=_id(item, "library", path),
        mode=mode,
        group=_id(item, "group", path),
        default=default,
        fallback=_optional_string(item, "fallback", path),
    )


def _parse_option(data: object, index: int) -> PromptOption:
    path = f"library.options[{index}]"
    item = _mapping(data, path)
    _reject_unknown(
        item,
        {
            "id",
            "text",
            "weight",
            "tags",
            "status",
            "semantic_key",
            "requires",
            "excludes",
            "implies",
            "prefer",
            "sentence",
            "variants",
            "join_hint",
        },
        path,
    )
    weight = _number(item, "weight", 1.0, path)
    _validate_weight(weight, f"{path}.weight")
    rules: list[Rule] = []
    for rule_type in RuleType:
        rules.extend(_parse_rules(item.get(rule_type.value, ()), rule_type, path))
    variants_data = _sequence(item.get("variants", ()), f"{path}.variants")
    variants = tuple(_parse_variant(value, path, i) for i, value in enumerate(variants_data))
    tags = _string_tuple(item.get("tags", ()), f"{path}.tags")
    if len(tags) != len(set(tags)):
        raise _error(f"{path}.tags", "contains duplicate tags")
    return PromptOption(
        id=_id(item, "id", path),
        text=_non_empty_string(item, "text", path),
        weight=weight,
        tags=tuple(sorted(tags)),
        status=_enum_value(
            OptionStatus,
            _optional_string(item, "status", path) or OptionStatus.ACTIVE.value,
            f"{path}.status",
        ),
        semantic_key=_optional_string(item, "semantic_key", path),
        rules=tuple(rules),
        sentence=_optional_string(item, "sentence", path),
        variants=variants,
        join_hint=_optional_string(item, "join_hint", path),
    )


def _parse_rules(data: object, rule_type: RuleType, parent_path: str) -> list[Rule]:
    path = f"{parent_path}.{rule_type.value}"
    items = _sequence(data, path)
    parsed: list[Rule] = []
    for index, value in enumerate(items):
        rule_path = f"{path}[{index}]"
        item = _mapping(value, rule_path)
        if rule_type is RuleType.IMPLIES:
            _reject_unknown(item, {"field", "value"}, rule_path)
            parsed.append(
                Rule(
                    type=rule_type,
                    target_field=_id(item, "field", rule_path),
                    target_value=_non_empty_string(item, "value", rule_path),
                )
            )
            continue
        allowed = {"field", "operator", "value"}
        if rule_type is RuleType.PREFER:
            allowed.add("multiplier")
        _reject_unknown(item, allowed, rule_path)
        operator = _enum_value(
            RuleOperator,
            _non_empty_string(item, "operator", rule_path),
            f"{rule_path}.operator",
        )
        condition_value = item.get("value")
        if operator not in {RuleOperator.MISSING, RuleOperator.PRESENT} and "value" not in item:
            raise _error(f"{rule_path}.value", f"is required for operator {operator.value}")
        multiplier = _number(item, "multiplier", 1.0, rule_path)
        if rule_type is RuleType.PREFER and (not math.isfinite(multiplier) or multiplier <= 0):
            raise _error(f"{rule_path}.multiplier", "must be finite and greater than zero")
        parsed.append(
            Rule(
                type=rule_type,
                condition=RuleCondition(
                    field=_id(item, "field", rule_path),
                    operator=operator,
                    value=_freeze_json(condition_value),
                ),
                multiplier=multiplier,
            )
        )
    return parsed


def _parse_variant(data: object, parent_path: str, index: int) -> TextVariant:
    path = f"{parent_path}.variants[{index}]"
    item = _mapping(data, path)
    _reject_unknown(item, {"text", "weight"}, path)
    weight = _number(item, "weight", 1.0, path)
    _validate_weight(weight, f"{path}.weight")
    return TextVariant(text=_non_empty_string(item, "text", path), weight=weight)


def _parse_group(group_id: str, data: object) -> GroupConfiguration:
    _validate_id_value(group_id, f"configuration.groups.{group_id}")
    path = f"configuration.groups.{group_id}"
    item = _mapping(data, path)
    _reject_unknown(item, {"locked", "seed"}, path)
    seed = _optional_int(item, "seed", None, path)
    if seed is not None and (seed < 0 or seed > (2**64 - 1)):
        raise _error(f"{path}.seed", "must be between 0 and 2^64-1")
    return GroupConfiguration(locked=_optional_bool(item, "locked", False, path), seed=seed)


def _parse_field(field_id: str, data: object) -> FieldConfiguration:
    _validate_id_value(field_id, f"configuration.fields.{field_id}")
    path = f"configuration.fields.{field_id}"
    item = _mapping(data, path)
    _reject_unknown(item, {"mode", "value", "include_tags", "exclude_tags"}, path)
    mode = _enum_value(FieldMode, _non_empty_string(item, "mode", path), f"{path}.mode")
    value = _optional_string(item, "value", path)
    if mode is FieldMode.FIXED and value is None:
        raise _error(f"{path}.value", "is required when mode is fixed")
    return FieldConfiguration(
        mode=mode,
        value=value,
        include_tags=tuple(
            sorted(_string_tuple(item.get("include_tags", ()), f"{path}.include_tags"))
        ),
        exclude_tags=tuple(
            sorted(_string_tuple(item.get("exclude_tags", ()), f"{path}.exclude_tags"))
        ),
    )


def _validate_template_fields(templates: Mapping[str, str], section_ids: frozenset[str]) -> None:
    allowed = section_ids | {"negative_global", "negative_conditional"}
    formatter = Formatter()
    for template_name, template in templates.items():
        try:
            fields = [field for _, field, _, _ in formatter.parse(template) if field]
        except ValueError as error:
            raise _error(
                f"profile.templates.{template_name}", f"invalid template: {error}"
            ) from error
        unsupported = sorted(field for field in fields if field not in allowed)
        if unsupported:
            raise _error(
                f"profile.templates.{template_name}",
                f"contains unsupported placeholders: {', '.join(unsupported)}",
            )


def _validate_weight(weight: float, path: str) -> None:
    if not math.isfinite(weight) or weight < 0:
        raise _error(path, "must be finite and non-negative")


def _schema_version(data: Mapping[str, object], path: str) -> str:
    value = _non_empty_string(data, "schema_version", path)
    if value != SUPPORTED_SCHEMA_VERSION:
        raise _error(f"{path}.schema_version", f"unsupported schema version {value!r}")
    return value


def _version(data: Mapping[str, object], key: str, path: str) -> str:
    value = _non_empty_string(data, key, path)
    if not _VERSION_PATTERN.fullmatch(value):
        raise _error(f"{path}.{key}", "must be a semantic version")
    return value


def _optional_version(data: Mapping[str, object], key: str, path: str) -> str | None:
    value = _optional_string(data, key, path)
    if value is not None and not _VERSION_PATTERN.fullmatch(value):
        raise _error(f"{path}.{key}", "must be a semantic version")
    return value


def _id(data: Mapping[str, object], key: str, path: str) -> str:
    value = _non_empty_string(data, key, path)
    _validate_id_value(value, f"{path}.{key}")
    return value


def _validate_id_value(value: str, path: str) -> None:
    if not _ID_PATTERN.fullmatch(value):
        raise _error(path, "must use lowercase kebab-case")


def _mapping(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise _error(path, "must be a JSON object")
    return value


def _optional_mapping(data: Mapping[str, object], key: str, path: str) -> Mapping[str, object]:
    return _mapping(data.get(key, {}), f"{path}.{key}")


def _sequence(value: object, path: str) -> Sequence[object]:
    if not isinstance(value, list) and not isinstance(value, tuple):
        raise _error(path, "must be a JSON array")
    return value


def _required(data: Mapping[str, object], key: str, path: str) -> object:
    if key not in data:
        raise _error(f"{path}.{key}", "is required")
    return data[key]


def _non_empty_string(data: Mapping[str, object], key: str, path: str) -> str:
    value = _required(data, key, path)
    if not isinstance(value, str) or not value.strip():
        raise _error(f"{path}.{key}", "must be a non-empty string")
    return value.strip()


def _optional_string(data: Mapping[str, object], key: str, path: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise _error(f"{path}.{key}", "must be a non-empty string when provided")
    return value.strip()


def _bool(data: Mapping[str, object], key: str, path: str) -> bool:
    value = _required(data, key, path)
    if not isinstance(value, bool):
        raise _error(f"{path}.{key}", "must be a boolean")
    return value


def _optional_bool(data: Mapping[str, object], key: str, default: bool, path: str) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise _error(f"{path}.{key}", "must be a boolean")
    return value


def _integer(data: Mapping[str, object], key: str, path: str) -> int:
    value = _required(data, key, path)
    if not isinstance(value, int) or isinstance(value, bool):
        raise _error(f"{path}.{key}", "must be an integer")
    return value


def _optional_int(
    data: Mapping[str, object], key: str, default: int | None, path: str
) -> int | None:
    value = data.get(key, default)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise _error(f"{path}.{key}", "must be an integer")
    return value


def _positive_int(data: Mapping[str, object], key: str, path: str) -> int:
    value = _integer(data, key, path)
    if value <= 0:
        raise _error(f"{path}.{key}", "must be greater than zero")
    return value


def _number(data: Mapping[str, object], key: str, default: float, path: str) -> float:
    value = data.get(key, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise _error(f"{path}.{key}", "must be a number")
    return float(value)


def _string_tuple(value: object, path: str) -> tuple[str, ...]:
    items = _sequence(value, path)
    if not all(isinstance(item, str) and item.strip() for item in items):
        raise _error(path, "must contain only non-empty strings")
    return tuple(item.strip() for item in items if isinstance(item, str))


def _string_mapping(value: object, path: str) -> Mapping[str, str]:
    item = _mapping(value, path)
    if not all(isinstance(entry, str) for entry in item.values()):
        raise _error(path, "must contain only string values")
    return {key: entry for key, entry in item.items() if isinstance(entry, str)}


def _optional_string_mapping(data: Mapping[str, object], key: str, path: str) -> Mapping[str, str]:
    return _string_mapping(data.get(key, {}), f"{path}.{key}")


def _enum_value(enum_type: type[_T], value: str, path: str) -> _T:
    try:
        return enum_type(value)  # type: ignore[call-arg]
    except ValueError as error:
        choices = ", ".join(member.value for member in enum_type)  # type: ignore[attr-defined]
        raise _error(path, f"must be one of: {choices}") from error


def _reject_unknown(data: Mapping[str, object], allowed: set[str], path: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise _error(path, f"contains unknown fields: {', '.join(unknown)}")


def _freeze_json(value: object) -> object:
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    if isinstance(value, dict):
        return MappingProxyType({str(key): _freeze_json(item) for key, item in value.items()})
    return value


def _error(path: str, message: str) -> SchemaValidationError:
    return SchemaValidationError(f"{path}: {message}")
