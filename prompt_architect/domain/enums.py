"""Enumerations shared by the Prompt Architect domain."""

from enum import Enum


class StringEnum(str, Enum):
    """String-valued enum with stable JSON-compatible values."""

    def __str__(self) -> str:
        return str(self.value)


class FieldMode(StringEnum):
    """How a section or field obtains its value."""

    DISABLED = "disabled"
    FIXED = "fixed"
    RANDOM = "random"
    INHERIT = "inherit"


class GenerationMode(StringEnum):
    """Selection strictness and diversity strategy."""

    STRICT = "strict"
    BALANCED = "balanced"
    CREATIVE = "creative"
    DATASET = "dataset"
    SEQUENTIAL = "sequential"


class RuleType(StringEnum):
    """Supported compatibility rule categories."""

    REQUIRES = "requires"
    EXCLUDES = "excludes"
    IMPLIES = "implies"
    PREFER = "prefer"


class RuleOperator(StringEnum):
    """Declarative condition operators; arbitrary expressions are forbidden."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS_TAG = "contains_tag"
    MISSING = "missing"
    PRESENT = "present"


class IssueSeverity(StringEnum):
    """Severity of a structured validation issue."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SelectionSource(StringEnum):
    """Origin of a selected option."""

    FIXED = "fixed"
    RANDOM = "random"
    INHERITED = "inherited"
    IMPLIED = "implied"
    FALLBACK = "fallback"


class OptionStatus(StringEnum):
    """Lifecycle status of a library option."""

    ACTIVE = "active"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"
