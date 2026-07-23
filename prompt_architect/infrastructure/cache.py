"""Small content-aware file cache with explicit test invalidation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar

_T = TypeVar("_T")


@dataclass(frozen=True, slots=True)
class FileSignature:
    """Stable file identity used to invalidate parsed objects."""

    resolved_path: Path
    mtime_ns: int
    size: int
    content_hash: str


@dataclass(frozen=True, slots=True)
class CacheEntry(Generic[_T]):
    """One parsed value and the exact signature it came from."""

    signature: FileSignature
    value: _T


class FileObjectCache:
    """Type-erased cache keyed by a resolved authorized path."""

    def __init__(self) -> None:
        self._entries: dict[Path, CacheEntry[object]] = {}

    def get(self, signature: FileSignature) -> object | None:
        """Return a value only when every signature component still matches."""
        entry = self._entries.get(signature.resolved_path)
        if entry is None or entry.signature != signature:
            return None
        return entry.value

    def put(self, signature: FileSignature, value: object) -> None:
        """Store a parsed immutable value."""
        self._entries[signature.resolved_path] = CacheEntry(signature, value)

    def clear(self) -> None:
        """Remove all entries; primarily used by tests and explicit reload."""
        self._entries.clear()

    @property
    def size(self) -> int:
        """Return the number of cached paths."""
        return len(self._entries)
