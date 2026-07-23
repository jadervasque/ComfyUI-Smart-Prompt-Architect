"""Structured selection compositor and fallback tests."""

import unittest
from dataclasses import replace

from prompt_architect.domain.engine import compose_selection
from prompt_architect.domain.enums import FieldMode, GenerationMode, RuleOperator, RuleType
from prompt_architect.domain.exceptions import ConfigurationError, RuleConflictError, SelectionError
from prompt_architect.domain.models import (
    FieldConfiguration,
    LibraryDefinition,
    NodeConfiguration,
    ProfileDefinition,
    PromptOption,
    Rule,
    RuleCondition,
    SectionDefinition,
)


def _profile(*, required_fallback: str | None = "adult") -> ProfileDefinition:
    return ProfileDefinition(
        schema_version="1.0",
        id="portrait",
        version="1.0.0",
        display_name="Portrait",
        language="en",
        minimum_sections=2,
        minimum_prompt_characters=10,
        max_selection_attempts=4,
        section_order=("subject", "outfit", "background"),
        sections={
            "subject": SectionDefinition(
                "subject", True, "subjects", FieldMode.FIXED, "identity", "adult", "adult"
            ),
            "outfit": SectionDefinition(
                "outfit", True, "outfits", FieldMode.RANDOM, "outfit", fallback="plain"
            ),
            "background": SectionDefinition(
                "background", False, "backgrounds", FieldMode.RANDOM, "scene"
            ),
        },
        templates={"positive": "{subject}. {outfit}. {background}."},
        profile_fallbacks={"subject": required_fallback} if required_fallback else {},
    )


def _configuration(**fields: FieldConfiguration) -> NodeConfiguration:
    return NodeConfiguration(
        "1.0",
        "portrait",
        "1.0.0",
        GenerationMode.BALANCED,
        123,
        fields=fields,
    )


def _libraries() -> dict[str, LibraryDefinition]:
    return {
        "subjects": LibraryDefinition(
            "1.0",
            "subjects",
            "1.0.0",
            "Subjects",
            (PromptOption("adult", "An adult person"),),
            "adult",
        ),
        "outfits": LibraryDefinition(
            "1.0",
            "outfits",
            "1.0.0",
            "Outfits",
            (
                PromptOption("formal", "Formal clothing", tags=("formal",)),
                PromptOption("plain", "Plain clothing", tags=("plain",)),
            ),
            "plain",
        ),
        "backgrounds": LibraryDefinition(
            "1.0",
            "backgrounds",
            "1.0.0",
            "Backgrounds",
            (PromptOption("studio", "Studio background"),),
        ),
    }


