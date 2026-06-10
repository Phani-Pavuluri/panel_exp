# Experiment Planning Orchestration Roadmap 001

**Document ID:** EXPERIMENT-PLANNING-ORCHESTRATION-ROADMAP-001  
**Title:** Experiment Planning Orchestration Roadmap 001  
**Status:** **Deferred / future** — parked roadmap only  
**Scope:** GeoX / `panel_exp` / MMM / MIP future experiment-planning recommendation layer  
**Artifact type:** Documentation / governance — **no implementation**  
**Date:** 2026-06-09  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) · [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md)

**Companions:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md)

**Guardrails:** No recommendation logic · no ranking implementation · no LLM orchestration · no MMM integration · no GeoX execution · no design/estimator/inference selection code · no promotion · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Purpose

This artifact **parks** the future platform layer where:

1. **MMM/MIP** identifies an experiment need (decision gap, uncertainty, scope).  
2. **GeoX / design layer** generates feasible design candidates with diagnostics and power/MDE estimates.  
3. **Suitability layer** evaluates **design × estimator × inference × geometry × readout** combinations — including blocked and bridge-required paths.  
4. **Trust layer** blocks unsafe choices and emits pass/warn/block with required caveats.  
5. **LLM layer** explains the recommendation, blocked alternatives, and required human decisions — **without overriding statistical gates**.

The lane is **not rejected**. It is **explicitly deferred** until design, estimator, inference, geometry, and readout governance are complete. This document prevents the planning/orchestration vision from being lost while keeping it out of the immediate implementation queue.

---

## 2. Future artifacts (parked — not started)

| Artifact ID | Status | Role |
|-------------|--------|------|
| **`EXPERIMENT_RECOMMENDATION_CONTRACT_001`** | **Parked / future** | Input/output contract between MMM/MIP, GeoX, suitability, trust, and LLM |
| **`DESIGN_CANDIDATE_RANKING_POLICY_001`** | **Parked / future** | Candidate generation, hard filters, scoring, tie-breakers, explanation requirements |
| **`EXPERIMENT_PLANNING_DECISION_SURFACE_001`** | **Parked / future** | Decision surface schema: recommended candidate, alternatives, blocks, risk, human next action |

**None** of these artifacts are **Accepted**, **in progress**, or **authorized for implementation** today.

---

## 3. Dependency gates

Experiment planning orchestration artifacts are **blocked** until **all** prerequisites below are **Accepted** (or explicitly satisfied where noted):

| Prerequisite | Status today |
|--------------|--------------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | ✅ Accepted — ladder not complete |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | ✅ Accepted — ladder not complete |
| [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) | ✅ Accepted |
| [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) | ✅ Accepted |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | ✅ Accepted |
| [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) | ✅ Accepted — protocol only; **D5-DES-STAT-* execution blocked** |
| **`DESIGN_COMBINATION_VALIDATION_MATRIX_001`** | ✅ Accepted — [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) |
| **`DESIGN_GUARDRAILS_001`** | ✅ Accepted — [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) |
| **`DESIGN_SUITABILITY_FRAMEWORK_001`** | ✅ Accepted — [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) |
| **`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001`** | ✅ Accepted — [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) |
| **`DESIGN_CONTRACT_SCHEMA_001`** | ✅ Accepted — [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) |
| **`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001`** | ✅ Accepted — [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md); **not implemented** |
| **`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001`** | Not started — **next** |
| [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) | ✅ Accepted |
| [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) | ✅ Accepted |
| Estimator/inference method-specific fixes | Partial — D5 Level B complete; enhancement lanes open |
| **Suitability framework v2** | Not started — requires design audit parity + combination matrix v2 |

**Rule:** No experiment-planning artifact may be **Accepted** or implemented until dependency gates clear. Parked status does **not** waive gates.

---

## 4. Future workflow

```text
MMM/MIP  →  GeoX/design  →  Suitability  →  Trust  →  LLM explain  →  Human decision
```

