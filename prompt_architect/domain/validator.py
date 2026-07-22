"""Structured context and final prompt validation."""

import re
from collections.abc import Sequence

from prompt_architect.domain.enums import IssueSeverity
from prompt_architect.domain.exceptions import FinalPromptValidationError
from prompt_architect.domain.models import (
    ProfileDefinition,
    RenderedPrompt,
    SelectionResult,
    ValidationIssue,
)
from prompt_architect.domain.rules import validate_context_rules

_PLACEHOLDER = re.compile(r"\{[^{}]+\}")
_SENTINEL = re.compile(r"\b(?:none|null|undefined)\b", re.IGNORECASE)
_HAS_WORD = re.compile(r"[\w\d]", re.UNICODE)


def validate_context(
    profile: ProfileDefinition, selection: SelectionResult
) -> tuple[ValidationIssue, ...]:
    """Validate required sections and absolute rules before final output."""
    issues: list[ValidationIssue] = []
    for section_id in profile.section_order:
        if profile.sections[section_id].required and section_id not in selection.context.selections:
            issues.append(
                ValidationIssue(
                    "required-section-missing",
                    f"Required section {section_id!r} is unresolved",
                    IssueSeverity.ERROR,
                    f"sections.{section_id}",
                )
            )
    for violation in validate_context_rules(selection.context):
        issues.append(
            ValidationIssue("absolute-rule-violation", violation, IssueSeverity.ERROR, "selections")
        )
    return tuple(issues)


def validate_final(
    profile: ProfileDefinition, rendered: RenderedPrompt
) -> tuple[ValidationIssue, ...]:
    """Validate non-empty, complete prompt text and profile thresholds."""
    issues: list[ValidationIssue] = []
    positive = rendered.positive.strip()
    if not positive or not _HAS_WORD.search(positive):
        issues.append(
            ValidationIssue(
                "positive-empty",
                "Positive prompt is empty or contains only punctuation",
                IssueSeverity.ERROR,
                "positive_prompt",
            )
        )
    if len(positive) < profile.minimum_prompt_characters:
        issues.append(
            ValidationIssue(
                "positive-too-short",
                f"Positive prompt has {len(positive)} characters; minimum is "
                f"{profile.minimum_prompt_characters}",
                IssueSeverity.ERROR,
                "positive_prompt",
            )
        )
    rendered_count = sum(bool(text.strip()) for text in rendered.rendered_sections.values())
    if rendered_count < profile.minimum_sections:
        issues.append(
            ValidationIssue(
                "too-few-sections",
                f"Rendered {rendered_count} sections; minimum is {profile.minimum_sections}",
                IssueSeverity.ERROR,
                "rendered_sections",
            )
        )
    for name, prompt in (("positive_prompt", positive), ("negative_prompt", rendered.negative)):
        if _PLACEHOLDER.search(prompt):
            issues.append(
                ValidationIssue(
                    "residual-placeholder",
                    f"{name} contains a residual placeholder",
                    IssueSeverity.ERROR,
                    name,
                )
            )
        if _SENTINEL.search(prompt):
            issues.append(
                ValidationIssue(
                    "sentinel-text",
                    f"{name} contains a null-like sentinel",
                    IssueSeverity.ERROR,
                    name,
                )
            )
    if not profile.allow_empty_negative and not rendered.negative.strip():
        issues.append(
            ValidationIssue(
                "negative-empty",
                "Profile requires a non-empty negative prompt",
                IssueSeverity.ERROR,
                "negative_prompt",
            )
        )
    return tuple(issues)


def raise_for_errors(issues: Sequence[ValidationIssue]) -> None:
    """Raise one clear failure when any structured error issue exists."""
    errors = [issue for issue in issues if issue.severity is IssueSeverity.ERROR]
    if errors:
        detail = "; ".join(f"{issue.code}: {issue.message}" for issue in errors)
        raise FinalPromptValidationError(detail)
