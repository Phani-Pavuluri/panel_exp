"""D5-INST-AUDIT-001 — GeoX estimator × inference × geometry inventory (research).

Code-grounded audit before further instrument OC batteries. No production changes.
"""

from __future__ import annotations

import importlib
import json
import re
import subprocess
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal

import numpy as np
import pandas as pd

from panel_exp.inference.registry import get_inference_registry
from panel_exp.method_metadata import _ESTIMATOR_CATALOG, _INFERENCE_MODE_CATALOG
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.track_b._registry import CONFIG_RESOLUTION
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason, jax_stack_skip_reason
from panel_exp.validation.recovery_runner import all_recovery_configs
from panel_exp.validation.runner import SKIPPED_ESTIMATORS, default_estimator_configs
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001e import _assign

GovernanceClass = Literal[
    "production_safe",
    "restricted",
    "diagnostic_only",
    "characterization_required",
    "blocked",
    "research_only",
    "legacy",
    "uncharacterized",
]

Callability = Literal[
    "implemented",
    "production_callable",
    "research_callable",
    "probe_success",
    "probe_blocked",
    "probe_failed",
    "not_wired",
    "optional_dep_missing",
]

GEOMETRY_MODES: tuple[str, ...] = (
    "single_cell_unit_level",
    "multi_cell_per_cell_unit",
    "single_treated_unit",
    "multi_treated_natural",
    "aggregate_two_series",
    "pooled_multi_cell",
    "supergeo_design_only",
    "trimmed_population_design_only",
)

D5_OC_EVIDENCE: dict[str, list[str]] = {
    "SCM_UnitJackKnife": [
        "D5-POW-001b",
        "D5-POW-001e",
        "D5-INF-002a/002b",
        "D3",
    ],
    "SCM_Placebo": ["D5-INST-PLACEBO-001", "PHASE15"],
    "TBRRidge_Kfold": ["D5-INST-TBRRIDGE-001", "D5-POW-001a", "D5-POW-001c"],
    "TBRRidge_BlockResidualBootstrap": ["D5-INST-TBRRIDGE-001", "D3"],
    "TBRRidge": ["D5-POW-001a/c", "recovery_runner"],
    "TBR": ["method_metadata", "tbr.py asserts"],
    "DID_Bootstrap": ["D3", "DEF-003", "recovery_runner"],
    "AugSynthCVXPY_Point": ["PHASE14", "GOLD-003"],
    "AugSynthCVXPY_UnitJackKnife": ["PHASE14", "D3"],
    "AugSynth": ["D2", "limited"],
    "SyntheticControlCVXPY": ["D2", "test_scm.py"],
    "BayesianTBR": ["INV-015", "method_metadata"],
    "TROP": ["trop_test.py", "recovery_runner skipped"],
    "SyntheticDID": ["synthetic_did_test.py", "recovery skipped"],
    "MTGP": ["method_metadata", "validation skipped"],
}

ESTIMATOR_IMPORTS: dict[str, tuple[str, str]] = {
    "SyntheticControl": ("panel_exp.methods.scm", "SyntheticControl"),
    "AugSynth": ("panel_exp.methods.scm", "AugSynth"),
    "SyntheticControlCVXPY": ("panel_exp.methods.scm", "SyntheticControlCVXPY"),
    "AugSynthCVXPY": ("panel_exp.methods.scm", "AugSynthCVXPY"),
    "TBR": ("panel_exp.methods.tbr", "TBR"),
    "TBRRidge": ("panel_exp.methods.tbr", "TBRRidge"),
    "TBRAutoSARIMAX": ("panel_exp.methods.tbr", "TBRAutoSARIMAX"),
    "BayesianTBR": ("panel_exp.methods.bayesian_regression", "BayesianTBR"),
    "BayesianTBRHorseShoe": ("panel_exp.methods.bayesian_regression", "BayesianTBRHorseShoe"),
    "DID": ("panel_exp.methods.DID", "DID"),
    "SyntheticDID": ("panel_exp.methods.synthetic_did", "SyntheticDID"),
    "TROP": ("panel_exp.methods.triply_robust_est", "TROP"),
    "MTGP": ("panel_exp.methods.mtgp", "MTGP"),
}


