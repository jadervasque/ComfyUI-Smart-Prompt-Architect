"""Bounded UTF-8 JSON loading with duplicate-key rejection."""

import json
from pathlib import Path
from typing import Any

from prompt_architect.domain.exceptions import SchemaValidationError

DEFAULT_MAX_JSON_BYTES = 1_048_576


def read_json_bytes(path: Path, label: str, *, max_bytes: int = DEFAULT_MAX_JSON_BYTES) -> bytes:
    """Read a bounded regular JSON file from an already allowlisted path."""
    try:
        stat = path.stat()
    except OSError as error:
        raise SchemaValidationError(f"{label}: file is not readable") from error
    if not path.is_file():
        raise SchemaValidationError(f"{label}: expected a regular file")
    if stat.st_size > max_bytes:
        raise SchemaValidationError(f"{label}: JSON exceeds {max_bytes} byte limit")
    try:
        content = path.read_bytes()
    except OSError as error:
        raise SchemaValidationError(f"{label}: file is not readable") from error
    if len(content) > max_bytes:
        raise SchemaValidationError(f"{label}: JSON exceeds {max_bytes} byte limit")
    return content


def decode_json_object(content: bytes, label: str) -> dict[str, object]:
    """Decode one UTF-8 JSON object and reject duplicate keys and non-finite numbers."""

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise SchemaValidationError(f"{label}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    def invalid_constant(value: str) -> object:
        raise SchemaValidationError(f"{label}: non-finite JSON number {value!r} is forbidden")

    try:
        decoded = json.loads(
            content.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=invalid_constant,
        )
    except UnicodeDecodeError as error:
        raise SchemaValidationError(f"{label}: file must be UTF-8") from error
    except json.JSONDecodeError as error:
        raise SchemaValidationError(
            f"{label}: invalid JSON at line {error.lineno}, column {error.colno}"
        ) from error
    if not isinstance(decoded, dict):
        raise SchemaValidationError(f"{label}: top-level JSON value must be an object")
    return decoded
