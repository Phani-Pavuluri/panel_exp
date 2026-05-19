"""Behavior equivalence tests for design registry refactor."""

from __future__ import annotations

import pytest

from panel_exp.design.assign import (
    BalancedRandomization,
    CompleteRandomization,
    Rerandomization,
    StratifiedRandomization,
    greedy_match_markets,
)
from panel_exp.design.geo_experiment_design import GEO_RUN_DESIGN_SUPPORTED, GeoExperimentDesign
from panel_exp.design.registry import (
    LEGACY_GEO_RUN_DESIGN_SUPPORTED,
    get_design_registry,
)
from tests.design_registry_helpers import (
    GOLDEN_DIR,
    LEGACY_ASSIGNMENT_GROUP_LABELS,
    LEGACY_GEO_RUN_DESIGN_SUPPORTED as HELPERS_LEGACY_GEO,
    LEGACY_MDE_PRC_COLUMNS,
    LEGACY_MDE_VAL_COLUMNS,
    assert_assignment_group_labels,
    load_assignment,
    make_geo_panel,
)


def _geo(
    label: str,
    cls: type,
    panel=None,
    *,
    random_state: int = 42,
    **kwargs,
) -> GeoExperimentDesign:
    return GeoExperimentDesign(
        panel_data=panel or make_geo_panel(seed=42),
        base_randomizer_cls=cls,
        random_state=random_state,
        test_lengths=[28],
        n_test_grps=1,
        validate_after_assign=False,
        max_iter=8,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# 1. Legacy output keys (run_design tuple + dataframe columns)
# ---------------------------------------------------------------------------


def test_run_design_output_keys_and_columns(monkeypatch):
    """Registry run path returns legacy 3-tuple with expected dataframe columns."""
    import pandas as pd

    def _fake_metrics(self, rs_dp_grps, control):
        mde_prc = pd.DataFrame(
            {
                "4wk_percent": [0.1],
                "control_dmas": [["u0"]],
                "test_dmas": [["u1"]],
                "test_prc": [10.0],
                "control_prc": [90.0],
            }
        )
        mde_val = pd.DataFrame(
            {
                "4wk_val": [1.0],
                "control_dmas": [["u0"]],
                "test_dmas": [["u1"]],
                "test_prc": [10.0],
                "control_prc": [90.0],
            }
        )
        power_df = pd.DataFrame(
            {
                "4wk_pa_obj1": [None],
                "4wk_pa_obj2": [None],
                "control_dmas": [["u0"]],
                "test_dmas": [["u1"]],
                "test_prc": [10.0],
                "control_prc": [90.0],
            }
        )
        return mde_prc, mde_val, power_df

    monkeypatch.setattr(GeoExperimentDesign, "_calculate_sensitivity_metrics", _fake_metrics)
    geo = _geo("balanced", BalancedRandomization)
    result = geo.run_design()
    assert isinstance(result, tuple)
    assert len(result) == 3
    mde_prc, mde_val, power_df = result
    assert LEGACY_MDE_PRC_COLUMNS <= set(mde_prc.columns)
    assert LEGACY_MDE_VAL_COLUMNS <= set(mde_val.columns)
    assert "control_dmas" in power_df.columns


# ---------------------------------------------------------------------------
# 2. Design alias equivalence
# ---------------------------------------------------------------------------


def test_greedy_match_assignment_repeatable_in_same_session():
    panel = make_geo_panel(seed=42)
    geo = _geo("gmm", greedy_match_markets, panel=panel)
    a1 = geo.create_design().assign(panel_data=panel, n_test_grps=1)
    a2 = geo.create_design().assign(panel_data=panel, n_test_grps=1)
    assert {k: sorted(v) for k, v in a1.items()} == {k: sorted(v) for k, v in a2.items()}


def test_gmm_alias_same_assignment_as_canonical():
    panel = make_geo_panel(seed=42)
    a1 = _geo("gmm", greedy_match_markets, panel=panel).create_design().assign(
        panel_data=panel, n_test_grps=1
    )
    a2 = _geo("canonical", greedy_match_markets, panel=panel).create_design().assign(
        panel_data=panel, n_test_grps=1
    )
    assert {k: sorted(v) for k, v in a1.items()} == {k: sorted(v) for k, v in a2.items()}


# ---------------------------------------------------------------------------
# 3–5. Deterministic assignment / rerandomization / constraints
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "label,cls",
    [
        ("balanced", BalancedRandomization),
        ("complete", CompleteRandomization),
        ("stratified", StratifiedRandomization),
    ],
)
def test_assignment_matches_golden(label: str, cls: type):
    golden_path = GOLDEN_DIR / f"assignment_{label}.json"
    if not golden_path.exists():
        pytest.skip(f"missing golden {golden_path}")
    import json

    payload = json.loads(golden_path.read_text())
    assert payload.get("group_labels") == list(LEGACY_ASSIGNMENT_GROUP_LABELS)
    panel = make_geo_panel(seed=42)
    geo = _geo(label, cls, panel=panel)
    assignment = geo.create_design().assign(panel_data=panel, n_test_grps=1)
    assert_assignment_group_labels(assignment)
    expected = load_assignment(golden_path)
    assert {k: sorted(v) for k, v in assignment.items()} == expected


