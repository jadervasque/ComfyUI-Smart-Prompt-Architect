"""Framework-independent read-only API operations for the local editor."""

from __future__ import annotations

import json
from collections.abc import Mapping

from prompt_architect.application.compose_service import ComposeService
from prompt_architect.domain.models import CompositionResult
from prompt_architect.domain.parser import parse_configuration
from prompt_architect.domain.seeds import derive_seed
from prompt_architect.infrastructure.json_loader import decode_json_object
from prompt_architect.infrastructure.repository import PromptDataRepository, bundled_repository

MAX_PREVIEW_PAYLOAD_BYTES = 262_144


def decode_preview_payload(content: bytes) -> dict[str, object]:
    """Decode one bounded JSON object without accepting duplicate keys."""
    if len(content) > MAX_PREVIEW_PAYLOAD_BYTES:
        raise ValueError(f"request exceeds {MAX_PREVIEW_PAYLOAD_BYTES} byte limit")
    return decode_json_object(content, "request")


def list_profiles(repository: PromptDataRepository | None = None) -> dict[str, object]:
    """Return safe public metadata for all valid profiles."""
    source = repository or bundled_repository()
    return {
        "profiles": [
            {
                "id": item.id,
                "version": item.version,
                "display_name": item.display_name,
                "language": item.language,
            }
            for item in source.list_profiles()
        ]
    }


def get_profile(
    profile_id: str, repository: PromptDataRepository | None = None
) -> dict[str, object]:
    """Return editor metadata and selectable options for one validated profile ID."""
    source = repository or bundled_repository()
    profile = source.load_profile(profile_id)
    sections: list[dict[str, object]] = []
    for section_id in profile.section_order:
        section = profile.sections[section_id]
        library = source.load_library_for_profile(profile, section.library)
        sections.append(
            {
                "id": section.id,
                "required": section.required,
                "library": section.library,
                "mode": section.mode.value,
                "group": section.group,
                "default": section.default,
                "fallback": section.fallback,
                "options": [
                    {
                        "id": option.id,
                        "text": option.text,
                        "tags": list(option.tags),
                        "status": option.status.value,
                    }
                    for option in library.options
                ],
            }
        )
    return {
        "profile": {
            "id": profile.id,
            "version": profile.version,
            "display_name": profile.display_name,
            "language": profile.language,
            "sections": sections,
        }
    }


def preview(
    payload: Mapping[str, object], repository: PromptDataRepository | None = None
) -> dict[str, object]:
    """Compose a preview using the same authoritative application pipeline as the node."""
    configuration_data = payload.get("configuration", payload)
    if not isinstance(configuration_data, Mapping) or not all(
        isinstance(key, str) for key in configuration_data
    ):
        raise ValueError("configuration must be a JSON object")
    configuration = parse_configuration(_materialize_identity_seed(configuration_data))
    result = ComposeService(repository or bundled_repository()).compose(configuration)
    return _result_payload(result)


def validate(
    payload: Mapping[str, object], repository: PromptDataRepository | None = None
) -> dict[str, object]:
    """Validate and compose without queuing or mutating files."""
    result = preview(payload, repository)
    manifest = result["manifest"]
    if not isinstance(manifest, dict):
        raise RuntimeError("preview manifest payload is not an object")
    return {
        "valid": True,
        "issues": result["issues"],
        "configuration_hash": manifest["configuration_hash"],
        "summary": result["summary"],
    }


def _result_payload(result: CompositionResult) -> dict[str, object]:
    return {
        "positive_prompt": result.rendered.positive,
        "negative_prompt": result.rendered.negative,
        "manifest": json.loads(result.manifest_json),
        "summary": result.summary,
        "seed_used": result.seed_used,
        "issues": [
            {
                "code": issue.code,
                "message": issue.message,
                "severity": issue.severity.value,
                "path": issue.path,
            }
            for issue in result.issues
        ],
    }


def _materialize_identity_seed(configuration: Mapping[str, object]) -> dict[str, object]:
    """Mirror the node's visible identity-lock precedence for exact preview parity."""
    data = dict(configuration)
    groups_value = data.get("groups", {})
    if not isinstance(groups_value, Mapping):
        return data
    groups = dict(groups_value)
    identity_value = groups.get("identity", {})
    if not isinstance(identity_value, Mapping):
        return data
    identity = dict(identity_value)
    master_seed = data.get("master_seed")
    if (
        identity.get("locked") is True
        and identity.get("seed") is None
        and isinstance(master_seed, int)
    ):
        identity["seed"] = derive_seed(master_seed, "identity-lock")
        groups["identity"] = identity
        data["groups"] = groups
    return data
