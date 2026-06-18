"""Tests for DCM-005 TrustReport eligibility reassessment core logic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import load_registry
from panel_exp.validation.dcm005_trustreport_eligibility_reassessment_001 import (
    INV_BRB,
    INV_KFOLD,
    INV_PLACEBO,
    RC_AUTH_BLOCKED,
    RC_BRB_CAUSAL_BLOCKED,
    RC_BRB_CENTERING,
    RC_KFOLD_DIAG,
    RC_PLACEBO_NULL,
    REMEDIATION_ARTIFACT_BRB,
    load_dcm005_evidence,
    reassess_dcm005_trustreport_eligibility,
)

_REPO = Path(__file__).resolve().parents[2]
_ARCHIVE = _REPO / "docs/track_d/archives"
_PRIOR = _ARCHIVE / "TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"


@pytest.fixture(scope="module")
def evidence() -> dict:
    return load_dcm005_evidence(
        brb_summary=json.loads((_ARCHIVE / "D5_TRUST_TBRRIDGE_BRB_001_summary.json").read_text()),
        brb_correction_summary=json.loads(
            (_ARCHIVE / "TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json").read_text()
        ),
        kfold_summary=json.loads((_ARCHIVE / "D5_TRUST_TBRRIDGE_KFOLD_001_summary.json").read_text()),
        placebo_summary=json.loads(
            (_ARCHIVE / "D5_TRUST_TBRRIDGE_PLACEBO_001_summary.json").read_text()
        ),
    )


@pytest.fixture(scope="module")
def prior_brb() -> dict:
    prior = json.loads(_PRIOR.read_text())
    return next(r for r in prior["combination_results"] if r["combination_key"] == "DCM-005-BRB")


@pytest.fixture(scope="module")
def registry_inv() -> dict[str, dict]:
    reg = load_registry()
    return {i["investigation_id"]: i for i in reg["investigations"]}


class TestDCM005ReassessmentCore:
    def test_load_evidence_brb_metrics(self, evidence: dict) -> None:
        assert evidence["brb"]["centering_corrected"] is True
        assert (evidence["brb"]["type_i_error"] or 0) > 0.5
        assert (evidence["brb"]["variance_ratio"] or 0) > 10

    def test_load_evidence_kfold_sign_failure(self, evidence: dict) -> None:
        assert (evidence["kfold"]["sign_accuracy_positive"] or 1) < 0.05
        assert evidence["kfold"]["leakage_flagged"] is False

    def test_load_evidence_placebo_null_monitor(self, evidence: dict) -> None:
        assert evidence["placebo"]["type_i_null"] == 0.0
        assert "one treated unit" in " ".join(evidence["placebo"]["failure_reasons"]).lower()

    def test_reassess_path_decisions(self, evidence: dict, prior_brb: dict, registry_inv: dict) -> None:
        result = reassess_dcm005_trustreport_eligibility(
            prior_eligibility_result=prior_brb,
            path_evidence=evidence,
            registry_investigations=registry_inv,
        )
        assert result.dcm_row_id == "DCM-005"
        assert len(result.path_decisions) == 3
        assert result.trust_report_authorized is False
        assert result.eligible_for_promotion is False
        assert result.aggregate_status == "MIXED_WITH_TERMINAL_PATH_DECISIONS"

    def test_brb_path_deferred_remediation(self, evidence: dict, prior_brb: dict, registry_inv: dict) -> None:
        result = reassess_dcm005_trustreport_eligibility(
            prior_eligibility_result=prior_brb,
            path_evidence=evidence,
            registry_investigations=registry_inv,
        )
        brb = next(p for p in result.path_decisions if p.path_id == "DCM-005-BRB")
        assert brb.statistical_status == "DEFERRED_FOR_REMEDIATION"
        assert brb.trustreport_eligibility_status == "INELIGIBLE_FOR_CAUSAL_INTERVAL"
        assert brb.investigation_disposition == "REMEDIATE"
        assert RC_BRB_CENTERING in brb.reason_codes
        assert RC_BRB_CAUSAL_BLOCKED in brb.reason_codes
        assert REMEDIATION_ARTIFACT_BRB in " ".join(brb.restrictions)

    def test_kfold_diagnostic_only(self, evidence: dict, prior_brb: dict, registry_inv: dict) -> None:
        result = reassess_dcm005_trustreport_eligibility(
            prior_eligibility_result=prior_brb,
            path_evidence=evidence,
            registry_investigations=registry_inv,
        )
        kf = next(p for p in result.path_decisions if p.path_id == "DCM-005-KFOLD")
        assert kf.semantic_class == "DIAGNOSTIC_ONLY"
        assert kf.investigation_disposition == "DIAGNOSTIC_ONLY"
        assert RC_KFOLD_DIAG in kf.reason_codes

    def test_placebo_null_monitor(self, evidence: dict, prior_brb: dict, registry_inv: dict) -> None:
        result = reassess_dcm005_trustreport_eligibility(
            prior_eligibility_result=prior_brb,
            path_evidence=evidence,
            registry_investigations=registry_inv,
        )
        pl = next(p for p in result.path_decisions if p.path_id == "DCM-005-PLACEBO")
        assert pl.semantic_class == "NULL_MONITOR_ONLY"
        assert pl.investigation_disposition == "NULL_MONITOR_ONLY"
        assert RC_PLACEBO_NULL in pl.reason_codes

    def test_investigation_handoff_consumption(self, evidence: dict, prior_brb: dict, registry_inv: dict) -> None:
        result = reassess_dcm005_trustreport_eligibility(
            prior_eligibility_result=prior_brb,
            path_evidence=evidence,
            registry_investigations=registry_inv,
        )
        handoff = result.investigation_handoff
        assert INV_KFOLD in handoff["resolved_issues"]
        assert INV_PLACEBO in handoff["resolved_issues"]
        assert INV_BRB in handoff["follow_up_issues"]
        assert len(handoff["terminal_dispositions"]) == 2

    def test_missing_registry_investigation_fails(self, evidence: dict, prior_brb: dict) -> None:
        with pytest.raises(ValueError, match="missing required investigations"):
            reassess_dcm005_trustreport_eligibility(
                prior_eligibility_result=prior_brb,
                path_evidence=evidence,
                registry_investigations={},
            )

    def test_unauthorized_evidence_fails_closed(self, evidence: dict) -> None:
        bad = dict(evidence)
        bad_summary = json.loads((_ARCHIVE / "D5_TRUST_TBRRIDGE_BRB_001_summary.json").read_text())
        bad_summary["authorization_summary"] = {"trust_report_authorized": True}
        with pytest.raises(ValueError, match="unexpectedly authorizes"):
            load_dcm005_evidence(
                brb_summary=bad_summary,
                brb_correction_summary=json.loads(
                    (_ARCHIVE / "TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json").read_text()
                ),
                kfold_summary=json.loads(
                    (_ARCHIVE / "D5_TRUST_TBRRIDGE_KFOLD_001_summary.json").read_text()
                ),
                placebo_summary=json.loads(
                    (_ARCHIVE / "D5_TRUST_TBRRIDGE_PLACEBO_001_summary.json").read_text()
                ),
            )

    def test_all_paths_have_auth_blocked(self, evidence: dict, prior_brb: dict, registry_inv: dict) -> None:
        result = reassess_dcm005_trustreport_eligibility(
            prior_eligibility_result=prior_brb,
            path_evidence=evidence,
            registry_investigations=registry_inv,
        )
        for path in result.path_decisions:
            assert RC_AUTH_BLOCKED in path.reason_codes
            assert path.trust_report_authorized is False
