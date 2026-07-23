"""Pure parsing and precedence rules for ComfyUI node inputs."""

from collections.abc import Mapping

from prompt_architect.domain.enums import FieldMode
from prompt_architect.domain.exceptions import ConfigurationError, SchemaValidationError
from prompt_architect.domain.models import NodeConfiguration, ProfileDefinition
from prompt_architect.domain.parser import (
    CURRENT_CONFIGURATION_SCHEMA_VERSION,
    parse_configuration,
    parse_profile,
)
from prompt_architect.domain.seeds import derive_seed
from prompt_architect.infrastructure.json_loader import decode_json_object

MAX_NODE_JSON_BYTES = 262_144


def parse_profile_override(value: str) -> ProfileDefinition | None:
    """Parse an optional bounded connected profile override object."""
    if not value.strip():
        return None
    return parse_profile(_json_input(value, "profile_override_json"))


def build_node_configuration(
    *,
    profile: str,
    profile_version: str = "1.0.0",
    seed: int,
    generation_mode: str,
    identity_lock: bool,
    configuration_json: str,
    positive_prefix: str,
    positive_suffix: str,
    negative_prefix: str,
    negative_suffix: str,
    external_context_json: str = "",
    batch_index: int = 0,
) -> NodeConfiguration:
    """Merge serialized state and visible/connected inputs with explicit precedence."""
    if configuration_json.strip() in {"", "{}"}:
        data: dict[str, object] = {}
    else:
        data = _json_input(configuration_json, "configuration_json")
    data.update(
        {
            "schema_version": CURRENT_CONFIGURATION_SCHEMA_VERSION,
            "profile_id": profile,
            "profile_version": profile_version,
            "mode": generation_mode,
            "master_seed": seed,
            "batch_index": batch_index,
        }
    )
    groups = _mutable_mapping(data.get("groups", {}), "configuration_json.groups")
    identity = _mutable_mapping(groups.get("identity", {}), "configuration_json.groups.identity")
    identity["locked"] = identity_lock
    if identity_lock and identity.get("seed") is None:
        identity["seed"] = derive_seed(seed, "identity-lock")
    groups["identity"] = identity
    data["groups"] = groups
    fields = _mutable_mapping(data.get("fields", {}), "configuration_json.fields")
    if external_context_json.strip():
        external = _json_input(external_context_json, "external_context_json")
        for field_id, option_id in external.items():
            if not isinstance(option_id, str) or not option_id.strip():
                raise ConfigurationError(
                    f"external_context_json.{field_id}: value must be a non-empty option ID"
                )
            fields[field_id] = {"mode": FieldMode.FIXED.value, "value": option_id.strip()}
    data["fields"] = fields
    data["overrides"] = {
        "positive_prefix": positive_prefix,
        "positive_suffix": positive_suffix,
        "negative_prefix": negative_prefix,
        "negative_suffix": negative_suffix,
    }
    return parse_configuration(data)


def _json_input(value: str, label: str) -> dict[str, object]:
    encoded = value.encode("utf-8")
    if len(encoded) > MAX_NODE_JSON_BYTES:
        raise SchemaValidationError(f"{label}: JSON exceeds {MAX_NODE_JSON_BYTES} byte limit")
    return decode_json_object(encoded, label)


def _mutable_mapping(value: object, path: str) -> dict[str, object]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise ConfigurationError(f"{path}: must be a JSON object")
    return {str(key): item for key, item in value.items()}


def node_input_fingerprint(inputs: Mapping[str, object], data_fingerprint: str) -> str:
    """Hash node inputs and bundled data without NaN cache sentinels."""
    from prompt_architect.infrastructure.hashing import canonical_json_hash

    safe_inputs = {
        key: value
        for key, value in sorted(inputs.items())
        if isinstance(value, (str, int, float, bool)) or value is None
    }
    return canonical_json_hash({"inputs": safe_inputs, "data": data_fingerprint})
