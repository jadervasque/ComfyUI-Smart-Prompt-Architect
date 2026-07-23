"""Versioned ComfyUI API V3 extension entry point."""

from comfy_api.v0_0_2 import ComfyExtension, io

from prompt_architect.comfy.nodes import (
    PromptArchitectNode,
    PromptArchitectSetupLibraryNode,
)


class PromptArchitectExtension(ComfyExtension):
    """Expose Prompt Architect nodes to ComfyUI."""

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        """Return public node classes in stable order."""
        return [PromptArchitectNode, PromptArchitectSetupLibraryNode]


async def comfy_entrypoint() -> PromptArchitectExtension:
    """Create the Prompt Architect V3 extension."""
    return PromptArchitectExtension()
