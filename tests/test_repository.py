"""Security, precedence, cache, and reload tests for the JSON repository."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from prompt_architect.domain.exceptions import (
    ConfigurationError,
    LibraryLoadError,
    ProfileLoadError,
    SchemaValidationError,
)
from prompt_architect.domain.parser import parse_library
from prompt_architect.infrastructure.json_loader import decode_json_object, read_json_bytes
from prompt_architect.infrastructure.paths import data_file
from prompt_architect.infrastructure.repository import JsonPromptDataRepository


def _library(text: str = "Internal adult person") -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "id": "subjects",
        "version": "1.0.0",
        "display_name": "Subjects",
        "options": [{"id": "adult-person", "text": text, "weight": 1.0}],
        "fallback_option_id": "adult-person",
    }


def _profile(profile_id: str = "portrait") -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "id": profile_id,
        "version": "1.0.0",
        "display_name": profile_id.title(),
        "language": "en",
        "minimum_sections": 1,
        "minimum_prompt_characters": 5,
        "max_selection_attempts": 5,
        "section_order": ["subject"],
        "sections": {
            "subject": {
                "required": True,
                "library": "subjects",
                "mode": "fixed",
                "default": "adult-person",
                "group": "identity",
                "fallback": "adult-person",
            }
        },
        "templates": {"positive": "{subject}."},
    }


def _write(root: Path, category: str, data_id: str, data: object) -> Path:
    directory = root / category
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{data_id}.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


class RepositoryTests(unittest.TestCase):
    """Exercise repository behavior only within temporary authorized roots."""

    def test_traversal_and_absolute_ids_are_rejected(self) -> None:
        root = Path("authorized")
        for invalid in ("../secret", "C:/secret", "/secret", "UPPER"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ConfigurationError):
                    data_file(root, "profiles", invalid)

    def test_unknown_category_is_rejected(self) -> None:
        with self.assertRaises(ConfigurationError):
            data_file(Path("authorized"), "secrets", "portrait")

    def test_bounded_loader_rejects_large_file_without_leaking_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.json"
            path.write_bytes(b"{}" * 10)
            with self.assertRaisesRegex(SchemaValidationError, "safe/large.json") as captured:
                read_json_bytes(path, "safe/large.json", max_bytes=5)
            self.assertNotIn(directory, str(captured.exception))

    def test_duplicate_json_keys_are_rejected(self) -> None:
        with self.assertRaisesRegex(SchemaValidationError, "duplicate JSON key 'id'"):
            decode_json_object(b'{"id":"one","id":"two"}', "internal/test.json")

    def test_user_root_precedes_internal_data(self) -> None:
        with (
            tempfile.TemporaryDirectory() as internal_dir,
            tempfile.TemporaryDirectory() as user_dir,
        ):
            internal = Path(internal_dir)
            user = Path(user_dir)
            _write(internal, "libraries", "subjects", _library("Internal"))
            _write(user, "libraries", "subjects", _library("User data"))
            repository = JsonPromptDataRepository(internal, user_roots=(user,))
            self.assertEqual(repository.load_library("subjects").options[0].text, "User data")

    def test_connected_override_precedes_files(self) -> None:
        with tempfile.TemporaryDirectory() as internal_dir:
            internal = Path(internal_dir)
            _write(internal, "libraries", "subjects", _library("Internal"))
            override = parse_library(_library("Connected override"))
            repository = JsonPromptDataRepository(
                internal, library_overrides={"subjects": override}
            )
            self.assertEqual(
                repository.load_library("subjects").options[0].text,
                "Connected override",
            )

    def test_invalid_user_file_does_not_fall_back_silently(self) -> None:
        with (
            tempfile.TemporaryDirectory() as internal_dir,
            tempfile.TemporaryDirectory() as user_dir,
        ):
            internal = Path(internal_dir)
            user = Path(user_dir)
            _write(internal, "libraries", "subjects", _library("Internal"))
            _write(user, "libraries", "subjects", {"broken": True})
            repository = JsonPromptDataRepository(internal, user_roots=(user,))
            with self.assertRaises(LibraryLoadError):
                repository.load_library("subjects")

    def test_cache_reloads_when_hash_changes_but_metadata_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as internal_dir:
            internal = Path(internal_dir)
            path = _write(internal, "libraries", "subjects", _library("Alpha"))
            repository = JsonPromptDataRepository(internal)
            self.assertEqual(repository.load_library("subjects").options[0].text, "Alpha")
            original = path.stat()
            updated = path.read_text(encoding="utf-8").replace("Alpha", "Bravo")
            path.write_text(updated, encoding="utf-8")
            os.utime(path, ns=(original.st_atime_ns, original.st_mtime_ns))
            self.assertEqual(repository.load_library("subjects").options[0].text, "Bravo")
            self.assertEqual(repository.cache_size, 1)
            repository.clear_cache()
            self.assertEqual(repository.cache_size, 0)

    def test_profile_references_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as internal_dir:
            internal = Path(internal_dir)
            _write(internal, "libraries", "subjects", _library())
            profile = _profile()
            sections = profile["sections"]
            self.assertIsInstance(sections, dict)
            sections["subject"]["fallback"] = "missing"  # type: ignore[index]
            _write(internal, "profiles", "portrait", profile)
            repository = JsonPromptDataRepository(internal)
            with self.assertRaisesRegex(ProfileLoadError, "unknown option 'missing'"):
                repository.load_profile("portrait")

    def test_list_profiles_is_sorted_and_omits_invalid_data(self) -> None:
        with tempfile.TemporaryDirectory() as internal_dir:
            internal = Path(internal_dir)
            _write(internal, "libraries", "subjects", _library())
            _write(internal, "profiles", "zeta", _profile("zeta"))
            _write(internal, "profiles", "alpha", _profile("alpha"))
            _write(internal, "profiles", "broken", {"schema_version": "1.0"})
            repository = JsonPromptDataRepository(internal)
            self.assertEqual(
                [summary.id for summary in repository.list_profiles()],
                ["alpha", "zeta"],
            )


if __name__ == "__main__":
    unittest.main()
