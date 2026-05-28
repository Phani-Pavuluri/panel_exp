# Phase 12 INV-017 — calibration governance and archival framework 001

**Investigation:** INV-017 — calibration scaling and governance  
**Status:** governance standard (pre–Run 002)  
**Last updated:** 2026-05-28  
**Package version:** 0.2.1  
**Phase:** 12 — TBRRidge inference investigation program  

**Related:** [`PHASE12_INVESTIGATION_PLAN.md`](PHASE12_INVESTIGATION_PLAN.md) · [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) · [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) · [`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) · [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md) · [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md)

**This document does not:** modify code, run calibration jobs, change eligibility or thresholds, promote estimators, or reorder the roadmap.

---

## 1. Executive purpose

Calibration studies in this project are **governed operating-characteristic (OC) characterization** — not certification exercises and not estimator-promotion mechanisms.

| Principle | Meaning |
|-----------|---------|
| **Characterization ≠ certification** | Archives describe how an instrument behaves under declared scenarios; they do not confer production readiness. |
| **Green tests ≠ nominal validity** | Passing CI smoke tests or recovery plumbing does not satisfy n≥100 production-scale evidence requirements. |
| **Evidence archives are mandatory** | No movement in eligibility, maturity labels, or expert-review expansion without committed markdown archives + governance review. |

**Governed measurement instruments:** Each estimator × inference config is characterized like scientific equipment — with estimand contract, interval contract, OC archive, failure analysis, and intended usage boundary ([`ROADMAP_V4.md`](ROADMAP_V4.md) § Governed measurement instruments).

**Current registry (frozen until Phase 13 decision):**

- `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = {"SCM_UnitJackKnife"}`  
- Removed configs retain skip reasons: `brb_bounds_inverted_run001`, `kfold_multi_treated_unsupported_run001` ([`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md))

**INV-017 role:** Define **how** future calibration runs (starting with Run 002) are archived, interpreted, and connected to eligibility decisions — **before** any new Monte Carlo execution.

---

## 2. Calibration evidence lifecycle

Evidence maturity progresses through **stages**. Movement between stages requires **archived evidence** at the target stage — not implementation completeness alone.

| Stage | Definition | Typical evidence |
|-------|------------|------------------|
| **exploratory** | Ad-hoc diagnostics, n < 25, single seed | Notebook output, local scripts — **not governance-grade** |
| **smoke characterization** | CI-scale runs (n small, few seeds) | `tests/test_recovery_inference_calibration.py` class; informs hypotheses only |
| **production-scale characterization** | n ≥ 100 per config × scenario × seed | Run 001 / Run 002 class archives |
| **governance-reviewed** | Markdown archive + threshold assessment + human review | `CALIBRATION_RUN_XXX.md`, linked failure/OC docs |
| **eligible-for-expert-review** | Registry lists config for relative-ATT nominal path with documented bounds | `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` entry + skip-reason clearance |
| **supported** | Expert-review workflow may cite config for declared use case | Governance decision doc + METHOD_VALIDATION_PLAN path |
| **deprecated** | Still documented; discouraged for new studies | OC shows unfavorable tradeoffs; superseding config exists |
| **research-only** | Available in code; no calibration or promotion claims | Path E in METHOD_VALIDATION_PLAN; permanent skip reason optional |
| **retired** | Removed from nominal path; historical archives retained | Skip reason + failure analysis; no re-entry without full chain |

### Lifecycle rules

1. **No stage skipping** — e.g. smoke → eligible-for-expert-review is invalid without production-scale characterization and governance review.  
2. **Downgrade requires documentation** — removal from eligibility needs failure analysis or OC evidence (Run 001 pattern for BRB/Kfold).  
3. **Conditional stages are explicit** — e.g. SCM jackknife: production-scale + governance-reviewed for **null monitoring only**; not “supported” for lift detection (Phase 11 OC).  
4. **Stage labels are advisory** — they do not auto-update code, cards, or TrustReport implementations in v0.2.1.

---

## 3. Standard calibration archive schema

All future production-scale calibration runs and OC studies must produce a **committed markdown archive** meeting this schema. Run 001 (`CALIBRATION_RUN_001.md`) and Phase 11 (`SCM_JACKKNIFE_CHARACTERIZATION_001.md`) are reference implementations.

### 3.1 Required metadata (header table)

