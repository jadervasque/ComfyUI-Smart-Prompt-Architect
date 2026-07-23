"""Domain-specific exceptions with safe user-facing messages."""


class PromptArchitectError(Exception):
    """Base class for expected Prompt Architect failures."""


class ConfigurationError(PromptArchitectError):
    """The effective node configuration is invalid."""


class ProfileLoadError(PromptArchitectError):
    """A profile could not be loaded or parsed."""


class LibraryLoadError(PromptArchitectError):
    """A library could not be loaded or parsed."""


class SchemaValidationError(PromptArchitectError):
    """Declarative JSON data violates a versioned contract."""


class SelectionError(PromptArchitectError):
    """No valid deterministic selection could be produced."""


class RuleConflictError(PromptArchitectError):
    """Compatibility rules conflict, especially with a fixed user value."""


class RenderError(PromptArchitectError):
    """A prompt template could not be rendered safely."""


class FinalPromptValidationError(PromptArchitectError):
    """Rendered prompt output violates final safety or completeness rules."""
