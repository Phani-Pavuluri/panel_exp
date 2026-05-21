"""Tests for human-readable experiment card artifacts."""

from __future__ import annotations

from panel_exp.artifacts.experiment_card import (
    CARD_VERSION,
    attach_experiment_card_markdown,
    build_experiment_card,
)
from panel_exp.design.validation import ValidationCheck, ValidationStatus
from panel_exp.evidence import DesignEvidence, ExperimentEvidence
from panel_exp.inference_result import InferenceResult, IntervalType
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import InterferenceAssumption, spec_from_geo_design


def _spec(**kwargs):
    defaults = dict(
        experiment_id="exp-card-1",
        outcome_column="y",
        unit_column="u",
        time_column="t",
        pre_period=TimePeriod(0, 10),
        experiment_period=TimePeriod(10, 30),
        design_method="balancedrandomization",
        random_state=7,
        interference=InterferenceAssumption.NO_INTERFERENCE,
    )
    defaults.update(kwargs)
    return spec_from_geo_design(**defaults)


def _validation_with_interference() -> dict:
    check = ValidationCheck(
        metric="interference_assumption",
        status=ValidationStatus.PASS,
        threshold=None,
        value=None,
        message="No interference declared for this design.",
        blocking=False,
    )
    return {
        "status": "PASS",
        "blocking_failures": [],
        "checks": [check.to_dict()],
    }


def _full_experiment_evidence() -> ExperimentEvidence:
    spec = _spec()
    assignment = {"control": ["u0", "u1"], "test_0": ["u2"]}
    ir = InferenceResult.for_path_intervals(
        method="UnitJackKnife",
        alpha=0.05,
        path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
    )
    return ExperimentEvidence.build(
        spec,
        assignment,
        validation_summary=_validation_with_interference(),
        inference_result=ir,
        inference_method="UnitJackKnife",
        warnings=["Pre-period fit is short."],
        errors=[],
        created_at="2026-05-20T12:00:00+00:00",
        artifacts={
            "validation_metadata": {
                "validation_scenarios_run": ["scm_low_signal"],
                "validation_bias": {"scm_low_signal": 0.01},
            }
        },
    )


def test_builds_from_full_experiment_evidence():
    ev = _full_experiment_evidence()
    card = build_experiment_card(ev)
    assert card.experiment_id == "exp-card-1"
    assert card.design_name == "balanced_randomization"
    assert card.inference_mode == "UnitJackKnife"
    assert card.interval_type == "confidence_interval"
    assert card.intervals_available is True
    assert card.assignment_summary == {"control": 2, "test_0": 1}
    assert card.card_version == CARD_VERSION


def test_builds_from_design_only_evidence():
    spec = _spec(interference=InterferenceAssumption.UNKNOWN)
    assignment = {"control": ["a"], "test_0": ["b"]}
    ev = DesignEvidence.from_assignment(
        spec,
        assignment,
        validation_summary=_validation_with_interference(),
        warnings=["interference is unknown"],
        created_at="2026-05-20T12:00:00+00:00",
    )
    card = build_experiment_card(ev)
    assert card.experiment_id == "exp-card-1"
    assert card.inference_mode == "unknown"
    assert card.estimator_maturity == "unknown"
    assert card.interval_type == "unknown"
    assert card.intervals_available is None


def test_missing_optional_inference_fields_do_not_crash():
    spec = _spec()
    ev = DesignEvidence.from_assignment(spec, {"control": ["x"], "test_0": ["y"]})
    card = build_experiment_card(ev)
    md = card.to_markdown()
    assert "# Experiment Card" in md
    assert card.estimator_name == "unknown"


def test_warnings_prominent_in_markdown():
    ev = _full_experiment_evidence()
    md = build_experiment_card(ev).to_markdown()
    assert "## Warnings and Limitations" in md
    assert "**WARNING:** Pre-period fit is short." in md
    assert "does not establish causal validity" in md


def test_interference_in_markdown():
    ev = _full_experiment_evidence()
    md = build_experiment_card(ev).to_markdown()
    assert "## Interference Assumptions" in md
    assert "No interference declared" in md


def test_estimator_maturity_in_markdown():
    spec = _spec()
    assignment = {"control": ["u0"], "test_0": ["u1"]}
    ev = DesignEvidence.from_assignment(
        spec,
        assignment,
        inference_metadata={
            "estimator_maturity": "expert_review",
            "inference_mode_maturity": "expert_review",
            "estimator_name": "TBRRidge",
        },
        created_at="2026-05-20T12:00:00+00:00",
    )
    md = build_experiment_card(ev).to_markdown()
    assert "expert_review" in md
    assert "TBRRidge" in md


def test_lineage_hashes_in_markdown():
    ev = _full_experiment_evidence()
    card = build_experiment_card(ev)
    md = card.to_markdown()
    assert "## Lineage" in md
    assert card.spec_hash in md
    assert card.assignment_hash in md
    assert card.input_structure_hash in md or "unknown" in md


def test_to_dict_deterministic_except_created_at():
    ev = _full_experiment_evidence()
    c1 = build_experiment_card(ev).to_dict()
    c2 = build_experiment_card(ev).to_dict()
    d1 = {k: v for k, v in c1.items() if k != "created_at"}
    d2 = {k: v for k, v in c2.items() if k != "created_at"}
    assert d1 == d2
    assert c1["created_at"] == c2["created_at"]


def test_evidence_not_mutated():
    ev = _full_experiment_evidence()
    before = ev.to_json()
    before_assign_id = id(ev.assignment)
    _ = build_experiment_card(ev)
    after = ev.to_json()
    assert before == after
    assert id(ev.assignment) == before_assign_id


def test_attach_experiment_card_markdown_additive():
    ev = _full_experiment_evidence()
    artifacts: dict = {"existing": True}
    md = attach_experiment_card_markdown(artifacts, ev)
    assert "experiment_card_markdown" in artifacts
    assert artifacts["experiment_card_markdown"] == md
    assert artifacts["existing"] is True
    assert "experiment_card_markdown" not in ev.to_dict().get("artifacts", {})


def test_errors_in_markdown():
    spec = _spec()
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["a"], "test_0": ["b"]},
        errors=["assignment imbalanced"],
        created_at="2026-05-20T12:00:00+00:00",
    )
    md = build_experiment_card(ev).to_markdown()
    assert "**ERROR:** assignment imbalanced" in md


def test_validation_metadata_summary_in_markdown():
    ev = _full_experiment_evidence()
    md = build_experiment_card(ev).to_markdown()
    assert "scm_low_signal" in md
    assert "## Validation Evidence" in md


def test_empty_assignment_summary_graceful():
    spec = _spec()
    ev = DesignEvidence.from_assignment(spec, {"control": [], "test_0": []})
    card = build_experiment_card(ev)
    assert card.assignment_summary["control"] == 0