| Field | Required | Example / source |
|-------|----------|------------------|
| Run / archive ID | Yes | `CALIBRATION_RUN_002`, `PHASE12_INV008_BRB_OC_001` |
| Date generated | Yes | ISO date |
| Package version | Yes | `0.2.1` |
| Git commit | Yes | Full SHA |
| Branch | Yes | e.g. `main` |
| Harness | Yes | `run_production_nominal_calibration` and/or `RecoveryRunner` |
| Estimator config(s) | Yes | e.g. `TBRRidge_BlockResidualBootstrap` |
| Inference mode | Yes | Registry name |
| Scenario(s) | Yes | e.g. `recovery_null_effect`, `recovery_positive_effect` |
| Seeds | Yes | e.g. `0, 1, 2` |
| n_simulations | Yes | Per config × scenario × seed |
| Nominal α | Yes | `0.05` |
| Point estimand | Yes | e.g. `relative_att_post` via `_path_relative_att` |
| Interval estimand | Yes | e.g. `relative_att_post` or `unavailable` |
| Interval aligned | Yes | Boolean + `ineligible_reason` when false |
| DGP assumptions | Yes | `missingness_policy`, treated count, pre/post lengths |
| Randomization / interference | When applicable | Expert-review flags; not applicable for synthetic recovery default |
| Production tier tag | Yes | `production` if n ≥ 100; else `smoke` / `exploratory` |
| Raw JSON location | Yes | Local path (typically uncommitted) |
| Prior run comparison | When applicable | Run 001 baseline for Run 002 |

### 3.2 Required metrics (per config × scenario)

Report **mean / std / min / max** across seeds where production harness aggregates (Run 001 pattern).

| Metric | Null scenario | Positive scenario | Notes |
|--------|---------------|-------------------|-------|
| Coverage | Required | Required (informative) | vs threshold ≥ 0.90 on null |
| False positive rate | Required | N/A | vs threshold ≤ 0.10 on null |
| Power | N/A | Informative | Target 0.80 advisory; zero power with coverage 1.0 is a flag (SCM) |
| Interval width | Required when aligned | Required when aligned | Mean width; width/effect ratio |
| Failure rate | Required | Required | vs threshold < 0.05 |
| Recovery success rate | Required | Required | Point finite metrics |
| Significance rate | Recommended | Recommended | Detect always-significant anti-calibration |
| Seed variability | Recommended | Recommended | Flag std > 0.05 on FPR/coverage |
| Failure types | Required if > 0 | Required if > 0 | e.g. `ValueError`, `PATH_INTERVAL_BOUNDS_INVERTED` |
| Inverted CI rate | Required for interval configs | Required | `ci_lower > ci_upper` |

Mark metrics **unavailable** with reason when intervals not aligned — do not impute pass.

### 3.3 Required narrative sections

Every archive must include:

| Section | Content |
|---------|---------|
| **Strengths** | What the config does well (e.g. point recovery, null FPR) |
| **Weaknesses** | Power, width, geometry limits |
| **Failure surfaces** | Scenarios/geometries where runs fail or mis-calibrate |
| **Unsupported conditions** | e.g. multi-treated Kfold on default `recovery_*` |
| **Interpretation boundaries** | What reviewers may and may not claim |
| **Threshold assessment** | Explicit pass/fail/unavailable vs frozen thresholds |
| **Recommendation** | exclude / conditional / monitor-only / research-only / redesign |
| **Comparison to prior archives** | When succeeding Run 001, Phase 11, etc. |

---

## 4. Calibration interpretation policy

### 4.1 What counts as evidence

| Counts | Does not count |
|--------|----------------|
| Production-scale (n ≥ 100) archived run with full metadata | Single-rep or n < 100 without `smoke` tier label |
| Failure analysis explaining mechanism | Threshold adjustment to force pass |
| OC characterization (width, geometry matrix) | Point recovery success alone |
| Alignment flags (`interval_estimand`, `interval_aligned`) | `interval_aligned=true` with inverted or degenerate bounds |
| Multi-seed stability assessment | One lucky seed |
| Governance-reviewed markdown in `docs/` | Uncommitted JSON only |
| Explicit usage boundary (null monitor vs lift detector) | “Passed calibration” without scenario scope |

### 4.2 Why smoke tests are insufficient

