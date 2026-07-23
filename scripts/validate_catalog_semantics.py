"""Cross-file semantic, safety, and reachability validation for Catalog V2."""

from __future__ import annotations

import re
from collections import defaultdict

from prompt_architect.domain.enums import OptionStatus, RuleType
from prompt_architect.infrastructure.repository import bundled_repository

_FORBIDDEN = re.compile(
    r"\b(?:girl|boy|teen|schoolgirl|schoolboy|child|celebrity|masterpiece|"
    r"signature|gore|bloodied|dismembered)\b",
    re.IGNORECASE,
)
_SENTINEL = re.compile(r"\b(?:none|null|undefined)\b", re.IGNORECASE)


def main() -> None:
    """Fail on cross-pack collisions, unsafe language, or unreachable active options."""
    repository = bundled_repository()
    index = repository.load_catalog_index()
    ids: dict[str, str] = {}
    semantic_keys: dict[str, str] = {}
    active_by_pack: dict[str, set[str]] = defaultdict(set)
    options_by_library: dict[str, set[str]] = {}
    option_objects = []
    option_count = 0
    for library_id in sorted(index.libraries):
        library = repository.load_library(library_id)
        if not library.options:
            raise SystemExit(f"empty logical library {library_id!r}")
        options_by_library[library_id] = {option.id for option in library.options}
        for option in library.options:
            option_objects.append(option)
            option_count += 1
            if option.id in ids:
                raise SystemExit(f"global option ID collision: {option.id!r}")
            ids[option.id] = library_id
            if option.semantic_key is None:
                raise SystemExit(f"missing semantic_key: {option.id!r}")
            if option.semantic_key in semantic_keys:
                raise SystemExit(f"global semantic_key collision: {option.semantic_key!r}")
            semantic_keys[option.semantic_key] = option.id
            if _FORBIDDEN.search(option.text) or _SENTINEL.search(option.text):
                raise SystemExit(f"forbidden catalog language in {option.id!r}")
            if option.pack_id is None or option.family is None or not option.facets:
                raise SystemExit(f"incomplete V2 metadata in {option.id!r}")
            if not option.variants or any(not variant.text.strip() for variant in option.variants):
                raise SystemExit(f"missing or empty variants in {option.id!r}")
            if option.status is not OptionStatus.DEPRECATED and option.weight > 0:
                active_by_pack[option.pack_id].add(option.id)
    known_fields = set(index.libraries) | {"generation-mode"}
    implication_graph: dict[str, set[str]] = defaultdict(set)
    for option in option_objects:
        for rule in option.rules:
            if rule.type is RuleType.IMPLIES:
                if rule.target_field not in options_by_library:
                    raise SystemExit(f"{option.id!r} implies unknown field {rule.target_field!r}")
                if (
                    rule.target_value is None
                    or rule.target_value not in options_by_library[rule.target_field]
                ):
                    raise SystemExit(f"{option.id!r} implies unknown option {rule.target_value!r}")
                implication_graph[option.id].add(rule.target_value)
            elif rule.condition is not None and rule.condition.field not in known_fields:
                raise SystemExit(
                    f"{option.id!r} rule references unknown field {rule.condition.field!r}"
                )
    _reject_implication_cycles(implication_graph)
    reachable: set[str] = set()
    profiles = repository.list_profiles()
    for summary in profiles:
        profile = repository.load_profile(summary.id)
        if profile.catalog_version != index.version:
            raise SystemExit(f"profile {profile.id!r} has incorrect catalog version")
        profile_options = 0
        for section in profile.sections.values():
            library = repository.load_library_for_profile(profile, section.library)
            selected_ids = {
                option.id
                for option in library.options
                if option.status is not OptionStatus.DEPRECATED and option.weight > 0
            }
            profile_options += len(selected_ids)
            reachable.update(selected_ids)
        if profile_options == 0:
            raise SystemExit(f"profile {profile.id!r} has no reachable options")
    active = set().union(*active_by_pack.values())
    unreachable = active - reachable
    if unreachable:
        sample = ", ".join(sorted(unreachable)[:10])
        raise SystemExit(f"{len(unreachable)} active options are unreachable: {sample}")
    if option_count < 4_000:
        raise SystemExit(f"catalog has only {option_count} options; minimum is 4000")
    print(
        f"PASS: {option_count} globally unique options; {len(profiles)} profiles; "
        f"{len(reachable)} active options reachable; no forbidden terms"
    )


def _reject_implication_cycles(graph: dict[str, set[str]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(option_id: str) -> None:
        if option_id in visiting:
            raise SystemExit(f"implication cycle involving {option_id!r}")
        if option_id in visited:
            return
        visiting.add(option_id)
        for target in graph.get(option_id, set()):
            visit(target)
        visiting.remove(option_id)
        visited.add(option_id)

    for option_id in sorted(graph):
        visit(option_id)


if __name__ == "__main__":
    main()
