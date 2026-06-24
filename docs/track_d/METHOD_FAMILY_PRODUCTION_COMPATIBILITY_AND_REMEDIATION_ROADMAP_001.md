# METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001

## 1. Artifact ID

`METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`

## 2. Purpose

This docs/governance checkpoint defines, for every governed estimator family, how it can move from current status toward production-compatible candidacy, remediation, diagnostic-only use with a promotion hypothesis, research-only use with a promotion hypothesis, retire/replace, or blocked status.

Research-only and diagnostic-only mean **not production-valid yet**, not abandoned. Every non-production family must document blockers, fixability, remediation or scout paths, promotion evidence requirements, and retirement criteria.

## 3. Why this roadmap exists

Prior control artifacts established suitability matrices, failure registries, assignment stress tests, and family-specific audits (TBRRidge, DID). This roadmap consolidates **per-family production compatibility posture** so later scouts and promotion gates do not re-litigate baseline family status ad hoc.

## 4. Meaning of production-compatible

A family is **production-compatible candidate** only when observed diagnostics, design validity, inference suitability, DGP coverage, null calibration, failure-registry consultation, and family-specific promotion evidence are satisfied. **This roadmap does not authorize production inference, production p-values, or causal confidence intervals for any family.**

## 5. Meaning of remediation-required

**Remediation-required** means known blockers are plausibly fixable via governed code, adapter, calibration, or design-documentation work. Remediation must name required future artifacts and evidence; it is not automatic promotion.

## 6. Meaning of diagnostic-only

**Diagnostic-only** means point estimates, decomposition readouts, or null-monitor semantics may be used for exploration and falsification when labeled diagnostic. Diagnostic-only is a **promotion hypothesis**, not abandonment.

## 7. Meaning of research-only

**Research-only** means restricted research, scout, or calibration use only. Research-only requires a documented scout or remediation path and promotion evidence checklist. It does **not** mean the method is retired.

## 8. Meaning of retire/replace

**Retire/replace** means the family or inference path should not advance without strong new evidence or a replacement estimator. Retirement criteria must be explicit; blocked paths remain blocked until waived by a later audit.

## 9. Estimator family table

| Family | Current status | Fixability | Exit path type |
|--------|----------------|------------|----------------|
| SCM | Production-candidate lane (gated) | High | Remediation + promotion gate |
| AugSynth CVXPY | Diagnostic/point candidate; inference remediation required | Medium | Remediation + promotion gate |
| DID | Conditional candidate (suitability audited) | Medium | Remediation + promotion criteria |
| Synthetic DID | Research/scout candidate | Medium | Scout + suitability |
| TBRRidge | Diagnostic-only unless future remediation proves otherwise | Low–medium | Remediation or retire |
| TBR aggregate / classic TBR | Retire/block likely | Low | Retire/replace audit |
| Bayesian TBR | Posterior diagnostic/research-only | Low | Boundary audit + retire criteria |
| TROP | Research-only/scout until evidence exists | Unknown | Scout boundary audit |
| Multicell/shared-control (cross-estimator) | Cross-cutting blocker | Medium | Max-T/stepdown scout |

## 10. Known blockers by family

### SCM
- Single-treated placebo null-monitor only (`FM-ES-002`, `FM-INF-001`)
- Poor donor support / weight degeneracy (`FM-DS-006`, `FM-DS-007`)
- Studentized placebo requires adapter + null calibration (`FM-INF-002`)
- Multicell dependence if pooled (`FM-DA-009`)

### AugSynth CVXPY
- Point without calibrated inference (`FM-ES-003`)
- Augmentation instability (`FM-ES-004`)
- Jackknife diagnostic/retire paths (`FM-INF-005`)
- Placebo rank overinterpretation risk (`FM-INF-001`)

### DID
- Parallel-trend violations (`FM-PF-003`, `FM-ES-005`)
- Unknown/deterministic assignment (`FM-DA-001`, `FM-DA-002`)
- Bootstrap cannot fix invalid assignment (`FM-INF-003`)
- Few clusters (`FM-INF-006`)
- Staggered/TWFE ambiguity (`FM-TE-004`)

### Synthetic DID
- Balance/stress gaps (`FM-ES-009`)
- Staggered validation unwired in repo evidence
- Research-not-production posture (`FM-CP-005`)

### TBRRidge
- BRB/KFold/placebo/jackknife not production-valid (TBRRidge audit)
- Aggregate/global overclaim (`FM-ES-007`)
- Regularization masks instability (`FM-ES-006`)

### TBR aggregate / classic TBR
- Aggregate geometry mismatch (`FM-ES-007`)
- Global causal overclaim (`FM-INF-011`)
- Small-N overclaim (`FM-PS-010`)

### Bayesian TBR
- Posterior treated as causal CI (`FM-ES-008`, `FM-INF-008`)
- Not governed causal uncertainty path

### TROP
- Research-as-production risk (`FM-ES-010`)
- Triply-robust evidence not yet promotion-grade

