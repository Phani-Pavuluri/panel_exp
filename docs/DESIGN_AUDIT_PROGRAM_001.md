# Design Audit Program 001

**Document ID:** DESIGN-AUDIT-PROGRAM-001  
**Title:** Design Audit Program 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` design methods and design-output governance  
**Artifact type:** Documentation / governance — **no code changes**  
**Date:** 2026-06-09  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) · [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md)

**Companions:** [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) · [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md)

**Guardrails:** No design implementation · no promotion · no suitability claim · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Audit Program 001 |
| Status | **Accepted** |
| Scope | GeoX / `panel_exp` design methods and design-output governance |
| Artifact type | Documentation / governance |

This artifact establishes the **design-side audit program** with the same layered rigor applied to estimator and inference families. It does **not** authorize any design for production use.

---

## 2. Purpose

Design methods define **assignment geometry**, treated/control structure, donor eligibility, target population, multi-cell layout, and downstream estimator/inference compatibility. Without a governed design audit ladder, estimator/inference characterization (D5 Level B, readout semantics, geometry bridge) risks being read as end-to-end platform proof.

This program requires:

- Repository-complete design discovery (not a fixed name list)  
- Literature alignment per design family  
- Implementation validation against declared semantics  
- Statistical validation worlds for design quality  
- Design × geometry × estimator × inference × readout combination matrix  
- Design guardrails and suitability placement  

**Estimator/inference audit parity is incomplete until the design audit ladder completes.**

---

## 3. Why this artifact exists

| Prior work | Gap |
|------------|-----|
| D5 Level B (SCM, AugSynth, TBR, DID, MCELL, TBRRidge) | Uses **reference designs** (mostly `greedy_match_markets`) — does not audit all design families |
| [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) | Defines geometry transitions — **does not replace** design method audit |
| [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) | Readout targets — assumes assignment metadata exists |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Policy-only v1 — **incomplete without design audit parity** |
| D5-POW / D5-DES artifacts | Partial design characterization (001e null FPR, supergeo, trim) — not full design ladder |
| [`METHOD_CODE_INVENTORY_001.md`](METHOD_CODE_INVENTORY_001.md) | Mixed design/estimator inventory — design-specific ladder needed |

Design outputs are the **upstream contract** for geometry_id, pooling policy, concurrent multi-experiment compatibility, and bridge requirements. They must be audited independently.

---

## 4. Scope

Includes **all repository-discovered**:

- Design classes and registry entries  
- Assignment generators and randomizers  
- Matching, blocking, stratification, thinning, supergeo, trim logic  
- Multi-cell / shared-control assignment configurations  
- Donor-pool and eligibility helpers  
- Design validation gates and balance diagnostics  
- Power/MDE design helpers and orchestration (`GeoExperimentDesign`, `PowerAnalysis`)  
- Design output structures (assignment dict, pair DataFrames, numpy vectors, evidence payloads)  

**Not limited** to known names (GreedyMatch, QuickBlock, Thinning, SuperGeo, TrimmedMatch, etc.).

---

## 5. Non-goals

- No design implementation changes  
- No estimator or inference changes  
- No new simulations or D5 archive regeneration  
- No design promotion or suitability claim  
- No TrustReport role, CalibrationSignal eligibility, MMM, or LLM authorization  
- No claim that any design is production-ready or statistically validated  

---

## 6. Repository discovery requirement

All design methods **must** be discovered from:

- `panel_exp/design/` modules  
- `get_design_registry()` / `register_builtin_designs`  
- Public exports (`panel_exp/__init__.py`, `panel_exp/design/__init__.py`)  
- Tests (`tests/test_design_registry.py`, `tests/track_d/test_design_inventory_001.py`, D5-POW/D5-DES harnesses)  
- Validation inventories (`track_d_design_inventory_001.py`, `METHOD_CODE_INVENTORY_001`)  
- Docs and examples referencing design entrypoints  

**Discovery searches performed for this artifact:**

```bash
grep -R "class .*Design" panel_exp tests docs
grep -R "QuickBlock\|Thinning\|SuperGeo\|Trimmed\|Greedy\|Match\|Block\|Stratified\|Random" panel_exp tests docs
grep -R "design" panel_exp/design panel_exp/validation tests docs
find panel_exp -iname "*design*" -o -iname "*match*" -o -iname "*block*"
```

### Discovery register (2026-06-09)

| Discovered name | File path | Class / function / module | Design category | Audit status | Suitability status | Notes |
|-----------------|-----------|---------------------------|-----------------|----------------|-------------------|-------|
| **greedy_match_markets** | `panel_exp/design/assign.py` | `greedy_match_markets` | matching_design | not_evaluated (partial D5-POW-001e) | contract_required | Geo-run default base; pre-period matching (INV-D1-001) |
| **CompleteRandomization** | `panel_exp/design/assign.py` | `CompleteRandomization` | standard_assignment_design | not_evaluated (partial 001e) | contract_required | Bernoulli arms + constraints |
| **BalancedRandomization** | `panel_exp/design/assign.py` | `BalancedRandomization` | standard_assignment_design | not_evaluated (partial 001e) | contract_required | KPI volume-share balancing |
| **StratifiedRandomization** | `panel_exp/design/assign.py` | `StratifiedRandomization` | stratified_assignment_design | not_evaluated (partial 001e) | contract_required | Percentile strata + balance |
| **ThinningDesign** | `panel_exp/design/assign.py` | `ThinningDesign` | thinning_design | not_evaluated (partial 001e) | contract_required | Kernel thinning on wide panel |
| **Rerandomization** | `panel_exp/design/assign.py` | `Rerandomization` | blocking_assignment_design (wrapper) | not_evaluated (partial 001e) | contract_required | Wraps geo tier-1 bases; imbalance minimization |
| **QuickBlock** | `panel_exp/design/quickblock.py` | `QuickBlock` | blocking_assignment_design | not_evaluated | not_evaluated | Registered; not geo-run; legacy `assign_all` API |
| **MatchedPair** | `panel_exp/design/matched_pair.py` | `MatchedPair` | matching_design | not_evaluated | not_evaluated | Graph matching; numpy vector output |
| **TrimmedMatchDesign** | `panel_exp/design/trimmed_match.py` | `TrimmedMatchDesign` | trimmed_population_design | not_evaluated (D5-DES-TRIM-001 partial) | bridge_required | Tp/Te pairs; changes target population |
| **SupergeoModel** | `panel_exp/design/supergeos.py` | `SupergeoModel` | supergeo_design | not_evaluated (D5-DES-SUPERGEO-001 partial) | bridge_required | MILP supergeo pairs; not flat assignment dict |
| **multi_test_groups** | config (`n_test_grps > 1`) | parameter on geo designs | multi_cell_assignment_design | not_evaluated (partial D5-MCELL) | restricted | Shared control; per-cell only at readout |
| **GeoExperimentDesign** | `panel_exp/design/geo_experiment_design.py` | `GeoExperimentDesign` | panel_construction_helper | not_evaluated | contract_required | Orchestrator: assign + validate + power + evidence |
| **run_geo_experiment_design** | `panel_exp/design/geo_runner.py` | function | panel_construction_helper | not_evaluated | contract_required | Registry dispatch pipeline |
| **PowerAnalysis** | `panel_exp/design/power.py` | `PowerAnalysis` | power_mde_design_helper | not_evaluated (D5-POW partial) | contract_required | Simulation MDE; often 2-row agg panel |
| **prepare_constraint_context** | `panel_exp/design/constraints.py` | function | donor_pool_eligibility_helper | not_evaluated | contract_required | Whitelist/blacklist pinning and exclusion |
| **validate_assignment_dict** | `panel_exp/design/constraints.py` | function | donor_pool_eligibility_helper | not_evaluated | contract_required | Post-assign constraint validation |
| **validate_design** | `panel_exp/design/validation.py` | function | panel_construction_helper | not_evaluated | contract_required | PASS/WARN/FAIL design validation gate |
| **slice_wide_to_time_period** | `panel_exp/design/period_slice.py` | function | panel_construction_helper | not_evaluated | contract_required | INV-D1-001 pre-period slice helper |
| **imbalance** | `panel_exp/design/design_metrics.py` | function | panel_construction_helper | not_evaluated | contract_required | Balance metrics for rerandomization |
| **make_generator** | `panel_exp/design/rng.py` | function | panel_construction_helper | not_evaluated | contract_required | Reproducible RNG contract |
| **DesignRegistry** | `panel_exp/design/registry.py` | class | panel_construction_helper | not_evaluated | contract_required | Registration + geo-run allowlist |
| **create_design_comparison_dashboard** | `panel_exp/utils/test_designs_evaluation.py` | function | power_mde_design_helper | not_evaluated | not_evaluated | MLflow design comparison utility |

**Count:** 10 registered design implementations + 1 multi-cell configuration + 11 helpers/orchestration surfaces (22 rows).

Future `DESIGN_CODE_INVENTORY_001` must re-run discovery and supersede this table.

**Superseded by:** [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) ✅ Accepted (31 rows).

---

## 7. Initial design taxonomy

| Category ID | Description |
|-------------|-------------|
| `standard_assignment_design` | Random assignment to control/test arms (complete, balanced) |
| `matching_design` | Pre-period or covariate-driven matching (greedy, matched pair) |
| `blocking_assignment_design` | Block construction + within-block assignment (QuickBlock, rerandomization wrapper) |
| `stratified_assignment_design` | Strata-defined assignment (StratifiedRandomization) |
| `thinning_design` | Kernel / distance thinning of assignment space |
| `trimmed_population_design` | Exclusion/trim changes effective sample and target population |
| `supergeo_design` | Constructs new aggregate units from base geos |
| `multi_cell_assignment_design` | Multiple test cells with shared or cell-specific controls |
| `shared_control_design` | Explicit shared-control reuse policy across cells |
| `power_mde_design_helper` | Simulation-based MDE / power ranking (not classical analytic power) |
| `donor_pool_eligibility_helper` | Whitelist/blacklist, pinning, exclusion before assignment |
| `panel_construction_helper` | Orchestration, slicing, validation, registry, evidence emission |
| `unknown_or_not_evaluated` | Discovered but category or semantics not yet classified |

---

## 8. Design-side audit ladder

Full sequence — later steps blocked until earlier artifacts are **Accepted**:

### A. DESIGN_CODE_INVENTORY_001 ✅

**Status:** **Accepted** — [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md)

Enumerate all design methods and helpers from repo inspection; map to [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md). Verdict: `design_code_inventory_complete_contract_gaps_identified`.

### B. DESIGN_LITERATURE_ALIGNMENT_001 ✅

**Status:** **Accepted** — [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md)

Per design family, compare to published or standard design logic (matched-market, blocking, rerandomization, trim, supergeo, multi-cell, power/MDE). Verdict: `design_literature_alignment_complete_with_open_conceptual_gaps`.

### C. DESIGN_IMPLEMENTATION_VALIDATION_001 ✅

**Status:** **Accepted** — [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md)

Compare implementation behavior to intended semantics and required metadata emission. Verdict: `design_implementation_validation_complete_contract_blockers_identified`. **0 contract-complete designs.**

### D. DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001 ✅

**Status:** **Accepted** — [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md)

Define simulation worlds, diagnostics, metrics, and pass/warn/block rules for design quality (§12). Verdict: `design_statistical_validation_protocol_defined_not_executed`. **0 designs statistically validated.**

### E. DESIGN_COMBINATION_VALIDATION_MATRIX_001 ✅

**Status:** **Accepted** — [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md)

Allowed / blocked / deferred / bridge-required combinations across design × geometry × estimator × inference × readout × concurrent multi-experiment mode. Verdict: `design_combination_matrix_defined_no_combinations_promoted`. **0 combinations promoted.**

### F. DESIGN_GUARDRAILS_001 ✅

**Status:** **Accepted** — [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md)

Converts contract blockers, implementation gaps, statistical protocol eligibility, and combination matrix statuses into PASS/WARN/BLOCK policy. Verdict: `design_guardrails_defined_no_downstream_pass`. **0 downstream PASS.**

### G. DESIGN_SUITABILITY_FRAMEWORK_001 ✅

**Status:** **Accepted** — [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md)

Classify each design into suitability categories (`contract_blocked`, `stat_validation_required`, `adapter_required`, `bridge_required`, `planning_only`, `blocked`, …). Consumes guardrails + combination matrix. Verdict: `design_suitability_framework_defined_no_downstream_suitable_designs`. **0 downstream suitable designs.**

### H. DESIGN_CONTRACT_ENFORCEMENT_PLAN_001 ✅

**Status:** **Accepted** — [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md)

Defines implementation plan for emitting, validating, and enforcing required contract fields on `DesignEvidence`, `geo_runner`, and related paths. Verdict: `design_contract_enforcement_plan_defined_not_implemented`. **Phase 0 only — no code changes.**

### I. DESIGN_CONTRACT_SCHEMA_001 ✅

**Status:** **Accepted** — [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md)

Machine-readable schema specification for `design_contract` nested block. Phase 1 of enforcement plan. Verdict: `design_contract_schema_defined_not_implemented`. **Not implemented in code.**

### J. DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001 ✅

**Status:** **Accepted** — [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md)

Phase 2 tier-1 geo-run emission plan for DES-001–004, DES-006, constrained DES-011. Verdict: `design_tier1_contract_emission_plan_defined_not_implemented`. **Planned only — not implemented in code; 0/31 contract-complete.**

### K. Method-specific design audits (as needed)

Examples: `D5-DES-SUPERGEO-001` follow-on, `D5-DES-TRIM-001` hardening, QuickBlock geo integration ADR.

---

## 9. Conceptual checks required by design family

For **every** discovered design, future audits must document:

| Check | Question |
|-------|----------|
| Unit of randomization | Market, geo, user, block, pair, supergeo? |
| Eligible unit universe | Full panel vs restricted vs trimmed? |
| Treated/control assignment | Exclusive arms? Pair structure? |
| Cell structure | Single vs multi-cell; cell IDs |
| Shared-control policy | Reuse across cells; load limits |
| Donor-pool definition | Who is eligible as control/donor post-design |
| Balance objective | Metric, period, threshold |
| Power/MDE target | Simulation grid, estimator dependency |
| Exclusion/trim rule | Global vs cell-specific |
| Target population before/after | Population shift from trim/supergeo |
| Concurrency support | `concurrent_multi_experiment_compatibility` |
| Estimator compatibility | Which geometries and estimators allowed |
| Inference compatibility | Block-aware? Cluster-robust required? |
| Failure modes | Infeasible constraints, empty donor pool, overlap collapse |
| Forbidden claims | Full-population after trim; original-geo after supergeo |

---

## 10. Literature alignment requirements

For each design family, `DESIGN_LITERATURE_ALIGNMENT_001` must answer:

1. What design problem does it solve?  
2. What assumptions does it introduce (SUTVA, interference, overlap)?  
3. What objective does it optimize?  
4. What diagnostics are standard (balance, SRM, overlap)?  
5. What downstream inference adjustments are required?  
6. One test/control pair or multiple simultaneous cells?  
7. Does it preserve the original target population?  
8. Does it preserve original units or create new units?  
9. Known failure modes from literature and industry practice?  

---

## 11. Implementation validation requirements

For every implementation, `DESIGN_IMPLEMENTATION_VALIDATION_001` must verify:

| Requirement | Emission / behavior |
|-------------|---------------------|
| Reproducibility | `random_seed` / `random_state` honored |
| Deterministic behavior | Where documented (rerandomization seeds, MILP seed) |
| Unit identity preservation | Stable unit IDs through assignment |
| Cell identity preservation | `test_0..test_{K-1}` exclusivity |
| Treated/control exclusivity | No unit in multiple arms |
| No duplicate assignments | Within arm lists |
| Missing eligible units | Only via explicit exclusion |
| Donor eligibility emitted | Control pool documented |
| Block IDs emitted | QuickBlock, stratified blocks |
| Excluded/trimmed units emitted | With reason |
| Supergeo source mapping emitted | Base geo → supergeo ID |
| Balance diagnostics emitted | Pre-period metrics |
| Power/MDE metadata emitted | Simulation contract fields |
| Target population emitted | Pre/post design |
| geometry_id emitted | Canonical from geometry bridge |
| Concurrency metadata emitted | §13 classification |
| Downstream compatibility hints | Estimator/inference geometry notes |

---

## 12. Statistical validation requirements

`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001` must define worlds:

| World | Stress |
|-------|--------|
| Balanced markets | Baseline donor pool |
| Weak donor pool | Few controls |
| High market heterogeneity | Covariate/outcome dispersion |
| Small geo count | Feasibility edge cases |
| Many simultaneous test cells | Multi-cell load |
| One shared control, many test groups | Control reuse stress |
| Uneven cell sizes | Imbalanced arms |
| Cell-specific shocks | Isolation test |
| Cross-cell contamination | Shared-control leakage |
| Spillover risk | Interference stress |
| Block imbalance | Blocking failure |
| Poor overlap | Matching/thinning collapse |
| Trimming-induced target shift | Population change |
| Supergeo aggregation effect | New-unit distortion |
| Power/MDE degradation | Small sample MDE inflation |
| Assignment infeasibility | Constraint impossibility |

**Required metrics:** pre-period outcome balance · covariate balance · donor-pool quality · treated/control support · block balance · cell balance · shared-control load · target-population drift · excluded-unit share · supergeo aggregation distortion · power/MDE accuracy · failure rate · reproducibility · downstream estimator compatibility.

---

## 13. Concurrent multi-experiment compatibility

**Mandatory field:** `concurrent_multi_experiment_compatibility`

| Value | Meaning |
|-------|---------|
| `compatible` | Multiple simultaneous experiments supported with documented policy |
| `compatible_with_constraints` | Supported only under explicit constraints (documented) |
| `restricted` | Limited reuse; cell isolation or control-load rules apply |
| `blocked_without_bridge` | Requires bridge artifact before concurrent use |
| `not_evaluated` | Default until design audit completes |

Every design must classify support for:

- Multiple simultaneous experiments  
- One shared control with many test groups  
- Multiple independent test cells  
- Cell-specific control groups  
- Overlapping campaigns/channels  
- Assignment exclusivity  
- Unit reuse / control reuse  
- Cell isolation  
- Concurrent power/MDE calculation  

**Rule:** Designs that **create new units** (supergeo) or **remove/alter eligible population** (trimmed/thinning with exclusion) may be **restricted** for concurrent multi-experiment execution and require explicit bridge/governance before ordinary multi-cell use.

---

## 14. Supergeo-specific pending work

Required future audit checks for `SupergeoModel` / `supergeos`:

- Source-unit mapping (base geo → supergeo ID)  
- Aggregation rule (sum, mean, weighted)  
- New unit definition and cardinality  
- Loss of original unit granularity  
- Donor/control implications on supergeo-unit panel  
- Power/MDE implications (2-row vs unit-panel mismatch)  
- Spillover assumptions across merged geos  
- Concurrent multi-cell restrictions  
- Bridge to original-geo causal claims ([`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) §13)  
- Downstream estimator compatibility (SCM/TBR/TBRRidge blocked without bridge per D5-DES-SUPERGEO-001)

