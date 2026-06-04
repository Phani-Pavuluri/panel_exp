"""METHOD-CODE-INVENTORY-001 — read-only code discovery for method components.

Introspects design registry, estimator/inference catalogs, and known wrappers.
Does not import estimators for fitting or mutate production state.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from panel_exp.design.registry import get_design_registry
from panel_exp.method_metadata import estimator_catalog, inference_mode_catalog

InventoryStatus = Literal[
    "implemented",
    "partial",
    "test_only",
    "research_only",
    "legacy",
    "duplicate_or_alias",
    "dead_or_unreachable",
    "unclear_requires_review",
]

MethodType = Literal[
    "design",
    "estimator",
    "inference",
    "wrapper",
    "orchestration",
    "registry",
    "research",
    "unknown",
]


@dataclass
class InventoryRow:
    canonical_name: str
    aliases: list[str] = field(default_factory=list)
    method_type: MethodType = "unknown"
    module_path: str = ""
    class_or_function_name: str = ""
    public_entrypoint_status: str = "unclear"
    expected_inputs: str = ""
    expected_outputs: str = ""
    supported_geometry_if_declared: str = ""
    treatment_structure_if_declared: str = ""
    estimand_if_declared: str = ""
    uncertainty_output_if_any: str = ""
    docs_references: list[str] = field(default_factory=list)
    tests_references: list[str] = field(default_factory=list)
    validation_artifacts_references: list[str] = field(default_factory=list)
    known_gaps_from_existing_docs: str = ""
    inventory_status: InventoryStatus = "unclear_requires_review"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _design_rows() -> list[InventoryRow]:
    registry = get_design_registry()
    rows: list[InventoryRow] = []
    for spec in registry._sorted_specs():
        geo = spec.geo_run_supported
        rows.append(
            InventoryRow(
                canonical_name=spec.name,
                aliases=list(spec.aliases),
                method_type="design",
                module_path=f"panel_exp.design (handler: {spec.run.__module__})",
                class_or_function_name=spec.randomizer_cls.__name__,
                public_entrypoint_status="public" if geo else "internal",
                expected_inputs="PanelDataset / wide panel; design kwargs; optional pre_treatment_period",
                expected_outputs=spec.output_type or "assignment_dict",
                supported_geometry_if_declared=(
                    "unit assignment dict control/test_*; multi-cell via n_test_grps"
                    if geo
                    else "design-specific (see notes)"
                ),
                treatment_structure_if_declared="n_test_grps >= 1",
                estimand_if_declared="assignment / balance (not ATT)",
                uncertainty_output_if_any="none",
                docs_references=["TRACK_D_DESIGN_METHOD_INVENTORY_001.md"],
                tests_references=(
                    ["tests/track_d/test_design_inventory_001.py"]
                    if geo
                    else []
                ),
                validation_artifacts_references=(
                    ["track_d/D5_POW_001e", "track_d/D5_DES_*"]
                    if geo
                    else ["track_d/D5_DES_SUPERGEO_001", "track_d/D5_DES_TRIM_001"]
                    if spec.name in ("supergeos", "trimmedmatch")
                    else []
                ),
                known_gaps_from_existing_docs=(
                    "INV-D1-001: caller must pass pre_treatment_period for matching"
                    if spec.name == "greedy_match_markets"
                    else "Not geo-run supported" if not geo else ""
                ),
                inventory_status="implemented" if geo else "partial",
            )
        )
    rows.append(
        InventoryRow(
            canonical_name="rerandomization_wrapper",
            aliases=("Rerandomization", "rerandomization"),
            method_type="wrapper",
            module_path="panel_exp/design/assign.py",
            class_or_function_name="Rerandomization",
            public_entrypoint_status="public",
            expected_inputs="base_randomizer_cls + panel_data; imbalance metric",
            expected_outputs="assignment via wrapped base randomizer",
            supported_geometry_if_declared="same as wrapped base (typically unit dict)",
            treatment_structure_if_declared="via base randomizer",
            estimand_if_declared="assignment",
            docs_references=["DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md"],
            tests_references=["tests/track_d/test_design_inventory_001.py"],
            validation_artifacts_references=["D5-POW-001e inventory"],
            known_gaps_from_existing_docs="Distinct from bare greedy in some OC paths",
            inventory_status="implemented",
        )
    )
    return rows


def _estimator_rows() -> list[InventoryRow]:
    rows: list[InventoryRow] = []
    test_map = {
        "SCM": ["tests/test_scm.py"],
        "AugSynth": ["tests/test_scm.py"],
        "SyntheticControlCVXPY": ["tests/test_scm.py"],
        "AugSynthCVXPY": ["tests/test_scm.py", "tests/track_d/test_d5_inst_augsynth_ascm_003.py"],
        "TBR": ["tests/track_d/test_d5_inst_tbr_001.py"],
        "TBRRidge": [
            "tests/track_d/test_d5_inst_tbrridge_001.py",
            "tests/track_d/test_d5_inst_tbrridge_003.py",
        ],
        "DID": ["tests/test_did_interval_policy.py", "tests/test_did_pretrend_contract.py"],
        "SyntheticDID": ["tests/synthetic_did_test.py"],
        "TROP": ["tests/trop_test.py"],
        "BayesianTBR": ["tests/jax_test_helpers.py"],
    }
    for meta in estimator_catalog():
        maturity = meta.maturity.value
        status: InventoryStatus = "implemented"
        if maturity == "research_only":
            status = "research_only"
        elif meta.name == "AugSynth":
            status = "partial"
        rows.append(
            InventoryRow(
                canonical_name=meta.name,
                aliases=[meta.class_name] if meta.class_name != meta.name else [],
                method_type="estimator",
                module_path=meta.module_path,
                class_or_function_name=meta.class_name,
                public_entrypoint_status="public",
                expected_inputs="PanelDataset; treated units; pre/post windows via ImpactAnalyzer",
                expected_outputs="point effect / model results / optional inference paths",
                supported_geometry_if_declared=(
                    "unit panel (SCM/AugSynth/TBRRidge/DID); aggregate 1x1 (TBR only)"
                    if meta.name in ("TBR",)
                    else "unit panel typical"
                ),
                treatment_structure_if_declared="single or multi treated per fit loop",
                estimand_if_declared="method-specific (often undeclared in code)",
                uncertainty_output_if_any=", ".join(meta.inference_support) or "none",
                docs_references=["method_metadata.py", "METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"],
                tests_references=test_map.get(meta.name, []),
                validation_artifacts_references=[],
                known_gaps_from_existing_docs="; ".join(meta.known_limitations[:2]),
                inventory_status=status,
            )
        )
    rows.append(
        InventoryRow(
            canonical_name="synthetic_control_function",
            aliases=["synthetic_control"],
            method_type="estimator",
            module_path="panel_exp/methods/synthetic_control.py",
            class_or_function_name="synthetic_control",
            public_entrypoint_status="internal",
            expected_inputs="PanelDataset",
            expected_outputs="dict weights",
            inventory_status="legacy",
            known_gaps_from_existing_docs="Legacy scipy function; not ImpactAnalyzer catalog entry",
        )
    )
    return rows


def _inference_rows() -> list[InventoryRow]:
    rows: list[InventoryRow] = []
    impl_map = {
        "point_estimate": "panel_exp/inference/modes/impl.py:run_point_estimate",
        "UnitJackKnife": "panel_exp/inference/unit_jackknife.py",
        "JKP": "panel_exp/inference/unit_jackknife.py:jkp",
        "Kfold": "panel_exp/inference/k_fold.py",
        "BlockResidualBootstrap": "panel_exp/inference/block_residual_bootstrap.py",
        "Conformal": "panel_exp/inference/conformal.py",
        "Placebo": "panel_exp/inference/placebo.py",
        "TimeSeriesKfold": "panel_exp/inference/k_fold.py (TS path)",
        "Bayesian": "panel_exp/inference/modes/impl.py:run_bayesian",
    }
    for meta in inference_mode_catalog():
        rows.append(
            InventoryRow(
                canonical_name=meta.name,
                method_type="inference",
                module_path=impl_map.get(meta.name, "panel_exp/inference/modes/impl.py"),
                class_or_function_name=f"run_{meta.name}",
                public_entrypoint_status="public",
                expected_inputs="ImpactAnalyzer + PanelDataset post-fit",
                expected_outputs="y_hat; optional y_lower/y_upper; mode-specific keys",
                uncertainty_output_if_any=meta.name
                if meta.name != "point_estimate"
                else "none",
                docs_references=["F_INF_001", "F_INF_003", "method_metadata.py"],
                tests_references=["tests/governance/test_f_inf_001_interval_semantics.py"],
                known_gaps_from_existing_docs="; ".join(meta.known_limitations[:2]),
                inventory_status=(
                    "research_only"
                    if meta.maturity.value == "research_only"
                    else "implemented"
                ),
            )
        )
    rows.append(
        InventoryRow(
            canonical_name="DID_native_bootstrap",
            aliases=["estimator_native_bootstrap"],
            method_type="inference",
            module_path="panel_exp/methods/DID.py",
            class_or_function_name="DID.run_analysis",
            public_entrypoint_status="internal",
            expected_inputs="DID estimator only",
            expected_outputs="cumulative ATT intervals (embedded)",
            estimand_if_declared="relative ATT path (DEF-003 partial)",
            inventory_status="partial",
            known_gaps_from_existing_docs="Not in inference registry; DEF-003 relative CI deferred",
            docs_references=["TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md"],
        )
    )
    return rows


def _orchestration_and_registry_rows() -> list[InventoryRow]:
    return [
        InventoryRow(
            canonical_name="GeoExperimentDesign",
            method_type="orchestration",
            module_path="panel_exp/design/geo_experiment_design.py",
            class_or_function_name="GeoExperimentDesign",
            public_entrypoint_status="public",
            expected_inputs="PanelDataset; design kwargs; PowerAnalysis hooks",
            expected_outputs="Rerandomization design; ExperimentEvidence; MDE paths",
            inventory_status="implemented",
            tests_references=["tests/track_d/test_design_inventory_001.py"],
        ),
        InventoryRow(
            canonical_name="run_geo_experiment_design",
            method_type="orchestration",
            module_path="panel_exp/design/geo_runner.py",
            class_or_function_name="run_geo_experiment_design",
            public_entrypoint_status="internal",
            inventory_status="implemented",
        ),
        InventoryRow(
            canonical_name="ImpactAnalyzer",
            method_type="orchestration",
            module_path="panel_exp/impact.py",
            class_or_function_name="ImpactAnalyzer",
            public_entrypoint_status="public",
            expected_inputs="PanelDataset; inference mode string",
            inventory_status="implemented",
        ),
        InventoryRow(
            canonical_name="PowerAnalysis",
            method_type="orchestration",
            module_path="panel_exp/design/power.py",
            class_or_function_name="PowerAnalysis",
            public_entrypoint_status="public",
            known_gaps_from_existing_docs="Often TBRRidge agg2; mismatch vs SCM+JK readout (POW-001a)",
            inventory_status="implemented",
        ),
        InventoryRow(
            canonical_name="design_registry",
            method_type="registry",
            module_path="panel_exp/design/registry.py",
            class_or_function_name="DesignRegistry",
            inventory_status="implemented",
        ),
        InventoryRow(
            canonical_name="inference_registry",
            method_type="registry",
            module_path="panel_exp/inference/registry.py",
            class_or_function_name="InferenceRegistry",
            inventory_status="implemented",
        ),
        InventoryRow(
            canonical_name="estimator_maturity_catalog",
            method_type="registry",
            module_path="panel_exp/method_metadata.py",
            class_or_function_name="_ESTIMATOR_CATALOG",
            inventory_status="implemented",
        ),
        InventoryRow(
            canonical_name="governance_catalog_contract",
            method_type="registry",
            module_path="panel_exp/governance/catalog_contract.py",
            class_or_function_name="FORBIDDEN_ESTIMATOR_CATALOG_NAMES",
            known_gaps_from_existing_docs="Placebo forbidden as estimator name",
            inventory_status="implemented",
        ),
        InventoryRow(
            canonical_name="SCM_catalog_alias",
            aliases=["SyntheticControl", "SCM"],
            method_type="registry",
            module_path="panel_exp/method_metadata.py",
            class_or_function_name="SyntheticControl",
            inventory_status="duplicate_or_alias",
            known_gaps_from_existing_docs="Registry name SCM maps to class SyntheticControl",
        ),
        InventoryRow(
            canonical_name="TBR_vs_TBRRidge",
            aliases=["TBR", "TBRRidge"],
            method_type="estimator",
            module_path="panel_exp/methods/tbr.py",
            inventory_status="duplicate_or_alias",
            known_gaps_from_existing_docs="Product/language conflation risk (GAP-TBR-TBRR-001)",
        ),
    ]


def build_inventory() -> dict[str, Any]:
    designs = _design_rows()
    estimators = _estimator_rows()
    inference = _inference_rows()
    other = _orchestration_and_registry_rows()
    all_rows = designs + estimators + inference + other
    return {
        "document_id": "METHOD-CODE-INVENTORY-001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "panel_exp/validation/method_code_inventory_001.py",
        "discovery_sources": [
            "panel_exp.design.registry.get_design_registry",
            "panel_exp.method_metadata.estimator_catalog",
            "panel_exp.method_metadata.inference_mode_catalog",
            "manual wrapper/orchestration enrichment",
        ],
        "counts": {
            "design": len(designs),
            "estimator": len(estimators),
            "inference": len(inference),
            "orchestration_registry_alias": len(other),
            "total": len(all_rows),
        },
        "items": [r.to_dict() for r in all_rows],
    }


def default_archive_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "METHOD_CODE_INVENTORY_001.json"
    )


def main() -> None:
    payload = build_inventory()
    out = default_archive_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({payload['counts']['total']} items)")


if __name__ == "__main__":
    main()
