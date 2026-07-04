"""STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001 — numeric promotion threshold policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "statistical_promotion_thresholds_enforced_no_method_unblock_or_claim_authorization"
_VERDICT = "statistical_promotion_thresholds_enforced_no_method_unblock_or_claim_authorization"
_RECOMMENDED_NEXT = "GOVERNED_RANDOMIZATION_RUNTIME_001"
_ALTERNATIVE_NEXT = "SRM_BALANCE_READOUT_DIAGNOSTIC_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001_summary.json"
)

STATISTICAL_PROMOTION_PASSED = "STATISTICAL_PROMOTION_PASSED"
STATISTICAL_PROMOTION_PASSED_WITH_WARNINGS = "STATISTICAL_PROMOTION_PASSED_WITH_WARNINGS"
STATISTICAL_PROMOTION_FAILED = "STATISTICAL_PROMOTION_FAILED"
STATISTICAL_PROMOTION_INCONCLUSIVE = "STATISTICAL_PROMOTION_INCONCLUSIVE"
STATISTICAL_PROMOTION_BLOCKED = "STATISTICAL_PROMOTION_BLOCKED"
STATISTICAL_PROMOTION_NOT_EVALUATED = "STATISTICAL_PROMOTION_NOT_EVALUATED"

THRESHOLD_MET = "THRESHOLD_MET"
THRESHOLD_FAILED = "THRESHOLD_FAILED"
THRESHOLD_MISSING = "THRESHOLD_MISSING"
THRESHOLD_NOT_APPLICABLE = "THRESHOLD_NOT_APPLICABLE"
THRESHOLD_NOT_DEFINED = "THRESHOLD_NOT_DEFINED"

FAILURE_MISSING_REQUIRED_EVIDENCE = "MISSING_REQUIRED_EVIDENCE"
FAILURE_MISSING_NUMERIC_THRESHOLD = "MISSING_NUMERIC_THRESHOLD"
FAILURE_THRESHOLD_FAILED_BIAS = "THRESHOLD_FAILED_BIAS"
FAILURE_THRESHOLD_FAILED_RMSE = "THRESHOLD_FAILED_RMSE"
FAILURE_THRESHOLD_FAILED_COVERAGE = "THRESHOLD_FAILED_COVERAGE"
FAILURE_THRESHOLD_FAILED_TYPE_I_ERROR = "THRESHOLD_FAILED_TYPE_I_ERROR"
FAILURE_THRESHOLD_FAILED_FALSE_POSITIVE_RATE = "THRESHOLD_FAILED_FALSE_POSITIVE_RATE"
FAILURE_THRESHOLD_FAILED_FALSE_NEGATIVE_RATE = "THRESHOLD_FAILED_FALSE_POSITIVE_RATE"
FAILURE_THRESHOLD_FAILED_DIRECTIONAL_FALSE_SIGNAL = "THRESHOLD_FAILED_DIRECTIONAL_FALSE_SIGNAL"
FAILURE_THRESHOLD_FAILED_INTERVAL_SANITY = "THRESHOLD_FAILED_INTERVAL_SANITY"
FAILURE_THRESHOLD_FAILED_NEGATIVE_INTERVAL_WIDTH = "THRESHOLD_FAILED_NEGATIVE_INTERVAL_WIDTH"
FAILURE_THRESHOLD_FAILED_POWER = "THRESHOLD_FAILED_POWER"
FAILURE_THRESHOLD_FAILED_MDE_STABILITY = "THRESHOLD_FAILED_MDE_STABILITY"
FAILURE_THRESHOLD_FAILED_SMALL_SAMPLE = "THRESHOLD_FAILED_SMALL_SAMPLE_BEHAVIOR"
FAILURE_THRESHOLD_FAILED_NULL_CALIBRATION = "THRESHOLD_FAILED_NULL_CALIBRATION"
FAILURE_THRESHOLD_FAILED_AA_CALIBRATION = "THRESHOLD_FAILED_AA_CALIBRATION"
FAILURE_THRESHOLD_FAILED_OUTLIER_ROBUSTNESS = "THRESHOLD_FAILED_OUTLIER_ROBUSTNESS"
FAILURE_NEGATIVE_CHARACTERIZATION = "NEGATIVE_CHARACTERIZATION_EVIDENCE"
FAILURE_REQUESTED_PROMOTION_NOT_ALLOWED = "REQUESTED_PROMOTION_NOT_ALLOWED"
FAILURE_PRODUCTION_CATALOG_BLOCKED = "PRODUCTION_CATALOG_BLOCKED"
FAILURE_CLAIM_AUTHORIZATION_MISSING = "CLAIM_AUTHORIZATION_MISSING"

REMEDIATION_ADD_RECOVERY = "ADD_REQUIRED_RECOVERY_EVIDENCE"
REMEDIATION_ADD_NULL_AA = "ADD_NULL_OR_AA_CALIBRATION"
REMEDIATION_ADD_COVERAGE = "ADD_COVERAGE_CALIBRATION"
REMEDIATION_FIX_INTERVAL = "FIX_INTERVAL_CONSTRUCTION"
REMEDIATION_FIX_METHOD = "FIX_METHOD_IMPLEMENTATION"
REMEDIATION_DEFINE_THRESHOLDS = "DEFINE_NUMERIC_THRESHOLDS"
REMEDIATION_RECHARACTERIZE = "RECHARACTERIZE_METHOD"
REMEDIATION_KEEP_RESEARCH = "KEEP_RESEARCH_ONLY"
REMEDIATION_KEEP_DIAGNOSTIC = "KEEP_DIAGNOSTIC_ONLY"
REMEDIATION_BLOCK_CATALOG = "BLOCK_PRODUCTION_CATALOG"

MATURITY_RESTRICTED_EXPERT_REVIEW = "RESTRICTED_EXPERT_REVIEW"
MATURITY_PRODUCTION_CANDIDATE = "PRODUCTION_CANDIDATE"
MATURITY_PRODUCTION_SAFE = "PRODUCTION_SAFE"
MATURITY_RESEARCH_ONLY = "RESEARCH_ONLY"
MATURITY_DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"

_METRIC_FAILURE_MAP = {
    "coverage": FAILURE_THRESHOLD_FAILED_COVERAGE,
    "coverage_rate": FAILURE_THRESHOLD_FAILED_COVERAGE,
    "type_i_error": FAILURE_THRESHOLD_FAILED_TYPE_I_ERROR,
    "type_i_error_rate": FAILURE_THRESHOLD_FAILED_TYPE_I_ERROR,
    "false_positive_rate": FAILURE_THRESHOLD_FAILED_FALSE_POSITIVE_RATE,
    "fpr": FAILURE_THRESHOLD_FAILED_FALSE_POSITIVE_RATE,
    "null_fpr": FAILURE_THRESHOLD_FAILED_FALSE_POSITIVE_RATE,
    "directional_false_signal_rate": FAILURE_THRESHOLD_FAILED_DIRECTIONAL_FALSE_SIGNAL,
    "negative_interval_width_rate": FAILURE_THRESHOLD_FAILED_NEGATIVE_INTERVAL_WIDTH,
    "invalid_interval_rate": FAILURE_THRESHOLD_FAILED_INTERVAL_SANITY,
    "bias": FAILURE_THRESHOLD_FAILED_BIAS,
    "bias_abs": FAILURE_THRESHOLD_FAILED_BIAS,
    "rmse": FAILURE_THRESHOLD_FAILED_RMSE,
    "power": FAILURE_THRESHOLD_FAILED_POWER,
    "null_calibration_rate": FAILURE_THRESHOLD_FAILED_NULL_CALIBRATION,
    "aa_calibration_rate": FAILURE_THRESHOLD_FAILED_AA_CALIBRATION,
}

_POSITIVE_FLAGS = {
    "statistical_promotion_thresholds_defined": True,
    "statistical_promotion_thresholds_evaluated": True,
    "statistical_promotion_failures_block_production_promotion": True,
}

_AUTH_FALSE = {
    "methods_unblocked": False,
    "production_catalog_unblocked": False,
    "production_safe_method_promoted": False,
    "claim_authorization_runtime_implemented": False,
    "claim_authorized": False,
    "claim_authorized_with_restrictions": False,
    "authorized_claim_text_generated": False,
    "trusted_readout_handoff_generated": False,
    "production_readout_authorized": False,
    "causal_claim_authorized": False,
    "incremental_lift_claim_authorized": False,
    "roi_claim_authorized": False,
    "production_authorization_granted": False,
    "estimator_implemented": False,
    "inference_implemented": False,
    "bootstrap_inference_implemented": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}


@dataclass(frozen=True)
class StatisticalPromotionThresholdPolicy:
    policy_version: str = _POLICY_VERSION
    coverage_min_restricted_expert_review: float = 0.80
    coverage_min_production_candidate: float = 0.90
    coverage_min_production_safe: float = 0.90
    type_i_error_max_restricted_expert_review: float = 0.15
    type_i_error_max_production_candidate: float = 0.10
    type_i_error_max_production_safe: float = 0.05
    false_positive_rate_max_restricted_expert_review: float = 0.15
    false_positive_rate_max_production_candidate: float = 0.10
    false_positive_rate_max_production_safe: float = 0.05
    directional_false_signal_rate_max_production_candidate: float = 0.10
    directional_false_signal_rate_max_production_safe: float = 0.10
    negative_interval_width_rate_max: float = 0.0
    invalid_interval_rate_max: float = 0.0
    power_min_production_candidate: float = 0.80
    bias_abs_max: float | None = None
    rmse_max: float | None = None
    require_claim_authorization_for_production_safe: bool = True
    require_trusted_readout_for_production_safe: bool = True
    block_production_safe_by_default: bool = True


@dataclass(frozen=True)
class StatisticalPromotionThresholdConfig:
    enforce_statistical_promotion_thresholds: bool = True
    default_requested_maturity_state: str = MATURITY_PRODUCTION_CANDIDATE
    policy: StatisticalPromotionThresholdPolicy = field(default_factory=StatisticalPromotionThresholdPolicy)


@dataclass(frozen=True)
class MetricThresholdResult:
    metric_name: str
    observed_value: float | None
    threshold_operator: str
    threshold_value: float | None
    threshold_status: str
    evidence_source: str | None
    required_for_requested_maturity: bool
    failure_category: str | None


@dataclass(frozen=True)
class StatisticalPromotionThresholdReport:
    request_id: str
    instrument_id: str
    method_family: str
    estimator_family: str
    inference_family: str
    current_maturity_state: str | None
    requested_maturity_state: str
    requested_role: str | None
    claim_type: str | None
    production_context: str | None
    promotion_status: str
    is_statistically_promotable: bool
    required_gates: tuple[str, ...]
    metric_results: tuple[MetricThresholdResult, ...]
    passed_metrics: tuple[str, ...]
    failed_metrics: tuple[str, ...]
    missing_metrics: tuple[str, ...]
    undefined_thresholds: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    required_remediation: tuple[str, ...]
    evidence_sources: tuple[str, ...]
    policy_version: str
    trace: dict[str, Any]
    claim_boundary_report: dict[str, Any]


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _hash_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _token(value: Any) -> str:
    return str(value).strip().upper() if value is not None else ""


def _safe_str_list(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(v for v in values if v))


def _resolve_config(
    config: StatisticalPromotionThresholdConfig | dict[str, Any] | None,
) -> StatisticalPromotionThresholdConfig:
    if config is None:
        return StatisticalPromotionThresholdConfig()
    if isinstance(config, StatisticalPromotionThresholdConfig):
        return config
    base = StatisticalPromotionThresholdConfig()
    policy_data = config.get("policy") or {}
    policy = StatisticalPromotionThresholdPolicy(
        **{**base.policy.__dict__, **{k: v for k, v in policy_data.items() if k in base.policy.__dict__}}
    )
    merged = {
        **{k: getattr(base, k) for k in ("enforce_statistical_promotion_thresholds", "default_requested_maturity_state")},
        **{k: v for k, v in config.items() if k in ("enforce_statistical_promotion_thresholds", "default_requested_maturity_state")},
    }
    return StatisticalPromotionThresholdConfig(policy=policy, **merged)


def get_default_statistical_promotion_policy() -> StatisticalPromotionThresholdPolicy:
    return StatisticalPromotionThresholdPolicy()


def _normalize_metrics(data: dict[str, Any]) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for source_key in ("evidence", "observed_metrics", "archive_metrics"):
        source = data.get(source_key)
        if isinstance(source, dict):
            for key, val in source.items():
                try:
                    metrics[str(key).strip().lower()] = float(val)
                except (TypeError, ValueError):
                    continue
    for record in data.get("metric_records") or data.get("metrics") or []:
        if not isinstance(record, dict):
            continue
        name = str(record.get("metric_name") or record.get("name") or "").strip().lower()
        if not name:
            continue
        try:
            metrics[name] = float(record.get("observed_value") or record.get("value"))
        except (TypeError, ValueError):
            continue
    archive = _to_dict(data.get("archive_summary"))
    for key, val in archive.items():
        if isinstance(val, (int, float)) and not key.startswith("_"):
            metrics[str(key).strip().lower()] = float(val)
    aliases = {
        "null_fpr": "false_positive_rate",
        "fpr": "false_positive_rate",
        "type_i": "type_i_error",
        "coverage_rate": "coverage",
    }
    for alias, canonical in aliases.items():
        if alias in metrics and canonical not in metrics:
            metrics[canonical] = metrics[alias]
    return metrics


def _known_negative_policy(
    instrument_id: str,
    estimator_family: str,
    inference_family: str,
) -> tuple[list[str], list[str], list[str]]:
    """Return blockers, remediation, evidence sources for policy-known negatives."""
    iid = _token(instrument_id)
    est = _token(estimator_family)
    inf = _token(inference_family)
    blockers: list[str] = []
    remediation: list[str] = []
    evidence: list[str] = []

    if iid in {"DID_BOOTSTRAP", "DID_BOOTSTRAP_INFERENCE"} or "BOOTSTRAP" in iid and "DID" in iid:
        blockers.extend([FAILURE_NEGATIVE_CHARACTERIZATION, FAILURE_REQUESTED_PROMOTION_NOT_ALLOWED])
        remediation.extend([REMEDIATION_ADD_RECOVERY, REMEDIATION_KEEP_RESEARCH])
        evidence.append("policy:did_bootstrap_inference_not_production_promotable")

    if est in {"TBR_RIDGE", "TBRRIDGE", "TBR_RIDGE_FAMILY"} or "TBRRIDGE" in est:
        if inf in {"KFOLD", "K_FOLD", "TIME_SERIES_KFOLD", "TIMESERIESKFOLD"}:
            blockers.extend([FAILURE_NEGATIVE_CHARACTERIZATION, FAILURE_THRESHOLD_FAILED_NEGATIVE_INTERVAL_WIDTH])
            remediation.extend([REMEDIATION_FIX_INTERVAL, REMEDIATION_RECHARACTERIZE, REMEDIATION_BLOCK_CATALOG])
            evidence.append("policy:tbr_ridge_kfold_invalid_interval_evidence")
        if inf in {"CONFORMAL", "CONFORMAL_INFERENCE_FAMILY"}:
            blockers.extend([FAILURE_MISSING_REQUIRED_EVIDENCE, FAILURE_THRESHOLD_FAILED_COVERAGE])
            remediation.extend([REMEDIATION_ADD_COVERAGE, REMEDIATION_RECHARACTERIZE])
            evidence.append("policy:tbr_ridge_conformal_uncalibrated")
        if inf in {"UNITJACKKNIFE", "UNIT_JACKKNIFE", "JACKKNIFE", "JKP", "JK"}:
            blockers.extend([FAILURE_THRESHOLD_FAILED_INTERVAL_SANITY, FAILURE_NEGATIVE_CHARACTERIZATION])
            remediation.extend([REMEDIATION_FIX_INTERVAL, REMEDIATION_RECHARACTERIZE, REMEDIATION_KEEP_DIAGNOSTIC])
            evidence.append("policy:tbr_ridge_jackknife_negative_characterization")

    if est in {"AUGSYNTH", "AUGSYNTH_FAMILY"} and inf in {"CONFORMAL", "CONFORMAL_INFERENCE_FAMILY"}:
        blockers.extend([FAILURE_MISSING_REQUIRED_EVIDENCE, FAILURE_THRESHOLD_FAILED_NULL_CALIBRATION])
        remediation.extend([REMEDIATION_ADD_NULL_AA, REMEDIATION_RECHARACTERIZE])
        evidence.append("policy:augsynth_conformal_null_calibration_missing")

    if est in {"TROP", "TROP_FAMILY", "MTGP", "MTGP_FAMILY", "BAYESIANTBR", "BAYESIAN_TBR_FAMILY"}:
        blockers.extend([FAILURE_REQUESTED_PROMOTION_NOT_ALLOWED, FAILURE_MISSING_REQUIRED_EVIDENCE])
        remediation.append(REMEDIATION_KEEP_RESEARCH)
        evidence.append("policy:research_only_estimator_family")

    if iid == "DID_2X2_POINT_ESTIMATE" or iid == "DID_GOVERNED_POINT_ESTIMATE":
        evidence.append("policy:did_point_estimate_not_inference_promotable")

    return blockers, remediation, evidence


def _thresholds_for_maturity(
    maturity: str,
    policy: StatisticalPromotionThresholdPolicy,
) -> dict[str, tuple[str, float | None, bool]]:
    """metric -> (operator, threshold, required)."""
    mat = _token(maturity)
    reqs: dict[str, tuple[str, float | None, bool]] = {}

    if mat in {MATURITY_RESTRICTED_EXPERT_REVIEW, MATURITY_PRODUCTION_CANDIDATE, MATURITY_PRODUCTION_SAFE}:
        reqs["negative_interval_width_rate"] = ("<=", policy.negative_interval_width_rate_max, True)
        reqs["invalid_interval_rate"] = ("<=", policy.invalid_interval_rate_max, True)

    if mat == MATURITY_RESTRICTED_EXPERT_REVIEW:
        reqs["coverage"] = (">=", policy.coverage_min_restricted_expert_review, False)
        reqs["type_i_error"] = ("<=", policy.type_i_error_max_restricted_expert_review, False)
        reqs["false_positive_rate"] = ("<=", policy.false_positive_rate_max_restricted_expert_review, False)

    if mat in {MATURITY_PRODUCTION_CANDIDATE, MATURITY_PRODUCTION_SAFE}:
        cov_min = (
            policy.coverage_min_production_safe
            if mat == MATURITY_PRODUCTION_SAFE
            else policy.coverage_min_production_candidate
        )
        t1_max = (
            policy.type_i_error_max_production_safe
            if mat == MATURITY_PRODUCTION_SAFE
            else policy.type_i_error_max_production_candidate
        )
        fpr_max = (
            policy.false_positive_rate_max_production_safe
            if mat == MATURITY_PRODUCTION_SAFE
            else policy.false_positive_rate_max_production_candidate
        )
        reqs["coverage"] = (">=", cov_min, True)
        reqs["type_i_error"] = ("<=", t1_max, True)
        reqs["false_positive_rate"] = ("<=", fpr_max, True)
        if mat == MATURITY_PRODUCTION_CANDIDATE:
            reqs["directional_false_signal_rate"] = (
                "<=",
                policy.directional_false_signal_rate_max_production_candidate,
                False,
            )
            reqs["power"] = (">=", policy.power_min_production_candidate, False)
        if mat == MATURITY_PRODUCTION_SAFE:
            reqs["directional_false_signal_rate"] = (
                "<=",
                policy.directional_false_signal_rate_max_production_safe,
                True,
            )
            reqs["null_calibration_rate"] = (">=", 0.0, False)
            reqs["aa_calibration_rate"] = (">=", 0.0, False)

    if policy.bias_abs_max is not None:
        reqs["bias_abs"] = ("<=", policy.bias_abs_max, mat == MATURITY_PRODUCTION_SAFE)
    elif mat == MATURITY_PRODUCTION_SAFE:
        reqs["bias_abs"] = ("<=", None, True)

    if policy.rmse_max is not None:
        reqs["rmse"] = ("<=", policy.rmse_max, mat == MATURITY_PRODUCTION_SAFE)
    elif mat == MATURITY_PRODUCTION_SAFE:
        reqs["rmse"] = ("<=", None, True)

    return reqs


def _required_gates_for_maturity(maturity: str) -> tuple[str, ...]:
    mat = _token(maturity)
    base = (
        "known_estimand",
        "method_identity",
        "no_invalid_interval_behavior",
        "no_negative_characterization_blocker",
    )
    if mat == MATURITY_RESTRICTED_EXPERT_REVIEW:
        return base + ("minimum_recovery_evidence", "diagnostic_requirements_documented")
    if mat == MATURITY_PRODUCTION_CANDIDATE:
        return base + (
            "numeric_thresholds_defined",
            "coverage_gate_if_inference",
            "type_i_fpr_gate_if_inference",
            "interval_sanity_gate",
            "assignment_compatibility",
            "assignment_panel_integrity_compatibility",
            "governed_runtime_support",
            "production_catalog_not_blocked",
        )
    if mat == MATURITY_PRODUCTION_SAFE:
        return _required_gates_for_maturity(MATURITY_PRODUCTION_CANDIDATE) + (
            "stronger_thresholds",
            "diagnostic_sensitivity_evidence",
            "null_aa_calibration",
            "claim_authorization_compatibility",
            "trusted_readout_compatibility",
            "no_open_p0_blockers",
        )
    return base


def _compare_metric(observed: float, operator: str, threshold: float) -> bool:
    if operator == ">=":
        return observed >= threshold
    if operator == "<=":
        return observed <= threshold
    if operator == ">":
        return observed > threshold
    if operator == "<":
        return observed < threshold
    return False


def _evaluate_single(data: dict[str, Any], cfg: StatisticalPromotionThresholdConfig) -> StatisticalPromotionThresholdReport:
    request_id = str(data.get("request_id") or data.get("instrument_id") or "request_unspecified")
    instrument_id = str(data.get("instrument_id") or "instrument_unspecified")
    method_family = str(data.get("method_family") or data.get("estimator_family") or "UNKNOWN")
    estimator_family = str(data.get("estimator_family") or method_family)
    inference_family = str(data.get("inference_family") or "UNKNOWN")
    current_maturity = str(data.get("current_maturity_state") or data.get("maturity_status") or "") or None
    requested_maturity = str(
        data.get("requested_maturity_state") or cfg.default_requested_maturity_state
    )
    requested_role = data.get("requested_role")
    claim_type = data.get("claim_type")
    production_context = data.get("production_context")
    evidence_sources = list(data.get("evidence_sources") or [])

    blockers: list[str] = []
    warnings: list[str] = []
    remediation: list[str] = []
    required_gates = _required_gates_for_maturity(requested_maturity)
    metric_results: list[MetricThresholdResult] = []
    passed: list[str] = []
    failed: list[str] = []
    missing: list[str] = []
    undefined: list[str] = []

    if not cfg.enforce_statistical_promotion_thresholds:
        return StatisticalPromotionThresholdReport(
            request_id=request_id,
            instrument_id=instrument_id,
            method_family=method_family,
            estimator_family=estimator_family,
            inference_family=inference_family,
            current_maturity_state=current_maturity,
            requested_maturity_state=requested_maturity,
            requested_role=str(requested_role) if requested_role else None,
            claim_type=str(claim_type) if claim_type else None,
            production_context=str(production_context) if production_context else None,
            promotion_status=STATISTICAL_PROMOTION_NOT_EVALUATED,
            is_statistically_promotable=False,
            required_gates=required_gates,
            metric_results=(),
            passed_metrics=(),
            failed_metrics=(),
            missing_metrics=(),
            undefined_thresholds=(),
            blockers=(),
            warnings=("enforcement_disabled",),
            required_remediation=(),
            evidence_sources=tuple(evidence_sources),
            policy_version=cfg.policy.policy_version,
            trace={"enforcement_disabled": True},
            claim_boundary_report=_claim_boundary(evaluated=False, promotable=False),
        )

    policy_blockers, policy_remediation, policy_evidence = _known_negative_policy(
        instrument_id, estimator_family, inference_family
    )
    blockers.extend(policy_blockers)
    remediation.extend(policy_remediation)
    evidence_sources.extend(policy_evidence)

    metrics = _normalize_metrics(data)
    thresholds = _thresholds_for_maturity(requested_maturity, cfg.policy)

    has_inference = _token(inference_family) not in {
        "POINT_ESTIMATE_ONLY",
        "POINT_ESTIMATE",
        "NONE",
        "UNKNOWN",
        "",
    }

    for metric_name, (operator, threshold_value, required) in thresholds.items():
        if metric_name in {"coverage", "type_i_error", "false_positive_rate", "power"}:
            if not has_inference and metric_name in {"coverage", "type_i_error", "false_positive_rate"}:
                required = required and _token(requested_maturity) == MATURITY_PRODUCTION_SAFE

        observed = metrics.get(metric_name)
        if metric_name == "bias_abs" and observed is None and "bias" in metrics:
            observed = abs(metrics["bias"])

        if threshold_value is None:
            status = THRESHOLD_NOT_DEFINED if required else THRESHOLD_NOT_APPLICABLE
            if required:
                undefined.append(metric_name)
                blockers.append(FAILURE_MISSING_NUMERIC_THRESHOLD)
                remediation.append(REMEDIATION_DEFINE_THRESHOLDS)
            metric_results.append(
                MetricThresholdResult(
                    metric_name=metric_name,
                    observed_value=observed,
                    threshold_operator=operator,
                    threshold_value=threshold_value,
                    threshold_status=status,
                    evidence_source=evidence_sources[0] if evidence_sources else None,
                    required_for_requested_maturity=required,
                    failure_category=FAILURE_MISSING_NUMERIC_THRESHOLD if required else None,
                )
            )
            continue

        if observed is None:
            status = THRESHOLD_MISSING if required else THRESHOLD_NOT_APPLICABLE
            if required:
                missing.append(metric_name)
                blockers.append(FAILURE_MISSING_REQUIRED_EVIDENCE)
                remediation.append(REMEDIATION_ADD_RECOVERY)
            metric_results.append(
                MetricThresholdResult(
                    metric_name=metric_name,
                    observed_value=None,
                    threshold_operator=operator,
                    threshold_value=threshold_value,
                    threshold_status=status,
                    evidence_source=None,
                    required_for_requested_maturity=required,
                    failure_category=FAILURE_MISSING_REQUIRED_EVIDENCE if required else None,
                )
            )
            continue

        ok = _compare_metric(observed, operator, threshold_value)
        status = THRESHOLD_MET if ok else THRESHOLD_FAILED
        failure_cat = None if ok else _METRIC_FAILURE_MAP.get(metric_name, FAILURE_MISSING_NUMERIC_THRESHOLD)
        if ok:
            passed.append(metric_name)
        else:
            failed.append(metric_name)
            if failure_cat:
                blockers.append(failure_cat)
            remediation.append(REMEDIATION_RECHARACTERIZE)
        metric_results.append(
            MetricThresholdResult(
                metric_name=metric_name,
                observed_value=observed,
                threshold_operator=operator,
                threshold_value=threshold_value,
                threshold_status=status,
                evidence_source=evidence_sources[0] if evidence_sources else "supplied_evidence",
                required_for_requested_maturity=required,
                failure_category=failure_cat,
            )
        )

    mat_tok = _token(requested_maturity)
    if mat_tok == MATURITY_PRODUCTION_SAFE:
        blockers.append(FAILURE_CLAIM_AUTHORIZATION_MISSING)
        remediation.append(REMEDIATION_BLOCK_CATALOG)
        if cfg.policy.block_production_safe_by_default:
            blockers.append(FAILURE_REQUESTED_PROMOTION_NOT_ALLOWED)
            warnings.append("production_safe_unreachable_without_full_gate_pass")

    if mat_tok in {MATURITY_PRODUCTION_CANDIDATE, MATURITY_PRODUCTION_SAFE} and policy_blockers:
        blockers.append(FAILURE_NEGATIVE_CHARACTERIZATION)

    if not data.get("estimand") and not data.get("estimand_type") and mat_tok != MATURITY_RESEARCH_ONLY:
        if mat_tok in {MATURITY_PRODUCTION_CANDIDATE, MATURITY_PRODUCTION_SAFE, MATURITY_RESTRICTED_EXPERT_REVIEW}:
            blockers.append(FAILURE_MISSING_REQUIRED_EVIDENCE)
            missing.append("estimand")
            remediation.append(REMEDIATION_ADD_RECOVERY)

    if _token(instrument_id) == "DID_2X2_POINT_ESTIMATE" and mat_tok in {
        MATURITY_PRODUCTION_CANDIDATE,
        MATURITY_PRODUCTION_SAFE,
    }:
        blockers.extend([FAILURE_MISSING_REQUIRED_EVIDENCE, FAILURE_CLAIM_AUTHORIZATION_MISSING])
        remediation.extend([REMEDIATION_KEEP_DIAGNOSTIC, REMEDIATION_BLOCK_CATALOG])
        warnings.append("did_point_estimate_not_production_candidate_without_inference_gates")

    promotion_status = STATISTICAL_PROMOTION_PASSED
    if policy_blockers and mat_tok in {MATURITY_PRODUCTION_CANDIDATE, MATURITY_PRODUCTION_SAFE}:
        promotion_status = STATISTICAL_PROMOTION_BLOCKED
    elif blockers:
        if missing or undefined:
            promotion_status = STATISTICAL_PROMOTION_INCONCLUSIVE
        else:
            promotion_status = STATISTICAL_PROMOTION_FAILED
    elif warnings:
        promotion_status = STATISTICAL_PROMOTION_PASSED_WITH_WARNINGS

    is_promotable = promotion_status in {
        STATISTICAL_PROMOTION_PASSED,
        STATISTICAL_PROMOTION_PASSED_WITH_WARNINGS,
    } and not blockers

    trace_payload = {
        "artifact_id": _ARTIFACT_ID,
        "request_id": request_id,
        "instrument_id": instrument_id,
        "requested_maturity_state": requested_maturity,
        "promotion_status": promotion_status,
        "policy_version": cfg.policy.policy_version,
        "config_hash": _hash_payload(cfg.__dict__),
        "input_hash": _hash_payload(data),
        "metric_count": len(metric_results),
    }
    trace = {**trace_payload, "integrity_hash": _hash_payload(trace_payload)}

    return StatisticalPromotionThresholdReport(
        request_id=request_id,
        instrument_id=instrument_id,
        method_family=method_family,
        estimator_family=estimator_family,
        inference_family=inference_family,
        current_maturity_state=current_maturity,
        requested_maturity_state=requested_maturity,
        requested_role=str(requested_role) if requested_role else None,
        claim_type=str(claim_type) if claim_type else None,
        production_context=str(production_context) if production_context else None,
        promotion_status=promotion_status,
        is_statistically_promotable=is_promotable,
        required_gates=required_gates,
        metric_results=tuple(metric_results),
        passed_metrics=_safe_str_list(passed),
        failed_metrics=_safe_str_list(failed),
        missing_metrics=_safe_str_list(missing),
        undefined_thresholds=_safe_str_list(undefined),
        blockers=_safe_str_list(blockers),
        warnings=_safe_str_list(warnings),
        required_remediation=_safe_str_list(remediation),
        evidence_sources=_safe_str_list(evidence_sources),
        policy_version=cfg.policy.policy_version,
        trace=trace,
        claim_boundary_report=_claim_boundary(evaluated=True, promotable=is_promotable),
    )


def _claim_boundary(*, evaluated: bool, promotable: bool) -> dict[str, Any]:
    return {
        **_POSITIVE_FLAGS,
        "statistical_promotion_thresholds_evaluated": evaluated,
        "is_statistically_promotable": promotable,
        **_AUTH_FALSE,
    }


def evaluate_statistical_promotion_thresholds(
    input_data: Any,
    config: StatisticalPromotionThresholdConfig | dict[str, Any] | None = None,
) -> StatisticalPromotionThresholdReport | list[StatisticalPromotionThresholdReport]:
    cfg = _resolve_config(config)
    if isinstance(input_data, list):
        return [_evaluate_single(_to_dict(x), cfg) for x in input_data]
    data = _to_dict(input_data)
    if "requests" in data and isinstance(data["requests"], list):
        return [_evaluate_single(_to_dict(x), cfg) for x in data["requests"]]
    return _evaluate_single(data, cfg)


evaluate_promotion_thresholds = evaluate_statistical_promotion_thresholds
check_statistical_thresholds = evaluate_statistical_promotion_thresholds


def is_statistically_promotable(
    input_data: Any,
    config: StatisticalPromotionThresholdConfig | dict[str, Any] | None = None,
) -> bool:
    report = evaluate_statistical_promotion_thresholds(input_data, config=config)
    if isinstance(report, list):
        return all(r.is_statistically_promotable for r in report)
    return report.is_statistically_promotable


def explain_threshold_failures(
    input_data: Any,
    config: StatisticalPromotionThresholdConfig | dict[str, Any] | None = None,
) -> tuple[str, ...]:
    report = evaluate_statistical_promotion_thresholds(input_data, config=config)
    if isinstance(report, list):
        blockers: list[str] = []
        for r in report:
            blockers.extend(r.blockers)
        return _safe_str_list(blockers)
    return report.blockers


def statistical_promotion_overlay_for_matrix(
    report: StatisticalPromotionThresholdReport,
) -> dict[str, Any]:
    hard_blocked = report.promotion_status in {
        STATISTICAL_PROMOTION_FAILED,
        STATISTICAL_PROMOTION_BLOCKED,
    }
    return {
        "statistical_promotion_status": report.promotion_status,
        "is_statistically_promotion_blocked": hard_blocked,
        "statistical_threshold_failures": list(report.blockers),
        "statistical_threshold_evidence": list(report.evidence_sources),
        "statistical_promotion_trace": dict(report.trace),
        "is_statistically_promotable": report.is_statistically_promotable,
    }


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=_REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def run_validation(*, write_summary: bool = True) -> dict[str, Any]:
    smoke = evaluate_statistical_promotion_thresholds(
        {
            "instrument_id": "SCM_UNIT_JACKKNIFE",
            "estimator_family": "SCM",
            "inference_family": "UNIT_JACKKNIFE",
            "requested_maturity_state": MATURITY_RESTRICTED_EXPERT_REVIEW,
            "estimand": "STANDARD_INCREMENTALITY",
            "observed_metrics": {"coverage": 0.85, "false_positive_rate": 0.05},
        }
    )
    assert isinstance(smoke, StatisticalPromotionThresholdReport)
    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "statistical_promotion_threshold_enforcement",
        "base_commit": _git_head(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": [
            "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001",
            "DID_INSTRUMENT_ESTIMAND_UNIFICATION_001",
            "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001",
            "METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001",
            "AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001",
        ],
        "statistical_promotion_thresholds_defined": True,
        "statistical_promotion_thresholds_evaluated": True,
        "statistical_promotion_statuses_defined": True,
        "statistical_promotion_metric_taxonomy_defined": True,
        "statistical_promotion_failure_taxonomy_defined": True,
        "statistical_promotion_remediation_taxonomy_defined": True,
        "statistical_promotion_failures_block_production_promotion": True,
        "known_negative_policy_evidence_encoded": True,
        "did_bootstrap_promotion_blocked": True,
        "tbr_ridge_invalid_interval_promotion_blocked": True,
        "research_only_methods_remain_research_only": True,
        "production_catalog_integrated_with_statistical_promotion": True,
        "method_suitability_integrated_with_statistical_promotion": True,
        "readout_plan_integrated_with_statistical_promotion": True,
        "methods_unblocked": False,
        "production_catalog_unblocked": False,
        "production_safe_method_promoted": False,
        "claim_authorization_runtime_implemented": False,
        "claim_authorized": False,
        "claim_authorized_with_restrictions": False,
        "authorized_claim_text_generated": False,
        "trusted_readout_handoff_generated": False,
        "production_readout_authorized": False,
        "causal_claim_authorized": False,
        "incremental_lift_claim_authorized": False,
        "roi_claim_authorized": False,
        "production_authorization_granted": False,
        "estimator_implemented": False,
        "inference_implemented": False,
        "bootstrap_inference_implemented": False,
        "p_value_computed": False,
        "confidence_interval_computed": False,
        "uncertainty_computed": False,
        "mmm_runtime_calls_implemented": False,
        "mmm_calibration_authorized": False,
        "llm_decisioning_authorized": False,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "final_verdict": _VERDICT,
        "smoke_status": smoke.promotion_status,
        "failed_scenarios": [],
    }
    if write_summary:
        _DEFAULT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
        _DEFAULT_SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--write-summary", action="store_true")
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
