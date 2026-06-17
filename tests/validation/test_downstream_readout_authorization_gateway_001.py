"""Tests for DOWNSTREAM-READOUT-AUTHORIZATION-GATEWAY-001."""

from __future__ import annotations

import copy
import inspect
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from panel_exp.evidence import DesignEvidence, ReadoutEvidence
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.track_b.readout_evidence_wiring import (
    DOWNSTREAM_READOUT_NOT_AUTHORIZED,
    assert_trust_report_bundle_authorized,
    build_trust_report_decision_inputs_from_bundle,
    evaluate_bundle_downstream_authorization,
)
from panel_exp.validation.design_guardrail_enforcement_001 import build_producer_guardrail_bundle
from panel_exp.validation.estimator_readout_adapter_001 import (
    GOVERNED_READOUT_MARKER,
    build_estimator_readout,
)
from panel_exp.validation.downstream_readout_authorization_001 import (
    AUTHORIZATION_VERSION,
    DownstreamPromotionEvidence,
    DownstreamReadoutAuthorizationViolation,
    PRODUCTION_FACING_ROLES,
    RESEARCH_SAFE_ROLES,
    STATUS_BLOCKED,
    STATUS_RESTRICTED,
    assert_downstream_readout_authorized,
    evaluate_downstream_readout_authorization,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "artifact_schemas"
CONTRACT_DIR = FIXTURE_DIR / "design_contract_golden_001"
ESTIMATOR_SCENARIOS = json.loads(
    (FIXTURE_DIR / "estimator_readout_guardrail_integration_001" / "scenarios.json").read_text()
)
GATEWAY_SCENARIOS = json.loads(
    (FIXTURE_DIR / "downstream_readout_authorization_gateway_001" / "scenarios.json").read_text()
)

_TEMPLATE_TO_ESTIMATOR_FIXTURE: dict[str, str] = {
    "scm_jk": "scm_jk_research",
    "augsynth_point": "augsynth_point",
    "did_bootstrap": "did_bootstrap",
    "multicell_percell": "multicell_per_cell",
    "augsynth_interval": "augsynth_interval_blocked",
    "multicell_pooled": "multicell_pooled_blocked",
}


def _load_contract(name: str = "tier1_complete_randomization_contract.json") -> dict[str, Any]:
    return json.loads((CONTRACT_DIR / name).read_text())


def _design_evidence_from_contract(
    name: str = "tier1_complete_randomization_contract.json",
    *,
    design_override: str | None = None,
) -> DesignEvidence:
    payload = _load_contract(name)
    contract = dict(payload["design_contract"])
    validation = payload["contract_validation"]
    if design_override == "multicell_percell":
        identity = dict(contract.get("design_identity") or {})
        identity["design_inventory_id"] = "DES-011"
        contract["design_identity"] = identity
        geometry = dict(contract.get("geometry") or {})
        geometry["geometry_id"] = "multi_cell_per_cell"
        contract["geometry"] = geometry
        contract["multi_cell"] = {
            "is_multi_cell": True,
            "cell_ids": ["test_0", "test_1"],
            "shared_control_policy": "explicit_reservation",
            "control_reuse_policy": "per_cell_isolated",
            "pooled_claims_allowed": False,
        }
    bundle = build_producer_guardrail_bundle(
        design_contract=contract,
        contract_validation=validation,
    )
    spec = spec_from_geo_design(
        "gateway-test",
        "y",
        "unit",
        "time",
        pre_period=TimePeriod(0, 10),
        experiment_period=TimePeriod(10, 20),
        design_method="completerandomization",
        random_state=1,
        treatment_probability=0.5,
    )
    return DesignEvidence.from_assignment(
        spec,
        {"control": ["a", "b"], "test_0": ["c"]},
        design_contract=contract,
        contract_validation=validation,
        design_guardrail=bundle["design_guardrail"],
        combination_guardrail=bundle["combination_guardrail"],
        guardrail_enforcement=bundle["guardrail_enforcement"],
    )


def _build_estimator_scenario(fixture_id: str, *, enforce: bool = True) -> ReadoutEvidence:
    scenario = next(s for s in ESTIMATOR_SCENARIOS if s["fixture_id"] == fixture_id)
    design_ev = _design_evidence_from_contract(
        scenario.get("design_contract", "tier1_complete_randomization_contract.json"),
        design_override=scenario.get("design_override"),
    )
    if scenario.get("geometry_id"):
        contract = dict(design_ev.design_contract or {})
        geometry = dict(contract.get("geometry") or {})
        geometry["geometry_id"] = scenario["geometry_id"]
        contract["geometry"] = geometry
        design_ev = DesignEvidence.from_dict({**design_ev.to_dict(), "design_contract": contract})
    return build_estimator_readout(
        design_evidence=design_ev,
        estimator_id=scenario.get("estimator_id"),
        inference_id=scenario.get("inference_id"),
        result_payload=scenario.get("native"),
        readout_semantics=scenario.get("readout_semantics"),
        interval_type=scenario.get("interval_type"),
        cell_id=scenario.get("cell_id"),
        pooled=bool(scenario.get("pooled", False)),
        requested_role="research",
        enforce=enforce,
    )


def _build_gateway_readout(scenario: dict[str, Any]) -> ReadoutEvidence | None:
    if scenario.get("readout") is None and not scenario.get("template") and not scenario.get("native"):
        return None
    if scenario.get("native"):
        return scenario["native"]  # type: ignore[return-value]
    template = scenario.get("template")
    if not template:
        return None
    fixture_id = _TEMPLATE_TO_ESTIMATOR_FIXTURE[template]
    enforce = template not in ("augsynth_interval", "multicell_pooled")
    readout = _build_estimator_scenario(fixture_id, enforce=enforce)
    if scenario.get("strip_marker"):
        payload = dict(readout.result_payload or {})
        meta = dict(payload.get("metadata") or {})
        meta.pop(GOVERNED_READOUT_MARKER, None)
        payload["metadata"] = meta
        readout = ReadoutEvidence.from_dict(
            {**readout.to_dict(), "result_payload": payload}
        )
    if scenario.get("invalid_marker"):
        payload = dict(readout.result_payload or {})
        meta = dict(payload.get("metadata") or {})
        meta[GOVERNED_READOUT_MARKER] = False
        payload["metadata"] = meta
        readout = ReadoutEvidence.from_dict(
            {**readout.to_dict(), "result_payload": payload}
        )
    if scenario.get("strip_boundary"):
        readout = ReadoutEvidence.from_dict(
            {**readout.to_dict(), "inference_boundary_guardrail": None}
        )
    return readout


def _valid_promotion(**overrides: Any) -> DownstreamPromotionEvidence:
    base = {
        "artifact_id": "PROMO-TEST-001",
        "status": "approved",
        "approved_roles": tuple(RESEARCH_SAFE_ROLES),
        "approved_dcm_rows": ("DCM-001", "DCM-002", "DCM-004", "DCM-006"),
        "approved_estimators": ("scm", "augsynth", "did"),
        "approved_inference_paths": ("unit_jackknife", "point_only", "bootstrap"),
        "approved_readout_semantics": (
            "causal_interval",
            "point_estimate",
            "per_cell_point",
        ),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "evidence_version": "1.0.0",
    }
    base.update(overrides)
    return DownstreamPromotionEvidence(**base)


@pytest.mark.parametrize("scenario", GATEWAY_SCENARIOS, ids=lambda s: s["fixture_id"])
def test_gateway_fixture_scenarios(scenario: dict[str, Any]) -> None:
    if scenario.get("legacy_bundle"):
        bundle = {
            "evidence": {
                "inference_metadata": {
                    "estimator_name": "SCM",
                    "inference_mode": "UnitJackKnife",
                },
                "track_b_export_hints": {"run_status": "success"},
            }
        }
        result = evaluate_bundle_downstream_authorization(bundle, requested_role="trust_report")
        assert result["status"] == scenario["expected_status"]
        assert result["authorized"] is False
        return

    readout = _build_gateway_readout(scenario)
    promotion = scenario.get("promotion")
    if promotion is not None and promotion != "valid":
        promo_arg: Any = promotion
    elif promotion == "valid":
        promo_arg = _valid_promotion()
    else:
        promo_arg = None

    result = evaluate_downstream_readout_authorization(
        readout_evidence=readout,
        requested_role=scenario["requested_role"],
        promotion_evidence=promo_arg,
    )
    assert result.status == scenario["expected_status"]
    assert result.authorized is scenario.get("expected_authorized", False)
    if scenario.get("expect_role_code"):
        assert scenario["expect_role_code"] in result.reason_codes


class TestGovernedReadoutValidation:
    def test_valid_governed_marker_recognized(self) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="research",
        )
        assert result.governed_readout_present is True
        assert result.governed_readout_valid is True

    def test_missing_marker_blocked(self) -> None:
        readout = _build_gateway_readout({"template": "scm_jk", "strip_marker": True})
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="research",
        )
        assert result.status == STATUS_BLOCKED
        assert "D-AUTH-MISSING-GOVERNED-MARKER" in result.reason_codes

    def test_invalid_marker_blocked(self) -> None:
        readout = _build_gateway_readout({"template": "scm_jk", "invalid_marker": True})
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="research",
        )
        assert result.status == STATUS_BLOCKED
        assert "D-AUTH-INVALID-GOVERNED-MARKER" in result.reason_codes

    def test_missing_boundary_blocked(self) -> None:
        readout = _build_gateway_readout({"template": "scm_jk", "strip_boundary": True})
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="research",
        )
        assert result.status == STATUS_BLOCKED
        assert "D-AUTH-MISSING-INFERENCE-BOUNDARY" in result.reason_codes

    def test_native_result_dict_blocked(self) -> None:
        result = evaluate_downstream_readout_authorization(
            readout_evidence={"y": [1, 2], "y_hat": [1, 1]},
            requested_role="research",
        )
        assert result.status == STATUS_BLOCKED
        assert "D-AUTH-LEGACY-NATIVE-RESULT" in result.reason_codes


