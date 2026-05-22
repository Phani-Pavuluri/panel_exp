"""Tests for interference review metadata (no spillover estimation)."""

from __future__ import annotations

import copy

from panel_exp.artifacts.experiment_card import build_experiment_card
from panel_exp.artifacts.run_bundle import build_run_artifact_bundle
from panel_exp.evidence import (
    DesignEvidence,
    attach_interference_review,
    build_interference_review,
)
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import (
    InterferenceAssumption,
    InterferenceReview,
    ReviewRiskLevel,
    SpilloverDirection,
    spec_from_geo_design,
)


def _spec(**kwargs):
    defaults = dict(
        experiment_id="ir-test-1",
        outcome_column="y",
        unit_column="u",
        time_column="t",
        pre_period=TimePeriod(0, 5),
        experiment_period=TimePeriod(5, 10),
        design_method="balancedrandomization",
        random_state=1,
    )
    defaults.update(kwargs)
    return spec_from_geo_design(**defaults)


def test_interference_review_defaults():
    review = InterferenceReview()
    d = review.to_dict()
    assert d["assumption"] == "unknown"
    assert d["buffer_geos"] == []
    assert d["adjacent_geos"] == []
    assert d["shared_market_risk"] == "unknown"
    assert d["contamination_risk"] == "unknown"
    assert d["expected_spillover_direction"] == "unknown"
    assert d["spillover_notes"] == ""
    assert d["review_warnings"] == []


def test_build_interference_review_explicit_values():
    spec = _spec(
        interference=InterferenceAssumption.PARTIAL_INTERFERENCE,
        spillover_notes="DMA overlap expected",
    )
    packet = build_interference_review(
        spec,
        buffer_geos=["g1", "g2"],
        adjacent_geos=["g3"],
        shared_market_risk=ReviewRiskLevel.MEDIUM,
        expected_spillover_direction=SpilloverDirection.POSITIVE,
        contamination_risk=ReviewRiskLevel.LOW,
        exposure_channel_overlap="search + display",
        ad_saturation_risk=ReviewRiskLevel.HIGH,
    )
    assert packet["assumption"] == "partial_interference"
    assert packet["buffer_geos"] == ["g1", "g2"]
    assert packet["adjacent_geos"] == ["g3"]
    assert packet["shared_market_risk"] == "medium"
    assert packet["expected_spillover_direction"] == "positive"
    assert packet["spillover_notes"] == "DMA overlap expected"
    assert packet["exposure_channel_overlap"] == "search + display"
    assert packet["ad_saturation_risk"] == "high"


def test_unknown_assumption_warning():
    spec = _spec(interference=InterferenceAssumption.UNKNOWN)
    packet = build_interference_review(spec)
    assert any("limits causal interpretation" in w for w in packet["review_warnings"])


def test_no_interference_without_buffer_warns():
    spec = _spec(interference=InterferenceAssumption.NO_INTERFERENCE)
    packet = build_interference_review(spec)
    assert any("no buffer geos documented" in w for w in packet["review_warnings"])


def test_partial_interference_without_adjacent_warns():
    spec = _spec(interference=InterferenceAssumption.PARTIAL_INTERFERENCE)
    packet = build_interference_review(spec)
    assert any("without adjacent geo metadata" in w for w in packet["review_warnings"])


def test_high_contamination_risk_warning():
    spec = _spec()
    packet = build_interference_review(
        spec,
        contamination_risk=ReviewRiskLevel.HIGH,
    )
    assert any("High contamination risk documented" in w for w in packet["review_warnings"])


def test_attach_helper_additive():
    artifacts: dict = {"existing": 1}
    review = build_interference_review(_spec())
    attach_interference_review(artifacts, review)
    assert artifacts["existing"] == 1
    assert artifacts["interference_review"] == review


def test_design_evidence_includes_interference_review():
    spec = _spec(
        interference=InterferenceAssumption.NO_INTERFERENCE,
        buffer_geos=["dma_a"],
    )
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["u0"], "test_0": ["u1"]},
        created_at="2026-05-20T12:00:00+00:00",
    )
    ir = ev.to_dict()["artifacts"]["interference_review"]
    assert ir["assumption"] == "no_interference"
    assert ir["buffer_geos"] == ["dma_a"]


def test_experiment_card_renders_interference_review_section():
    spec = _spec(
        interference=InterferenceAssumption.PARTIAL_INTERFERENCE,
        spillover_notes="notes",
        buffer_geos=["b1"],
        adjacent_geos=["a1"],
    )
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["u0"], "test_0": ["u1"]},
        created_at="2026-05-20T12:00:00+00:00",
    )
    md = build_experiment_card(ev).to_markdown()
    assert "## Interference Review" in md
    assert "Assumption" in md
    assert "Buffer geos" in md
    assert "b1" in md
    assert "does not estimate spillover effects" in md


def test_run_bundle_includes_interference_review():
    spec = _spec(interference=InterferenceAssumption.UNKNOWN)
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["u0"], "test_0": ["u1"]},
        created_at="2026-05-20T12:00:00+00:00",
    )
    bundle = build_run_artifact_bundle(evidence=ev)
    assert bundle.interference_review is not None
    assert bundle.interference_review["assumption"] == "unknown"
    assert "interference_review" in bundle.to_dict()
    assert "## Interference Review" in bundle.to_markdown()


def test_input_objects_not_mutated():
    spec = _spec()
    assignment = {"control": ["u0"], "test_0": ["u1"]}
    assignment_copy = copy.deepcopy(assignment)
    assumptions_copy = dict(spec.assumptions)
    artifacts = {"keep": True}
    artifacts_copy = copy.deepcopy(artifacts)
    ev = DesignEvidence.from_assignment(
        spec,
        assignment,
        artifacts=artifacts,
        created_at="2026-05-20T12:00:00+00:00",
    )
    build_interference_review(spec)
    attach_interference_review(artifacts, {"assumption": "unknown"})
    assert assignment == assignment_copy
    assert dict(spec.assumptions) == assumptions_copy
    assert artifacts["keep"] is True
    assert "interference_review" in artifacts
    assert artifacts_copy == {"keep": True}
    _ = ev.to_dict()