- `MIN_REPLICATIONS_FOR_STABLE_CALIBRATION = 100` ([`calibration_report.py`](../../panel_exp/validation/calibration_report.py))  
- Production harness warns below n = 100 ([`production_nominal_calibration.py`](../../panel_exp/validation/production_nominal_calibration.py))  
- Smoke tests (e.g. n = 4 in CI) detect **gross failures** only — not stable FPR/coverage (Run 001 showed BRB could complete 100/100 reps while FPR = 1.0)

### 4.3 Why null-only success is insufficient

A config may pass null FPR and coverage while:

- **Power = 0** on positive scenarios (SCM jackknife — Phase 11)  
- **Intervals are useless for decisions** (width >> |effect|)  
- **Positive scenario shows degenerate significance** (BRB Run 001: power 1.0, coverage 0.0)

Null monitoring and lift detection are **different usage boundaries**. Eligibility and expert-review language must state which is supported.

### 4.4 Why operating characteristics matter more than isolated metrics

Single-metric pass/fail without width, geometry sensitivity, and failure-type context misleads reviewers. Phase 11 demonstrated:

- Perfect null coverage with **zero power everywhere**  
- Width driven by **panel geometry**, not noise or treated count alone  

OC archives answer: *under what conditions is this instrument honest, conservative, or misleading?*

### 4.5 Perfect coverage may indicate over-conservative intervals

**Null coverage = 1.0 and FPR = 0.0 is not automatic proof of good calibration.**

It may indicate **over-coverage** — intervals so wide they always contain zero and the true effect (SCM Run 001 + Phase 11). Interpret alongside:

- Interval width and width/effect ratio  
- Power on positive scenarios  
- Significance rate  

Report over-conservatism as a **documented limitation**, not a hidden success.

---

## 5. Eligibility evolution rules

`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` ([`nominal_calibration.py`](../../panel_exp/validation/nominal_calibration.py)) is the **registry of configs permitted for relative-ATT nominal calibration claims** on declared scenarios. Changes follow these rules:

### 5.1 Adding a config

**Requires all of:**

1. Estimand documented and aligned with recovery scoring  
2. Recovery evidence on standard battery  
3. Production-scale calibration archive (n ≥ 100) with null FPR/coverage assessment  
4. Failure analysis if any prior skip reason existed  
5. OC characterization (width, geometry, failure modes)  
6. Governance decision doc (Phase 13) citing archives  
7. Update to `VALIDATION_COVERAGE.md` and `METHOD_VALIDATION_PLAN.md`  

**No add** based on: code fix alone, smoke pass, or threshold tuning.

### 5.2 Conditional eligibility

A config may be listed with **explicit conditions** in registry notes (pattern: `SCM_UNIT_JACKKNIFE_NOMINAL_CALIBRATION_NOTES`):

- Scenario restrictions (e.g. single-treated only)  
- Null-monitoring-only (no lift-detection claims)  
- Geometry bounds (donor tier, treated count)  

Conditional eligibility must appear in **archive narrative**, **VALIDATION_COVERAGE**, and **skip-reason clearance** — not only in prose.

### 5.3 Removal from eligibility

**Requires:**

- Production-scale or diagnostic evidence of miscalibration or unsupported geometry  
- Failure analysis with mechanism (Run 001 pattern)  
- Entry in `NOMINAL_CALIBRATION_REMOVED_CONFIG_REASONS` with stable skip reason ID  
- No threshold relaxation as substitute  

Removal does **not** remove point-estimate or expert-review use — only nominal calibration claims.

### 5.4 Re-entry after fixes

After inference or correctness fixes (e.g. BRB bound ordering):

1. Fix merged with regression tests — **does not** re-enter eligibility automatically  
2. New production-scale run archived (Run 002 class)  
3. Failure analysis comparing to prior run  
4. OC archive if thresholds fail or usage is conditional  
5. Full advancement policy chain + Phase 13 decision  

Skip reason remains until steps 2–5 complete.

### 5.5 Research-only retention

Configs may permanently remain **research-only** (Path E):

- Documented in METHOD_VALIDATION_PLAN  
- Optional permanent skip reason  
- No nominal calibration claims  
- Acceptable Phase 12 outcome  

### 5.6 Governance gate

> **No eligibility change without archived evidence + governance review.**

