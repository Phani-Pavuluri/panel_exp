# TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001` |
| **Artifact type** | `tbrridge_kfold_coverage_validation_audit` |
| **Status** | `completed` |
| **Scope** | `tbrridge_kfold_coverage_validation_requirements_audited_no_coverage_runtime_or_uncertainty` |
| **Base commit** | `1a9add4` (Add TBRRidge placebo calibration diagnostic runtime) |
| **Final verdict** | `tbrridge_kfold_coverage_validation_requirements_audited_no_coverage_runtime_or_uncertainty` |

**Depends on:** `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001` · `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001` · `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001` · `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001_REPORT.md`
- `docs/track_d/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001_REPORT.md`
- `docs/track_d/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001_REPORT.md`
- `docs/track_d/D5_TRUST_TBRRIDGE_KFOLD_001_REPORT.md`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`
- `docs/track_d/METHOD_PROMOTION_CANDIDATE_AUDIT_001.md`
- `panel_exp/validation/tbrridge_kfold_leakage_diagnostic_contract_001.py`
- `panel_exp/validation/tbrridge_kfold_leakage_diagnostic_runtime_001.py`
- `panel_exp/validation/tbrridge_placebo_calibration_diagnostic_contract_001.py`
- `panel_exp/validation/tbrridge_placebo_calibration_diagnostic_runtime_001.py`
- `panel_exp/validation/track_d_d5_trust_tbrridge_kfold_001.py`
- `docs/INFERENCE_READOUT_SEMANTICS_001.md`

---

## 3. Why coverage validation is now the right next question

TBRRidge now has two executable false-confidence gates:

1. **KFold leakage diagnostic runtime** — governs fold/temporal/geometry leakage before any KFold uncertainty surface is interpreted.
2. **Placebo calibration diagnostic runtime** — governs null construction, contamination, rank/tail instability, and placebo false-confidence risks before placebo or KFold significance claims.

Prior audits (`TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001`, `D5-TRUST-TBRRIDGE-KFOLD-001`) established that TBRRidge+KFold is **not causal-interval eligible** and that coverage was **unvalidated** relative to governed interval semantics. With leakage and placebo calibration gates in place, the next governable question is: **what evidence would be required before TBRRidge KFold could enter uncertainty-candidate review** — not whether to authorize uncertainty now.

**Core principle:** Coverage validation is only meaningful after fold leakage and placebo calibration are governed. This audit defines required evidence; it does not compute coverage, intervals, or authorization.

---

## 4. Relationship to KFold leakage runtime

`TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001` emits manifest-driven leakage diagnostic packets and blocks KFold uncertainty/CI/significance/coverage surfaces. Coverage validation must **consume** `leakage_diagnostic_report` as a prerequisite:

- **Blocked leakage** → coverage validation cannot start (`COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK`).
- **Diagnostic-ready with restrictions** → coverage validation may proceed only on explicitly compatible surfaces and fold geometries.
- **Clean leakage diagnostic** → coverage evidence building may proceed, but does not authorize uncertainty.

Coverage measurement without a governed leakage gate would reintroduce false confidence from temporal leakage, fold overlap, treated/control contamination, and unsupported multi-treated geometry.

---

## 5. Relationship to placebo calibration runtime

`TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001` governs placebo/null construction and false-confidence risks. Coverage validation must **consume** `placebo_calibration_diagnostic_report` because:

- Placebo-calibrated false-positive behavior is required to distinguish valid interval undercoverage from placebo rank/tail instability.
- Pre-period fit overconfidence and regularization-masked placebo failure can produce spurious "coverage pass" if placebo calibration is not clean or restricted.
- Placebo inference/significance surfaces remain blocked; placebo evidence informs **false-confidence calibration**, not promotion.

Blocked or restricted placebo calibration → `COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION` until remediated or explicitly scoped.

---

## 6. Current TBRRidge KFold readiness posture

| Layer | Posture |
|-------|---------|
| **Evidence ladder** | STAGE_2 diagnostic-only; uncertainty evidence building |
| **False-confidence audit** | `TBRRIDGE_UNCERTAINTY_EVIDENCE_BUILDING` for KFold |
| **Leakage gate** | Runtime implemented; KFold uncertainty surfaces blocked |
| **Placebo gate** | Runtime implemented; placebo inference surfaces blocked |
| **D5-TRUST-TBRRIDGE-KFOLD-001** | `tbrridge_kfold_not_causal_interval_eligible`; null interval coverage 100% with severe level bias; sign accuracy ~35% |
| **Promotion audit** | BRB/KFold RANK_0 blocked |
| **Production catalog** | KFold blocked; no catalog unblock |

TBRRidge KFold remains **diagnostic-only**. Coverage validation requirements are **not yet satisfied**.

---

## 7. Coverage validation evidence inventory

| Evidence artifact | Present in repo | Governed by | Gap |
|-------------------|-----------------|-------------|-----|
| `leakage_diagnostic_report` | Runtime packet schema | KFold leakage runtime | Must be attached to future coverage packets |
| `placebo_calibration_diagnostic_report` | Runtime packet schema | Placebo calibration runtime | Must be attached to future coverage packets |
| `interval_semantics_report` | Partial (`INFERENCE_READOUT_SEMANTICS_001`) | Readout contract | TBRRidge KFold-specific interval centering/width semantics undefined |
| `simulation_design_manifest` | D5-TRUST partial worlds | D5 battery | Not unified with governed coverage contract |
| `null_control_manifest` | D5 null worlds | D5 battery | Not linked to leakage/placebo gates |
| `positive_control_manifest` | D5 effect sweep partial | D5 battery | Recovery thresholds not governed |
| `empirical_coverage_report` | D5 archive only | Research OC | Not production-governed; scale mismatch documented |
| `false_positive_rate_report` | D5 partial | Research OC | Directional FPR conflated with scale |
| `placebo_calibrated_tail_report` | Missing | — | Required for future contract |
| `fold_geometry_regime_manifest` | Leakage contract fields | Leakage contract | Coverage regime grid not defined |
| `sample_size_regime_manifest` | Missing | — | Required |
| `regularization_grid_manifest` | Ridge alpha in D5 only | Research | Not governed sensitivity grid |

---

## 8. Coverage validation gap analysis

| Dimension | Current state | Gap | Blocker severity |
|-----------|---------------|-----|------------------|
| Nominal vs empirical coverage | D5 reports 100% null interval coverage with ~395 level bias | Interval semantics undefined; coverage on wrong estimand | **P0** |
| Undercoverage risk | Not governed | No stratified undercoverage battery across regimes | **P0** |
| Overcoverage / uninformative intervals | D5 shows wide intervals with poor sign accuracy | No governed width/informativeness policy | **P1** |
| False-positive rate under null | D5 interval type-I 0%; directional metrics unreliable | Must re-measure under governed semantics | **P0** |
| Directional false-signal rate | Sign accuracy ~35% overall | Threshold and estimand alignment missing | **P0** |
| Placebo-calibrated false confidence | Placebo runtime exists; no joint battery | Requires placebo-calibrated tail report | **P0** |
| Positive-control recovery | D5 clean_positive coverage ~91% | Not governed; scale mismatch | **P1** |
| Fold-geometry sensitivity | Leakage runtime detects; D5 fold variants | No coverage-by-geometry matrix | **P0** |
| Temporal leakage sensitivity | Leakage runtime | Must gate coverage runs | **P0** |
| Sample-size sensitivity | D5 small/large pre-period worlds | No governed sample-size regime manifest | **P1** |
| Donor-pool sensitivity | D5 small_donor_set world | No governed donor-pool manifest | **P1** |
| Outlier-week sensitivity | Leakage/placebo flags only | No coverage under outlier regimes | **P1** |
| Regularization sensitivity | D5 ridge_dominant world | No governed lambda grid manifest | **P1** |
| Interval symmetry/asymmetry | Undefined for TBRRidge KFold | `interval_semantics_report` required | **P0** |
| Metric/estimand alignment | D5 level_mean_relative_percent_injection | Must align with governed ATT estimand | **P0** |
| Aggregate/pooled misuse | Multicell runtime blocks pooled | Aggregate claims remain blocked | **P0** |

---

## 9. Required simulation/validation design

Future coverage validation must use a **governed simulation design manifest** specifying:

- **World taxonomy:** clean null, placebo null, weak/strong signal, serial dependence, heteroskedasticity, regime shift, post-treatment shock, pre-trend violation, poor pre-fit, small/large pre-period, small donor pool, ridge-dominant, outlier-week influence.
- **Effect injection:** synthetic effect sizes on governed estimand (not ad hoc level-percent injection unless explicitly declared).
- **Fold schemes:** single-treated only until multi-treated geometry policy is explicit; include rolling/expanding time-series KFold and blocked pre-period holdouts; prohibit sklearn random unit KFold for causal readout.
- **Replication:** minimum replicate count per world×regime cell for stable coverage/FPR estimates.
- **Dependency ordering:** each run must attach leakage and placebo diagnostic reports; blocked diagnostics abort coverage measurement for that cell.
- **Lineage:** `lineage_provenance_manifest` on every simulation cell.

---

## 10. Required null-control evidence

`null_control_manifest` must define:

- Zero-effect worlds with known null DGP.
- Governed interval semantics before measuring coverage or FPR.
- **Measured outputs:** `empirical_coverage_report`, `false_positive_rate_report`, `directional_error_report`.
- **Conservative thresholds (future review):** null interval coverage within tolerance of nominal only if interval centering bias is within governed bound; directional false-signal rate must be documented, not assumed from interval exclusion alone.
- **Blocked:** using null "100% coverage" as promotion evidence when point bias or sign accuracy fails (per D5-TRUST finding).

---

## 11. Required positive-control evidence

`positive_control_manifest` must define:

- Injected effects at weak, moderate, and strong magnitudes on governed estimand.
- **Measured outputs:** coverage of true effect, sign recovery rate, interval width relative to effect size.
- **Conservative thresholds:** positive-control recovery must be demonstrated across fold-geometry and sample-size regimes, not a single clean-positive cell.
- Positive-control pass does **not** authorize production readout or catalog unblock.

---

## 12. Required placebo-calibrated false-positive evidence

`placebo_calibrated_false_positive_requirements` must include:

- Joint use of `placebo_calibration_diagnostic_report` and `placebo_calibrated_tail_report`.
- Placebo rank/tail stability under null before interpreting KFold interval tail behavior.
- Documentation of placebo-calibrated false confidence: intervals that appear tight because pre-period fit or regularization masks placebo failure.
- Placebo evidence informs **diagnostic restriction**, not placebo p-value or significance claims.

---

## 13. Required fold-geometry regimes

`fold_geometry_regime_manifest` must enumerate:

| Regime | Requirement |
|--------|-------------|
| Single-treated unit panel | Primary governed geometry |
| Rolling time-series KFold | Expanding/rolling pre-period blocks |
| Blocked pre-period holdout | Legacy KFold path characterization |
| Shared-control families | Requires geometry declaration; blocked if undeclared |
| Multi-treated | **Blocked** until explicit geometry policy and leakage diagnostic ready |
| Aggregate/pooled | **Blocked** — separate pooled estimand semantics required |

Coverage must be reported **per regime**, not pooled across incompatible geometries.

---

## 14. Required sample-size regimes

`sample_size_regime_manifest` must include:

- Small vs large pre-period length.
- Small vs adequate donor/control pool size.
- Small-sample fold degeneracy cells (aligned with leakage `SMALL_SAMPLE_FOLD_DEGENERACY`).
- Minimum per-fold unit/time counts declared before coverage measurement.

---

## 15. Required interval-semantics definition

`interval_semantics_report` must define before any coverage measurement:

- **Centering:** what quantity the interval is centered on (ATT point, fold-dispersion surrogate, debiased level shift).
- **Width construction:** fold CV dispersion vs explicit confidence level; symmetry vs asymmetry.
- **Estimand alignment:** interval must target the same estimand as the point readout and simulation truth.
- **Prohibited semantics:** using fold dispersion as causal CI without explicit contract; using level-percent injection truth with mismatched readout scale.
- **Gap today:** `INFERENCE_READOUT_SEMANTICS_001` exists but TBRRidge KFold-specific interval semantics are **not closed** → `COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS` until defined.

---

## 16. Required failure packet semantics for future contract/runtime

Future coverage contract/runtime failure packets should include:

| Field | Purpose |
|-------|---------|
| `failure_code` | Standardized blocker (e.g. `LEAKAGE_BLOCKED`, `PLACEBO_MISCALIBRATED`, `INTERVAL_SEMANTICS_UNDEFINED`, `UNDERCOVERAGE_DETECTED`, `DIRECTIONAL_FPR_EXCEEDED`) |
| `failure_reason` | Human-readable summary |
| `coverage_validation_status` | One of readiness statuses below |
| `detected_coverage_risks` | Taxonomy of failed dimensions |
| `missing_evidence` | Required manifests not present |
| `required_remediation` | Retry category |
| `leakage_diagnostic_status` | Propagated from leakage runtime |
| `placebo_calibration_status` | Propagated from placebo runtime |
| `lineage_manifest` | Provenance |

No failure packet may authorize production readout or method promotion.

---

## 17. Stop/go thresholds for moving toward uncertainty-candidate review

Conservative **go** prerequisites (all required for `COVERAGE_VALIDATION_READY_FOR_UNCERTAINTY_CANDIDATE_REVIEW`):

1. Leakage diagnostic **clean** or **restricted with explicitly compatible surfaces** for the evaluated geometry.
2. Placebo calibration diagnostic **clean** or **restricted** with documented placebo-calibrated tail behavior.
3. `interval_semantics_report` **defined and validated** for TBRRidge KFold.
4. `simulation_design_manifest` **approved** with governed world×regime grid.
5. Null-control FPR and coverage measured under governed semantics across fold-geometry, sample-size, donor-pool, and regularization regimes.
6. Positive-control recovery measured on governed estimand (not a single world).
7. Directional false-signal rate measured and within documented diagnostic bounds.
8. Undercoverage and overcoverage risks characterized per regime.
9. Aggregate/pooled claims **remain blocked** unless separate pooled estimand semantics exist.
10. No production readout until method promotion and production compatibility chains approve later.

**Stop** conditions (immediate block):

- Any blocking leakage or placebo diagnostic on the evaluation path.
- Missing interval semantics.
- Missing simulation design manifest.
- Scale/estimand mismatch between truth and readout.
- Multi-treated or aggregate geometry without explicit policy.

---

## 18. Blockers that keep TBRRidge KFold diagnostic-only

| Blocker | Source |
|---------|--------|
| `GEOMETRY_MISSPECIFICATION` | Multi-treated unsupported; aggregate blocked |
| `FOLD_LEAKAGE` | Must pass leakage runtime for coverage path |
| `PLACEBO_SEMANTICS_UNGOVERNED` | Must pass placebo calibration runtime |
| `COVERAGE_UNVALIDATED` | This audit — evidence not yet built |
| `INTERVAL_SEMANTICS_UNDEFINED` | TBRRidge KFold centering/width not governed |
| `ESTIMAND_UNRESOLVED` | Level-percent vs ATT alignment |
| `INFERENCE_DEFECT` | D5 level bias ~395; sign accuracy ~35% |
| `METHOD_PROMOTION_INELIGIBLE` | RANK_0 in promotion audit |
| `PRODUCTION_CATALOG_BLOCKED` | Catalog blocklist enforced |

---

## 19. Future artifact sequence

| Order | Artifact | Purpose |
|-------|----------|---------|
| **1 (next)** | `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001` | Define coverage statuses, evidence taxonomy, failure semantics |
| **2** | `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001` | Governed coverage evidence packet runtime (no inference computation) |
| **3 (later)** | `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001` | Restricted uncertainty-candidate review after evidence built |

**Alternative:** `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`

---

## 20. Authorization boundary

| Flag | Value |
|------|-------|
| `coverage_validation_audit_completed` | true |
| `coverage_evidence_taxonomy_defined` | true |
| `interval_semantics_gap_documented` | true |
| `simulation_design_requirements_defined` | true |
| `null_control_requirements_defined` | true |
| `positive_control_requirements_defined` | true |
| `placebo_calibrated_false_positive_requirements_defined` | true |
| `fold_geometry_regime_requirements_defined` | true |
| `sample_size_regime_requirements_defined` | true |
| `stop_go_criteria_defined` | true |
| `future_contract_recommended` | true |
| `coverage_runtime_implemented` | false |
| `kfold_inference_implemented` | false |
| `placebo_inference_implemented` | false |
| `uncertainty_computed` | false |
| `coverage_computed` | false |
| `confidence_interval_computed` | false |
| `method_promoted` | false |
| `production_readout_authorized` | false |

---

## 21. Validation results

- Summary JSON valid
- Governance tests assert taxonomy, requirements, stop/go criteria, forbidden flags
- Safety grep: no forbidden `true` computation/promotion flags in audit artifacts

---

## 22. Known limitations

- Audit is descriptive and governance-only; does not re-run D5-TRUST-TBRRIDGE-KFOLD-001 batteries.
- Does not prescribe numeric coverage tolerance bands — deferred to future contract after interval semantics closure.
- Does not integrate with estimator execution or TrustReport authorization.
- BRB coverage path is out of scope; this audit is KFold-specific.

---

## Appendix A. Coverage validation readiness statuses

| Status | Meaning |
|--------|---------|
| `COVERAGE_VALIDATION_NOT_STARTED` | No coverage evidence pipeline initiated |
| `COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK` | Leakage diagnostic blocked or incompatible |
| `COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION` | Placebo calibration blocked or restricted beyond compatible scope |
| `COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS` | Interval centering/width/estimand not defined |
| `COVERAGE_VALIDATION_BLOCKED_BY_MISSING_SIMULATION_DESIGN` | Simulation design manifest missing |
| `COVERAGE_VALIDATION_EVIDENCE_BUILDING` | Governed evidence collection in progress |
| `COVERAGE_VALIDATION_READY_FOR_CONTRACT` | Requirements audited; contract may be defined |
| `COVERAGE_VALIDATION_READY_FOR_RUNTIME` | Contract complete; runtime may be implemented |
| `COVERAGE_VALIDATION_READY_FOR_UNCERTAINTY_CANDIDATE_REVIEW` | Evidence sufficient for restricted uncertainty-candidate review — **not production approval** |
| `COVERAGE_VALIDATION_REQUIRES_METHOD_REVIEW` | Conflicting evidence or policy violation |

**No status grants production approval.**

---

## Appendix B. Required evidence taxonomy

`leakage_diagnostic_report` · `placebo_calibration_diagnostic_report` · `interval_semantics_report` · `simulation_design_manifest` · `null_control_manifest` · `positive_control_manifest` · `synthetic_effect_injection_manifest` · `fold_geometry_regime_manifest` · `sample_size_regime_manifest` · `regularization_grid_manifest` · `donor_pool_sensitivity_report` · `outlier_sensitivity_report` · `empirical_coverage_report` · `false_positive_rate_report` · `directional_error_report` · `placebo_calibrated_tail_report` · `failure_packet_manifest` · `lineage_provenance_manifest`

---

## Appendix C. Coverage validation dimensions audited

Nominal vs empirical coverage · undercoverage risk · overcoverage / uninformative interval risk · false-positive rate under null · directional false-signal rate · placebo-calibrated false confidence · positive-control recovery behavior · fold-geometry sensitivity · treated/control contamination sensitivity · temporal leakage sensitivity · sample-size sensitivity · donor/control pool size sensitivity · outlier-week sensitivity · regularization sensitivity · interval symmetry/asymmetry semantics · metric/estimand alignment · aggregate/pooled misuse risk
