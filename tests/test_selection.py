"""Golden and behavioral tests for deterministic seeds and weighted selection."""

import random
import unittest
from dataclasses import replace

from prompt_architect.domain.enums import FieldMode, GenerationMode, SelectionSource
from prompt_architect.domain.exceptions import ConfigurationError, SelectionError
from prompt_architect.domain.models import (
    FieldConfiguration,
    GroupConfiguration,
    LibraryDefinition,
    NodeConfiguration,
    ProfileDefinition,
    PromptOption,
    SectionDefinition,
)
from prompt_architect.domain.seeds import derive_section_seed, derive_seed, resolve_group_seed
from prompt_architect.domain.selector import select_basic_option, weighted_choice


def _profile() -> ProfileDefinition:
    sections = {
        "identity": SectionDefinition(
            "identity", True, "identity", FieldMode.RANDOM, "identity", fallback="one"
        ),
        "outfit": SectionDefinition(
            "outfit", True, "outfit", FieldMode.RANDOM, "outfit", fallback="one"
        ),
    }
    return ProfileDefinition(
        schema_version="1.0",
        id="test-profile",
        version="1.0.0",
        display_name="Test",
        language="en",
        minimum_sections=2,
        minimum_prompt_characters=2,
        max_selection_attempts=5,
        section_order=("identity", "outfit"),
        sections=sections,
        templates={"positive": "{identity}. {outfit}."},
    )


def _configuration(seed: int = 123) -> NodeConfiguration:
    return NodeConfiguration(
        schema_version="1.0",
        profile_id="test-profile",
        profile_version="1.0.0",
        mode=GenerationMode.BALANCED,
        master_seed=seed,
        groups={"identity": GroupConfiguration(locked=True, seed=999)},
    )


def _library(library_id: str) -> LibraryDefinition:
    return LibraryDefinition(
        schema_version="1.0",
        id=library_id,
        version="1.0.0",
        display_name=library_id,
        options=(
            PromptOption("one", "One", 1.0, ("plain",)),
            PromptOption("two", "Two", 2.0, ("plain", "second")),
            PromptOption("zero", "Zero", 0.0, ("plain",)),
        ),
        fallback_option_id="one",
    )


class SeedTests(unittest.TestCase):
    """Stable golden values must not change without an engine version decision."""

    def test_derive_seed_golden_value(self) -> None:
        self.assertEqual(derive_seed(123456, "identity"), 11537384483888281349)

    def test_explicit_locked_seed_wins(self) -> None:
        self.assertEqual(
            resolve_group_seed(123, "identity", GroupConfiguration(True, 42)),
            42,
        )

    def test_group_seed_is_namespace_independent(self) -> None:
        self.assertNotEqual(resolve_group_seed(123, "identity"), resolve_group_seed(123, "outfit"))

    def test_invalid_seed_inputs_fail_explicitly(self) -> None:
        with self.assertRaisesRegex(ValueError, r"between 0 and 2\^64-1"):
            derive_seed(-1, "identity")
        with self.assertRaisesRegex(ValueError, "namespace cannot be empty"):
            derive_seed(0, "")
        with self.assertRaisesRegex(ValueError, "batch_index must be non-negative"):
            derive_section_seed(0, "identity", -1)


class WeightedChoiceTests(unittest.TestCase):
    """Weighted choice validates all candidates and is stable by candidate ID."""

    def test_golden_choice_is_independent_of_input_order(self) -> None:
        options = [PromptOption("b", "B", 2), PromptOption("a", "A", 1)]
        self.assertEqual(weighted_choice(options, random.Random(7)).id, "a")
        self.assertEqual(weighted_choice(list(reversed(options)), random.Random(7)).id, "a")

    def test_zero_weight_is_never_selected(self) -> None:
        options = [PromptOption("off", "Off", 0), PromptOption("on", "On", 1)]
        for seed in range(100):
            self.assertEqual(weighted_choice(options, random.Random(seed)).id, "on")

    def test_invalid_and_zero_sum_weights_fail(self) -> None:
        for weight in (-1.0, float("inf"), float("nan")):
            with self.subTest(weight=weight):
                with self.assertRaises(SelectionError):
                    weighted_choice([PromptOption("bad", "Bad", weight)], random.Random(1))
        with self.assertRaises(SelectionError):
            weighted_choice([PromptOption("off", "Off", 0)], random.Random(1))


class BasicModeTests(unittest.TestCase):
    """Basic modes must preserve fixed values and isolate group randomness."""

    def test_fixed_value_is_preserved(self) -> None:
        profile = _profile()
        configuration = replace(
            _configuration(), fields={"identity": FieldConfiguration(FieldMode.FIXED, "two")}
        )
        selected = select_basic_option(
            profile.sections["identity"], _library("identity"), profile, configuration
        )
        self.assertIsNotNone(selected)
        self.assertEqual(selected.option.id, "two")  # type: ignore[union-attr]
        self.assertEqual(selected.source, SelectionSource.FIXED)  # type: ignore[union-attr]

    def test_unknown_fixed_value_fails_explicitly(self) -> None:
        profile = _profile()
        configuration = replace(
            _configuration(), fields={"identity": FieldConfiguration(FieldMode.FIXED, "missing")}
        )
        with self.assertRaises(ConfigurationError):
            select_basic_option(
                profile.sections["identity"], _library("identity"), profile, configuration
            )

    def test_disabled_optional_returns_none_but_required_fails(self) -> None:
        profile = _profile()
        configuration = replace(
            _configuration(), fields={"identity": FieldConfiguration(FieldMode.DISABLED)}
        )
        with self.assertRaises(ConfigurationError):
            select_basic_option(
                profile.sections["identity"], _library("identity"), profile, configuration
            )
        optional = replace(profile.sections["identity"], required=False)
        self.assertIsNone(
            select_basic_option(optional, _library("identity"), profile, configuration)
        )

    def test_locked_identity_does_not_change_when_master_seed_changes(self) -> None:
        profile = _profile()
        identity_library = _library("identity")
        first = select_basic_option(
            profile.sections["identity"], identity_library, profile, _configuration(10)
        )
        second = select_basic_option(
            profile.sections["identity"], identity_library, profile, _configuration(99999)
        )
        self.assertEqual(first, second)

    def test_outfit_seed_change_does_not_change_locked_identity(self) -> None:
        profile = _profile()
        identity = select_basic_option(
            profile.sections["identity"], _library("identity"), profile, _configuration(1)
        )
        changed_outfit_config = replace(
            _configuration(1),
            groups={
                "identity": GroupConfiguration(True, 999),
                "outfit": GroupConfiguration(True, 555),
            },
        )
        identity_after = select_basic_option(
            profile.sections["identity"],
            _library("identity"),
            profile,
            changed_outfit_config,
        )
        self.assertEqual(identity, identity_after)


if __name__ == "__main__":
    unittest.main()