@dataclass(frozen=True)
class ProbeConfig:
    train_length: int = 20
    test_length: int = 6
    n_geos: int = 12
    seed: int = 42


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _import_estimator(class_name: str) -> type | None:
    spec = ESTIMATOR_IMPORTS.get(class_name)
    if spec is None:
        return None
    mod_name, attr = spec
    try:
        mod = importlib.import_module(mod_name)
        return getattr(mod, attr)
    except Exception:
        return None


def _build_wide(cfg: ProbeConfig) -> pd.DataFrame:
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY["scm_low_signal"],
        random_state=cfg.seed,
        n_geos=cfg.n_geos,
        n_periods=cfg.train_length + cfg.test_length,
        treatment_start=cfg.train_length,
        true_effect=0.0,
    )
    return SyntheticWorld.generate(scenario).to_panel_dataset().wide_data


def _panel_single_cell_unit(wide: pd.DataFrame, cfg: ProbeConfig) -> PanelDataset:
    assignment = _assign(
        "greedy_match_markets",
        wide,
        train_length=cfg.train_length,
        seed=cfg.seed,
        treatment_probability=0.35,
        n_test_grps=1,
        rerandomization_max_iter=200,
    )
    control = list(assignment["control"])
    treated = list(assignment["test_0"])
    end = cfg.train_length + cfg.test_length
    units = control + treated
    return PanelDataset(
        wide.loc[units].iloc[:, :end].copy(),
        treated_units=treated,
        treated_periods=[TimePeriod(cfg.train_length, end - 1) for _ in treated],
    )


def _panel_single_treated(wide: pd.DataFrame, cfg: ProbeConfig) -> PanelDataset:
    p = _panel_single_cell_unit(wide, cfg)
    if len(p.treated_units) < 1:
        raise ValueError("no treated")
    tu = [p.treated_units[0]]
    end = cfg.train_length + cfg.test_length
    units = list(p.control_units) + tu
    return PanelDataset(
        p.wide_data.loc[units].iloc[:, :end].copy(),
        treated_units=tu,
        treated_periods=[TimePeriod(cfg.train_length, end - 1)],
    )


def _panel_multi_treated(wide: pd.DataFrame, cfg: ProbeConfig) -> PanelDataset:
    return _panel_single_cell_unit(wide, cfg)


def _panel_aggregate_two_series(wide: pd.DataFrame, cfg: ProbeConfig) -> PanelDataset:
    p = _panel_single_cell_unit(wide, cfg)
    end = cfg.train_length + cfg.test_length
    treated_sum = p.wide_data.loc[p.treated_units].sum(axis=0).iloc[:end]
    control_sum = p.wide_data.loc[p.control_units].sum(axis=0).iloc[:end]
    agg = pd.DataFrame({"treated": treated_sum, "control": control_sum}).T
    return PanelDataset(
        agg,
        treated_units=["treated"],
        treated_periods=[TimePeriod(cfg.train_length, end - 1)],
    )


def _panel_multi_cell_per_cell(wide: pd.DataFrame, cfg: ProbeConfig) -> PanelDataset:
    assignment = _assign(
        "greedy_match_markets",
        wide,
        train_length=cfg.train_length,
        seed=cfg.seed,
        treatment_probability=0.35,
        n_test_grps=2,
        rerandomization_max_iter=200,
    )
    control = list(assignment["control"])
    treated = list(assignment["test_0"][:1] or assignment["test_0"])
    if not treated and assignment.get("test_0"):
        treated = [assignment["test_0"][0]]
    end = cfg.train_length + cfg.test_length
    units = control + treated
    return PanelDataset(
        wide.loc[units].iloc[:, :end].copy(),
        treated_units=treated,
        treated_periods=[TimePeriod(cfg.train_length, end - 1)],
    )


GEOMETRY_BUILDERS: dict[str, Callable[[pd.DataFrame, ProbeConfig], PanelDataset]] = {
    "single_cell_unit_level": _panel_single_cell_unit,
    "multi_cell_per_cell_unit": _panel_multi_cell_per_cell,
    "single_treated_unit": _panel_single_treated,
    "multi_treated_natural": _panel_multi_treated,
    "aggregate_two_series": _panel_aggregate_two_series,
}


