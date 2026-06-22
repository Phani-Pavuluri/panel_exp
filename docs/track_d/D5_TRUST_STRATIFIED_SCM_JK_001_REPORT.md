# D5-TRUST-STRATIFIED-SCM-JK-001 Report

## 1. Executive summary

This artifact evaluates stratified SCM+UnitJackknife behavior.
It does not authorize TrustReport.
It does not perform the full TrustReport eligibility reassessment.
It does not validate unrelated estimator/inference combinations.

**Verdict:** `stratified_scm_jk_diagnostic_only`
**Aggregate status:** `DIAGNOSTIC_ONLY`

**Aggregate stratified readout is characterization only, not a governed pooled causal estimand.** Per-stratum marginal intervals may be shown under diagnostic/restricted semantics; aggregate volume-weighted readout does not authorize causal claims unless a later pooled/stratified estimand artifact is built.

## 2. Prior DCM-008 status

DCM-008 was characterized_with_restrictions; stratified SCM+JK statistical behavior unresolved.

## 3. Scope

Stratified randomization + SCM + UnitJackknife per stratum across geometry variants and synthetic worlds.

## 4. Non-goals

No TrustReport authorization; no production algorithm changes; no pooled stratified estimand validation.

## 5. Stratified design geometry

Strata from adaptive percentile stratification on pre-period covariate; donor pools evaluated per policy.

## 6. Stratum identity contract

Per-stratum panels include only treated units in stratum plus eligible donors; other-stratum treated excluded.

## 7. Donor-pool policy

Within-stratum, global, and partial-overlap donor constructions evaluated.

## 8. Estimand and scale contract

Canonical scale: `level_mean_relative_percent_injection`.

## 9. SCM+JK inference path

Primary: `STRATIFIED-PERSTRATUM-SCM-JK`. SCM fit mode: `per_stratum_panel_aggregate_treated`.

## 10. Worlds

all_strata_null, homogeneous_positive, heterogeneous_positive, one_stratum_positive, mixed_sign, weak_effects, strong_effects, serial_correlation, high_serial_correlation, heteroskedasticity_by_stratum, poor_prefit_one_stratum, poor_prefit_all_strata, stratum_specific_shock, common_shock, donor_contamination_one_stratum, donor_contamination_cross_strata, small_donor_one_stratum, high_imbalance, missing_tiny_stratum, weight_dominated_stratum

## 11. Effect patterns

[[0.0, 0.0], [0.08, 0.08], [0.08, 0.0], [0.08, -0.05], [0.03, 0.03], [0.12, 0.0], [0.0, 0.0, 0.0], [0.08, 0.08, 0.08], [0.08, 0.0, 0.0], [0.08, -0.05, 0.03], [0.12, 0.03, 0.0]]

## 12. Geometry variants

[
  {
    "geometry_id": "balanced_two_strata",
    "n_strata": 2,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "balanced_three_strata",
    "n_strata": 3,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "unequal_strata_sizes",
    "n_strata": 3,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "small_stratum",
    "n_strata": 4,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "large_stratum",
    "n_strata": 2,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "one_weak_stratum",
    "n_strata": 2,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "one_bad_prefit_stratum",
    "n_strata": 2,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "stratum_specific_shock",
    "n_strata": 2,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "cross_stratum_common_shock",
    "n_strata": 2,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "stratum_weight_imbalance",
    "n_strata": 2,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "donor_pool_within_stratum_only",
    "n_strata": 2,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "donor_pool_global",
    "n_strata": 2,
    "donor_pool_policy": "global",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "donor_pool_partial_overlap",
    "n_strata": 2,
    "donor_pool_policy": "partial_overlap",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "treated_absent_in_one_stratum_negative_control",
    "n_strata": 4,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": true,
    "geometry_failure_reason": null
  },
  {
    "geometry_id": "control_absent_in_one_stratum_negative_control",
    "n_strata": 2,
    "donor_pool_policy": "within_stratum_only",
    "geometry_supported": false,
    "geometry_failure_reason": "control_absent_in_stratum_not_supported"
  }
]

## 13. Run counts/runtime

{
  "total_runs": 1222,
  "successful_runs": 1222,
  "failed_runs": 0,
  "stratum_level_results": 2774,
  "runtime_seconds": 18.59
}

## 14. Stratum-level point behavior

Mean bias by stratum: {"0": -0.023118968216703395, "1": 1.0500910471297438, "2": 0.5310917091523775, "3": 1.183144795917224}

## 15. Stratum-level interval behavior