---

## 15. Trimmed / thinning-specific pending work

**TrimmedMatchDesign** (`trimmedmatch`):

- Trim/thinning rule and `trim_rate`  
- Excluded units and exclusion reason  
- Global vs cell-specific exclusion  
- Target population before/after trim  
- Generalization limits to full population  
- Impact on shared controls and concurrent experiments  
- Impact on power/MDE (Tp/Te split semantics)  
- Bridge to full-population claims  

**ThinningDesign** (kernel thinning — distinct from trim):

- Thinning kernel and distance metric  
- Whether thinning excludes units or reweights assignment space  
- Target population impact (typically none — verify)  
- Concurrent multi-experiment status  

---

## 16. Blocking / QuickBlock / stratified design pending work

**QuickBlock:**

- Block construction variables and k-neighbor graph  
- Block IDs emission  
- Within-block assignment rule  
- Treatment/control counts per block  
- Multi-cell support (currently single treatment vector)  
- Block-aware inference requirements  
- Balance diagnostics  
- Failure modes (degenerate blocks)  

**StratifiedRandomization:**

- Stratum construction (percentile bins)  
- Within-stratum balance rule  
- Stratum IDs emission  
- Multi-cell + shared-control behavior  

**Rerandomization wrapper:**

- Imbalance metric and stopping rule  
- Equivalence to bare base randomizer (D5-POW sensitivity)  
- Seed handling across rerandomization draws  