def _optional_skip(class_name: str) -> str | None:
    if class_name in ("SyntheticControlCVXPY", "AugSynthCVXPY"):
        return cvxpy_osqp_skip_reason()
    if class_name in ("BayesianTBR", "BayesianTBRHorseShoe", "MTGP"):
        return jax_stack_skip_reason()
    return None


def _probe_run(
    cls: type,
    panel: PanelDataset,
    *,
    inference: str | None,
    extra_kwargs: dict[str, Any] | None = None,
    timeout_class: bool = False,
) -> dict[str, Any]:
    if timeout_class:
        return {"status": "probe_skipped", "reason": "slow_or_mcmc_estimator"}
    skip = _optional_skip(cls.__name__)
    if skip:
        return {"status": "optional_dep_missing", "reason": skip}
    try:
        if cls.__name__ == "DID":
            est = cls()
            est.run_analysis(panel, multiple_treated="pooled")
        elif inference is None:
            est = cls(inference=None)
            est.run_analysis(panel)
        else:
            est = cls(inference=inference, alpha=0.05)
            kwargs = dict(extra_kwargs or {})
            if inference == "Placebo":
                kwargs.setdefault("placebo_strict", False)
            if inference == "BlockResidualBootstrap":
                kwargs.update(
                    n_bootstrap=15,
                    block_length=4,
                    min_train_periods=6,
                    show_progress=False,
                    random_state=0,
                )
            est.run_analysis(panel, **kwargs)
        ir = getattr(est, "inference_result", None)
        path_it = None
        if ir is not None:
            pit = getattr(ir, "path_interval_type", None)
            path_it = getattr(pit, "value", pit)
        return {
            "status": "probe_success",
            "has_y_hat": bool(getattr(est, "results", {}).get("y_hat") is not None),
            "path_interval_type": path_it,
            "n_treated": len(panel.treated_units),
            "n_control": len(panel.control_units),
        }
    except Exception as exc:
        return {
            "status": "probe_failed",
            "error_type": type(exc).__name__,
            "error": str(exc)[:240],
            "n_treated": len(panel.treated_units),
            "n_control": len(panel.control_units),
        }


def _count_test_references() -> dict[str, int]:
    root = _repo_root() / "tests"
    counts: dict[str, int] = {}
    for meta in _ESTIMATOR_CATALOG:
        cn = meta.class_name
        pattern = re.compile(rf"\b{re.escape(cn)}\b")
        n = 0
        for path in root.rglob("*.py"):
            try:
                if pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
                    n += 1
            except OSError:
                continue
        counts[meta.name] = n
    return counts


def _git_head() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=_repo_root(),
                text=True,
            )
            .strip()
        )
    except Exception:
        return "unknown"


def _estimator_static_record(meta: Any) -> dict[str, Any]:
    cls = _import_estimator(meta.class_name)
    return {
        "registry_name": meta.name,
        "class_name": meta.class_name,
        "module_path": meta.module_path,
        "maturity_catalog": meta.maturity.value,
        "inference_support_declared": list(meta.inference_support),
        "known_limitations": list(meta.known_limitations),
        "optional_dependencies": list(meta.optional_dependencies),
        "synthetic_validation_flag": meta.synthetic_validation,
        "import_ok": cls is not None,
        "default_validation_runner": meta.name in {c.estimator_name for c in default_estimator_configs()},
        "validation_runner_skipped": meta.name in SKIPPED_ESTIMATORS
        or meta.class_name in SKIPPED_ESTIMATORS,
        "recovery_config_keys": [
            k for k, v in all_recovery_configs().items() if v.estimator_name == meta.name
        ],
        "track_b_config_aliases": [
            alias
            for alias, res in CONFIG_RESOLUTION.items()
            if res.instrument_family in meta.name.lower()
            or meta.name.lower() in res.instrument_family
            or (
                meta.name == "SCM"
                and res.instrument_family == "synthetic_control"
            )
            or (meta.name == "TBRRidge" and res.instrument_family == "tbrridge")
            or (meta.name == "DID" and res.instrument_family == "did")
            or (meta.name.startswith("AugSynth") and "augsynth" in res.instrument_family)
        ],
    }


