"""Report deterministic Catalog V2 counts without loading ComfyUI."""

from __future__ import annotations

from collections import Counter

from prompt_architect.infrastructure.repository import bundled_repository


def main() -> None:
    """Print pack, domain, option, variant, family, and safety totals."""
    repository = bundled_repository()
    index = repository.load_catalog_index()
    domains: Counter[str] = Counter()
    safety: Counter[str] = Counter()
    options = 0
    variants = 0
    families: set[str] = set()
    option_ids: set[str] = set()
    for reference in index.packs:
        library = repository.load_library(reference.library)
        pack_options = [option for option in library.options if option.pack_id == reference.id]
        domains[reference.domain] += len(pack_options)
        safety[reference.safety] += len(pack_options)
        options += len(pack_options)
        variants += sum(len(option.variants) for option in pack_options)
        families.update(option.family for option in pack_options if option.family is not None)
        option_ids.update(option.id for option in pack_options)
    if len(option_ids) != options:
        raise SystemExit("catalog option IDs are not globally unique")
    print(
        f"PASS: catalog {index.version}; {len(index.packs)} packs; "
        f"{len(index.libraries)} libraries; {options} options; "
        f"{variants} variants; {len(families)} families"
    )
    print("DOMAINS " + " ".join(f"{key}={domains[key]}" for key in sorted(domains)))
    print("SAFETY " + " ".join(f"{key}={safety[key]}" for key in sorted(safety)))


if __name__ == "__main__":
    main()