### A. MMM/MIP identifies

| Field | Description |
|-------|-------------|
| Decision gap | Business question requiring geo experiment evidence |
| Uncertainty source | Model disagreement, weak signal, untested channel, etc. |
| Channel / campaign / geo scope | Where the experiment applies |
| KPI | Primary outcome metric |
| Business constraint | Budget, inventory, operational limits |
| Required precision / MDE target | Minimum detectable effect or interval width target |

### B. GeoX / design layer generates

| Output | Description |
|--------|-------------|
| Candidate designs | Registry-backed design methods passing hard filters |
| Feasible geographies | Eligible units after constraints/trim/supergeo rules |
| Control/test assignment options | Assignment dict or documented pair structure |
| Power / MDE estimates | Simulation-based MDE with explicit contract ([`design/power.py`](../panel_exp/design/power.py) semantics) |
| Design diagnostics | Balance, donor pool, overlap, concurrency compatibility |

### C. Suitability layer evaluates

| Evaluation | Source |
|------------|--------|
| design × estimator × inference × geometry × readout | Future `DESIGN_COMBINATION_VALIDATION_MATRIX_001` + suitability v2 |
| Blocked combinations | Geometry bridge, guardrails, D5 blocked register |
| Bridge-required combinations | Explicit bridge artifact required before recommendation |
| Eligible candidates | Rows passing suitability + guardrails only |

### D. Trust layer emits

| Output | Meaning |
|--------|---------|
| pass / warn / block | Per candidate package |
| Blocked alternatives | With reason codes |
| Required caveats | Readout scale, geometry, population scope |
| Unsupported claims | Explicit negatives (pooled multi-cell, trim generalization, etc.) |

### E. LLM layer explains

| Explanation | Constraint |
|-------------|--------------|
| Why an experiment is recommended | Grounded in MMM/MIP decision gap — not fabricated certainty |
| Why a design is recommended | Cites suitability row + diagnostics |
| Why alternatives were blocked | Cites trust/guardrail/bridge registers |
| What human decision is needed next | Operational approval, scope change, bridge ADR, etc. |

**LLM does not override** statistical gates, trust blocks, or suitability classifications.

---

## 5. Future artifact responsibilities

### A. EXPERIMENT_RECOMMENDATION_CONTRACT_001 (parked)

Must define:

- Experiment objective  
- MMM uncertainty / decision gap reference  
- Target KPI  
- Geo / channel / campaign scope  
- Budget / time constraints  
- Required precision / MDE  
- Operational constraints  
- Recommended **design × estimator × inference** package (when eligible)  
- Blocked alternatives with reason codes  
- Trust status (pass / warn / block)  

### B. DESIGN_CANDIDATE_RANKING_POLICY_001 (parked)

Must define:

- Candidate generation rules  
- Hard filters (infeasible, blocked, bridge-missing, guardrail fail)  
- Scoring metrics (composite rank — not sole authority)  
- Power / MDE scoring  
- Balance scoring  
- Donor-pool scoring  
- Target-population drift penalty  
- Concurrency compatibility scoring  
- Geometry bridge status weighting  
- Estimator / inference compatibility scoring  
- Tie-breakers  
- Explanation requirements for ranked vs blocked candidates  

**Unsafe designs must not enter normal scoring** — hard-filter first.

### C. EXPERIMENT_PLANNING_DECISION_SURFACE_001 (parked)

Must define:

- Decision surface schema for experiment planning UI/API  
- Recommended candidate (single primary)  
- Alternatives evaluated  
- Blocked alternatives with codes  
- Risk flags  
- Trust summary  
- Human next action  

---

## 6. Guardrails

