"""Pure node-input parsing tests that do not require ComfyUI imports."""

import json
import unittest
from pathlib import Path

from prompt_architect.comfy.schemas import (
    MAX_NODE_JSON_BYTES,
    build_node_configuration,
    node_input_fingerprint,
    parse_profile_override,
)
from prompt_architect.domain.enums import FieldMode
from prompt_architect.domain.exceptions import ConfigurationError, SchemaValidationError
from prompt_architect.domain.models import NodeConfiguration


def _build(
    *,
    configuration_json: str = "{}",
    external_context_json: str = "",
    identity_lock: bool = True,
) -> NodeConfiguration:
    return build_node_configuration(
        profile="portrait",
        seed=123,
        generation_mode="balanced",
        identity_lock=identity_lock,
        configuration_json=configuration_json,
        positive_prefix="",
        positive_suffix="",
        negative_prefix="",
        negative_suffix="",
        external_context_json=external_context_json,
        batch_index=0,
    )


class NodeSchemaTests(unittest.TestCase):
    """Visible and connected input precedence remains explicit and bounded."""

    def test_visible_inputs_override_serialized_core_values(self) -> None:
        serialized = json.dumps(
            {
                "schema_version": "1.0",
                "profile_id": "dataset",
                "mode": "strict",
                "master_seed": 999,
            }
        )
        configuration = _build(configuration_json=serialized)
        self.assertEqual(configuration.profile_id, "portrait")
        self.assertEqual(configuration.master_seed, 123)
        self.assertEqual(configuration.mode.value, "balanced")
        self.assertEqual(configuration.schema_version, "1.1")

    def test_custom_field_survives_node_input_merge(self) -> None:
        configuration = _build(
            configuration_json=json.dumps(
                {
                    "schema_version": "1.1",
                    "fields": {
                        "face": {
                            "mode": "custom",
                            "value": "A heart-shaped adult face with a small beauty mark",
                        }
                    },
                }
            )
        )
        self.assertEqual(configuration.fields["face"].mode, FieldMode.CUSTOM)
        self.assertIn("beauty mark", configuration.fields["face"].value or "")

    def test_external_context_has_fixed_precedence(self) -> None:
        configuration = _build(external_context_json='{"outfit":"formal-suit"}')
        self.assertEqual(configuration.fields["outfit"].mode, FieldMode.FIXED)
        self.assertEqual(configuration.fields["outfit"].value, "formal-suit")

    def test_identity_lock_materializes_explicit_seed(self) -> None:
        first = _build()
        second = _build()
        self.assertTrue(first.groups["identity"].locked)
        self.assertIsNotNone(first.groups["identity"].seed)
        self.assertEqual(first.groups["identity"], second.groups["identity"])

    def test_invalid_external_value_and_oversized_json_fail(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "must be a non-empty option ID"):
            _build(external_context_json='{"outfit":1}')
        oversized = "{" + (" " * MAX_NODE_JSON_BYTES) + "}"
        with self.assertRaisesRegex(SchemaValidationError, "exceeds"):
            _build(configuration_json=oversized)

    def test_profile_override_is_typed_and_duplicate_keys_fail(self) -> None:
        fixture = (Path(__file__).parent / "fixtures" / "valid" / "profile-minimal.json").read_text(
            encoding="utf-8"
        )
        override = parse_profile_override(fixture)
        if override is None:
            self.fail("non-empty profile override unexpectedly parsed as None")
        self.assertEqual(override.id, "portrait")
        with self.assertRaisesRegex(SchemaValidationError, "duplicate JSON key"):
            parse_profile_override('{"schema_version":"1.0","schema_version":"1.0"}')

    def test_fingerprint_is_stable_and_input_sensitive(self) -> None:
        first = node_input_fingerprint({"profile": "portrait", "seed": 1}, "data")
        second = node_input_fingerprint({"seed": 1, "profile": "portrait"}, "data")
        changed = node_input_fingerprint({"profile": "portrait", "seed": 2}, "data")
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)


if __name__ == "__main__":
    unittest.main()