class TestRoleAuthorization:
    @pytest.mark.parametrize("role", sorted(RESEARCH_SAFE_ROLES))
    def test_research_safe_restricted(self, role: str) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role=role,
        )
        assert result.status == STATUS_RESTRICTED
        assert result.authorized is False
        assert_downstream_readout_authorized(result, requested_role=role)

    @pytest.mark.parametrize(
        "role,code",
        [
            ("trust_report", "D-AUTH-TRUSTREPORT-BLOCKED"),
            ("calibration_signal", "D-AUTH-CALIBRATION-SIGNAL-BLOCKED"),
            ("mmm_calibration", "D-AUTH-MMM-BLOCKED"),
            ("llm_decision_support", "D-AUTH-LLM-BLOCKED"),
            ("production_recommendation", "D-AUTH-PRODUCTION-RECOMMENDATION-BLOCKED"),
            ("automated_budget_action", "D-AUTH-AUTOMATED-BUDGET-ACTION-BLOCKED"),
            ("external_export", "D-AUTH-EXTERNAL-EXPORT-BLOCKED"),
        ],
    )
    def test_production_roles_blocked(self, role: str, code: str) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role=role,
        )
        assert result.status == STATUS_BLOCKED
        assert code in result.reason_codes
        with pytest.raises(DownstreamReadoutAuthorizationViolation) as exc:
            assert_downstream_readout_authorized(result, requested_role=role)
        assert exc.value.result is result