def _governance_for_combo(
    est_name: str,
    inference: str | None,
    geometry: str,
) -> GovernanceClass:
    key = f"{est_name}_{inference}" if inference else est_name
    if geometry in ("supergeo_design_only", "trimmed_population_design_only"):
        return "characterization_required"
    if est_name in ("TROP", "SyntheticDID", "MTGP", "BayesianTBR", "BayesianTBRHorseShoe"):
        return "research_only"
    if est_name == "AugSynth":
        return "blocked"
    if est_name in ("SyntheticControlCVXPY", "AugSynthCVXPY") and inference is None:
        return "characterization_required"
    if est_name == "AugSynthCVXPY" and inference == "UnitJackKnife":
        return "diagnostic_only"
    if est_name == "SCM" and inference == "UnitJackKnife":
        return "diagnostic_only"  # null_monitor_only maps to diagnostic_only in E2
    if est_name == "SCM" and inference == "Placebo":
        if geometry == "multi_treated_natural":
            return "blocked"
        return "diagnostic_only"
    if est_name == "TBRRidge":
        if inference in ("Kfold", "BlockResidualBootstrap"):
            return "restricted"
        return "restricted"
    if est_name == "TBR":
        return "restricted"
    if est_name == "DID":
        return "restricted"
    if inference == "Bayesian":
        return "research_only"
    return "uncharacterized"


def _build_compatibility_matrix(cfg: ProbeConfig) -> list[dict[str, Any]]:
    registry = get_inference_registry()
    wide = _build_wide(cfg)
    rows: list[dict[str, Any]] = []

    slow_estimators = frozenset({"TROP", "BayesianTBR", "BayesianTBRHorseShoe", "MTGP", "SyntheticDID"})

    for meta in _ESTIMATOR_CATALOG:
        cls = _import_estimator(meta.class_name)
        if cls is None:
            continue
        inferences: list[str | None] = list(meta.inference_support) or [None]
        if "point_estimate" in inferences:
            inferences = [None if i == "point_estimate" else i for i in inferences]
            if None not in inferences:
                inferences = [None] + [i for i in inferences if i is not None]

        for geometry, builder in GEOMETRY_BUILDERS.items():
            try:
                panel = builder(wide, cfg)
            except Exception as exc:
                for inf in inferences:
                    rows.append(
                        {
                            "estimator": meta.name,
                            "class_name": meta.class_name,
                            "inference": inf,
                            "geometry_mode": geometry,
                            "implemented": True,
                            "callable_status": "probe_blocked",
                            "probe": {"status": "panel_build_failed", "error": str(exc)[:120]},
                            "governance_class": _governance_for_combo(meta.name, inf, geometry),
                            "d5_oc_evidence": D5_OC_EVIDENCE.get(
                                f"{meta.name}_{inf}" if inf else meta.name, []
                            ),
                        }
                    )
                continue

            for inf in inferences:
                if inf is not None:
                    try:
                        registry.resolve(inf)
                        registry_wired = True
                    except (KeyError, NotImplementedError):
                        registry_wired = False
                else:
                    registry_wired = True

                if meta.class_name == "DID" and inf == "bootstrap":
                    registry_wired = False  # native bootstrap in fit_model, not registry

                probe = _probe_run(
                    cls,
                    panel,
                    inference=inf,
                    timeout_class=meta.class_name in slow_estimators,
                )

                if meta.class_name == "TBR" and geometry == "single_cell_unit_level":
                    probe = {
                        "status": "probe_blocked",
                        "reason": "TBR requires 1 aggregated treated + 1 aggregated control (tbr.py asserts)",
                        **probe,
                    }

                if meta.class_name == "SyntheticControl" and inf == "Placebo":
                    if len(panel.treated_units) != 1:
                        probe = {
                            "status": "probe_blocked",
                            "reason": "placebo() single_treated_only",
                            "n_treated": len(panel.treated_units),
                        }

                prod_callable = (
                    probe.get("status") == "probe_success"
                    and meta.name in {"SCM", "TBRRidge", "DID"}
                    and geometry in ("single_cell_unit_level", "aggregate_two_series")
                )
                research_callable = probe.get("status") == "probe_success"

                rows.append(
                    {
                        "estimator": meta.name,
                        "class_name": meta.class_name,
                        "inference": inf,
                        "geometry_mode": geometry,
                        "implemented": True,
                        "registry_inference_wired": registry_wired,
                        "callable_status": probe.get("status"),
                        "probe": probe,
                        "supports_unit_level_data": geometry
                        in (
                            "single_cell_unit_level",
                            "multi_cell_per_cell_unit",
                            "single_treated_unit",
                            "multi_treated_natural",
                        ),
                        "supports_aggregate_treated_control": geometry == "aggregate_two_series",
                        "supports_multi_treated": len(panel.treated_units) > 1,
                        "supports_multi_cell_per_cell": geometry == "multi_cell_per_cell_unit",
                        "supports_pooled_multi_cell": False,
                        "has_uncertainty": inf is not None and inf != "point_estimate",
                        "geo_power_readout": (
                            meta.name == "TBRRidge"
                            and geometry == "aggregate_two_series"
                            and inf in (None, "Kfold")
                        ),
                        "impact_analyzer_path": meta.class_name != "DID"
                        or inf is None,
                        "did_native_bootstrap": meta.class_name == "DID",
                        "governance_class": _governance_for_combo(meta.name, inf, geometry),
                        "d5_oc_evidence": D5_OC_EVIDENCE.get(
                            f"{meta.name}_{inf}" if inf else meta.name,
                            D5_OC_EVIDENCE.get(meta.name, []),
                        ),
                    }
                )

    for geometry in ("supergeo_design_only", "trimmed_population_design_only"):
        rows.append(
            {
                "estimator": "_design_geometry_",
                "class_name": None,
                "inference": None,
                "geometry_mode": geometry,
                "implemented": False,
                "callable_status": "not_estimator_scope",
                "note": "Design-method geometry (D5-DES-SUPERGEO/TRIM); not ImpactAnalyzer readout.",
                "governance_class": "characterization_required",
                "d5_oc_evidence": ["D5-DES-SUPERGEO-001", "D5-DES-TRIM-001"],
            }
        )

    return rows


