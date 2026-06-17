# Inference Readout Semantics 001

**Document ID:** INFERENCE-READOUT-SEMANTICS-001  
**Title:** Inference Readout Semantics 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` post-D5 semantic contract  
**Artifact type:** Documentation / governance — **no code changes**  
**Date:** 2026-06-09  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) · [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md)

**Guardrails:** No promotion · no TrustReport role assignment · no CalibrationSignal/MMM/LLM authorization · no governed-readout claim · no method upgrade in this artifact

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Inference Readout Semantics 001 |
| Status | **Accepted** |
| Scope | GeoX / `panel_exp` post-D5 semantic contract |
| Artifact type | Documentation / governance |

This document is the first post-D5 enhancement artifact. It standardizes how inference outputs are **interpreted** before any method may be upgraded, rerun for suitability framework v2, assigned a TrustReport role, or considered under future CalibrationSignal eligibility policy.

---

## 2. Purpose

Level B characterization (D5-STAT) established **callable behavior** and **structural interval sanity** under controlled synthetic worlds. Product integration requires a **shared semantic contract** so that:

- Point estimates name their **estimand**, **scale**, and **post-period aggregation**.
- Intervals name their **uncertainty target** and **coverage target**.
- Null decisions and directional signals use **separate, explicit rules**.
- Prediction/forecast/resampling intervals are **not** treated as causal intervals by default.

This artifact converts D5 findings into governed **interpretation rules**. It does **not** promote any method or authorize production use.

---

## 3. Why this artifact exists

The D5 queue through **`D5-STAT-TBRRIDGE-INF-001`** shows the bottleneck is not only whether code runs; it is **what the inferential output means**.

| D5 artifact | Finding driving this contract |
|-------------|------------------------------|
| **SCM-JK** | Structurally clean intervals (orientation, half-width) but **elevated stress-null false positives** (~23% weak signal, ~33% post-shock). JK interval target vs scored truth needs explicit naming. |
| **AugSynth point** | Strong injected **point** recovery; **no uncertainty semantics** — intervals not applicable on characterized path. |
| **TBR aggregate** | Excellent injected recovery (~1.0 ratios, 0% sign errors) but **high null directional false signal** (0.87–1.0) — point mass without calibrated null decision rule. |
| **DID bootstrap** | Clean interval orientation; **0% cumulative coverage** vs injected cumulative truth — interval target vs scored truth **misaligned**. |
| **MCELL per-cell** | Cell/method identity and no-pooling preserved; **post-shock one-cell** sign-error caveat (~0.63) — per-cell readout must not imply pooled causal readout. |
| **TBRRidge inference** | Mixed characterization: KFold/TSKFold **leakage risk** and outcome-scale vs percent-injection mismatch; BRB diverges from KFold at null; Conformal **blocked** on multi-treated unit panel. |

**Conclusion:** Without canonical readout semantics, validation batteries score incompatible quantities, coverage claims are ambiguous, and enhancement work cannot be prioritized safely.

---

## 4. Definitions

| Term | Definition |
|------|------------|
| **Observed outcome** | Post-assignment realized outcome `Y` for treated units (or aggregate treated series), on stated time index and scale. |
| **Counterfactual outcome** | Estimated untreated outcome `Ŷ` (or synthetic control / forecast counterfactual) for the same unit(s), period(s), and scale. |
| **Point estimate** | Scalar or vector summary of treatment effect derived from `Y` and `Ŷ` (or method-native ATT object). Must declare estimand and scale. |
| **Period-level effect** | Effect for a single post-treatment time index: typically `Y_t − Ŷ_t` (possibly per unit, then aggregated). |
| **Cumulative effect** | Sum (or integral) of period-level effects over the post window: `Σ_t (Y_t − Ŷ_t)` or method-native cumulative ATT. |
| **Average post-period effect** | Mean of period-level effects over the post window: `(1/T_post) Σ_t (Y_t − Ŷ_t)`. |
| **Fractional lift** | Relative change vs counterfactual baseline, e.g. `(Y − Ŷ) / Ŷ` or percent injection parameter in D5 fixtures. |
| **Level lift** | Absolute change on outcome scale: `Y − Ŷ` (or injected level delta). |
| **Incremental outcome** | Additive treatment increment on outcome scale; may coincide with level lift when counterfactual is additive. |
| **Interval** | Ordered pair `[L, U]` (or per-period bands) intended to bracket a stated target with stated probability under stated assumptions. |
| **Interval target** | Random quantity the interval is designed to cover (e.g., cumulative ATT, average period effect, forecast error). |
| **Coverage target** | The quantity against which empirical coverage is scored in validation (must match interval target unless transformation is documented). |
| **Null decision** | Formal rule for rejecting / not rejecting a **null effect** hypothesis on the stated estimand and scale. |
| **Directional signal** | Weaker statement that point estimate (or interval exclusion of zero) suggests positive or negative direction on stated scale — **not** equivalent to null rejection or causal evidence. |
| **Prediction uncertainty** | Variability of `Ŷ` or residuals under model fit / cross-validation / holdout — may include in-sample and sampling instability. |
| **Causal uncertainty** | Uncertainty attributed to the **causal estimand** (ATT/LATE-style quantity) under design and identification assumptions — requires explicit justification. |
| **Design uncertainty** | Uncertainty from assignment, donor eligibility, or geometry choice (e.g., which units enter panel). |
| **Model uncertainty** | Uncertainty from estimator specification (donor weights, ridge penalty, SARIMAX order). |
| **Split uncertainty** | Variability induced by train/test or fold split policy (KFold, TimeSeriesKFold, calibration split). |
| **Calibration uncertainty** | Uncertainty from conformal or bootstrap calibration sample; distinct from structural causal uncertainty. |

---

## 5. Canonical effect scales

**Allowed scales** (every artifact must declare one primary scale; secondary scales require explicit transformation):

| Scale ID | Description | Typical use |
|----------|-------------|-------------|
| `level_effect` | Absolute outcome units per period or aggregated window | SCM/DID level readouts |
| `cumulative_level_effect` | Sum of level effects over post window | DID `cumulative_att`, cumulative injection truth |
| `average_post_period_level_effect` | Mean level effect over post window | TBRRidge mean post-window residual |
| `fractional_lift` | Unitless ratio vs counterfactual | Literature-style lift |
| `percentage_lift` | Percent change vs baseline | D5 percent injection parameter |
| `log_scale_effect` | Log difference or log-ratio | When explicitly documented and invertible |

**Rules:**

1. Every validation artifact and product readout must state **`effect_scale`**.
2. Scale conversion must be **explicit** (formula, baseline definition, aggregation).
3. **No interval reuse across scales** unless transformation and coverage propagation are documented.
4. **Future CalibrationSignal eligibility** (gated) requires estimand and scale compatibility with calibration target.
5. **Future MMM attachment** requires explicit scale mapping to model increment units.

---

## 6. Canonical post-period readouts

| Readout ID | Definition | Appropriate when | Blocked when |
|------------|------------|------------------|--------------|
| `period_level` | Per-period `Y_t − Ŷ_t` (possibly vector over units) | Trajectory diagnostics, period-specific effects | Scored against cumulative truth without aggregation rule |
| `cumulative_post_period` | Sum over post indices | DID cumulative ATT, total lift campaigns | Compared to average or fractional truth without bridge |
| `average_post_period` | Mean over post indices | Mean ATT, TBRRidge-style pooled mean | Used as cumulative causal total without documentation |
| `endpoint` | Effect at final post period only | Terminal KPI focus | Generalized to full-window cumulative without rule |
| `trajectory` | Full post-period vector of period-level effects | Path dynamics, ramp detection | Collapsed to scalar without declared aggregation |

**Rule:** Post-period aggregation used for scoring in validation must match **`post_period_readout`** in metadata.

---

## 7. Point estimate semantics

Every point readout must expose (in artifact JSON or product contract):

| Field | Required content |
|-------|------------------|
| `point_estimand` | Named quantity (e.g., `average_post_period_att`, `cumulative_att`) |
| `effect_scale` | From §5 |
| `post_period_aggregation` | From §6 |
| `target_quantity` | Estimand under identification assumptions |
| `observed_quantity` | What was taken from `Y` |
| `counterfactual_quantity` | What was taken from `Ŷ` |
| `units` | Outcome units or dimensionless |
| `transformation` | None, sum, mean, ratio, log, etc. |
| `sign_convention` | See below |

**Sign convention (required):**

- **Positive** = treatment **increased** outcome relative to counterfactual on the declared scale.
- **Negative** = treatment **decreased** outcome relative to counterfactual.

D5 batteries that compare point sign to **percent injection** while readout is **outcome-scale** (TBRRidge) must be classified as **readout mismatch**, not sign failure of the estimand, until scales are aligned.

---

## 8. Interval semantics

| Field | Required content |
|-------|------------------|
| `interval_type` | e.g., `jackknife`, `bootstrap`, `kfold_dispersion`, `conformal`, `forecast`, `posterior_credible` |
| `interval_lower` / `interval_upper` | On **`interval_scale`** |
| `interval_scale` | Must match `effect_scale` unless documented transform |
| `interval_target` | Quantity interval is designed to cover |
| `interval_level` | Nominal probability (e.g., 0.95) |
| `coverage_target` | Quantity used in validation coverage metric |
| `uncertainty_sources_included` | List (e.g., `resampling`, `split`, `model_fit`) |
| `uncertainty_sources_excluded` | List (e.g., `design`, `causal_identification`) |
| `orientation_valid` | `lower <= upper` |
| `half_width` | `(upper − lower) / 2` at reference point |
| `degenerate_interval_flag` | Width ≤ ε |

**Rules:**

1. **`interval_lower <= interval_upper`** — violation blocks stronger claims.
2. **No negative half-width.**
3. **Interval scale must match point scale** (or documented transform).
4. **Interval target must match point target** for joint causal interpretation.
5. An interval does **not** imply **causal uncertainty** unless `uncertainty_sources_included` and identification assumptions support that claim.
6. **Forecast intervals are not causal intervals by default.**

---

## 9. Coverage semantics

Coverage claims must **name the target**. Allowed coverage types:

| Coverage type | Covers |
|---------------|--------|
| `coverage_cumulative_effect` | True cumulative effect on cumulative scale |
| `coverage_average_post_period_effect` | True average post-period effect |
| `coverage_period_level_effect` | True effect at specific period(s) |
| `coverage_prediction_target` | Prediction error or residual under stated model |
| `coverage_model_forecast` | Forecast target for untreated series |
| `coverage_under_null` | Null estimand (typically zero on declared scale) |

**Rule:** Reporting `coverage = 1.0` against **percent injection** while interval is on **outcome scale** (D5 TBRRidge pattern) is **invalid causal coverage** — classify as `blocked_due_to_readout_mismatch` for decision use.

---

## 10. Null decision semantics

| Term | Definition |
|------|------------|
| **Null effect** | Zero (or practical-zero) on declared estimand and scale |
| **Null rejection** | Interval excludes null zone **or** formal test rejects — per `null_decision_rule` |
| **Null false positive rate** | Share of null worlds where null is rejected |
| **Practical-null zone** | `[−δ, δ]` on declared scale; δ must be documented |
| **Equivalence / no-material-effect zone** | If used, requires pre-registered δ and scale |
| **Blocking condition** | When null behavior unstable (shock, trend violation), null decision is **blocked** for product use |

**Required rule:** A **null decision cannot be inferred from directional sign alone.** Directional signal and null rejection are **separate** metrics and metadata fields.

---

## 11. Directional signal semantics

| Term | Definition |
|------|------------|
| **Directional positive signal** | Point > 0 (or > δ) on declared scale |
| **Directional negative signal** | Point < 0 (or < −δ) on declared scale |
| **Sign correctness under injection** | Sign matches injected truth **on compatible scale only** |
| **Directional false signal under null** | Non-zero direction under null world |
| **Magnitude threshold** | `δ` for ignoring noise (must be scale-specific; D5 fixed thresholds are characterization-only) |
| **Minimum interval support** | If used, interval must exclude zero on declared scale |

**Required rules:**

1. **Directional signal is weaker than causal evidence.**
2. **Directional signal does not imply TrustReport eligibility.**

TBR aggregate D5: high directional FPR under null despite good injected recovery — demonstrates need for separated null decision rule.

---

## 12. Prediction uncertainty vs causal uncertainty

| Mechanism | Typical uncertainty target | Default classification |
|-----------|---------------------------|------------------------|
| **KFold** | Prediction stability / CV dispersion | `prediction_interval_only` or `resampling_interval_target_ambiguous` |
| **TimeSeriesKFold** | Forecast stability across horizons | `prediction_interval_only` |
| **Block residual bootstrap (BRB)** | Resampled residual variability | `resampling_interval_target_ambiguous` until contract names causal estimand |
| **Embedded DID bootstrap** | Resampled ATT sampling distribution | `causal_interval_candidate_requires_validation` — must align cumulative vs average target |
| **Conformal** | Predictive coverage under exchangeability | `prediction_interval_only` unless causal estimand justified |
| **SARIMAX forecast intervals** | Forecast of untreated treated series | `forecast_interval_only` — **not** causal by default |
| **Bayesian posterior intervals** | Posterior of parameter/forecast under model+prior | `prediction_interval_only` or `resampling_interval_target_ambiguous` — **not** automatically causal |

**Required rule:** Do **not** call an interval **causal** unless the artifact states **why** the uncertainty target covers the **causal estimand** under documented identification and design assumptions.

**TBRRidge D5:** KFold temporal leakage risk **blocks** stronger causal classification until split policy is governed in `TBRRIDGE_OPERATOR_CONTRACT_001`.

---

## 13. Method-family implications

### A. SCM-JK

- JK interval target must be named (`interval_target`); D5 suggests resampling/causal candidacy, not validated causal interval.
- Stress-null instability (`weak_signal_null`, `post_shock_null`) requires **calibration / blocking rules** before null decisions in product.
- **No automatic suitability claim.**

### B. AugSynth point

- Point recovery does not create interval semantics.
- **`AUGSYNTH_INFERENCE_BRIDGE_001`** must define uncertainty source before any interval claim.

### C. TBR aggregate

- Strong injected recovery does **not** override high null directional false signal.
- Require **readout / null-decision separation** (`TBR_READOUT_SEMANTICS_001`).

### D. DID bootstrap

- Bootstrap interval must state **cumulative vs average vs period-level** target.
- D5 **0% cumulative coverage** vs injected cumulative truth → **`blocked_due_to_readout_mismatch`** until `DID_BOOTSTRAP_CUMULATIVE_READOUT_FIX_001`.

### E. MCELL per-cell

- Per-cell identity preserved; no pooled causal or interval readout without bridge.
- Cross-cell summaries are **metadata only** unless pooling bridge exists.

### F. TBRRidge inference

- Split policy must be recorded (`leakage_warning`, `split_policy`).
- Classify KFold / TSKFold / BRB by **uncertainty target** (§12).
- KFold: **`blocked_due_to_leakage_risk`** for causal claims; **`prediction_interval_only`** for dispersion characterization.
- Conformal: **`blocked_due_to_readout_mismatch`** (implementation broadcast) on multi-treated unit panel.

### G. Future SARIMAX / Auto-SARIMAX

- Forecast target separated from causal target (`TBR_SARIMAX_OPERATOR_CONTRACT_001`).
- Auto-selection uncertainty recorded; forecast intervals **`forecast_interval_only`**.

### I. Future triply robust / TROP

- **Parked** — [`TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md`](TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md); not rejected.
- Influence-function, sandwich, or cross-fitted doubly/triply robust intervals require **explicit `interval_target`** and **nuisance-model assumptions**.
- Default classification: `causal_interval_candidate_requires_validation` or `resampling_interval_target_ambiguous` until TROP validation protocol passes.
- **No causal interval claim** without validation; null decision and directional signal remain separate.

---

## 14. Required metadata contract for future validation artifacts

| Field | Required | Notes |
|-------|----------|-------|
| `artifact_id` | Yes | Stable ID |
| `method_family` | Yes | e.g., SCM, DID, TBRRidge |
| `estimator` | Yes | Class / module |
| `inference_method` | Yes | JK, bootstrap, KFold, … |
| `geometry` | Yes | e.g., `single_cell_unit_level` |
| `estimand` | Yes | Named causal/predictive quantity |
| `effect_scale` | Yes | §5 |
| `post_period_readout` | Yes | §6 |
| `point_target` | Yes | Point estimand |
| `interval_present` | Yes | Boolean |
| `interval_type` | If interval | §8 |
| `interval_target` | If interval | §8 |
| `coverage_target` | If coverage scored | §9 |
| `uncertainty_sources_included` | If interval | §12 |
| `uncertainty_sources_excluded` | If interval | §12 |
| `null_decision_rule` | Yes | §10 |
| `directional_signal_rule` | Yes | §11 |
| `leakage_warning` | If applicable | TBRRidge, conformal, SARIMAX |
| `forecast_vs_causal_classification` | If interval | §15 taxonomy |
| `promotion_allowed` | Yes | Must default **false** in D5 |
| `suitability_claim_allowed` | Yes | Must default **false** |
| `trust_role_allowed` | Yes | Must default **false** |
| `calibration_signal_allowed` | Yes | Must default **false** |

Protocol v2 and matrix v2 generators should consume this contract; D5 v1 archives may backfill classification without regenerating JSON in this artifact.

---

## 15. Classification taxonomy

| Classification | Meaning |
|----------------|---------|
| `point_only_no_uncertainty` | Point characterized; intervals absent or not applicable |
| `prediction_interval_only` | Interval targets prediction/forecast stability, not validated causal estimand |
| `forecast_interval_only` | Explicit forecast band (SARIMAX, model forward path) |
| `resampling_interval_target_ambiguous` | Resampling interval present; causal vs prediction target not established |
| `causal_interval_candidate_requires_validation` | Intended causal estimand; Level B structural checks may pass; Level C / contract fix required |
| `causal_interval_validated_in_scope` | **Future only** — requires explicit later artifact; **not** assigned to current D5 archives |
| `blocked_due_to_readout_mismatch` | Point/interval scale or aggregation incompatible with scored truth |
| `blocked_due_to_geometry_mismatch` | Geometry in output ≠ declared geometry |
| `blocked_due_to_leakage_risk` | Split/leakage policy blocks causal interpretation |

---

## 16. Decision rules

| Decision | Allowed when | Blocked when |
|----------|--------------|--------------|
| **Point-only characterization** | Estimand + scale documented; geometry match | Readout mismatch or geometry mismatch |
| **Interval allowed (caveated)** | Orientation valid; target named; classification ≤ `resampling_interval_target_ambiguous` or `prediction_interval_only` | Negative half-width, orientation fail, leakage unmitigated for causal claim |
| **Interval blocked** | — | Readout mismatch, geometry mismatch, implementation failure (Conformal broadcast) |
| **Directional signal reported** | Rule + scale documented | Used as null decision proxy |
| **Null decision** | `null_decision_rule` + stable null worlds or calibrated δ | Stress-null unstable without blocking policy |
| **TrustReport role** | **Blocked today** — requires suitability v2 + role framework + validation evidence | All current D5 artifacts |
| **CalibrationSignal eligibility** | **Blocked today** — requires scale compatibility + calibration archives | All current D5 artifacts |

---

## 17. Relationship to future artifacts

This artifact **feeds** (ordered per enhancement roadmap):

1. **`GEOMETRY_BRIDGE_REQUIREMENTS_001`** ✅ — geometry compatibility gates  
2. **`DESIGN_OUTPUT_CONTRACT_001`** — design-layer geometry metadata **(next)**  
3. **`TBRRIDGE_OPERATOR_CONTRACT_001`** — split policy, leakage, path-specific targets  
4. **`SCM_JK_STRESS_NULL_CALIBRATION_001`** — stress-null FPR and JK target clarification  
5. **`AUGSYNTH_INFERENCE_BRIDGE_001`** — uncertainty path after point characterization  
6. **`DID_BOOTSTRAP_CUMULATIVE_READOUT_FIX_001`** — cumulative vs bootstrap target alignment  
7. **`TBR_SARIMAX_OPERATOR_CONTRACT_001`** · **`TBR_AUTO_SARIMAX_MODEL_SELECTION_POLICY_001`**  
8. **`BAYESIAN_METHOD_SPECIFICATION_001`**  
9. **Suitability framework v2** · **Protocol v2** · **Matrix v2**  
10. **Future TrustReport / CalibrationSignal / MMM integration** — only after above + explicit role assignment

---

## 18. Current D5 artifact backfill assessment

Non-promotional classification of completed Level B archives:

| D5 artifact | Geometry | Point classification | Interval classification | Notes |
|-------------|----------|----------------------|-------------------------|-------|
| **D5-STAT-SCM-JK-001** | `single_cell_unit_level` | `average_post_period_level_effect` (level) | `causal_interval_candidate_requires_validation` | Stress-null FPR elevated; structural intervals clean |
| **D5-STAT-AUGSYNTH-POINT-001** | `single_cell_unit_level` | `point_only_no_uncertainty` | N/A | No interval semantics on path |
| **D5-STAT-TBR-AGG-001** | `aggregate_two_series` | `average_post_period_level_effect` | N/A | `blocked_due_to_readout_mismatch` for **null decision use** — high directional FPR |
| **D5-STAT-DID-BOOTSTRAP-001** | `single_cell_unit_level` | `cumulative_level_effect` | `blocked_due_to_readout_mismatch` | 0% cumulative coverage vs injected cumulative truth |
| **D5-STAT-MCELL-PERCELL-001** | `multi_cell_per_cell_only` | Per-cell: SCM-JK interval + AugSynth point | SCM-JK: `causal_interval_candidate_requires_validation`; AugSynth: `point_only_no_uncertainty` | No pooled readout; shock cell caveat |
| **D5-STAT-TBRRIDGE-INF-001** | `single_cell_unit_level` | Outcome-scale average post-window | KFold/TSKFold: `prediction_interval_only` + `blocked_due_to_leakage_risk` for causal; BRB: `resampling_interval_target_ambiguous`; Conformal: `blocked_due_to_readout_mismatch` | Scale mismatch vs percent injection in D5 scoring |

**No row above assigns** production readiness, trust, suitability, CalibrationSignal, or MMM authorization.

---

## 19. Governance gates

This artifact:

- **Does not promote** any method.
- **Does not authorize** TrustReport role assignment.
- **Does not authorize** CalibrationSignal eligibility (future gated concept).
- **Does not authorize** MMM use or attachment.
- **Does not authorize** LLM recommendation use.
- **Requires** validation evidence + suitability framework v2 + explicit role assignment for any future eligibility.

All current D5 **`forbidden_flags`** remain **false** until separate artifacts explicitly change policy with evidence.

---

## 20. Non-goals

- No estimator code changes  
- No design code changes  
- No inference code changes  
- No new simulations or D5 archive regeneration  
- No validation harness changes  
- No method promotion  
- No governed-readout claim for existing methods  
- No Bayesian or SARIMAX shortcut  
- No pooled multi-cell causal readout  

---

## 21. Roadmap and audit updates checked

| Document | Update |
|----------|--------|
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | GEOMETRY_BRIDGE_REQUIREMENTS_001 **complete**; next = DESIGN_OUTPUT_CONTRACT_001 |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Post-D5 enhancement sequence updated |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Current status / next item adjusted |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Artifact registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Readout-semantics controller cross-link |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Suitability v2 dependency note |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Matrix v2 must reference these semantics |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Protocol v2 must use these semantics |

**D5 reports inspected:** SCM-JK, AugSynth point, TBR aggregate, DID bootstrap, MCELL per-cell, TBRRidge inference (see §3, §18).

---

**Estimator readout integration (2026-06-18):** Governed estimator readouts exist via [`ESTIMATOR_READOUT_GUARDRAIL_INTEGRATION_001.md`](ESTIMATOR_READOUT_GUARDRAIL_INTEGRATION_001.md). Native `run_analysis()` dicts are **not** governed readouts and must not be interpreted as TrustReport/CalibrationSignal/MMM/LLM authorization.

*INFERENCE-READOUT-SEMANTICS-001 v1.0.0 — Accepted; geometry bridge complete; next = DESIGN_OUTPUT_CONTRACT_001.*
