# Design Suitability Reassessment 001

**Document ID:** DESIGN-SUITABILITY-REASSESSMENT-001  
**Title:** Design Suitability Reassessment 001  
**Status:** **Accepted**  
**Scope:** Post-contract-emission and post-guardrail-runtime design suitability reassessment  
**Artifact type:** Reassessment / governance — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md)

**Inputs:** [`DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001.md`](DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001.md) · [`DESIGN_CONTRACT_GOLDEN_FIXTURES_001.md`](DESIGN_CONTRACT_GOLDEN_FIXTURES_001.md) · [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) · [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) · [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md)

**Guardrails:** No algorithm implementation · no D5-DES-STAT execution · no estimator/inference promotion · no product authorization · no suitability promotion

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Suitability Reassessment 001 |
| Status | **Accepted** |
| Artifact type | Reassessment / governance |
| Scope | Post-contract-emission and post-guardrail-runtime reassessment |

Seventeenth design audit artifact. Reassesses design suitability after tier-1 contract emission, validator implementation, golden fixtures, and runtime guardrail evaluation — **without collapsing metadata validity into statistical or downstream suitability**.

---

## 2. Purpose

This artifact determines **what changed** after:

- tier-1 `design_contract` runtime emission (`geo_runner` → builder → validator)  
- standalone contract validation (`design_contract_validator_001.py`)  
- golden fixture stabilization (9 JSON fixtures, 39 tests)  
- runtime guardrail evaluation (`design_guardrail_runtime_001.py`, 24 tests)  

It updates suitability **classification vocabulary** and **layered decision logic** so orchestration can distinguish metadata completeness from statistical evidence and downstream authorization.

**Reassessment ≠ promotion.**

---

## 3. Why this reassessment exists

| Prior state | Current state |
|-------------|---------------|
| [`DESIGN_SUITABILITY_FRAMEWORK_001`](DESIGN_SUITABILITY_FRAMEWORK_001.md) authored before runtime contracts | Framework categories now map to **measurable** contract/guardrail outputs |
| All designs effectively `contract_blocked` (no emitted contract) | Tier-1 geo-run paths **emit** conservative contracts + `contract_validation` summaries |
| Guardrails were policy-only | Runtime guardrail evaluator returns PASS/WARN/BLOCK on emitted metadata |
| Metadata completeness unmeasured | Validator + fixtures prove mechanical contract validity for representative tier-1 shapes |
| Statistical validity unchanged | Protocol defined; **0** design families executed under `D5-DES-STAT-*` |
| Downstream authorization blocked | **Still blocked** — `suitability_may_proceed=False`, `downstream_may_proceed=False` |

Prior suitability assumed universal `contract_blocked`. Reassessment shows **metadata-layer improvement** for tier-1 paths while **statistical and downstream suitability remain blocked**.

---

## 4. Inputs

