"""
Deterministic JSON canonicalization and stable hashing for evidence artifacts.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None  # type: ignore


class EvidenceSerializationError(TypeError):
    """Raised when a value cannot be canonicalized for evidence JSON."""


def canonicalize(obj: Any) -> Any:
    """
    Convert ``obj`` to a JSON-serializable structure with deterministic ordering.

    Raises ``EvidenceSerializationError`` for unsupported types.
    """
    if obj is None or isinstance(obj, (str, bool)):
        return obj
    if isinstance(obj, int) and not isinstance(obj, bool):
        return int(obj)
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return str(obj)
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        val = float(obj)
        if np.isnan(val) or np.isinf(val):
            return str(val)
        return val
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return canonicalize(obj.tolist())
    if pd is not None:
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.Timedelta):
            return str(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Mapping):
        return {
            str(k): canonicalize(v)
            for k, v in sorted(obj.items(), key=lambda item: str(item[0]))
        }
    if isinstance(obj, (list, tuple)):
        return [canonicalize(v) for v in obj]
    if isinstance(obj, set):
        normalized = [canonicalize(v) for v in obj]
        return sorted(normalized, key=lambda x: json.dumps(x, sort_keys=True, default=str))
    if is_dataclass(obj):
        return canonicalize(asdict(obj))
    raise EvidenceSerializationError(
        f"Cannot canonicalize type {type(obj).__name__!r} for evidence JSON."
    )


def canonical_json(obj: Any) -> str:
    """Stable JSON string (sorted keys, compact separators)."""
    return json.dumps(canonicalize(obj), sort_keys=True, separators=(",", ":"))


def stable_hash(obj: Any, *, digest_bytes: int = 16) -> str:
    """SHA-256 hex digest (truncated to ``digest_bytes`` bytes = 2× hex chars)."""
    digest = hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
    return digest[: 2 * digest_bytes]


def canonical_assignment(
    assignment: Dict[str, List],
) -> Dict[str, Tuple[str, ...]]:
    """
    Frozen canonical assignment: sorted group keys, sorted string unit ids per group.
    """
    if not isinstance(assignment, Mapping):
        raise EvidenceSerializationError(
            f"assignment must be a mapping, got {type(assignment).__name__!r}"
        )
    return {
        str(k): tuple(sorted(str(u) for u in v))
        for k, v in sorted(assignment.items(), key=lambda item: str(item[0]))
    }


def assignment_hash(assignment: Dict[str, List]) -> str:
    """
    Stable hash of a design assignment.

    Arm-label sensitive and unit-order insensitive within each arm:
    reordering units inside ``control`` does not change the hash; moving a unit
  from ``control`` to ``test_0`` does; swapping units across ``test_0`` vs
    ``test_1`` does.
    """
    canonical = canonical_assignment(assignment)
    payload = {k: list(v) for k, v in canonical.items()}
    return stable_hash(payload)


def assignment_to_json_dict(assignment: Mapping[str, Tuple[str, ...]]) -> Dict[str, List[str]]:
    """JSON-friendly assignment dict with deterministic key order."""
    return {k: list(assignment[k]) for k in sorted(assignment.keys())}


def input_structure_hash_from_wide(
    wide_data: Any,
    *,
    value_sample_size: int = 0,
) -> Optional[str]:
    """
    Structural panel fingerprint (unit index, time columns, shape).

    This is **not** a full data-content hash and does not prove value-level
    provenance. ``input_data_hash`` is a backward-compatible alias for this
    function.

    When ``value_sample_size > 0``, a short leading slice of flattened values is
    included for diagnostics only (still not a full-matrix hash).
    """
    if wide_data is None:
        return None
    try:
        index = [str(u) for u in wide_data.index.tolist()]
        columns = [str(c) for c in wide_data.columns.tolist()]
        payload: Dict[str, Any] = {
            "index": sorted(index),
            "columns": columns,
            "shape": [int(wide_data.shape[0]), int(wide_data.shape[1])],
        }
        if value_sample_size > 0:
            flat = np.asarray(wide_data.values, dtype=float).ravel()
            n = min(value_sample_size, flat.size)
            if n > 0:
                payload["value_sample"] = [float(x) for x in flat[:n]]
        return stable_hash(payload)
    except Exception:
        return None


def input_data_hash_from_wide(
    wide_data: Any,
    *,
    value_sample_size: int = 0,
) -> Optional[str]:
    """Backward-compatible alias for :func:`input_structure_hash_from_wide`."""
    return input_structure_hash_from_wide(
        wide_data, value_sample_size=value_sample_size
    )


def deep_freeze(obj: Any) -> Any:
    """
    Recursively freeze mappings and sequences for immutable evidence payloads.

    - dict-like -> ``MappingProxyType`` with frozen values
    - list/tuple -> ``tuple`` with frozen elements
    - scalars unchanged
    """
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, Mapping):
        frozen = {str(k): deep_freeze(v) for k, v in obj.items()}
        return MappingProxyType(frozen)
    if isinstance(obj, (list, tuple)):
        return tuple(deep_freeze(v) for v in obj)
    if isinstance(obj, Enum):
        return obj.value
    raise EvidenceSerializationError(
        f"Cannot deep-freeze type {type(obj).__name__!r} for evidence storage."
    )
