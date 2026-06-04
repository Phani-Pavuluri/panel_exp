"""DESIGN-ESTIMATOR-INFERENCE-SUITABILITY-FRAMEWORK-001 — post-Layer-5 suitability policy.

Maps Layer 5 combination matrix rows to non-promotional suitability classes.
Does not assign trust roles, run OC, or wire TrustReport/CalibrationSignal/MMM/LLM.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LAYER5_JSON = _REPO_ROOT / "docs/track_d/archives/METHOD_COMBINATION_VALIDATION_MATRIX_001.json"

SuitabilityClass = Literal[
    "not_yet_assessed",
    "oc_ready_not_suitable_yet",
    "diagnostic_candidate_pending_oc",
    "suitability_candidate_pending_oc",
    "blocked_before_suitability",
    "bridge_required_before_suitability",
    "implementation_fix_required",
    "research_only",
    "quarantine_or_deprecate",
]

CurrentAllowedUse = Literal[
    "planning_only",
    "diagnostic_research_only",
    "oc_execution_only",
    "metadata_guardrail_only",
    "no_runtime_use",
]

FrameworkNextAction = Literal[
    "run_d5_stat_smoke",
    "run_d5_stat_characterization",
    "run_d5_stat_calibration",
    "write_bridge_adr",
    "fix_implementation_gap",
    "quarantine_or_deprecate",
    "research_only",
    "wait_for_oc_evidence",
]

FORBIDDEN_CLASS_SUBSTRINGS = (
    "primary",
    "secondary",
    "directional",
    "trusted",
    "promoted",
    "production_ready",
    "production-ready",
    "calibration_signal_eligible",
    "governed_uncertainty",
)

RECOMMENDED_NEXT_ARTIFACT = "D5-STAT-SMOKE-CALLABLE-001"

# Explicit suitability overrides (policy rules 5–14).
COMBO_SUITABILITY: dict[str, SuitabilityClass] = {
    "AUGSYNTH-CONFORMAL": "blocked_before_suitability",
    "AUGSYNTH-JK": "implementation_fix_required",
    "MCELL-POOLED-AUGSYNTH": "bridge_required_before_suitability",
    "MCELL-POOLED-SCM-JK": "bridge_required_before_suitability",
    "SUPERGEO-SCM-JK": "bridge_required_before_suitability",
    "TRIM-SCM-JK": "bridge_required_before_suitability",
    "SUPERGEO-AUGSYNTH-POINT": "bridge_required_before_suitability",
    "TRIM-AUGSYNTH-POINT": "bridge_required_before_suitability",
    "TBR-UNIT-JK": "blocked_before_suitability",
    "TBRRIDGE-BAYESIAN-REG": "blocked_before_suitability",
    "TROP-RESEARCH": "research_only",
    "MTGP-RESEARCH": "research_only",
    "BAYESIANTBR-MCMC": "research_only",
    "SDID-POINT": "research_only",
    "TBRRIDGE-PLACEBO": "blocked_before_suitability",
    "SCM-JK": "suitability_candidate_pending_oc",
    "SCM-PLACEBO": "diagnostic_candidate_pending_oc",
    "AUGSYNTH-POINT": "diagnostic_candidate_pending_oc",
    "TBR-AGG-POINT": "suitability_candidate_pending_oc",
    "TBR-AGG-KFOLD": "diagnostic_candidate_pending_oc",
    "DID-BOOTSTRAP": "suitability_candidate_pending_oc",
    "MCELL-PERCELL-SCM-JK": "suitability_candidate_pending_oc",
}

SUITABILITY_CANDIDATE_PENDING = frozenset(
    {"suitability_candidate_pending_oc", "diagnostic_candidate_pending_oc"}
)


@dataclass
class SuitabilityRow:
    combination_id: str
    source_matrix_status: str
    design_family: str
    estimator_family: str
    inference_family: str
    geometry: str
    estimand: str
    effect_scale: str
    interval_semantics: str
    suitability_class: SuitabilityClass
    required_oc_artifacts: list[str]
    required_bridge_artifacts: list[str]
    required_implementation_fixes: list[str]
    minimum_evidence_before_diagnostic_use: str
    minimum_evidence_before_suitability_claim: str
    minimum_evidence_before_role_assignment: str
    current_allowed_use: CurrentAllowedUse
    current_forbidden_use: list[str]
    next_action: FrameworkNextAction
    promotion_allowed: bool = False
    trust_role_allowed: bool = False
    calibration_signal_allowed: bool = False
    mmm_allowed: bool = False
    llm_recommendation_allowed: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_layer5_matrix() -> dict[str, Any]:
    return json.loads(_LAYER5_JSON.read_text(encoding="utf-8"))


def _suitability_from_matrix(row: dict[str, Any]) -> SuitabilityClass:
    cid = row["combination_id"]
    if cid in COMBO_SUITABILITY:
        return COMBO_SUITABILITY[cid]
    status = row["validation_matrix_status"]
    if status == "research_only_oc":
        return "research_only"
    if status == "quarantine_or_deprecate":
        return "quarantine_or_deprecate"
    if status == "blocked_needs_bridge":
        return "bridge_required_before_suitability"
    if status == "blocked_before_oc":
        if row.get("allowed_next_action") == "fix_implementation_gap":
            return "implementation_fix_required"
        return "blocked_before_suitability"
    if status == "ready_for_oc_execution":
        return "oc_ready_not_suitable_yet"
    if status == "ready_for_oc_with_caveats":
        return "diagnostic_candidate_pending_oc"
    return "not_yet_assessed"


def _next_action(row: dict[str, Any], suitability: SuitabilityClass) -> FrameworkNextAction:
    if suitability == "bridge_required_before_suitability":
        return "write_bridge_adr"
    if suitability == "implementation_fix_required":
        return "fix_implementation_gap"
    if suitability == "research_only":
        return "research_only"
    if suitability == "quarantine_or_deprecate":
        return "quarantine_or_deprecate"
    if suitability in (
        "blocked_before_suitability",
        "not_yet_assessed",
    ):
        return "wait_for_oc_evidence"
    matrix_action = row.get("allowed_next_action", "")
    battery = row.get("minimum_battery_level", "B")
    if matrix_action == "run_smoke_protocol" or battery == "A":
        return "run_d5_stat_smoke"
    if matrix_action == "run_calibration_protocol" or battery == "C":
        return "run_d5_stat_calibration"
    if suitability in SUITABILITY_CANDIDATE_PENDING:
        return "run_d5_stat_characterization"
    if suitability == "oc_ready_not_suitable_yet":
        return "run_d5_stat_smoke"
    return "wait_for_oc_evidence"


def _allowed_use(suitability: SuitabilityClass) -> CurrentAllowedUse:
    if suitability in ("blocked_before_suitability", "bridge_required_before_suitability"):
        return "no_runtime_use"
    if suitability == "implementation_fix_required":
        return "planning_only"
    if suitability == "research_only":
        return "diagnostic_research_only"
    if suitability == "quarantine_or_deprecate":
        return "no_runtime_use"
    if suitability in SUITABILITY_CANDIDATE_PENDING:
        return "oc_execution_only"
    if suitability == "oc_ready_not_suitable_yet":
        return "oc_execution_only"
    return "planning_only"


def _forbidden_use() -> list[str]:
    return [
        "trustreport_primary_secondary_directional_role",
        "calibration_signal_export",
        "mmm_integration",
        "llm_product_recommendation",
        "production_promotion_claim",
        "governed_uncertainty_without_oc",
    ]


def _evidence_strings(suitability: SuitabilityClass, row: dict[str, Any]) -> tuple[str, str, str]:
    artifact = row.get("required_d5_stat_artifact") or "D5-STAT-* pending"
    diagnostic = f"Completed {artifact} Level B characterization archive (none exist yet)"
    suitability_ev = (
        f"Completed {artifact} Level C calibration + interval semantics evidence "
        "(not satisfied by protocol alone)"
    )
    role_ev = (
        "Explicit TRUST_ROLE_ASSIGNMENT_FRAMEWORK_001 charter after suitability evidence; "
        "not authorized by this artifact"
    )
    if suitability in ("blocked_before_suitability", "bridge_required_before_suitability"):
        diagnostic = "blocked — no diagnostic product use until bridge/fix"
        suitability_ev = "blocked — no suitability claim"
    elif suitability == "implementation_fix_required":
        diagnostic = "blocked until implementation gaps closed"
        suitability_ev = "blocked until IMPL fixes + OC"
    elif suitability == "research_only":
        diagnostic = "research characterization only — no product diagnostic claim"
        suitability_ev = "not applicable for product suitability"
    elif suitability == "oc_ready_not_suitable_yet":
        diagnostic = f"Requires smoke then characterization: {RECOMMENDED_NEXT_ARTIFACT} then {artifact}"
        suitability_ev = "Requires completed D5-STAT OC — protocol readiness insufficient"
    return diagnostic, suitability_ev, role_ev


def _row_from_matrix(matrix_row: dict[str, Any]) -> SuitabilityRow:
    suitability = _suitability_from_matrix(matrix_row)
    oc_artifacts: list[str] = []
    if matrix_row.get("required_d5_stat_artifact"):
        oc_artifacts.append(matrix_row["required_d5_stat_artifact"])
    elif suitability not in ("blocked_before_suitability", "bridge_required_before_suitability"):
        oc_artifacts.append(RECOMMENDED_NEXT_ARTIFACT)
    bridge: list[str] = []
    if matrix_row.get("required_bridge"):
        bridge.append(matrix_row["required_bridge"])
    fixes = list(matrix_row.get("known_failure_modes", []))[:5]
    diag, suit, role = _evidence_strings(suitability, matrix_row)
    return SuitabilityRow(
        combination_id=matrix_row["combination_id"],
        source_matrix_status=matrix_row["validation_matrix_status"],
        design_family=matrix_row["design_family"],
        estimator_family=matrix_row["estimator_family"],
        inference_family=matrix_row["inference_family"],
        geometry=matrix_row["geometry"],
        estimand=matrix_row["estimand"],
        effect_scale=matrix_row["effect_scale"],
        interval_semantics=matrix_row["interval_semantics"],
        suitability_class=suitability,
        required_oc_artifacts=oc_artifacts,
        required_bridge_artifacts=bridge,
        required_implementation_fixes=fixes,
        minimum_evidence_before_diagnostic_use=diag,
        minimum_evidence_before_suitability_claim=suit,
        minimum_evidence_before_role_assignment=role,
        current_allowed_use=_allowed_use(suitability),
        current_forbidden_use=_forbidden_use(),
        next_action=_next_action(matrix_row, suitability),
        notes=(
            "OC-ready from Layer 5 does not imply suitable. "
            "No TrustReport/CalibrationSignal/MMM/LLM wiring from this framework."
        ),
    )


def suitability_rows() -> list[SuitabilityRow]:
    l5 = load_layer5_matrix()
    return [_row_from_matrix(r) for r in l5["rows"]]


def assert_layer5_coverage(payload: dict[str, Any]) -> None:
    l5 = load_layer5_matrix()
    framework_ids = {r["combination_id"] for r in payload["rows"]}
    matrix_ids = {r["combination_id"] for r in l5["rows"]}
    if framework_ids != matrix_ids:
        raise ValueError(
            f"Layer 5 coverage mismatch missing={matrix_ids - framework_ids} "
            f"extra={framework_ids - matrix_ids}"
        )


def build_suitability_framework() -> dict[str, Any]:
    rows = suitability_rows()
    by_class: dict[str, int] = {}
    for r in rows:
        by_class[r.suitability_class] = by_class.get(r.suitability_class, 0) + 1
    payload = {
        "document_id": "DESIGN-ESTIMATOR-INFERENCE-SUITABILITY-FRAMEWORK-001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "panel_exp/validation/design_estimator_inference_suitability_framework_001.py",
        "parent_artifact": "METHOD-COMBINATION-VALIDATION-MATRIX-001",
        "suitability_class_values": [
            "not_yet_assessed",
            "oc_ready_not_suitable_yet",
            "diagnostic_candidate_pending_oc",
            "suitability_candidate_pending_oc",
            "blocked_before_suitability",
            "bridge_required_before_suitability",
            "implementation_fix_required",
            "research_only",
            "quarantine_or_deprecate",
        ],
        "current_allowed_use_values": [
            "planning_only",
            "diagnostic_research_only",
            "oc_execution_only",
            "metadata_guardrail_only",
            "no_runtime_use",
        ],
        "next_action_values": [
            "run_d5_stat_smoke",
            "run_d5_stat_characterization",
            "run_d5_stat_calibration",
            "write_bridge_adr",
            "fix_implementation_gap",
            "quarantine_or_deprecate",
            "research_only",
            "wait_for_oc_evidence",
        ],
        "recommended_next_concrete_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "future_role_assignment_prerequisite": "TRUST_ROLE_ASSIGNMENT_FRAMEWORK_001",
        "policy_rules": [
            "ready_for_oc does not imply suitable",
            "suitability requires completed D5-STAT evidence",
            "inference suitability requires interval semantics OC",
            "geometry evidence does not transfer across modes",
            "pooled multicell blocked until causal pooling ADR + OC",
            "supergeo/trim blocked until bridge ADR + validation",
            "no CalibrationSignal/MMM/TrustReport/LLM from this artifact",
        ],
        "d5_stat_evidence_queue": list(
            load_layer5_matrix().get("d5_stat_execution_queue", [])
        ),
        "counts": {
            "rows_total": len(rows),
            "by_suitability_class": by_class,
            "layer5_rows_mapped": len(rows),
        },
        "known_blocked_combos": [
            "AUGSYNTH-CONFORMAL",
            "AUGSYNTH-JK",
            "MCELL-POOLED-AUGSYNTH",
            "MCELL-POOLED-SCM-JK",
            "SUPERGEO-SCM-JK",
            "TRIM-SCM-JK",
            "TBR-UNIT-JK",
            "TBRRIDGE-BAYESIAN-REG",
        ],
        "rows": [r.to_dict() for r in rows],
    }
    assert_layer5_coverage(payload)
    return payload


def write_archive(path: Path | None = None) -> Path:
    payload = build_suitability_framework()
    if path is None:
        path = (
            _REPO_ROOT
            / "docs"
            / "track_d"
            / "archives"
            / "DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.json"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    out = write_archive()
    n = build_suitability_framework()["counts"]["rows_total"]
    print(f"Wrote {out} ({n} suitability rows)")


if __name__ == "__main__":
    main()
