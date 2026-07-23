"""Catalog V2 contracts, pack composition, and stratified mode behavior."""

from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path

from prompt_architect.application.compose_service import ComposeService
from prompt_architect.domain.enums import FieldMode, GenerationMode
from prompt_architect.domain.exceptions import (
    LibraryLoadError,
    SchemaValidationError,
    SelectionError,
)
from prompt_architect.domain.models import (
    FieldConfiguration,
    NodeConfiguration,
    PromptOption,
)
from prompt_architect.domain.parser import parse_catalog_index
from prompt_architect.domain.selector import hierarchical_choice
from prompt_architect.infrastructure.repository import (
    JsonPromptDataRepository,
    bundled_repository,
)


def _pack(pack_id: str, option_id: str) -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "id": pack_id,
        "version": "2.0.0",
        "library": "combined",
        "domain": "identity",
        "category": "test",
        "language": "en",
        "status": "active",
        "safety": "general",
        "tags": ["test"],
        "fallback_option_id": option_id,
        "options": [
            {
                "id": option_id,
                "semantic_key": option_id,
                "text": f"text for {option_id}",
                "family": f"{pack_id}-family",
                "facets": {"kind": "test"},
                "variants": [
                    {"id": "plain", "text": f"text for {option_id}"},
                    {"id": "alternate", "text": f"alternate text for {option_id}"},
                ],
            }
        ],
    }


def _index(pack_ids: tuple[str, ...]) -> dict[str, object]:
    return {
        "schema_version": "2.0",
        "id": "test-catalog",
        "version": "2.0.0",
        "language": "en",
        "packs": [
            {
                "id": pack_id,
                "library": "combined",
                "domain": "identity",
                "path": f"packs/{pack_id}.json",
                "version": "2.0.0",
                "language": "en",
                "status": "active",
                "safety": "general",
                "tags": ["test"],
                "dependencies": [],
                "priority": index,
            }
            for index, pack_id in enumerate(pack_ids)
        ],
        "libraries": {
            "combined": {
                "display_name": "Combined",
                "packs": list(pack_ids),
                "fallback_option_id": "shared-option",
            }
        },
    }


