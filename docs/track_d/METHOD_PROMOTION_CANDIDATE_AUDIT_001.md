# METHOD_PROMOTION_CANDIDATE_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PROMOTION_CANDIDATE_AUDIT_001` |
| **Artifact type** | `method_promotion_candidate_audit` |
| **Status** | `completed` |
| **Scope** | `method_promotion_candidates_ranked_no_method_promotion_or_catalog_change` |
| **Base commit** | `9cfcaa2` (Define production compatibility promotion review contract) |
| **Final verdict** | `method_promotion_candidates_ranked_no_method_promotion_or_catalog_change` |

**Depends on:** `METHOD_PROMOTION_REVIEW_RUNTIME_001` · `METHOD_PROMOTION_REVIEW_CONTRACT_001` · `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001` · `TRUSTED_READOUT_REPORT_RUNTIME_001` · `CLAIM_AUTHORIZATION_RUNTIME_001` · `PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001` · `METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001`

---

## 2. Source files inspected

- `docs/ROADMAP_V4.md` · `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md` · `docs/MIP_AUDIT_REGISTRY.md`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`
- `docs/track_d/METHOD_PROMOTION_REVIEW_CONTRACT_001_REPORT.md` · `METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md` · `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001_REPORT.md`
- `docs/track_d/METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001.md`
- `docs/F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md` · `docs/GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md`
- `docs/MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001.md`
- `panel_exp/validation/production_catalog_blocklist_001.py` · `nominal_calibration.py`
- `panel_exp/validation/method_promotion_review_runtime_001.py`
- `panel_exp/validation/production_compatibility_promotion_review_contract_001.py`
- `docs/track_d/archives/D5_INST_AUDIT_001_results.json` · `ROADMAP_REFOCUS_METHOD_VALIDATION_001_summary.json`

---

## 3. Why production compatibility runtime is deferred

`PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` is **gate-triggered and deferred** until at least one method/instrument has a credible, evidence-backed promotion path.

Reasons:

1. **No RANK_4 candidates** — no combo has existing evidence strong enough for production-compatibility review readiness without hard blockers.
2. **Over-engineering risk** — building a compatibility runtime before identifying real promotion candidates would assemble packets for empty or blocked inventories.
3. **Contract is sufficient for now** — `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001` defines semantics; runtime waits on candidate evidence.
4. **Promotion review stack is complete** — method promotion review contract/runtime can evaluate eligibility when candidates exist; compatibility runtime adds value only after ranked candidates emerge.

**Revisit trigger:** completion of `SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001` (or equivalent) showing a candidate at RANK_3+ with bounded blockers and a named evidence gap closure plan.

---

## 4. Candidate ranking taxonomy

| Rank | Label | Meaning |
|------|-------|---------|
| **RANK_0** | `RANK_0_BLOCKED_DO_NOT_ADVANCE` | Hard catalog blockers, invalid inference, or policy-forbidden paths |
| **RANK_1** | `RANK_1_DEFER_UNTIL_METHOD_EVIDENCE` | Diagnostic/research posture; defer until family validation strengthens |
| **RANK_2** | `RANK_2_EVIDENCE_BUILDING_CANDIDATE` | Smallest next step is targeted evidence audit or validation artifact |
| **RANK_3** | `RANK_3_RESTRICTED_REVIEW_CANDIDATE` | May enter restricted/governed promotion review with caveats; not production approval |
| **RANK_4** | `RANK_4_PRODUCTION_COMPATIBILITY_REVIEW_CANDIDATE` | Strong review readiness; still not production approval |

**Conservative rule:** RANK_4 requires visible evidence across promotion review prerequisites and no hard blockers. **No candidate received RANK_4 in this audit.**

---

## 5. Method/instrument inventory summary

| Candidate | method_id / instrument_id | Catalog status | Rank | Promotion posture |
|-----------|---------------------------|----------------|------|-------------------|
| SCM + UnitJackKnife | `SCM` / `SCM_UnitJackKnife` | restricted / governed null monitor | **RANK_3** | restricted_review_candidate |
| SCM + Placebo | `SCM` / `SCM_Placebo` | diagnostic / falsification | **RANK_2** | evidence_building_candidate |
| DID + bootstrap | `DID` / `DID_BOOTSTRAP` | blocked | **RANK_0** | no_promotion |
| DID 2×2 point estimate | `DID` / `DID_2X2_POINT_ESTIMATE` | restricted expert review | **RANK_3** | restricted_review_candidate |
| per-cell marginal readout | multicell / `marginal_per_cell` | governed per-cell restricted | **RANK_3** | restricted_review_candidate |
| AugSynth point-only | `AugSynthCVXPY` / `AugSynthCVXPY_Point` | diagnostic / research | **RANK_2** | evidence_building_candidate |
| AugSynth + JK | `AugSynthCVXPY` / `AugSynth_Jackknife` | diagnostic-only | **RANK_1** | defer |
| TBRRidge + BRB | `TBRRidge` / `TBRRidge_BlockResidualBootstrap` | blocked | **RANK_0** | no_promotion |
| TBRRidge + KFold | `TBRRidge` / `TBRRidge_Kfold` | blocked | **RANK_0** | no_promotion |
| TBRRidge + Placebo | `TBRRidge` / `TBRRidge_Placebo` | diagnostic / restricted | **RANK_2** | evidence_building_candidate |
| TBR aggregate / pooled | `TBR` / aggregate paths | blocked | **RANK_0** | no_promotion |
| multi-cell pooled/global | multicell / pooled lift | blocked | **RANK_0** | no_promotion |
| SCM multi-treated production | `SCM` / multi-treated inference | blocked / unresolved | **RANK_1** | defer |
| SyntheticDID | `SyntheticDID` | research-only | **RANK_1** | defer |
| TROP / MTGP / BayesianTBR | various | research-only | **RANK_1** | defer |
| AugSynth + Conformal | `AugSynthCVXPY` / Conformal | diagnostic-only | **RANK_1** | defer |

---

## 6. Per-candidate evidence and blockers

### SCM + UnitJackKnife — RANK_3

- **Catalog:** `PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW`; only entry in `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`.
- **Evidence present:** Run 001 null FPR/coverage pass; F-DECISION `primary_null_monitor`; governed runtime path; blocklist enforcement; method promotion review stack.
- **Evidence missing:** Lift/power characterization; full statistical promotion threshold battery for promotion scope; production compatibility human-governance packet; MMM-scale readout bridge.
- **Blockers:** `null_monitor_only` — not lift detector; zero power in Run 001; intervals ~15× effect width (conservatism).
- **Readiness:** trusted readout partial (point/null); claim auth blocks causal/ROI; statistical promotion not passed for promotion; assignment/SRM chain available at runtime layer but not combo-specific.
- **Next smallest artifact:** `SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001`
- **Do not build now:** production compatibility runtime; production approval; MMM ingestion.

### SCM + Placebo — RANK_2

- **Catalog:** falsification / null-reference diagnostic (`falsification_check` in F-DECISION).
- **Evidence present:** Track B placebo semantics documented; single-treated constraint known.
- **Evidence missing:** `SCM_PLACEBO_GOVERNED_SEMANTICS_001` package contract; governed runtime binding; promotion threshold evidence.
- **Blockers:** single-treated only; not a promotion target until governed semantics land.
- **Next smallest artifact:** `SCM_PLACEBO_GOVERNED_SEMANTICS_001` (or fold into evidence audit family).

### DID + bootstrap — RANK_0

- **Catalog:** `PRODUCTION_CATALOG_BLOCKED` — inference not implemented in governed runtime (`BLOCKER_INFERENCE_NOT_IMPLEMENTED`).
- **Evidence:** `D5_STAT_DID_BOOTSTRAP_001`; estimand unification complete but bootstrap runtime deferred.
- **Blockers:** `did_bootstrap_inference_family_blocked`; uncalibrated; misleading instrument ID policy.
- **Next smallest artifact:** `DID_BOOTSTRAP_PROMOTION_EVIDENCE_AUDIT_001` **after** bootstrap executor exists — **defer now**.
- **Do not build now:** bootstrap inference runtime (`ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_004`); catalog unblock.

### DID 2×2 point estimate — RANK_3

- **Catalog:** `PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW`; first governed DID executor exists.
- **Evidence present:** `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001`; point-estimate execution runtime; assignment integrity / SRM / claim auth integration paths.
- **Evidence missing:** Statistical promotion pass; uncertainty governance; bootstrap separation policy closure.
- **Blockers:** `point_estimate_only_no_uncertainty`; production claims blocked without thresholds.
- **Next smallest artifact:** `DID_2X2_POINT_ESTIMATE_PROMOTION_EVIDENCE_AUDIT_001` (secondary to SCM JK).

### per-cell marginal readout — RANK_3

- **Catalog:** governed per-cell restricted (`DCM-006`); `marginal_per_cell_readout_allowed` under `PARALLEL_MARGINAL_CELLS`.
- **Evidence present:** multicell decision policy contract; `D5-TRUST-MULTICELL-PERCELL-INFERENCE-001` lineage.
- **Evidence missing:** multiplicity calibration; familywise error governance; promotion threshold per cell.
- **Blockers:** `multicell_percell_multiplicity_unresolved`; no pooled causal claim.
- **Next smallest artifact:** `PERCELL_MARGINAL_READOUT_PROMOTION_EVIDENCE_AUDIT_001`

### AugSynth point-only — RANK_2

- **Catalog:** diagnostic / research characterized (`AugSynthCVXPY_Point` in D5_INST audit).
- **Evidence present:** point recovery wiring; unit tests; CVXPY path exists.
- **Evidence missing:** null calibration; ASCM remediation; promotion thresholds.
- **Blockers:** `diagnostic_research_only_until_null_calibration`; no governed causal readout.
- **Next smallest artifact:** `AUGSYNTH_POINT_ONLY_VALIDATION_EVIDENCE_AUDIT_001`

### AugSynth + JK — RANK_1

- **Catalog:** diagnostic-only; estimand/scale bridge blocks causal readout.
- **Defer until:** `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` and stronger validation.

### TBRRidge + BRB / KFold — RANK_0

- **BRB:** `brb_bounds_inverted_run001` — inverted CI bounds; removed from eligibility.
- **KFold:** `kfold_multi_treated_unsupported_run001` — geometry failure on multi-treated.
- **Do not advance** until `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001` remediation paths close.

### TBRRidge + Placebo — RANK_2

- **Catalog:** diagnostic comparator; restricted.
- **Evidence building only** — no promotion path until inference rehabilitation.

### TBR aggregate / pooled / multi-cell pooled — RANK_0

- **Blockers:** `BLOCKER_AGGREGATE_MISMATCH`; pooled lift ADR unresolved; F-P0-006 pooling rule required.
- **Do not build now:** aggregate production paths; global lift claims.

### SCM multi-treated production inference — RANK_1

- **Defer:** multi-treated placebo/randomization inference unresolved (`MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001`).

### Research-only families (SyntheticDID, TROP, MTGP, BayesianTBR) — RANK_1

- **Catalog:** `PRODUCTION_CATALOG_RESEARCH_ONLY`.
- **Defer** until family validation plans complete.

---

## 7. Top ranked candidates (none at RANK_4)

1. **SCM + UnitJackKnife** — strongest evidence base (null calibration eligible); restricted review only.
2. **per-cell marginal readout** — governed multicell contract exists; multiplicity remains blocker for promotion.
3. **DID 2×2 point estimate** — governed executor exists; point-only restriction remains.

**No candidate is production-compatibility-review ready (RANK_4).**

---

## 8. Deferred candidates and artifacts

| Item | Reason |
|------|--------|
| `DID_BOOTSTRAP` | Catalog blocked; no governed bootstrap runtime |
| `TBRRidge` BRB/KFold | Terminal inference defects documented |
| TBR aggregate / pooled multicell | Aggregate semantics unresolved |
| `AugSynth` JK / Conformal | Diagnostic-only until remediation |
| `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` | No RANK_4 candidates; over-engineering risk |

---

## 9. Recommended next smallest artifact

**`SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001`**

Rationale: SCM + UnitJackKnife is the only nominally calibration-eligible combo with governed null-monitor role, existing blocklist posture, and a plausible restricted-review path. A focused evidence audit is smaller than compatibility runtime and names concrete gaps before any promotion review packet is attempted.

**Alternative:** `PRODUCTION_READINESS_GOVERNANCE_PACKET_CONTRACT_001`

**If no method progresses after evidence audit:** `METHOD_PROMOTION_EVIDENCE_GAP_WORKPLAN_001`

---

## 10. Authorization boundary

This audit **promotes nothing**. Rankings are review eligibility hints only. All authorization flags remain false. No catalog status changes. No runtime implementation.

| Flag | Value |
|------|-------|
| `method_promoted` | false |
| `production_authorization_granted` | false |
| `production_catalog_unblocked` | false |
| `production_compatibility_runtime_deferred` | true |

---

## 11. Validation results

- Summary JSON valid
- Governance tests assert taxonomy, candidates, deferral, and forbidden flags
- Safety grep: no forbidden `true` promotion/production flags

---

## 12. Known limitations

- Rankings reflect **documented repo state at base commit**; not a live execution sweep.
- Does not invoke `generate_method_promotion_review` on live experiments.
- Per-candidate statistical promotion readiness is inferred from catalog/docs, not re-run OC batteries.

---

## 13. Recommended next artifact

**`SCM_UNIT_JACKKNIFE_PROMOTION_EVIDENCE_AUDIT_001`**

**Alternative:** `PRODUCTION_READINESS_GOVERNANCE_PACKET_CONTRACT_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`
