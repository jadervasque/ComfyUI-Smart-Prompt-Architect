"""Contract parser tests for valid and invalid declarative data."""

import json
import unittest
from copy import deepcopy
from pathlib import Path
from typing import cast

from prompt_architect.domain.enums import FieldMode, GenerationMode
from prompt_architect.domain.exceptions import SchemaValidationError
from prompt_architect.domain.parser import parse_configuration, parse_library, parse_profile

_FIXTURES = Path(__file__).parent / "fixtures"


def _fixture(*parts: str) -> object:
    return json.loads(_FIXTURES.joinpath(*parts).read_text(encoding="utf-8"))


class ParserContractTests(unittest.TestCase):
    """Ensure valid data becomes typed and invalid data fails specifically."""

    def test_minimal_profile_is_typed(self) -> None:
        profile = parse_profile(_fixture("valid", "profile-minimal.json"))
        self.assertEqual(profile.id, "portrait")
        self.assertEqual(profile.sections["subject"].mode, FieldMode.FIXED)

    def test_minimal_library_is_typed(self) -> None:
        library = parse_library(_fixture("valid", "library-minimal.json"))
        self.assertEqual(library.fallback_option_id, "adult-person")
        self.assertEqual(library.options[0].tags, ("adult", "person"))

    def test_minimal_configuration_is_typed(self) -> None:
        configuration = parse_configuration(_fixture("valid", "configuration-minimal.json"))
        self.assertEqual(configuration.mode, GenerationMode.BALANCED)
        self.assertEqual(configuration.groups["identity"].seed, 42)

    def test_duplicate_option_id_is_rejected(self) -> None:
        with self.assertRaisesRegex(SchemaValidationError, "duplicate option IDs"):
            parse_library(_fixture("invalid", "library-duplicate-id.json"))

    def test_negative_weight_is_rejected(self) -> None:
        with self.assertRaisesRegex(SchemaValidationError, "finite and non-negative"):
            parse_library(_fixture("invalid", "library-negative-weight.json"))

    def test_non_finite_weight_is_rejected(self) -> None:
        data = cast(dict[str, object], deepcopy(_fixture("valid", "library-minimal.json")))
        options = cast(list[dict[str, object]], data["options"])
        options[0]["weight"] = float("inf")
        with self.assertRaisesRegex(SchemaValidationError, "finite and non-negative"):
            parse_library(data)

    def test_missing_fallback_is_rejected(self) -> None:
        with self.assertRaisesRegex(SchemaValidationError, "unknown option"):
            parse_library(_fixture("invalid", "library-missing-fallback.json"))

    def test_unknown_schema_is_rejected(self) -> None:
        with self.assertRaisesRegex(SchemaValidationError, "unsupported schema version"):
            parse_library(_fixture("invalid", "library-unknown-schema.json"))

    def test_missing_essential_profile_field_is_rejected(self) -> None:
        data = cast(dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json")))
        del data["templates"]
        with self.assertRaisesRegex(SchemaValidationError, "profile.templates: is required"):
            parse_profile(data)

    def test_unknown_field_is_rejected(self) -> None:
        data = cast(dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json")))
        data["surprise"] = True
        with self.assertRaisesRegex(SchemaValidationError, "unknown fields: surprise"):
            parse_profile(data)

    def test_unknown_template_placeholder_is_rejected(self) -> None:
        data = cast(dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json")))
        templates = cast(dict[str, object], data["templates"])
        templates["positive"] = "{subject} {unknown}."
        with self.assertRaisesRegex(SchemaValidationError, "unsupported placeholders: unknown"):
            parse_profile(data)


if __name__ == "__main__":
    unittest.main()
