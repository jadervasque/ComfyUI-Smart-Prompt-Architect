"""Validate every bundled profile, referenced library, and schema JSON file."""

from __future__ import annotations

import json
from pathlib import Path

from prompt_architect.infrastructure.repository import bundled_repository


def main() -> None:
    """Fail on invalid JSON or any profile/library contract violation."""
    repository = bundled_repository()
    profile_count = 0
    library_ids: set[str] = set()
    libraries = 0
    for summary in repository.list_profiles():
        profile = repository.load_profile(summary.id)
        profile_count += 1
        profile_libraries = {section.library for section in profile.sections.values()}
        library_ids.update(profile_libraries)
        for library_id in sorted(profile_libraries):
            repository.load_library_for_profile(profile, library_id)
            libraries += 1
    catalog = repository.load_catalog_index()
    if profile_count < 15:
        raise SystemExit(f"expected at least 15 valid profiles, found {profile_count}")
    if len(catalog.packs) < 1 or len(catalog.libraries) < 1:
        raise SystemExit("Catalog V2 index is empty")

    data_root = Path(__file__).resolve().parents[1] / "prompt_architect" / "data"
    json_count = 0
    for path in sorted(data_root.rglob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
        json_count += 1
    print(
        f"PASS: {profile_count} profiles, {len(library_ids)} logical libraries, "
        f"{libraries} profile/library resolutions, {json_count} JSON files"
    )


if __name__ == "__main__":
    main()
