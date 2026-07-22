"""Stable hashing helpers for files and canonical JSON-compatible data."""

import hashlib
import json


def sha256_bytes(content: bytes) -> str:
    """Return a lowercase SHA-256 hex digest for bytes."""
    return hashlib.sha256(content).hexdigest()


def canonical_json_hash(data: object) -> str:
    """Hash canonical UTF-8 JSON without relying on insertion order."""
    payload = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return f"sha256:{sha256_bytes(payload)}"
