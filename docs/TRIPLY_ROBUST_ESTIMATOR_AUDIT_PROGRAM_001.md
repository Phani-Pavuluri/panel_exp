# Triply Robust Estimator Audit Program 001

**Document ID:** TRIPLY-ROBUST-ESTIMATOR-AUDIT-PROGRAM-001  
**Title:** Triply Robust Estimator Audit Program 001  
**Status:** **Proposed** — parked future estimator family  
**Scope:** GeoX / `panel_exp` documentation and governance  
**Artifact type:** Deferred estimator audit program — **no implementation**  
**Date:** 2026-06-09  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) · [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md)

**Companions:** [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md)

**Guardrails:** No TROP implementation · no new dependencies · no promotion · no suitability claim · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Triply Robust Estimator Audit Program 001 |
| Status | **Proposed** — parked future estimator family |
| Scope | GeoX / `panel_exp` documentation and governance |
| Artifact type | Deferred estimator audit program |

Triply robust / **TROP** estimation is **not rejected**. It is **parked** behind a full audit ladder so it may later integrate with current GeoX infrastructure under explicit contracts — the same rigor applied to SCM, AugSynth, TBR, DID, MCELL, and TBRRidge characterization paths.

---

## 2. Purpose

GeoX may eventually evaluate **triply robust** panel estimators as a **candidate estimator family** for covariate-adjusted causal effects with nuisance-model robustness. Before any implementation work, promotion discussion, or product wiring, the program requires:

- Literature-aligned estimand and identification assumptions  
- Implementation gap analysis against the current repo  
- Statistical validation protocol with nuisance-model stress worlds  
- Combination matrix and geometry placement  
- Suitability extension under framework v2  

This artifact defines that **audit program**. It does **not** implement TROP or authorize use on current GeoX data.

---

## 3. Why TROP is parked

| Factor | Implication |
|--------|-------------|
| **D5 queue focus** | Level B characterization completed for **existing** SCM-JK, AugSynth point, TBR aggregate, DID bootstrap, MCELL per-cell, and TBRRidge inference — not TROP. |
| **Identification structure** | TROP depends on **outcome**, **treatment/assignment**, and **selection/transport** nuisance models — a different causal stack than synthetic-control or ridge counterfactual paths. |
| **Metadata gaps** | Covariates, propensity/overlap, eligibility, trimming, and target population are **not yet governed** by [`DESIGN_OUTPUT_CONTRACT_001`](METHOD_ENHANCEMENT_ROADMAP_001.md) (planned). |
| **Infrastructure contract** | TROP must connect to design outputs, readout semantics, and geometry bridges **explicitly** — not by silent reuse of SCM/TBR/DID panels. |
| **Existing repo posture** | `TROP` class exists in `panel_exp/methods/triply_robust_est.py` at **`research_only`** — validation runner skipped; no registry inference surface; no D5-STAT characterization archive. |

**Parked ≠ rejected.** TROP may proceed only through the audit ladder below.

---

## 4. What “triply robust” means in this project

**Candidate robustness components** (to be confirmed by `TRIPLY_ROBUST_LITERATURE_ALIGNMENT_001`):

| Component | Candidate role |
|-----------|----------------|
| **Outcome model** | Models potential outcomes or conditional expectations given covariates. |
| **Treatment / assignment model** | Models treatment probability, assignment mechanism, or exposure given covariates. |
| **Selection / missingness / transport model** | Models sample inclusion, attrition, or transport to target population. |

**Triply robust** (candidate definition): the estimand remains **consistent** if **any one** of the three nuisance models is correctly specified (plus regularity/overlap), under the formal target cited in literature alignment — not assumed here.

These are **candidate components** until literature alignment names the exact theorem, estimand, and failure modes for the GeoX use case.

---

## 5. Intended estimator role

Possible **future** roles (none authorized today):

| Role | Notes |
|------|-------|
| **Unit-level / market-level covariate panels** | Natural fit when covariates and assignment metadata exist per geo. |
| **Adjusted treatment effects** | Where assignment, outcomes, and selection/transport are explicitly modeled. |
| **Complement to SCM/TBR/DID** | **Not** a default replacement; parallel estimator family with its own evidence ladder. |
| **Aggregate 2-row geometry** | **Not valid by default** — blocked unless a later spec and bridge justify aggregate nuisance-model geometry. |

---

## 6. Relationship to current infrastructure

TROP integration (future) must connect to:

| Layer | Requirement |
|-------|-------------|
| **Design outputs** | Assignment, eligibility, inclusion/exclusion, target population ([`DESIGN_OUTPUT_CONTRACT_001`](METHOD_ENHANCEMENT_ROADMAP_001.md) — planned) |
| **Assignment metadata** | Treatment timing, cell, propensity inputs |
| **Outcome panels** | Pre/post wide or long format with consistent unit index |
| **Covariates** | Governed covariate table contract (future) |
| **Treatment / assignment model** | Propensity or assignment mechanism interface |
| **Selection / transport** | Eligibility, trimming, missingness metadata |
| **Readout semantics** | [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) — effect scale, interval target, null vs directional |
| **Geometry bridge** | [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) — nuisance-model geometry not yet accepted |
| **Suitability v2** | Separate extension artifact after audit ladder |

