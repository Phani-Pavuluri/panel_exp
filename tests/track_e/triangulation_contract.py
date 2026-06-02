"""Track E triangulation contract evaluator (E5/E6 — non-production).

Evaluates E3 ``TriangulationProfile`` shapes against E5 CalibrationSignal
eligibility policy. Used as test oracle for E4 JSON fixtures only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "track_e_conflicts"
MANIFEST_PATH = FIXTURES_DIR / "manifest.json"

LIFT_CLAIM_TYPES = frozenset({"positive_lift_detection", "mmm_lift", "lift_point"})
INTERVAL_CLAIM_TYPES = frozenset(LIFT_CLAIM_TYPES | {"null_viability"})


@dataclass(frozen=True)
class TriangulationOutcome:
    agreement_state: str
    trust_report_disposition: str
    conflict_class: str
    trust_outcome_hint: str
    calibration_signal_eligibility: dict[str, Any]
    per_cell_dispositions: dict[str, str] = field(default_factory=dict)
    warning_class: str | None = None
    exclusion_class: str | None = None
    forbidden_violations: tuple[str, ...] = ()


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_e4_fixture(relative_path: str) -> dict[str, Any]:
    return json.loads((FIXTURES_DIR / relative_path).read_text(encoding="utf-8"))


def load_all_e4_fixtures() -> list[dict[str, Any]]:
    manifest = load_manifest()
    return [load_e4_fixture(entry["file"]) for entry in manifest["fixtures"]]


def _rows(profile: dict[str, Any]) -> list[dict[str, Any]]:
    return list(profile.get("evidence_rows") or [])


def _primary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in rows if r.get("evidence_role") == "primary"]


def _sign(point: float | None) -> int:
    if point is None or not isinstance(point, (int, float)):
        return 0
    if abs(point) < 1e-9:
        return 0
    return 1 if point > 0 else -1


def _covers_zero(row: dict[str, Any]) -> bool | None:
    unc = row.get("uncertainty")
    if not unc:
        return None
    return bool(unc.get("covers_zero"))


def _interval_excludes_zero(row: dict[str, Any]) -> bool:
    cz = _covers_zero(row)
    return cz is False


def _is_blocked_row(row: dict[str, Any]) -> bool:
    return row.get("suitability_status") in {"blocked", "characterization_required"} or row.get(
        "evidence_role"
    ) in {"blocked"}


def _has_planning_diagnostic(rows: list[dict[str, Any]]) -> bool:
    for r in rows:
        if r.get("evidence_role") != "diagnostic":
            continue
        mid = str(r.get("measurement_instrument_id", ""))
        if "power_analysis" in mid or r.get("claim_type") == "planning_mde":
            return True
    return False


def _non_comparable_estimand(rows: list[dict[str, Any]], declared: str) -> bool:
    groups = {r.get("comparability_group") for r in rows}
    return "non_comparable_estimand" in groups or any(
        r.get("estimand_id") and r.get("estimand_id") != declared
        and r.get("comparability_group") == "non_comparable_estimand"
        for r in rows
    )


def _detect_cell_level_conflict(profile: dict[str, Any], primaries: list[dict[str, Any]]) -> bool:
    if profile.get("geometry_mode") != "multi_cell":
        return False
    if profile.get("pooling_rule_id"):
        return False
    by_cell: dict[str, list[dict[str, Any]]] = {}
    for r in primaries:
        by_cell.setdefault(str(r.get("cell_id", "test_0")), []).append(r)
    if len(by_cell) < 2:
        return False
    signs = []
    excludes = []
    for cell_rows in by_cell.values():
        pt = cell_rows[0].get("point_estimate")
        signs.append(_sign(pt))
        excludes.append(_interval_excludes_zero(cell_rows[0]))
    if len(set(s for s in signs if s != 0)) > 1:
        return True
    if any(excludes) and not all(excludes):
        return True
    return False


def _per_cell_dispositions(primaries: list[dict[str, Any]], *, conflict: bool = False) -> dict[str, str]:
    out: dict[str, str] = {}
    for r in primaries:
        cell = str(r.get("cell_id", "test_0"))
        pt = r.get("point_estimate")
        if _interval_excludes_zero(r):
            out[cell] = "supported_with_limitations"
        elif _covers_zero(r) is True:
            if conflict and isinstance(pt, (int, float)) and pt > 0:
                out[cell] = "inconclusive"
            else:
                out[cell] = "null_compatible"
        else:
            out[cell] = "inconclusive"
    return out


def evaluate_triangulation(profile: dict[str, Any]) -> TriangulationOutcome:
    """Contract-only evaluator implementing E5 disposition priority."""
    rows = _rows(profile)
    declared = str(profile.get("declared_estimand_id", ""))
    declared_claim = str(profile.get("declared_claim_type", ""))

    if any(r.get("suitability_status") == "characterization_required" for r in rows):
        return _outcome(
            "blocked_by_suitability",
            "characterization_required",
            "E-CONFLICT-004",
            "not_assessable",
            {"eligible": False, "reason": "characterization_required"},
            warning_class="characterization_required",
            exclusion_class="blocked",
        )

    if any(
        r.get("suitability_status") == "blocked"
        or r.get("comparability_group") == "blocked_instrument"
        for r in rows
    ):
        return _outcome(
            "blocked_by_suitability",
            "blocked_by_geometry",
            "E-CONFLICT-004",
            "not_assessable",
            {"eligible": False, "reason": "blocked_by_geometry"},
            warning_class="blocked_by_geometry",
            exclusion_class="blocked",
        )

    if any(
        (r.get("freshness") or {}).get("stale") for r in rows if r.get("evidence_role") == "primary"
    ):
        return _outcome(
            "stale_or_freshness_blocked",
            "stale_downweight_or_exclude",
            "E-CONFLICT-002",
            "not_assessable",
            {"eligible": False, "bind_blocked": True, "reason": "stale_or_missing"},
            warning_class="stale",
            exclusion_class="stale_exclude",
        )

    if _non_comparable_estimand(rows, declared):
        return _outcome(
            "non_comparable_estimand",
            "non_comparable_estimand",
            "E-CONFLICT-003",
            "unsupported",
            {"eligible": False, "combined_signal_allowed": False},
            warning_class="non_comparable_estimand",
            exclusion_class="estimand_mismatch",
        )

    primaries = _primary_rows(rows)
    restricted = [r for r in rows if r.get("evidence_role") == "restricted"]

    if declared_claim in INTERVAL_CLAIM_TYPES or declared_claim in LIFT_CLAIM_TYPES:
        for r in rows:
            if r.get("interval_semantics") == "none" and r.get("uncertainty") is None:
                if r.get("evidence_role") in {"primary", "diagnostic"}:
                    return _outcome(
                        "missing_uncertainty",
                        "missing_uncertainty_warning",
                        "E-CONFLICT-002",
                        "unsupported",
                        {"eligible": False, "interval_claim_blocked": True},
                        warning_class="missing_uncertainty",
                        exclusion_class="missing_se",
                    )

    if _has_planning_diagnostic(rows) and primaries:
        return _outcome(
            "diagnostic_only_agreement",
            "planning_diagnostic_only",
            "E-CONFLICT-005",
            "inconclusive",
            {"eligible": False, "mmm_mde_feed_forbidden": True},
            warning_class="planning_diagnostic_only",
            exclusion_class="mmm_forbidden",
        )

    if _detect_cell_level_conflict(profile, primaries):
        per_cell = _per_cell_dispositions(primaries, conflict=True)
        return _outcome(
            "cell_level_conflict",
            "cell_level_conflict",
            "E-CONFLICT-008",
            "inconclusive",
            {"eligible": False, "pooled_allowed": False},
            per_cell_dispositions=per_cell,
            warning_class="cell_level_conflict",
            exclusion_class="pooled_forbidden",
        )

    primary = primaries[0] if primaries else None
    if primary and restricted:
        p_sign = _sign(primary.get("point_estimate"))
        for rr in restricted:
            r_sign = _sign(rr.get("point_estimate"))
            same_estimand = rr.get("estimand_id") == primary.get("estimand_id")
            if same_estimand and p_sign != 0 and r_sign != 0 and p_sign != r_sign:
                return _outcome(
                    "high_trust_conflict",
                    "method_conflict_warning",
                    "E-CONFLICT-008",
                    "divergent",
                    {"eligible": False, "lift_mmm_allowed": False},
                    warning_class="method_conflict_warning",
                    exclusion_class="conflict_fail_closed",
                )

        if _covers_zero(primary) is True and any(_interval_excludes_zero(r) for r in restricted):
            return _outcome(
                "restricted_method_conflict",
                "restricted_method_positive_but_primary_null_compatible",
                "E-CONFLICT-001",
                "inconclusive",
                {"eligible": False, "lift_mmm_allowed": False},
                warning_class="restricted_positive_context",
                exclusion_class="no_lift_claim",
            )

        if p_sign != 0 and all(_sign(r.get("point_estimate")) == p_sign for r in restricted):
            cs = _conditional_null_monitor_eligibility(primary, restricted)
            return _outcome(
                "directional_agreement_magnitude_differs",
                "directional_support_with_caveats",
                "E-CONFLICT-001",
                "supported_with_limitations",
                cs,
                warning_class="directional_support_with_caveats",
            )

    if primary:
        cs = _conditional_null_monitor_eligibility(primary, [])
        return _outcome(
            "aligned_agreement",
            "directional_support_with_caveats",
            "E-CONFLICT-001",
            "supported_with_limitations",
            cs,
        )

    return _outcome(
        "blocked_by_suitability",
        "blocked_by_geometry",
        "E-CONFLICT-004",
        "not_assessable",
        {"eligible": False},
    )


def _conditional_null_monitor_eligibility(
    primary: dict[str, Any],
    restricted: list[dict[str, Any]],
) -> dict[str, Any]:
    row_cs = primary.get("calibration_signal_eligibility") or {}
    eligible = bool(row_cs.get("eligible")) and primary.get("suitability_status") in {
        "suitable",
        "suitable_with_caveats",
    }
    return {
        "eligible": eligible,
        "strength": "conditional_weak" if eligible else None,
        "scope": "null_monitor_only",
        "lift_mmm_allowed": False,
        "mmm_ingress_allowed": False,
        "bind_requires": [
            "declared_estimand_id_match",
            "interval_semantics_match",
            "fresh_calibration_signal",
            "no_triangulation_conflict",
        ],
    }


def _outcome(
    agreement_state: str,
    disposition: str,
    conflict_class: str,
    trust_hint: str,
    cs: dict[str, Any],
    *,
    per_cell_dispositions: dict[str, str] | None = None,
    warning_class: str | None = None,
    exclusion_class: str | None = None,
) -> TriangulationOutcome:
    return TriangulationOutcome(
        agreement_state=agreement_state,
        trust_report_disposition=disposition,
        conflict_class=conflict_class,
        trust_outcome_hint=trust_hint,
        calibration_signal_eligibility=cs,
        per_cell_dispositions=per_cell_dispositions or {},
        warning_class=warning_class,
        exclusion_class=exclusion_class,
    )


def apply_e5_calibration_policy(outcome: TriangulationOutcome) -> dict[str, Any]:
    """Return normalized CalibrationSignal eligibility per E5."""
    disp = outcome.trust_report_disposition
    cs = dict(outcome.calibration_signal_eligibility)

    excluded_dispositions = {
        "restricted_method_positive_but_primary_null_compatible",
        "method_conflict_warning",
        "non_comparable_estimand",
        "blocked_by_geometry",
        "planning_diagnostic_only",
        "characterization_required",
        "missing_uncertainty_warning",
        "stale_downweight_or_exclude",
    }
    if disp in excluded_dispositions:
        cs.setdefault("eligible", False)
        cs.setdefault("lift_mmm_allowed", False)
        cs.setdefault("mmm_ingress_allowed", False)

    if disp == "cell_level_conflict":
        cs["eligible"] = False
        cs["pooled_allowed"] = False
        cs["lift_mmm_allowed"] = False
        cs["mmm_ingress_allowed"] = False

    if disp == "directional_support_with_caveats":
        cs.setdefault("scope", "null_monitor_only")
        cs.setdefault("lift_mmm_allowed", False)
        cs.setdefault("mmm_ingress_allowed", False)

    return cs


def assert_forbidden_actions(
    outcome: TriangulationOutcome,
    profile: dict[str, Any],
    forbidden_actions: list[str],
) -> list[str]:
    """Return list of violated forbidden action IDs (empty if pass)."""
    violations: list[str] = []
    cs = apply_e5_calibration_policy(outcome)
    rows = _rows(profile)

    if "no_averaging" in forbidden_actions or "no_silent_average" in forbidden_actions:
        if cs.get("combined_point_estimate") is not None:
            violations.append("no_averaging")

    if "no_pooled_multi_cell_claim" in forbidden_actions or "no_averaging_across_cells" in forbidden_actions:
        if profile.get("geometry_mode") == "multi_cell" and not profile.get("pooling_rule_id"):
            if cs.get("pooled_allowed") is True:
                violations.append("no_pooled_multi_cell_claim")

    if "no_mmm_lift_feed" in forbidden_actions or "no_mmm_feed" in forbidden_actions or "no_mmm_pooled_feed" in forbidden_actions:
        if cs.get("mmm_ingress_allowed") or cs.get("lift_mmm_allowed"):
            violations.append("no_mmm_feed")

    if "no_mmm_calibration_from_geo_mde" in forbidden_actions:
        if cs.get("mmm_mde_feed_forbidden") is False and cs.get("eligible") and _has_planning_diagnostic(rows):
            violations.append("no_mmm_calibration_from_geo_mde")

    if "no_lift_promotion_from_restricted" in forbidden_actions or "no_lift_claim" in forbidden_actions:
        if outcome.trust_outcome_hint == "supported" and any(
            r.get("evidence_role") == "restricted" for r in rows
        ):
            if outcome.trust_report_disposition != "directional_support_with_caveats":
                violations.append("no_lift_promotion_from_restricted")

    if "no_lift_claim" in forbidden_actions:
        if outcome.trust_report_disposition == "restricted_method_positive_but_primary_null_compatible":
            if cs.get("eligible"):
                violations.append("no_lift_claim")

    if "no_triangulation_lift_compare" in forbidden_actions:
        if outcome.trust_report_disposition == "blocked_by_geometry" and cs.get("eligible"):
            violations.append("no_triangulation_lift_compare")

    if "no_promotion" in forbidden_actions:
        if cs.get("lift_mmm_allowed"):
            violations.append("no_promotion")

    if "no_full_universe_claim" in forbidden_actions or "no_001e_transfer" in forbidden_actions:
        pass

    if "no_combined_estimate" in forbidden_actions or "no_agreement_narrative" in forbidden_actions:
        if cs.get("combined_signal_allowed") is True:
            violations.append("no_combined_estimate")

    restricted_positive = any(
        r.get("evidence_role") == "restricted" and _interval_excludes_zero(r) for r in rows
    )
    primary_null = any(
        r.get("evidence_role") == "primary" and _covers_zero(r) is True for r in rows
    )
    if "no_lift_promotion_from_restricted" in forbidden_actions and restricted_positive and primary_null:
        if outcome.trust_outcome_hint == "supported":
            violations.append("no_lift_promotion_from_restricted")

    return violations


def evaluate_e4_fixture(fixture: dict[str, Any]) -> TriangulationOutcome:
    profile = fixture["triangulation_profile"]
    outcome = evaluate_triangulation(profile)
    outcome = TriangulationOutcome(
        agreement_state=outcome.agreement_state,
        trust_report_disposition=outcome.trust_report_disposition,
        conflict_class=outcome.conflict_class,
        trust_outcome_hint=outcome.trust_outcome_hint,
        calibration_signal_eligibility=apply_e5_calibration_policy(outcome),
        per_cell_dispositions=outcome.per_cell_dispositions,
        warning_class=outcome.warning_class,
        exclusion_class=outcome.exclusion_class,
        forbidden_violations=tuple(
            assert_forbidden_actions(
                outcome,
                profile,
                fixture.get("forbidden_actions") or [],
            )
        ),
    )
    return outcome