class CompositorTests(unittest.TestCase):
    """Required resolution, diagnostics, and mode relaxation are deterministic."""

    def test_complete_context_follows_profile_order(self) -> None:
        result = compose_selection(_profile(), _libraries(), _configuration())
        self.assertEqual(tuple(result.context.selections), ("subject", "outfit", "background"))
        self.assertEqual(result.context.selections["subject"].source.value, "fixed")
        self.assertEqual(result.attempts["outfit"], 1)

    def test_optional_disabled_is_recorded(self) -> None:
        configuration = _configuration(background=FieldConfiguration(FieldMode.DISABLED))
        result = compose_selection(_profile(), _libraries(), configuration)
        self.assertNotIn("background", result.context.selections)
        self.assertIn("section background disabled", result.warnings)

    def test_custom_value_is_preserved_as_a_user_locked_selection(self) -> None:
        custom = "They wear a hand-painted cobalt flight jacket"
        configuration = _configuration(outfit=FieldConfiguration(FieldMode.CUSTOM, custom))
        result = compose_selection(_profile(), _libraries(), configuration)
        selected = result.context.selections["outfit"]
        self.assertEqual(selected.option.id, "custom")
        self.assertEqual(selected.option.text, custom)
        self.assertEqual(selected.source.value, "custom")
        self.assertEqual(result.attempts["outfit"], 0)

    def test_required_disabled_fails(self) -> None:
        configuration = _configuration(outfit=FieldConfiguration(FieldMode.DISABLED))
        with self.assertRaises(ConfigurationError):
            compose_selection(_profile(), _libraries(), configuration)

    def test_no_eligible_candidate_uses_explicit_fallback(self) -> None:
        libraries = _libraries()
        libraries["outfits"] = replace(
            libraries["outfits"],
            options=(
                PromptOption("formal", "Formal", 0),
                PromptOption("plain", "Plain", 0),
            ),
        )
        result = compose_selection(_profile(), libraries, _configuration())
        self.assertEqual(result.context.selections["outfit"].option.id, "plain")
        self.assertTrue(result.context.selections["outfit"].fallback_used)
        self.assertEqual(result.fallbacks, ("section outfit used fallback plain",))

    def test_balanced_relaxes_optional_tags_but_strict_does_not(self) -> None:
        field = FieldConfiguration(FieldMode.RANDOM, include_tags=("missing-tag",))
        balanced = compose_selection(_profile(), _libraries(), _configuration(outfit=field))
        self.assertIn("section outfit relaxed optional tag filters", balanced.warnings)
        strict_config = replace(_configuration(outfit=field), mode=GenerationMode.STRICT)
        strict = compose_selection(_profile(), _libraries(), strict_config)
        self.assertEqual(strict.context.selections["outfit"].option.id, "plain")
        self.assertEqual(strict.fallbacks, ("section outfit used fallback plain",))

    def test_missing_required_fallback_fails_explicitly(self) -> None:
        profile = _profile(required_fallback=None)
        section = replace(profile.sections["outfit"], fallback=None)
        profile = replace(profile, sections={**profile.sections, "outfit": section})
        libraries = _libraries()
        libraries["outfits"] = replace(
            libraries["outfits"],
            options=(PromptOption("off", "Off", 0),),
            fallback_option_id=None,
        )
        with self.assertRaisesRegex(SelectionError, "no valid candidate or fallback"):
            compose_selection(profile, libraries, _configuration())

    def test_fixed_value_conflicting_with_implication_fails(self) -> None:
        libraries = _libraries()
        rain = PromptOption(
            "rain",
            "Rain",
            rules=(Rule(RuleType.IMPLIES, target_field="outfit", target_value="plain"),),
        )
        libraries["backgrounds"] = replace(libraries["backgrounds"], options=(rain,))
        configuration = _configuration(
            outfit=FieldConfiguration(FieldMode.FIXED, "formal"),
            background=FieldConfiguration(FieldMode.FIXED, "rain"),
        )
        with self.assertRaisesRegex(RuleConflictError, "conflicts with user-locked value"):
            compose_selection(_profile(), libraries, configuration)

    def test_custom_value_conflicting_with_implication_fails(self) -> None:
        libraries = _libraries()
        rain = PromptOption(
            "rain",
            "Rain",
            rules=(Rule(RuleType.IMPLIES, target_field="outfit", target_value="plain"),),
        )
        libraries["backgrounds"] = replace(libraries["backgrounds"], options=(rain,))
        configuration = _configuration(
            outfit=FieldConfiguration(FieldMode.CUSTOM, "A custom protective coat"),
            background=FieldConfiguration(FieldMode.FIXED, "rain"),
        )
        with self.assertRaisesRegex(RuleConflictError, "conflicts with user-locked value"):
            compose_selection(_profile(), libraries, configuration)

    def test_fallback_that_violates_absolute_rule_fails(self) -> None:
        libraries = _libraries()
        needs_night = Rule(
            RuleType.REQUIRES,
            RuleCondition("background", RuleOperator.EQUALS, "night"),
        )
        libraries["outfits"] = replace(
            libraries["outfits"],
            options=(PromptOption("plain", "Plain", 0, rules=(needs_night,)),),
        )
        with self.assertRaisesRegex(SelectionError, "fallback 'plain'.*violates rules"):
            compose_selection(_profile(), libraries, _configuration())


if __name__ == "__main__":
    unittest.main()
