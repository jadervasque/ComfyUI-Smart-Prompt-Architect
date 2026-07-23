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
from prompt_architect.domain.models import (
    CatalogIndexDefinition,
    CatalogPackDefinition,
    CatalogPackReference,
    LibraryDefinition,
    ProfileDefinition,
)
from prompt_architect.domain.parser import (
    parse_catalog_index,
    parse_catalog_pack,
    parse_library,
    parse_profile,
)
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

    def load_library_for_profile(
        self, profile: ProfileDefinition, library_id: str
    ) -> LibraryDefinition: ...

    def load_catalog_index(self) -> CatalogIndexDefinition: ...


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
        """Load a V2 logical library when available, otherwise a legacy library."""
        safe_id = validate_data_id(library_id, kind="library")
        override = self._libraries.get(safe_id)
        if override is not None:
            return override
        user_source = self._find_optional_source("libraries", safe_id, self._users)
        if user_source is not None:
            try:
                return cast(
                    LibraryDefinition,
                    self._load_file_from_source(
                        *user_source,
                        "libraries",
                        safe_id,
                        parse_library,
                    ),
                )
            except PromptArchitectError as error:
                raise LibraryLoadError(str(error)) from error
        catalog = self._optional_catalog()
        if catalog is not None and safe_id in catalog[1].libraries:
            return self._load_catalog_library(catalog[0], catalog[1], safe_id)
        try:
            return cast(
                LibraryDefinition,
                self._load_file("libraries", safe_id, parse_library),
            )
        except PromptArchitectError as error:
            raise LibraryLoadError(str(error)) from error

    def load_library_for_profile(
        self, profile: ProfileDefinition, library_id: str
    ) -> LibraryDefinition:
        """Load a profile-filtered logical library with declared safety constraints."""
        safe_id = validate_data_id(library_id, kind="library")
        override = self._libraries.get(safe_id)
        if override is not None:
            return override
        if profile.catalog_version is None:
            return self.load_library(safe_id)
        catalog = self._optional_catalog()
        if catalog is None:
            raise LibraryLoadError(
                f"profile {profile.id!r} requires Catalog {profile.catalog_version}, "
                "but catalogs/index.json is missing"
            )
        root, index = catalog
        if index.version != profile.catalog_version:
            raise LibraryLoadError(
                f"profile {profile.id!r} requires catalog {profile.catalog_version}, "
                f"loaded {index.version}"
            )
        return self._load_catalog_library(
            root,
            index,
            safe_id,
            enabled_packs=frozenset(profile.enabled_packs),
            allowed_safety=frozenset(profile.allowed_safety_classes),
        )

    def clear_cache(self) -> None:
        """Explicitly clear parsed file objects."""
        self._cache.clear()

    def load_catalog_index(self) -> CatalogIndexDefinition:
        """Load the highest-precedence validated Catalog V2 index."""
        catalog = self._optional_catalog()
        if catalog is None:
            raise LibraryLoadError("catalogs/index.json is missing")
        return catalog[1]

    @property
    def cache_size(self) -> int:
        """Expose cache size for diagnostics and tests, not cached contents."""
        return self._cache.size

    def _load_file(self, category: str, data_id: str, parser: object) -> object:
        source, path = self._find_source(category, data_id)
        return self._load_file_from_source(source, path, category, data_id, parser)

    def _load_file_from_source(
        self,
        source: DataRoot,
        path: Path,
        category: str,
        data_id: str,
        parser: object,
    ) -> object:
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

    def _optional_catalog(self) -> tuple[DataRoot, CatalogIndexDefinition] | None:
        for root in (*self._users, self._internal):
            path = root.path / "catalogs" / "index.json"
            if not path.is_file():
                continue
            label = f"{root.label}/catalogs/index.json"
            content = read_json_bytes(path, label, max_bytes=self._max_json_bytes)
            signature = self._signature(path, content)
            cached = self._cache.get(signature)
            if cached is None:
                cached = parse_catalog_index(decode_json_object(content, label))
                self._cache.put(signature, cached)
            return root, cast(CatalogIndexDefinition, cached)
        return None

    def _load_catalog_library(
        self,
        root: DataRoot,
        index: CatalogIndexDefinition,
        library_id: str,
        *,
        enabled_packs: frozenset[str] = frozenset(),
        allowed_safety: frozenset[str] = frozenset(
            {"general", "fashion-mature", "dark-atmospheric", "experimental"}
        ),
    ) -> LibraryDefinition:
        logical = index.libraries.get(library_id)
        if logical is None:
            raise LibraryLoadError(f"catalog library {library_id!r} is not declared")
        references = {reference.id: reference for reference in index.packs}
        selected_ids = tuple(
            pack_id
            for pack_id in logical.pack_ids
            if (not enabled_packs or pack_id in enabled_packs)
            and references[pack_id].safety in allowed_safety
            and references[pack_id].status != "deprecated"
        )
        if not selected_ids:
            raise LibraryLoadError(
                f"catalog library {library_id!r} has no enabled packs for this profile"
            )
        selected_set = frozenset(selected_ids)
        for pack_id in selected_ids:
            missing = set(references[pack_id].dependencies) - selected_set
            if missing:
                raise LibraryLoadError(
                    f"pack {pack_id!r} requires disabled packs: {', '.join(sorted(missing))}"
                )
        ordered = sorted(
            (references[pack_id] for pack_id in selected_ids),
            key=lambda reference: (reference.priority, reference.id),
        )
        packs = tuple(self._load_catalog_pack(root, reference) for reference in ordered)
        option_ids: set[str] = set()
        semantic_keys: set[str] = set()
        options = []
        for pack in packs:
            for option in pack.options:
                if option.id in option_ids:
                    raise LibraryLoadError(
                        f"catalog option ID collision in {library_id!r}: {option.id!r}"
                    )
                if option.semantic_key is not None and option.semantic_key in semantic_keys:
                    raise LibraryLoadError(
                        f"catalog semantic key collision in {library_id!r}: {option.semantic_key!r}"
                    )
                option_ids.add(option.id)
                if option.semantic_key is not None:
                    semantic_keys.add(option.semantic_key)
                options.append(option)
        fallback = logical.fallback_option_id
        if fallback not in option_ids:
            fallback = next(
                (pack.fallback_option_id for pack in packs if pack.fallback_option_id is not None),
                None,
            )
        if fallback is not None and fallback not in option_ids:
            raise LibraryLoadError(
                f"fallback {fallback!r} for catalog library {library_id!r} is disabled or missing"
            )
        return LibraryDefinition(
            schema_version="2.0",
            id=logical.id,
            version=index.version,
            display_name=logical.display_name,
            options=tuple(options),
            fallback_option_id=fallback,
            catalog_version=index.version,
            pack_versions={pack.id: pack.version for pack in packs},
        )

    def _load_catalog_pack(
        self, root: DataRoot, reference: CatalogPackReference
    ) -> CatalogPackDefinition:
        catalogs_root = (root.path / "catalogs").resolve(strict=False)
        path = (catalogs_root / Path(reference.path)).resolve(strict=False)
        try:
            path.relative_to(catalogs_root)
        except ValueError as error:
            raise LibraryLoadError("catalog pack path escapes its authorized root") from error
        label = f"{root.label}/catalogs/{reference.path}"
        content = read_json_bytes(path, label, max_bytes=self._max_json_bytes)
        signature = self._signature(path, content)
        cached = self._cache.get(signature)
        if cached is None:
            cached = parse_catalog_pack(decode_json_object(content, label))
            self._cache.put(signature, cached)
        pack = cast(CatalogPackDefinition, cached)
        expected = (
            reference.id,
            reference.library,
            reference.domain,
            reference.version,
            reference.language,
            reference.status,
            reference.safety,
        )
        actual = (
            pack.id,
            pack.library,
            pack.domain,
            pack.version,
            pack.language,
            pack.status,
            pack.safety,
        )
        if actual != expected:
            raise LibraryLoadError(f"{label}: metadata does not match catalogs/index.json")
        return pack

    @staticmethod
    def _signature(path: Path, content: bytes) -> FileSignature:
        stat = path.stat()
        return FileSignature(path, stat.st_mtime_ns, len(content), sha256_bytes(content))

    def _find_source(self, category: str, data_id: str) -> tuple[DataRoot, Path]:
        for root in (*self._users, self._internal):
            path = data_file(root.path, category, data_id)
            if path.is_file():
                return root, path
        label = relative_label("authorized-roots", category, data_id)
        raise SchemaValidationError(f"{label}: file not found")

    @staticmethod
    def _find_optional_source(
        category: str,
        data_id: str,
        roots: Sequence[DataRoot],
    ) -> tuple[DataRoot, Path] | None:
        for root in roots:
            path = data_file(root.path, category, data_id)
            if path.is_file():
                return root, path
        return None

    def _validate_profile_references(self, profile: ProfileDefinition) -> None:
        unknown_profile_fallbacks = set(profile.profile_fallbacks) - set(profile.sections)
        if unknown_profile_fallbacks:
            names = ", ".join(sorted(unknown_profile_fallbacks))
            raise SchemaValidationError(f"profile_fallbacks reference unknown sections: {names}")
        for section_id in profile.section_order:
            section = profile.sections[section_id]
            library = self.load_library_for_profile(profile, section.library)
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
