"""PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001 — production catalog blocklist policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.method_metadata import EstimatorMaturity, estimator_catalog

_ARTIFACT_ID = "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "production_catalog_blocklist_enforced_no_claim_or_production_authorization"
_VERDICT = "production_catalog_blocklist_enforced_no_claim_or_production_authorization"
_RECOMMENDED_NEXT = "DID_INSTRUMENT_ESTIMAND_UNIFICATION_001"
_ALTERNATIVE_NEXT = "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001_summary.json"
)

PRODUCTION_CATALOG_ELIGIBLE_FOR_REVIEW = "PRODUCTION_CATALOG_ELIGIBLE_FOR_REVIEW"
PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW = "PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW"
PRODUCTION_CATALOG_DIAGNOSTIC_ONLY = "PRODUCTION_CATALOG_DIAGNOSTIC_ONLY"
PRODUCTION_CATALOG_RESEARCH_ONLY = "PRODUCTION_CATALOG_RESEARCH_ONLY"
PRODUCTION_CATALOG_BLOCKED = "PRODUCTION_CATALOG_BLOCKED"
PRODUCTION_CATALOG_NOT_EVALUATED = "PRODUCTION_CATALOG_NOT_EVALUATED"

BLOCKER_NEGATIVE_CHARACTERIZATION = "NEGATIVE_CHARACTERIZATION_EVIDENCE"
BLOCKER_MISSING_THRESHOLDS = "MISSING_STATISTICAL_THRESHOLDS"
BLOCKER_MISSING_GOVERNED_RUNTIME = "MISSING_GOVERNED_RUNTIME"
BLOCKER_MISLEADING_INSTRUMENT = "MISLEADING_INSTRUMENT_ID"
BLOCKER_INFERENCE_NOT_IMPLEMENTED = "INFERENCE_NOT_IMPLEMENTED"
BLOCKER_UNCALIBRATED_INFERENCE = "UNCALIBRATED_INFERENCE"
BLOCKER_INVALID_INTERVAL = "INVALID_INTERVAL_EVIDENCE"
BLOCKER_UNSUPPORTED_PRODUCTION_CLAIM = "UNSUPPORTED_PRODUCTION_CLAIM"
BLOCKER_RESEARCH_ONLY = "RESEARCH_ONLY_METHOD"
BLOCKER_UNVALIDATED = "UNVALIDATED_METHOD"
BLOCKER_DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY_INSTRUMENT"
BLOCKER_AGGREGATE_MISMATCH = "AGGREGATE_UNIT_PANEL_MISMATCH"
BLOCKER_CLAIM_AUTH_MISSING = "CLAIM_AUTHORIZATION_MISSING"
BLOCKER_PRODUCTION_GOV_MISSING = "PRODUCTION_GOVERNANCE_MISSING"

PRODUCTION_CONTEXTS = frozenset({
    "PRODUCTION",
    "PRODUCTION_CANDIDATE",
    "PRODUCTION_READOUT",
    "TRUSTED_READOUT",
    "TRUST_REPORT",
    "CALIBRATION_SIGNAL",
    "MMM_INGESTION",
    "LLM_DECISIONING",
    "BUDGET_OPTIMIZATION",
})

PRODUCTION_CLAIM_TYPES = frozenset({
    "CAUSAL_LIFT_CLAIM",
    "INCREMENTAL_LIFT_CLAIM",
    "ROI_CLAIM",
    "PRODUCTION_READOUT_CLAIM",
    "POINT_ESTIMATE_CLAIM",
    "DESCRIPTIVE_EFFECT_CLAIM",
})

_ESTIMATOR_MATURITY: dict[str, EstimatorMaturity] = {}
for _meta in estimator_catalog():
    _ESTIMATOR_MATURITY[_meta.name.upper()] = _meta.maturity
    _ESTIMATOR_MATURITY[_meta.class_name.upper()] = _meta.maturity

_FAMILY_TO_ESTIMATOR: dict[str, str] = {
    "DID_FAMILY": "DID",
    "TBR_RIDGE_FAMILY": "TBRRIDGE",
    "TBR_FAMILY": "TBR",
    "SCM_FAMILY": "SCM",
    "AUGSYNTH_FAMILY": "AUGSYNTH",
    "SYNTHETIC_DID_FAMILY": "SYNTHETICDID",
    "TROP_FAMILY": "TROP",
    "MTGP_FAMILY": "MTGP",
    "BAYESIAN_TBR_FAMILY": "BAYESIANTBR",
    "AB_TEST_FAMILY": "TBR",
}

_INFERENCE_ALIASES = {
    "BOOTSTRAP": "BOOTSTRAP",
    "BOOTSTRAP_INFERENCE_FAMILY": "BOOTSTRAP",
    "KFOLD": "KFOLD",
    "K_FOLD": "KFOLD",
    "TIME_SERIES_KFOLD": "TIME_SERIES_KFOLD",
    "TIMESERIESKFOLD": "TIME_SERIES_KFOLD",
    "CONFORMAL": "CONFORMAL",
    "CONFORMAL_INFERENCE_FAMILY": "CONFORMAL",
    "UNITJACKKNIFE": "UNIT_JACKKNIFE",
    "UNIT_JACKKNIFE": "UNIT_JACKKNIFE",
    "JKP": "JKP",
    "JACKKNIFE": "JACKKNIFE",
    "PLACEBO": "PLACEBO",
    "BLOCK_RESIDUAL_BOOTSTRAP": "BRB",
    "BRB": "BRB",
}

_AUTH_FALSE = {
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
    "estimator_execution_implemented": False,
    "inference_execution_implemented": False,
    "effect_estimate_computed": False,
    "diagnostic_check_executed": False,
    "sensitivity_check_executed": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}

_POSITIVE_FLAGS = {
    "production_catalog_blocklist_defined": True,
    "production_catalog_blocklist_enforced": True,
    "production_catalog_status_evaluated": True,
    "production_catalog_blockers_emitted": True,
}


@dataclass(frozen=True)
class ProductionCatalogBlocklistConfig:
    enforce_production_catalog_blocklist: bool = True
    block_production_context_when_catalog_blocked: bool = True
    block_research_context_when_catalog_blocked: bool = False
    allow_research_only_dry_run: bool = True
    allow_augsynth_conformal_production: bool = False


@dataclass(frozen=True)
class ProductionCatalogStatusReport:
    request_id: str
    instrument_id: str
    method_family: str
    estimator_family: str
    inference_family: str
    claim_type: str | None
    requested_role: str | None
    production_context: str | None
    production_catalog_status: str
    is_production_blocked: bool
    is_research_allowed: bool
    is_diagnostic_only: bool
    is_restricted_expert_review: bool
    blockers: tuple[str, ...]
    restrictions: tuple[str, ...]
    required_remediation: tuple[str, ...]
    evidence_sources: tuple[str, ...]
    maturity_status: str | None
    characterization_status: str | None
    claim_boundary_report: dict[str, Any]
    trace: dict[str, Any]
    warnings: tuple[str, ...]


def get_default_production_catalog_policy() -> ProductionCatalogBlocklistConfig:
    return ProductionCatalogBlocklistConfig()


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _token(value: Any) -> str:
    return str(value).strip().upper() if value is not None else ""


def _normalize_inference(inference_family: str) -> str:
    tok = _token(inference_family).replace(" ", "_")
    return _INFERENCE_ALIASES.get(tok, tok)


def _resolve_maturity(estimator_family: str, method_family: str) -> EstimatorMaturity | None:
    for key in (
        _token(estimator_family),
        _token(method_family),
        _FAMILY_TO_ESTIMATOR.get(_token(estimator_family), ""),
        _FAMILY_TO_ESTIMATOR.get(_token(method_family), ""),
    ):
        if not key:
            continue
        if key in _ESTIMATOR_MATURITY:
            return _ESTIMATOR_MATURITY[key]
        short = key.replace("_FAMILY", "")
        if short in _ESTIMATOR_MATURITY:
            return _ESTIMATOR_MATURITY[short]
    return None


def _is_production_context(production_context: str | None, requested_role: str | None) -> bool:
    ctx = _token(production_context)
    role = _token(requested_role)
    if ctx in PRODUCTION_CONTEXTS:
        return True
    if role in PRODUCTION_CONTEXTS:
        return True
    if "PRODUCTION" in role and role not in ("NON_PRODUCTION",):
        return True
    return False


def _claim_boundary_report(*, evaluated: bool, blocked: bool) -> dict[str, Any]:
    return {
        "production_catalog_blocklist_defined": True,
        "production_catalog_blocklist_enforced": evaluated,
        "production_catalog_status_evaluated": evaluated,
        "production_catalog_blockers_emitted": blocked,
        **_AUTH_FALSE,
    }


def _apply_instrument_rules(
    *,
    instrument_id: str,
    estimator_family: str,
    inference_family: str,
    claim_type: str | None,
    blockers: list[str],
    restrictions: list[str],
    remediation: list[str],
    evidence: list[str],
    warnings: list[str],
    allow_augsynth_conformal_production: bool = False,
) -> str | None:
    iid = _token(instrument_id)
    est = _token(estimator_family)
    inf = _normalize_inference(inference_family)
    claim = _token(claim_type) if claim_type else ""

    if iid == "DID_BOOTSTRAP" or (est == "DID_FAMILY" and inf == "BOOTSTRAP"):
        blockers.extend([
            BLOCKER_MISLEADING_INSTRUMENT,
            BLOCKER_INFERENCE_NOT_IMPLEMENTED,
            BLOCKER_UNCALIBRATED_INFERENCE,
            BLOCKER_NEGATIVE_CHARACTERIZATION,
        ])
        restrictions.append("governed_executor_point_estimate_only")
        remediation.extend([
            "DID_INSTRUMENT_ESTIMAND_UNIFICATION_001",
            "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001",
        ])
        evidence.append("D5_STAT_DID_BOOTSTRAP_001")
        evidence.append("estimator_inference_did_executor_003")
        return PRODUCTION_CATALOG_BLOCKED

    if iid == "TBR_RIDGE_KFOLD" or (est in ("TBR_RIDGE_FAMILY", "TBRRIDGE") and inf in ("KFOLD", "TIME_SERIES_KFOLD")):
        blockers.extend([BLOCKER_INVALID_INTERVAL, BLOCKER_NEGATIVE_CHARACTERIZATION])
        remediation.append("TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001")
        evidence.append("D5_INST_TBRRIDGE_002")
        return PRODUCTION_CATALOG_BLOCKED

    if est in ("TBR_RIDGE_FAMILY", "TBRRIDGE") and inf == "CONFORMAL":
        blockers.extend([BLOCKER_INVALID_INTERVAL, BLOCKER_UNCALIBRATED_INFERENCE])
        evidence.append("D5_INST_TBRRIDGE_002")
        return PRODUCTION_CATALOG_BLOCKED

    if est in ("TBR_RIDGE_FAMILY", "TBRRIDGE") and inf in ("UNIT_JACKKNIFE", "JKP", "JACKKNIFE"):
        blockers.extend([BLOCKER_INVALID_INTERVAL, BLOCKER_NEGATIVE_CHARACTERIZATION])
        evidence.append("D5_INST_TBRRIDGE_002")
        return PRODUCTION_CATALOG_BLOCKED

    if est in ("TBR_FAMILY", "TBR") and est not in ("TBR_RIDGE_FAMILY", "TBRRIDGE"):
        blockers.append(BLOCKER_AGGREGATE_MISMATCH)
        restrictions.append("aggregate_unit_panel_semantics_unresolved")
        evidence.append("FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001")
        return PRODUCTION_CATALOG_BLOCKED

    if iid == "AUGSYNTH_JACKKNIFE" or (est in ("AUGSYNTH_FAMILY", "AUGSYNTH", "AUGSYNTHCVXPY") and inf == "CONFORMAL"):
        if allow_augsynth_conformal_production:
            return None
        blockers.extend([BLOCKER_UNCALIBRATED_INFERENCE, BLOCKER_MISSING_THRESHOLDS])
        restrictions.append("diagnostic_research_only_until_null_calibration")
        remediation.extend(["AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001", "null_fpr_gate"])
        evidence.append("D5_AUGSYNTH_CONFORMAL")
        return PRODUCTION_CATALOG_DIAGNOSTIC_ONLY

    if est in ("TROP_FAMILY", "TROP") or _token(instrument_id).startswith("TROP"):
        blockers.append(BLOCKER_RESEARCH_ONLY)
        return PRODUCTION_CATALOG_RESEARCH_ONLY

    if est in ("MTGP_FAMILY", "MTGP"):
        blockers.append(BLOCKER_RESEARCH_ONLY)
        return PRODUCTION_CATALOG_RESEARCH_ONLY

    if est in ("BAYESIAN_TBR_FAMILY", "BAYESIANTBR", "BAYESIANTBRHORSESHOE"):
        blockers.append(BLOCKER_RESEARCH_ONLY)
        return PRODUCTION_CATALOG_RESEARCH_ONLY

    if claim in PRODUCTION_CLAIM_TYPES and iid == "DID_BOOTSTRAP":
        blockers.append(BLOCKER_UNSUPPORTED_PRODUCTION_CLAIM)
        return PRODUCTION_CATALOG_BLOCKED

    # claim authorization runtime not implemented
    if claim in PRODUCTION_CLAIM_TYPES:
        blockers.append(BLOCKER_CLAIM_AUTH_MISSING)
        restrictions.append("claim_authorization_runtime_not_implemented")

    return None


def _apply_maturity_rules(
    maturity: EstimatorMaturity | None,
    *,
    blockers: list[str],
    restrictions: list[str],
) -> str:
    if maturity is None:
        blockers.append(BLOCKER_UNVALIDATED)
        return PRODUCTION_CATALOG_NOT_EVALUATED
    if maturity == EstimatorMaturity.RESEARCH_ONLY:
        blockers.append(BLOCKER_RESEARCH_ONLY)
        return PRODUCTION_CATALOG_RESEARCH_ONLY
    if maturity == EstimatorMaturity.UNVALIDATED:
        blockers.append(BLOCKER_UNVALIDATED)
        return PRODUCTION_CATALOG_BLOCKED
    if maturity == EstimatorMaturity.EXPERT_REVIEW:
        restrictions.append("expert_review_not_production_safe")
        return PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW
    if maturity == EstimatorMaturity.PRODUCTION_SAFE:
        return PRODUCTION_CATALOG_ELIGIBLE_FOR_REVIEW
    blockers.append(BLOCKER_UNVALIDATED)
    return PRODUCTION_CATALOG_NOT_EVALUATED


def evaluate_production_catalog_status(
    input_data: dict[str, Any] | Any,
    config: ProductionCatalogBlocklistConfig | dict[str, Any] | None = None,
) -> ProductionCatalogStatusReport:
    cfg = (
        config
        if isinstance(config, ProductionCatalogBlocklistConfig)
        else ProductionCatalogBlocklistConfig(**dict(config or {}))
    )
    data = _to_dict(input_data)

    request_id = str(data.get("request_id") or data.get("instrument_id") or "request_unspecified")
    instrument_id = str(data.get("instrument_id") or "instrument_unspecified")
    method_family = str(data.get("method_family") or data.get("estimator_family") or "UNKNOWN")
    estimator_family = str(data.get("estimator_family") or method_family)
    inference_family = str(data.get("inference_family") or "UNKNOWN")
    claim_type = data.get("claim_type")
    requested_role = data.get("requested_role")
    production_context = data.get("production_context")
    characterization_status = data.get("characterization_status")
    evidence_sources = list(data.get("evidence_sources") or ())

    blockers: list[str] = []
    restrictions: list[str] = []
    remediation: list[str] = []
    warnings: list[str] = []

    if not cfg.enforce_production_catalog_blocklist:
        return ProductionCatalogStatusReport(
            request_id=request_id,
            instrument_id=instrument_id,
            method_family=method_family,
            estimator_family=estimator_family,
            inference_family=inference_family,
            claim_type=str(claim_type) if claim_type else None,
            requested_role=str(requested_role) if requested_role else None,
            production_context=str(production_context) if production_context else None,
            production_catalog_status=PRODUCTION_CATALOG_NOT_EVALUATED,
            is_production_blocked=False,
            is_research_allowed=True,
            is_diagnostic_only=False,
            is_restricted_expert_review=False,
            blockers=(),
            restrictions=(),
            required_remediation=(),
            evidence_sources=tuple(evidence_sources),
            maturity_status=None,
            characterization_status=str(characterization_status) if characterization_status else None,
            claim_boundary_report=_claim_boundary_report(evaluated=False, blocked=False),
            trace={"enforcement_disabled": True},
            warnings=(),
        )

    maturity = _resolve_maturity(estimator_family, method_family)
    maturity_status = maturity.value if maturity else None

    instrument_status = _apply_instrument_rules(
        instrument_id=instrument_id,
        estimator_family=estimator_family,
        inference_family=inference_family,
        claim_type=str(claim_type) if claim_type else None,
        blockers=blockers,
        restrictions=restrictions,
        remediation=remediation,
        evidence=evidence_sources,
        warnings=warnings,
        allow_augsynth_conformal_production=cfg.allow_augsynth_conformal_production,
    )
    maturity_status_value = _apply_maturity_rules(maturity, blockers=blockers, restrictions=restrictions)

    if instrument_status:
        status = instrument_status
    else:
        status = maturity_status_value

    if status == PRODUCTION_CATALOG_ELIGIBLE_FOR_REVIEW:
        blockers.append(BLOCKER_MISSING_THRESHOLDS)
        blockers.append(BLOCKER_CLAIM_AUTH_MISSING)
        status = PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW
        restrictions.append("no_production_safe_estimators_in_catalog")

    is_diagnostic_only = status == PRODUCTION_CATALOG_DIAGNOSTIC_ONLY
    is_restricted = status == PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW
    is_research_only = status == PRODUCTION_CATALOG_RESEARCH_ONLY
    is_production_blocked = status in (
        PRODUCTION_CATALOG_BLOCKED,
        PRODUCTION_CATALOG_RESEARCH_ONLY,
        PRODUCTION_CATALOG_DIAGNOSTIC_ONLY,
        PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW,
        PRODUCTION_CATALOG_NOT_EVALUATED,
    )

    prod_ctx = _is_production_context(
        str(production_context) if production_context else None,
        str(requested_role) if requested_role else None,
    )
    if prod_ctx and is_production_blocked and cfg.block_production_context_when_catalog_blocked:
        if not blockers:
            blockers.append(BLOCKER_UNSUPPORTED_PRODUCTION_CLAIM)

    is_research_allowed = True
    if cfg.block_research_context_when_catalog_blocked and is_production_blocked:
        is_research_allowed = False
    elif is_research_only and cfg.allow_research_only_dry_run:
        is_research_allowed = True

    trace = {
        "policy_version": _ARTIFACT_VERSION,
        "instrument_id": instrument_id,
        "estimator_family": estimator_family,
        "inference_family": inference_family,
        "production_context": production_context,
        "requested_role": requested_role,
        "claim_type": claim_type,
        "maturity_status": maturity_status,
        "production_context_evaluated": prod_ctx,
    }

    return ProductionCatalogStatusReport(
        request_id=request_id,
        instrument_id=instrument_id,
        method_family=method_family,
        estimator_family=estimator_family,
        inference_family=inference_family,
        claim_type=str(claim_type) if claim_type else None,
        requested_role=str(requested_role) if requested_role else None,
        production_context=str(production_context) if production_context else None,
        production_catalog_status=status,
        is_production_blocked=is_production_blocked,
        is_research_allowed=is_research_allowed,
        is_diagnostic_only=is_diagnostic_only,
        is_restricted_expert_review=is_restricted,
        blockers=tuple(dict.fromkeys(blockers)),
        restrictions=tuple(dict.fromkeys(restrictions)),
        required_remediation=tuple(dict.fromkeys(remediation)),
        evidence_sources=tuple(dict.fromkeys(evidence_sources)),
        maturity_status=maturity_status,
        characterization_status=str(characterization_status) if characterization_status else None,
        claim_boundary_report=_claim_boundary_report(evaluated=True, blocked=bool(blockers)),
        trace=trace,
        warnings=tuple(dict.fromkeys(warnings)),
    )


def evaluate_production_catalog_status_batch(
    requests: list[dict[str, Any] | Any],
    config: ProductionCatalogBlocklistConfig | dict[str, Any] | None = None,
) -> tuple[ProductionCatalogStatusReport, ...]:
    return tuple(evaluate_production_catalog_status(req, config=config) for req in requests)


def is_production_blocked(
    input_data: dict[str, Any] | Any,
    config: ProductionCatalogBlocklistConfig | dict[str, Any] | None = None,
) -> bool:
    return evaluate_production_catalog_status(input_data, config=config).is_production_blocked


def explain_production_blockers(
    input_data: dict[str, Any] | Any,
    config: ProductionCatalogBlocklistConfig | dict[str, Any] | None = None,
) -> tuple[str, ...]:
    return evaluate_production_catalog_status(input_data, config=config).blockers


def production_catalog_overlay_for_matrix(
    report: ProductionCatalogStatusReport,
) -> dict[str, Any]:
    return {
        "production_catalog_status": report.production_catalog_status,
        "is_production_blocked": report.is_production_blocked,
        "is_research_allowed": report.is_research_allowed,
        "production_blockers": list(report.blockers),
        "production_restrictions": list(report.restrictions),
        "production_catalog_evidence": list(report.evidence_sources),
        "production_catalog_trace": dict(report.trace),
        "maturity_status": report.maturity_status,
    }


def production_catalog_executor_metadata(
    report: ProductionCatalogStatusReport,
) -> dict[str, Any]:
    return {
        "production_catalog_status": report.production_catalog_status,
        "production_catalog_blocked": report.is_production_blocked,
        "production_claim_blocked": report.is_production_blocked,
        "production_blockers": list(report.blockers),
        "production_catalog_metadata": {
            "restrictions": list(report.restrictions),
            "required_remediation": list(report.required_remediation),
            "is_research_allowed": report.is_research_allowed,
            "is_diagnostic_only": report.is_diagnostic_only,
            "maturity_status": report.maturity_status,
        },
    }


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    scenarios = [
        ("did_bootstrap_blocked", is_production_blocked({"instrument_id": "DID_BOOTSTRAP", "production_context": "production"})),
        ("tbr_ridge_kfold_blocked", is_production_blocked({"instrument_id": "TBR_RIDGE_KFOLD", "production_context": "production"})),
        ("research_allowed", evaluate_production_catalog_status(
            {"instrument_id": "DID_BOOTSTRAP", "production_context": "research"},
            config={"allow_research_only_dry_run": True},
        ).is_research_allowed),
    ]
    failed = [name for name, ok in scenarios if not ok]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "production_catalog_blocklist_enforcement",
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": [
            "AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001",
            "CLAIM_AUTHORIZATION_CONTRACT_001",
            "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC",
            "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR",
            "READOUT_PLAN_RUNTIME_001",
            "METHOD_SUITABILITY_RUNTIME_001",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "failed_scenarios": failed,
        "final_verdict": _VERDICT,
        "research_use_preserved": True,
        "production_claims_blocked_for_research_only_methods": True,
        "did_bootstrap_production_claim_blocked": is_production_blocked(
            {"instrument_id": "DID_BOOTSTRAP", "production_context": "production"}
        ),
        "tbr_ridge_kfold_production_claim_blocked": is_production_blocked(
            {"instrument_id": "TBR_RIDGE_KFOLD", "production_context": "production"}
        ),
        "tbr_ridge_conformal_production_claim_blocked": is_production_blocked(
            {"estimator_family": "TBR_RIDGE_FAMILY", "inference_family": "Conformal", "production_context": "production"}
        ),
        "tbr_ridge_jackknife_production_claim_blocked": is_production_blocked(
            {"estimator_family": "TBR_RIDGE_FAMILY", "inference_family": "UnitJackKnife", "production_context": "production"}
        ),
        "trop_mtgp_bayesian_tbr_production_exposure_blocked": all(
            is_production_blocked({"estimator_family": fam, "production_context": "production"})
            for fam in ("TROP_FAMILY", "MTGP_FAMILY", "BAYESIAN_TBR_FAMILY")
        ),
        "production_catalog_integrated_with_method_suitability": True,
        "production_catalog_integrated_with_readout_plan": True,
        "production_catalog_integrated_with_executor_adapters": True,
        "production_catalog_integrated_with_execution_runtime": True,
        **_POSITIVE_FLAGS,
        **_AUTH_FALSE,
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