### Multicell/shared-control (cross-estimator)
- Shared-control dependence (`FM-DA-009`)
- Winner-selection / max-T / stepdown gaps (`FM-DA-010`, `FM-INF-009`, `FM-INF-010`)
- Pooled/global estimand ambiguity

## 11. Remediation paths by family

| Family | Remediation plan | Required future artifacts |
|--------|------------------|---------------------------|
| SCM | Complete studentized adapter contract, null calibration, multicell-safe readouts | `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`, `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` |
| AugSynth CVXPY | Inference adapter + null calibration; retire unsafe JK paths | `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001` |
| DID | Parallel-trend diagnostics, cluster count gates, bootstrap dependence DGP | `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` (post-multicell scout) |
| Synthetic DID | Scout implementation coverage and suitability | `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001` |
| TBRRidge | BRB/variance remediation already attempted; remain diagnostic unless new evidence | Prior TBRRidge audits; no new promotion without DGP + null calibration |
| TBR aggregate | Strong evidence required or retire | `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001` |
| Bayesian TBR | Posterior diagnostic boundary only | `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001` |
| TROP | Research boundary scout | `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001` |
| Multicell/shared-control | Max-T/stepdown/dependence research | `MULTICELL_MAX_T_RESEARCH_SCOUT_001` |

## 12. Promotion evidence by family

All production-candidate promotion requires: observed diagnostics (`OPD-*`), DGP coverage (`DGP-*`), failure-registry consult (`FM-CP-004`), design stress compatibility (`ST-*`), null calibration, and family-specific adapter contracts where applicable.

- **SCM:** Single-treated placebo governed semantics; studentized adapter; null FPR/coverage gates
- **AugSynth CVXPY:** Point + governed inference adapter; disagreement diagnostics
- **DID:** Parallel trends; assignment validity; bootstrap/randomization suitability audits passed
- **Synthetic DID:** Balance DGP stress; staggered estimand clarity; scout report
- **TBRRidge:** Not promotion-target unless remediation audit reopened with new evidence
- **TBR aggregate:** Unlikely without geometry remediation evidence
- **Bayesian TBR:** Posterior diagnostic calibration only; never causal CI authorization from this roadmap
- **TROP:** Research scout evidence only
- **Multicell:** Dependence model + multiplicity adjustment evidence

## 13. Retirement criteria by family

| Family | Retire/replace when |
|--------|---------------------|
| SCM | Never from this roadmap; gated promotion only |
| AugSynth CVXPY | JK paths remain retire candidates; inference cannot be calibrated |
| DID | Persistent trend violation with production promotion attempted |
| Synthetic DID | Scout shows unwired/invalid staggered recovery |
| TBRRidge | Aggregate/global paths; jackknife-as-CI; failed remediation with no new evidence |
| TBR aggregate | Geometry mismatch unresolved after boundary audit |
| Bayesian TBR | Posterior continues to be used as causal CI |
| TROP | Promoted without research boundary audit |
| Multicell | Shared-control dependence ignored in production-like selection |

## 14. Cross-cutting multicell/shared-control blocker

Multicell/shared-control is a **cross-estimator blocker**. No family may claim production compatibility on pooled multicell readouts until `MULTICELL_MAX_T_RESEARCH_SCOUT_001` and downstream multiplicity artifacts complete. Applies to SCM, AugSynth, DID, TBRRidge, TBR, and Bayesian paths.

## 15. Updated roadmap sequence

**Completed checkpoint:** `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`

**Immediate next:** `MULTICELL_MAX_T_RESEARCH_SCOUT_001`

**Forward sequence:**
1. `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
2. `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
3. `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
4. `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`
5. `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`
6. `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`

## 16. Family detail records

### SCM (`scm`)

- **current_status:** production-compatible candidate (gated)
- **known_blockers:** placebo overinterpretation; donor degeneracy; adapter/null calibration; multicell pooling
- **fixability_assessment:** high
- **remediation_plan:** complete inference promotion gate after multicell scout
- **required_future_artifacts:** `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`, `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`
- **promotion_evidence_required:** OPD/DGP/FM/ST/null calibration/adapter contract
- **retirement_or_replacement_criteria:** none at this checkpoint
- **allowed_current_use:** diagnostic point; governed placebo null-monitor; research calibration
- **forbidden_current_use:** production p-values; causal CIs; TrustReport; ungoverned promotion
- **downstream_authorization_status:** paused

### AugSynth CVXPY (`augsynth_cvxpy`)

- **current_status:** diagnostic-only with promotion hypothesis
- **known_blockers:** uncalibrated inference; augmentation instability; JK retire path
- **fixability_assessment:** medium
- **remediation_plan:** inference adapter + null calibration + promotion gate audit
- **required_future_artifacts:** `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
- **promotion_evidence_required:** adapter contract; null calibration; disagreement diagnostics
- **retirement_or_replacement_criteria:** JK as causal CI; promotion without adapter
- **allowed_current_use:** point estimates; diagnostic decomposition
- **forbidden_current_use:** production inference; TrustReport
- **downstream_authorization_status:** paused

