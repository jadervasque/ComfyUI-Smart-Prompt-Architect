"""Immutable domain contracts for profiles, libraries, configuration, and results."""

from collections.abc import Mapping
from dataclasses import dataclass, field

from prompt_architect.domain.enums import (
    FieldMode,
    GenerationMode,
    IssueSeverity,
    OptionStatus,
    RuleOperator,
    RuleType,
    SelectionSource,
)

MAX_CUSTOM_TEXT_CHARACTERS = 4096


@dataclass(frozen=True, slots=True)
class RuleCondition:
    """One safe declarative predicate over the selection context."""

    field: str
    operator: RuleOperator
    value: object | None = None


@dataclass(frozen=True, slots=True)
class Rule:
    """A compatibility constraint, implication, or preference."""

    type: RuleType
    condition: RuleCondition | None = None
    target_field: str | None = None
    target_value: str | None = None
    multiplier: float = 1.0


@dataclass(frozen=True, slots=True)
class TextVariant:
    """Optional weighted wording variant for an option."""

    text: str
    weight: float = 1.0


@dataclass(frozen=True, slots=True)
class PromptOption:
    """A selectable library option with validated metadata and rules."""

    id: str
    text: str
    weight: float = 1.0
    tags: tuple[str, ...] = ()
    status: OptionStatus = OptionStatus.ACTIVE
    semantic_key: str | None = None
    rules: tuple[Rule, ...] = ()
    sentence: str | None = None
    variants: tuple[TextVariant, ...] = ()
    join_hint: str | None = None


@dataclass(frozen=True, slots=True)
class SectionDefinition:
    """How one profile section is resolved."""

    id: str
    required: bool
    library: str
    mode: FieldMode
    group: str
    default: str | None = None
    fallback: str | None = None


@dataclass(frozen=True, slots=True)
class ProfileDefinition:
    """A versioned prompt composition profile."""

    schema_version: str
    id: str
    version: str
    display_name: str
    language: str
    minimum_sections: int
    minimum_prompt_characters: int
    max_selection_attempts: int
    section_order: tuple[str, ...]
    sections: Mapping[str, SectionDefinition]
    templates: Mapping[str, str]
    profile_fallbacks: Mapping[str, str] = field(default_factory=dict)
    allow_empty_negative: bool = True
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class LibraryDefinition:
    """A versioned set of selectable prompt options."""

    schema_version: str
    id: str
    version: str
    display_name: str
    options: tuple[PromptOption, ...]
    fallback_option_id: str | None = None

    def option_by_id(self, option_id: str) -> PromptOption | None:
        """Return an option by stable ID without exposing mutable indexes."""
        return next((option for option in self.options if option.id == option_id), None)


@dataclass(frozen=True, slots=True)
class FieldConfiguration:
    """Per-field mode, fixed option ID or custom text, and optional tag filters."""

    mode: FieldMode
    value: str | None = None
    include_tags: tuple[str, ...] = ()
    exclude_tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GroupConfiguration:
    """Lock and optional explicit seed for a deterministic group."""

    locked: bool = False
    seed: int | None = None


@dataclass(frozen=True, slots=True)
class NodeConfiguration:
    """Serializable effective node configuration."""

    schema_version: str
    profile_id: str
    profile_version: str | None
    mode: GenerationMode
    master_seed: int
    groups: Mapping[str, GroupConfiguration] = field(default_factory=dict)
    fields: Mapping[str, FieldConfiguration] = field(default_factory=dict)
    overrides: Mapping[str, str] = field(default_factory=dict)
    batch_index: int = 0


@dataclass(frozen=True, slots=True)
class SelectedValue:
    """Resolved value and provenance for one section."""

    section_id: str
    option: PromptOption
    source: SelectionSource
    fallback_used: bool = False
    rendered_text: str = ""


@dataclass(frozen=True, slots=True)
class SelectionContext:
    """Incrementally resolved structured prompt context."""

    selections: Mapping[str, SelectedValue] = field(default_factory=dict)
    fixed_fields: frozenset[str] = frozenset()
    profile_metadata: Mapping[str, object] = field(default_factory=dict)
    generation_mode: GenerationMode = GenerationMode.BALANCED


@dataclass(frozen=True, slots=True)
class SelectionResult:
    """Completed structured selection and diagnostic events."""

    context: SelectionContext
    group_seeds: Mapping[str, int]
    attempts: Mapping[str, int]
    applied_rules: tuple[str, ...] = ()
    resolved_conflicts: tuple[str, ...] = ()
    fallbacks: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RenderedPrompt:
    """Positive and negative text after safe rendering and normalization."""

    positive: str
    negative: str
    rendered_sections: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Machine-readable validation issue."""

    code: str
    message: str
    severity: IssueSeverity
    path: str | None = None


@dataclass(frozen=True, slots=True)
class PromptManifest:
    """Reproducibility record for one composition."""

    schema_version: str
    engine_version: str
    profile_id: str
    profile_version: str
    library_versions: Mapping[str, str]
    configuration_hash: str
    effective_configuration: Mapping[str, object]
    master_seed: int
    group_seeds: Mapping[str, int]
    selections: Mapping[str, Mapping[str, object]]
    applied_rules: tuple[str, ...]
    resolved_conflicts: tuple[str, ...]
    fallbacks: tuple[str, ...]
    attempts: Mapping[str, int]
    warnings: tuple[str, ...]
    positive_prompt: str
    negative_prompt: str


@dataclass(frozen=True, slots=True)
class CompositionResult:
    """Complete public result returned by application services and adapters."""

    rendered: RenderedPrompt
    manifest: PromptManifest
    manifest_json: str
    summary: str
    seed_used: int
    issues: tuple[ValidationIssue, ...] = ()
