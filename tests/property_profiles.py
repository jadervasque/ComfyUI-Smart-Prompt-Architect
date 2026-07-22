"""Dedicated 10,000-seed reliability runner for every bundled profile."""

import re
import sys

from prompt_architect.application.compose_service import compose_prompt
from tests.test_official_data import _PROFILE_IDS, official_configuration, official_context

_PLACEHOLDER = re.compile(r"\{[^{}]+\}")


def main() -> int:
    """Return nonzero on the first reproducibility or prompt-integrity failure."""
    for profile_id in _PROFILE_IDS:
        profile, libraries = official_context(profile_id)
        for seed in range(10_000):
            configuration = official_configuration(profile_id, seed)
            first = compose_prompt(profile, libraries, configuration)
            second = compose_prompt(profile, libraries, configuration)
            if not first.rendered.positive.strip():
                raise AssertionError(f"{profile_id} seed {seed}: empty positive prompt")
            if _PLACEHOLDER.search(first.rendered.positive):
                raise AssertionError(f"{profile_id} seed {seed}: residual placeholder")
            if first.manifest_json != second.manifest_json:
                raise AssertionError(f"{profile_id} seed {seed}: nondeterministic result")
        print(f"PASS {profile_id}: 10000 seeds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