---

## 7. Required audit ladder

Full sequence — **order preserved**; later steps blocked until earlier artifacts are **Accepted**:

### A. TRIPLY_ROBUST_LITERATURE_ALIGNMENT_001

Compare candidate TROP formulations to literature; define:

- Estimand (ATE, ATT, transported effect, etc.)  
- Identifying assumptions  
- Nuisance components and robustness theorem target  
- Required data geometry  
- Inference prescription (IF, bootstrap, cross-fit variance)  
- Known failure modes (overlap, model misspecification, transport violation)

### B. TRIPLY_ROBUST_IMPLEMENTATION_GAP_ANALYSIS_001

Inspect repo; document:

- Whether TROP code exists and its surface (`triply_robust_est.py`, `tests/trop_test.py`)  
- Outcome-model infrastructure  
- Assignment/propensity infrastructure  
- Selection/transport/missingness infrastructure  
- Cross-fitting support  
- Nuisance diagnostics  
- Variance / influence-function inference  
- Gap list for governed integration

### C. TRIPLY_ROBUST_STATISTICAL_VALIDATION_PROTOCOL_001

Define validation worlds (nuisance correctness patterns):

- All nuisance models correct  
- Outcome model correct only  
- Assignment model correct only  
- Selection/transport model correct only  
- Two of three correct  
- All three wrong  
- Poor overlap / positivity violation  
- High-dimensional covariates  
- Small sample / few markets  
- Geo heterogeneity  
- Trimmed population / transport stress  
- Post-period shock  

### D. TRIPLY_ROBUST_COMBINATION_MATRIX_001

Define allowed / deferred / blocked combinations:

- Valid geometries  
- Estimator variants  
- Inference variants  
- Readout targets  
- Bridge-required cases  
- **Blocked:** `aggregate_two_row` unless explicitly justified

### E. TRIPLY_ROBUST_SUITABILITY_EXTENSION_001

Placement under suitability framework v2:

- `blocked` · `research_only` · `characterization_candidate` · `bridge_required` · `not_applicable` · future suitability candidate — **one explicit classification per combination row**

### F. Future D5-style characterization

**Only if** implementation exists or is added under a **separate implementation plan** — not part of this audit-program artifact.

---

## 8. Conceptual gaps to close

| Gap | Open question |
|-----|----------------|
| **Target estimand** | ATE, ATT, transported effect, incremental lift, geo-level effect? |
| **Unit of analysis** | User, market, geo, cell, aggregate? |
| **Treatment definition** | Binary, staggered, continuous exposure? |
| **Assignment model** | Randomized geo, observational propensity, design-based? |
| **Outcome model** | Panel outcome specification, time trends |
| **Selection / transport / missingness** | Eligibility, trimming, target population |
| **Overlap / positivity** | Diagnostics and blocking rules |
| **Cross-fitting** | Required for sample splitting? |
| **Nuisance diagnostics** | Residual, calibration, overlap plots |
| **Variance estimator** | IF, sandwich, bootstrap — interval target |
| **Interval target** | Causal estimand vs nuisance instability |
| **Readout scale** | Level, log, percent — per readout semantics |
| **Geometry compatibility** | Which canonical geometry IDs apply |
| **Sensitivity to nuisance failure** | Partial robustness behavior |
| **Randomized geo design** | Compatibility with current design methods |

---

## 9. Statistical validation requirements

TROP cannot advance beyond **research-only** without simulation worlds testing **nuisance-model correctness patterns** (§7.C).

**Required metrics** (minimum):

| Metric | Purpose |
|--------|---------|
| Bias | Estimand recovery |
| RMSE | Precision |
| Coverage | Named coverage target per readout semantics |
| Sign error | Injected-world direction |
| Null false positive rate | Null decision rule |
| Overlap diagnostics | Positivity/support |
| Nuisance model error | Per-component fit quality |
| Cross-fit stability | Split-seed sensitivity |
| Sensitivity to trimming/selection | Transport stress |
| Failure / block register | Explicit skips and blocks |

---

## 10. Infrastructure requirements

Future governed TROP integration requires (not implemented here):