Coverage by geometry: {
  "balanced_two_strata": {
    "n_stratum_results": 184,
    "n_ok": 184,
    "coverage": 0.8586956521739131,
    "type_i_error": 0.16666666666666666,
    "mean_bias": 1.5606680172813916,
    "mean_interval_width": 19.18318581545758
  },
  "balanced_three_strata": {
    "n_stratum_results": 270,
    "n_ok": 270,
    "coverage": 0.8925925925925926,
    "type_i_error": 0.1388888888888889,
    "mean_bias": 0.34745704342633493,
    "mean_interval_width": 22.64772079907962
  },
  "unequal_strata_sizes": {
    "n_stratum_results": 240,
    "n_ok": 240,
    "coverage": 0.8708333333333333,
    "type_i_error": 0.1488095238095238,
    "mean_bias": 0.5778616413863246,
    "mean_interval_width": 25.006421208427387
  },
  "small_stratum": {
    "n_stratum_results": 320,
    "n_ok": 160,
    "coverage": 0.88125,
    "type_i_error": 0.14814814814814814,
    "mean_bias": 0.374430871130698,
    "mean_interval_width": 32.75614583688156
  },
  "large_stratum": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.88125,
    "type_i_error": 0.20454545454545456,
    "mean_bias": 0.6688500194730916,
    "mean_interval_width": 12.62704562401943
  },
  "one_weak_stratum": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.85625,
    "type_i_error": 0.19318181818181818,
    "mean_bias": 1.8204657918962326,
    "mean_interval_width": 20.254054681992933
  },
  "one_bad_prefit_stratum": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.8875,
    "type_i_error": 0.19318181818181818,
    "mean_bias": 0.27027605640715946,
    "mean_interval_width": 23.29858205382383
  },
  "stratum_specific_shock": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.85625,
    "type_i_error": 0.19318181818181818,
    "mean_bias": 0.8460116601157157,
    "mean_interval_width": 20.194354286884277
  },
  "cross_stratum_common_shock": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.8875,
    "type_i_error": 0.1590909090909091,
    "mean_bias": 0.22439846266474134,
    "mean_interval_width": 19.645109096930973
  },
  "stratum_weight_imbalance": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.9125,
    "type_i_error": 0.10227272727272728,
    "mean_bias": -2.3154590428325212,
    "mean_interval_width": 131.90204810665742
  },
  "donor_pool_within_stratum_only": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.85625,
    "type_i_error": 0.19318181818181818,
    "mean_bias": 0.2380166814322917,

## 16. Aggregate point behavior

{
  "n_runs": 1142,
  "aggregate_coverage": 0.8966725043782837,
  "aggregate_type_i": 0.2601010101010101,
  "mean_aggregate_bias": 0.8689791463496583,
  "weight_dominance_rate": 0.06129597197898424,
  "aggregate_claim_blocked_rate": 1.0
}

## 17. Aggregate interval behavior

Aggregate intervals are volume-weighted stratum means for characterization only; not valid pooled estimand.

## 18. Null type-I

{
  "0": 0.17424242424242425,
  "1": 0.17341772151898735,
  "2": 0.11788617886178862,
  "3": 0.11875
}

Aggregate type-I: 0.2601010101010101

## 19. Coverage

{
  "0": {
    "n_stratum_results": 1142,
    "n_ok": 1142,
    "coverage": 0.8984238178633975,
    "type_i_error": 0.17424242424242425,
    "mean_bias": -0.023118968216703395,
    "mean_interval_width": 27.4670131466576
  },
  "1": {
    "n_stratum_results": 1142,
    "n_ok": 1062,
    "coverage": 0.8559322033898306,
    "type_i_error": 0.17341772151898735,
    "mean_bias": 1.0500910471297438,
    "mean_interval_width": 28.02022317939696
  },
  "2": {
    "n_stratum_results": 330,
    "n_ok": 250,
    "coverage": 0.884,
    "type_i_error": 0.11788617886178862,
    "mean_bias": 0.5310917091523775,
    "mean_interval_width": 22.382952949932854
  },
  "3": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.88125,
    "type_i_error": 0.11875,
    "mean_bias": 1.183144795917224,
    "mean_interval_width": 29.819541371703384
  }
}

## 20. Heterogeneous-effect findings

See heterogeneous_positive, mixed_sign, and effect-pattern worlds.

## 21. Small-stratum findings

{
  "n_stratum_results": 320,
  "n_ok": 160,
  "coverage": 0.88125,
  "type_i_error": 0.14814814814814814,
  "mean_bias": 0.374430871130698,
  "mean_interval_width": 32.75614583688156
}

## 22. Weight-dominance findings