def _explicit_answers() -> dict[str, Any]:
    return {
        "normal_tbr_where_runs": [
            "panel_exp.methods.tbr.TBR — ImpactAnalyzer + inference registry when panel has exactly 1 treated and 1 control series.",
            "NOT in default_estimator_configs (TBRRidge is listed as 'TBR' label but factory is TBRRidge).",
            "recovery_runner 'TBR' config incorrectly uses TBRRidge factory (audit finding).",
            "Geo PowerAnalysis uses TBRRidge on aggregate two-row panel, not class TBR.",
        ],
        "normal_tbr_geometry": {
            "unit_level_multi_control": "Blocked — fit_data asserts num_control_units == 1.",
            "aggregated_two_series": "Required — 1 treated row + 1 control row (or single treated + single control column).",
            "multi_treated": "Blocked at TBR class; use TBRRidge for multiple treated units.",
        },
        "normal_tbr_inference_wired": [
            "Declared in method_metadata: point_estimate, UnitJackKnife, JKP, Kfold.",
            "Placebo explicitly excluded in inference/modes/impl.py for TBR class.",
            "Live probe: unit-level multi-control panel fails asserts.",
        ],
        "bayesian_tbr_where_runs": [
            "panel_exp.methods.bayesian_regression.BayesianTBR / BayesianTBRHorseShoe.",
            "Uses ImpactAnalyzer.run_analysis → registry 'Bayesian' mode (NOT full NUTS path in registry handler).",
            "Skipped in EstimatorValidationRunner (SKIPPED_ESTIMATORS / jax).",
        ],
        "bayesian_tbr_geometry": {
            "multi_control_unit_level": "Supported in fit_data (de-aggregated controls).",
            "aggregate_control": "Docstring notes aggregated or de-aggregated controls.",
            "multi_treated": "Treated series can be multivariate; registry Bayesian uses quantiles on predict output.",
        },
        "bayesian_tbr_uncertainty_object": (
            "Registry path: IntervalType.CREDIBLE_INTERVAL on path via JAX quantiles of predict() — "
            "NOT the same as estimator-native NUTS posterior from fit_model MCMC unless caller uses MCMC API directly."
        ),
        "bayesian_tbr_production_status": "research_only (method_metadata RESEARCH_ONLY; optional jax stack; INV-015)",
        "augsynth_variants": {
            "AugSynth": "Implemented; inference point_estimate/Kfold/Conformal per catalog; limited tests; UNVALIDATED.",
            "AugSynthCVXPY": "Implemented; requires cvxpy+osqp; point/Kfold/Conformal; Phase 14 OC.",
            "SyntheticControlCVXPY": "SCM CVXPY variant; expert_review; test_scm.py.",
            "track_b": "AugSynthCVXPY_Point, AugSynthCVXPY_UnitJackKnife (characterized, not eligible).",
        },
        "trop_status": "research_only — TROP class in triply_robust_est.py; validation runner SKIPPED; tests/trop_test.py only.",
        "combinations_tested_today": {
            "d5_instrument_batteries": [
                "SCM+JK (001b/e)",
                "TBRRidge+Kfold/BRB (001a/c, D5-INST-TBRRIDGE-001)",
                "SCM+Placebo (D5-INST-PLACEBO-001)",
            ],
            "not_d5_battery": [
                "normal TBR class",
                "BayesianTBR MCMC",
                "TROP",
                "SyntheticDID recovery",
                "MTGP",
                "AugSynth base (non-CVXPY) D5",
            ],
        },
        "readout_path_summary": {
            "governed_null_monitor": "unit panel + SyntheticControl + UnitJackKnife (001e)",
            "geo_power_mde": "aggregate two-row + TBRRidge + Kfold (001a/c)",
            "placebo_diagnostic": "unit single-treated + SCM + Placebo",
            "did": "native moving_block_bootstrap in DID.run_analysis (overrides registry)",
        },
    }