class TestPromotionEvidence:
    def test_missing_promotion_blocked_for_production(self) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="trust_report",
        )
        assert "D-AUTH-MISSING-PROMOTION-EVIDENCE" in result.reason_codes
        assert result.status == STATUS_BLOCKED

    def test_malformed_promotion_blocked(self) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="trust_report",
            promotion_evidence={"artifact_id": "", "status": ""},
        )
        assert "D-AUTH-PROMOTION-NOT-APPROVED" in result.reason_codes

    def test_expired_promotion_blocked(self) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        promo = _valid_promotion(
            expires_at=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        )
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="trust_report",
            promotion_evidence=promo,
        )
        assert "D-AUTH-PROMOTION-NOT-APPROVED" in result.reason_codes
        assert result.status == STATUS_BLOCKED

    def test_role_mismatch_blocked(self) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        promo = _valid_promotion(approved_roles=("diagnostic",))
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="validation",
            promotion_evidence=promo,
        )
        assert "D-AUTH-ROLE-NOT-APPROVED" in result.reason_codes

    def test_no_fixture_produces_production_authorization(self) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        promo = _valid_promotion(approved_roles=tuple(PRODUCTION_FACING_ROLES))
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="trust_report",
            promotion_evidence=promo,
        )
        assert result.authorized is False
        assert result.status == STATUS_BLOCKED


