"""Audit the local wildcard collection as taxonomy input without copying content."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

_DEFAULT_ROOT = Path(__file__).resolve().parents[3] / "wildcards"
_PROPER_NAME = re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$")
_UNSAFE = re.compile(
    r"\b(?:girl|boy|teen|schoolgirl|child|gore|blood|dismember|victim|"
    r"celebrity|artist|masterpiece)\b",
    re.IGNORECASE,
)
_MULTI_DIMENSION = re.compile(r"[,;:]|\b(?:wearing|with|paired with|holding)\b", re.IGNORECASE)


def main() -> None:
    """Print only aggregate findings and taxonomy filenames from the fixed local root."""
    root = _DEFAULT_ROOT.resolve(strict=False)
    if not root.is_dir():
        raise SystemExit(f"wildcard collection not found at {root}")
    files = sorted(root.glob("*.txt"), key=lambda path: path.name.casefold())
    normalized: Counter[str] = Counter()
    lines = 0
    empty_files = 0
    proper_names = 0
    unsafe = 0
    multi_dimension = 0
    for path in files:
        entries = [
            line.strip()
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip()
        ]
        if not entries:
            empty_files += 1
        for entry in entries:
            lines += 1
            normalized[" ".join(entry.casefold().split())] += 1
            proper_names += bool(_PROPER_NAME.fullmatch(entry))
            unsafe += bool(_UNSAFE.search(entry))
            multi_dimension += bool(_MULTI_DIMENSION.search(entry) or len(entry) > 140)
    duplicate_lines = sum(count - 1 for count in normalized.values() if count > 1)
    taxonomies = ", ".join(path.stem for path in files)
    print(
        f"PASS: audited {len(files)} TXT files and {lines} non-empty lines; "
        f"empty_files={empty_files}; duplicate_lines={duplicate_lines}; "
        f"proper_name_candidates={proper_names}; unsafe_candidates={unsafe}; "
        f"multi_dimension_candidates={multi_dimension}"
    )
    print(f"TAXONOMY FILES: {taxonomies}")
    print("POLICY: taxonomy names only; no external line is copied into official catalog data")


if __name__ == "__main__":
    main()