def test_seeded_assignment_repeatable():
    panel = make_geo_panel(seed=7)
    g1 = _geo("balanced", BalancedRandomization, panel=panel, random_state=99)
    g2 = _geo("balanced", BalancedRandomization, panel=panel, random_state=99)
    a1 = g1.create_design().assign(panel_data=panel, n_test_grps=1)
    a2 = g2.create_design().assign(panel_data=panel, n_test_grps=1)
    assert a1 == a2


def test_whitelist_enforced_via_geo_pipeline():
    panel = make_geo_panel(seed=1)
    geo = _geo(
        "balanced",
        BalancedRandomization,
        panel=panel,
        control_whitelist=["u0"],
        test_whitelist=["u1"],
    )
    out = geo.create_design().assign(
        panel_data=panel,
        control_whitelist=["u0"],
        test_whitelist=["u1"],
        n_test_grps=1,
    )
    assert "u0" in out["control"]
    assert "u1" in out["test_0"]


def test_rerandomization_imbalance_path_unchanged():
    panel = make_geo_panel(n_units=10)
    rr = Rerandomization(
        treatment_probability=0.3,
        max_iter=5,
        base_randomizer_cls=BalancedRandomization,
        random_state=3,
    )
    out = rr.assign(panel_data=panel, n_test_grps=1)
    assert "control" in out and "test_0" in out


# ---------------------------------------------------------------------------
# 6. Validation failures
# ---------------------------------------------------------------------------


def test_unsupported_quickblock_at_geo_init():
    qb = pytest.importorskip("panel_exp.design.quickblock", reason="quickblock deps")
    QuickBlock = qb.QuickBlock
    panel = make_geo_panel()
    with pytest.raises(ValueError, match="not supported via GeoExperimentDesign"):
        GeoExperimentDesign(panel_data=panel, base_randomizer_cls=QuickBlock)


def test_whitelist_unsupported_design_raises():
    from panel_exp.design.modes import register_builtin_designs
    from panel_exp.design.registry import DesignRegistry, DesignSpec
    from panel_exp.design.geo_runner import run_geo_experiment_design

    reg = DesignRegistry()
    register_builtin_designs(reg)

    class _FakeNoWhitelist(type):
        __name__ = "FakeNoWhitelist"

    reg.register(
        DesignSpec(
            name="fake_no_whitelist",
            randomizer_cls=_FakeNoWhitelist,
            run=run_geo_experiment_design,
            geo_run_supported=True,
            supports_whitelist=False,
            supports_blacklist=True,
            priority=999,
        )
    )
    spec = reg.resolve("fake_no_whitelist")

    class _GeoStub:
        design_kwargs = {}
        test_whitelist = ["u0"]
        control_whitelist = []
        test_blacklist = []
        control_blacklist = []
        control_test_blacklist = []

    with pytest.raises(ValueError, match="does not support whitelist"):
        reg.validate_geo_capabilities(spec, _GeoStub())


def test_geo_run_design_supported_exact_legacy_set():
    assert GEO_RUN_DESIGN_SUPPORTED == LEGACY_GEO_RUN_DESIGN_SUPPORTED
    assert GEO_RUN_DESIGN_SUPPORTED == HELPERS_LEGACY_GEO
    assert "gmm" not in GEO_RUN_DESIGN_SUPPORTED
    assert "matched_pair" not in GEO_RUN_DESIGN_SUPPORTED
    assert "matchedpair" not in GEO_RUN_DESIGN_SUPPORTED


def test_registry_lists_more_than_geo_supported():
    reg = get_design_registry()
    registered = set(reg.list_registered_names())
    geo_supported = set(reg.geo_supported_names())
    assert geo_supported < registered or len(registered) > len(geo_supported)


@pytest.mark.parametrize("lookup", ["matchedpair", "matched_pair"])
def test_matched_pair_alias_not_geo_supported(lookup: str):
    reg = get_design_registry()
    if "matchedpair" not in reg.list_names():
        pytest.skip("matchedpair not registered")
    spec = reg.resolve(lookup)
    assert spec.name == "matchedpair"
    assert spec.geo_run_supported is False
    assert reg.resolve("matchedpair") is spec


def test_matched_pair_alias_fails_same_as_class_at_init():
    mp = pytest.importorskip("panel_exp.design.matched_pair", reason="networkx")
    MatchedPair = mp.MatchedPair
    panel = make_geo_panel()
    reg = get_design_registry()
    msg_class = None
    msg_alias = None
    try:
        GeoExperimentDesign(panel_data=panel, base_randomizer_cls=MatchedPair)
    except ValueError as e:
        msg_class = str(e)
    spec = reg.resolve("matched_pair")
    geo_stub = type(
        "Stub",
        (),
        {
            "design_kwargs": {},
            "test_whitelist": [],
            "control_whitelist": [],
            "test_blacklist": [],
            "control_blacklist": [],
            "control_test_blacklist": [],
        },
    )()
    try:
        reg.validate_geo_capabilities(spec, geo_stub)
    except ValueError as e:
        msg_alias = str(e)
    assert msg_class is not None
    assert msg_alias is not None
    assert "not supported via GeoExperimentDesign" in msg_class
    assert "not supported via GeoExperimentDesign" in msg_alias


def test_unsupported_init_before_train_length():
    qb = pytest.importorskip("panel_exp.design.quickblock", reason="quickblock deps")
    QuickBlock = qb.QuickBlock
    panel = make_geo_panel()
    with pytest.raises(ValueError, match="not supported via GeoExperimentDesign"):
        GeoExperimentDesign(panel_data=panel, base_randomizer_cls=QuickBlock)


def test_supported_init_completes_train_length():
    panel = make_geo_panel()
    geo = GeoExperimentDesign(
        panel_data=panel,
        base_randomizer_cls=BalancedRandomization,
        test_lengths=[28],
        validate_after_assign=False,
        max_iter=3,
    )
    assert geo.train_length > 0


def test_unsupported_registry_run_before_pipeline(monkeypatch):
    mp = pytest.importorskip("panel_exp.design.matched_pair", reason="networkx")
    MatchedPair = mp.MatchedPair
    panel = make_geo_panel()
    geo = GeoExperimentDesign(
        panel_data=panel,
        base_randomizer_cls=BalancedRandomization,
        test_lengths=[28],
        validate_after_assign=False,
        max_iter=3,
    )
    calls: list[str] = []

    def _track_run(_ctx):
        calls.append("run")
        return None

    import panel_exp.design.geo_runner as geo_runner

    monkeypatch.setattr(geo_runner, "run_geo_experiment_design", _track_run)
    reg = get_design_registry()
    with pytest.raises(ValueError, match="not supported via GeoExperimentDesign"):
        reg.run(MatchedPair, geo)
    assert calls == []
    assert geo.last_evidence is None
    assert geo.last_validation is None


def test_run_design_pipeline_order(monkeypatch):
    """assign → validate → evidence → MDE (legacy order)."""
    from unittest.mock import MagicMock

    import panel_exp.design.geo_runner as geo_runner
    from panel_exp.design.assign import Rerandomization

    order: list[str] = []
    panel = make_geo_panel()
    geo = GeoExperimentDesign(
        panel_data=panel,
        base_randomizer_cls=BalancedRandomization,
        test_lengths=[28],
        validate_after_assign=True,
        max_iter=3,
    )

    def _assign(self, panel_data=None, **kwargs):
        order.append("assign")
        return {"control": ["u0", "u1"], "test_0": ["u2", "u3"]}

    def _validate(*args, **kwargs):
        order.append("validate")
        mock = MagicMock()
        mock.to_dict.return_value = {}
        return mock

    def _from_assignment(*args, **kwargs):
        order.append("evidence")
        return MagicMock()

    def _mde(self, rs_dp_grps, control):
        order.append("mde")
        import pandas as pd

        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    monkeypatch.setattr(Rerandomization, "assign", _assign)
    monkeypatch.setattr(geo_runner, "validate_design", _validate)
    monkeypatch.setattr(geo_runner.DesignEvidence, "from_assignment", _from_assignment)
    monkeypatch.setattr(GeoExperimentDesign, "_calculate_sensitivity_metrics", _mde)

    geo.run_design()
    assert order == ["assign", "validate", "evidence", "mde"]
