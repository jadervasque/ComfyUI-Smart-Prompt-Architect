"""Renderer and normalizer snapshots."""

import unittest
from dataclasses import replace

from prompt_architect.domain.enums import FieldMode, GenerationMode, SelectionSource
from prompt_architect.domain.exceptions import RenderError
from prompt_architect.domain.models import (
    ProfileDefinition,
    PromptOption,
    SectionDefinition,
    SelectedValue,
    SelectionContext,
    SelectionResult,
    TextVariant,
)
from prompt_architect.domain.normalizer import normalize_prompt
from prompt_architect.domain.renderer import render_selection, safe_format


def _profile() -> ProfileDefinition:
    sections = {
        "subject": SectionDefinition("subject", True, "subjects", FieldMode.FIXED, "identity"),
        "outfit": SectionDefinition("outfit", False, "outfits", FieldMode.RANDOM, "outfit"),
        "detail": SectionDefinition("detail", False, "details", FieldMode.RANDOM, "appearance"),
    }
    return ProfileDefinition(
        "1.0",
        "render-test",
        "1.0.0",
        "Render Test",
        "en",
        1,
        5,
        4,
        ("subject", "outfit", "detail"),
        sections,
        {"positive": "{subject}. {outfit} , {detail}..", "negative": "{negative_global}"},
    )


def _selection(*options: tuple[str, PromptOption]) -> SelectionResult:
    selections = {
        section_id: SelectedValue(section_id, option, SelectionSource.RANDOM)
        for section_id, option in options
    }
    return SelectionResult(
        SelectionContext(selections=selections, generation_mode=GenerationMode.BALANCED),
        group_seeds={"identity": 1, "outfit": 2, "appearance": 3},
        attempts={},
    )


class NormalizerTests(unittest.TestCase):
    """Conservative cleanup snapshots stay readable and deterministic."""

    def test_spacing_punctuation_capitalization_plus_and_articles(self) -> None:
        raw = "  a orange + coat  ,with detail..next sentence!  "
        self.assertEqual(
            normalize_prompt(raw),
            "An orange and coat, with detail. Next sentence!",
        )

    def test_duplicate_sentences_are_removed(self) -> None:
        self.assertEqual(
            normalize_prompt("soft light. Soft light. portrait."), "Soft light. Portrait."
        )


class RendererTests(unittest.TestCase):
    """Templates accept plain names only and remove duplicate fragments."""

    def test_snapshot_with_optional_empty_and_exact_deduplication(self) -> None:
        option = PromptOption("adult", "an adult person")
        selection = _selection(
            ("subject", option), ("outfit", PromptOption("same", "an adult person"))
        )
        rendered = render_selection(_profile(), selection)
        self.assertEqual(rendered.positive, "An adult person.")
        self.assertEqual(rendered.rendered_sections["outfit"], "")

    def test_semantic_key_deduplicates_equivalent_wording(self) -> None:
        subject = PromptOption("adult", "An adult person", semantic_key="person")
        detail = PromptOption("human", "A photographed human", semantic_key="person")
        rendered = render_selection(
            _profile(), _selection(("subject", subject), ("detail", detail))
        )
        self.assertEqual(rendered.positive, "An adult person.")

    def test_weighted_variant_is_deterministic(self) -> None:
        variant_option = PromptOption(
            "coat",
            "Coat",
            variants=(TextVariant("A red coat", 1), TextVariant("A blue coat", 2)),
        )
        selection = _selection(
            ("subject", PromptOption("adult", "An adult person")),
            ("outfit", variant_option),
        )
        self.assertEqual(
            render_selection(_profile(), selection), render_selection(_profile(), selection)
        )

    def test_sentence_field_precedes_text(self) -> None:
        option = PromptOption("adult", "fragment", sentence="A complete adult portrait")
        rendered = render_selection(_profile(), _selection(("subject", option)))
        self.assertEqual(rendered.positive, "A complete adult portrait.")

    def test_required_missing_placeholder_fails(self) -> None:
        with self.assertRaisesRegex(RenderError, "required placeholder 'subject'"):
            render_selection(_profile(), _selection())

    def test_unsafe_field_and_format_operations_fail(self) -> None:
        with self.assertRaises(RenderError):
            safe_format("{subject.__class__}", {"subject": "safe"}, required=frozenset())
        with self.assertRaises(RenderError):
            safe_format("{subject!r}", {"subject": "safe"}, required=frozenset())

    def test_residual_punctuation_is_cleaned(self) -> None:
        profile = replace(_profile(), templates={"positive": "{subject},,, {outfit}... {detail}"})
        rendered = render_selection(
            profile,
            _selection(("subject", PromptOption("adult", "an adult person"))),
        )
        self.assertEqual(rendered.positive, "An adult person.")


if __name__ == "__main__":
    unittest.main()
