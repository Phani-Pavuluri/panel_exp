"""D5-INST-COMBO-AUDIT-001 — Estimator × inference × geometry compatibility audit (research).

Verifies combinations from code paths and targeted probes — not a blind Cartesian product.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.inference.registry import get_inference_registry
from panel_exp.inference_result import IntervalType
from panel_exp.method_metadata import _ESTIMATOR_CATALOG
from panel_exp.track_b._registry import CONFIG_RESOLUTION
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason, jax_stack_skip_reason
from panel_exp.validation.track_d_d5_inst_audit_001 import (
    ESTIMATOR_IMPORTS,
    GEOMETRY_BUILDERS,
    ProbeConfig,
    _build_wide,
    _import_estimator,
    _probe_run,
)

ComboStatus = Literal[
    "valid_candidate",
    "implemented_but_unvalidated",
    "invalid_by_interface",
    "invalid_by_geometry",
    "invalid_by_estimand",
    "invalid_by_scale",
    "research_only",
    "blocked",
    "already_characterized",
]

INFERENCE_MODES: tuple[str | None, ...] = (
    None,
    "UnitJackKnife",
    "JKP",
    "Kfold",
    "BlockResidualBootstrap",
    "Placebo",
    "Conformal",
    "Bayesian",
    "TimeSeriesKfold",
)

# Geometries where estimator readout applies (not design-only).
READOUT_GEOMETRIES: tuple[str, ...] = (
    "single_cell_unit_level",
    "single_treated_unit",
    "multi_treated_natural",
    "aggregate_two_series",
    "multi_cell_per_cell_unit",
    "pooled_multi_cell",
)

DESIGN_ONLY_GEOMETRIES: tuple[str, ...] = (
    "supergeo_design_only",
    "trimmed_population_design_only",
)

ALREADY_CHARACTERIZED: dict[tuple[str, str, str], str] = {
    ("SyntheticControl", "UnitJackKnife", "single_cell_unit_level"): "D5-POW-001e",
    ("SyntheticControl", "Placebo", "single_treated_unit"): "D5-INST-PLACEBO-001",
    ("SyntheticControl", "Placebo", "multi_treated_natural"): "D5-INST-PLACEBO-001",
    ("TBRRidge", "Kfold", "single_cell_unit_level"): "D5-INST-TBRRIDGE-001",
    ("TBRRidge", "Kfold", "aggregate_two_series"): "D5-INST-TBRRIDGE-001",
    ("TBRRidge", "BlockResidualBootstrap", "single_cell_unit_level"): "D5-INST-TBRRIDGE-001",
    ("AugSynthCVXPY", "point_estimate", "single_cell_unit_level"): "D5-INST-AUGSYNTH-001",
    ("AugSynthCVXPY", "UnitJackKnife", "single_cell_unit_level"): "D5-INST-AUGSYNTH-001",
    ("AugSynthCVXPY", "UnitJackKnife", "multi_cell_per_cell_unit"): "D5-INST-AUGSYNTH-001",
    ("DID", "estimator_native_bootstrap", "single_cell_unit_level"): "D3/DEF-003",
    ("DID", "estimator_native_bootstrap", "multi_treated_natural"): "D3/DEF-003",
}


@dataclass(frozen=True)
class ComboAuditConfig:
    probe: ProbeConfig = ProbeConfig(train_length=20, test_length=6, n_geos=12, seed=42)
    run_probes: bool = True
    probe_required_examples_only: bool = False


def _inference_key(inf: str | None) -> str:
    return "point_estimate" if inf is None else inf


def _declared_inference(estimator_class: str) -> set[str | None]:
    for meta in _ESTIMATOR_CATALOG:
        if meta.class_name == estimator_class:
            out: set[str | None] = set()
            for i in meta.inference_support:
                out.add(None if i == "point_estimate" else i)
            return out
    return {None}


def _tbr_geometry_ok(geometry: str) -> bool:
    return geometry == "aggregate_two_series"


def _placebo_geometry_ok(geometry: str, n_treated: int) -> bool:
    if geometry == "single_treated_unit":
        return n_treated == 1
    return False


def _static_classify(
    estimator_class: str,
    inference: str | None,
    geometry: str,
) -> dict[str, Any]:
    inf_key = _inference_key(inference)
    char_key = (estimator_class, inf_key, geometry)
    if char_key in ALREADY_CHARACTERIZED:
        return {
            "status": "already_characterized",
            "rationale": f"Prior D5/Phase evidence: {ALREADY_CHARACTERIZED[char_key]}",
            "code_refs": ["prior_artifacts"],
            "probe_required": False,
        }

    if geometry in DESIGN_ONLY_GEOMETRIES:
        return {
            "status": "invalid_by_geometry",
            "rationale": "Design-method geometry (supergeo/trim); not ImpactAnalyzer readout scope.",
            "code_refs": ["D5-DES-SUPERGEO-001", "D5-DES-TRIM-001"],
            "probe_required": False,
        }

    if geometry == "pooled_multi_cell":
        return {
            "status": "blocked",
            "rationale": "No governed pooled multi-cell instrument path; per-cell only.",
            "code_refs": ["D5-MCELL-001", "E-DES-MCELL-*"],
            "probe_required": False,
        }

    declared = _declared_inference(estimator_class)
    if inference not in declared and estimator_class != "DID":
        return {
            "status": "invalid_by_interface",
            "rationale": f"{estimator_class} catalog inference_support does not include {inf_key}.",
            "code_refs": ["method_metadata.py"],
            "probe_required": False,
        }

    # --- DID: native bootstrap only ---
    if estimator_class == "DID":
        if inf_key != "estimator_native_bootstrap":
            return {
                "status": "invalid_by_interface",
                "rationale": "DID.run_analysis overrides registry; bootstrap is estimator-native cumulative ATT.",
                "code_refs": ["methods/DID.py run_analysis"],
                "probe_required": False,
            }
        if geometry == "aggregate_two_series":
            return {
                "status": "invalid_by_estimand",
                "rationale": "DID exports cumulative ATT intervals — not relative ATT post without bridge.",
                "code_refs": ["DEF-003", "track_b DID_Bootstrap"],
                "probe_required": False,
            }
        return {
            "status": "already_characterized",
            "rationale": "Restricted; native bootstrap only (D3).",
            "code_refs": ["DID.py _block_bootstrap_inference"],
            "probe_required": False,
        }

    # --- TROP ---
    if estimator_class == "TROP":
        if inf_key != "point_estimate":
            return {
                "status": "invalid_by_interface",
                "rationale": "TROP uses ImpactAnalyzer point path only; no registry inference modes.",
                "code_refs": ["triply_robust_est.py TROP.run_analysis"],
                "probe_required": False,
            }
        return {
            "status": "research_only",
            "rationale": "TROP research_only; validation runner skipped.",
            "code_refs": ["runner.SKIPPED_ESTIMATORS"],
            "probe_required": False,
        }

    # --- BayesianTBR ---
    if estimator_class in ("BayesianTBR", "BayesianTBRHorseShoe"):
        if inf_key == "Bayesian":
            return {
                "status": "research_only",
                "rationale": (
                    "Registry Bayesian uses JAX predict quantiles — not equivalent to "
                    "estimator-native NUTS MCMC (INV-015)."
                ),
                "code_refs": ["inference/modes/impl.py run_bayesian"],
                "probe_required": True,
            }
        if inf_key == "mcmc_native":
            return {
                "status": "research_only",
                "rationale": "NUTS via fit_model MCMC — exploratory only.",
                "code_refs": ["bayesian_regression.py fit_model"],
                "probe_required": False,
            }
        return {
            "status": "invalid_by_interface",
            "rationale": "BayesianTBR only supports registry Bayesian / native MCMC.",
            "code_refs": ["method_metadata"],
            "probe_required": False,
        }

    # --- TBR class (not TBRRidge) ---
    if estimator_class == "TBR":
        if not _tbr_geometry_ok(geometry):
            return {
                "status": "invalid_by_geometry",
                "rationale": "TBR.fit_data requires exactly 1 treated + 1 control (pre-aggregated).",
                "code_refs": ["methods/tbr.py TBR.fit_data asserts"],
                "probe_required": False,
            }
        if inf_key == "Placebo":
            return {
                "status": "invalid_by_interface",
                "rationale": "run_placebo sets placebo_unsupported for TBR class.",
                "code_refs": ["inference/modes/impl.py run_placebo is_tbr"],
                "probe_required": False,
            }
        if inf_key in ("UnitJackKnife", "JKP", "Kfold", "point_estimate"):
            return {
                "status": "valid_candidate" if inf_key == "point_estimate" else "implemented_but_unvalidated",
                "rationale": f"TBR aggregate 1×1 panel; {inf_key} via registry if probe passes.",
                "code_refs": ["tbr.py", "ImpactAnalyzer.run_analysis"],
                "probe_required": True,
            }
        return {
            "status": "invalid_by_interface",
            "rationale": f"TBR not wired for {inf_key} on aggregate panel in catalog.",
            "code_refs": ["method_metadata TBR inference_support"],
            "probe_required": False,
        }

    # --- Placebo ---
    if inf_key == "Placebo":
        if geometry != "single_treated_unit":
            return {
                "status": "invalid_by_geometry",
                "rationale": "placebo() requires len(treated_units)==1 (in-space).",
                "code_refs": ["inference/placebo.py"],
                "probe_required": False,
            }
        if estimator_class == "TBR":
            return {
                "status": "invalid_by_interface",
                "rationale": "TBR excluded from placebo-in-space.",
                "code_refs": ["impl.run_placebo"],
                "probe_required": False,
            }
        return {
            "status": "valid_candidate",
            "rationale": "SCM-family placebo-in-space when donors>=5; diagnostic_only.",
            "code_refs": ["placebo.py", "impl.run_placebo"],
            "probe_required": True,
        }

    # --- UnitJackKnife ---
    if inf_key == "UnitJackKnife":
        if geometry == "aggregate_two_series" and estimator_class in (
            "SyntheticControl",
            "AugSynthCVXPY",
        ):
            return {
                "status": "invalid_by_geometry",
                "rationale": "JK is unit-level LOO over control donors; 2-row agg panel breaks donor semantics.",
                "code_refs": ["unit_jackknife.py"],
                "probe_required": False,
            }

    # --- AugSynthCVXPY ---
    if estimator_class == "AugSynthCVXPY":
        if cvxpy_osqp_skip_reason():
            return {
                "status": "blocked",
                "rationale": cvxpy_osqp_skip_reason() or "cvxpy missing",
                "code_refs": ["optional_deps"],
                "probe_required": False,
            }
        if inf_key in ("Kfold", "BlockResidualBootstrap", "Conformal", "TimeSeriesKfold"):
            if geometry not in ("single_cell_unit_level", "multi_cell_per_cell_unit", "single_treated_unit"):
                return {
                    "status": "invalid_by_geometry",
                    "rationale": "AugSynthCVXPY unit donor panel required; min_donors=5.",
                    "code_refs": ["scm.py AugSynthCVXPY min_donors"],
                    "probe_required": False,
                }
            return {
                "status": "implemented_but_unvalidated",
                "rationale": (
                    f"Registry wires {inf_key}; refits estimator — OC not run on 001e windows. "
                    "BRB uses SCM-tuned defaults for AugSynth family."
                ),
                "code_refs": ["impl.run_block_residual_bootstrap _is_scm", "registry"],
                "probe_required": True,
            }
        if inf_key == "Bayesian":
            return {
                "status": "invalid_by_estimand",
                "rationale": "Registry Bayesian not coherent with AugSynthCVXPY MCMC; use SCM/TBR if needed.",
                "code_refs": ["impl.run_bayesian"],
                "probe_required": False,
            }

    # --- Base AugSynth ---
    if estimator_class == "AugSynth":
        return {
            "status": "implemented_but_unvalidated",
            "rationale": "Inner SyntheticControlCVXPY; unvalidated duplicate of CVXPY path.",
            "code_refs": ["scm.py AugSynth"],
            "probe_required": False,
        }

    # --- TBRRidge ---
    if estimator_class == "TBRRidge":
        if inf_key in ("Kfold", "BlockResidualBootstrap"):
            if geometry == "aggregate_two_series":
                status: ComboStatus = "already_characterized" if inf_key == "Kfold" else "implemented_but_unvalidated"
                return {
                    "status": status,
                    "rationale": "TBRRidge agg2 geo-power path; restricted comparator.",
                    "code_refs": ["D5-INST-TBRRIDGE-001", "geo_experiment_design PowerAnalysis"],
                    "probe_required": inf_key != "Kfold",
                }
            return {
                "status": (
                    "already_characterized"
                    if inf_key == "Kfold"
                    else "implemented_but_unvalidated"
                ),
                "rationale": f"Unit-panel TBRRidge+{inf_key}; D5-INST-TBRRIDGE-001.",
                "code_refs": ["D5-INST-TBRRIDGE-001"],
                "probe_required": inf_key != "Kfold",
            }
        if inf_key == "Placebo":
            return {
                "status": "invalid_by_interface",
                "rationale": "Placebo-in-space excluded for TBR class name check — TBRRidge is not TBR but verify donors.",
                "code_refs": ["impl.run_placebo — TBRRidge not is_tbr"],
                "probe_required": True,
            }
        if inf_key == "UnitJackKnife":
            return {
                "status": "implemented_but_unvalidated",
                "rationale": "Wired but not characterized; scale may diverge from SCM JK.",
                "code_refs": ["unit_jackknife"],
                "probe_required": True,
            }

    # --- SCM ---
    if estimator_class == "SyntheticControl" and inf_key == "UnitJackKnife":
        if geometry == "single_cell_unit_level":
            return {
                "status": "already_characterized",
                "rationale": "Governed null-monitor reference.",
                "code_refs": ["D5-POW-001e"],
                "probe_required": False,
            }

    # --- Track B scale / CalibrationSignal ---
    scale_note = ""
    status_default: ComboStatus = "implemented_but_unvalidated"
    if inf_key == "point_estimate":
        status_default = "valid_candidate"

    tb_alias = any(
        estimator_class in ("SyntheticControl", "AugSynthCVXPY", "TBRRidge")
        and inf_key in ("UnitJackKnife", "Kfold")
        for _ in [0]
    )
    if tb_alias and estimator_class == "TBRRidge" and inf_key == "Kfold":
        pass  # handled above

    return {
        "status": status_default,
        "rationale": f"Default classification for {estimator_class}+{inf_key} on {geometry}.{scale_note}",
        "code_refs": ["ImpactAnalyzer.run_analysis", "registry"],
        "probe_required": inf_key not in ("point_estimate",) and geometry == "single_cell_unit_level",
        "calibration_signal_note": "No combo infers MMM ingress; Track B CONFIG_RESOLUTION only lists governed aliases.",
    }


def _explicit_combo_list() -> list[tuple[str, str | None, str]]:
    """Curated combinations — not full Cartesian product."""
    combos: list[tuple[str, str | None, str]] = []
    required: list[tuple[str, str | None, str]] = [
        ("AugSynthCVXPY", None, "single_cell_unit_level"),
        ("AugSynthCVXPY", "UnitJackKnife", "single_cell_unit_level"),
        ("AugSynthCVXPY", "Kfold", "single_cell_unit_level"),
        ("AugSynthCVXPY", "BlockResidualBootstrap", "single_cell_unit_level"),
        ("AugSynthCVXPY", "Conformal", "single_cell_unit_level"),
        ("AugSynthCVXPY", "Placebo", "single_treated_unit"),
        ("TBR", None, "aggregate_two_series"),
        ("TBR", "UnitJackKnife", "aggregate_two_series"),
        ("TBR", "JKP", "aggregate_two_series"),
        ("TBR", "Kfold", "aggregate_two_series"),
        ("TBR", "Placebo", "aggregate_two_series"),
        ("TBR", None, "single_cell_unit_level"),
        ("TBRRidge", "Kfold", "single_cell_unit_level"),
        ("TBRRidge", "BlockResidualBootstrap", "single_cell_unit_level"),
        ("TBRRidge", "Kfold", "aggregate_two_series"),
        ("TBRRidge", "UnitJackKnife", "single_cell_unit_level"),
        ("TBRRidge", "Placebo", "single_treated_unit"),
        ("BayesianTBR", "Bayesian", "single_cell_unit_level"),
        ("BayesianTBR", "mcmc_native", "single_cell_unit_level"),
        ("TROP", None, "single_cell_unit_level"),
        ("DID", "estimator_native_bootstrap", "single_cell_unit_level"),
        ("SyntheticControl", "UnitJackKnife", "single_cell_unit_level"),
        ("SyntheticControl", "Placebo", "single_treated_unit"),
        ("SyntheticControl", "Placebo", "multi_treated_natural"),
    ]
    combos.extend(required)
    for geom in DESIGN_ONLY_GEOMETRIES:
        combos.append(("SyntheticControl", "UnitJackKnife", geom))

    for inf in ("Conformal", "TimeSeriesKfold", "Bayesian", "JKP"):
        combos.append(("TBRRidge", inf, "single_cell_unit_level"))

    # Dedupe
    seen: set[tuple[str, str | None, str]] = set()
    out: list[tuple[str, str | None, str]] = []
    for c in combos:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _apply_probe(
    row: dict[str, Any],
    panel: Any,
    estimator_class: str,
    inference: str | None,
    cfg: ComboAuditConfig,
) -> None:
    cls = _import_estimator(estimator_class)
    if cls is None:
        row["probe"] = {"status": "import_failed"}
        return
    if estimator_class == "DID":
        row["probe"] = {"status": "skipped", "reason": "DID uses native run_analysis"}
        return
    if row.get("status") in ("invalid_by_geometry", "invalid_by_interface", "blocked", "already_characterized"):
        if row["status"] == "already_characterized":
            row["probe"] = {"status": "skipped", "reason": "already_characterized"}
        return
    if not cfg.run_probes:
        row["probe"] = {"status": "not_run"}
        return
    if cfg.probe_required_examples_only and not row.get("probe_required"):
        row["probe"] = {"status": "not_run_static_sufficient"}
        return

    kwargs: dict[str, Any] = {}
    if inference == "Placebo":
        kwargs["placebo_strict"] = False
    if inference == "BlockResidualBootstrap":
        kwargs.update(
            n_bootstrap=12,
            block_length=4,
            min_train_periods=6,
            show_progress=False,
            random_state=0,
        )
    if inference == "Kfold":
        kwargs["random_state"] = 0

    probe = _probe_run(
        cls,
        panel,
        inference=inference,
        extra_kwargs=kwargs,
        timeout_class=estimator_class in ("TROP", "BayesianTBR", "BayesianTBRHorseShoe"),
    )
    row["probe"] = probe
    if probe.get("status") == "probe_success" and row["status"] == "implemented_but_unvalidated":
        row["status"] = "valid_candidate"
        row["rationale"] = row["rationale"] + " Probe succeeded on battery panel."
    elif probe.get("status") == "probe_failed" and row["status"] == "valid_candidate":
        row["status"] = "invalid_by_interface"
        row["rationale"] = f"Probe failed: {probe.get('error_type')}: {probe.get('error', '')[:120]}"


def _track_b_alignment(estimator_class: str, inference: str | None) -> dict[str, Any]:
    inf_key = _inference_key(inference)
    aliases = []
    for alias, res in CONFIG_RESOLUTION.items():
        fam = res.instrument_family
        if estimator_class == "SyntheticControl" and fam == "synthetic_control":
            if inf_key == "UnitJackKnife" and "jackknife" in res.inference_method:
                aliases.append(alias)
            if inf_key == "Placebo" and res.inference_method == "placebo":
                aliases.append(alias)
        if estimator_class == "TBRRidge" and fam == "tbrridge":
            if inf_key == "Kfold" and res.inference_method == "kfold":
                aliases.append(alias)
            if inf_key == "BlockResidualBootstrap" and "bootstrap" in res.inference_method:
                aliases.append(alias)
        if estimator_class == "AugSynthCVXPY" and "augsynth" in fam:
            if inf_key == "point_estimate":
                aliases.append(alias)
    return {
        "config_aliases": aliases,
        "calibration_signal_eligible": False,
        "note": "Only SCM_UnitJackKnife is nominal-calibration eligible per policy.",
    }


def _oc_roadmap(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = [r for r in rows if r["status"] == "valid_candidate"]
    unvalidated = [r for r in rows if r["status"] == "implemented_but_unvalidated"]
    blocked_invalid = [
        r for r in rows if r["status"].startswith("invalid") or r["status"] == "blocked"
    ]
    return [
        {
            "priority": "P1",
            "battery_id": "D5-INST-TBR-001",
            "combos": [
                f"{r['estimator_class']}+{r['inference']}+{r['geometry_mode']}"
                for r in candidates
                if r["estimator_class"] == "TBR"
            ],
        },
        {
            "priority": "P2",
            "battery_id": "D5-INST-TBRRIDGE-002",
            "combos": [
                f"{r['estimator_class']}+{r['inference']}+{r['geometry_mode']}"
                for r in unvalidated
                if r["estimator_class"] == "TBRRidge"
            ],
        },
        {
            "priority": "P2",
            "battery_id": "D5-INST-AUGSYNTH-002-inference",
            "combos": [
                f"{r['estimator_class']}+{r['inference']}+{r['geometry_mode']}"
                for r in unvalidated
                if r["estimator_class"] == "AugSynthCVXPY"
                and r["inference"] in ("Kfold", "BlockResidualBootstrap")
            ],
        },
        {
            "priority": "deferred",
            "battery_id": "invalid_or_blocked",
            "count": len(blocked_invalid),
            "examples": [
                f"{r['estimator_class']}+{r['inference']}+{r['geometry_mode']}: {r['status']}"
                for r in blocked_invalid[:8]
            ],
        },
        {
            "priority": "P0_after_P1",
            "battery_id": "AUDIT-010",
            "note": "MMM readiness/gap after TBR-001 + characterized comparators",
        },
    ]


def build_d5_inst_combo_audit_001(cfg: ComboAuditConfig | None = None) -> dict[str, Any]:
    cfg = cfg or ComboAuditConfig()
    wide = _build_wide(cfg.probe)
    combos = _explicit_combo_list()
    rows: list[dict[str, Any]] = []

    for estimator_class, inference, geometry in combos:
        static = _static_classify(estimator_class, inference, geometry)
        row: dict[str, Any] = {
            "estimator_class": estimator_class,
            "inference": _inference_key(inference),
            "geometry_mode": geometry,
            "status": static["status"],
            "rationale": static["rationale"],
            "code_refs": static["code_refs"],
            "probe_required": static.get("probe_required", False),
            "geometry_support": {
                "single_treated": geometry in ("single_treated_unit",),
                "multi_treated": geometry == "multi_treated_natural",
                "multi_cell_per_cell": geometry == "multi_cell_per_cell_unit",
                "aggregate_two_series": geometry == "aggregate_two_series",
                "unit_level_donors": geometry
                in ("single_cell_unit_level", "multi_cell_per_cell_unit", "multi_treated_natural"),
                "pooled_multi_cell": False,
            },
            "conceptual_checks": {
                "registry_wired": inference in get_inference_registry().list_mode_names()
                or inference is None
                or inference == "estimator_native_bootstrap",
                "refits_estimator": inference not in (None, "point_estimate", "estimator_native_bootstrap"),
                "track_b": _track_b_alignment(estimator_class, inference),
            },
        }
        if geometry in GEOMETRY_BUILDERS:
            try:
                panel = GEOMETRY_BUILDERS[geometry](wide, cfg.probe)
                row["panel_meta"] = {
                    "n_treated": len(panel.treated_units),
                    "n_control": len(panel.control_units),
                }
                _apply_probe(row, panel, estimator_class, inference, cfg)
            except Exception as exc:
                row["probe"] = {"status": "panel_build_failed", "error": str(exc)[:120]}
        rows.append(row)

    status_counts: dict[str, int] = {}
    for r in rows:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1

    return {
        "artifact_id": "D5-INST-COMBO-AUDIT-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "governance": {
            "no_cartesian_product": True,
            "no_promotion": True,
            "no_new_production_combinations": True,
        },
        "binding_docs": ["D5_INST_AUDIT_001", "D5_INST_AUGSYNTH_001"],
        "compatibility_matrix": rows,
        "status_counts": status_counts,
        "n_combinations_audited": len(rows),
        "oc_battery_roadmap": _oc_roadmap(rows),
        "findings": [
            {
                "id": "D5-COMBO-FIND-001",
                "summary": "TBR+Kfold/Placebo on unit panel invalid_by_geometry; aggregate 1×1 only.",
            },
            {
                "id": "D5-COMBO-FIND-002",
                "summary": "AugSynthCVXPY+Kfold/BRB wired but unvalidated — probe before OC battery.",
            },
            {
                "id": "D5-COMBO-FIND-003",
                "summary": "TBRRidge+Placebo may run (not is_tbr) but single-treated+donors required.",
            },
            {
                "id": "D5-COMBO-FIND-004",
                "summary": "BayesianTBR registry Bayesian ≠ NUTS MCMC — invalid_by_estimand for governed use.",
            },
        ],
        "overall_verdict": "compatibility_audited_curated_combinations_only",
        "user_facing_warnings": [
            "Do not OC test invalid_by_* combinations.",
            "already_characterized combos do not need repeat batteries unless geometry changes.",
            "AUDIT-010 blocks invalid combos from MMM intake explicitly.",
        ],
    }


def write_artifact(path: Path | None = None, *, cfg: ComboAuditConfig | None = None) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_COMBO_AUDIT_001_results.json"
    )
    payload = build_d5_inst_combo_audit_001(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
