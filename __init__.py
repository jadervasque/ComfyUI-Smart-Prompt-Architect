"""ComfyUI custom-node entry module."""

import sys
from importlib import import_module

from . import prompt_architect as _prompt_architect

# ComfyUI loads custom-node folders under an implementation-defined module name.
# Publish the nested package under its stable import name before loading adapters.
sys.modules.setdefault("prompt_architect", _prompt_architect)

comfy_entrypoint = import_module(".prompt_architect.extension", __package__).comfy_entrypoint
import_module(".prompt_architect.comfy.routes", __package__).register_routes()

WEB_DIRECTORY = "./prompt_architect/web"

__all__ = ["WEB_DIRECTORY", "comfy_entrypoint"]
