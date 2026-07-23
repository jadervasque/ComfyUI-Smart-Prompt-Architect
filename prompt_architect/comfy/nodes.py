"""ComfyUI API V3 node adapter; domain logic remains in the pure core."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from comfy_api.v0_0_2 import io

from prompt_architect.application.compose_service import ComposeService
from prompt_architect.comfy.errors import node_error
from prompt_architect.comfy.schemas import (
    build_node_configuration,
    node_input_fingerprint,
    parse_profile_override,
)
from prompt_architect.domain.enums import GenerationMode
from prompt_architect.domain.exceptions import ConfigurationError, PromptArchitectError
from prompt_architect.infrastructure.repository import bundled_repository

if TYPE_CHECKING:
    from prompt_architect.domain.models import CompositionResult

_PROFILE_SUMMARIES = bundled_repository().list_profiles()
_PROFILE_IDS = [summary.id for summary in _PROFILE_SUMMARIES]
_PROFILE_VERSIONS = {summary.id: summary.version for summary in _PROFILE_SUMMARIES}
_DATA_ROOT = Path(__file__).resolve().parents[1] / "data"


class PromptArchitectNode(io.ComfyNode):
    """Compose deterministic structured prompts without a model or GPU."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define the public V3 node schema and tooltips."""
        return io.Schema(
            node_id="PromptArchitect_PromptArchitect",
            display_name="Prompt Architect",
            category="Prompt Architect/Generation",
            description="Compose validated deterministic positive and negative prompts.",
            search_aliases=["structured prompt", "deterministic prompt"],
            inputs=[
                io.Combo.Input(
                    "profile",
                    options=_PROFILE_IDS,
                    default="portrait-core",
                    tooltip="Bundled or overridden versioned prompt profile.",
                ),
                io.Int.Input(
                    "seed",
                    default=0,
                    min=0,
                    max=2**64 - 1,
                    control_after_generate=True,
                    tooltip="Unsigned master seed used to derive independent group seeds.",
                ),
                io.Combo.Input(
                    "generation_mode",
                    options=[mode.value for mode in GenerationMode],
                    default=GenerationMode.BALANCED.value,
                    tooltip="Strictness and deterministic diversity strategy.",
                ),
                io.Boolean.Input(
                    "strict_validation",
                    default=True,
                    tooltip=(
                        "Keep full profile validation enabled; empty-prompt safety always applies."
                    ),
                ),
                io.Boolean.Input(
                    "identity_lock",
                    default=True,
                    tooltip="Use a stable explicit subseed for the identity group.",
                ),
                io.String.Input(
                    "configuration_json",
                    default="{}",
                    multiline=True,
                    tooltip="Portable advanced configuration JSON stored in the workflow.",
                ),
                io.String.Input(
                    "positive_prefix", default="", tooltip="Text placed before positive output."
                ),
                io.String.Input(
                    "positive_suffix", default="", tooltip="Text placed after positive output."
                ),
                io.String.Input(
                    "negative_prefix", default="", tooltip="Text placed before negative output."
                ),
                io.String.Input(
                    "negative_suffix", default="", tooltip="Text placed after negative output."
                ),
                io.String.Input(
                    "profile_override_json",
                    default="",
                    multiline=True,
                    optional=True,
                    advanced=True,
                    tooltip="Optional connected profile JSON; no paths or code are accepted.",
                ),
                io.String.Input(
                    "external_context_json",
                    default="",
                    multiline=True,
                    optional=True,
                    advanced=True,
                    tooltip="Optional object mapping section IDs to fixed option IDs.",
                ),
                io.Int.Input(
                    "batch_index",
                    default=0,
                    min=0,
                    optional=True,
                    advanced=True,
                    tooltip="Explicit deterministic index for dataset or sequential composition.",
                ),
            ],
            outputs=[
                io.String.Output("positive_prompt", tooltip="Validated non-empty positive prompt."),
                io.String.Output(
                    "negative_prompt", tooltip="Validated negative prompt, when required."
                ),
                io.String.Output(
                    "manifest_json", tooltip="Canonical reproducibility manifest JSON."
                ),
                io.String.Output(
                    "summary", tooltip="Concise profile, seed, attempts, and warning summary."
                ),
                io.Int.Output("seed_used", tooltip="Master seed used for this composition."),
            ],
        )

    @classmethod
    def execute(
        cls,
        profile: str,
        seed: int,
        generation_mode: str,
        strict_validation: bool,
        identity_lock: bool,
        configuration_json: str,
        positive_prefix: str,
        positive_suffix: str,
        negative_prefix: str,
        negative_suffix: str,
        profile_override_json: str = "",
        external_context_json: str = "",
        batch_index: int = 0,
    ) -> io.NodeOutput:
        """Execute the pure composition service and return five V3 outputs."""
        del strict_validation  # Mandatory safety remains enabled in every mode.
        try:
            configuration = build_node_configuration(
                profile=profile,
                profile_version=_PROFILE_VERSIONS[profile],
                seed=seed,
                generation_mode=generation_mode,
                identity_lock=identity_lock,
                configuration_json=configuration_json,
                positive_prefix=positive_prefix,
                positive_suffix=positive_suffix,
                negative_prefix=negative_prefix,
                negative_suffix=negative_suffix,
                external_context_json=external_context_json,
                batch_index=batch_index,
            )
            override = parse_profile_override(profile_override_json)
            if override is not None and override.id != profile:
                raise ConfigurationError(
                    f"profile override ID {override.id!r} does not match "
                    f"selected profile {profile!r}"
                )
            overrides = {override.id: override} if override is not None else None
            repository = bundled_repository(profile_overrides=overrides)
            result: CompositionResult = ComposeService(repository).compose(configuration)
        except PromptArchitectError as error:
            raise node_error(error) from None
        return io.NodeOutput(
            result.rendered.positive,
            result.rendered.negative,
            result.manifest_json,
            result.summary,
            result.seed_used,
        )

    @classmethod
    def fingerprint_inputs(cls, **kwargs: Any) -> str:
        """Invalidate execution cache on any input or packaged JSON content change."""
        return node_input_fingerprint(kwargs, _bundled_data_fingerprint())


class PromptArchitectSetupLibraryNode(io.ComfyNode):
    """Workflow-local setup library without input or output ports."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Define a utility node that stores setup JSON in workflow metadata."""
        return io.Schema(
            node_id="PromptArchitect_SetupLibrary",
            display_name="Prompt Architect Setup Library",
            category="Prompt Architect/Utilities",
            description="Store and manage reusable setup JSON snippets inside the workflow.",
            search_aliases=["setup library", "json presets", "workflow notes"],
            inputs=[],
            outputs=[],
        )

    @classmethod
    def execute(cls) -> io.NodeOutput:
        """No-op execution; this node only stores serialized workflow metadata."""
        return io.NodeOutput()


def _bundled_data_fingerprint() -> str:
    digest = hashlib.sha256()
    for path in sorted(_DATA_ROOT.rglob("*.json"), key=lambda item: item.as_posix()):
        digest.update(path.relative_to(_DATA_ROOT).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()