def _oc_battery_roadmap() -> list[dict[str, Any]]:
    return [
        {
            "battery_id": "D5-INST-AUGSYNTH-001",
            "priority": "P1",
            "estimators": ["AugSynthCVXPY", "AugSynth"],
            "rationale": "Phase 14 archive exists but no 001e-window D5 harness; base AugSynth unvalidated.",
            "blocked_by": "cvxpy optional deps for CVXPY path",
        },
        {
            "battery_id": "D5-INST-TBR-001",
            "priority": "P1",
            "estimators": ["TBR"],
            "rationale": "Distinct from TBRRidge; aggregate-only asserts; geo product confusion risk.",
            "blocked_by": "Must use aggregate_two_series panels only",
        },
        {
            "battery_id": "D5-INST-BAYESIANTBR-001",
            "priority": "P2",
            "estimators": ["BayesianTBR"],
            "rationale": "Clarify registry Bayesian vs NUTS MCMC; multi-treated/aggregate geometry.",
            "blocked_by": "jax stack; slow MCMC",
        },
        {
            "battery_id": "D5-INST-TROP-001",
            "priority": "P3",
            "estimators": ["TROP"],
            "rationale": "Active code but skipped in validation runner; research_only.",
            "blocked_by": "Runtime; large config space",
        },
        {
            "battery_id": "D5-INST-DID-001",
            "priority": "deferred",
            "estimators": ["DID"],
            "rationale": "DEF-016 deferred; native bootstrap already documented; cumulative vs relative ATT policy closed.",
            "blocked_by": "Policy closure DEF-003; low marginal governance value",
        },
        {
            "battery_id": "D5-INST-TBRRIDGE-002",
            "priority": "P2",
            "estimators": ["TBRRidge"],
            "rationale": "Remaining inference paths: UnitJackKnife, Conformal, TimeSeriesKfold, registry Bayesian on TBRRidge.",
            "blocked_by": "001 covered Kfold/BRB only",
        },
        {
            "battery_id": "AUDIT-010",
            "priority": "P0_after_P1_instruments",
            "estimators": ["_governance_"],
            "rationale": (
                "MMM readiness / gap audit — not a promotion gate until "
                "D5-INST-AUGSYNTH-001 and D5-INST-TBR-001 characterize core gaps."
            ),
            "blocked_by": "AugSynthCVXPY and normal TBR uncharacterized on 001e windows",
        },
    ]


