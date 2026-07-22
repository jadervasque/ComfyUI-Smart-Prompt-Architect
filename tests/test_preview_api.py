"""Read-only preview API service tests without ComfyUI or aiohttp."""

import json
import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Any, cast

from prompt_architect.application.preview_api import (
    MAX_PREVIEW_PAYLOAD_BYTES,
    decode_preview_payload,
    get_profile,
    list_profiles,
    preview,
    validate,
)
from prompt_architect.domain.exceptions import ConfigurationError


def _configuration(seed: int = 7) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "profile_id": "portrait",
        "profile_version": "1.0.0",
        "mode": "balanced",
        "master_seed": seed,
        "groups": {"identity": {"locked": True, "seed": 123}},
        "fields": {},
        "overrides": {},
        "batch_index": 0,
    }


class PreviewApiTests(unittest.TestCase):
    def test_lists_profiles_and_profile_options_without_paths(self) -> None:
        listing = list_profiles()
        profiles = cast(list[dict[str, Any]], listing["profiles"])
        self.assertEqual(
            [item["id"] for item in profiles], ["dataset", "portrait", "virtual-model"]
        )
        detail = get_profile("portrait")
        profile = cast(dict[str, Any], detail["profile"])
        self.assertEqual(profile["id"], "portrait")
        serialized = json.dumps(detail)
        self.assertNotIn("E:\\", serialized)
        self.assertIn("options", serialized)

    def test_preview_and_validate_use_authoritative_pipeline(self) -> None:
        result = preview({"configuration": _configuration()})
        self.assertTrue(result["positive_prompt"])
        self.assertEqual(result["seed_used"], 7)
        validation = validate(_configuration())
        self.assertTrue(validation["valid"])
        manifest = cast(dict[str, Any], result["manifest"])
        self.assertEqual(validation["configuration_hash"], manifest["configuration_hash"])

    def test_invalid_id_and_oversized_payload_fail(self) -> None:
        with self.assertRaises(ConfigurationError):
            get_profile("../portrait")
        with self.assertRaisesRegex(ValueError, "exceeds"):
            decode_preview_payload(b" " * (MAX_PREVIEW_PAYLOAD_BYTES + 1))

    def test_duplicate_json_keys_fail(self) -> None:
        with self.assertRaisesRegex(Exception, "duplicate JSON key"):
            decode_preview_payload(b'{"configuration":{},"configuration":{}}')

    def test_concurrent_previews_are_identical(self) -> None:
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(lambda _: preview(_configuration()), range(32)))
        first = json.dumps(results[0], sort_keys=True)
        self.assertTrue(all(json.dumps(result, sort_keys=True) == first for result in results))


if __name__ == "__main__":
    unittest.main()
