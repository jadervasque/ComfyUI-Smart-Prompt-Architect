"""Small deterministic composition performance guard for CI and release checks."""

from __future__ import annotations

import argparse
import time

from prompt_architect.application.compose_service import compose_prompt
from prompt_architect.domain.parser import parse_configuration
from prompt_architect.infrastructure.repository import bundled_repository


def main() -> None:
    """Compose each official profile repeatedly and enforce an optional wall-time limit."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=1_000)
    parser.add_argument("--max-seconds", type=float, default=30.0)
    arguments = parser.parse_args()
    if arguments.iterations <= 0 or arguments.max_seconds <= 0:
        parser.error("iterations and max-seconds must be positive")

    repository = bundled_repository()
    profiles = [item.id for item in repository.list_profiles()]
    contexts = {}
    for profile_id in profiles:
        profile = repository.load_profile(profile_id)
        libraries = {
            section.library: repository.load_library(section.library)
            for section in profile.sections.values()
        }
        contexts[profile_id] = (profile, libraries)
    started = time.perf_counter()
    compositions = 0
    for profile_id in profiles:
        profile, libraries = contexts[profile_id]
        for seed in range(arguments.iterations):
            configuration = parse_configuration(
                {
                    "schema_version": "1.0",
                    "profile_id": profile_id,
                    "profile_version": "1.0.0",
                    "mode": "balanced",
                    "master_seed": seed,
                }
            )
            compose_prompt(profile, libraries, configuration)
            compositions += 1
    elapsed = time.perf_counter() - started
    rate = compositions / elapsed
    print(f"PASS: {compositions} compositions in {elapsed:.3f}s ({rate:.1f}/s)")
    if elapsed > arguments.max_seconds:
        raise SystemExit(f"benchmark exceeded {arguments.max_seconds:.3f}s limit: {elapsed:.3f}s")


if __name__ == "__main__":
    main()
