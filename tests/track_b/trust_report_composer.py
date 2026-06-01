"""Track B contract TrustReport composer (B5c test oracle wrapper).

Delegates to production ``panel_exp.track_b.trust_report``; golden fixtures
remain the test oracle.
"""

from __future__ import annotations

from typing import Any

from panel_exp.track_b.trust_report import (
    TrustComposeContext,
    TrustReportComposition,
    TrustScenarioVerdict,
    compose_trust_report as _compose_trust_report,
    compose_trust_scenario_verdict as _compose_trust_scenario_verdict,
    trust_report_to_dict as _trust_report_to_dict,
)
from tests.track_b.contract_fixtures import FixtureCase, TRUST_VERDICT_FIELDS

def _context_from_case(case: FixtureCase) -> TrustComposeContext:
    tr = case.trust_report_expected_output
    return TrustComposeContext(
        spec=case.spec,
        adapter_output=case.adapter_expected_output,
        calibration_signal_binding=case.calibration_signal_binding,
        composition_permitted=tr.get("composition_permitted", True) is not False,
        alignment_reference_estimand_id=tr.get("alignment_reference_estimand_id"),
    )


def compose_trust_scenario_verdict(
    case: FixtureCase,
    scenario: dict[str, Any],
) -> TrustScenarioVerdict:
    return _compose_trust_scenario_verdict(_context_from_case(case), scenario)


def compose_trust_report(case: FixtureCase) -> TrustReportComposition:
    tr_out = case.trust_report_expected_output
    scenarios_cfg = tr_out.get("scenarios") or []
    return _compose_trust_report(_context_from_case(case), scenarios_cfg)


def trust_report_to_dict(composition: TrustReportComposition) -> dict[str, Any]:
    d = _trust_report_to_dict(composition)
    # Fixture oracles omit trust_report_version; strip for comparison helpers.
    return {k: v for k, v in d.items() if k != "trust_report_version"}


def assert_composition_has_only_trust_verdict_fields(
    composition: TrustReportComposition,
) -> None:
    d = trust_report_to_dict(composition)
    for key in d:
        if key == "scenarios":
            continue
        assert key not in TRUST_VERDICT_FIELDS, f"root must not contain {key}"
    for scenario in d["scenarios"]:
        assert "alignment_verdict" in scenario
        assert "trust_outcome" in scenario
