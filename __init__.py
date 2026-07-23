"""ComfyUI custom-node entry module."""

import sys
from importlib import import_module

if __package__:
    _package_name = f"{__package__}.prompt_architect"
    _prompt_architect = import_module(".prompt_architect", __package__)
else:
    _package_name = "prompt_architect"
    _prompt_architect = import_module(_package_name)

# ComfyUI loads custom-node folders under an implementation-defined module name.
# Publish the nested package under its stable import name before loading adapters.
sys.modules.setdefault("prompt_architect", _prompt_architect)

_server_module = sys.modules.get("server")
_prompt_server = getattr(_server_module, "PromptServer", None)
if getattr(_prompt_server, "instance", None) is not None:
    import_module(f"{_package_name}.comfy.routes").register_routes()


async def comfy_entrypoint() -> object:
    """Load the V3 extension lazily so package tooling does not require ComfyUI."""
    entrypoint = import_module(f"{_package_name}.extension").comfy_entrypoint
    return await entrypoint()


WEB_DIRECTORY = "./prompt_architect/web"

__all__ = ["WEB_DIRECTORY", "comfy_entrypoint"]