1. **MMM recommends evidence need** — not estimator/inference selection by itself.  
2. **LLM explains and orchestrates** — does **not** override statistical gates, trust blocks, or suitability rows.  
3. **Candidate designs must pass hard filters** before ranking.  
4. **Unsafe designs must not be scored** as normal candidates (block or quarantine).  
5. **No recommendation** authorizes TrustReport role, CalibrationSignal eligibility, MMM calibration attachment, or LLM autonomous decisioning without **explicit** eligibility artifacts.  
6. **No design × estimator × inference package** may be recommended unless **both** suitability gates **and** trust gates pass.  
7. **Pooled multi-cell, trim generalization, supergeo original-geo claims** remain blocked per geometry bridge until accepted bridges exist.  
8. **Parked artifacts** in §2 do not imply partial implementation authority.  

---

## 7. Current status

| Dimension | Status |
|-----------|--------|
| Experiment planning orchestration lane | **Deferred / future** |
| `EXPERIMENT_RECOMMENDATION_CONTRACT_001` | **Parked** — not started |
| `DESIGN_CANDIDATE_RANKING_POLICY_001` | **Parked** — not started |
| `EXPERIMENT_PLANNING_DECISION_SURFACE_001` | **Parked** — not started |
| MMM → GeoX recommendation wiring | **Blocked** |
| LLM experiment-planning orchestration | **Blocked** |
| TrustReport / CalibrationSignal / MMM calibration from recommendations | **Blocked** |

**Immediate program priority (unchanged):** design audit ladder — tier-1 emission **planned**; **experiment planning cannot consume tier-1 outputs until emission is implemented and validation tests pass.**

---

## 8. Relationship to current artifacts

| Artifact | Relationship |
|----------|--------------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Design candidates must come from audited, metadata-complete designs |
| [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) | **Future experiment planning must filter candidates through design guardrails** — BLOCK rows excluded first; LLM may explain but not override |
| [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) | **Future experiment planning may consume suitability categories only after guardrails + this framework** — ranked/filtered candidates; no LLM upgrade |
| [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) | **Experiment planning cannot consume design outputs until contract enforcement exists** (Phases 2–3 minimum); `artifact_status=contract_complete` required |
| [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) | **Schema-only artifacts are insufficient** — planning blocked until emission + guardrail enforcement |
| [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) | Combination statuses feed guardrail and suitability evaluation |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Suitability v2 feeds eligibility evaluation |
| [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) | Bridge-required combinations cannot be recommended without bridge |
| [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) | Readout targets must match recommended package |
| [`TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md`](TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md) | Future estimator families enter ranking only after own audit ladder |
| F-DECISION / TrustReport | Role assignment paused until foundation + suitability v2 |

---

## 9. Roadmap placement

**After** (not before):

1. Design audit ladder complete through `DESIGN_SUITABILITY_FRAMEWORK_001`  
2. Suitability framework v2  
3. Targeted estimator/inference enhancement lanes  
4. Trust role assignment framework (when authorized)  

**Then** (parked sequence):

1. `EXPERIMENT_RECOMMENDATION_CONTRACT_001`  
2. `DESIGN_CANDIDATE_RANKING_POLICY_001`  
3. `EXPERIMENT_PLANNING_DECISION_SURFACE_001`  

---

## 10. Non-goals

- No recommendation, ranking, or orchestration implementation  
- No MMM/MIP code integration  
- No LLM prompt/product wiring  
- No GeoX design generation changes  
- No estimator or inference selection automation  
- No TrustReport, CalibrationSignal, or MMM calibration authorization  
- No claim that experiment planning is ready for product use  

---

## 11. Roadmap and audit updates checked

| Document | Update |
|----------|--------|
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Deferred experiment-planning lane |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Parked orchestration track |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Future planning layer placement |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Artifact registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Planning gap cross-link |

**Optional architecture docs:** `ARCHITECTURE.md`, `PLATFORM_VISION.md`, `TRUST_ARCHITECTURE.md` — **not present** in repo; no update.

---

*EXPERIMENT-PLANNING-ORCHESTRATION-ROADMAP-001 v1.0.1 — DESIGN_OUTPUT_CONTRACT_001 prerequisite accepted; next program artifact = DESIGN_CODE_INVENTORY_001.*
