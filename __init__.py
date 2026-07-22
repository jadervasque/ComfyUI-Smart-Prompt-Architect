"""ComfyUI custom-node entry module."""

from prompt_architect.extension import comfy_entrypoint

WEB_DIRECTORY = "./prompt_architect/web"

__all__ = ["WEB_DIRECTORY", "comfy_entrypoint"]
