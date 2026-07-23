"""High-volume Catalog V2 reliability, diversity, and coverage runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path

from prompt_architect.domain.engine import compose_selection
from prompt_architect.domain.enums import GenerationMode, OptionStatus
from prompt_architect.domain.models import NodeConfiguration
from prompt_architect.domain.renderer import render_selection
from prompt_architect.domain.validator import (
    raise_for_errors,
    validate_context,
    validate_final,
)
from tests.test_official_data import _PROFILE_IDS, official_context

_PLACEHOLDER = re.compile(r"\{[^{}]+\}")
_FORBIDDEN = re.compile(
    r"\b(?:girl|boy|teen|schoolgirl|schoolboy|child|celebrity|gore|bloodied)\b",
    re.IGNORECASE,
)


def _entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in counter.values() if count)


def _mode(profile_mode: object) -> GenerationMode:
    if isinstance(profile_mode, str):
        return GenerationMode(profile_mode)
    return GenerationMode.BALANCED


def main() -> int:
    """Generate every requested seed and fail on integrity or diversity regressions."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=10_000)
    parser.add_argument("--determinism-seeds", type=int, default=128)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    if arguments.seeds <= 0 or arguments.determinism_seeds < 0:
        parser.error("seeds must be positive and determinism-seeds non-negative")
    report: dict[str, object] = {
        "seeds_per_profile": arguments.seeds,
        "determinism_samples_per_profile": min(arguments.seeds, arguments.determinism_seeds),
        "profiles": {},
    }
    report_profiles: dict[str, object] = report["profiles"]  # type: ignore[assignment]
    globally_eligible: set[str] = set()
    globally_selected: set[str] = set()
    for profile_id in _PROFILE_IDS:
        profile, libraries = official_context(profile_id)
        generation_mode = _mode(profile.metadata.get("recommended_mode"))
        eligible = {
            option.id
            for library in libraries.values()
            for option in library.options
            if option.status is not OptionStatus.DEPRECATED and option.weight > 0
        }
        globally_eligible.update(eligible)
        enabled_packs = frozenset(profile.enabled_packs)
        option_frequency: Counter[str] = Counter()
        family_frequency: Counter[str] = Counter()
        prompt_hashes: set[bytes] = set()
        fallbacks = 0
        rejections = 0
        attempts = 0
        started = time.perf_counter()
        for seed in range(arguments.seeds):
            configuration = NodeConfiguration(
                "1.1",
                profile.id,
                profile.version,
                generation_mode,
                seed,
                batch_index=seed,
            )
            selection = compose_selection(profile, libraries, configuration)
            rendered = render_selection(profile, selection)
            issues = (*validate_context(profile, selection), *validate_final(profile, rendered))
            raise_for_errors(issues)
            if not rendered.positive.strip():
                raise AssertionError(f"{profile_id} seed {seed}: empty positive prompt")
            if _PLACEHOLDER.search(rendered.positive):
                raise AssertionError(f"{profile_id} seed {seed}: residual placeholder")
            if _FORBIDDEN.search(rendered.positive) or _FORBIDDEN.search(rendered.negative):
                raise AssertionError(f"{profile_id} seed {seed}: forbidden content")
            selected = tuple(selection.context.selections.values())
            if any(
                value.option.pack_id is not None and value.option.pack_id not in enabled_packs
                for value in selected
            ):
                raise AssertionError(f"{profile_id} seed {seed}: disabled pack selected")
            for value in selected:
                option_frequency[value.option.id] += 1
                family_frequency[value.option.family or value.option.id] += 1
            prompt_hashes.add(hashlib.sha256(rendered.positive.encode("utf-8")).digest())
            fallbacks += len(selection.fallbacks)
            rejections += sum(" rejected:" in event for event in selection.applied_rules)
            attempts += sum(selection.attempts.values())
            if seed < arguments.determinism_seeds:
                repeated = compose_selection(profile, libraries, configuration)
                repeated_rendered = render_selection(profile, repeated)
                if rendered != repeated_rendered or selection != repeated:
                    raise AssertionError(f"{profile_id} seed {seed}: nondeterministic result")
        elapsed = time.perf_counter() - started
        unique_ratio = len(prompt_hashes) / arguments.seeds
        coverage = len(option_frequency) / len(eligible)
        never_selected = sorted(eligible - set(option_frequency))
        globally_selected.update(option_frequency)
        if unique_ratio < 0.95:
            raise AssertionError(
                f"{profile_id}: unique prompt ratio {unique_ratio:.4f} is below 0.95"
            )
        if arguments.seeds >= 10_000 and coverage < 0.90:
            raise AssertionError(f"{profile_id}: option coverage {coverage:.4f} is below 0.90")
        metrics = {
            "mode": generation_mode.value,
            "eligible_options": len(eligible),
            "selected_options": len(option_frequency),
            "coverage": coverage,
            "unique_prompts": len(prompt_hashes),
            "unique_ratio": unique_ratio,
            "fallback_rate": fallbacks / max(1, attempts),
            "rejections": rejections,
            "average_attempts": attempts / arguments.seeds,
            "family_entropy_bits": _entropy(family_frequency),
            "top_options": option_frequency.most_common(10),
            "never_selected": never_selected,
            "elapsed_seconds": elapsed,
            "prompts_per_second": arguments.seeds / elapsed,
        }
        report_profiles[profile_id] = metrics
        print(
            f"PASS {profile_id}: {arguments.seeds} seeds; "
            f"unique={unique_ratio:.4f}; coverage={coverage:.4f}; "
            f"fallbacks={fallbacks}; {arguments.seeds / elapsed:.1f}/s",
            flush=True,
        )
    globally_unreachable = sorted(globally_eligible - globally_selected)
    if arguments.seeds >= 10_000 and globally_unreachable:
        raise AssertionError(
            f"{len(globally_unreachable)} active options were never selected by any profile: "
            + ", ".join(globally_unreachable[:10])
        )
    report["global"] = {
        "eligible_options": len(globally_eligible),
        "selected_options": len(globally_selected),
        "coverage": len(globally_selected) / len(globally_eligible),
        "never_selected": globally_unreachable,
    }
    if arguments.output is not None:
        output = arguments.output.resolve(strict=False)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
