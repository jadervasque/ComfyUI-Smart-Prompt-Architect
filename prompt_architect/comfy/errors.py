"""Safe conversion of expected domain failures for ComfyUI execution."""

from prompt_architect.domain.exceptions import PromptArchitectError


class PromptArchitectNodeError(RuntimeError):
    """Clear execution error shown by ComfyUI instead of a raw domain exception."""


def node_error(error: PromptArchitectError) -> PromptArchitectNodeError:
    """Create a concise public node error without sensitive paths or prompt text."""
    return PromptArchitectNodeError(f"Prompt Architect could not compose the prompt: {error}")
