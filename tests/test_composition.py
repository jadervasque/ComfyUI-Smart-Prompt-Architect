"""End-to-end validation, override, manifest, and summary tests."""

import json
import unittest
from dataclasses import replace

from prompt_architect.application.compose_service import compose_prompt
from prompt_architect.domain.enums import FieldMode, GenerationMode, IssueSeverity
from prompt_architect.domain.exceptions import ConfigurationError, FinalPromptValidationError
from prompt_architect.domain.models import (
    FieldConfiguration,
    LibraryDefinition,
    NodeConfiguration,
    ProfileDefinition,
    PromptOption,
    RenderedPrompt,
    SectionDefinition,
)
from prompt_architect.domain.validator import raise_for_errors, validate_final


def _profile() -> ProfileDefinition:
    return ProfileDefinition(
        "1.0",
        "portrait",
        "1.0.0",
        "Portrait",
        "en",
        1,
        10,
        5,
        ("subject", "negative"),
        {
            "subject": SectionDefinition(
                "subject", True, "subjects", FieldMode.FIXED, "identity", "adult", "adult"
            ),
            "negative": SectionDefinition(
                "negative", False, "negative", FieldMode.RANDOM, "negative", fallback="blurry"
            ),
        },
        {"positive": "{subject}.", "negative": "{negative_global}."},
        allow_empty_negative=False,
    )


def _libraries() -> dict[str, LibraryDefinition]:
    return {
        "subjects": LibraryDefinition(
            "1.0",
            "subjects",
            "1.2.0",
            "Subjects",
            (PromptOption("adult", "an adult portrait"),),
            "adult",
        ),
        "negative": LibraryDefinition(
            "1.0",
            "negative",
            "1.1.0",
            "Negative",
            (PromptOption("blurry", "blurry artifacts"),),
            "blurry",
        ),
    }


def _configuration(seed: int = 42, **overrides: str) -> NodeConfiguration:
    return NodeConfiguration(
        "1.0",
        "portrait",
        "1.0.0",
        GenerationMode.BALANCED,
        seed,
        overrides=overrides,
    )


class CompositionTests(unittest.TestCase):
    """Public composition output remains complete and canonical."""

    def test_end_to_end_outputs_and_overrides(self) -> None:
        configuration = _configuration(
            positive_prefix="editorial photograph",
            positive_suffix="high detail",
            negative_prefix="avoid",
            negative_suffix="low quality",
        )
        result = compose_prompt(_profile(), _libraries(), configuration)
        self.assertEqual(
            result.rendered.positive,
            "Editorial photograph. An adult portrait. High detail",
        )
        self.assertEqual(
            result.rendered.negative,
            "Avoid. Blurry artifacts. Low quality",
        )
        self.assertEqual(result.seed_used, 42)
        self.assertEqual(result.issues, ())

    def test_manifest_is_canonical_complete_and_deterministic(self) -> None:
        first = compose_prompt(_profile(), _libraries(), _configuration())
        second = compose_prompt(_profile(), _libraries(), _configuration())
        self.assertEqual(first.manifest_json, second.manifest_json)
        data = json.loads(first.manifest_json)
        self.assertEqual(data["libraries"], {"negative": "1.1.0", "subjects": "1.2.0"})
        self.assertEqual(data["profile"], {"id": "portrait", "version": "1.0.0"})
        self.assertEqual(data["selections"]["subject"]["source"], "fixed")
        self.assertTrue(data["configuration_hash"].startswith("sha256:"))
        self.assertEqual(len(data["configuration_hash"]), 71)

    def test_configuration_hash_changes_with_seed(self) -> None:
        first = compose_prompt(_profile(), _libraries(), _configuration(1))
        second = compose_prompt(_profile(), _libraries(), _configuration(2))
        self.assertNotEqual(
            first.manifest.configuration_hash,
            second.manifest.configuration_hash,
        )

    def test_custom_text_is_rendered_and_recorded_in_manifest(self) -> None:
        text = "A precise custom adult subject description"
        configuration = replace(
            _configuration(),
            schema_version="1.1",
            fields={"subject": FieldConfiguration(FieldMode.CUSTOM, text)},
        )
        result = compose_prompt(_profile(), _libraries(), configuration)
        data = json.loads(result.manifest_json)
        self.assertIn(text, result.rendered.positive)
        self.assertEqual(data["selections"]["subject"]["option_id"], "custom")
        self.assertEqual(data["selections"]["subject"]["raw_text"], text)
        self.assertEqual(data["selections"]["subject"]["source"], "custom")

    def test_summary_has_diagnostics_without_prompt_text(self) -> None:
        result = compose_prompt(_profile(), _libraries(), _configuration())
        self.assertIn("Profile portrait@1.0.0", result.summary)
        self.assertIn("seed 42", result.summary)
        self.assertNotIn(result.rendered.positive, result.summary)

    def test_unknown_override_fails(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "unknown prompt overrides"):
            compose_prompt(_profile(), _libraries(), _configuration(unknown="value"))

    def test_negative_empty_fails_when_profile_requires_it(self) -> None:
        profile = _profile()
        profile = replace(profile, templates={"positive": "{subject}.", "negative": ""})
        configuration = replace(
            _configuration(),
            fields={"negative": FieldConfiguration(FieldMode.DISABLED)},
        )
        with self.assertRaisesRegex(FinalPromptValidationError, "negative-empty"):
            compose_prompt(profile, _libraries(), configuration)


class FinalValidationTests(unittest.TestCase):
    """Final validator produces structured errors before raising."""

    def test_empty_punctuation_placeholder_and_sentinel_are_issues(self) -> None:
        profile = replace(_profile(), minimum_prompt_characters=1, allow_empty_negative=True)
        rendered = RenderedPrompt("... {subject} None", "undefined", {"subject": ""})
        issues = validate_final(profile, rendered)
        codes = {issue.code for issue in issues}
        self.assertTrue(
            {"residual-placeholder", "sentinel-text", "too-few-sections"}.issubset(codes)
        )
        self.assertTrue(all(issue.severity is IssueSeverity.ERROR for issue in issues))
        with self.assertRaises(FinalPromptValidationError):
            raise_for_errors(issues)

    def test_positive_punctuation_only_is_rejected(self) -> None:
        profile = replace(_profile(), minimum_prompt_characters=1, allow_empty_negative=True)
        issues = validate_final(profile, RenderedPrompt("...", "", {"subject": "..."}))
        self.assertIn("positive-empty", {issue.code for issue in issues})


if __name__ == "__main__":
    unittest.main()
