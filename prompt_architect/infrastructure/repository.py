"""Secure profile and library repository with deterministic precedence and caching."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

from prompt_architect.domain.exceptions import (
    LibraryLoadError,
    ProfileLoadError,
    PromptArchitectError,
    SchemaValidationError,
)
from prompt_architect.domain.models import LibraryDefinition, ProfileDefinition
from prompt_architect.domain.parser import parse_library, parse_profile
from prompt_architect.infrastructure.cache import FileObjectCache, FileSignature
from prompt_architect.infrastructure.hashing import sha256_bytes
from prompt_architect.infrastructure.json_loader import (
    DEFAULT_MAX_JSON_BYTES,
    decode_json_object,
    read_json_bytes,
)
from prompt_architect.infrastructure.paths import (
    authorized_root,
    data_file,
    relative_label,
    validate_data_id,
)


@dataclass(frozen=True, slots=True)
class ProfileSummary:
    """Safe metadata for profile listing APIs."""

    id: str
    version: str
    display_name: str
    language: str


class PromptDataRepository(Protocol):
    """Read-only data interface consumed by application services."""

    def list_profiles(self) -> Sequence[ProfileSummary]: ...

    def load_profile(self, profile_id: str) -> ProfileDefinition: ...

    def load_library(self, library_id: str) -> LibraryDefinition: ...


@dataclass(frozen=True, slots=True)
class DataRoot:
    """Trusted root and non-sensitive label used in diagnostics."""

    path: Path
    label: str


class JsonPromptDataRepository:
    """Read-only repository for connected overrides, user data, and bundled data."""

    def __init__(
        self,
        internal_root: Path,
        *,
        user_roots: Sequence[Path] = (),
        profile_overrides: Mapping[str, ProfileDefinition] | None = None,
        library_overrides: Mapping[str, LibraryDefinition] | None = None,
        max_json_bytes: int = DEFAULT_MAX_JSON_BYTES,
    ) -> None:
        if max_json_bytes <= 0:
            raise ValueError("max_json_bytes must be positive")
        self._internal = DataRoot(authorized_root(internal_root), "internal")
        self._users = tuple(
            DataRoot(authorized_root(root), f"user-{index + 1}")
            for index, root in enumerate(user_roots)
        )
        self._profiles = dict(profile_overrides or {})
        self._libraries = dict(library_overrides or {})
        self._max_json_bytes = max_json_bytes
        self._cache = FileObjectCache()

    def list_profiles(self) -> Sequence[ProfileSummary]:
        """List only profiles that fully validate, sorted by stable ID."""
        candidate_ids = set(self._profiles)
        for root in (*self._users, self._internal):
            directory = root.path / "profiles"
            if not directory.is_dir():
                continue
            for path in directory.glob("*.json"):
                try:
                    candidate_ids.add(validate_data_id(path.stem, kind="profile"))
                except PromptArchitectError:
                    continue
        summaries: list[ProfileSummary] = []
        for profile_id in sorted(candidate_ids):
            try:
                profile = self.load_profile(profile_id)
            except PromptArchitectError:
                continue
            summaries.append(
                ProfileSummary(
                    id=profile.id,
                    version=profile.version,
                    display_name=profile.display_name,
                    language=profile.language,
                )
            )
        return tuple(summaries)

    def load_profile(self, profile_id: str) -> ProfileDefinition:
        """Load a profile from the highest-precedence source and validate references."""
        safe_id = validate_data_id(profile_id, kind="profile")
        override = self._profiles.get(safe_id)
        if override is not None:
            profile = override
        else:
            try:
                profile = cast(
                    ProfileDefinition,
                    self._load_file("profiles", safe_id, parse_profile),
                )
            except PromptArchitectError as error:
                raise ProfileLoadError(str(error)) from error
        try:
            self._validate_profile_references(profile)
        except PromptArchitectError as error:
            raise ProfileLoadError(f"profile {safe_id!r}: {error}") from error
        return profile

    def load_library(self, library_id: str) -> LibraryDefinition:
        """Load a library from the highest-precedence source."""
        safe_id = validate_data_id(library_id, kind="library")
        override = self._libraries.get(safe_id)
        if override is not None:
            return override
        try:
            return cast(
                LibraryDefinition,
                self._load_file("libraries", safe_id, parse_library),
            )
        except PromptArchitectError as error:
            raise LibraryLoadError(str(error)) from error

    def clear_cache(self) -> None:
        """Explicitly clear parsed file objects."""
        self._cache.clear()

    @property
    def cache_size(self) -> int:
        """Expose cache size for diagnostics and tests, not cached contents."""
        return self._cache.size

    def _load_file(self, category: str, data_id: str, parser: object) -> object:
        source, path = self._find_source(category, data_id)
        label = relative_label(source.label, category, data_id)
        content = read_json_bytes(path, label, max_bytes=self._max_json_bytes)
        stat = path.stat()
        signature = FileSignature(path, stat.st_mtime_ns, len(content), sha256_bytes(content))
        cached = self._cache.get(signature)
        if cached is not None:
            return cached
        data = decode_json_object(content, label)
        if parser is parse_profile:
            parsed: object = parse_profile(data)
        elif parser is parse_library:
            parsed = parse_library(data)
        else:
            raise TypeError("unsupported repository parser")
        self._cache.put(signature, parsed)
        return parsed

    def _find_source(self, category: str, data_id: str) -> tuple[DataRoot, Path]:
        for root in (*self._users, self._internal):
            path = data_file(root.path, category, data_id)
            if path.is_file():
                return root, path
        label = relative_label("authorized-roots", category, data_id)
        raise SchemaValidationError(f"{label}: file not found")

    def _validate_profile_references(self, profile: ProfileDefinition) -> None:
        unknown_profile_fallbacks = set(profile.profile_fallbacks) - set(profile.sections)
        if unknown_profile_fallbacks:
            names = ", ".join(sorted(unknown_profile_fallbacks))
            raise SchemaValidationError(f"profile_fallbacks reference unknown sections: {names}")
        for section_id in profile.section_order:
            section = profile.sections[section_id]
            library = self.load_library(section.library)
            option_ids = {option.id for option in library.options}
            for label, option_id in (
                ("default", section.default),
                ("fallback", section.fallback),
                ("profile fallback", profile.profile_fallbacks.get(section_id)),
            ):
                if option_id is not None and option_id not in option_ids:
                    raise SchemaValidationError(
                        f"section {section_id!r} {label} references unknown option {option_id!r}"
                    )
            if (
                section.required
                and section.fallback is None
                and profile.profile_fallbacks.get(section_id) is None
                and library.fallback_option_id is None
            ):
                raise SchemaValidationError(
                    f"required section {section_id!r} has no section, profile, or library fallback"
                )


def bundled_repository(
    *,
    user_roots: Sequence[Path] = (),
    profile_overrides: Mapping[str, ProfileDefinition] | None = None,
    library_overrides: Mapping[str, LibraryDefinition] | None = None,
) -> JsonPromptDataRepository:
    """Create a repository rooted at packaged official data."""
    data_root = Path(__file__).resolve().parents[1] / "data"
    return JsonPromptDataRepository(
        data_root,
        user_roots=user_roots,
        profile_overrides=profile_overrides,
        library_overrides=library_overrides,
    )