| Input | Source | Role in reassessment |
|-------|--------|----------------------|
| Emitted tier-1 `design_contract` | `geo_runner` · `design_contract_builder_001.py` | Contract shape presence |
| Validator results | `design_contract_validator_001.py` | Mechanical contract validity |
| Golden fixture results | `design_contract_golden_001/` · 39 fixture tests | Stabilized tier-1 shape regression |
| Guardrail runtime results | `design_guardrail_runtime_001.py` · 24 integration tests | Metadata PASS/WARN/BLOCK |
| Design implementation findings | [`DESIGN_IMPLEMENTATION_VALIDATION_001`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | Adapter/ambiguous/helper blockers |
| Design statistical validation protocol | [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Execution requirements (not outcomes) |
| Design combination matrix | [`DESIGN_COMBINATION_VALIDATION_MATRIX_001`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) | Design × estimator × inference status |
| Geometry / readout governance | [`GEOMETRY_BRIDGE_REQUIREMENTS_001`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`INFERENCE_READOUT_SEMANTICS_001`](INFERENCE_READOUT_SEMANTICS_001.md) | Bridge and readout gates |

---

## 5. Non-goals

- No new design algorithm implementation  
- No `D5-DES-STAT-*` harness execution in this artifact  
- No estimator/inference promotion  
- No adapter implementation (QuickBlock, MatchedPair, Trim, Supergeo)  
- No geometry bridge implementation  
- No TrustReport / CalibrationSignal / MMM / LLM authorization  
- No collapse of layered statuses into a single “suitable” label  
- No use of `production_suitable` as a category  

---

## 6. Reassessment taxonomy

Categories describe **layer-specific** status. A design may hold multiple labels simultaneously across layers.

| Category | Layer | Meaning |
|----------|-------|---------|
| `metadata_valid_statistically_unvalidated` | Contract + guardrail | Mechanical contract valid; stat protocol not executed |
| `metadata_valid_guardrail_warn` | Guardrail | Runtime guardrail `WARN` — readable metadata, not downstream-safe |
| `contract_blocked` | Contract | Validator `contract_blocked` / incomplete / unknown |
| `adapter_required` | Implementation | Non-standard output; adapter before advancement |
| `bridge_required` | Geometry | Population/geometry bridge before scoped claims |
| `implementation_ambiguous` | Implementation | Population/semantics unclear in code |
| `planning_only` | Use scope | MDE/power/planning helpers only |
| `statistical_validation_required` | Statistical | `D5-DES-STAT-*` not executed for family scope |
| `combination_validation_required` | Combination | Matrix row not validated for design × estimator × inference |
| `downstream_blocked` | Authorization | No TrustReport/CalibrationSignal/MMM/LLM/production role |
| `eligible_for_next_validation_stage` | Pipeline | May enter `D5-DES-STAT-TIER1-001` candidate queue (metadata gates met) |
| `not_reassessed` | — | Outside tier-1 emission wave; prior framework row unchanged |

**Forbidden label:** `production_suitable` — not used in this artifact.

---

## 7. Layered decision model

Ordered evaluation logic (each layer is independent):

1. **Contract emission** — Does runtime output emit a `design_contract` block?  
2. **Validator acceptance** — Does `validate_design_contract` return `contract_valid` or `contract_valid_with_warnings`?  
3. **Runtime guardrail** — Does guardrail return `BLOCK` or `WARN`? (`suitability_may_proceed` / `downstream_may_proceed` remain `False`)  
4. **Design statistical validation** — Has `D5-DES-STAT-*` been executed and passed for this design family?  
5. **Geometry support** — Is geometry direct, or bridge-required (trim/supergeo/pooled multi-cell)?  
6. **Adapter requirement** — Does design require adapter artifact (QuickBlock, MatchedPair, Trim, Supergeo)?  
7. **Combination validation** — Is design × estimator × inference × geometry × readout row validated in matrix?  
8. **Downstream authorization** — Has separate product-role authorization occurred? (**Currently: never**)

A design may pass layers 1–3 while failing 4–8. **No layer implies the next.**

---

## 8. What changed since prior suitability framework

| Change | Evidence |
|--------|----------|
| Tier-1 contract emission exists | `geo_runner` calls `build_and_validate_tier1_contract` |
| Contract validator exists | `design_contract_validator_001.py` + 26 tests |
| Golden fixtures exist | 9 JSON fixtures; DES-002/003/004/006 positive shapes |
| Guardrail evaluator exists | `design_guardrail_runtime_001.py` + 24 tests |
| Metadata validity measurable | `contract_validation.status` + guardrail `WARN` on positive fixtures |
| Tier-1 designs can exit universal `contract_blocked` **at metadata layer only** | Reclassified to `metadata_valid_statistically_unvalidated` when emitted correctly |
| Statistical validation | **Unchanged** — protocol only |
| Downstream authorization | **Unchanged** — blocked |

---

## 9. What did not change

- No `D5-DES-STAT-*` family execution completed solely from the contract-infra lane  
- No adapter work for QuickBlock / MatchedPair / Trim / Supergeo  
- No thinning (`DES-005`) semantic resolution  
- No geometry bridge completion for trim / supergeo / pooled multi-cell causal claims  
- No estimator/inference compatibility promotion from contract metadata  
- No TrustReport / CalibrationSignal / MMM / LLM authorization  
- **`contract_complete_allowed=False`** on all emitted contracts  
- **0/31 contract-complete** for downstream authorization purposes  

---

## 10. Tier-1 reassessment table

| Design | Contract emission | Validator | Guardrail | Statistical validation | Current category |
|--------|-------------------|-----------|-----------|------------------------|------------------|
| **DES-001** `greedy_match_markets` | ✅ tier-1 path via `geo_runner` | Expected `contract_valid` when universal fields populated | Expected `WARN` + `D-GUARDRAIL-REQUIRES-STATISTICAL-VALIDATION` | ✅ tier-1 + ✅ feasibility fix (`control_reservation`) | `metadata_valid_feasibility_improved_statistically_unvalidated` · `eligible_for_next_validation_stage` |
| **DES-002** `CompleteRandomization` | ✅ emitted | ✅ `contract_valid` (golden fixture) | `WARN` | ❌ not executed | `metadata_valid_guardrail_warn` · `statistical_validation_required` |
| **DES-003** `BalancedRandomization` | ✅ emitted | ✅ `contract_valid` (golden fixture) | `WARN` | ❌ not executed | `metadata_valid_guardrail_warn` · `statistical_validation_required` |
| **DES-004** `StratifiedRandomization` | ✅ emitted | ✅ `contract_valid` **when stratum metadata present** | `WARN` or `BLOCK` | ✅ tier-1 + ✅ stratified fix (`adaptive_strata`) | `metadata_valid_feasibility_improved_statistically_unvalidated` |
| **DES-006** `Rerandomization` | ✅ emitted (wrapper) | ✅ `contract_valid` **when wrapper/base identity preserved** (golden fixture) | `WARN` | ❌ not executed | `metadata_valid_guardrail_warn` · `statistical_validation_required` |
| **DES-011** `multi_test_groups` | ✅ emitted | ✅ metadata when `last_multicell_metadata` present | `BLOCK` | ✅ **`D5-DES-STAT-MULTICELL-001`** | `metadata_valid_per_cell_only_pooled_blocked` · pooled claims blocked |

**Conservative interpretation:** DES-002/003/004 (with strata)/006 may be mechanically contract-valid with guardrail `WARN`. None are statistically validated or downstream-authorized.

---

## 11. Non-tier-1 reassessment table

| Design / helper | Contract emission | Reassessment category | Next action |
|-----------------|-------------------|----------------------|-------------|
| **DES-005** `ThinningDesign` | Not tier-1 wave | `implementation_ambiguous` | Thinning semantic clarification ADR |
| **QuickBlock** | No tier-1 contract | `adapter_required` | `D5-DES-STAT-BLOCK-PAIR-001` adapter lane |
| **MatchedPair** | No tier-1 contract | `adapter_required` | Block/pair adapter lane |
| **TrimmedMatch** | No tier-1 contract | `adapter_required` · `bridge_required` | Trim adapter + `GEOMETRY_BRIDGE` validation |
| **Supergeo** | No tier-1 contract | `adapter_required` · `bridge_required` | Supergeo adapter + population bridge |
| **Power / MDE helpers** | Helper output | `planning_only` · `helper_not_suitable` | Planning rank only; not design suitability anchor |
| **Validation helpers** (`validate_assignment_dict`, etc.) | Internal | `helper_not_suitable` | Not reassessed as design methods |
| **DES-007–DES-031** (remaining inventory) | Mostly not tier-1 | `not_reassessed` or prior framework row | Per-family audit as needed |

---

## 12. Contract-valid versus suitable

**Strong rules (binding for orchestration):**

```
contract_valid != statistically_valid
contract_valid != combination_validated
contract_valid != downstream_authorized
```

Mechanical contract validity means the emitted metadata envelope is **readable, validator-accepted, and guardrail-evaluable**. It does **not** mean:

- assignment quality is proven under simulation  
- design × estimator × inference path is safe  
- TrustReport / CalibrationSignal / MMM / LLM may consume the design  
- production experiment recommendation is permitted  

---

## 13. Guardrail WARN interpretation

| Statement | True? |
|-----------|-------|
| `WARN` means metadata is readable and mechanically coherent | ✅ |
| `WARN` means statistically suitable | ❌ |
| `WARN` permits downstream use | ❌ |
| `suitability_may_proceed=False` is authoritative | ✅ |
| `downstream_may_proceed=False` is authoritative | ✅ |
| Positive fixtures include `D-GUARDRAIL-REQUIRES-STATISTICAL-VALIDATION` | ✅ |

Guardrail `WARN` on tier-1 positive fixtures is a **metadata completeness signal**, not a suitability promotion. Runtime guardrail behavior is unchanged: both proceed flags remain `False`.

---

## 14. Statistical validation status

| Item | Status |
|------|--------|
| Design statistical protocol | ✅ [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) **Accepted** |
| `statistical_validation_status` on emitted contracts | `protocol_defined_not_executed` |
| `D5-DES-STAT-*` harnesses | Named in protocol; **not executed** for full tier-1 family scope |
| Promotion from protocol definition | **Forbidden** |
| Designs statistically validated (executed evidence) | **0** families |

D5-DES-TRIM / D5-DES-SUPERGEO / D5-POW-001e provide **characterization evidence** for specific paths — they do **not** substitute for tier-1 statistical validation battery execution.

---

## 15. Design × estimator × inference status

- Combination matrix remains **advisory and governed** — [`DESIGN_COMBINATION_VALIDATION_MATRIX_001`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md)  
- Contract/guardrail metadata success **does not upgrade** blocked or `restricted_requires_*` matrix rows  
- Final structural suitability requires **validated design + estimator + inference + geometry + readout** combination  
- [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) remains a **separate layer** — not overridden by design contract metadata  

---

## 16. Geometry and concurrency reassessment

| Geometry / mode | Tier-1 status | Reassessment |
|-----------------|---------------|--------------|
| Single-cell `unit_panel_single_cell` | ✅ tier-1 default (DES-001–004, DES-006) | Metadata-valid path when contract emitted |
| Multi-cell `multi_cell_per_cell` | Partial — DES-011 emission conservative | `contract_blocked` until shared-control policy + cell IDs complete |
| Pooled multi-cell `pooled_multi_cell` | Blocked in guardrail runtime | `bridge_required` · no pooled causal claims |
| Trim / `trimmed_geometry` | Not tier-1 | `bridge_required` · adapter lane |
| Supergeo | Not tier-1 | `bridge_required` · adapter lane |
| Concurrency | Emitted `concurrent_multi_experiment_compatibility` | Restricted/blocked paths unchanged; metadata only |

---

## 17. Current allowed uses

| Use | Allowed? |
|-----|----------|
| Metadata validation (validator + fixtures) | ✅ |
| Guardrail evaluation (runtime module) | ✅ |
| Research / internal planning under non-production labels | ✅ |
| `D5-DES-STAT-TIER1-001` candidate selection (tier-1 metadata-valid families) | ✅ |
| Explaining blocked status to users / docs | ✅ |
| Internal design comparison (no production claims) | ✅ |

---

## 18. Current blocked uses

| Use | Blocked? |
|-----|----------|
| Production experiment recommendation | ✅ BLOCKED |
| TrustReport role assignment | ✅ BLOCKED |
| CalibrationSignal eligibility | ✅ BLOCKED |
| MMM automated experiment recommendation | ✅ BLOCKED |
| LLM override of guardrails | ✅ BLOCKED |
| Pooled multi-cell causal claims | ✅ BLOCKED |
| Automatic suitability promotion from metadata | ✅ BLOCKED |

---

## 19. Reassessment result by design group

| Design group | Metadata status | Guardrail | Statistical validation | Bridge/adapter | Next action | Downstream |
|--------------|-----------------|-----------|------------------------|----------------|-------------|------------|
| Tier-1 single-cell (DES-001–003, DES-006) | Valid when emitted | WARN | Required | None | `D5-DES-STAT-TIER1-001` | Blocked |
| Tier-1 stratified (DES-004) | Valid with strata | WARN / BLOCK | Required | None | Stat validation + strata regression | Blocked |
| Tier-1 multi-cell (DES-011) | ✅ D5-DES-STAT-MULTICELL-001 | BLOCK | Required | Per-cell only | Pooled blocked; downstream still blocked | Blocked |
| Thinning (DES-005) | Not tier-1 | N/A | Required | Ambiguous | Semantic ADR | Blocked |
| Block/pair adapters | No contract | N/A | Required | Adapter | Adapter lane | Blocked |
| Trim/supergeo | No tier-1 contract | N/A | Required | Adapter + bridge | Bridge validation | Blocked |
| Power/MDE helpers | Helper-only | N/A | N/A | N/A | Planning only | Blocked |
| Remaining DES rows | Not reassessed | Prior policy | Protocol-defined | Per inventory | Family-specific audit | Blocked |

---

## 20. Promotion gates

A design may move toward **positive structural suitability** only after **all** of:

1. Emitted contract passes validator (`contract_valid` or `contract_valid_with_warnings` without BLOCK guardrail)  
2. Runtime guardrail has no `BLOCK` for requested scope  
3. Required `D5-DES-STAT-*` suite executed and passed for design family  
4. Geometry/concurrency issues resolved (bridges where required)  
5. Design × estimator × inference combination validated in matrix  
6. Downstream role explicitly assigned by separate product charter  

**Current state:** No design has passed gates 3–6. Gate 1–2 partially met for tier-1 single-cell metadata only.

---

## 21. Current counts

| Count | Value | Notes |
|-------|-------|-------|
| Contract-emitting tier-1 paths | **5 families** | DES-001–004, DES-006 (+ constrained DES-011 emission) |
| Mechanically valid fixture-backed paths | **4 positive fixtures** | DES-002, DES-003, DES-004, DES-006 (DES-001 path exists; no golden file yet) |
| Contract-complete for downstream authorization | **0 / 31** | `contract_complete_allowed=False` always |
| Statistically validated design families (executed `D5-DES-STAT-*`) | **5 tier-1 families characterized** | [`D5_DES_STAT_TIER1_001`](track_d/D5_DES_STAT_TIER1_001_REPORT.md); not production-suitable |
| Downstream-authorized designs | **0** | |
| TrustReport-eligible designs | **0** | |
| CalibrationSignal-eligible designs | **0** | |
| MMM-ready designs | **0** | |
| LLM-authorized designs | **0** | |

---

## 22. Reassessment verdict

**Verdict:** `design_metadata_suitability_improved_statistical_and_downstream_suitability_still_blocked`

Metadata-layer suitability **improved** for tier-1 geo-run paths: contracts emit, validate, fixture-regress, and guardrail-evaluate. Statistical suitability and downstream authorization **remain blocked**. No design receives a production-suitable label.

---

## 23. Recommended next work

**Default next artifact:** **`D5-DES-STAT-TIER1-001`**

The design contract-infrastructure lane has reached a useful stopping point. Next value comes from **executed statistical validation**, not additional metadata plumbing.

**Candidate scope for `D5-DES-STAT-TIER1-001`:**

- DES-002 `CompleteRandomization`  
- DES-003 `BalancedRandomization`  
- DES-004 `StratifiedRandomization` (with strata fixtures)  
- DES-006 `Rerandomization` (wrapper identity)  
- DES-001 `greedy_match_markets` (after emission regression fixture added if needed)  

**Follow-on artifacts (not default):**

- ✅ `D5-DES-STAT-MULTICELL-001` — executed; per-cell metadata + pooled blocking characterized  
- Thinning semantic clarification (DES-005)  
- Block/pair adapter lane (QuickBlock, MatchedPair)  
- Trim/supergeo bridge validation  

Do **not** default to another generic infrastructure artifact unless a concrete prerequisite blocker is discovered.

---

## 24. Relationship to algorithm-improvement work

- The contract / validator / fixture / guardrail infrastructure lane is **paused at a useful milestone**  
- Next value comes from **executed design statistical validation** and **algorithm/design improvement** under observed behavior  
- Metadata plumbing alone **cannot** improve assignment quality, balance, or causal-readout safety  
- Reassessment explicitly returns the program to the **evidence-execution lane**  

---

## 25. Governance gates

| Gate | Status |
|------|--------|
| No design promoted | ✅ |
| No downstream eligibility granted | ✅ |
| No TrustReport / CalibrationSignal / MMM / LLM authorization | ✅ |
| No estimator/inference suitability override from contract metadata | ✅ |
| Layered statuses preserved | ✅ |

---

## 26. Roadmap

| Milestone | Status |
|-----------|--------|
| Contract schema | ✅ |
| Validator | ✅ |
| Tier-1 emission | ✅ |
| Golden fixtures | ✅ |
| Guardrail runtime | ✅ |
| **Suitability reassessment** | ✅ **This artifact** |
| **Next default** | **`D5-DES-STAT-MULTICELL-001`** (after stratified fix ✅) |

---

## 27. Completion checklist

| Item | Status |
|------|--------|
| Prerequisites inspected | ✅ |
| Tier-1 reassessed | ✅ §10 |
| Non-tier-1 reassessed | ✅ §11 |
| Contract vs statistical suitability separated | ✅ §12 |
| Guardrail semantics preserved | ✅ §13 |
| Current counts documented | ✅ §21 |
| Roadmap returns to executed validation | ✅ §23 |
| No code changed | ✅ |
| Existing tests pass | ✅ (completion report) |

---

## 28. Current status and verdict

**Verdict:** `design_metadata_suitability_improved_statistical_and_downstream_suitability_still_blocked`

Tier-1 metadata suitability improved through measurable contract emission, validation, fixtures, and guardrail evaluation. Statistical validation and downstream authorization remain blocked for all designs. Next default artifact: **`D5-DES-STAT-TIER1-001`**.

---

*DESIGN-SUITABILITY-REASSESSMENT-001 v1.0.0 — Accepted; metadata suitability improved; statistical and downstream suitability still blocked; next = D5-DES-STAT-TIER1-001.*
