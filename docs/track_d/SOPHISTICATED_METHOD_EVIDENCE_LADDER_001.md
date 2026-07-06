# SOPHISTICATED_METHOD_EVIDENCE_LADDER_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001` |
| **Artifact type** | `sophisticated_method_evidence_ladder` |
| **Status** | `completed` |
| **Scope** | `sophisticated_methods_evidence_ladder_defined_no_method_promotion` |
| **Base commit** | `159cc78` (Add method promotion candidate audit) |
| **Final verdict** | `sophisticated_methods_evidence_ladder_defined_no_method_promotion` |

**Depends on:** `METHOD_PROMOTION_CANDIDATE_AUDIT_001` · `METHOD_PROMOTION_REVIEW_RUNTIME_001` · `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001`

---

## 2. Source files inspected

- `docs/ROADMAP_V4.md` · `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md` · `docs/MIP_AUDIT_REGISTRY.md`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`
- `docs/track_d/METHOD_PROMOTION_CANDIDATE_AUDIT_001.md` · `METHOD_PROMOTION_CANDIDATE_AUDIT_001_summary.json`
- `docs/track_d/METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001.md`
- `docs/MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001.md`
- `docs/F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md` · `docs/GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md`
- `docs/track_d/DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001_REPORT.md`
- `docs/track_d/MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001_REPORT.md`
- `docs/track_d/AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001_REPORT.md`
- `docs/track_d/METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001.md`
- `panel_exp/validation/production_catalog_blocklist_001.py` · `nominal_calibration.py`
- `panel_exp/validation/method_promotion_review_runtime_001.py`
- `panel_exp/validation/production_compatibility_promotion_review_contract_001.py`

---

## 3. Why “deferred” means deferred from promotion, not validation

`METHOD_PROMOTION_CANDIDATE_AUDIT_001` found **zero RANK_4** production-compatibility-ready candidates and deferred `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`. That deferral applies **only** to promotion/production surfaces:

- production catalog unblock
- production authorization / trusted readout
- compatibility review runtime assembly for promotion packets
- governed uncertainty on production readout paths

**Deferred does not mean:**

- stop research on sophisticated methods
- stop diagnostic-only execution where catalog permits
- stop evidence audits, validation plans, or OC batteries
- stop documenting false-confidence risks
- stop building contracts that define estimand semantics before runtime

This ladder defines how sophisticated method families **earn trust through staged evidence** without prematurely promoting them. Every stage below STAGE_6 is explicitly **not** production approval; STAGE_6 is compatibility-review candidacy only — still not production approval.

---

## 4. Ladder stage taxonomy

| Stage | Label | Meaning |
|-------|-------|---------|
| **STAGE_0** | `STAGE_0_BLOCKED_OR_UNCHARACTERIZED` | Hard catalog blockers, unresolved estimand semantics, or insufficient characterization to trust any readout |
| **STAGE_1** | `STAGE_1_RESEARCH_SANDBOX` | Research/offline characterization permitted; no governed diagnostic readout claims |
| **STAGE_2** | `STAGE_2_DIAGNOSTIC_ONLY` | Governed diagnostic/falsification surfaces only; no causal or uncertainty promotion |
| **STAGE_3** | `STAGE_3_POINT_ESTIMATE_ONLY` | Restricted point-estimate readout permitted with explicit no-uncertainty boundary |
| **STAGE_4** | `STAGE_4_UNCERTAINTY_CANDIDATE` | Evidence-building toward governed intervals/null monitors; coverage not yet validated for promotion |
| **STAGE_5** | `STAGE_5_RESTRICTED_REVIEW_CANDIDATE` | May enter restricted method promotion review with caveats; not production approval |
| **STAGE_6** | `STAGE_6_PRODUCTION_COMPATIBILITY_CANDIDATE` | Strongest evidence posture short of production; eligible for compatibility review packet only — **not production approval** |

**No stage grants production approval.** STAGE_6 means “may assemble a production-compatibility review packet,” consistent with `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001`.

---

## 5. Sophisticated method inventory

| Method family | method_id / instrument_id | Current stage | Target next stage |
|---------------|---------------------------|---------------|-------------------|
| DID bootstrap | `DID` / `DID_BOOTSTRAP` | STAGE_2 | STAGE_4 |
| TBRRidge BRB/KFold/Placebo | `TBRRidge` / BRB, KFold, Placebo | STAGE_2 | STAGE_4 |
| TBR aggregate / pooled | `TBR` / aggregate paths | STAGE_0 | STAGE_1 |
| multi-cell pooled / global | multicell / pooled lift | STAGE_0 | STAGE_1 |
| AugSynth jackknife | `AugSynthCVXPY` / `AugSynth_Jackknife` | STAGE_2 | STAGE_4 |
| SCM multi-treated production inference | `SCM` / multi-treated inference | STAGE_1 | STAGE_2 |

---

## 6. Per-method evidence ladder

### 6.1 DID_BOOTSTRAP

| Field | Value |
|-------|-------|
| **Current stage** | `STAGE_2_DIAGNOSTIC_ONLY` |
| **Target next stage** | `STAGE_4_UNCERTAINTY_CANDIDATE` |
| **Allowed surfaces** | Research sandbox (`D5_STAT_DID_BOOTSTRAP_001` lineage); estimand documentation; parallel-trends diagnostic attachment where DID point path exists; falsification planning |
| **Prohibited surfaces** | Governed bootstrap CI/p-value; production catalog unblock; trusted causal readout; statistical promotion pass; compatibility review candidacy |
| **Evidence present** | `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001`; separate `DID_2X2_POINT_ESTIMATE` governed point path (STAGE_3 sibling); `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001` suitability audit |
| **Missing evidence** | Bootstrap executor in governed runtime; cluster/unit dependence policy; small-sample coverage calibration; placebo/pre-period falsification battery; contrast/estimand semantics closure for bootstrap estimand |
| **False-confidence risks** | Bootstrap intervals under violated parallel trends; ignored clustering inflating precision; treatment-timing heterogeneity masked; placebo pass misread as design validity |
| **Minimum next validation artifact** | `DID_BOOTSTRAP_VALIDITY_EVIDENCE_AUDIT_001` (after estimand contract; not bootstrap runtime) |
| **Stop/go criteria** | **Stop:** catalog unblock or CI surfacing before coverage audit. **Go:** parallel-trends + clustering diagnostics documented; placebo falsification plan defined; bootstrap estimand matches point estimand contract |
| **Do not build yet** | `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_004_BOOTSTRAP_INFERENCE`; catalog unblock; production uncertainty readout |
| **Method promotion review** | Not eligible — blocked catalog posture; promotion review may reference ladder gaps only |
| **Production compatibility review** | Not eligible — hard blocker `BLOCKER_INFERENCE_NOT_IMPLEMENTED` |

**Parallel trends / timing:** Bootstrap does not repair invalid assignment or trend violations; diagnostics must gate any future uncertainty surfacing.

**Point vs uncertainty:** Point estimate allowed only via sibling `DID_2X2_POINT_ESTIMATE` (STAGE_3). `DID_BOOTSTRAP` uncertainty remains prohibited until STAGE_4 evidence.

---

### 6.2 TBRRidge BRB / KFold / Placebo

| Field | Value |
|-------|-------|
| **Current stage** | `STAGE_2_DIAGNOSTIC_ONLY` |
| **Target next stage** | `STAGE_4_UNCERTAINTY_CANDIDATE` |
| **Allowed surfaces** | TBRRidge Placebo diagnostic comparator (restricted); offline BRB/KFold research replay; prediction-stability diagnostics; regularization sensitivity sweeps |
| **Prohibited surfaces** | Production BRB/KFold CI; catalog unblock for BRB/KFold; trusted lift/significance; multi-treated KFold readout without geometry remediation |
| **Evidence present** | `brb_bounds_inverted_run001` documented; `kfold_multi_treated_unsupported_run001` documented; Track B placebo semantics; F-INF-002 pooled-CF multi-treated readout fix (research lineage) |
| **Missing evidence** | BRB bounds remediation or retirement decision; KFold geometry policy for multi-treated; fold/temporal leakage audit; placebo calibration against null DGP; coverage validation for any revived uncertainty path |
| **False-confidence risks** | Inverted BRB bounds; regularization hiding misspecification; donor/control extrapolation; placebo miscalibration; fold leakage inflating precision |
| **Minimum next validation artifact** | `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001` |
| **Stop/go criteria** | **Stop:** any production CI until coverage validated. **Go:** false-confidence diagnostic catalog complete; BRB retired or remediated; KFold geometry class explicit |
| **Do not build yet** | Production BRB/KFold inference runtime; catalog unblock; ensemble TBRRidge promotion |
| **Method promotion review** | BRB/KFold blocked (RANK_0); Placebo RANK_2 evidence-building only |
| **Production compatibility review** | Not eligible for BRB/KFold; Placebo not a promotion target |

**BRB/KFold uncertainty semantics:** Block-residual bootstrap and KFold CV intervals are **not** governed uncertainty until coverage and geometry policies pass dedicated audits.

---

### 6.3 TBR aggregate / pooled paths

| Field | Value |
|-------|-------|
| **Current stage** | `STAGE_0_BLOCKED_OR_UNCHARACTERIZED` |
| **Target next stage** | `STAGE_1_RESEARCH_SANDBOX` |
| **Allowed surfaces** | Offline aggregate replay; ADR/pooling semantics research; heterogeneity documentation |
| **Prohibited surfaces** | Aggregate production readout; pooled lift claims; governed CI on collapsed cells; compatibility review |
| **Evidence present** | `BLOCKER_AGGREGATE_MISMATCH` in blocklist; classic TBR aggregate 1×1 research lineage; METHOD_FAMILY retire/replace plan |
| **Missing evidence** | Pooled residual/covariance handling contract; weighting/estimand semantics; heterogeneity collapse diagnostics; `pooling_rule_id` governance |
| **False-confidence risks** | Aggregate lift false-confidence when cells heterogeneous; wrong residual pooling; scale conflation across units |
| **Minimum next validation artifact** | `POOLED_AGGREGATE_ESTIMAND_SEMANTICS_CONTRACT_001` (or fold into multicell contract) |
| **Stop/go criteria** | **Stop:** any aggregate summary on blocked paths. **Go:** estimand contract names primary estimand, weighting, and collapse rules |
| **Do not build yet** | Aggregate production executor; global lift readout; catalog unblock |
| **Method promotion review** | RANK_0 — no promotion |
| **Production compatibility review** | Not eligible |

**Required diagnostic before restricted review:** heterogeneity diagnostic + explicit pooling rule ID per F-P0-006.

---

### 6.4 multi-cell pooled / global paths

| Field | Value |
|-------|-------|
| **Current stage** | `STAGE_0_BLOCKED_OR_UNCHARACTERIZED` |
| **Target next stage** | `STAGE_1_RESEARCH_SANDBOX` |
| **Allowed surfaces** | Per-cell marginal restricted readout (sibling path, STAGE_5 candidate); multicell decision policy contract research; max-T research scout |
| **Prohibited surfaces** | Pooled/global lift without `pooling_rule_id`; global winner claims; independent per-cell tests without multiplicity; production pooled inference |
| **Evidence present** | `MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001`; `D5_MCELL_001` no pooled claim; `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001`; DCM-006 multiplicity ~27% familywise issue documented |
| **Missing evidence** | Shared-control covariance contract; governed multiplicity policy; contrast taxonomy (global vs cell-level); dosage/arm semantics; correlated-cell handling |
| **False-confidence risks** | Independent-test fiction across shared controls; multiplicity inflation; global scale claims without covariance; correlated cell double-counting |
| **Minimum next validation artifact** | `MULTICELL_CONTRAST_MULTIPLICITY_EVIDENCE_CONTRACT_001` |
| **Stop/go criteria** | **Stop:** global winner/scale claim without multiplicity + covariance. **Go:** contrast taxonomy + multiplicity policy documented and testable |
| **Do not build yet** | Pooled production runtime; global lift authorization; catalog unblock for pooled paths |
| **Method promotion review** | Pooled/global RANK_0; per-cell marginal separate ladder (STAGE_5 sibling) |
| **Production compatibility review** | Not eligible for pooled/global |

---

### 6.5 AugSynth JK

| Field | Value |
|-------|-------|
| **Current stage** | `STAGE_2_DIAGNOSTIC_ONLY` |
| **Target next stage** | `STAGE_4_UNCERTAINTY_CANDIDATE` |
| **Allowed surfaces** | Diagnostic-only jackknife replay; donor hull stress tests; weight stability monitoring; method disagreement diagnostics vs SCM |
| **Prohibited surfaces** | Governed causal readout; production CI; catalog promotion; ASCM production remediation before validity closure |
| **Evidence present** | `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`; diagnostic-only catalog posture; point-only sibling (STAGE_2) |
| **Missing evidence** | Jackknife coverage validation; scale bridge closure; weak-match sensitivity bounds; null calibration; CVXPY solver reliability evidence |
| **False-confidence risks** | Donor hull extrapolation; unstable weights; scale bridge errors; JK intervals under weak matches; disagreement with SCM ignored |
| **Minimum next validation artifact** | `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001` |
| **Stop/go criteria** | **Stop:** governed uncertainty until coverage + stability validated. **Go:** JK coverage audit on null DGP; donor hull stress passes thresholds |
| **Do not build yet** | `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` production path; governed uncertainty surfacing |
| **Method promotion review** | RANK_1 defer — evidence-building via ladder only |
| **Production compatibility review** | Not eligible |

---

### 6.6 SCM multi-treated production inference

| Field | Value |
|-------|-------|
| **Current stage** | `STAGE_1_RESEARCH_SANDBOX` |
| **Target next stage** | `STAGE_2_DIAGNOSTIC_ONLY` |
| **Allowed surfaces** | Research replay; treated-set placebo framework planning; assignment geometry documentation; donor overlap analysis |
| **Prohibited surfaces** | Production multi-treated inference; aggregate vs unit-level lift without semantics; placebo on unsupported geometry |
| **Evidence present** | Single-treated SCM+JK governed path (sibling); `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001` deferral; Phase 13/15 geometry docs |
| **Missing evidence** | Treated-set placebo semantics; multi-treated assignment geometry contract; donor overlap/support thresholds; inference validity for treated sets |
| **False-confidence risks** | Placebo on multi-treated mis-specified; donor overlap double-use; aggregate lift conflation; unit-level vs set-level estimand confusion |
| **Minimum next validation artifact** | Treated-set placebo semantics contract (fold into multicell or dedicated `SCM_MULTITREATED_INFERENCE_EVIDENCE_AUDIT_001`) |
| **Stop/go criteria** | **Stop:** production inference until placebo/JK semantics governed. **Go:** treated-set placebo framework documented with geometry gates |
| **Do not build yet** | Production multi-treated SCM inference runtime; catalog unblock |
| **Method promotion review** | RANK_1 defer |
| **Production compatibility review** | Not eligible |

---

## 7. Comparison table

| method_family | current_stage | next_stage | biggest_blocker | next_smallest_artifact | do_not_build_yet |
|---------------|---------------|------------|-----------------|------------------------|------------------|
| DID_BOOTSTRAP | STAGE_2 | STAGE_4 | No governed bootstrap runtime; coverage unvalidated | DID_BOOTSTRAP_VALIDITY_EVIDENCE_AUDIT_001 | Bootstrap inference runtime; catalog unblock |
| TBRRidge BRB/KFold/Placebo | STAGE_2 | STAGE_4 | BRB bounds inverted; KFold multi-treated unsupported | TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001 | Production BRB/KFold CI |
| TBR aggregate/pooled | STAGE_0 | STAGE_1 | Aggregate estimand semantics unresolved | POOLED_AGGREGATE_ESTIMAND_SEMANTICS_CONTRACT_001 | Aggregate production paths |
| multi-cell pooled/global | STAGE_0 | STAGE_1 | Multiplicity + shared-control covariance | MULTICELL_CONTRAST_MULTIPLICITY_EVIDENCE_CONTRACT_001 | Global lift / pooled runtime |
| AugSynth JK | STAGE_2 | STAGE_4 | JK coverage + donor hull unvalidated | AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001 | Governed uncertainty surfacing |
| SCM multi-treated | STAGE_1 | STAGE_2 | Placebo/JK semantics for treated sets | SCM_MULTITREATED_INFERENCE_EVIDENCE_AUDIT_001 | Production multi-treated inference |

---

## 8. False-confidence risks (cross-cutting)

| Risk class | Affected families | Mitigation ladder step |
|------------|-------------------|------------------------|
| Uncalibrated intervals | DID_BOOTSTRAP, TBRRidge BRB/KFold, AugSynth JK | STAGE_4 coverage audits before any CI surfacing |
| Estimand collapse / pooling | TBR aggregate, multi-cell pooled | STAGE_0→1 contracts before sandbox execution |
| Multiplicity / shared control | multi-cell, per-cell marginal sibling | MULTICELL_CONTRAST_MULTIPLICITY_EVIDENCE_CONTRACT_001 |
| Geometry misspecification | TBRRidge KFold, SCM multi-treated, Placebo | Geometry-class gates in diagnostic-only stage |
| Donor extrapolation | AugSynth JK, SCM multi-treated | Donor hull stress + overlap diagnostics |
| Model misspecification hiding | TBRRidge regularization | False-confidence diagnostic audit |

---

## 9. Shared blockers across methods

1. **Multi-cell contrast + multiplicity semantics** — blocks pooled/global paths, weakens per-cell marginal promotion, and constrains any cross-cell summary. Largest shared leverage.
2. **Pooled/aggregate estimand contract** — blocks TBR aggregate and informs multicell pooling rules.
3. **Coverage validation gap** — common blocker for DID_BOOTSTRAP, TBRRidge uncertainty revival, AugSynth JK.
4. **TBRRidge inference defects** — terminal blockers for BRB/KFold until remediation or retirement.
5. **Multi-treated geometry / placebo semantics** — blocks SCM multi-treated and TBRRidge KFold on multi-treated panels.

---

## 10. Recommended next smallest artifact

**`MULTICELL_CONTRAST_MULTIPLICITY_EVIDENCE_CONTRACT_001`**

Rationale: Multi-cell/pooled semantics and multiplicity policy are the **largest shared blocker** across sophisticated methods. TBR aggregate (STAGE_0), multi-cell pooled/global (STAGE_0), and per-cell marginal promotion (sibling STAGE_5) all require governed contrast taxonomy, shared-control covariance handling, and multiplicity policy before any path advances. This contract is docs/tests-only, smaller than compatibility runtime, and unlocks the widest set of downstream evidence audits.

**Parallel smaller-scope artifact (non-sophisticated top candidate):** `SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001` — remains valid for the strongest non-sophisticated promotion candidate; does not replace multicell contract for pooled/global blockers.

**Alternative:** `PRODUCTION_READINESS_GOVERNANCE_PACKET_CONTRACT_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`

---

## 11. Deferred runtime rationale

`PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` stays **gate-triggered and deferred** because:

1. Zero sophisticated method families at STAGE_6.
2. Zero RANK_4 candidates from `METHOD_PROMOTION_CANDIDATE_AUDIT_001`.
3. Building compatibility runtime before evidence ladder closure would assemble empty or blocked packets.
4. `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001` suffices for semantics until STAGE_6 candidates exist.

**Revisit trigger:** any method family reaches STAGE_6 with bounded blockers and named evidence-gap closure plan.

---

## 12. Authorization boundary

This ladder **promotes nothing** and **unblocks nothing**. Stages are evidence posture labels only.

| Flag | Value |
|------|-------|
| `method_promoted` | false |
| `method_unblocked` | false |
| `production_catalog_unblocked` | false |
| `production_authorization_granted` | false |
| `production_readout_authorized` | false |
| `trusted_business_recommendation_authorized` | false |
| `estimator_implemented` | false |
| `inference_implemented` | false |
| `bootstrap_inference_implemented` | false |
| `ladder_stages_defined` | true |
| `sophisticated_method_inventory_completed` | true |
| `false_confidence_risks_documented` | true |
| `next_smallest_artifacts_recommended` | true |
| `production_compatibility_runtime_deferred` | true |

---

## 13. Validation results

- Summary JSON valid (`docs/track_d/archives/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001_summary.json`)
- Governance tests assert stage taxonomy, method sections, deferral, forbidden flags
- Safety grep: no forbidden `true` promotion/production/computation flags in ladder artifacts

---

## 14. Known limitations

- Stages reflect **documented repo state at base commit** `159cc78`; not a live execution sweep.
- Does not re-run OC batteries or invoke promotion review runtime on live experiments.
- Sibling paths (e.g. `DID_2X2_POINT_ESTIMATE`, per-cell marginal, SCM single-treated JK) are referenced but not re-ranked here.
- STAGE_6 does not imply production approval — compatibility review candidacy only.

---

## 15. Relationship to promotion and compatibility review

| Review type | Ladder role |
|-------------|-------------|
| **Method promotion review** (`METHOD_PROMOTION_REVIEW_RUNTIME_001`) | May evaluate families at STAGE_5+ only; sophisticated families at STAGE_0–4 supply gap evidence, not promotion packets |
| **Production compatibility review** (`PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001`) | Waits on STAGE_6 candidates; runtime deferred |
