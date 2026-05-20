"""
Experiment and design specification contracts.

Typed boundaries for geo-panel experiments. Production-facing entry points
should accept these specs rather than inferring critical fields silently.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from panel_exp.evidence_hash import stable_hash
from panel_exp.panel_data import TimePeriod


class InterferenceAssumption(str, Enum):
    """
    User-declared interference / spillover assumption for geo experiments.

    Geo media experiments often violate SUTVA (no-interference). The package does
    not estimate spillovers; declare the assumption explicitly. ``UNKNOWN``
    weakens causal interpretation and triggers validation warnings.
    """

    NO_INTERFERENCE = "no_interference"
    PARTIAL_INTERFERENCE = "partial_interference"
    UNKNOWN = "unknown"


class DesignMethod(str, Enum):
    BALANCED_RANDOMIZATION = "balanced_randomization"
    COMPLETE_RANDOMIZATION = "complete_randomization"
    STRATIFIED_RANDOMIZATION = "stratified_randomization"
    THINNING = "thinning"
    RERANDOMIZATION = "rerandomization"
    GREEDY_MATCH = "greedy_match"
    QUICKBLOCK = "quickblock"
    MATCHED_PAIR = "matched_pair"


def spillover_metadata_available(spec: "DesignSpec") -> bool:
    """True when optional spillover-related metadata was provided (not estimated)."""
    if spec.spillover_notes and str(spec.spillover_notes).strip():
        return True
    if spec.exposure_column and str(spec.exposure_column).strip():
        return True
    if spec.assumptions.get("adjacency_matrix") is not None:
        return True
    return False


def interference_evidence_metadata(
    spec: "DesignSpec",
    *,
    validation_warnings: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Additive inference/evidence metadata for interference guardrails.

    Does not rename existing evidence keys; merge into ``inference_metadata``.
    """
    meta: Dict[str, Any] = {
        "interference_assumption": spec.interference.value,
        "spillover_metadata_available": spillover_metadata_available(spec),
        "interference_user_declared": spec.interference != InterferenceAssumption.UNKNOWN,
        "spillover_estimation_available": False,
    }
    if spec.interference == InterferenceAssumption.NO_INTERFERENCE:
        meta["interference_note"] = (
            "User declared no_interference; not empirically verified by this package."
        )
    elif spec.interference == InterferenceAssumption.UNKNOWN:
        meta["interference_note"] = (
            "Interference unknown; causal estimates assume limited spillover unless validated."
        )
    if validation_warnings:
        meta["interference_validation_warnings"] = list(validation_warnings)
    if spec.spillover_notes:
        meta["spillover_notes"] = str(spec.spillover_notes)
    if spec.exposure_column:
        meta["exposure_column"] = str(spec.exposure_column)
    return meta


@dataclass(frozen=True)
class DesignSpec:
    """
    Design-time specification (randomization, constraints, periods).

    Geo experiments often violate strict no-interference (SUTVA). Set
    ``interference`` explicitly; default ``unknown`` records weak causal claims.
    Optional spillover fields are metadata only (no spillover estimation).
    """

    experiment_id: str
    outcome_column: str
    unit_column: str
    time_column: str
    pre_period: TimePeriod
    experiment_period: TimePeriod
    design_method: DesignMethod
    treatment_probability: float = 0.5
    n_test_groups: int = 1
    test_whitelist: tuple = ()
    control_whitelist: tuple = ()
    test_blacklist: tuple = ()
    control_blacklist: tuple = ()
    control_test_blacklist: tuple = ()
    random_state: int = 42
    alpha: float = 0.05
    assumptions: Dict[str, Any] = field(default_factory=dict)
    interference: InterferenceAssumption = InterferenceAssumption.UNKNOWN
    spillover_notes: Optional[str] = None
    exposure_column: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.experiment_id or not str(self.experiment_id).strip():
            raise ValueError("experiment_id is required and must be non-empty.")
        for col in (self.outcome_column, self.unit_column, self.time_column):
            if not col or not str(col).strip():
                raise ValueError(f"Column name is required; got {col!r}.")
        if self.pre_period is None or self.experiment_period is None:
            raise ValueError("pre_period and experiment_period are required.")
        if not (0.0 < self.treatment_probability < 1.0):
            raise ValueError(
                f"treatment_probability must be in (0, 1); got {self.treatment_probability}."
            )
        if self.n_test_groups < 1:
            raise ValueError(f"n_test_groups must be >= 1; got {self.n_test_groups}.")
        if not (0.0 < self.alpha < 1.0):
            raise ValueError(f"alpha must be in (0, 1); got {self.alpha}.")
        overlap = set(self.test_whitelist) & set(self.control_whitelist)
        if overlap:
            raise ValueError(
                f"Units cannot be on both test and control whitelist: {sorted(overlap)}"
            )
        bl_overlap = set(self.test_blacklist) & set(self.control_blacklist)
        if bl_overlap:
            raise ValueError(
                f"Units cannot be on both test and control blacklist: {sorted(bl_overlap)}"
            )

    @property
    def confidence_level(self) -> float:
        return 1.0 - self.alpha

    def content_hash(self) -> str:
        return stable_hash(spec_canonical_payload(self))


