"""Track B TrustReport composition (M2.2 production path).

Consumes adapter **facts** and optional calibration **scope**; emits
``alignment_verdict`` and ``trust_outcome`` only on TrustReport scenarios —
never on Evidence or adapter layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Optional, Sequence

TRUST_REPORT_VERSION = "0.1-m2.2"

AlignmentVerdict = Literal["aligned", "divergent", "incompatible", "not_assessable"]
TrustOutcome = Literal[
    "supported",
    "supported_with_limitations",
    "inconclusive",
    "unsupported",
    "not_assessable",
]

LIFT_CLAIM_TYPES = frozenset({"positive_lift_detection"})
INTERVAL_BACKED_CLAIM_TYPES = frozenset({"positive_lift_detection"})
MMM_CLAIM_TYPES = frozenset({"mmm_delta_mu"})

TRUST_VERDICT_FIELDS = frozenset({"trust_outcome", "alignment_verdict"})


@dataclass(frozen=True)
class TrustComposeContext:
    """Inputs for TrustReport interpretation (adapter facts + spec scope)."""

    spec: Mapping[str, Any]
    adapter_output: Mapping[str, Any]
    calibration_signal_binding: Optional[Mapping[str, Any]] = None
    composition_permitted: bool = True
    alignment_reference_estimand_id: Optional[str] = None


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
    alignment_reference_estimand_id: str
    declared_estimand_id: Optional[str]
    exported_estimand_id: Optional[str]
    measurement_instrument_id: Optional[str]
    scenarios: tuple[TrustScenarioVerdict, ...]


@dataclass(frozen=True)
class TrustReportAttachResult:
    """Outcome of optional TrustReport attachment to ``track_b_views``."""

    present: bool
    omit_reason: Optional[str] = None
    composition: Optional[TrustReportComposition] = None


def effective_declared_estimand_id(ctx: TrustComposeContext) -> Optional[str]:
    evidence = ctx.adapter_output.get("experiment_evidence") or {}
    return ctx.spec.get("declared_estimand_id") or evidence.get("declared_estimand_id")


def alignment_reference_estimand_id(ctx: TrustComposeContext) -> str:
    if ctx.alignment_reference_estimand_id:
        return ctx.alignment_reference_estimand_id
    return effective_declared_estimand_id(ctx) or ""


def compose_trust_scenario_verdict(
    ctx: TrustComposeContext,
    scenario: Mapping[str, Any],
) -> TrustScenarioVerdict:
    alignment_verdict, trust_outcome = _interpret(ctx, scenario)
    return TrustScenarioVerdict(
        scenario_id=str(scenario["scenario_id"]),
        intended_use=str(scenario.get("intended_use", "")),
        claim_type=str(scenario.get("claim_type", "any")),
        alignment_verdict=alignment_verdict,
        trust_outcome=trust_outcome,
        alignment_reference_estimand_id=alignment_reference_estimand_id(ctx),
    )


def compose_trust_report(
    ctx: TrustComposeContext,
    scenarios: Sequence[Mapping[str, Any]],
) -> TrustReportComposition:
    scenarios_cfg = list(scenarios)
    if not ctx.composition_permitted and not scenarios_cfg:
        scenarios_cfg = [
            {
                "scenario_id": "blocked_composition",
                "intended_use": "any",
                "claim_type": "any",
            }
        ]
    composed = tuple(compose_trust_scenario_verdict(ctx, s) for s in scenarios_cfg)
    evidence = ctx.adapter_output.get("experiment_evidence") or {}
    return TrustReportComposition(
        alignment_reference_estimand_id=alignment_reference_estimand_id(ctx),
        declared_estimand_id=evidence.get("declared_estimand_id"),
        exported_estimand_id=evidence.get("exported_estimand_id"),
        measurement_instrument_id=evidence.get("measurement_instrument_id"),
        scenarios=composed,
    )


def trust_report_to_dict(composition: TrustReportComposition) -> dict[str, Any]:
    return {
        "trust_report_version": TRUST_REPORT_VERSION,
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


def attach_trust_report_to_views(
    views: dict[str, Any],
    *,
    spec: Mapping[str, Any],
    adapter_output: Mapping[str, Any],
    scenarios: Optional[Sequence[Mapping[str, Any]]],
    calibration_signal_binding: Optional[Mapping[str, Any]] = None,
    composition_permitted: bool = True,
    alignment_reference_estimand_id: Optional[str] = None,
) -> TrustReportAttachResult:
    """
    Attach TrustReport to an existing ``track_b_views`` dict (mutates ``views``).

    When ``scenarios`` is missing or empty, records an explicit omit reason and
    does not attach verdict fields.
    """
    if not scenarios:
        views["trust_report_present"] = False
        views["trust_report_omit_reason"] = "missing_trust_scenarios"
        return TrustReportAttachResult(
            present=False,
            omit_reason="missing_trust_scenarios",
        )

    ctx = TrustComposeContext(
        spec=spec,
        adapter_output=adapter_output,
        calibration_signal_binding=calibration_signal_binding,
        composition_permitted=composition_permitted,
        alignment_reference_estimand_id=alignment_reference_estimand_id,
    )
    composition = compose_trust_report(ctx, scenarios)
    views["trust_report_present"] = True
    views["trust_report_view"] = trust_report_to_dict(composition)
    return TrustReportAttachResult(present=True, composition=composition)


def _interpret(
    ctx: TrustComposeContext,
    scenario: Mapping[str, Any],
) -> tuple[AlignmentVerdict, TrustOutcome]:
    claim = scenario.get("claim_type", "any")
    adapter = ctx.adapter_output
    evidence = adapter.get("experiment_evidence") or {}
    facts = adapter.get("alignment_facts") or {}
    signal = ctx.calibration_signal_binding or {}
    spec = ctx.spec
    export_status = adapter.get("export_status")

    if export_status == "blocked":
        return "not_assessable", "not_assessable"

    if not ctx.composition_permitted:
        return "not_assessable", "not_assessable"

    if not effective_declared_estimand_id(ctx):
        return "not_assessable", "not_assessable"

    if evidence.get("calibration_signal_missing"):
        if claim in LIFT_CLAIM_TYPES and claim not in MMM_CLAIM_TYPES:
            return "not_assessable", "not_assessable"

    if claim in MMM_CLAIM_TYPES:
        if evidence.get("mmm_intake_blocked"):
            if not spec.get("estimand_transform_ref"):
                return "incompatible", "unsupported"
            if not evidence.get("transform_evidence_complete"):
                return "aligned", "not_assessable"
        return "aligned", "not_assessable"

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

    if facts.get("aggregation_divergence_detected"):
        return "divergent", "inconclusive"

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

    if facts.get("declared_exported_aligned") is False:
        if claim in LIFT_CLAIM_TYPES:
            return "incompatible", "unsupported"
        if claim == "point_directional_read":
            return "aligned", "inconclusive"

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

    if export_status == "complete":
        if facts.get("declared_exported_aligned", True) and facts.get(
            "declared_interval_aligned", True
        ):
            return "aligned", "inconclusive"

    return "not_assessable", "not_assessable"
