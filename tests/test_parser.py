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

    def test_profile_invariants_are_rejected_at_the_contract_boundary(self) -> None:
        cases: list[tuple[str, str, object]] = []

        empty_sections = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        empty_sections["sections"] = {}
        empty_sections["section_order"] = []
        cases.append(("empty sections", "at least one section", empty_sections))

        duplicate_order = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        duplicate_order["section_order"] = ["subject", "subject"]
        cases.append(("duplicate order", "duplicate section IDs", duplicate_order))

        incomplete_order = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        incomplete_order["section_order"] = []
        cases.append(("incomplete order", "list every section", incomplete_order))

        excessive_minimum = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        excessive_minimum["minimum_sections"] = 2
        cases.append(("minimum sections", "cannot exceed", excessive_minimum))

        empty_positive = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        cast(dict[str, object], empty_positive["templates"])["positive"] = " "
        cases.append(("empty positive", "cannot be empty", empty_positive))

        missing_fixed_default = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        section = cast(
            dict[str, object],
            cast(dict[str, object], missing_fixed_default["sections"])["subject"],
        )
        del section["default"]
        cases.append(("fixed default", "required when mode is fixed", missing_fixed_default))

        disabled_required = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        cast(dict[str, object], cast(dict[str, object], disabled_required["sections"])["subject"])[
            "mode"
        ] = "disabled"
        cases.append(("required disabled", "cannot be disabled", disabled_required))

        malformed_template = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        cast(dict[str, object], malformed_template["templates"])["positive"] = "{subject"
        cases.append(("malformed template", "invalid template", malformed_template))

        invalid_version = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        invalid_version["version"] = "latest"
        cases.append(("semantic version", "semantic version", invalid_version))

        invalid_order_type = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        invalid_order_type["section_order"] = "subject"
        cases.append(("order type", "JSON array", invalid_order_type))

        invalid_display_name = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        invalid_display_name["display_name"] = ""
        cases.append(("display name", "non-empty string", invalid_display_name))

        invalid_optional_bool = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        invalid_optional_bool["allow_empty_negative"] = "yes"
        cases.append(("optional bool", "must be a boolean", invalid_optional_bool))

        zero_minimum = cast(dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json")))
        zero_minimum["minimum_sections"] = 0
        cases.append(("positive integer", "greater than zero", zero_minimum))

        invalid_template_value = cast(
            dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json"))
        )
        cast(dict[str, object], invalid_template_value["templates"])["negative"] = 1
        cases.append(("template value", "only string values", invalid_template_value))

        invalid_mode = cast(dict[str, object], deepcopy(_fixture("valid", "profile-minimal.json")))
        cast(dict[str, object], cast(dict[str, object], invalid_mode["sections"])["subject"])[
            "mode"
        ] = "surprise"
        cases.append(("enum", "must be one of", invalid_mode))

        for name, message, data in cases:
            with self.subTest(name=name):
                with self.assertRaisesRegex(SchemaValidationError, message):
                    parse_profile(data)

    def test_library_rule_and_option_invariants_are_rejected(self) -> None:
        empty = cast(dict[str, object], deepcopy(_fixture("valid", "library-minimal.json")))
        empty["options"] = []
        with self.assertRaisesRegex(SchemaValidationError, "at least one option"):
            parse_library(empty)

        duplicate_tags = cast(
            dict[str, object], deepcopy(_fixture("valid", "library-minimal.json"))
        )
        option = cast(list[dict[str, object]], duplicate_tags["options"])[0]
        option["tags"] = ["adult", "adult"]
        with self.assertRaisesRegex(SchemaValidationError, "duplicate tags"):
            parse_library(duplicate_tags)

        missing_condition_value = cast(
            dict[str, object], deepcopy(_fixture("valid", "library-minimal.json"))
        )
        option = cast(list[dict[str, object]], missing_condition_value["options"])[0]
        option["requires"] = [{"field": "subject", "operator": "equals"}]
        with self.assertRaisesRegex(SchemaValidationError, "value: is required"):
            parse_library(missing_condition_value)

        invalid_preference = cast(
            dict[str, object], deepcopy(_fixture("valid", "library-minimal.json"))
        )
        option = cast(list[dict[str, object]], invalid_preference["options"])[0]
        option["prefer"] = [{"field": "subject", "operator": "present", "multiplier": 0}]
        with self.assertRaisesRegex(SchemaValidationError, "greater than zero"):
            parse_library(invalid_preference)

    def test_configuration_numeric_and_fixed_constraints_are_rejected(self) -> None:
        cases: list[tuple[str, str, object]] = []

        invalid_master_seed = cast(
            dict[str, object], deepcopy(_fixture("valid", "configuration-minimal.json"))
        )
        invalid_master_seed["master_seed"] = -1
        cases.append(("master seed range", r"between 0 and 2\^64-1", invalid_master_seed))

        null_batch = cast(
            dict[str, object], deepcopy(_fixture("valid", "configuration-minimal.json"))
        )
        null_batch["batch_index"] = None
        cases.append(("null batch", "must be an integer", null_batch))

        negative_batch = cast(
            dict[str, object], deepcopy(_fixture("valid", "configuration-minimal.json"))
        )
        negative_batch["batch_index"] = -1
        cases.append(("negative batch", "must be non-negative", negative_batch))

        invalid_group_seed = cast(
            dict[str, object], deepcopy(_fixture("valid", "configuration-minimal.json"))
        )
        cast(dict[str, object], cast(dict[str, object], invalid_group_seed["groups"])["identity"])[
            "seed"
        ] = -1
        cases.append(("group seed", r"between 0 and 2\^64-1", invalid_group_seed))

        missing_fixed_value = cast(
            dict[str, object], deepcopy(_fixture("valid", "configuration-minimal.json"))
        )
        del cast(
            dict[str, object], cast(dict[str, object], missing_fixed_value["fields"])["subject"]
        )["value"]
        cases.append(("fixed field", "required when mode is fixed", missing_fixed_value))

        invalid_profile_version = cast(
            dict[str, object], deepcopy(_fixture("valid", "configuration-minimal.json"))
        )
        invalid_profile_version["profile_version"] = "latest"
        cases.append(("profile version", "semantic version", invalid_profile_version))

        for name, message, data in cases:
            with self.subTest(name=name):
                with self.assertRaisesRegex(SchemaValidationError, message):
                    parse_configuration(data)


if __name__ == "__main__":
    unittest.main()