@dataclass(frozen=True)
class ExperimentSpec(DesignSpec):
    """
    Full experiment specification including analysis assumptions.

    Extends DesignSpec with analysis-facing fields. Design and analysis code
    should require explicit periods, alpha, and interference where decisions
    depend on them.
    """

    inference_method: Optional[str] = None
    estimator: Optional[str] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.interference == InterferenceAssumption.UNKNOWN:
            # Record warning in assumptions; callers may block on policy.
            object.__setattr__(
                self,
                "assumptions",
                {
                    **dict(self.assumptions),
                    "interference_warning": (
                        "interference is unknown; geo media experiments may violate "
                        "no-interference unless explicitly validated."
                    ),
                },
            )


def spec_canonical_payload(spec: DesignSpec) -> Dict[str, Any]:
    """Canonical spec dict for stable ``spec_hash`` / ``content_hash``."""
    payload = asdict(spec)
    payload["pre_period"] = {
        "start": _serialize_time(spec.pre_period.start),
        "end": _serialize_time(spec.pre_period.end),
    }
    payload["experiment_period"] = {
        "start": _serialize_time(spec.experiment_period.start),
        "end": _serialize_time(spec.experiment_period.end),
    }
    payload["design_method"] = spec.design_method.value
    payload["interference"] = spec.interference.value
    payload["spillover_metadata_available"] = spillover_metadata_available(spec)
    if spec.spillover_notes:
        payload["spillover_notes"] = str(spec.spillover_notes)
    if spec.exposure_column:
        payload["exposure_column"] = str(spec.exposure_column)
    payload["test_whitelist"] = sorted(str(u) for u in spec.test_whitelist)
    payload["control_whitelist"] = sorted(str(u) for u in spec.control_whitelist)
    payload["test_blacklist"] = sorted(str(u) for u in spec.test_blacklist)
    payload["control_blacklist"] = sorted(str(u) for u in spec.control_blacklist)
    payload["control_test_blacklist"] = sorted(str(u) for u in spec.control_test_blacklist)
    return payload


def _serialize_time(t: Any) -> Any:
    if t is None:
        return None
    if hasattr(t, "isoformat"):
        return t.isoformat()
    return t


def class_name_to_design_method(class_name: str) -> DesignMethod:
    """Map design class name (lowercase) to DesignMethod enum."""
    key = class_name.lower().replace(" ", "")
    mapping = {
        "balancedrandomization": DesignMethod.BALANCED_RANDOMIZATION,
        "completerandomization": DesignMethod.COMPLETE_RANDOMIZATION,
        "stratifiedrandomization": DesignMethod.STRATIFIED_RANDOMIZATION,
        "thinningdesign": DesignMethod.THINNING,
        "rerandomization": DesignMethod.RERANDOMIZATION,
        "greedy_match_markets": DesignMethod.GREEDY_MATCH,
        "greedymatchmarkets": DesignMethod.GREEDY_MATCH,
        "quickblock": DesignMethod.QUICKBLOCK,
        "matchedpair": DesignMethod.MATCHED_PAIR,
    }
    for fragment, method in mapping.items():
        if fragment in key:
            return method
    raise ValueError(
        f"Cannot map design class {class_name!r} to DesignMethod; "
        f"known patterns: {list(mapping.keys())}"
    )


def spec_from_geo_design(
    experiment_id: str,
    outcome_column: str,
    unit_column: str,
    time_column: str,
    pre_period: TimePeriod,
    experiment_period: TimePeriod,
    design_method: Union[DesignMethod, str],
    *,
    random_state: int = 42,
    alpha: float = 0.05,
    treatment_probability: float = 0.5,
    n_test_groups: int = 1,
    test_whitelist: Optional[List] = None,
    control_whitelist: Optional[List] = None,
    test_blacklist: Optional[List] = None,
    control_blacklist: Optional[List] = None,
    control_test_blacklist: Optional[List] = None,
    interference: InterferenceAssumption = InterferenceAssumption.UNKNOWN,
    spillover_notes: Optional[str] = None,
    exposure_column: Optional[str] = None,
    **assumptions: Any,
) -> DesignSpec:
    """Build a DesignSpec from geo experiment parameters."""
    if isinstance(design_method, str):
        design_method = class_name_to_design_method(design_method)
    return DesignSpec(
        experiment_id=experiment_id,
        outcome_column=outcome_column,
        unit_column=unit_column,
        time_column=time_column,
        pre_period=pre_period,
        experiment_period=experiment_period,
        design_method=design_method,
        treatment_probability=treatment_probability,
        n_test_groups=n_test_groups,
        test_whitelist=tuple(test_whitelist or ()),
        control_whitelist=tuple(control_whitelist or ()),
        test_blacklist=tuple(test_blacklist or ()),
        control_blacklist=tuple(control_blacklist or ()),
        control_test_blacklist=tuple(control_test_blacklist or ()),
        random_state=random_state,
        alpha=alpha,
        assumptions=dict(assumptions),
        interference=interference,
        spillover_notes=spillover_notes,
        exposure_column=exposure_column,
    )
