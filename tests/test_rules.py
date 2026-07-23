"""Compatibility rule engine tests."""

import unittest
from types import MappingProxyType

from prompt_architect.domain.enums import (
    GenerationMode,
    RuleOperator,
    RuleType,
    SelectionSource,
)
from prompt_architect.domain.exceptions import RuleConflictError
from prompt_architect.domain.models import (
    LibraryDefinition,
    PromptOption,
    Rule,
    RuleCondition,
    SelectedValue,
    SelectionContext,
)
from prompt_architect.domain.rules import (
    apply_implications,
    compatible_options,
    evaluate_condition,
    preference_multiplier,
    validate_context_rules,
)


def _condition(field: str, operator: RuleOperator, value: object | None = None) -> RuleCondition:
    return RuleCondition(field, operator, value)


def _selected(
    field: str, option: PromptOption, source: SelectionSource = SelectionSource.RANDOM
) -> SelectedValue:
    return SelectedValue(field, option, source)


def _library(library_id: str, *options: PromptOption) -> LibraryDefinition:
    return LibraryDefinition("1.0", library_id, "1.0.0", library_id, options)


class ConditionTests(unittest.TestCase):
    """Every allowlisted operator is covered without arbitrary evaluation."""

    def setUp(self) -> None:
        option = PromptOption("blue-shirt", "Blue shirt", tags=("blue", "casual"))
        self.context = SelectionContext(
            selections={"outfit": _selected("outfit", option)},
            profile_metadata={"language": "en"},
            generation_mode=GenerationMode.BALANCED,
        )

    def test_value_operators(self) -> None:
        cases = (
            (_condition("outfit", RuleOperator.EQUALS, "blue-shirt"), True),
            (_condition("outfit", RuleOperator.NOT_EQUALS, "red-shirt"), True),
            (_condition("outfit", RuleOperator.IN, ("blue-shirt", "coat")), True),
            (_condition("outfit", RuleOperator.NOT_IN, ("coat",)), True),
            (_condition("outfit", RuleOperator.CONTAINS_TAG, "casual"), True),
            (_condition("outfit", RuleOperator.PRESENT), True),
            (_condition("missing-field", RuleOperator.MISSING), True),
            (_condition("generation-mode", RuleOperator.EQUALS, "balanced"), True),
            (_condition("language", RuleOperator.EQUALS, "en"), True),
        )
        for condition, expected in cases:
            with self.subTest(condition=condition):
                self.assertEqual(evaluate_condition(condition, self.context), expected)


class CompatibilityTests(unittest.TestCase):
    """Absolute rules filter while preferences only affect valid weights."""

    def test_requires_and_excludes_filter_candidates(self) -> None:
        context = SelectionContext(
            selections={"location": _selected("location", PromptOption("studio", "Studio"))}
        )
        valid = PromptOption(
            "valid",
            "Valid",
            rules=(Rule(RuleType.REQUIRES, _condition("location", RuleOperator.PRESENT)),),
        )
        excluded = PromptOption(
            "excluded",
            "Excluded",
            rules=(
                Rule(
                    RuleType.EXCLUDES,
                    _condition("location", RuleOperator.EQUALS, "studio"),
                ),
            ),
        )
        missing = PromptOption(
            "missing",
            "Missing",
            rules=(Rule(RuleType.REQUIRES, _condition("pose", RuleOperator.PRESENT)),),
        )
        self.assertEqual(
            [item.id for item in compatible_options((missing, valid, excluded), context)], ["valid"]
        )

    def test_preference_multiplier_is_mode_aware(self) -> None:
        option = PromptOption(
            "preferred",
            "Preferred",
            rules=(
                Rule(
                    RuleType.PREFER,
                    _condition("location", RuleOperator.EQUALS, "studio"),
                    multiplier=4.0,
                ),
            ),
        )
        base = {"location": _selected("location", PromptOption("studio", "Studio"))}
        balanced = SelectionContext(selections=base, generation_mode=GenerationMode.BALANCED)
        creative = SelectionContext(selections=base, generation_mode=GenerationMode.CREATIVE)
        self.assertEqual(preference_multiplier(option, balanced), 4.0)
        self.assertEqual(preference_multiplier(option, creative), 2.0)


class ImplicationTests(unittest.TestCase):
    """Implications fill, replace, preserve fixed values, and detect cycles."""

    def test_implication_fills_empty_field_and_is_recorded(self) -> None:
        source = PromptOption(
            "rain",
            "Rain",
            rules=(Rule(RuleType.IMPLIES, target_field="lighting", target_value="overcast"),),
        )
        overcast = PromptOption("overcast", "Overcast")
        context = SelectionContext(selections={"weather": _selected("weather", source)})
        result = apply_implications(context, {"lighting": _library("lighting", overcast)})
        self.assertEqual(result.context.selections["lighting"].option.id, "overcast")
        self.assertEqual(result.context.selections["lighting"].source, SelectionSource.IMPLIED)
        self.assertEqual(len(result.applied_rules), 1)

    def test_implication_replaces_random_but_not_fixed(self) -> None:
        source = PromptOption(
            "rain",
            "Rain",
            rules=(Rule(RuleType.IMPLIES, target_field="lighting", target_value="overcast"),),
        )
        sunny = PromptOption("sunny", "Sunny")
        overcast = PromptOption("overcast", "Overcast")
        selections = {
            "weather": _selected("weather", source),
            "lighting": _selected("lighting", sunny),
        }
        result = apply_implications(
            SelectionContext(selections=selections),
            {"lighting": _library("lighting", sunny, overcast)},
        )
        self.assertEqual(result.context.selections["lighting"].option.id, "overcast")
        self.assertEqual(len(result.resolved_conflicts), 1)
        fixed = SelectionContext(selections=selections, fixed_fields=frozenset({"lighting"}))
        with self.assertRaisesRegex(RuleConflictError, "conflicts with user-locked value"):
            apply_implications(fixed, {"lighting": _library("lighting", sunny, overcast)})

    def test_implication_cycle_is_rejected(self) -> None:
        a1 = PromptOption(
            "a-one",
            "A1",
            rules=(Rule(RuleType.IMPLIES, target_field="b", target_value="b-one"),),
        )
        a2 = PromptOption(
            "a-two",
            "A2",
            rules=(Rule(RuleType.IMPLIES, target_field="b", target_value="b-two"),),
        )
        b1 = PromptOption(
            "b-one",
            "B1",
            rules=(Rule(RuleType.IMPLIES, target_field="a", target_value="a-two"),),
        )
        b2 = PromptOption(
            "b-two",
            "B2",
            rules=(Rule(RuleType.IMPLIES, target_field="a", target_value="a-one"),),
        )
        context = SelectionContext(selections={"a": _selected("a", a1)})
        libraries = {
            "a": _library("a", a1, a2),
            "b": _library("b", b1, b2),
        }
        with self.assertRaisesRegex(RuleConflictError, "cycle detected"):
            apply_implications(context, libraries)

    def test_final_context_rule_validation(self) -> None:
        option = PromptOption(
            "needs-pose",
            "Needs pose",
            rules=(Rule(RuleType.REQUIRES, _condition("pose", RuleOperator.PRESENT)),),
        )
        context = SelectionContext(
            selections=MappingProxyType({"outfit": _selected("outfit", option)})
        )
        self.assertEqual(len(validate_context_rules(context)), 1)


if __name__ == "__main__":
    unittest.main()