| Component | Description |
|-----------|-------------|
| **Covariate table contract** | Unit × time × covariate schema |
| **Assignment metadata contract** | Treatment, timing, cell, design id |
| **Outcome model interface** | Pluggable outcome nuisance fit |
| **Assignment/propensity interface** | Treatment mechanism fit |
| **Selection/transport interface** | Inclusion and transport model |
| **Cross-fitting splitter** | Sample partitions without leakage |
| **Influence-function / readout calculator** | Point + variance with explicit scale |
| **Nuisance diagnostics registry** | Standard diagnostic outputs |
| **Validation fixture generator** | Nuisance-world DGPs |
| **Report / archive schema** | TROP audit + future D5 JSON fields |

---

## 11. Relationship to INFERENCE_READOUT_SEMANTICS_001

Per [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md):

- **TROP effect scale** must be explicit (`effect_scale`, `point_estimand`).  
- **TROP interval target** must be explicit — influence-function, sandwich, or bootstrap intervals are **not** automatically **causal intervals** without assumptions and validation.  
- **Null decision** and **directional signal** remain **separate** metrics.  
- Classification default: `causal_interval_candidate_requires_validation` or `resampling_interval_target_ambiguous` until protocol passes.

---

## 12. Relationship to GEOMETRY_BRIDGE_REQUIREMENTS_001

Per [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md):

- TROP uses **future nuisance-model estimator geometry** — **not yet accepted**.  
- Current D5 geometries (`unit_panel_single_cell`, `aggregate_two_row`, `pooled_treated_control_panel`, `multi_cell_per_cell`) do **not** automatically support TROP.  
- **Transport** or **trimmed-population** claims require a **geometry bridge**.  
- **`aggregate_two_row`** remains **blocked** for TROP until combination matrix + bridge justify it.

Future geometry declarations must include:

- Unit-level vs market-level covariate layout  
- Treatment assignment geometry  
- Selection/transport geometry  
- Target population

---

## 13. Relationship to DESIGN_OUTPUT_CONTRACT_001

TROP depends heavily on **design-layer metadata** (planned [`DESIGN_OUTPUT_CONTRACT_001`](METHOD_ENHANCEMENT_ROADMAP_001.md)):

- Assignment fields  
- Eligibility and inclusion/exclusion  
- Covariate availability flags  
- Target population declaration  

TROP **cannot** be evaluated properly until design output exposes these fields in a governed contract. **DESIGN_OUTPUT_CONTRACT_001** remains the **immediate** post-geometry enhancement artifact — not TROP implementation.

---

## 14. Current status

| Dimension | Status |
|-----------|--------|
| TROP characterization (D5) | **None** |
| TROP implementation acceptance | **None** — `research_only` code exists; runner skipped |
| TROP suitability status | **None** — no row advancement |
| TrustReport role | **Blocked** |
| CalibrationSignal eligibility | **Blocked** |
| MMM / LLM use | **Blocked** |

Existing references: `TROP-RESEARCH` in combination matrix / suitability register at **`research_only`** / **`research_only_oc`** — unchanged by this artifact.

---

## 15. Governance gates

TROP cannot move forward until **all** are satisfied:

1. `TRIPLY_ROBUST_LITERATURE_ALIGNMENT_001` — **Accepted**  
2. `TRIPLY_ROBUST_IMPLEMENTATION_GAP_ANALYSIS_001` — **Accepted**  
3. `TRIPLY_ROBUST_STATISTICAL_VALIDATION_PROTOCOL_001` — **Accepted**  
4. `TRIPLY_ROBUST_COMBINATION_MATRIX_001` — **Accepted**  
5. Geometry requirements satisfied per [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) + TROP geometry extension  
6. Readout semantics satisfied per [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md)  
7. [`DESIGN_OUTPUT_CONTRACT_001`](METHOD_ENHANCEMENT_ROADMAP_001.md) supplies required metadata  
8. D5-style characterization passes **if** implementation exists  
9. `TRIPLY_ROBUST_SUITABILITY_EXTENSION_001` explicitly approves a role  

---

## 16. Non-goals

- No TROP implementation or new dependencies  
- No estimator, inference, or design code changes  
- No D5 archive regeneration  
- No promotion or suitability claim  
- No TrustReport role, CalibrationSignal eligibility, MMM, or LLM usage  
- No claim that TROP is valid for current GeoX production data  

---

## 17. Roadmap and audit updates checked

| Document | Update |
|----------|--------|
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | TROP deferred family + audit ladder |
| [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) | Future TROP readout implications |
| [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) | Future TROP geometry |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Deferred estimator audit track |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Future TROP audit placement |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Artifact registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Parked estimator cross-link |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | No current suitability; audit ladder required |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | TROP deferred; own combination matrix |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | TROP requires own protocol |

**D5 reports inspected:** SCM-JK, AugSynth point, TBR aggregate, DID bootstrap, MCELL per-cell, TBRRidge inference (context for parked status).

---

*TRIPLY-ROBUST-ESTIMATOR-AUDIT-PROGRAM-001 v1.0.0 — Proposed; parked future estimator family. Immediate program next artifact remains DESIGN_OUTPUT_CONTRACT_001.*
