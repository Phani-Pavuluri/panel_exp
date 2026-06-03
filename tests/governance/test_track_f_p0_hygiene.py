"""Track F P0 hygiene guards (AUDIT-010 follow-on)."""

from __future__ import annotations

import pytest

from panel_exp.governance.instrument_contract import (
    FULL_MODEL_BLOCKED_REASON,
    INV_015_REGISTRY_BAYESIAN_NOT_MCMC,
    MULTI_CELL_POOLED_WITHOUT_RULE,
    assert_class_tbr_recovery_factory,
    assert_full_model_allowed_for_export,
    assert_multi_cell_not_pooled_without_rule,
    assert_not_placebo_as_estimator,
    class_tbr_recovery_factory,
    full_model_export_block_reason,
    is_placebo_inference_mode,
    multi_cell_pooling_block_reason,
    registry_bayesian_production_block_reason,
)
from panel_exp.validation.did_interval_policy import (
    DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED,
    build_did_interval_policy,
)
from panel_exp.validation.recovery_runner import all_recovery_configs


def test_p0_001_full_model_blocked_for_scm_augsynth_governed_export():
    assert (
        full_model_export_block_reason("SyntheticControl", True)
        == FULL_MODEL_BLOCKED_REASON
    )
    assert (
        full_model_export_block_reason("AugSynthCVXPY", True)
        == FULL_MODEL_BLOCKED_REASON
    )
    assert full_model_export_block_reason("SyntheticControl", False) is None
    assert full_model_export_block_reason("TBRRidge", True) is None
    with pytest.raises(ValueError, match="full_model=True is blocked"):
        assert_full_model_allowed_for_export("AugSynthCVXPY", True)


def test_p0_002_recovery_runner_tbr_uses_class_tbr_not_tbrridge():
    cfg = all_recovery_configs()["TBR"]
    assert cfg.estimator_name == "TBR"
    assert_class_tbr_recovery_factory(cfg.factory)
    inst = cfg.factory()
    assert type(inst).__name__ == "TBR"
    assert class_tbr_recovery_factory()().__class__.__name__ == "TBR"


def test_p0_003_registry_bayesian_inv015_block():
    assert (
        registry_bayesian_production_block_reason("TBRRidge", "Bayesian")
        == INV_015_REGISTRY_BAYESIAN_NOT_MCMC
    )
    assert (
        registry_bayesian_production_block_reason("BayesianTBR", "Bayesian")
        == INV_015_REGISTRY_BAYESIAN_NOT_MCMC
    )
    assert registry_bayesian_production_block_reason("SCM", "UnitJackKnife") is None


def test_p0_004_did_relative_ci_policy_restricted():
    policy = build_did_interval_policy()
    assert policy["relative_att_interval_supported"] is False
    assert DID_RELATIVE_ATT_INTERVAL_UNSUPPORTED == "did_relative_att_interval_unsupported"


def test_p0_005_placebo_is_inference_not_estimator():
    assert is_placebo_inference_mode("Placebo")
    with pytest.raises(ValueError, match="inference/falsification"):
        assert_not_placebo_as_estimator("Placebo")


def test_p0_006_multi_cell_no_pooling_without_rule():
    assert multi_cell_pooling_block_reason(1, None) is None
    assert (
        multi_cell_pooling_block_reason(2, None, pooled_aggregation_requested=True)
        == MULTI_CELL_POOLED_WITHOUT_RULE
    )
    assert multi_cell_pooling_block_reason(2, "gov_rule_v1", pooled_aggregation_requested=True) is None
    with pytest.raises(ValueError, match="pooling_rule_id"):
        assert_multi_cell_not_pooled_without_rule(3, None, pooled_aggregation_requested=True)