### DID (`did`)

- **current_status:** conditional candidate (remediation-required for inference)
- **known_blockers:** trends; assignment; bootstrap dependence; clusters; staggered timing
- **fixability_assessment:** medium
- **remediation_plan:** consume `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`; promotion criteria matrix
- **required_future_artifacts:** `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`
- **promotion_evidence_required:** suitability audit; parallel trends; DGP coverage
- **retirement_or_replacement_criteria:** promotion despite known trend violation
- **allowed_current_use:** diagnostic point; sensitivity; restricted research randomization/bootstrap
- **forbidden_current_use:** production p-values; causal CIs; bootstrap as assignment fix
- **downstream_authorization_status:** paused

### Synthetic DID (`synthetic_did`)

- **current_status:** research-only with promotion hypothesis
- **known_blockers:** balance stress; staggered wiring; research-not-production
- **fixability_assessment:** medium
- **remediation_plan:** dedicated scout and suitability artifact
- **required_future_artifacts:** `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
- **promotion_evidence_required:** scout report; DGP balance coverage
- **retirement_or_replacement_criteria:** promotion without scout completion
- **allowed_current_use:** research/scout calibration
- **forbidden_current_use:** production inference; TrustReport
- **downstream_authorization_status:** paused

### TBRRidge (`tbrridge`)

- **current_status:** diagnostic-only unless future remediation proves otherwise
- **known_blockers:** BRB/KFold/placebo/JK; aggregate overclaim; regularization masking
- **fixability_assessment:** low–medium
- **remediation_plan:** prior remediation audits; no promotion without new validation
- **required_future_artifacts:** none immediate; reopen only with new evidence
- **promotion_evidence_required:** full TBRRidge audit + DGP + null calibration if reopened
- **retirement_or_replacement_criteria:** aggregate/global; jackknife-as-CI; failed remediation
- **allowed_current_use:** diagnostic point; labeled sensitivity
- **forbidden_current_use:** production inference; production p-values; causal CIs
- **downstream_authorization_status:** paused

### TBR aggregate / classic TBR (`tbr_aggregate`)

- **current_status:** retire/replace likely
- **known_blockers:** geometry mismatch; global overclaim; small-N
- **fixability_assessment:** low
- **remediation_plan:** boundary audit with Bayesian TBR
- **required_future_artifacts:** `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`
- **promotion_evidence_required:** strong geometry remediation evidence if reconsidered
- **retirement_or_replacement_criteria:** unresolved aggregate geometry mismatch
- **allowed_current_use:** diagnostic exploration only when explicitly labeled
- **forbidden_current_use:** production causal claims; TrustReport
- **downstream_authorization_status:** paused

### Bayesian TBR (`bayesian_tbr`)

- **current_status:** posterior diagnostic/research-only
- **known_blockers:** posterior as causal CI; ungoverned uncertainty
- **fixability_assessment:** low
- **remediation_plan:** boundary audit; posterior diagnostic semantics only
- **required_future_artifacts:** `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`
- **promotion_evidence_required:** governed posterior diagnostic calibration
- **retirement_or_replacement_criteria:** causal CI authorization from posterior
- **allowed_current_use:** posterior diagnostic research
- **forbidden_current_use:** causal CI; production p-values; TrustReport
- **downstream_authorization_status:** paused

### TROP (`trop`)

- **current_status:** research-only/scout
- **known_blockers:** research-as-production; limited promotion evidence
- **fixability_assessment:** unknown
- **remediation_plan:** research-only boundary audit
- **required_future_artifacts:** `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`
- **promotion_evidence_required:** scout + triply-robust DGP evidence
- **retirement_or_replacement_criteria:** promotion without boundary audit
- **allowed_current_use:** research/scout only
- **forbidden_current_use:** production inference; TrustReport
- **downstream_authorization_status:** paused

### Multicell/shared-control cross-estimator (`multicell_shared_control`)

- **current_status:** blocked cross-cutting until multiplicity research
- **known_blockers:** dependence; winner selection; max-T/stepdown gaps
- **fixability_assessment:** medium
- **remediation_plan:** max-T research scout first
- **required_future_artifacts:** `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
- **promotion_evidence_required:** dependence handling; multiplicity calibration
- **retirement_or_replacement_criteria:** independent-cell assumption when invalid
- **allowed_current_use:** per-cell diagnostic readouts only
- **forbidden_current_use:** pooled production inference; global winner selection
- **downstream_authorization_status:** paused

## 17. Downstream boundary

This roadmap does not authorize production inference.
This roadmap does not authorize production p-values.
This roadmap does not authorize causal confidence intervals.
This roadmap does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 18. Validation

Summary: [`docs/track_d/archives/METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001_summary.json`](archives/METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001_summary.json)

Tests: `tests/governance/test_method_family_production_compatibility_remediation_roadmap_001.py`

## 19. Verdict

`method_family_production_compatibility_and_remediation_roadmap_defined_no_downstream_authorization`

**Next:** `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