Registry PRs must cite: calibration run ID, failure analysis ID (if applicable), OC archive ID, and governance decision ID.

---

## 6. Investigation artifact conventions

### 6.1 Naming patterns

| Artifact type | Pattern | Example |
|---------------|---------|---------|
| Production calibration run | `docs/CALIBRATION_RUN_XXX.md` | `CALIBRATION_RUN_002.md` |
| Failure analysis | `docs/CALIBRATION_FAILURE_ANALYSIS_XXX.md` | `CALIBRATION_FAILURE_ANALYSIS_002.md` |
| OC / geometry characterization | `docs/<TOPIC>_CHARACTERIZATION_XXX.md` or `docs/PHASE12_INV<NNN>_<TOPIC>_XXX.md` | `SCM_JACKKNIFE_CHARACTERIZATION_001.md`, `PHASE12_INV007_KFOLD_GEOMETRY_001.md` |
| Phase 12 track archive | `docs/PHASE12_INV<NNN>_<TOPIC>_XXX.md` | `PHASE12_INV003_AGGREGATION_SEMANTICS_001.md` |
| Governance decision | `docs/GOVERNANCE_DECISION_XXX.md` or Phase 13 memo | Phase 13 TBRRidge decision |
| Investigation plan | `docs/PHASE12_INVESTIGATION_PLAN.md` | Pre-execution plan |
| Governance framework | `docs/PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md` | This document |

**XXX** = zero-padded sequential integer within artifact family (001, 002, …).

### 6.2 Raw JSON policy

| Policy | Detail |
|--------|--------|
| **Default** | Raw harness JSON remains **local and uncommitted** (e.g. `.calibration_run_002.json`) |
| **Markdown is source of truth** | Committed archives contain aggregated tables + interpretation |
| **Archive header** | Must record local JSON path and generation command |
| **Future change** | Committing raw JSON requires separate governance decision — not in v0.2.1 |

### 6.3 Cross-linking requirements

Each archive must link:

- Upstream: investigation ID, investigation plan section, prior runs  
- Downstream: failure analysis, OC deep-dive, OPEN_INVESTIGATIONS status update  
- Registry: VALIDATION_COVERAGE row and skip reason if applicable  

---

## 7. TrustReport implications (future-facing)

This section connects calibration evidence to **future** platform semantics — **no implementation schemas in v0.2.1**.

