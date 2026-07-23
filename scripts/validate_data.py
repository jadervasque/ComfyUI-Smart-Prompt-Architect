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
    for summary in repository.list_profiles():
        profile = repository.load_profile(summary.id)
        profile_count += 1
        library_ids.update(section.library for section in profile.sections.values())
    for library_id in sorted(library_ids):
        repository.load_library(library_id)

    data_root = Path(__file__).resolve().parents[1] / "prompt_architect" / "data"
    json_count = 0
    for path in sorted(data_root.rglob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
        json_count += 1
    print(f"PASS: {profile_count} profiles, {len(library_ids)} libraries, {json_count} JSON files")


if __name__ == "__main__":
    main()
