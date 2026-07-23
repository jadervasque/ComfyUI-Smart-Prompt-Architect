"""Thin aiohttp routes for local read-only preview and validation."""

from __future__ import annotations

from collections.abc import Callable

from aiohttp import web
from server import PromptServer

from prompt_architect.application import preview_api
from prompt_architect.domain.exceptions import PromptArchitectError

_ROUTES_REGISTERED = False


def register_routes() -> None:
    """Register versioned routes once on the active ComfyUI PromptServer."""
    global _ROUTES_REGISTERED
    if _ROUTES_REGISTERED:
        return
    routes = PromptServer.instance.routes

    routes.get("/prompt_architect/v1/profiles")(_profiles)
    routes.get("/prompt_architect/v1/profiles/{profile_id}")(_profile)
    routes.post("/prompt_architect/v1/preview")(_preview)
    routes.post("/prompt_architect/v1/validate")(_validate)
    _ROUTES_REGISTERED = True


async def _profiles(_: web.Request) -> web.Response:
    return _success(preview_api.list_profiles())


async def _profile(request: web.Request) -> web.Response:
    return _call(lambda: preview_api.get_profile(request.match_info["profile_id"]))


async def _preview(request: web.Request) -> web.Response:
    return await _post(request, preview_api.preview)


async def _validate(request: web.Request) -> web.Response:
    return await _post(request, preview_api.validate)


async def _post(
    request: web.Request,
    operation: Callable[[dict[str, object]], dict[str, object]],
) -> web.Response:
    content_length = request.content_length
    if content_length is not None and content_length > preview_api.MAX_PREVIEW_PAYLOAD_BYTES:
        return _error(413, "payload_too_large", "request payload is too large")
    content = await request.content.read(preview_api.MAX_PREVIEW_PAYLOAD_BYTES + 1)
    if len(content) > preview_api.MAX_PREVIEW_PAYLOAD_BYTES:
        return _error(413, "payload_too_large", "request payload is too large")
    try:
        payload = preview_api.decode_preview_payload(content)
    except (PromptArchitectError, ValueError, UnicodeError) as error:
        return _error(400, "invalid_json", str(error))
    return _call(lambda: operation(payload))


def _call(operation: Callable[[], dict[str, object]]) -> web.Response:
    try:
        return _success(operation())
    except PromptArchitectError as error:
        status = 404 if "file not found" in str(error) else 400
        return _error(status, type(error).__name__, str(error))
    except ValueError as error:
        return _error(400, "invalid_request", str(error))


def _success(data: dict[str, object]) -> web.Response:
    return web.json_response({"ok": True, "data": data})


def _error(status: int, code: str, message: str) -> web.Response:
    return web.json_response(
        {"ok": False, "error": {"code": code, "message": message}}, status=status
    )