| Future artifact | Calibration evidence inputs |
|-----------------|----------------------------|
| **`CalibrationSignal` lifecycle** | Stage from §2; skip reasons; OC summary; last run ID |
| **`TrustReport` outcomes** | Map OC to `supported_*`, `inconclusive`, `underpowered`, `calibration_unavailable`, `incompatible_estimand` ([`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md)) |
| **`ReleaseGate`** | Human review checkpoint — requires governance-reviewed stage + Phase 13 decision for eligibility changes |
| **`ExperimentEvidence`** | Pointers to run archive IDs, interval_estimand, alignment flags, usage boundary |
| **`ExperimentSpec`** | Declared scenario eligibility — e.g. single-treated-only for Kfold |
| **MMM calibration compatibility** | INV-023 — only `supported` or conditional stages with calibrated contribution mapping |
| **Conversational orchestration** | LLM responses must cite archive IDs and state interpretation boundaries; no unsourced promotion |

**Trust boundary rule:** Calibration archives inform **honest limits** (`calibration_unavailable`, `inconclusive`) — not automated approval.

---

## 8. Phase 12 governance sequencing

Official execution order for Phase 12. **Do not run Run 002 before this framework is committed and reviewed.**

| Step | Action | Investigation | Output artifact |
|------|--------|---------------|-----------------|
| **1** | **Governance framework** | INV-017 | **`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`** (this doc) |
| **2** | Production calibration Run 002 | INV-008 | `CALIBRATION_RUN_002.md` + local JSON |
| **3** | Failure analysis (if thresholds fail or vs Run 001) | INV-008 | `CALIBRATION_FAILURE_ANALYSIS_002.md` |
| **4** | KFold geometry characterization | INV-007 | `PHASE12_INV007_KFOLD_GEOMETRY_001.md` |
| **5** | Multi-treated aggregation semantics | INV-003 | `PHASE12_INV003_AGGREGATION_SEMANTICS_001.md` |
| **6** | Governance decision memo | Phase 13 prep | `GOVERNANCE_DECISION_002.md` (or Phase 13 doc) |
| **7** | Eligibility reconsideration | Phase 13 | Registry PR **only if** step 6 approves + full policy chain |

Steps 4–5 may proceed in parallel with step 3 after step 2 completes. Step 7 is **never** parallel with step 2.

**Run 002 scope (step 2):** `TBRRidge_BlockResidualBootstrap` on default `recovery_null_effect` / `recovery_positive_effect`; n = 100; seeds 0, 1, 2; frozen thresholds — per [`PHASE12_INVESTIGATION_PLAN.md`](PHASE12_INVESTIGATION_PLAN.md) § INV-008.

---

## 9. Non-goals

This framework and Phase 12 execution **explicitly exclude:**

| Non-goal | Rationale |
|----------|-----------|
| Estimator ranking / leaderboards | Governed instruments, not competitions |
| Auto-promotion from pass metrics | Human governance + policy chain |
| `production_safe` labels | Not claimed in v0.2.1 |
| Threshold tuning to pass | Mechanism docs required instead |
| Estimator proliferation | Phase 12 characterizes existing TBRRidge modes |
| Package-wide “calibrated” marketing | SCM null monitor only today |
| Committing raw JSON by default | Markdown archives sufficient |
| API / schema implementation | Track B deferred |
| Reordering Tracks A/B/C | Roadmap sequencing unchanged |

---

## 10. Success criteria

Phase 12 (and INV-017) succeed when the program produces **honest characterization and governed evidence** — not necessarily TBRRidge rehabilitation.

| Success signal | Example |
|----------------|---------|
| Run 002 archived to standard schema | Complete metadata + metrics + narrative |
| Failure mechanism documented when OC fails | `CALIBRATION_FAILURE_ANALYSIS_002.md` |
| Geometry and aggregation contracts written | INV-007, INV-003 archives |
| Eligibility unchanged unless Phase 13 approves | BRB may remain excluded with evidence |
| OPEN_INVESTIGATIONS updated with archive links | INV-008/007/003/017 statuses |
| Reviewers can state usage boundaries | “Null monitor only”, “single-treated only”, “research-only” |

**Acceptable successful outcomes:**

- BRB intervals valid post-fix but **remain excluded** (FPR/coverage/width)  
- Kfold **single-treated-only** permanently  
- **No** TBRRidge config re-enters `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`  
- Governance playbook adopted for Run 003+ and Track B `CalibrationSignal` design  

**Failure of Phase 12 governance (process):**

- Run 002 executed without this framework  
- Eligibility changed without archive + decision doc  
- Thresholds tuned without mechanism analysis  
- “Passed Run 002” claimed without usage boundary narrative  

---

## Appendix A — Frozen threshold reference (Run 001 policy)

Do not change in Phase 12 without separate governance amendment.

| Metric | Null scenario | Source |
|--------|---------------|--------|
| Coverage | ≥ 0.90 | `MIN_COVERAGE_UNDER_NULL` |
| FPR | ≤ 0.10 | `MAX_FALSE_POSITIVE_RATE` |
| Failure rate | < 0.05 | Run 001 / production harness |
| Power (informative) | target 0.80 | Readiness / Run 001 positive scenario |
| n_simulations (production) | ≥ 100 | `MIN_REPLICATIONS_FOR_STABLE_CALIBRATION` |

---

## Appendix B — Advancement policy chain (eligibility reconsideration)

From [`ROADMAP_V4.md`](ROADMAP_V4.md) § Promotion policy — all steps required before registry add or expanded expert-review support:

1. Estimand definition  
2. Recovery evidence  
3. Calibration evidence (n ≥ 100)  
4. Failure analysis (when calibration fails or skip reason existed)  
5. Operating-characteristic characterization  

---

## Appendix C — Investigation cross-reference

| ID | This framework enables |
|----|------------------------|
| INV-008 | Run 002 archive schema, interpretation policy |
| INV-007 | OC artifact naming, geometry narrative requirements |
| INV-003 | Estimand / aggregation interpretation boundaries |
| INV-017 | This document — closes governance template step |
| Phase 13 | Eligibility evolution rules §5 |

---

*Governance standard INV-017-001. Does not modify code, eligibility, thresholds, or maturity labels. Execute Run 002 only after review of this framework.*
