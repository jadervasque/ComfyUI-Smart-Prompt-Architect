"""Safe prompt template rendering over an already validated selection context."""

import random
from collections.abc import Mapping
from string import Formatter
from types import MappingProxyType

from prompt_architect.domain.exceptions import RenderError
from prompt_architect.domain.models import (
    ProfileDefinition,
    RenderedPrompt,
    SelectedValue,
    SelectionResult,
    TextVariant,
)
from prompt_architect.domain.normalizer import normalize_fragment, normalize_prompt
from prompt_architect.domain.seeds import derive_seed


def render_selection(
    profile: ProfileDefinition,
    selection: SelectionResult,
    *,
    convert_plus: bool = True,
) -> RenderedPrompt:
    """Render profile templates using only exact allowlisted placeholder names."""
    rendered_sections = _render_sections(profile, selection, convert_plus=convert_plus)
    values = dict(rendered_sections)
    values["negative_global"] = rendered_sections.get("negative", "")
    values["negative_conditional"] = ""
    required = frozenset(
        section_id for section_id, section in profile.sections.items() if section.required
    )
    positive = safe_format(profile.templates["positive"], values, required=required)
    negative_template = profile.templates.get("negative", "")
    negative = safe_format(negative_template, values, required=frozenset())
    return RenderedPrompt(
        positive=normalize_prompt(positive, convert_plus=convert_plus),
        negative=normalize_prompt(negative, convert_plus=convert_plus),
        rendered_sections=MappingProxyType(rendered_sections),
    )


def safe_format(template: str, values: Mapping[str, str], *, required: frozenset[str]) -> str:
    """Substitute plain named placeholders without attribute access or format expressions."""
    output: list[str] = []
    try:
        parsed = Formatter().parse(template)
        for literal, field_name, format_spec, conversion in parsed:
            output.append(literal)
            if field_name is None:
                continue
            safe_name = field_name.replace("-", "").replace("_", "")
            if not field_name or not safe_name.isalnum():
                raise RenderError(f"unsafe template placeholder {field_name!r}")
            if format_spec or conversion:
                raise RenderError(f"format operations are forbidden for placeholder {field_name!r}")
            if field_name in required and not values.get(field_name, "").strip():
                raise RenderError(f"required placeholder {field_name!r} has no value")
            output.append(values.get(field_name, ""))
    except ValueError as error:
        raise RenderError(f"invalid template: {error}") from error
    return "".join(output)


def _render_sections(
    profile: ProfileDefinition,
    selection: SelectionResult,
    *,
    convert_plus: bool,
) -> dict[str, str]:
    result: dict[str, str] = {}
    seen_text: set[str] = set()
    seen_semantic: set[str] = set()
    for section_id in profile.section_order:
        selected = selection.context.selections.get(section_id)
        if selected is None:
            result[section_id] = ""
            continue
        text = _selected_text(profile, selection, selected)
        normalized = normalize_fragment(text, convert_plus=convert_plus)
        text_key = normalized.casefold()
        semantic_key = selected.option.semantic_key
        if text_key in seen_text or (semantic_key is not None and semantic_key in seen_semantic):
            result[section_id] = ""
            continue
        seen_text.add(text_key)
        if semantic_key is not None:
            seen_semantic.add(semantic_key)
        result[section_id] = normalized
    return result


def _selected_text(
    profile: ProfileDefinition, selection: SelectionResult, selected: SelectedValue
) -> str:
    option = selected.option
    if option.variants:
        section = profile.sections[selected.section_id]
        group_seed = selection.group_seeds[section.group]
        variant_seed = derive_seed(group_seed, f"variant:{selected.section_id}:{option.id}")
        return _choose_variant(option.variants, variant_seed).text
    return option.sentence or option.text


def _choose_variant(variants: tuple[TextVariant, ...], seed: int) -> TextVariant:
    ordered = sorted(variants, key=lambda variant: variant.text)
    enabled = [variant for variant in ordered if variant.weight > 0]
    total = sum(variant.weight for variant in enabled)
    if not enabled or total <= 0:
        raise RenderError("text variants have no positive weight")
    # Reproducible content wording is intentionally non-cryptographic.
    threshold = random.Random(seed).random() * total  # noqa: S311
    cumulative = 0.0
    for variant in enabled:
        cumulative += variant.weight
        if threshold < cumulative:
            return variant
    return enabled[-1]
