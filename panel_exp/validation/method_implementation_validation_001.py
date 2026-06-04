"""METHOD-IMPLEMENTATION-VALIDATION-001 — read-only implementation fidelity register.

Loads Layer 1 inventory + Layer 2 literature alignment; emits structured
implementation-validation rows from code inspection findings (no OC, no mutations).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LAYER1_JSON = _REPO_ROOT / "docs/track_d/archives/METHOD_CODE_INVENTORY_001.json"
_LAYER2_JSON = _REPO_ROOT / "docs/track_d/archives/METHOD_LITERATURE_ALIGNMENT_001.json"

ImplementationValidationStatus = Literal[
    "implementation_validated",
    "implementation_validated_with_caveats",
    "implementation_gap",
    "architecture_gap",
    "identity_collision",
    "unsupported_geometry_not_blocked",
    "requires_code_review",
    "research_only_not_validated",
    "deprecated_or_quarantine_candidate",
]

MethodType = Literal[
    "design",
    "estimator",
    "inference",
    "wrapper",
    "orchestration",
    "registry",
]


@dataclass
class ImplementationValidationRow:
    method_family: str
    implementation_name: str
    method_type: MethodType
    module_path: str
    entrypoint: str
    literature_alignment_status: str
    implementation_validation_status: ImplementationValidationStatus
    identity_fidelity: str
    estimand_fidelity: str
    geometry_fidelity: str
    inference_semantics_fidelity: str
    orchestration_fidelity: str
    known_gaps: list[str] = field(default_factory=list)
    evidence_sources: list[str] = field(default_factory=list)
    recommended_fix_or_next_check: str = ""
    layer4_statistical_validation_needed: list[str] = field(default_factory=list)
    promotion_allowed: bool = False
    trust_role_allowed: bool = False
    layer2_family_id: str = ""
    inventory_canonical_names: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_source(rel_path: str) -> str:
    return (_REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _source_has(rel_path: str, needle: str) -> bool:
    return needle in _read_source(rel_path)


def load_layer1() -> dict[str, Any]:
    return json.loads(_LAYER1_JSON.read_text(encoding="utf-8"))


def load_layer2() -> dict[str, Any]:
    return json.loads(_LAYER2_JSON.read_text(encoding="utf-8"))


def _row(
    *,
    family_id: str,
    lit_status: str,
    impl_status: ImplementationValidationStatus,
    implementation_name: str,
    method_type: MethodType,
    module_path: str,
    entrypoint: str,
    identity: str,
    estimand: str,
    geometry: str,
    inference_sem: str,
    orchestration: str,
    gaps: list[str],
    evidence: list[str],
    fix: str,
    layer4: list[str],
    inventory_names: list[str] | None = None,
) -> ImplementationValidationRow:
    return ImplementationValidationRow(
        method_family=family_id,
        layer2_family_id=family_id,
        literature_alignment_status=lit_status,
        implementation_validation_status=impl_status,
        implementation_name=implementation_name,
        method_type=method_type,
        module_path=module_path,
        entrypoint=entrypoint,
        identity_fidelity=identity,
        estimand_fidelity=estimand,
        geometry_fidelity=geometry,
        inference_semantics_fidelity=inference_sem,
        orchestration_fidelity=orchestration,
        known_gaps=gaps,
        evidence_sources=evidence,
        recommended_fix_or_next_check=fix,
        layer4_statistical_validation_needed=layer4,
        inventory_canonical_names=inventory_names or [implementation_name],
    )


def implementation_validation_rows() -> list[ImplementationValidationRow]:
    """Structured findings from code inspection + prior audit reconciliation."""
    osqp_penalty_unused = _source_has(
        "panel_exp/methods/scm.py",
        "not used in the OSQP solve",
    )
    geo_pre_slice = _source_has(
        "panel_exp/design/geo_runner.py",
        "pre_treatment_period = TimePeriod(start=0, end=geo.train_length)",
    )
    gmm_pre_slice = _source_has(
        "panel_exp/design/assign.py",
        "wide = slice_wide_to_time_period(wide, pre_treatment_period)",
    )
    tbr_aggregate_assert = _source_has(
        "panel_exp/methods/tbr.py",
        "TBR requires treated units to be pre-aggregated",
    )

    rows: list[ImplementationValidationRow] = [
        _row(
            family_id="DES-GMM-001",
            lit_status="partially_aligned",
            impl_status=(
                "implementation_validated_with_caveats"
                if geo_pre_slice and gmm_pre_slice
                else "implementation_gap"
            ),
            implementation_name="greedy_match_markets",
            method_type="design",
            module_path="panel_exp/design/assign.py",
            entrypoint="greedy_match_markets.assign → geo_runner.run_geo_experiment_design",
            identity="Class name matches registry greedy_match_markets; aliases gmm/greedymatchmarkets",
            estimand="Assignment only; KPI-mass treatment_probability — not unit-count 50/50",
            geometry="Unit assignment dict; multi-cell via n_test_grps",
            inference_sem="n/a at design stage",
            orchestration=(
                "GeoExperimentDesign passes pre_treatment_period when train_length>0"
                if geo_pre_slice
                else "geo_runner may omit pre_treatment_period"
            ),
            gaps=(
                ["INV-D1-001: direct assign() without pre_treatment_period uses full wide"]
                if gmm_pre_slice
                else ["INV-D1-001: pre-period slice not found in greedy_match_markets"]
            ),
            evidence=["panel_exp/design/geo_runner.py", "panel_exp/design/assign.py", "TRACK_D_D1"],
            fix="Layer 3 audit: all production callers pass pre_treatment_period; document bypass risk",
            layer4=["D5-POW-001e balance; null-monitor sensitivity with post periods in wide"],
            inventory_names=["greedy_match_markets"],
        ),
        _row(
            family_id="DES-RERAND-001",
            lit_status="aligned_pending_validation",
            impl_status="implementation_validated_with_caveats",
            implementation_name="rerandomization_wrapper",
            method_type="wrapper",
            module_path="panel_exp/design/assign.py",
            entrypoint="Rerandomization.assign; GeoExperimentDesign.create_design",
            identity="Wrapper not in design registry list_names(); collides with rerandomization concept",
            estimand="Assignment under balance threshold — not ATT",
            geometry="Inherits base randomizer geometry",
            inference_sem="n/a",
            orchestration="Imbalance evaluated on pre_treatment_period slice when provided (assign.py)",
            gaps=["Production path may differ from bare greedy_match_markets"],
            evidence=["panel_exp/design/assign.py", "DESIGN_INVENTORY_001"],
            fix="Document wrapper dispatch vs bare tier-1 in GeoExperimentDesign",
            layer4=["D5-POW-001e rerandomization vs bare sensitivity"],
            inventory_names=["rerandomization_wrapper"],
        ),
        _row(
            family_id="DES-TIER1-RAND-001",
            lit_status="aligned_pending_validation",
            impl_status="implementation_validated_with_caveats",
            implementation_name="tier1_randomizers",
            method_type="design",
            module_path="panel_exp/design/modes/",
            entrypoint="register_builtin_designs → geo_runner",
            identity="Five geo_run_supported randomizers share registry dispatch",
            estimand="Probabilistic assignment — not ATT",
            geometry="Unit dict; geo_run_supported=True",
            inference_sem="n/a",
            orchestration="Same geo_runner pre_treatment_period behavior as DES-GMM-001",
            gaps=["Design–readout bridge: randomization ≠ matched-market analysis story"],
            evidence=["panel_exp/design/registry.py", "D5-POW-001e"],
            fix="Per-mode constraint/KPI semantics checklist",
            layer4=["001e SCM+JK reference path per tier-1 arm"],
            inventory_names=[
                "completerandomization",
                "balancedrandomization",
                "stratifiedrandomization",
                "thinningdesign",
            ],
        ),
        _row(
            family_id="DES-SUPERGEO-001",
            lit_status="literature_mismatch",
            impl_status="unsupported_geometry_not_blocked",
            implementation_name="supergeos",
            method_type="design",
            module_path="panel_exp/design/supergeos.py",
            entrypoint="TrimmedMatch/Supergeo registry handler; not geo_run_supported",
            identity="supergeos registry name; output not flat assignment dict for SCM+JK",
            estimand="Cluster/pair estimand undefined for flat ImpactAnalyzer readout",
            geometry="MILP cluster geometry — blocked for 001e flat SCM+JK (A29)",
            inference_sem="n/a",
            orchestration="geo_run_supported=False — silent block only if caller respects registry",
            gaps=["F-GEO-003: no unit-panel bridge", "COMBO A29 invalid flat readout"],
            evidence=["D5-DES-SUPERGEO-001", "METHOD_SOUNDNESS §2.C"],
            fix="Geometry bridge ADR before Layer 4 combo OC",
            layer4=["D5-DES-SUPERGEO-001 replay after bridge"],
            inventory_names=["supergeos"],
        ),
        _row(
            family_id="DES-TRIM-001",
            lit_status="literature_mismatch",
            impl_status="unsupported_geometry_not_blocked",
            implementation_name="trimmedmatch",
            method_type="design",
            module_path="panel_exp/design/trimmed_match.py",
            entrypoint="registry; not geo_run_supported",
            identity="trimmedmatch / trimmed_match aliases",
            estimand="Tp/Te pair population — not unit-panel SCM estimand without bridge",
            geometry="Pair geometry — A30 blocked for flat SCM+JK",
            inference_sem="n/a",
            orchestration="geo_run_supported=False",
            gaps=["F-GEO-004 adapter missing"],
            evidence=["D5-DES-TRIM-001", "AUDIT-010 A30"],
            fix="F-GEO-004 bridge before SCM readout",
            layer4=["D5-DES-TRIM-001"],
            inventory_names=["trimmedmatch"],
        ),
        _row(
            family_id="DES-LEGACY-BLOCK-001",
            lit_status="unclear_requires_review",
            impl_status="deprecated_or_quarantine_candidate",
            implementation_name="quickblock_matchedpair",
            method_type="design",
            module_path="panel_exp/design/quickblock.py; matched_pair.py",
            entrypoint="registry only; not geo_run",
            identity="Legacy APIs registered but not geo orchestration path",
            estimand="Unclear product estimand",
            geometry="assignment_dict; geo_run_supported=False",
            inference_sem="n/a",
            orchestration="Not wired through GeoExperimentDesign production path",
            gaps=["No geo-run; sparse tests"],
            evidence=["METHOD_CODE_INVENTORY_001"],
            fix="Quarantine unless revival charter",
            layer4=[],
            inventory_names=["quickblock", "matchedpair"],
        ),
        _row(
            family_id="EST-SCM-001",
            lit_status="partially_aligned",
            impl_status="implementation_validated_with_caveats",
            implementation_name="SyntheticControlCVXPY",
            method_type="estimator",
            module_path="panel_exp/methods/scm.py",
            entrypoint="ImpactAnalyzer.run_analysis; catalog SCM/SyntheticControlCVXPY",
            identity="SCM catalog alias maps to multiple classes — identity_collision risk",
            estimand="Counterfactual gap; level vs relative depends on results export path (G7)",
            geometry="Unit panel; invalid on 2-row aggregate without guard",
            inference_sem="Multiple inference modes wired; Placebo falsification not CI",
            orchestration="method_metadata inference_support lists JK, JKP, BRB, etc.",
            gaps=(
                [
                    "G4: OSQP SCM leg may diverge from documented pre-RMSE objective",
                    "full_model=True post-period fit leakage risk (INV-D2-001)",
                ]
                if osqp_penalty_unused
                else ["full_model leakage risk"]
            ),
            evidence=["panel_exp/methods/scm.py", "TRACK_D_D2", "D5-POW-001e"],
            fix="D2 donor + full_model audit; disambiguate SCM alias in metadata",
            layer4=["SCM+JK null FPR; Placebo single-treated scope"],
            inventory_names=["SyntheticControlCVXPY", "SCM"],
        ),
        _row(
            family_id="EST-SCM-001",
            lit_status="partially_aligned",
            impl_status="implementation_gap",
            implementation_name="SyntheticControl",
            method_type="estimator",
            module_path="panel_exp/methods/scm.py",
            entrypoint="SyntheticControl scipy optimizer path",
            identity="Distinct from SyntheticControlCVXPY but shared SCM catalog name",
            estimand="Same ATT intent; scipy vs OSQP may differ numerically",
            geometry="Unit panel",
            inference_sem="Same registry inference list as CVXPY path",
            orchestration="Production often prefers CVXPY; scipy less exercised",
            gaps=["Numerical parity CVXPY vs scipy not guaranteed"],
            evidence=["D2 inventory", "test_scm.py"],
            fix="Document production default path; parity spot-check",
            layer4=["Recovery runner SCM arms"],
            inventory_names=["SCM"],
        ),
        _row(
            family_id="EST-SCM-001",
            lit_status="not_literature_backed",
            impl_status="deprecated_or_quarantine_candidate",
            implementation_name="synthetic_control_function",
            method_type="estimator",
            module_path="panel_exp/methods/synthetic_control.py",
            entrypoint="legacy function — not in estimator catalog",
            identity="Legacy scipy helper outside ImpactAnalyzer catalog",
            estimand="Undeclared in catalog",
            geometry="Caller-dependent",
            inference_sem="n/a",
            orchestration="Not dispatched via method_metadata catalog",
            gaps=["Dead or parallel path risk"],
            evidence=["METHOD_CODE_INVENTORY_001"],
            fix="Quarantine documentation",
            layer4=[],
            inventory_names=["synthetic_control_function"],
        ),
        _row(
            family_id="EST-AUGSYNTH-001",
            lit_status="partially_aligned",
            impl_status="implementation_gap",
            implementation_name="AugSynthCVXPY",
            method_type="estimator",
            module_path="panel_exp/methods/scm.py",
            entrypoint="AugSynthCVXPY.run_analysis",
            identity="ASCM colloquial name; catalog AugSynthCVXPY",
            estimand="Augmented gap; pooled multi-cell blocked by ADR semantics only",
            geometry="Unit panel per cell",
            inference_sem="JK unsafe strata; Conformal blocked pending interval redesign",
            orchestration="Export guards for full_model/Placebo documented in track_d harnesses",
            gaps=[
                "G1: penalty_strength stored but unused on OSQP SCM path"
                if osqp_penalty_unused
                else "G1: verify penalty on OSQP path",
                "G4/G7/G8: SCM leg mismatch; level vs relative; hull proxy",
            ],
            evidence=[
                "AUGSYNTH_IMPLEMENTATION_FIDELITY_AUDIT_001",
                "D5-INST-AUGSYNTH-ASCM-003",
                "D5-INF-AUGSYNTH-JK-CALIBRATION-001",
            ],
            fix="Close G1–G8 fidelity items; per-cell metadata enforcement",
            layer4=["ASCM-003 strata; JK calibration; Conformal POSTFIX non-promotion"],
            inventory_names=["AugSynthCVXPY"],
        ),
        _row(
            family_id="EST-AUGSYNTH-001",
            lit_status="unclear_requires_review",
            impl_status="research_only_not_validated",
            implementation_name="AugSynth",
            method_type="estimator",
            module_path="panel_exp/methods/scm.py",
            entrypoint="AugSynth non-CVXPY",
            identity="Distinct class; UNVALIDATED maturity in metadata",
            estimand="Claimed ASCM but not production charter path",
            geometry="Unit panel",
            inference_sem="point/Kfold/Conformal in catalog — not fidelity-reviewed",
            orchestration="F-CAT-003 deprioritized",
            gaps=["Not CVXPY fidelity path"],
            evidence=["method_metadata.py", "F-CAT-003"],
            fix="Quarantine from production wiring",
            layer4=[],
            inventory_names=["AugSynth"],
        ),
        _row(
            family_id="EST-TBR-001",
            lit_status="aligned_pending_validation",
            impl_status=(
                "implementation_validated_with_caveats"
                if tbr_aggregate_assert
                else "requires_code_review"
            ),
            implementation_name="TBR",
            method_type="estimator",
            module_path="panel_exp/methods/tbr.py",
            entrypoint="TBR.run_analysis",
            identity="TBR name distinct from TBRRidge but product conflation risk (GAP-TBR-TBRR-001)",
            estimand="Aggregate lift; cumulative vs relative via INV-003 export",
            geometry="Enforced 1 treated + 1 control pre-aggregated rows",
            inference_sem="point/JK/JKP/Kfold in catalog — aggregate-only",
            orchestration="PowerAnalysis may use TBRRidge agg2 — not TBR class",
            gaps=["identity_collision with TBRRidge in product docs"],
            evidence=["D5-INST-TBR-001", "D4 POW-EST-001"],
            fix="TBR aggregate estimand registry mapping",
            layer4=["D5-INST-TBR-001 ratio stability"],
            inventory_names=["TBR"],
        ),
        _row(
            family_id="EST-TBRRIDGE-001",
            lit_status="partially_aligned",
            impl_status="implementation_gap",
            implementation_name="TBRRidge",
            method_type="estimator",
            module_path="panel_exp/methods/tbr.py",
            entrypoint="TBRRidge.run_analysis",
            identity="TBRRidge vs TBR — high collision risk in naming/docs",
            estimand="Ridge-regularized lift; unit vs agg2 paths differ",
            geometry="Unit panel + agg2 power path — not equivalent to unit SCM+JK",
            inference_sem="JK/JKP high null FPR documented; Bayesian registry ≠ MCMC",
            orchestration="Primary OC path for BRB/Kfold/TS-Kfold",
            gaps=["POW-EST-001: PowerAnalysis agg2 vs SCM unit readout", "INV-015 Bayesian handler"],
            evidence=["D5-INST-TBRRIDGE-001/003", "AUDIT-010 A16/A21"],
            fix="JK/JKP pivot audit; disambiguate Bayesian registry",
            layer4=["TBRRIDGE-003 null FPR/coverage", "BRB positive OC"],
            inventory_names=["TBRRidge"],
        ),
        _row(
            family_id="EST-DID-001",
            lit_status="partially_aligned",
            impl_status="implementation_validated_with_caveats",
            implementation_name="DID",
            method_type="estimator",
            module_path="panel_exp/methods/DID.py",
            entrypoint="DID.run_analysis (embedded bootstrap)",
            identity="DID distinct from SyntheticDID",
            estimand="ATT / cumulative ATT; relative CI deferred DEF-003",
            geometry="Panel treated/control units",
            inference_sem="Native bootstrap not BlockResidualBootstrap registry mode",
            orchestration="ImpactAnalyzer must route to estimator-native bootstrap",
            gaps=["Bootstrap naming collision BRB vs DID embedded", "Relative ATT CI unsupported"],
            evidence=["D3 INF-010", "AUDIT-010 A25", "DEF-003"],
            fix="Document DID bootstrap dispatch; interval policy ADR",
            layer4=["A25 pretrend + bootstrap characterization"],
            inventory_names=["DID"],
        ),
        _row(
            family_id="EST-SDID-001",
            lit_status="unclear_requires_review",
            impl_status="research_only_not_validated",
            implementation_name="SyntheticDID",
            method_type="estimator",
            module_path="panel_exp/methods/synthetic_did.py",
            entrypoint="research catalog; validation runner skip",
            identity="SyntheticDID registered; research_only maturity",
            estimand="SDID ATT — fidelity vs Arkhangelsky et al. not proven",
            geometry="Panel timing structure",
            inference_sem="point only in catalog",
            orchestration="Skipped in validation runner",
            gaps=["No Layer 3 fidelity proof"],
            evidence=["synthetic_did_test.py", "CV-001"],
            fix="Fidelity spike or quarantine",
            layer4=["Research charter OC only"],
            inventory_names=["SyntheticDID"],
        ),
        _row(
            family_id="EST-RESEARCH-BAYES-001",
            lit_status="unclear_requires_review",
            impl_status="research_only_not_validated",
            implementation_name="BayesianTBR",
            method_type="estimator",
            module_path="panel_exp/methods/bayesian_regression.py",
            entrypoint="JAX optional MCMC",
            identity="BayesianTBR ≠ registry inference Bayesian shortcut on TBRRidge",
            estimand="Posterior lift per BSTS literature if MCMC run",
            geometry="Aggregate/unit per config",
            inference_sem="Bayesian mode in catalog — credible intervals",
            orchestration="Optional deps; not production metadata path",
            gaps=["INV-015 registry Bayesian on TBRRidge not NUTS"],
            evidence=["INV-015", "jax_test_helpers"],
            fix="Block registry misuse vs class MCMC",
            layer4=["RTP-001 charter only"],
            inventory_names=["BayesianTBR", "BayesianTBRHorseShoe", "TBRAutoSARIMAX"],
        ),
        _row(
            family_id="EST-RESEARCH-OTHER-001",
            lit_status="not_literature_backed",
            impl_status="research_only_not_validated",
            implementation_name="TROP_MTGP",
            method_type="estimator",
            module_path="panel_exp/methods/triply_robust_est.py; mtgp.py",
            entrypoint="research_only catalog",
            identity="TROP / MTGP in catalog without production inference surface",
            estimand="Undeclared for product",
            geometry="Research configs",
            inference_sem="point/Bayesian only",
            orchestration="validation runner skip/limit",
            gaps=["No implementation validation charter"],
            evidence=["METHOD_CODE_INVENTORY_001"],
            fix="Quarantine list confirmation",
            layer4=[],
            inventory_names=["TROP", "MTGP"],
        ),
        _row(
            family_id="INF-POINT-001",
            lit_status="aligned_pending_validation",
            impl_status="implementation_validated",
            implementation_name="point_estimate",
            method_type="inference",
            module_path="panel_exp/inference/modes/impl.py",
            entrypoint="run_point_estimate",
            identity="Registry point_estimate — clear diagnostic role",
            estimand="Point effect only",
            geometry="Estimator-dependent",
            inference_sem="No intervals — must not be labeled CI",
            orchestration="InferenceRegistry dispatch",
            gaps=[],
            evidence=["D3 INF-001"],
            fix="Metadata guard against promotion as uncertainty",
            layer4=[],
            inventory_names=["point_estimate"],
        ),
        _row(
            family_id="INF-JK-001",
            lit_status="partially_aligned",
            impl_status="implementation_gap",
            implementation_name="UnitJackKnife",
            method_type="inference",
            module_path="panel_exp/inference/unit_jackknife.py",
            entrypoint="run_unit_jackknife",
            identity="UnitJackKnife — not generic jackknife on aggregates",
            estimand="JK pivot on unit residuals — null-monitor role for SCM in evidence",
            geometry="Blocked invalid on 2-row aggregate SCM/AugSynth in audits",
            inference_sem="lower/upper percentiles on leave-one-unit distribution",
            orchestration="Paired SCM, AugSynthCVXPY, TBRRidge in COMBO matrix",
            gaps=["TBRRidge+JK high null FPR", "AugSynth unsafe strata", "aggregate geometry not always blocked in code"],
            evidence=["D3", "D5-INF-002", "JK calibration-001", "AUDIT-010 A16/A26"],
            fix="Hard-block JK on aggregate 2-row; stratum gates for AugSynth",
            layer4=["001e/ASCM-002 null FPR", "TBRRIDGE-003"],
            inventory_names=["UnitJackKnife"],
        ),
        _row(
            family_id="INF-JKP-001",
            lit_status="partially_aligned",
            impl_status="implementation_gap",
            implementation_name="JKP",
            method_type="inference",
            module_path="panel_exp/inference/modes/impl.py",
            entrypoint="run_jkp",
            identity="JKP registry name vs JackKnifePlus literature",
            estimand="Predictive interval pivot — pooled-CF on TBRRidge disputed",
            geometry="Unit panel",
            inference_sem="impl applies bounds to results y_lower/y_upper post-period",
            orchestration="SCM, TBR, TBRRidge wired",
            gaps=["TBRRidge pooled-CF semantics (~29% null FPR A21)"],
            evidence=["D5-TBRRIDGE-003", "impl.py run_jkp"],
            fix="Pivot definition audit on TBRRidge",
            layer4=["TBRRIDGE-003 coverage"],
            inventory_names=["JKP"],
        ),
        _row(
            family_id="INF-KFOLD-001",
            lit_status="implementation_specific_extension",
            impl_status="implementation_validated_with_caveats",
            implementation_name="Kfold",
            method_type="inference",
            module_path="panel_exp/inference/k_fold.py",
            entrypoint="run_kfold",
            identity="Kfold diagnostic bands — not literature-primary SCM inference",
            estimand="Diagnostic band around point effect",
            geometry="Unit blocking; multi-treated guards in OC",
            inference_sem="confidence_interval semantics in metadata — diagnostic role",
            orchestration="Multiple estimators in catalog",
            gaps=["Must not substitute for JK null monitor"],
            evidence=["D5-KFOLD", "AUDIT-010"],
            fix="Role taxonomy in Layer 5 only",
            layer4=["KFOLD null FPR archives"],
            inventory_names=["Kfold"],
        ),
        _row(
            family_id="INF-TSKFOLD-001",
            lit_status="partially_aligned",
            impl_status="implementation_validated_with_caveats",
            implementation_name="TimeSeriesKfold",
            method_type="inference",
            module_path="panel_exp/inference/modes/impl.py",
            entrypoint="run_timeseries_kfold",
            identity="Distinct from Kfold — temporal blocks",
            estimand="Diagnostic band",
            geometry="TBRRidge-primary in OC",
            inference_sem="F-INF-003 POSTFIX addressed orientation; verify half-width sign",
            orchestration="Registry separate from Kfold",
            gaps=["Historical negative half-width issue — confirm POSTFIX in all paths"],
            evidence=["F_INF_003", "AUDIT-010 A19"],
            fix="Re-verify orientation after POSTFIX on all export paths",
            layer4=["A19 null FPR post-POSTFIX"],
            inventory_names=["TimeSeriesKfold"],
        ),
        _row(
            family_id="INF-BRB-001",
            lit_status="aligned_pending_validation",
            impl_status="implementation_validated_with_caveats",
            implementation_name="BlockResidualBootstrap",
            method_type="inference",
            module_path="panel_exp/inference/block_residual_bootstrap.py",
            entrypoint="run_block_residual_bootstrap",
            identity="BRB acronym — not named Bootstrap in registry",
            estimand="CI from block residual bootstrap",
            geometry="TBRRidge-primary validated",
            inference_sem="effect_ci_lower/upper cumulative fields in impl",
            orchestration="Mis-pairing with AugSynth invalid (COMBO)",
            gaps=["DEF-002 bound ordering historically — verify fixed"],
            evidence=["D5-TBRRIDGE-001", "DEF-002", "D3"],
            fix="Confirm bound ordering; catalog invalid pairs",
            layer4=["TBRRIDGE-001 positive OC"],
            inventory_names=["BlockResidualBootstrap"],
        ),
        _row(
            family_id="INF-CONFORMAL-001",
            lit_status="partially_aligned",
            impl_status="implementation_gap",
            implementation_name="Conformal",
            method_type="inference",
            module_path="panel_exp/inference/conformal.py",
            entrypoint="run_conformal",
            identity="Conformal registry — not generic bootstrap CI",
            estimand="Conformal predictive band — exchangeability assumption",
            geometry="AugSynthCVXPY, TBRRidge wired",
            inference_sem="F-INF-003 orientation fix; AugSynth+Conformal blocked for new design",
            orchestration="Not governed export for AugSynth ADR-001",
            gaps=["IMPL-CONF-001: band construction mismatch on AugSynth", "Panel dependence"],
            evidence=["D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001", "F_INF_003"],
            fix="New interval design before re-enabling AugSynth+Conformal",
            layer4=["POSTFIX archives — non-promotion"],
            inventory_names=["Conformal"],
        ),
        _row(
            family_id="INF-PLACEBO-001",
            lit_status="aligned_pending_validation",
            impl_status="implementation_validated_with_caveats",
            implementation_name="Placebo",
            method_type="inference",
            module_path="panel_exp/inference/placebo.py",
            entrypoint="run_placebo",
            identity="Placebo inference-only — forbidden as estimator catalog name (governance)",
            estimand="Falsification / placebo distribution — not confirmatory CI",
            geometry="Single-treated scope in PLACEBO-001; multi-treated blocked",
            inference_sem="placebo_band semantics",
            orchestration="SCM primary; not AugSynth/TBR in COMBO",
            gaps=["Multi-treated 100% block rate A28 — by design"],
            evidence=["D5-INST-PLACEBO-001", "AUDIT-010 A27/A28"],
            fix="Maintain falsification taxonomy ADR",
            layer4=["PLACEBO-001 replay"],
            inventory_names=["Placebo"],
        ),
        _row(
            family_id="INF-BAYES-REG-001",
            lit_status="literature_mismatch",
            impl_status="architecture_gap",
            implementation_name="Bayesian",
            method_type="inference",
            module_path="panel_exp/inference/modes/impl.py",
            entrypoint="run_bayesian",
            identity="Registry Bayesian handler ≠ BayesianTBR MCMC (INV-015)",
            estimand="Credible intervals only if full posterior sampling",
            geometry="TBRRidge wired — research estimators optional",
            inference_sem="impl uses jnp.quantile on y_hat samples — may not be MCMC posterior",
            orchestration="A20 blocked on production misuse",
            gaps=["literature_mismatch on TBRRidge prod path"],
            evidence=["INV-015", "D3 INF-008", "AUDIT-010 A20"],
            fix="Disallow registry Bayesian on TBRRidge or implement full MCMC",
            layer4=[],
            inventory_names=["Bayesian"],
        ),
        _row(
            family_id="INF-DID-BOOT-001",
            lit_status="partially_aligned",
            impl_status="implementation_validated_with_caveats",
            implementation_name="DID_native_bootstrap",
            method_type="inference",
            module_path="panel_exp/methods/DID.py",
            entrypoint="DID.run_analysis embedded bootstrap",
            identity="Not in inference registry — distinct from BRB",
            estimand="Cumulative ATT intervals per DEF-003",
            geometry="DID panel only",
            inference_sem="Separate from registry BlockResidualBootstrap naming",
            orchestration="ImpactAnalyzer must not confuse with BRB dispatch",
            gaps=["Relative ATT CI unsupported"],
            evidence=["D3 INF-010", "DEF-003", "A25"],
            fix="Document embedded bootstrap routing",
            layer4=["A25 characterization"],
            inventory_names=["DID_native_bootstrap"],
        ),
        _row(
            family_id="ORCH-001",
            lit_status="partially_aligned",
            impl_status="implementation_validated_with_caveats",
            implementation_name="GeoExperimentDesign",
            method_type="orchestration",
            module_path="panel_exp/design/geo_experiment_design.py",
            entrypoint="create_design → assign → validate_design",
            identity="Orchestrates design registry + Rerandomization wrapper",
            estimand="Design + power evidence — not estimator estimand",
            geometry="Passes n_test_grps; train_length drives pre_treatment_period in geo_runner",
            inference_sem="n/a",
            orchestration="Stable registry names when train_length configured",
            gaps=["Power vs analysis estimator mismatch POW-EST-001"],
            evidence=["geo_runner.py", "DESIGN_INVENTORY_001"],
            fix="End-to-end design→analysis contract test",
            layer4=["001e design×readout"],
            inventory_names=["GeoExperimentDesign"],
        ),
        _row(
            family_id="ORCH-002",
            lit_status="partially_aligned",
            impl_status="architecture_gap",
            implementation_name="ImpactAnalyzer",
            method_type="orchestration",
            module_path="panel_exp/impact.py",
            entrypoint="run_analysis inference dispatch",
            identity="Central estimator + inference router",
            estimand="Delegates to estimator — export semantics vary by combo",
            geometry="Must enforce geometry per estimator asserts",
            inference_sem="Dispatches inference registry; DID bootstrap special case",
            orchestration="Method names must match catalog keys in archives",
            gaps=["Invalid combos may fail late — prefer explicit pairing matrix Layer 5"],
            evidence=["impact.py", "AUDIT-010", "COMBO-001"],
            fix="Explicit invalid-pair guards where COMBO marks invalid_by_interface",
            layer4=["Combo matrix Layer 5"],
            inventory_names=["ImpactAnalyzer"],
        ),
    ]
    return rows


KNOWN_GAP_REGISTER: tuple[str, ...] = (
    "INV-D1-001",
    "G1",
    "G4",
    "G7",
    "G8",
    "IMPL-CONF-001",
    "GAP-TBR-TBRR-001",
    "INV-D2-001",
    "INV-015",
    "F-GEO-003",
    "F-GEO-004",
    "POW-EST-001",
    "F-INF-003",
    "IMPL-JK-001",
)


def build_implementation_validation() -> dict[str, Any]:
    layer1 = load_layer1()
    layer2 = load_layer2()
    rows = implementation_validation_rows()
    by_status: dict[str, int] = {}
    for r in rows:
        by_status[r.implementation_validation_status] = (
            by_status.get(r.implementation_validation_status, 0) + 1
        )
    family_ids_l2 = {f["family_id"] for f in layer2["families"]}
    family_ids_l3 = {r.method_family for r in rows}
    orch_extra = {"ORCH-001", "ORCH-002"}
    missing = family_ids_l2 - family_ids_l3
    return {
        "document_id": "METHOD-IMPLEMENTATION-VALIDATION-001",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "panel_exp/validation/method_implementation_validation_001.py",
        "parent_artifacts": [
            layer1["document_id"],
            layer2["document_id"],
        ],
        "implementation_validation_status_values": [
            "implementation_validated",
            "implementation_validated_with_caveats",
            "implementation_gap",
            "architecture_gap",
            "identity_collision",
            "unsupported_geometry_not_blocked",
            "requires_code_review",
            "research_only_not_validated",
            "deprecated_or_quarantine_candidate",
        ],
        "known_gap_register": list(KNOWN_GAP_REGISTER),
        "counts": {
            "rows_total": len(rows),
            "by_status": by_status,
            "layer2_families": len(family_ids_l2),
            "layer2_families_covered": len(family_ids_l2 - missing),
            "orchestration_rows": len(orch_extra & family_ids_l3),
        },
        "coverage": {
            "missing_layer2_family_ids": sorted(missing),
            "extra_family_ids": sorted(family_ids_l3 - family_ids_l2 - orch_extra),
        },
        "rows": [r.to_dict() for r in rows],
    }


def assert_layer2_coverage(payload: dict[str, Any]) -> None:
    missing = payload["coverage"]["missing_layer2_family_ids"]
    if missing:
        raise ValueError(f"Layer 2 families without Layer 3 rows: {missing}")


def write_archive(path: Path | None = None) -> Path:
    payload = build_implementation_validation()
    assert_layer2_coverage(payload)
    if path is None:
        path = (
            _REPO_ROOT
            / "docs"
            / "track_d"
            / "archives"
            / "METHOD_IMPLEMENTATION_VALIDATION_001.json"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    out = write_archive()
    n = build_implementation_validation()["counts"]["rows_total"]
    print(f"Wrote {out} ({n} rows)")


if __name__ == "__main__":
    main()