class CatalogV2Tests(unittest.TestCase):
    def test_index_rejects_traversal_paths(self) -> None:
        data = _index(("pack-one",))
        data["packs"][0]["path"] = "../outside.json"  # type: ignore[index]
        with self.assertRaisesRegex(SchemaValidationError, "safe relative"):
            parse_catalog_index(data)

    def test_repository_detects_option_collisions_across_packs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "catalogs" / "packs").mkdir(parents=True)
            (root / "catalogs" / "index.json").write_text(
                json.dumps(_index(("pack-one", "pack-two"))),
                encoding="utf-8",
            )
            for pack_id in ("pack-one", "pack-two"):
                (root / "catalogs" / "packs" / f"{pack_id}.json").write_text(
                    json.dumps(_pack(pack_id, "shared-option")),
                    encoding="utf-8",
                )
            repository = JsonPromptDataRepository(root)
            with self.assertRaisesRegex(LibraryLoadError, "collision"):
                repository.load_library("combined")

    def test_official_manifest_records_catalog_packs_and_variants(self) -> None:
        repository = bundled_repository()
        profile = repository.load_profile("portrait-core")
        configuration = NodeConfiguration(
            "1.1",
            profile.id,
            profile.version,
            GenerationMode.BALANCED,
            123,
        )
        result = ComposeService(repository).compose(configuration)
        self.assertEqual(result.manifest.schema_version, "2.0")
        self.assertEqual(result.manifest.catalog_version, "2.0.0")
        self.assertGreater(len(result.manifest.pack_versions), 20)
        self.assertTrue(
            all(selection["pack_id"] for selection in result.manifest.selections.values())
        )
        self.assertTrue(
            any(selection["variant_id"] for selection in result.manifest.selections.values())
        )

    def test_negative_levels_enable_only_declared_modules(self) -> None:
        repository = bundled_repository()
        minimal = repository.load_profile("portrait-core")
        standard = repository.load_profile("editorial-fashion")
        strict = repository.load_profile("professional-headshot")
        self.assertEqual(
            {item for item in minimal.sections if item.startswith("negative-")},
            {"negative-base"},
        )
        self.assertEqual(
            {item for item in standard.sections if item.startswith("negative-")},
            {"negative-base", "negative-anatomy", "negative-camera"},
        )
        self.assertEqual(
            {item for item in strict.sections if item.startswith("negative-")},
            {
                "negative-base",
                "negative-anatomy",
                "negative-camera",
                "negative-context",
            },
        )

    def test_adaptive_density_omits_full_body_details_in_close_framing(self) -> None:
        repository = bundled_repository()
        profile = repository.load_profile("full-body-fashion")
        shot_library = repository.load_library_for_profile(profile, "shot-size")
        close = next(option for option in shot_library.options if "framing-close" in option.tags)
        configuration = NodeConfiguration(
            "1.1",
            profile.id,
            profile.version,
            GenerationMode.BALANCED,
            22,
            fields={
                "shot-size": FieldConfiguration(FieldMode.FIXED, close.id),
            },
        )
        result = ComposeService(repository).compose(configuration)
        body = result.manifest.selections["body-build"]
        self.assertFalse(body["rendered"])
        self.assertTrue(any("body-build" in warning for warning in result.manifest.warnings))

    def test_strict_fixed_weather_conflict_fails_explicitly(self) -> None:
        repository = bundled_repository()
        profile = repository.load_profile("dataset-balanced")
        season_library = repository.load_library_for_profile(profile, "season")
        weather_library = repository.load_library_for_profile(profile, "weather")
        hot = next(option for option in season_library.options if "season-hot" in option.tags)
        cold = next(option for option in weather_library.options if "weather-cold" in option.tags)
        configuration = NodeConfiguration(
            "1.1",
            profile.id,
            profile.version,
            GenerationMode.STRICT,
            33,
            fields={
                "season": FieldConfiguration(FieldMode.FIXED, hot.id),
                "weather": FieldConfiguration(FieldMode.FIXED, cold.id),
            },
        )
        with self.assertRaisesRegex(SelectionError, "absolute rules"):
            ComposeService(repository).compose(configuration)

    def test_hierarchical_choice_prevents_large_family_dominance(self) -> None:
        options = [PromptOption("a-only", "A", family="a")]
        options.extend(PromptOption(f"b-{index}", f"B{index}", family="b") for index in range(8))
        family_a = sum(
            hierarchical_choice(
                options,
                random.Random(seed),
                GenerationMode.DATASET,
            ).family
            == "a"
            for seed in range(2_000)
        )
        self.assertGreater(family_a, 800)
        self.assertLess(family_a, 1_200)

    def test_creative_mode_increases_rare_selection_rate(self) -> None:
        options = (
            PromptOption("common", "Common", weight=1.0, family="one"),
            PromptOption("rare", "Rare", weight=0.15, family="one"),
        )

        def rare_count(mode: GenerationMode) -> int:
            return sum(
                hierarchical_choice(options, random.Random(seed), mode).id == "rare"
                for seed in range(5_000)
            )

        self.assertGreater(rare_count(GenerationMode.CREATIVE), rare_count(GenerationMode.BALANCED))

    def test_sequential_mode_cycles_families_then_options(self) -> None:
        options = (
            PromptOption("a-one", "A1", family="a"),
            PromptOption("a-two", "A2", family="a"),
            PromptOption("b-one", "B1", family="b"),
            PromptOption("b-two", "B2", family="b"),
        )
        selected = [
            hierarchical_choice(
                options,
                random.Random(0),
                GenerationMode.SEQUENTIAL,
                sequence_index=index,
            ).id
            for index in range(4)
        ]
        self.assertEqual(selected, ["a-one", "b-one", "a-two", "b-two"])


if __name__ == "__main__":
    unittest.main()