---

## 17. Matching / GreedyMatch-style pending work

**greedy_match_markets:**

- Objective function and balance metric  
- Distance / KPI metric for matching  
- Donor eligibility vs SCM donor pool (MAT-004 separation)  
- Treated/control construction  
- Local optima / deterministic behavior with fixed seed  
- Multi-cell support via `n_test_grps`  
- Shared-control behavior  
- Power/MDE behavior under fixed-window harness  
- Downstream estimator compatibility (unit-panel SCM+JK reference design)

**MatchedPair:**

- Mahalanobis / graph matching objective  
- Output format vs geo assignment dict  
- Geo-runner integration gap  

---

## 18. Multi-cell / shared-control design pending work

Configuration: `n_test_grps > 1` on geo-supported designs.

Required checks:

- experiment_ids · cell_ids · test_group_ids  
- Shared control group ID and reuse policy  
- Cell-specific treated units; cell-specific control units (if any)  
- Control reuse policy (other test cells' units must not enter treated panel — D5 MCELL guard)  
- Cross-cell contamination risk  
- Cell failure policy (no silent cell dropping)  
- **No pooled causal claim without bridge** ([`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) §12)  
- **No pooled interval without bridge**  

---

## 19. Design output metadata — DESIGN_OUTPUT_CONTRACT_001 ✅

**Status:** **Accepted** — [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md)

First concrete output contract under the design audit lane. Defines **DesignOutputContract** schema (identity, unit universe, assignment, multi-cell, geometry, trim/supergeo, balance, power/MDE, compatibility hints, forbidden claims, PASS/WARN/BLOCK policy).

**Code inventory:** [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) maps current emitted fields against this contract — **no implementation is contract-complete**.

**Next design audit artifact:** `DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001` — contract validation test specification (Phase 3).

---

## 20. Design guardrails

Initial guardrails (enforce via `DESIGN_GUARDRAILS_001`):

1. No design output consumed without **`geometry_id`**.  
2. No design output consumed without **treated/control labels** (or documented pair structure).  
3. No multi-cell design may **silently pool** causal effects.  
4. No shared-control design may omit **control reuse policy**.  
5. No block design may omit **block IDs**.  
6. No trimmed/thinning design may **hide excluded units**.  
7. No supergeo design may hide **source-unit mapping**.  
8. No design may claim **full-population estimand after trimming** without bridge.  
9. No design may claim **original-geo estimand after supergeo** without bridge.  
10. No design may support **concurrent multi-experiment execution** without explicit compatibility status.  
11. No design may feed TrustReport, CalibrationSignal, MMM, or LLM layers without **suitability role** assignment.  

---

## 21. Relationship to current artifacts

| Artifact | Relationship |
|----------|--------------|
| [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) | Design outputs must declare `geometry_id`; trim/supergeo bridges depend on design metadata |
| [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) | Readout targets assume design-defined assignment and population |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | **Incomplete** until design audit parity; v2 requires design × estimator × inference rows |
| D5 Level B reports | Reference-design characterization — not full design audit |
| D5-POW / D5-DES | Partial design evidence (001e, supergeo, trim) |
| **`DESIGN_OUTPUT_CONTRACT_001`** | ✅ Accepted — [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md); feeds design audit ladder |
| Suitability v2 | Requires design combination matrix + design suitability framework |
| TROP / Bayesian extensions | Depend on design output metadata (assignment, eligibility, covariates) |

---

## 22. Current status of all discovered designs

| Design name | Category | Discovered in | Support status | Audit status | Geometry impact | Concurrency status | Downstream claim status | Required next audit artifact |
|-------------|----------|---------------|----------------|--------------|-----------------|--------------------|-------------------------|------------------------------|
| greedy_match_markets | matching_design | assign.py | geo-run active | not_evaluated | unit_panel_single_cell | compatible_with_constraints | contract_required | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| CompleteRandomization | standard_assignment | assign.py | geo-run active | not_evaluated | unit_panel_single_cell | compatible_with_constraints | contract_required | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| BalancedRandomization | standard_assignment | assign.py | geo-run active | not_evaluated | unit_panel_single_cell | compatible_with_constraints | contract_required | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| StratifiedRandomization | stratified_assignment | assign.py | geo-run active | not_evaluated | unit_panel_single_cell | compatible_with_constraints | contract_required | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| ThinningDesign | thinning_design | assign.py | geo-run active | not_evaluated | unit_panel_single_cell | not_evaluated | contract_required | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| Rerandomization | blocking wrapper | assign.py | geo-run orchestration | not_evaluated | inherits base | compatible_with_constraints | contract_required | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| QuickBlock | blocking_assignment | quickblock.py | registered, not geo-run | not_evaluated | unknown_or_not_evaluated | not_evaluated | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| MatchedPair | matching_design | matched_pair.py | registered, not geo-run | not_evaluated | unknown_or_not_evaluated | not_evaluated | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| TrimmedMatchDesign | trimmed_population | trimmed_match.py | registered, direct API | not_evaluated | trimmed_geometry | restricted | bridge_required | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| SupergeoModel | supergeo_design | supergeos.py | registered, direct API | not_evaluated | supergeo | blocked_without_bridge | bridge_required | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| multi_test_groups | multi_cell_assignment | n_test_grps config | geo-run param | not_evaluated | multi_cell_per_cell | restricted | bridge_required (pooled) | DESIGN_COMBINATION_VALIDATION_MATRIX_001 |
| GeoExperimentDesign | orchestration | geo_experiment_design.py | active | not_evaluated | emits via assignment | not_evaluated | contract_required | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| PowerAnalysis | power_mde_helper | power.py | active | not_evaluated | aggregate_two_row (MDE path) | not_evaluated | contract_required | DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001 |

**No row assigns** production readiness, trust, CalibrationSignal, MMM, or suitability.

---

## 23. Roadmap

Recommended sequence:

1. **`DESIGN_OUTPUT_CONTRACT_001`** — metadata schema ✅ **Accepted**  
2. **`DESIGN_CODE_INVENTORY_001`** — repo enumeration ✅ **Accepted**  
3. **`DESIGN_LITERATURE_ALIGNMENT_001`** — literature alignment ✅ **Accepted**  
4. **`DESIGN_IMPLEMENTATION_VALIDATION_001`** — implementation validation ✅ **Accepted**
5. **`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001`** — statistical protocol ✅ **Accepted**
6. **`DESIGN_COMBINATION_VALIDATION_MATRIX_001`** — design × geometry × estimator × inference × readout ✅ **Accepted**  
7. **`DESIGN_GUARDRAILS_001`** — PASS/WARN/BLOCK policy ✅ **Accepted**  
8. **`DESIGN_SUITABILITY_FRAMEWORK_001`** — design-side suitability ✅ **Accepted**  
9. **`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001`** — enforcement planning ✅ **Accepted**  
10. **`DESIGN_CONTRACT_SCHEMA_001`** — machine-readable schema ✅ **Accepted**  
11. **`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001`** — tier-1 emission plan ✅ **Accepted**  
12. **`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001`** — **(next)**  

Method-specific audits (supergeo, trim, QuickBlock integration) run in parallel where blocked on bridges.

---

## 24. Governance gates

No design promotion, suitability status, TrustReport role, CalibrationSignal eligibility, MMM/LLM authorization, or downstream estimator compatibility claim until:

1. Design audit ladder artifacts **Accepted** (§8)  
2. [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) supplies required metadata schema ✅  
3. Geometry and readout contracts satisfied per companion artifacts  
4. Design combination matrix row exists for each design × estimator × inference path  
5. `DESIGN_SUITABILITY_FRAMEWORK_001` explicitly approves a role  

---

## 25. Completion checklist

| Item | Status |
|------|--------|
| Repo searched for all design methods | ✅ §6 |
| Design list produced | ✅ §6, §22 |
| Roadmap updated | ✅ companion doc edits |
| Audit registry updated | ✅ |
| Design audit ladder defined | ✅ §8 |
| Concurrency gap captured | ✅ §13 |
| Supergeo/trim restrictions captured | ✅ §14–§15 |
| No code changed | ✅ |
| Tests run | ✅ (validation suite) |

---

## 26. Roadmap and audit updates checked

| Document | Update |
|----------|--------|
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Design-side audit lane + ladder |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Post-D5 design audit track |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Design audit placement |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Artifact registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Design-side soundness gap |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Incomplete without design audit |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Future full matrix scope |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Design validation worlds required |

**D5 reports inspected:** SCM-JK, AugSynth point, TBR aggregate, DID bootstrap, MCELL per-cell, TBRRidge inference; D5-POW-001e, D5-DES-SUPERGEO-001, D5-DES-TRIM-001, D5-MCELL-001; design inventory 001.

---

*DESIGN-AUDIT-PROGRAM-001 v1.1.1 — DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001 accepted; emission not implemented; next = DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.*
