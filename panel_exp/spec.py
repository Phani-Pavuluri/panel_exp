"""
Experiment and design specification contracts.

Typed boundaries for geo-panel experiments. Production-facing entry points
should accept these specs rather than inferring critical fields silently.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from panel_exp.evidence_hash import stable_hash
from panel_exp.panel_data import TimePeriod


class ReviewRiskLevel(str, Enum):
    """Reviewer-assessed risk level (metadata only; not estimated)."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class SpilloverDirection(str, Enum):
    """Expected spillover direction (declarative; not estimated)."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    BIDIRECTIONAL = "bidirectional"
    UNKNOWN = "unknown"


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


class TargetEstimand(str, Enum):
    """
    Declared causal quantity for analysis reporting.

    ``UNKNOWN`` is the default; callers must set an explicit estimand for
    decision-grade readouts. Values describe intent, not estimator outputs.
    """

    RELATIVE_ATT_POST = "relative_att_post"
    ABSOLUTE_ATT_POST = "absolute_att_post"
    CUMULATIVE_ATT = "cumulative_att"
    UNIT_LEVEL_ATT = "unit_level_att"
    POOLED_ATT = "pooled_att"
    UNKNOWN = "unknown"


class UncertaintyContract(str, Enum):
    """
    Declared interpretation of interval-like outputs (``y_lower`` / ``y_upper``).

    Distinct from :class:`~panel_exp.inference_result.IntervalType` on a run;
    prespecify the contract before analysis when possible.
    """

    CONFIDENCE_INTERVAL = "confidence_interval"
    CREDIBLE_INTERVAL = "credible_interval"
    CONFORMAL_INTERVAL = "conformal_interval"
    PLACEBO_BAND = "placebo_band"
    NONE = "none"
    UNKNOWN = "unknown"


_TARGET_ESTIMAND_LABELS: Dict[str, str] = {
    TargetEstimand.RELATIVE_ATT_POST.value: "Relative post-period ATT",
    TargetEstimand.ABSOLUTE_ATT_POST.value: "Absolute post-period ATT",
    TargetEstimand.CUMULATIVE_ATT.value: "Cumulative ATT",
    TargetEstimand.UNIT_LEVEL_ATT.value: "Unit-level ATT",
    TargetEstimand.POOLED_ATT.value: "Pooled ATT",
    TargetEstimand.UNKNOWN.value: "Unknown (not declared)",
}

_UNCERTAINTY_CONTRACT_LABELS: Dict[str, str] = {
    UncertaintyContract.CONFIDENCE_INTERVAL.value: "Confidence interval",
    UncertaintyContract.CREDIBLE_INTERVAL.value: "Credible interval",
    UncertaintyContract.CONFORMAL_INTERVAL.value: "Conformal interval",
    UncertaintyContract.PLACEBO_BAND.value: "Placebo band",
    UncertaintyContract.NONE.value: "None (point estimate only)",
    UncertaintyContract.UNKNOWN.value: "Unknown (not declared)",
}


def target_estimand_label(estimand: Union[TargetEstimand, str]) -> str:
    """Human-readable label for a :class:`TargetEstimand` value."""
    key = estimand.value if isinstance(estimand, TargetEstimand) else str(estimand)
    return _TARGET_ESTIMAND_LABELS.get(key, _TARGET_ESTIMAND_LABELS[TargetEstimand.UNKNOWN.value])


def uncertainty_contract_label(contract: Union[UncertaintyContract, str]) -> str:
    """Human-readable label for an :class:`UncertaintyContract` value."""
    key = contract.value if isinstance(contract, UncertaintyContract) else str(contract)
    return _UNCERTAINTY_CONTRACT_LABELS.get(
        key, _UNCERTAINTY_CONTRACT_LABELS[UncertaintyContract.UNKNOWN.value]
    )


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


def _coerce_review_risk(value: Any) -> ReviewRiskLevel:
    if isinstance(value, ReviewRiskLevel):
        return value
    if value is None or str(value).strip() == "":
        return ReviewRiskLevel.UNKNOWN
    try:
        return ReviewRiskLevel(str(value).lower())
    except ValueError:
        return ReviewRiskLevel.UNKNOWN


def _coerce_spillover_direction(value: Any) -> SpilloverDirection:
    if isinstance(value, SpilloverDirection):
        return value
    if value is None or str(value).strip() == "":
        return SpilloverDirection.UNKNOWN
    try:
        return SpilloverDirection(str(value).lower())
    except ValueError:
        return SpilloverDirection.UNKNOWN


def _string_list(value: Any) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        text = value.strip()
        return (text,) if text else ()
    if isinstance(value, (list, tuple)):
        return tuple(str(v).strip() for v in value if v is not None and str(v).strip())
    return ()


@dataclass(frozen=True)
class InterferenceReview:
    """
    Structured interference/spillover review packet (metadata and checklist only).

    Does not estimate spillover effects. All fields are optional at input time;
    defaults record ``unknown`` / empty collections for reviewer completion.
    """

    assumption: InterferenceAssumption = InterferenceAssumption.UNKNOWN
    buffer_geos: Tuple[str, ...] = ()
    adjacent_geos: Tuple[str, ...] = ()
    shared_market_risk: ReviewRiskLevel = ReviewRiskLevel.UNKNOWN
    expected_spillover_direction: SpilloverDirection = SpilloverDirection.UNKNOWN
    contamination_risk: ReviewRiskLevel = ReviewRiskLevel.UNKNOWN
    spillover_notes: str = ""
    exposure_channel_overlap: str = ""
    ad_saturation_risk: ReviewRiskLevel = ReviewRiskLevel.UNKNOWN
    review_warnings: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assumption": self.assumption.value,
            "buffer_geos": list(self.buffer_geos),
            "adjacent_geos": list(self.adjacent_geos),
            "shared_market_risk": self.shared_market_risk.value,
            "expected_spillover_direction": self.expected_spillover_direction.value,
            "contamination_risk": self.contamination_risk.value,
            "spillover_notes": self.spillover_notes,
            "exposure_channel_overlap": self.exposure_channel_overlap,
            "ad_saturation_risk": self.ad_saturation_risk.value,
            "review_warnings": list(self.review_warnings),
        }


def build_interference_review(
    spec: DesignSpec,
    *,
    existing_metadata: Optional[Mapping[str, Any]] = None,
    buffer_geos: Optional[Sequence[str]] = None,
    adjacent_geos: Optional[Sequence[str]] = None,
    shared_market_risk: Optional[Union[ReviewRiskLevel, str]] = None,
    expected_spillover_direction: Optional[Union[SpilloverDirection, str]] = None,
    contamination_risk: Optional[Union[ReviewRiskLevel, str]] = None,
    spillover_notes: Optional[str] = None,
    exposure_channel_overlap: Optional[str] = None,
    ad_saturation_risk: Optional[Union[ReviewRiskLevel, str]] = None,
    review_warnings: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """
    Build an interference review packet from design spec and optional reviewer inputs.

    Preserves explicit values; does not infer geo lists or risk levels aggressively.
    Emits checklist warnings only (non-blocking).
    """
    meta = dict(existing_metadata) if existing_metadata else {}
    assumptions = dict(spec.assumptions)
    nested = assumptions.get("assumptions")
    if isinstance(nested, Mapping):
        assumptions = {**assumptions, **dict(nested)}

    def _pick_geo(key: str, explicit: Optional[Sequence[str]]) -> Tuple[str, ...]:
        if explicit is not None:
            return _string_list(explicit)
        if key in assumptions:
            return _string_list(assumptions[key])
        if key in meta:
            return _string_list(meta[key])
        return ()

    def _pick_str(
        key: str,
        explicit: Optional[str],
        *,
        fallback_keys: Tuple[str, ...] = (),
    ) -> str:
        if explicit is not None and str(explicit).strip():
            return str(explicit).strip()
        for source in (assumptions, meta):
            if key in source and str(source[key]).strip():
                return str(source[key]).strip()
        for fk in fallback_keys:
            if fk in meta and str(meta[fk]).strip():
                return str(meta[fk]).strip()
        if spec.spillover_notes and key == "spillover_notes":
            return str(spec.spillover_notes).strip()
        return ""

    def _pick_risk(
        key: str,
        explicit: Optional[Union[ReviewRiskLevel, str]],
    ) -> ReviewRiskLevel:
        if explicit is not None:
            return _coerce_review_risk(explicit)
        if key in assumptions:
            return _coerce_review_risk(assumptions[key])
        if key in meta:
            return _coerce_review_risk(meta[key])
        return ReviewRiskLevel.UNKNOWN

    def _pick_direction(
        explicit: Optional[Union[SpilloverDirection, str]],
    ) -> SpilloverDirection:
        if explicit is not None:
            return _coerce_spillover_direction(explicit)
        for key in ("expected_spillover_direction", "spillover_direction"):
            if key in assumptions:
                return _coerce_spillover_direction(assumptions[key])
            if key in meta:
                return _coerce_spillover_direction(meta[key])
        return SpilloverDirection.UNKNOWN

    assumption = spec.interference
    buffers = _pick_geo("buffer_geos", buffer_geos)
    adjacent = _pick_geo("adjacent_geos", adjacent_geos)
    notes = _pick_str(
        "spillover_notes",
        spillover_notes,
        fallback_keys=("spillover_notes",),
    )
    overlap = _pick_str("exposure_channel_overlap", exposure_channel_overlap)
    shared_risk = _pick_risk("shared_market_risk", shared_market_risk)
    contam_risk = _pick_risk("contamination_risk", contamination_risk)
    ad_risk = _pick_risk("ad_saturation_risk", ad_saturation_risk)
    direction = _pick_direction(expected_spillover_direction)

    warnings: List[str] = []
    if review_warnings:
        for w in review_warnings:
            text = str(w).strip()
            if text and text not in warnings:
                warnings.append(text)

    if assumption in (
        InterferenceAssumption.NO_INTERFERENCE,
        InterferenceAssumption.PARTIAL_INTERFERENCE,
    ) and not buffers:
        msg = "Interference assumption declared but no buffer geos documented"
        if msg not in warnings:
            warnings.append(msg)

    if assumption == InterferenceAssumption.PARTIAL_INTERFERENCE and not adjacent:
        if not spillover_metadata_available(spec) and not notes:
            msg = "Partial interference declared without adjacent geo metadata"
            if msg not in warnings:
                warnings.append(msg)

    if assumption == InterferenceAssumption.UNKNOWN:
        msg = "Unknown interference assumption limits causal interpretation"
        if msg not in warnings:
            warnings.append(msg)

    if contam_risk == ReviewRiskLevel.HIGH:
        msg = "High contamination risk documented"
        if msg not in warnings:
            warnings.append(msg)

    review = InterferenceReview(
        assumption=assumption,
        buffer_geos=buffers,
        adjacent_geos=adjacent,
        shared_market_risk=shared_risk,
        expected_spillover_direction=direction,
        contamination_risk=contam_risk,
        spillover_notes=notes,
        exposure_channel_overlap=overlap,
        ad_saturation_risk=ad_risk,
        review_warnings=tuple(warnings),
    )
    return review.to_dict()


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
    target_estimand: TargetEstimand = TargetEstimand.UNKNOWN
    uncertainty_contract: UncertaintyContract = UncertaintyContract.UNKNOWN

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
    payload["target_estimand"] = spec.target_estimand.value
    payload["uncertainty_contract"] = spec.uncertainty_contract.value
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
    target_estimand: TargetEstimand = TargetEstimand.UNKNOWN,
    uncertainty_contract: UncertaintyContract = UncertaintyContract.UNKNOWN,
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
        target_estimand=target_estimand,
        uncertainty_contract=uncertainty_contract,
    )