{
  "dominance_rate": 0.06129597197898424,
  "geometries": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.9125,
    "type_i_error": 0.10227272727272728,
    "mean_bias": -2.3154590428325212,
    "mean_interval_width": 131.90204810665742
  }
}

## 23. Donor-pool findings

{
  "within_stratum": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.85625,
    "type_i_error": 0.19318181818181818,
    "mean_bias": 0.2380166814322917,
    "mean_interval_width": 18.07356285564443
  },
  "global": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.9,
    "type_i_error": 0.1590909090909091,
    "mean_bias": 0.6101750324910598,
    "mean_interval_width": 13.69397838070023
  },
  "partial_overlap": {
    "n_stratum_results": 160,
    "n_ok": 160,
    "coverage": 0.88125,
    "type_i_error": 0.18181818181818182,
    "mean_bias": 1.5412956038799472,
    "mean_interval_width": 10.97483877289792
  }
}

## 24. Poor-prefit findings

See poor_prefit_one_stratum and poor_prefit_all_strata worlds.

## 25. Shock/contamination findings

See stratum_specific_shock, common_shock, donor_contamination worlds.

## 26. Policy comparisons

See summary `policy_comparisons`.

## 27. Root-cause determination

Aggregate readout and weight-dominance limits are semantic/geometry; not isolated code defects unless confirmed.

## 28. Production-defect decision

{
  "decision": "geometry_or_semantic_limitation",
  "rationale": "Stratified SCM+JK uses per-stratum panels with volume-weighted aggregate characterization only; aggregate intervals are not a valid pooled estimand. Small-stratum instability and weight dominance are structural support limits."
}

## 29. Semantic classification

{
  "verdict": "stratified_scm_jk_diagnostic_only",
  "aggregate_status": "DIAGNOSTIC_ONLY",
  "path_decisions": {
    "balanced_strata": "per_stratum_marginal_allowed",
    "unequal_strata": "restricted",
    "small_stratum": "blocked_or_diagnostic",
    "weight_dominant_stratum": "aggregate_blocked",
    "global_donor_pool": "restricted_vs_within_stratum",
    "within_stratum_donor_pool": "preferred",
    "aggregate_readout": "characterization_only_blocked_for_claims",
    "per_stratum_readout": "diagnostic_or_restricted"
  },
  "supported_roles": [
    "per_stratum_diagnostic",
    "per_stratum_restricted_interval"
  ],
  "unsupported_roles": [
    "aggregate_causal_claim",
    "trust_report",
    "pooled_stratified_estimand"
  ]
}

## 30. TrustReport implications

{
  "dcm_008": "stratified_restricted_no_trustreport_authorization",
  "prior_status": "characterized_with_restrictions",
  "reassessment_required": true,
  "full_reassessment_deferred": false,
  "next_checkpoint": "FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT"
}

## 31. Authorization status

{
  "trust_report_authorized": false,
  "trust_report_ready": false,
  "trust_report_authorized_count": 0
}

## 32. Investigation lifecycle update

Consumed `INV-STRATIFIED-SCM-JK-TRUSTREPORT-DISPOSITION-001` → RESOLVED (DIAGNOSTIC_ONLY).

## 33. Remaining limitations

Evaluates stratified design × SCM+UnitJackknife; does not validate unrelated estimator/inference combinations.; Does not authorize TrustReport.; Does not perform the full TrustReport eligibility reassessment.; SCM is fit per-stratum panel (aggregate treated units in stratum); not per-unit SCM within stratum.; Aggregate intervals are volume-weighted stratum interval means — not a valid pooled stratified estimand.; Stratified assignment support does not imply valid aggregate or multi-cell decisioning.; Marginal per-stratum coverage does not authorize aggregate/pooled causal claims.; Distinct from DCM-006 multi-cell conclusions; stratified-specific behavior tested here.

## 34. Governance verdict

**`stratified_scm_jk_diagnostic_only`**

## Residual Issues and Handoff

**Resolved in this artifact:**
- INV-STRATIFIED-SCM-JK-TRUSTREPORT-DISPOSITION-001

**New investigations opened:** none

**Existing investigations updated:**
- INV-STRATIFIED-SCM-JK-TRUSTREPORT-DISPOSITION-001 → RESOLVED (DIAGNOSTIC_ONLY)

**Deferred issues:**
- INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001
- INV-MULTICELL-MULTIPLICITY-CALIBRATION-001

**Explicit exclusions:**
- DCM-006 multi-cell conclusions reused without stratified test

**Revisit trigger:** FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT DCM-008 row

**Required decision checkpoint:** FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT

**Next artifact:** FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT

