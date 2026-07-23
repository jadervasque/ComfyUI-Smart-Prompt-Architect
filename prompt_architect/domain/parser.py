"""Strict typed parser for versioned Prompt Architect JSON data."""

import math
import re
from collections.abc import Mapping, Sequence
from pathlib import PurePosixPath
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
    MAX_CUSTOM_TEXT_CHARACTERS,
    CatalogIndexDefinition,
    CatalogPackDefinition,
    CatalogPackReference,
    FieldConfiguration,
    GroupConfiguration,
    LibraryDefinition,
    LogicalLibraryDefinition,
    NodeConfiguration,
    ProfileDefinition,
    PromptOption,
    Rule,
    RuleCondition,
    SectionDefinition,
    TextVariant,
)

SUPPORTED_SCHEMA_VERSION = "1.0"
CATALOG_SCHEMA_VERSION = "2.0"
SUPPORTED_PROFILE_SCHEMA_VERSIONS = frozenset({SUPPORTED_SCHEMA_VERSION, CATALOG_SCHEMA_VERSION})
CURRENT_CONFIGURATION_SCHEMA_VERSION = "1.1"
SUPPORTED_CONFIGURATION_SCHEMA_VERSIONS = frozenset(
    {SUPPORTED_SCHEMA_VERSION, CURRENT_CONFIGURATION_SCHEMA_VERSION}
)
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
            "catalog_version",
            "enabled_packs",
            "allowed_safety_classes",
            "verbosity",
            "negative_level",
        },
        "profile",
    )
    schema_version = _schema_version(
        root,
        "profile",
        supported=SUPPORTED_PROFILE_SCHEMA_VERSIONS,
    )
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
        catalog_version=_optional_version(root, "catalog_version", "profile"),
        enabled_packs=tuple(
            sorted(_string_tuple(root.get("enabled_packs", ()), "profile.enabled_packs"))
        ),
        allowed_safety_classes=tuple(
            sorted(
                _string_tuple(
                    root.get("allowed_safety_classes", ["general"]),
                    "profile.allowed_safety_classes",
                )
            )
        ),
        verbosity=_choice(
            root,
            "verbosity",
            "standard",
            {"compact", "standard", "detailed"},
            "profile",
        ),
        negative_level=_choice(
            root,
            "negative_level",
            "standard",
            {"minimal", "standard", "strict"},
            "profile",
        ),
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
    options = tuple(
        sorted(
            (_parse_option(value, index) for index, value in enumerate(options_data)),
            key=lambda option: option.id,
        )
    )
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


def parse_catalog_index(data: object) -> CatalogIndexDefinition:
    """Parse the trusted Catalog V2 index without resolving any filesystem path."""
    root = _mapping(data, "catalog-index")
    _reject_unknown(
        root,
        {"schema_version", "id", "version", "language", "packs", "libraries"},
        "catalog-index",
    )
    schema_version = _schema_version(
        root,
        "catalog-index",
        supported=frozenset({CATALOG_SCHEMA_VERSION}),
    )
    pack_values = _sequence(_required(root, "packs", "catalog-index"), "catalog-index.packs")
    packs = tuple(_parse_pack_reference(value, index) for index, value in enumerate(pack_values))
    if not packs:
        raise _error("catalog-index.packs", "must contain at least one pack")
    pack_ids = [pack.id for pack in packs]
    if len(pack_ids) != len(set(pack_ids)):
        raise _error("catalog-index.packs", "contains duplicate pack IDs")
    known_packs = frozenset(pack_ids)
    for pack in packs:
        unknown = set(pack.dependencies) - known_packs
        if unknown:
            raise _error(
                f"catalog-index.packs.{pack.id}.dependencies",
                "references unknown packs: " + ", ".join(sorted(unknown)),
            )
    _validate_dependency_cycles(packs)
    libraries_data = _mapping(
        _required(root, "libraries", "catalog-index"),
        "catalog-index.libraries",
    )
    libraries = {
        library_id: _parse_logical_library(library_id, value, known_packs)
        for library_id, value in libraries_data.items()
    }
    if not libraries:
        raise _error("catalog-index.libraries", "must contain at least one logical library")
    for pack in packs:
        library = libraries.get(pack.library)
        if library is None or pack.id not in library.pack_ids:
            raise _error(
                f"catalog-index.packs.{pack.id}",
                f"is not declared by logical library {pack.library!r}",
            )
    return CatalogIndexDefinition(
        schema_version=schema_version,
        id=_id(root, "id", "catalog-index"),
        version=_version(root, "version", "catalog-index"),
        language=_non_empty_string(root, "language", "catalog-index"),
        packs=packs,
        libraries=MappingProxyType(libraries),
    )


def parse_catalog_pack(data: object) -> CatalogPackDefinition:
    """Parse one segmented Catalog V2 pack and its atomic options."""
    root = _mapping(data, "catalog-pack")
    _reject_unknown(
        root,
        {
            "schema_version",
            "id",
            "version",
            "library",
            "domain",
            "category",
            "language",
            "status",
            "safety",
            "tags",
            "options",
            "fallback_option_id",
        },
        "catalog-pack",
    )
    schema_version = _schema_version(
        root,
        "catalog-pack",
        supported=frozenset({CATALOG_SCHEMA_VERSION}),
    )
    pack_id = _id(root, "id", "catalog-pack")
    domain = _id(root, "domain", "catalog-pack")
    category = _id(root, "category", "catalog-pack")
    safety = _choice(
        root,
        "safety",
        "general",
        {"general", "fashion-mature", "dark-atmospheric", "experimental"},
        "catalog-pack",
    )
    status = _choice(
        root,
        "status",
        "active",
        {"active", "experimental", "deprecated"},
        "catalog-pack",
    )
    options_data = _sequence(
        _required(root, "options", "catalog-pack"),
        "catalog-pack.options",
    )
    options = tuple(
        sorted(
            (
                _parse_option(
                    value,
                    index,
                    parent_path="catalog-pack.options",
                    pack_id=pack_id,
                    domain=domain,
                    category=category,
                    safety=safety,
                )
                for index, value in enumerate(options_data)
            ),
            key=lambda option: option.id,
        )
    )
    if not options:
        raise _error("catalog-pack.options", "must contain at least one option")
    option_ids = [option.id for option in options]
    if len(option_ids) != len(set(option_ids)):
        raise _error("catalog-pack.options", "contains duplicate option IDs")
    semantic_keys = [option.semantic_key for option in options if option.semantic_key is not None]
    if len(semantic_keys) != len(set(semantic_keys)):
        raise _error("catalog-pack.options", "contains duplicate semantic keys")
    fallback = _optional_string(root, "fallback_option_id", "catalog-pack")
    if fallback is not None and fallback not in set(option_ids):
        raise _error("catalog-pack.fallback_option_id", f"references unknown option {fallback!r}")
    tags = _normalized_tags(root.get("tags", ()), "catalog-pack.tags")
    return CatalogPackDefinition(
        schema_version=schema_version,
        id=pack_id,
        version=_version(root, "version", "catalog-pack"),
        library=_id(root, "library", "catalog-pack"),
        domain=domain,
        category=category,
        language=_non_empty_string(root, "language", "catalog-pack"),
        status=status,
        safety=safety,
        tags=tags,
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
    schema_version = _schema_version(
        root,
        "configuration",
        supported=SUPPORTED_CONFIGURATION_SCHEMA_VERSIONS,
    )
    groups_data = _optional_mapping(root, "groups", "configuration")
    fields_data = _optional_mapping(root, "fields", "configuration")
    groups = {key: _parse_group(key, value) for key, value in groups_data.items()}
    fields = {
        key: _parse_field(key, value, schema_version=schema_version)
        for key, value in fields_data.items()
    }
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
        schema_version=schema_version,
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
    if mode is FieldMode.CUSTOM:
        raise _error(f"{path}.mode", "custom mode is only valid in node field overrides")
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


def _parse_pack_reference(data: object, index: int) -> CatalogPackReference:
    path = f"catalog-index.packs[{index}]"
    item = _mapping(data, path)
    _reject_unknown(
        item,
        {
            "id",
            "library",
            "domain",
            "path",
            "version",
            "language",
            "status",
            "safety",
            "tags",
            "dependencies",
            "priority",
        },
        path,
    )
    priority = _optional_int(item, "priority", 100, path)
    if priority is None or priority < 0:
        raise _error(f"{path}.priority", "must be a non-negative integer")
    return CatalogPackReference(
        id=_id(item, "id", path),
        library=_id(item, "library", path),
        domain=_id(item, "domain", path),
        path=_relative_catalog_path(_non_empty_string(item, "path", path), f"{path}.path"),
        version=_version(item, "version", path),
        language=_non_empty_string(item, "language", path),
        status=_choice(
            item,
            "status",
            "active",
            {"active", "experimental", "deprecated"},
            path,
        ),
        safety=_choice(
            item,
            "safety",
            "general",
            {"general", "fashion-mature", "dark-atmospheric", "experimental"},
            path,
        ),
        tags=_normalized_tags(item.get("tags", ()), f"{path}.tags"),
        dependencies=tuple(
            sorted(_string_tuple(item.get("dependencies", ()), f"{path}.dependencies"))
        ),
        priority=priority,
    )


def _parse_logical_library(
    library_id: str,
    data: object,
    known_packs: frozenset[str],
) -> LogicalLibraryDefinition:
    _validate_id_value(library_id, f"catalog-index.libraries.{library_id}")
    path = f"catalog-index.libraries.{library_id}"
    item = _mapping(data, path)
    _reject_unknown(item, {"display_name", "packs", "fallback_option_id"}, path)
    pack_ids = _string_tuple(_required(item, "packs", path), f"{path}.packs")
    if not pack_ids:
        raise _error(f"{path}.packs", "must contain at least one pack")
    if len(pack_ids) != len(set(pack_ids)):
        raise _error(f"{path}.packs", "contains duplicate pack IDs")
    unknown = set(pack_ids) - known_packs
    if unknown:
        raise _error(
            f"{path}.packs",
            "references unknown packs: " + ", ".join(sorted(unknown)),
        )
    return LogicalLibraryDefinition(
        id=library_id,
        display_name=_non_empty_string(item, "display_name", path),
        pack_ids=pack_ids,
        fallback_option_id=_optional_string(item, "fallback_option_id", path),
    )


def _validate_dependency_cycles(packs: tuple[CatalogPackReference, ...]) -> None:
    dependencies = {pack.id: pack.dependencies for pack in packs}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(pack_id: str) -> None:
        if pack_id in visiting:
            raise _error(
                "catalog-index.packs.dependencies",
                f"contains a cycle involving {pack_id!r}",
            )
        if pack_id in visited:
            return
        visiting.add(pack_id)
        for dependency in dependencies[pack_id]:
            visit(dependency)
        visiting.remove(pack_id)
        visited.add(pack_id)

    for pack_id in sorted(dependencies):
        visit(pack_id)


def _parse_option(
    data: object,
    index: int,
    *,
    parent_path: str = "library.options",
    pack_id: str | None = None,
    domain: str | None = None,
    category: str | None = None,
    safety: str = "general",
) -> PromptOption:
    path = f"{parent_path}[{index}]"
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
            "family",
            "facets",
            "subcategory",
            "intensity",
            "safety",
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
    if pack_id is not None and not 2 <= len(variants) <= 5:
        raise _error(f"{path}.variants", "Catalog V2 options require two to five variants")
    variant_ids = [variant.id for variant in variants if variant.id is not None]
    if len(variant_ids) != len(set(variant_ids)):
        raise _error(f"{path}.variants", "contains duplicate variant IDs")
    variant_texts = [variant.text.casefold() for variant in variants]
    if len(variant_texts) != len(set(variant_texts)):
        raise _error(f"{path}.variants", "contains duplicate variant text")
    tags = _normalized_tags(item.get("tags", ()), f"{path}.tags")
    facets = _string_mapping(item.get("facets", {}), f"{path}.facets")
    for facet_name, facet_value in facets.items():
        _validate_id_value(facet_name, f"{path}.facets.{facet_name}")
        _validate_id_value(facet_value, f"{path}.facets.{facet_name}")
    return PromptOption(
        id=_id(item, "id", path),
        text=_non_empty_string(item, "text", path),
        weight=weight,
        tags=tags,
        status=_enum_value(
            OptionStatus,
            _optional_string(item, "status", path) or OptionStatus.ACTIVE.value,
            f"{path}.status",
        ),
        semantic_key=_optional_string(item, "semantic_key", path),
        rules=tuple(rules),
        sentence=_optional_string(item, "sentence", path),
        variants=variants,
        join_hint=(
            _choice(
                item,
                "join_hint",
                "fragment",
                {"fragment", "sentence", "replace"},
                path,
            )
            if pack_id is not None
            else _optional_string(item, "join_hint", path)
        ),
        family=_optional_id(item, "family", path),
        facets=MappingProxyType(dict(sorted(facets.items()))),
        pack_id=pack_id,
        domain=domain,
        category=category,
        subcategory=_optional_id(item, "subcategory", path),
        intensity=_choice(
            item,
            "intensity",
            "moderate",
            {"subtle", "moderate", "strong"},
            path,
        ),
        safety=_choice(
            item,
            "safety",
            safety,
            {"general", "fashion-mature", "dark-atmospheric", "experimental"},
            path,
        ),
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
    _reject_unknown(item, {"id", "text", "weight"}, path)
    weight = _number(item, "weight", 1.0, path)
    _validate_weight(weight, f"{path}.weight")
    return TextVariant(
        text=_non_empty_string(item, "text", path),
        weight=weight,
        id=_optional_id(item, "id", path),
    )


def _parse_group(group_id: str, data: object) -> GroupConfiguration:
    _validate_id_value(group_id, f"configuration.groups.{group_id}")
    path = f"configuration.groups.{group_id}"
    item = _mapping(data, path)
    _reject_unknown(item, {"locked", "seed"}, path)
    seed = _optional_int(item, "seed", None, path)
    if seed is not None and (seed < 0 or seed > (2**64 - 1)):
        raise _error(f"{path}.seed", "must be between 0 and 2^64-1")
    return GroupConfiguration(locked=_optional_bool(item, "locked", False, path), seed=seed)


def _parse_field(field_id: str, data: object, *, schema_version: str) -> FieldConfiguration:
    _validate_id_value(field_id, f"configuration.fields.{field_id}")
    path = f"configuration.fields.{field_id}"
    item = _mapping(data, path)
    _reject_unknown(item, {"mode", "value", "include_tags", "exclude_tags"}, path)
    mode = _enum_value(FieldMode, _non_empty_string(item, "mode", path), f"{path}.mode")
    value = _optional_string(item, "value", path)
    if mode in {FieldMode.FIXED, FieldMode.CUSTOM} and value is None:
        raise _error(f"{path}.value", f"is required when mode is {mode.value}")
    if mode is FieldMode.CUSTOM:
        if schema_version != CURRENT_CONFIGURATION_SCHEMA_VERSION:
            raise _error(
                f"{path}.mode",
                f"custom requires configuration schema {CURRENT_CONFIGURATION_SCHEMA_VERSION}",
            )
        if value is not None and len(value) > MAX_CUSTOM_TEXT_CHARACTERS:
            raise _error(
                f"{path}.value",
                f"custom text cannot exceed {MAX_CUSTOM_TEXT_CHARACTERS} characters",
            )
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


def _schema_version(
    data: Mapping[str, object],
    path: str,
    *,
    supported: frozenset[str] = frozenset({SUPPORTED_SCHEMA_VERSION}),
) -> str:
    value = _non_empty_string(data, "schema_version", path)
    if value not in supported:
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


def _choice(
    data: Mapping[str, object],
    key: str,
    default: str,
    choices: set[str],
    path: str,
) -> str:
    value = _optional_string(data, key, path) or default
    if value not in choices:
        raise _error(f"{path}.{key}", "must be one of: " + ", ".join(sorted(choices)))
    return value


def _id(data: Mapping[str, object], key: str, path: str) -> str:
    value = _non_empty_string(data, key, path)
    _validate_id_value(value, f"{path}.{key}")
    return value


def _optional_id(data: Mapping[str, object], key: str, path: str) -> str | None:
    value = _optional_string(data, key, path)
    if value is not None:
        _validate_id_value(value, f"{path}.{key}")
    return value


def _validate_id_value(value: str, path: str) -> None:
    if not _ID_PATTERN.fullmatch(value):
        raise _error(path, "must use lowercase kebab-case")


def _relative_catalog_path(value: str, path: str) -> str:
    candidate = PurePosixPath(value)
    if (
        candidate.is_absolute()
        or candidate.suffix != ".json"
        or not candidate.parts
        or any(part in {"", ".", ".."} for part in candidate.parts)
        or "\\" in value
    ):
        raise _error(path, "must be a safe relative POSIX JSON path")
    return candidate.as_posix()


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


def _normalized_tags(value: object, path: str) -> tuple[str, ...]:
    tags = _string_tuple(value, path)
    if len(tags) != len(set(tags)):
        raise _error(path, "contains duplicate tags")
    for index, tag in enumerate(tags):
        _validate_id_value(tag, f"{path}[{index}]")
    return tuple(sorted(tags))


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
