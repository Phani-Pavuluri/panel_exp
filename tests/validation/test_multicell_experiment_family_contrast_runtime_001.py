"""Tests for MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.multicell_experiment_family_contrast_runtime_001 import (
    MulticellExperimentFamilyContrastReviewPacket,
    _AUTH_FALSE,
    _POSITIVE_FLAGS,
    build_multicell_contrast_eligibility_packet,
    evaluate_multicell_readout_surface,
    generate_multicell_experiment_family_contrast_review,
    get_runtime_metadata,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001_REPORT.md"


def _standalone_evidence(**extra: object) -> dict:
    payload = {
        "request_id": "runtime_test",
        "arm_ids": ["arm_1"],
        "common_estimand": "geo.relative_att_post",
        "trusted_readout_report": {"status": "ready"},
        "requested_surface": "STANDALONE_ARM_READOUT",
    }
    payload.update(extra)
    return payload


def test_public_api_exists() -> None:
    report = generate_multicell_experiment_family_contrast_review(_standalone_evidence())
    assert isinstance(report, MulticellExperimentFamilyContrastReviewPacket)
    alias = evaluate_multicell_readout_surface(_standalone_evidence(request_id="alias"))
    assert alias.review_id == build_multicell_contrast_eligibility_packet(
        _standalone_evidence(request_id="alias")
    ).review_id


def test_dict_input_supported() -> None:
    report = generate_multicell_experiment_family_contrast_review(_standalone_evidence())
    assert report.request_id == "runtime_test"
    assert report.allowed_surface is True


@dataclass
class _InputLike:
    request_id: str
    arm_ids: list[str]
    common_estimand: str
    trusted_readout_report: dict
    requested_surface: str


def test_dataclass_like_input_supported() -> None:
    obj = _InputLike(
        request_id="dc_001",
        arm_ids=["a1"],
        common_estimand="att",
        trusted_readout_report={"status": "ready"},
        requested_surface="STANDALONE_ARM_READOUT",
    )
    report = generate_multicell_experiment_family_contrast_review(obj)
    assert report.request_id == "dc_001"
    assert report.allowed_surface is True


def test_list_input_returns_multiple_packets_without_ranking() -> None:
    packets = generate_multicell_experiment_family_contrast_review(
        [
            _standalone_evidence(request_id="list_a", arm_ids=["a"]),
            _standalone_evidence(request_id="list_b", arm_ids=["b"]),
        ]
    )
    assert isinstance(packets, list)
    assert len(packets) == 2
    assert packets[0].request_id == "list_a"
    assert packets[1].request_id == "list_b"
    assert packets[0].review_id != packets[1].review_id


def test_independent_experiments_allow_standalone_without_multiplicity() -> None:
    report = generate_multicell_experiment_family_contrast_review(
        {
            "request_id": "indep",
            "experiment_ids": ["e1", "e2"],
            "platform": ["meta", "google"],
            "arm_ids": ["arm_meta"],
            "common_estimand": "att",
            "trusted_readout_report": {"ok": True},
            "requested_surface": "STANDALONE_ARM_READOUT",
        }
    )
    assert report.experiment_family == "INDEPENDENT_EXPERIMENTS"
    assert report.allowed_surface is True
    assert report.multiplicity_required is False
    assert report.covariance_semantics_required is False


def test_independent_experiments_block_winner_claim() -> None:
    report = generate_multicell_experiment_family_contrast_review(
        {
            "request_id": "indep_winner",
            "experiment_ids": ["e1", "e2"],
            "platform": ["meta", "google"],
            "requested_surface": "WINNER_CLAIM",
        }
    )
    assert report.blocked_surface is True
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "WINNER_CLAIM_BLOCKED"


def test_related_arms_require_contrast_definitions() -> None:
    report = generate_multicell_experiment_family_contrast_review(
        {
            "request_id": "related",
            "arm_ids": ["a", "b"],
            "planned_cross_arm_comparisons": ["a_vs_b"],
            "experiment_family_id": "fam",
            "common_estimand": "att",
            "shared_metric": "rev",
            "multiplicity_policy": {"method": "holm"},
            "requested_surface": "ARM_COMPARISON",
            "trusted_readout_report": {"ok": True},
        }
    )
    assert report.experiment_family == "RELATED_PARALLEL_ARMS"
    assert report.blocked_surface is True
    assert "contrast_definition" in report.missing_evidence


def test_related_arms_require_multiplicity_policy_for_arm_comparison() -> None:
    report = generate_multicell_experiment_family_contrast_review(
        {
            "request_id": "related_no_mult",
            "arm_ids": ["a", "b"],
            "planned_cross_arm_comparisons": ["a_vs_b"],
            "experiment_family_id": "fam",
            "common_estimand": "att",
            "shared_metric": "rev",
            "contrast_definitions": {"a_vs_b": {}},
            "requested_surface": "ARM_COMPARISON",
            "trusted_readout_report": {"ok": True},
        }
    )
    assert report.blocked_surface is True
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "MISSING_MULTIPLICITY_POLICY"


def test_shared_control_multi_arm_requires_covariance_semantics() -> None:
    report = generate_multicell_experiment_family_contrast_review(
        {
            "request_id": "shared_ctrl",
            "shared_control_group": "control_pool",
            "arm_ids": ["a", "b"],
            "planned_cross_arm_comparisons": ["a_vs_b"],
            "experiment_family_id": "fam",
            "common_estimand": "att",
            "shared_metric": "rev",
            "contrast_definitions": {"a_vs_b": {}},
            "multiplicity_policy": {"method": "holm"},
            "requested_surface": "ARM_COMPARISON",
            "trusted_readout_report": {"ok": True},
        }
    )
    assert report.experiment_family == "SHARED_CONTROL_MULTI_ARM"
    assert report.covariance_semantics_required is True
    assert report.blocked_surface is True
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "MISSING_SHARED_CONTROL_COVARIANCE_SEMANTICS"


def test_dose_response_family_requires_dose_semantics() -> None:
    report = generate_multicell_experiment_family_contrast_review(
        {
            "request_id": "dose",
            "experiment_family": "DOSE_RESPONSE_FAMILY",
            "arm_ids": ["low", "high"],
            "requested_surface": "DOSE_RESPONSE_SUMMARY",
        }
    )
    assert report.blocked_surface is True
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] in (
        "MISSING_DOSE_RESPONSE_SEMANTICS",
        "MISSING_MULTIPLICITY_POLICY",
        "COMPARATIVE_SURFACE_NOT_AUTHORIZED",
    )


def test_pooled_global_summary_requires_pooling_and_heterogeneity() -> None:
    report = generate_multicell_experiment_family_contrast_review(
        {
            "request_id": "pooled",
            "pooling_requested": True,
            "arm_ids": ["c1", "c2"],
            "requested_surface": "POOLED_EFFECT_SUMMARY",
            "pooling_weights": {"c1": 0.5, "c2": 0.5},
        }
    )
    assert report.experiment_family == "POOLED_AGGREGATE_FAMILY"
    assert report.blocked_surface is True
    assert "heterogeneity_diagnostics" in report.missing_evidence


def test_portfolio_ranking_requires_comparable_estimands() -> None:
    report = generate_multicell_experiment_family_contrast_review(
        {
            "request_id": "portfolio",
            "decision_family_id": "budget_q1",
            "experiment_ids": ["e1", "e2"],
            "platform": ["meta", "google"],
            "requested_surface": "PORTFOLIO_RANKING_REVIEW",
            "lineage_manifest": {"sources": ["e1", "e2"]},
        }
    )
    assert report.experiment_family == "PORTFOLIO_DECISION_FAMILY"
    assert report.blocked_surface is True
    assert "comparable_estimands" in report.missing_evidence


def test_unknown_family_blocks_comparative_surface() -> None:
    report = generate_multicell_experiment_family_contrast_review(
        {"request_id": "unknown", "requested_surface": "ARM_COMPARISON"}
    )
    assert report.experiment_family == "UNKNOWN_FAMILY_REQUIRES_REVIEW"
    assert report.blocked_surface is True
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "UNKNOWN_EXPERIMENT_FAMILY"


def test_winner_and_scale_budget_claims_blocked() -> None:
    winner = generate_multicell_experiment_family_contrast_review(
        {"request_id": "w", "arm_ids": ["a"], "requested_surface": "WINNER_CLAIM"}
    )
    budget = generate_multicell_experiment_family_contrast_review(
        {"request_id": "b", "arm_ids": ["a"], "requested_surface": "SCALE_BUDGET_CLAIM"}
    )
    assert winner.blocked_surface is True
    assert budget.blocked_surface is True
    assert winner.failure_packet["failure_code"] == "WINNER_CLAIM_BLOCKED"
    assert budget.failure_packet["failure_code"] == "BUDGET_SCALE_CLAIM_BLOCKED"


def test_deterministic_review_id_and_provenance_hash() -> None:
    payload = _standalone_evidence(request_id="det")
    a = generate_multicell_experiment_family_contrast_review(payload)
    b = generate_multicell_experiment_family_contrast_review(payload)
    assert a.review_id == b.review_id
    assert a.provenance_hash == b.provenance_hash
    assert a.review_id.startswith("mefcr-")


def test_all_forbidden_computation_authorization_flags_false() -> None:
    meta = get_runtime_metadata()
    for flag, expected in _AUTH_FALSE.items():
        assert meta[flag] is expected, flag
    report = generate_multicell_experiment_family_contrast_review(_standalone_evidence())
    for flag, expected in _AUTH_FALSE.items():
        assert report.authorization_boundary_report[flag] is expected, flag


def test_positive_flags_true() -> None:
    meta = get_runtime_metadata()
    for flag, expected in _POSITIVE_FLAGS.items():
        assert meta[flag] is expected, flag


def test_summary_json_exists() -> None:
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001"
    assert data["runtime_implemented"] is True
    assert data["final_verdict"] == (
        "multicell_experiment_family_and_contrast_runtime_implemented_no_multiplicity_or_inference_computation"
    )


def test_report_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert "independent-experiment" in text.lower()


def test_run_validation_passes() -> None:
    result = run_validation(write_summary=False)
    assert result["failed_scenarios"] == []
