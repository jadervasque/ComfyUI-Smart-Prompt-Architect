"""Stable seed derivation and group lock handling."""

import hashlib
from collections.abc import Mapping
from types import MappingProxyType

from prompt_architect.domain.models import GroupConfiguration, NodeConfiguration, ProfileDefinition


def derive_seed(master_seed: int, namespace: str) -> int:
    """Derive an unsigned 64-bit subseed with stable SHA-256."""
    if master_seed < 0 or master_seed > (2**64 - 1):
        raise ValueError("master_seed must be between 0 and 2^64-1")
    if not namespace:
        raise ValueError("namespace cannot be empty")
    payload = f"{master_seed}:{namespace}".encode()
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def resolve_group_seed(
    master_seed: int,
    group_id: str,
    configuration: GroupConfiguration | None = None,
) -> int:
    """Use an explicit locked seed or derive one independently from the master seed."""
    group = configuration or GroupConfiguration()
    if group.locked and group.seed is not None:
        return group.seed
    return derive_seed(master_seed, f"group:{group_id}")


def resolve_group_seeds(
    profile: ProfileDefinition, configuration: NodeConfiguration
) -> Mapping[str, int]:
    """Resolve every profile group in sorted order without depending on filesystem order."""
    group_ids = sorted({section.group for section in profile.sections.values()})
    return MappingProxyType(
        {
            group_id: resolve_group_seed(
                configuration.master_seed,
                group_id,
                configuration.groups.get(group_id),
            )
            for group_id in group_ids
        }
    )


def derive_section_seed(group_seed: int, section_id: str, batch_index: int = 0) -> int:
    """Derive one section RNG seed, including explicit dataset/sequential index."""
    if batch_index < 0:
        raise ValueError("batch_index must be non-negative")
    return derive_seed(group_seed, f"section:{section_id}:batch:{batch_index}")
