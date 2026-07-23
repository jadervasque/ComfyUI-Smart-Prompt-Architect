"""Detect literal and high-confidence near duplicates in Catalog V2."""

from __future__ import annotations

import re
from collections import defaultdict
from difflib import SequenceMatcher

from prompt_architect.infrastructure.repository import bundled_repository

_PUNCTUATION = re.compile(r"[^a-z0-9 ]+")
_SPACE = re.compile(r"\s+")


def _normalize(value: str) -> str:
    return _SPACE.sub(" ", _PUNCTUATION.sub(" ", value.casefold())).strip()


def main() -> None:
    """Fail on duplicate option text or near-identical text in one semantic family."""
    repository = bundled_repository()
    index = repository.load_catalog_index()
    exact: dict[str, str] = {}
    families: dict[str, list[tuple[str, str]]] = defaultdict(list)
    option_count = 0
    for library_id in sorted(index.libraries):
        library = repository.load_library(library_id)
        for option in library.options:
            option_count += 1
            normalized = _normalize(option.text)
            previous = exact.get(normalized)
            if previous is not None:
                raise SystemExit(
                    f"literal duplicate: {previous!r} and {option.id!r}: {option.text!r}"
                )
            exact[normalized] = option.id
            families[option.family or option.id].append((option.id, normalized))
            variant_texts = [_normalize(variant.text) for variant in option.variants]
            if len(variant_texts) != len(set(variant_texts)):
                raise SystemExit(f"repeated variant text in {option.id!r}")
    near_pairs = 0
    for family, entries in sorted(families.items()):
        for left_index, (left_id, left) in enumerate(entries):
            for right_id, right in entries[left_index + 1 :]:
                ratio = SequenceMatcher(None, left, right, autojunk=False).ratio()
                if ratio >= 0.985:
                    raise SystemExit(
                        f"near duplicate ({ratio:.3f}) in {family!r}: {left_id!r} and {right_id!r}"
                    )
                near_pairs += 1
    print(f"PASS: {option_count} option texts unique; {near_pairs} within-family pairs audited")


if __name__ == "__main__":
    main()