class TestTrackBIntegration:
    def test_governed_bundle_receives_authorization_block(self) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        bundle = {"evidence": {"readout_evidence": readout.to_dict()}}
        inputs = build_trust_report_decision_inputs_from_bundle(bundle)
        assert inputs.downstream_authorization is not None
        assert inputs.downstream_authorization["status"] == STATUS_BLOCKED
        assert inputs.trust_report_ready is False

    def test_ungoverned_bundle_fails_closed(self) -> None:
        bundle = {
            "evidence": {
                "inference_metadata": {
                    "estimator_name": "SCM",
                    "inference_mode": "UnitJackKnife",
                }
            }
        }
        inputs = build_trust_report_decision_inputs_from_bundle(bundle)
        assert any(DOWNSTREAM_READOUT_NOT_AUTHORIZED in w for w in inputs.extraction_warnings)
        assert inputs.trust_report_ready is False

    def test_legacy_bundle_loads_unauthorized(self) -> None:
        bundle = {
            "evidence": {
                "inference_metadata": {"estimator_name": "SCM"},
                "track_b_export_hints": {GOVERNED_READOUT_MARKER: True},
            }
        }
        inputs = build_trust_report_decision_inputs_from_bundle(bundle)
        assert inputs.downstream_authorization is not None
        assert inputs.downstream_authorization["authorized"] is False

    def test_assert_trust_report_raises(self) -> None:
        bundle = {"evidence": {"inference_metadata": {"estimator_name": "SCM"}}}
        with pytest.raises(DownstreamReadoutAuthorizationViolation):
            assert_trust_report_bundle_authorized(bundle)


class TestSerialization:
    def test_result_json_serializable(self) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="research",
        )
        payload = result.to_dict()
        roundtrip = json.loads(json.dumps(payload))
        assert roundtrip["authorization_version"] == AUTHORIZATION_VERSION
        assert roundtrip["status"] == STATUS_RESTRICTED

    def test_deterministic_result(self) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        a = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="research",
        )
        b = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="research",
        )
        assert a.to_dict() == b.to_dict()


class TestSecurity:
    def test_no_bypass_in_gateway(self) -> None:
        src = inspect.getsource(evaluate_downstream_readout_authorization)
        assert "force=True" not in src
        assert "override_authorization" not in src
        assert "bypass_authorization" not in src
        assert "ignore_authorization" not in src

    def test_exception_preserves_result(self) -> None:
        readout = _build_estimator_scenario("scm_jk_research")
        result = evaluate_downstream_readout_authorization(
            readout_evidence=readout,
            requested_role="trust_report",
        )
        with pytest.raises(DownstreamReadoutAuthorizationViolation) as exc:
            assert_downstream_readout_authorized(result, requested_role="trust_report")
        assert exc.value.result.reason_codes == result.reason_codes
