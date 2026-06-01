"""Track B contract TrustReport composer (B5c).

Consumes adapter **facts** and calibration **scope** from golden fixtures;
emits ``alignment_verdict`` and ``trust_outcome`` only here — not on Evidence.

This module implements the B2/B4 interpretation rules sufficient to match
B5a golden ``trust_report_expected_output`` oracles. It is not production
TrustReport code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional

from tests.track_b.contract_fixtures import FixtureCase, TRUST_VERDICT_FIELDS

AlignmentVerdict = Literal["aligned", "divergent", "incompatible", "not_assessable"]
TrustOutcome = Literal[
    "supported",
    "supported_with_limitations",
    "inconclusive",
    "unsupported",
    "not_assessable",
]

LIFT_CLAIM_TYPES = frozenset(
    {
        "positive_lift_detection",
    }
)
INTERVAL_BACKED_CLAIM_TYPES = frozenset(
    {
        "positive_lift_detection",
    }
)
MMM_CLAIM_TYPES = frozenset({"mmm_delta_mu"})


@dataclass(frozen=True)
class TrustScenarioVerdict:
    scenario_id: str
    intended_use: str
    claim_type: str
    alignment_verdict: AlignmentVerdict
    trust_outcome: TrustOutcome
    alignment_reference_estimand_id: str


@dataclass(frozen=True)
class TrustReportComposition:
    """TrustReport contract slice — verdict-bearing layers only."""

    alignment_reference_estimand_id: str
    declared_estimand_id: Optional[str]
    exported_estimand_id: Optional[str]
    measurement_instrument_id: Optional[str]
    scenarios: tuple[TrustScenarioVerdict, ...]


def _effective_declared_estimand_id(case: FixtureCase) -> Optional[str]:
    """Spec declaration, or evidence copy after adapter resolution (e.g. legacy map)."""
    spec = case.spec
    evidence = case.adapter_expected_output.get("experiment_evidence") or {}
    return spec.get("declared_estimand_id") or evidence.get("declared_estimand_id")


def _alignment_reference_estimand_id(case: FixtureCase) -> str:
    tr = case.trust_report_expected_output
    if tr.get("alignment_reference_estimand_id"):
        return tr["alignment_reference_estimand_id"]
    return _effective_declared_estimand_id(case) or ""


def compose_trust_scenario_verdict(
    case: FixtureCase,
    scenario: dict[str, Any],
) -> TrustScenarioVerdict:
    """Apply contract interpretation rules; return verdict for one scenario."""
    alignment_verdict, trust_outcome = _interpret(case, scenario)
    return TrustScenarioVerdict(
        scenario_id=scenario["scenario_id"],
        intended_use=scenario["intended_use"],
        claim_type=scenario["claim_type"],
        alignment_verdict=alignment_verdict,
        trust_outcome=trust_outcome,
        alignment_reference_estimand_id=_alignment_reference_estimand_id(case),
    )


def compose_trust_report(case: FixtureCase) -> TrustReportComposition:
    """Compose all TrustReport scenarios for a fixture case."""
    tr_out = case.trust_report_expected_output
    scenarios_cfg = tr_out.get("scenarios") or []
    if tr_out.get("composition_permitted") is False and not scenarios_cfg:
        scenarios_cfg = [
            {
                "scenario_id": "blocked_composition",
                "intended_use": "any",
                "claim_type": "any",
            }
        ]
    scenarios = tuple(
        compose_trust_scenario_verdict(case, s) for s in scenarios_cfg
    )
    evidence = case.adapter_expected_output.get("experiment_evidence") or {}
    return TrustReportComposition(
        alignment_reference_estimand_id=_alignment_reference_estimand_id(case),
        declared_estimand_id=evidence.get("declared_estimand_id"),
        exported_estimand_id=evidence.get("exported_estimand_id"),
        measurement_instrument_id=evidence.get("measurement_instrument_id"),
        scenarios=scenarios,
    )


def trust_report_to_dict(composition: TrustReportComposition) -> dict[str, Any]:
    """Serialize for comparison against fixture oracle keys."""
    return {
        "alignment_reference_estimand_id": composition.alignment_reference_estimand_id,
        "declared_estimand_id": composition.declared_estimand_id,
        "exported_estimand_id": composition.exported_estimand_id,
        "measurement_instrument_id": composition.measurement_instrument_id,
        "scenarios": [
            {
                "scenario_id": s.scenario_id,
                "intended_use": s.intended_use,
                "claim_type": s.claim_type,
                "alignment_verdict": s.alignment_verdict,
                "trust_outcome": s.trust_outcome,
            }
            for s in composition.scenarios
        ],
    }


def _interpret(
    case: FixtureCase,
    scenario: dict[str, Any],
) -> tuple[AlignmentVerdict, TrustOutcome]:
    claim = scenario.get("claim_type", "any")
    adapter = case.adapter_expected_output
    evidence = adapter.get("experiment_evidence") or {}
    facts = adapter.get("alignment_facts") or {}
    signal = case.calibration_signal_binding or {}
    spec = case.spec
    export_status = adapter.get("export_status")

    # --- assessability (B2 §4.4 step 1) ---
    if export_status == "blocked":
        return "not_assessable", "not_assessable"

    if case.trust_report_expected_output.get("composition_permitted") is False:
        return "not_assessable", "not_assessable"

    if not _effective_declared_estimand_id(case):
        return "not_assessable", "not_assessable"

    if evidence.get("calibration_signal_missing"):
        if claim in LIFT_CLAIM_TYPES and claim not in MMM_CLAIM_TYPES:
            return "not_assessable", "not_assessable"

    # --- MMM intake (B2 §4.3, GOLD-004) ---
    if claim in MMM_CLAIM_TYPES:
        if evidence.get("mmm_intake_blocked"):
            if not spec.get("estimand_transform_ref"):
                return "incompatible", "unsupported"
            if not evidence.get("transform_evidence_complete"):
                return "aligned", "not_assessable"
        return "aligned", "not_assessable"

    # --- geometry scope (GOLD-010) ---
    if facts.get("geometry_within_scope") is False:
        if claim == "null_viability":
            return "incompatible", "not_assessable"
        return "incompatible", "unsupported"

    if export_status == "partial":
        if evidence.get("decision_grade_export_permitted") is False:
            if claim in LIFT_CLAIM_TYPES:
                return "incompatible", "unsupported"
            if claim == "null_viability":
                return "incompatible", "not_assessable"

    if export_status == "complete" and evidence.get("exported_estimand_id") == "unknown":
        return "not_assessable", "not_assessable"

    # --- aggregation drift before interval mismatch (GOLD-009, DEF-009) ---
    if facts.get("aggregation_divergence_detected"):
        return "divergent", "inconclusive"

    # --- interval / scale compatibility for lift (GOLD-003, 005, 008) ---
    if claim in INTERVAL_BACKED_CLAIM_TYPES:
        interval_sem = evidence.get("interval_semantics")
        if interval_sem == "none":
            return "incompatible", "unsupported"
        if interval_sem == "placebo_band":
            return "incompatible", "unsupported"
        if facts.get("interval_semantics_compatible") is False:
            return "incompatible", "unsupported"
        if facts.get("declared_interval_aligned") is False:
            return "incompatible", "unsupported"
        if facts.get("scale_compatible") is False:
            return "incompatible", "unsupported"

    # --- declared vs exported mismatch ---
    if facts.get("declared_exported_aligned") is False:
        if claim in LIFT_CLAIM_TYPES:
            return "incompatible", "unsupported"
        if claim == "point_directional_read":
            return "aligned", "inconclusive"

    # --- calibration signal usage boundary (GOLD-001, 002) ---
    boundary = signal.get("expected_usage_boundary")
    lift_cal = signal.get("expected_lift_detection_calibrated")

    if claim == "null_viability":
        if boundary in ("null_monitor_only", "null_reference_diagnostic"):
            if export_status == "complete" and facts.get("declared_exported_aligned", True):
                if facts.get("declared_interval_aligned", True) is not False:
                    return "aligned", "supported"
        return "aligned", "inconclusive"

    if claim in LIFT_CLAIM_TYPES:
        if boundary == "null_monitor_only":
            return "aligned", "inconclusive"
        if boundary in ("runnable_not_trusted", "research_only"):
            return "aligned", "inconclusive"
        if lift_cal is False:
            return "aligned", "inconclusive"
        if boundary == "point_only":
            return "incompatible", "unsupported"

    if claim == "point_directional_read":
        return "aligned", "inconclusive"

    if claim == "cumulative_att_read":
        if facts.get("declared_exported_aligned", True):
            return "aligned", "inconclusive"
        return "incompatible", "unsupported"

    # --- default: complete export with aligned facts ---
    if export_status == "complete":
        if facts.get("declared_exported_aligned", True) and facts.get(
            "declared_interval_aligned", True
        ):
            return "aligned", "inconclusive"

    return "not_assessable", "not_assessable"


def assert_composition_has_only_trust_verdict_fields(
    composition: TrustReportComposition,
) -> None:
    """TrustReport scenarios may carry verdict fields; composition root may not."""
    d = trust_report_to_dict(composition)
    for key in d:
        if key == "scenarios":
            continue
        assert key not in TRUST_VERDICT_FIELDS, f"root must not contain {key}"
    for scenario in d["scenarios"]:
        assert "alignment_verdict" in scenario
        assert "trust_outcome" in scenario
