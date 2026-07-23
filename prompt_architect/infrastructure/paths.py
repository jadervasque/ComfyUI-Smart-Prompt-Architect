"""Allowlisted path construction that never accepts arbitrary file paths."""

import re
from pathlib import Path

from prompt_architect.domain.exceptions import ConfigurationError

_SAFE_ID = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_CATEGORIES = frozenset({"profiles", "libraries"})


def validate_data_id(value: str, *, kind: str = "data") -> str:
    """Validate and return a lowercase kebab-case data identifier."""
    if not _SAFE_ID.fullmatch(value):
        raise ConfigurationError(f"Invalid {kind} ID {value!r}; expected lowercase kebab-case")
    return value


def authorized_root(path: Path) -> Path:
    """Resolve a root supplied by trusted host configuration."""
    return path.expanduser().resolve(strict=False)


def data_file(root: Path, category: str, data_id: str) -> Path:
    """Construct a JSON path inside an authorized root and verify containment."""
    if category not in _CATEGORIES:
        raise ConfigurationError(f"Unsupported data category {category!r}")
    safe_id = validate_data_id(data_id, kind=category[:-1])
    resolved_root = authorized_root(root)
    candidate = (resolved_root / category / f"{safe_id}.json").resolve(strict=False)
    try:
        candidate.relative_to(resolved_root)
    except ValueError as error:
        raise ConfigurationError("Resolved data path escapes its authorized root") from error
    return candidate


def relative_label(source_name: str, category: str, data_id: str) -> str:
    """Return a safe diagnostic label without exposing an absolute host path."""
    safe_id = validate_data_id(data_id, kind=category[:-1])
    return f"{source_name}/{category}/{safe_id}.json"
