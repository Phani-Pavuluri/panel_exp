"""DESIGN-INVENTORY-001 — Code-derived design/assignment method inventory (research).

Discovers registered and implemented design methods from the repo (not roadmap
names) and classifies eligibility for D5-POW-001e null-FPR-at-scale checks.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from panel_exp.design.assign import (
    BalancedRandomization,
    CompleteRandomization,
    Rerandomization,
    StratifiedRandomization,
    ThinningDesign,
    greedy_match_markets,
)
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.design.geo_runner import run_geo_experiment_design
from panel_exp.design.registry import (
    LEGACY_GEO_RUN_DESIGN_SUPPORTED,
    get_design_registry,
)

Pow001eBucket = Literal[
    "tier_1_include_in_d5_pow_001e",
    "tier_2_separate_characterization",
    "tier_3_legacy_or_doc_only",
    "blocked_for_scm_jk_oc",
]


@dataclass(frozen=True)
class MethodRecord:
    method_id: str
    class_name: str
    module_path: str
    registry_name: str | None
    geo_run_supported: bool
    active_status: str
    entrypoints: tuple[str, ...]
    output_assignment_geometry: str
    single_cell_vs_multi_cell: str
    unit_level_vs_aggregated: str
    trims_or_excludes_markets: str
    changes_target_population: str
    uses_pre_period_only_for_matching: str
    supports_fixed_chronological_windows: str
    supports_whitelist_blacklist_constraints: str
    scm_unit_jackknife_compatibility: str
    d5_pow_001e_bucket: Pow001eBucket
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "method_id": self.method_id,
            "class_name": self.class_name,
            "module_path": self.module_path,
            "registry_name": self.registry_name,
            "geo_run_supported": self.geo_run_supported,
            "active_status": self.active_status,
            "entrypoints": list(self.entrypoints),
            "output_assignment_geometry": self.output_assignment_geometry,
            "single_cell_vs_multi_cell": self.single_cell_vs_multi_cell,
            "unit_level_vs_aggregated": self.unit_level_vs_aggregated,
            "trims_or_excludes_markets": self.trims_or_excludes_markets,
            "changes_target_population": self.changes_target_population,
            "uses_pre_period_only_for_matching": self.uses_pre_period_only_for_matching,
            "supports_fixed_chronological_windows": self.supports_fixed_chronological_windows,
            "supports_whitelist_blacklist_constraints": self.supports_whitelist_blacklist_constraints,
            "scm_unit_jackknife_compatibility": self.scm_unit_jackknife_compatibility,
            "d5_pow_001e_bucket": self.d5_pow_001e_bucket,
            "notes": self.notes,
        }


def _geo_tier1_records() -> list[MethodRecord]:
    """Five registry geo-supported randomizers (code-confirmed)."""
    common_entry = (
        "GeoExperimentDesign.run_design → get_design_registry().run → run_geo_experiment_design",
        "GeoExperimentDesign.create_design → Rerandomization.assign",
    )
    return [
        MethodRecord(
            method_id="greedy_match_markets",
            class_name="greedy_match_markets",
            module_path="panel_exp/design/assign.py",
            registry_name="greedy_match_markets",
            geo_run_supported=True,
            active_status="active_production_geo_default_base",
            entrypoints=common_entry
            + (
                "Direct: greedy_match_markets(...).assign(panel_data, pre_treatment_period=...)",
                "D5 harnesses: track_d_d5_pow_001a–d",
            ),
            output_assignment_geometry="dict[str, list[unit_id]] with keys control, test_0..test_{n-1}",
            single_cell_vs_multi_cell="both via n_test_grps parameter (default 1)",
            unit_level_vs_aggregated="unit_level_markets",
            trims_or_excludes_markets="blacklists remove units from pool; whitelists pin arms",
            changes_target_population="no; assigns subset of input markets to arms",
            uses_pre_period_only_for_matching="yes when pre_treatment_period passed (slice_wide_to_time_period)",
            supports_fixed_chronological_windows="yes for SCM+JK OC when harness uses fixed pre/post slice",
            supports_whitelist_blacklist_constraints="yes (constraints.py + prepare_constraint_context)",
            scm_unit_jackknife_compatibility="compatible (>=2 control units required at readout)",
            d5_pow_001e_bucket="tier_1_include_in_d5_pow_001e",
            notes="Production default base_randomizer_cls. D5-POW-001c/d baseline.",
        ),
        MethodRecord(
            method_id="completerandomization",
            class_name="CompleteRandomization",
            module_path="panel_exp/design/assign.py",
            registry_name="completerandomization",
            geo_run_supported=True,
            active_status="active_geo_registry",
            entrypoints=common_entry,
            output_assignment_geometry="dict control + test_* unit lists",
            single_cell_vs_multi_cell="both via n_test_grps",
            unit_level_vs_aggregated="unit_level_markets",
            trims_or_excludes_markets="constraint-driven exclusion only",
            changes_target_population="no",
            uses_pre_period_only_for_matching="no in assign(); geo_runner still passes pre_treatment_period for imbalance only when wrapped in Rerandomization",
            supports_fixed_chronological_windows="yes under D5 fixed-window harness",
            supports_whitelist_blacklist_constraints="yes",
            scm_unit_jackknife_compatibility="compatible",
            d5_pow_001e_bucket="tier_1_include_in_d5_pow_001e",
            notes="Bernoulli arm assignment with volume-free randomization.",
        ),
        MethodRecord(
            method_id="balancedrandomization",
            class_name="BalancedRandomization",
            module_path="panel_exp/design/assign.py",
            registry_name="balancedrandomization",
            geo_run_supported=True,
            active_status="active_geo_registry",
            entrypoints=common_entry,
            output_assignment_geometry="dict control + test_* unit lists",
            single_cell_vs_multi_cell="both via n_test_grps",
            unit_level_vs_aggregated="unit_level_markets",
            trims_or_excludes_markets="constraint-driven exclusion only",
            changes_target_population="no",
            uses_pre_period_only_for_matching="no in assign(); balancing uses full wide KPI totals",
            supports_fixed_chronological_windows="yes under D5 fixed-window harness",
            supports_whitelist_blacklist_constraints="yes",
            scm_unit_jackknife_compatibility="compatible",
            d5_pow_001e_bucket="tier_1_include_in_d5_pow_001e",
            notes="KPI volume-share balancing (not Bernoulli).",
        ),
        MethodRecord(
            method_id="stratifiedrandomization",
            class_name="StratifiedRandomization",
            module_path="panel_exp/design/assign.py",
            registry_name="stratifiedrandomization",
            geo_run_supported=True,
            active_status="active_geo_registry",
            entrypoints=common_entry,
            output_assignment_geometry="dict control + test_* unit lists",
            single_cell_vs_multi_cell="both via n_test_grps",
            unit_level_vs_aggregated="unit_level_markets",
            trims_or_excludes_markets="constraint-driven exclusion only",
            changes_target_population="no",
            uses_pre_period_only_for_matching="no; strata from unit mean KPI over full wide passed in",
            supports_fixed_chronological_windows="yes under D5 fixed-window harness",
            supports_whitelist_blacklist_constraints="yes",
            scm_unit_jackknife_compatibility="compatible",
            d5_pow_001e_bucket="tier_1_include_in_d5_pow_001e",
            notes="Percentile stratification + volume balancing within strata.",
        ),
        MethodRecord(
            method_id="thinningdesign",
            class_name="ThinningDesign",
            module_path="panel_exp/design/assign.py",
            registry_name="thinningdesign",
            geo_run_supported=True,
            active_status="active_geo_registry",
            entrypoints=common_entry,
            output_assignment_geometry="dict control + test_* unit lists",
            single_cell_vs_multi_cell="both via n_test_grps",
            unit_level_vs_aggregated="unit_level_markets",
            trims_or_excludes_markets="constraint-driven exclusion only",
            changes_target_population="no",
            uses_pre_period_only_for_matching="not sliced in assign(); kernel-thinning on provided wide",
            supports_fixed_chronological_windows="yes under D5 fixed-window harness",
            supports_whitelist_blacklist_constraints="yes",
            scm_unit_jackknife_compatibility="compatible",
            d5_pow_001e_bucket="tier_1_include_in_d5_pow_001e",
            notes="Kernel thinning design; geo-supported but less common in notebooks.",
        ),
    ]


def _orchestration_records() -> list[MethodRecord]:
    return [
        MethodRecord(
            method_id="rerandomization_wrapper",
            class_name="Rerandomization",
            module_path="panel_exp/design/assign.py",
            registry_name=None,
            geo_run_supported=True,
            active_status="active_production_geo_orchestration",
            entrypoints=(
                "GeoExperimentDesign.create_design() → Rerandomization",
                "Rerandomization.assign delegates to base_randomizer_cls",
            ),
            output_assignment_geometry="same as base randomizer (dict control + test_*)",
            single_cell_vs_multi_cell="inherits base n_test_grps",
            unit_level_vs_aggregated="unit_level_markets",
            trims_or_excludes_markets="inherits base",
            changes_target_population="no",
            uses_pre_period_only_for_matching="imbalance evaluated on pre_treatment_period slice when provided",
            supports_fixed_chronological_windows="yes for readout; geo MDE still uses PowerAnalysis sliding windows",
            supports_whitelist_blacklist_constraints="yes (forwarded to base)",
            scm_unit_jackknife_compatibility="compatible via unit-level assignment dict",
            d5_pow_001e_bucket="tier_1_include_in_d5_pow_001e",
            notes=(
                "Not a separate registry entry. Production path wraps geo-supported bases. "
                "001e must include rerandomization_wrapper+greedy_match_markets as distinct from bare greedy."
            ),
        ),
    ]


def _non_geo_records() -> list[MethodRecord]:
    return [
        MethodRecord(
            method_id="trimmedmatch",
            class_name="TrimmedMatchDesign",
            module_path="panel_exp/design/trimmed_match.py",
            registry_name="trimmedmatch",
            geo_run_supported=False,
            active_status="registered_not_geo_run_supported",
            entrypoints=("TrimmedMatchDesign.run_design()", "rerandomize_and_check"),
            output_assignment_geometry="paired geo subsets + trimmed pairs (not flat control/test dict)",
            single_cell_vs_multi_cell="multi test groups via n_test_groups",
            unit_level_vs_aggregated="unit_level but pair-structured",
            trims_or_excludes_markets="yes (trim_rate on pair differences)",
            changes_target_population="yes (pair selection + trim changes effective sample)",
            uses_pre_period_only_for_matching="splits Tp pairing vs Te evaluation internally",
            supports_fixed_chronological_windows="separate Te/Tp semantics",
            supports_whitelist_blacklist_constraints="no in registry spec",
            scm_unit_jackknife_compatibility="blocked (pair-trimmed estimand; classical power semantics)",
            d5_pow_001e_bucket="tier_2_separate_characterization",
            notes="Adjacent product design; not GeoExperimentDesign.run_design.",
        ),
        MethodRecord(
            method_id="supergeos",
            class_name="SupergeoModel",
            module_path="panel_exp/design/supergeos.py",
            registry_name="supergeos",
            geo_run_supported=False,
            active_status="registered_not_geo_run_supported",
            entrypoints=("SupergeoModel.run_model()",),
            output_assignment_geometry="supergeo clusters / MILP pairs (not control+test_* dict)",
            single_cell_vs_multi_cell="cluster-based",
            unit_level_vs_aggregated="aggregated supergeo units",
            trims_or_excludes_markets="min/max supergeo size constraints",
            changes_target_population="yes (markets merged into supergeos)",
            uses_pre_period_only_for_matching="no",
            supports_fixed_chronological_windows="no",
            supports_whitelist_blacklist_constraints="no",
            scm_unit_jackknife_compatibility="blocked (requires market-level unit panel)",
            d5_pow_001e_bucket="blocked_for_scm_jk_oc",
            notes="Use D5 aggregation geometry studies (001c-style), not 001e null FPR.",
        ),
        MethodRecord(
            method_id="quickblock",
            class_name="QuickBlock",
            module_path="panel_exp/design/quickblock.py",
            registry_name="quickblock",
            geo_run_supported=False,
            active_status="registered_legacy_api",
            entrypoints=("QuickBlock.assign_all", "Design.assign legacy path"),
            output_assignment_geometry="numpy assignment vector via assign_all (not geo dict)",
            single_cell_vs_multi_cell="single treatment vector",
            unit_level_vs_aggregated="unit_level",
            trims_or_excludes_markets="unknown / not integrated with constraints.py",
            changes_target_population="no",
            uses_pre_period_only_for_matching="no",
            supports_fixed_chronological_windows="not integrated with geo_runner",
            supports_whitelist_blacklist_constraints="no",
            scm_unit_jackknife_compatibility="blocked (no geo assignment dict contract)",
            d5_pow_001e_bucket="tier_3_legacy_or_doc_only",
            notes="Registered for discovery; not geo-run supported.",
        ),
        MethodRecord(
            method_id="matchedpair",
            class_name="MatchedPair",
            module_path="panel_exp/design/matched_pair.py",
            registry_name="matchedpair",
            geo_run_supported=False,
            active_status="registered_legacy_api",
            entrypoints=("MatchedPair.fit", "MatchedPair.assign(X)"),
            output_assignment_geometry="numpy vector over row index (graph matching)",
            single_cell_vs_multi_cell="paired blocks",
            unit_level_vs_aggregated="unit_level",
            trims_or_excludes_markets="no",
            changes_target_population="no",
            uses_pre_period_only_for_matching="matching_design_k uses time period arg",
            supports_fixed_chronological_windows="not geo_runner integrated",
            supports_whitelist_blacklist_constraints="no",
            scm_unit_jackknife_compatibility="blocked (non-dict API)",
            d5_pow_001e_bucket="tier_3_legacy_or_doc_only",
            notes="Mahalanobis matching graph; separate from geo design pipeline.",
        ),
    ]


def _configuration_notes() -> list[dict[str, Any]]:
    return [
        {
            "configuration_id": "multi_test_groups",
            "description": "n_test_grps > 1 on geo tier-1 methods (not a separate class).",
            "applies_to": [
                "greedy_match_markets",
                "completerandomization",
                "balancedrandomization",
                "stratifiedrandomization",
                "thinningdesign",
                "rerandomization_wrapper",
            ],
            "d5_pow_001e_bucket": "tier_1_include_in_d5_pow_001e",
            "notes": "Characterize as parameter sweep subset in 001e, not new method name.",
        },
        {
            "configuration_id": "geo_power_aggregated_panel",
            "description": "GeoExperimentDesign._run_power_analysis sums markets to 2-row panel.",
            "applies_to": ["GeoExperimentDesign MDE path only"],
            "d5_pow_001e_bucket": "blocked_for_scm_jk_oc",
            "notes": "Out of scope for 001e; covered by D5-POW-001c.",
        },
    ]


def build_design_inventory_001() -> dict[str, Any]:
    reg = get_design_registry()
    methods = _geo_tier1_records() + _orchestration_records() + _non_geo_records()

    confirmed_001e = [
        m.method_id
        for m in methods
        if m.d5_pow_001e_bucket == "tier_1_include_in_d5_pow_001e"
    ]

    return {
        "artifact_id": "DESIGN-INVENTORY-001",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "lane": "research",
        "discovery_sources": [
            "panel_exp/design/registry.py",
            "panel_exp/design/modes/__init__.py",
            "panel_exp/design/assign.py",
            "panel_exp/design/geo_experiment_design.py",
            "panel_exp/design/geo_runner.py",
        ],
        "registry_geo_supported_names": reg.geo_supported_names(),
        "legacy_geo_run_allowlist": sorted(LEGACY_GEO_RUN_DESIGN_SUPPORTED),
        "methods": [m.to_dict() for m in methods],
        "configuration_notes": _configuration_notes(),
        "confirmed_for_d5_pow_001e": confirmed_001e,
        "d5_pow_001e_harness_requirements": {
            "readout_instrument": "SyntheticControl+UnitJackKnife",
            "panel_geometry": "unit_level_markets",
            "window_construction": "fixed_chronological_pre_post (per D5-POW-001d)",
            "assignment_call": "assign(..., pre_treatment_period=TimePeriod(0, train_length-1), n_test_grps=...)",
            "null_fpr_semantics": "correct effect_lo=y-y_upper, effect_hi=y-y_lower (per D5-POW-001b)",
            "min_control_units": 2,
        },
        "excluded_from_d5_pow_001e": [
            m.method_id
            for m in methods
            if m.d5_pow_001e_bucket != "tier_1_include_in_d5_pow_001e"
        ],
        "track_e_forward": (
            "Promote E-POW-WIN-* diagnostics from D5-POW-001d and per-method null FPR "
            "from 001e into Track E E1/E2 suitability cards."
        ),
    }


def write_artifact(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