def build_d5_inst_audit_001(cfg: ProbeConfig | None = None) -> dict[str, Any]:
    cfg = cfg or ProbeConfig()
    inf_reg = get_inference_registry()
    inference_modes = []
    for m in _INFERENCE_MODE_CATALOG:
        key = None if m.name == "point_estimate" else m.name
        spec = inf_reg.resolve(key)
        pit = spec.path_interval_type
        inference_modes.append(
            {
                "name": m.name,
                "maturity": m.maturity.value,
                "path_interval_type": getattr(pit, "value", pit) if pit is not None else None,
            }
        )

    estimators = [_estimator_static_record(m) for m in _ESTIMATOR_CATALOG]
    matrix = _build_compatibility_matrix(cfg)
    test_counts = _count_test_references()

    n_success = sum(1 for r in matrix if r.get("callable_status") == "probe_success")

    return {
        "artifact_id": "D5-INST-AUDIT-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_head(),
        "lane": "research",
        "governance": {
            "no_promotion": True,
            "no_production_changes": True,
            "inventory_only": True,
        },
        "config": {"probe": cfg.__dict__},
        "inference_modes_registered": inference_modes,
        "estimators": estimators,
        "track_b_config_aliases": list(CONFIG_RESOLUTION.keys()),
        "nominal_calibration_eligible": ["SCM_UnitJackKnife"],
        "validation_runner_default": [c.estimator_name for c in default_estimator_configs()],
        "validation_runner_skipped": sorted(SKIPPED_ESTIMATORS),
        "recovery_config_names": sorted(all_recovery_configs().keys()),
        "compatibility_matrix": matrix,
        "matrix_summary": {
            "n_rows": len(matrix),
            "n_probe_success": n_success,
            "geometry_modes": list(GEOMETRY_MODES),
        },
        "test_file_hits_by_estimator": test_counts,
        "explicit_answers": _explicit_answers(),
        "oc_battery_roadmap": _oc_battery_roadmap(),
        "findings": [
            {
                "id": "D5-AUD-FIND-001",
                "summary": "TBR class requires aggregated 1×1 treated/control; TBRRidge is unit/multi-control path.",
                "implication": "Geo PowerAnalysis uses TBRRidge+agg2, not TBR class.",
            },
            {
                "id": "D5-AUD-FIND-002",
                "summary": "Registry 'Bayesian' ≠ BayesianTBR NUTS MCMC (INV-015).",
                "implication": "Do not promote registry Bayesian as BayesianTBR evidence.",
            },
            {
                "id": "D5-AUD-FIND-003",
                "summary": "DID.run_analysis overrides registry; bootstrap is estimator-native cumulative ATT.",
                "implication": "DID_Bootstrap Track B alias maps to native bootstrap, not registry mode.",
            },
            {
                "id": "D5-AUD-FIND-004",
                "summary": "recovery_runner TBR config uses TBRRidge factory.",
                "implication": "Fix or document before any TBR OC battery.",
            },
        ],
        "overall_verdict": "inventory_complete_augsynth_tbr_then_mmm_readiness_audit_010",
        "recommended_sequence": [
            "D5-INST-AUGSYNTH-001",
            "D5-INST-TBR-001",
            "AUDIT-010 (MMM readiness/gap — not promotion)",
            "D5-INST-TBRRIDGE-002",
            "D5-INST-BAYESIANTBR-001",
            "D5-INST-TROP-001",
        ],
    }


def write_artifact(path: Path | None = None, *, cfg: ProbeConfig | None = None) -> Path:
    path = path or (
        _repo_root()
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_AUDIT_001_results.json"
    )
    payload = build_d5_inst_audit_001(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
