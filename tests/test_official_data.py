"""Fast integration checks for bundled official profiles and libraries."""

import unittest

from prompt_architect.application.compose_service import ComposeService, compose_prompt
from prompt_architect.domain.enums import GenerationMode
from prompt_architect.domain.models import (
    GroupConfiguration,
    LibraryDefinition,
    NodeConfiguration,
    ProfileDefinition,
)
from prompt_architect.infrastructure.repository import bundled_repository

_PROFILE_IDS = ("dataset", "portrait", "virtual-model")
_LIBRARY_IDS = {
    "subjects",
    "identity",
    "face",
    "eyes",
    "mouth",
    "skin",
    "hair-color",
    "hair-length",
    "hair-texture",
    "hair-style",
    "body",
    "outfit",
    "expression",
    "pose",
    "location",
    "lighting",
    "camera",
    "composition",
    "quality",
    "negative",
}


def official_configuration(profile_id: str, seed: int) -> NodeConfiguration:
    """Create a portable official-profile configuration for tests and examples."""
    mode = GenerationMode.DATASET if profile_id == "dataset" else GenerationMode.BALANCED
    return NodeConfiguration(
        "1.0",
        profile_id,
        "1.0.0",
        mode,
        seed,
        groups={"identity": GroupConfiguration(locked=True, seed=20260722)},
        batch_index=seed if profile_id == "dataset" else 0,
    )


def official_context(
    profile_id: str,
) -> tuple[ProfileDefinition, dict[str, LibraryDefinition]]:
    """Preload immutable official data for high-volume core tests."""
    repository = bundled_repository()
    profile = repository.load_profile(profile_id)
    library_ids = sorted({section.library for section in profile.sections.values()})
    libraries = {library_id: repository.load_library(library_id) for library_id in library_ids}
    return profile, libraries


class OfficialDataTests(unittest.TestCase):
    """Bundled content loads and composes without hidden dependencies."""

    def test_three_profiles_are_listed_and_valid(self) -> None:
        repository = bundled_repository()
        self.assertEqual(tuple(summary.id for summary in repository.list_profiles()), _PROFILE_IDS)

    def test_all_minimum_libraries_load(self) -> None:
        repository = bundled_repository()
        loaded = {library_id for library_id in _LIBRARY_IDS if repository.load_library(library_id)}
        self.assertEqual(loaded, _LIBRARY_IDS)

    def test_first_hundred_seeds_per_profile_are_valid_and_deterministic(self) -> None:
        for profile_id in _PROFILE_IDS:
            profile, libraries = official_context(profile_id)
            for seed in range(100):
                with self.subTest(profile=profile_id, seed=seed):
                    configuration = official_configuration(profile_id, seed)
                    first = compose_prompt(profile, libraries, configuration)
                    second = compose_prompt(profile, libraries, configuration)
                    self.assertTrue(first.rendered.positive.strip())
                    self.assertNotIn("{", first.rendered.positive)
                    self.assertEqual(first.manifest_json, second.manifest_json)

    def test_compose_service_loads_bundled_data(self) -> None:
        result = ComposeService(bundled_repository()).compose(official_configuration("portrait", 1))
        self.assertTrue(result.rendered.positive)


if __name__ == "__main__":
    unittest.main()
