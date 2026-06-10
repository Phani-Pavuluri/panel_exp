# Design Literature Alignment 001

**Document ID:** DESIGN-LITERATURE-ALIGNMENT-001  
**Title:** Design Literature Alignment 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` design families and design-like helpers  
**Artifact type:** Documentation / governance / literature alignment — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) · [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md)

**Guardrails:** No implementation validation · no statistical validation · no promotion · no suitability claim · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Literature Alignment 001 |
| Status | **Accepted** |
| Scope | GeoX / `panel_exp` design families and design-like helpers |
| Artifact type | Documentation / governance / literature alignment |

Second concrete design audit artifact after [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md). Aligns all **31 inventory rows** (DES-001–DES-031) to canonical experimental-design methodology. **Does not validate or promote any design.**

---

## 2. Purpose

This artifact defines **what each design family is supposed to mean** in literature and standard geo-experiment practice before:

- `DESIGN_IMPLEMENTATION_VALIDATION_001` (code fidelity + contract emission)  
- `DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001` (simulation worlds)  
- `DESIGN_COMBINATION_VALIDATION_MATRIX_001` (design × estimator × inference)  
- `DESIGN_SUITABILITY_FRAMEWORK_001` (role assignment)

For every DES row it states: methodology family, alignment status, required assumptions, required contract fields, literature caveats, and downstream validation focus.

**Alignment ≠ validation ≠ suitability.**

---

## 3. Why this artifact exists

| Gap | This artifact addresses |
|-----|-------------------------|
| [`METHOD_LITERATURE_ALIGNMENT_001.md`](METHOD_LITERATURE_ALIGNMENT_001.md) Layer 2 | Covered estimators/inference; design families summarized only at high level |
| [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) | Found 31 rows, **0** contract-complete designs — existence ≠ correctness |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Literature implies fields (geometry, trim, blocks, concurrency) not yet emitted |
| D5-DES / D5-POW evidence | Trim/supergeo show geometry/population mismatch with flat SCM+JK paths |

Design methods fix **assignment**, **target population**, **geometry**, **donor pool**, and **concurrency** — all prerequisites for estimator/inference feasibility. Literature alignment must precede implementation and statistical proof.

---

## 4. Scope

Includes all rows from [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) §8:

- 9 registered designs + `Rerandomization` wrapper  
- `multi_test_groups` configuration  
- Power/MDE helpers · validation helpers · eligibility helpers  
- Orchestration (`GeoExperimentDesign`, `geo_runner`)  
- Output/governance objects (`DesignEvidence`, `DesignSpec`, …)  
- Reporting dashboard · superseded `track_d_design_inventory_001` (historical only)

**Evidence inputs (not proof):** [`D5_DES_TRIM_001_REPORT.md`](track_d/D5_DES_TRIM_001_REPORT.md) · [`D5_DES_SUPERGEO_001_REPORT.md`](track_d/D5_DES_SUPERGEO_001_REPORT.md) · D5-POW-001e tier-1 reports · D5-STAT reference-design characterization · [`METHOD_LITERATURE_ALIGNMENT_001.md`](METHOD_LITERATURE_ALIGNMENT_001.md) §5

---

## 5. Non-goals

- No implementation validation or statistical OC  
- No code, harness, fixture, or D5 archive changes  
- No design promotion or suitability claim  
- No TrustReport / CalibrationSignal / MMM / LLM authorization  
- No claim that literature alignment authorizes production use  

---

## 6. Source / methodology basis

### 6.1 Methodological families reviewed

| # | Family | Canonical sources (families, not implementation claims) |
|---|--------|----------------------------------------------------------|
| 1 | Geo-experiment / matched markets | Industry geo lift practice; matched-market test/control construction; pre-period balance (see Track D D1/D5-POW materials); Abadie & Gardeazabal (2003) geo case study tradition |
| 2 | Complete randomization | Fisher (1935); Cox (1958); Bernoulli assignment with known π |
| 3 | Balanced / constrained allocation | Fixed treatment counts or KPI-volume targets; differs from i.i.d. Bernoulli |
| 4 | Stratified randomization | Cochran (1977); Imbens & Rubin (2015) — strata defined on pre-treatment covariates |
| 5 | Blocked experiments | Imai, King, Nall (2009); block-randomized A/B tests |
| 6 | Covariate-adjusted blocking (QuickBlock) | Wang, Yu, Zubizarreta (2021) QuickBlock / regularized blocking |
| 7 | Matched pairs | Rosenbaum (2002); paired randomized experiments |
| 8 | Rerandomization | Morgan & Rubin (2012); Li, Ding, Rubin (2018) inference caveats |
| 9 | Kernel / candidate-space thinning | Dwivedi & Mackey (2021) kernel thinning |
| 10 | Trimmed / restricted population | Trimmed matching (product Tp/Te design); generalization limits for selected subsets |
| 11 | Supergeo / aggregation | Product-specific supergeo construction; changed unit of analysis |
| 12 | Multi-arm / shared control | Factorial and multi-cell geo experiments; multiple-comparison caution |
| 13 | Power / MDE (geo) | Simulation-based planning; Brodersen et al. (2015) BSTS planning tradition; classical power as contrast |
| 14 | Design-output governance | Reproducibility (assignment records, seeds, exclusions); CONSORT-style metadata |

### 6.2 Code inspection basis (read-only)

`panel_exp/design/assign.py` · `quickblock.py` · `matched_pair.py` · `trimmed_match.py` · `supergeos.py` · `power.py` · `constraints.py` · `validation.py` · `geo_experiment_design.py` · `geo_runner.py` · `evidence.py` · `spec.py` · `modes/__init__.py`

---

## 7. Alignment status taxonomy

| Status | Meaning |
|--------|---------|
| `aligned_conceptual_family` | Maps to a standard design family; main semantics recognizable |
| `partially_aligned_requires_contract_fields` | Family recognized but metadata, inference path, or emission incomplete |
| `aligned_but_requires_inference_adjustment` | Design valid but analysis must respect selection (rerandomization, blocks, pairs) |
| `bridge_required_due_to_geometry_or_population` | Target population or unit of analysis changed — bridge required per geometry contract |
| `not_literature_aligned_yet` | Cannot map to canonical family without further review |
| `helper_not_design_family` | Orchestration, validation, output, or governance — not a design method |
| `superseded_or_historical` | Prior generator superseded by inventory |
| `insufficient_information` | Literature or code mapping incomplete |

**Clarification:** Any `aligned_*` status still requires Layer 3–4 proof and contract PASS before downstream authorization.

---

## 8. Master alignment table

**Downstream status (all rows):** `not_validated` · `not_contract_complete` · `not_suitability_approved`

| ID | Name | Category | Methodology family | Alignment status | Impl. validation focus | Stat. validation focus |
|----|------|----------|-------------------|------------------|------------------------|------------------------|
| DES-001 | greedy_match_markets | matching | Matched-market greedy pairing | partially_aligned_requires_contract_fields | Pre-period slice (INV-D1-001); objective = corr/dtw/l2 | Balance worlds; weak donors; multi-cell |
| DES-002 | CompleteRandomization | standard | Bernoulli complete randomization | aligned_conceptual_family | π, exclusivity, seed | Null FPR; constraint infeasibility |
| DES-003 | BalancedRandomization | standard | KPI-volume balanced allocation | partially_aligned_requires_contract_fields | Volume target vs π semantics | Share imbalance; small N |
| DES-004 | StratifiedRandomization | stratified | Percentile stratification | partially_aligned_requires_contract_fields | Stratum construction; stratum IDs | Poor strata; empty cells |
| DES-005 | ThinningDesign | thinning | Kernel-thinning-inspired assignment | partially_aligned_requires_contract_fields | Candidate-space vs exclusion; δ, α | Thinning shift; multi-cell |
| DES-006 | Rerandomization | blocking wrapper | Morgan–Rubin rerandomization | aligned_but_requires_inference_adjustment | Base randomizer dispatch; acceptance rule | Selection bias vs bare randomization |
| DES-007 | QuickBlock | blocking | QuickBlock / kNN blocking | partially_aligned_requires_contract_fields | Block construction; block IDs | Block leakage; inference blocks |
| DES-008 | MatchedPair | matching | Optimal Mahalanobis pairing | partially_aligned_requires_contract_fields | Pair IDs; paired randomization | Pair mismatch; pair-aware inference |
| DES-009 | TrimmedMatchDesign | trimmed | Tp/Te trimmed pair design | bridge_required_due_to_geometry_or_population | Trim policy; excluded units | Target-population shift; trim rate |
| DES-010 | SupergeoModel | supergeo | MILP supergeo aggregation | bridge_required_due_to_geometry_or_population | Source map; aggregation weights | Aggregation distortion; MILP scope |
| DES-011 | multi_test_groups | multi_cell | Shared-control multi-arm | partially_aligned_requires_contract_fields | Cell IDs; reuse policy | Shared-control overload; pooling |
| DES-012 | GeoExperimentDesign | orchestration | Geo design orchestrator | helper_not_design_family | Rerandomization wrap; evidence path | Tier-1 OC batteries |
| DES-013 | run_geo_experiment_design | orchestration | Registry pipeline | helper_not_design_family | Handler contract | Pipeline integration |
| DES-014 | PowerAnalysis | power/MDE | Simulation MDE | partially_aligned_requires_contract_fields | Aggregate vs unit geometry | MDE miscalibration |
| DES-015 | PowerContract | power/MDE | MDE metadata envelope | helper_not_design_family | Join to design output | Semantics disclosure |
| DES-016 | prepare_constraint_context | eligibility | Constraint pinning | helper_not_design_family | Eligible/excluded emission | Infeasible constraints |
| DES-017 | validate_assignment_dict | validation | Assignment QA | helper_not_design_family | Exclusivity checks as fields | — |
| DES-018 | validate_design | validation | PASS/WARN/FAIL gate | helper_not_design_family | Balance threshold semantics | — |
| DES-019 | slice_wide_to_time_period | panel | Pre-period window (INV-D1-001) | helper_not_design_family | Time window metadata | Post-period leakage |
| DES-020 | imbalance | panel | Balance metric | helper_not_design_family | Metric name/threshold | Rerandomization acceptance |
| DES-021 | make_generator | panel | RNG reproducibility | helper_not_design_family | Seed policy | — |
| DES-022 | DesignRegistry | panel | Registration | helper_not_design_family | Registry ↔ literature IDs | — |
| DES-023 | balanced_volume_assign | eligibility | Volume balancing primitive | helper_not_design_family | Assignment probability | — |
| DES-024 | bernoulli_complete_assign | eligibility | Bernoulli primitive | helper_not_design_family | π documentation | — |
| DES-025 | create_design_comparison_dashboard | reporting | MLflow ranking UI | helper_not_design_family | Ungoverned outputs | — |
| DES-026 | DesignEvidence | output | Partial contract envelope | helper_not_design_family | Full contract emission | — |
| DES-027 | ExperimentEvidence | output | Design + inference wrap | helper_not_design_family | Contract linkage | — |
| DES-028 | DesignSpec | governance | Experiment specification | helper_not_design_family | design_method_id | — |
| DES-029 | DesignMethod enum | governance | Method taxonomy | helper_not_design_family | Enum ↔ registry keys | — |
| DES-030 | DesignProfile | governance | F-DECISION inputs | helper_not_design_family | Not contract object | — |
| DES-031 | track_d_design_inventory_001 | historical | Prior generator | superseded_or_historical | — | — |

---

## 9. Geo / matched-market alignment (DES-001)

**Inventory:** `greedy_match_markets` · `assign.py`

### Literature identity

Greedy augmentation of test/control markets to optimize pre-treatment similarity (correlation, DTW, or L2 imbalance) under KPI-share constraints — **matched-market / geo-experiment** family, not classical pair matching.

### Conceptual assumptions

| Assumption | Literature expectation | Repo posture |
|------------|------------------------|--------------|
| Unit of randomization | Geographic market (DMA/geo) | ✅ Market-level |
| Pre-period only for matching | Matching on pre-treatment outcomes/covariates | ✅ `pre_treatment_period` + `slice_wide_to_time_period` when set |
| Donor/control eligibility | Documented eligible universe | ⚠️ Implicit via assignment lists |
| Treatment probability | Declared π or volume share | ⚠️ `treatment_probability` + `split_type=kpi_share` |
| Local optimum | Greedy ≠ global optimum | ⚠️ Documented in docstring; not emitted |

### Required contract fields

`geometry_id` · `assignment_by_unit` · `donor_pool_units` · `pre_period_*` · `balance_diagnostics` · `concurrent_multi_experiment_compatibility` · `forbidden_downstream_claims`

### Literature caveats

- Greedy matching is **heuristic** — no guarantee of optimal market partition.  
- Design matching pool ≠ SCM donor pool at estimation ([`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) MAT-004).  
- Multi-cell (`n_test_grps > 1`) shares one control — requires shared-control policy metadata.  
- Analysis with SCM/TBR requires **design–analysis alignment** ([`METHOD_LITERATURE_ALIGNMENT_001.md`](METHOD_LITERATURE_ALIGNMENT_001.md) DES-GMM-001).

### Current gaps

Partial `DesignEvidence` only; no `geometry_id`; concurrency not emitted; balance metrics internal to rerandomization loop.

**Alignment:** `partially_aligned_requires_contract_fields`

---

## 10. Complete and balanced randomization alignment (DES-002, DES-003, DES-023, DES-024)

### DES-002 CompleteRandomization

| Aspect | Literature | Implementation |
|--------|------------|----------------|
| Assignment | Bernoulli(π) independent across eligible units | `bernoulli_complete_assign` + constraint context |
| Exclusivity | Each unit in exactly one arm | `validate_assignment_dict` |
| π | Known assignment probability | `treatment_probability` on `Design` |
| Seed | Reproducible RNG | `make_generator(random_state)` |

**Alignment:** `aligned_conceptual_family` — **pending** contract emission and Layer 3 π documentation under constraints.

### DES-003 BalancedRandomization

**Literature:** Constrained randomization with **fixed KPI-volume shares** to test arms — common in geo spend experiments; **not** identical to Bernoulli complete randomization.

**Implementation:** `balanced_volume_assign` targets volume shares; differs from `CompleteRandomization` stochastically.

**Caveat:** Must not label as "complete randomization" in product copy without clarifying volume-balancing semantics.

**Alignment:** `partially_aligned_requires_contract_fields` — requires `assignment_rule`, `assignment_probability` (effective, not just nominal π).

### DES-023 / DES-024 primitives

Assignment building blocks for tier-1 designs — `helper_not_design_family` but must support literature-aligned `assignment_probability` and exclusivity in contract.

---

## 11. Stratified / blocked / QuickBlock alignment (DES-004, DES-007)

### DES-004 StratifiedRandomization

| Aspect | Literature | Implementation |
|--------|------------|----------------|
| Strata | Covariate-defined homogeneous groups | Percentile bins on total pre-period volume (`n_percentiles`) |
| Within-stratum assignment | Random or balanced | Volume balancing within strata |
| Stratum IDs | Required for stratified analysis | **Not emitted** |

**Inference:** Stratum-aware inference may be required if strata are informative.

**Alignment:** `partially_aligned_requires_contract_fields`

### DES-007 QuickBlock

**Literature:** Covariate-adjusted regularized blocking (Wang et al. 2021 QuickBlock family) — partition units into blocks on covariate space, randomize within blocks.

**Implementation:** kNN graph blocking on `X`, optional block splitting; outputs **numpy treatment vector**, not geo assignment dict; **not geo-run supported**.

**Gaps:** `block_ids`, `block_variables`, `within_block_assignment_rule`, `inference_must_respect_blocks` — all missing from output.

**Alignment:** `partially_aligned_requires_contract_fields` — family recognized; geo integration and metadata **not_evaluated**.

---

## 12. Matched-pair alignment (DES-008)

**Literature:** Optimal pair matching on Mahalanobis distance; randomize treatment within pairs (Rosenbaum paired designs).

**Implementation:** `nx.matching.max_weight_matching` on negated distance graph; `assign` returns vector; **not** geo dict.

| Requirement | Status |
|-------------|--------|
| `pair_ids` | Not emitted |
| Pair-aware inference hint | Not emitted |
| Multi-cell | Not evaluated |

**Alignment:** `partially_aligned_requires_contract_fields`

---

## 13. Rerandomization alignment (DES-006)

**Literature:** Morgan & Rubin (2012) — repeat randomizations until covariate balance below threshold; valid inference requires accounting for rerandomization (not automatic in standard i.i.d. tests).

**Implementation:**

- Wraps tier-1 bases (`greedy_match_markets`, thinning, balanced, complete, stratified) in `GeoExperimentDesign`  
- `max_iter`, `target_imbalance`, `imbalance_metric` (l2/rmse/mae)  
- Accepts first assignment meeting threshold or best after `max_iter`  
- **Identity:** Evidence uses **base** design name, not `Rerandomization`

| Caveat | Implication |
|--------|-------------|
| Selection bias | Inference must be rerandomization-aware or conservative |
| Threshold tuning | Affects effective assignment distribution |
| Reproducibility | Seed + iteration count must be logged |

**Alignment:** `aligned_but_requires_inference_adjustment`

---

## 14. Thinning alignment (DES-005)

**Literature:** Dwivedi & Mackey (2021) kernel thinning — **candidate-space** reweighting/thinning of representative points; **not** the same as excluding units from target population.

**Implementation (`ThinningDesign`):**

- Docstring cites kernel thinning; uses norm-based weights `w_i`, parameters `delta`, volume-share guards  
- Assigns units to control/test groups — **does not** document excluded units  
- `assign_all` **not implemented**

### Critical ambiguity (conceptual gap G-DES-003)

| Question | Required resolution in Layer 3 |
|----------|-------------------------------|
| Candidate-space thinning only? | If yes → `target_population_changed = false` |
| Units removed from experiment? | If yes → trim-like metadata required |
| Estimand | Full eligible population vs thinned assignment support |

**Alignment:** `partially_aligned_requires_contract_fields` — family cited; **thinning semantics ambiguous** in output contract.

---

## 15. TrimmedMatch alignment (DES-009)

**Literature:** Restricted-population **paired geo design** — Tp for pairing, Te for evaluation/power; trim poor pairs; within-pair randomization + rerandomization ([`trimmed_match.py`](../panel_exp/design/trimmed_match.py) docstring; D5-DES-TRIM-001).

| Aspect | Finding |
|--------|---------|
| Target population | **Changes** — only trimmed pair subset |
| Full-population claims | **Blocked** without bridge ([`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) §14) |
| Output geometry | `trimmed_geometry` — pair DataFrame, not flat dict |
| Power | Classical pair-lift CIs on Te — **not** geo `PowerAnalysis` aggregate path |
| D5 verdict | `target_population_shift_severe` |

**Required contract fields:** `trim_policy`, `excluded_units`, `target_population_pre_trim/post_trim`, `full_population_claim_allowed=false`, `pair_ids`

**Alignment:** `bridge_required_due_to_geometry_or_population`

---

## 16. Supergeo alignment (DES-010)

**Literature:** **Product-specific** supergeo construction — KMeans partition, combinatorial supergeo candidates, MILP pair selection; creates **new experimental units** aggregating DMAs.

| Aspect | Finding |
|--------|---------|
| Unit of randomization | Supergeo aggregate, not original DMA |
| Source mapping | Internal only — **not** exported as `supergeo_source_unit_map` |
| Original-geo claims | **Blocked** without bridge ([`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) §13) |
| D5 verdict | `separate_geometry_design`; flat SCM+JK invalid |
| Power/MDE | Aggregate sales trajectories — geometry mismatch with unit-panel SCM |

**Alignment:** `bridge_required_due_to_geometry_or_population`

---

## 17. Multi-cell / shared-control alignment (DES-011)

**Literature:** Multi-arm experiments with one or more test cells and shared or cell-specific controls; factorial caution for multiple comparisons; portfolio/pooled claims require explicit estimand.

**Implementation:** `n_test_grps` parameter across tier-1 designs; assignment keys `test_0`, `test_1`, …; **shared control implicit** — same `control` list serves all test arms.

| Requirement | Status |
|-------------|--------|
| `cell_ids` / `test_group_ids` | Not emitted |
| `shared_control_policy` | Not emitted |
| `control_reuse_policy` | Not emitted |
| Pooled causal claim | **Blocked** without bridge |
| Portfolio claim | Default **false** |

**Concurrency:** `restricted` — overlapping campaigns need isolation rules.

**Alignment:** `partially_aligned_requires_contract_fields`

---

## 18. Power / MDE literature alignment (DES-014, DES-015)

**Literature contrast:**

| Classical power | Repo `PowerAnalysis` |
|-----------------|----------------------|
| Closed-form / analytic | **Simulation coverage** (`MDE_SEMANTICS`) |
| Unit-level geo panel | Often **aggregate 2-row** geometry in MDE path |
| Design-independent | **Estimator- and inference-dependent** |

**PowerContract** correctly disclaims financial-commitment use; warnings documented.

**Gaps:**

- Power/MDE **not joined** to `DesignOutputContract` envelope  
- Aggregate MDE ≠ unit-panel SCM readout (D5-POW vs D5-STAT gap)  
- Must emit `power_method`, `mde_method`, `power_mde_warnings`, geometry hints

**Alignment:** DES-014 `partially_aligned_requires_contract_fields`; DES-015 `helper_not_design_family`

---

## 19. Validation / helper / output object alignment (DES-012–DES-030)

These are **not** standalone design families. They must **support** literature-aligned metadata:

| ID | Role | Literature support required |
|----|------|----------------------------|
| DES-012–013 | Orchestration | Emit rerandomization params, design identity, join power to evidence |
| DES-016–018 | QA / eligibility | Surface `eligible_units`, `excluded_units`, exclusivity results |
| DES-019 | INV-D1-001 | Pre-period window in contract time fields |
| DES-020–021 | Balance / RNG | `imbalance_score`, `balance_metric_name`, `random_seed` |
| DES-022 | Registry | Stable `design_method_id` ↔ literature family |
| DES-025 | Dashboard | **Ungoverned** — no suitability inference from rankings |
| DES-026–027 | Evidence | Full `DesignOutputContract` emission |
| DES-028–030 | Spec / governance | `DesignSpec` seeds contract identity; `DesignProfile` not a design output |

**Alignment:** `helper_not_design_family` (DES-031: `superseded_or_historical`)

---

## 20. Contract field implications

Literature alignment **reinforces** [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) requirements:

| Literature topic | Contract groups |
|------------------|-----------------|
| Randomization / π | §7 identity, §9 assignment (`assignment_probability`, `assignment_rule`) |
| Eligibility / exclusions | §8 unit universe |
| Geometry / population | §12 geometry, §15 trim, §16 supergeo |
| Blocks / strata / pairs | §13 block/stratum/pair |
| Multi-cell / concurrency | §10–§11 |
| Balance / rerandomization | §17 balance, §9 assignment checks |
| Power / MDE | §18 power/MDE |
| Downstream safety | §21 hints, §24 forbidden claims |

**No design is compliant today** — literature alignment defines **why** fields are required, not that they are present.

---

## 21. Conceptual gap register

| Gap ID | Description | Affected DES |
|--------|-------------|--------------|
| G-DES-001 | QuickBlock geo-run path and block-ID emission undefined | DES-007 |
| G-DES-002 | Thinning: candidate-space vs population exclusion ambiguous | DES-005 |
| G-DES-003 | Supergeo source-unit bridge not implemented in output | DES-010 |
| G-DES-004 | Trim target-population bridge not implemented | DES-009 |
| G-DES-005 | Shared-control policy implicit, not specified | DES-011, tier-1 |
| G-DES-006 | Multi-cell pooled/portfolio claims blocked without bridge | DES-011 |
| G-DES-007 | Rerandomization inference implications not connected to inference layer | DES-006 |
| G-DES-008 | Block/pair/stratum-aware inference not connected | DES-004, DES-007, DES-008 |
| G-DES-009 | Power/MDE aggregate geometry ≠ unit-panel analysis geometry | DES-014 |
| G-DES-010 | Greedy matching local optimum vs literature matched-market protocols | DES-001 |
| G-DES-011 | Balanced vs complete randomization naming confusion | DES-002, DES-003 |
| G-DES-012 | Design outputs not contract-complete (0/31) | DES-026, all designs |
| G-DES-013 | TrimmedMatch / Supergeo non-dict outputs lack contract adapters | DES-009, DES-010 |
| G-DES-014 | Rerandomization wrapper identity lost in evidence | DES-006, DES-012 |

---

## 22. Statistical validation implications

Future `DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001` worlds (by family):

| World | Design families |
|-------|-----------------|
| Balanced markets | DES-001, tier-1 |
| Weak donor pool | DES-001, DES-009 |
| High heterogeneity | DES-001, DES-004 |
| Small N | All geo tier-1 |
| Many test groups | DES-011 |
| Shared control overload | DES-011 |
| Poor block/stratum construction | DES-004, DES-007 |
| Pair mismatch | DES-008, DES-009 |
| Thinning-induced shift | DES-005 |
| Trimming-induced target shift | DES-009 |
| Supergeo aggregation distortion | DES-010 |
| Rerandomization selection effects | DES-006 |
| Power/MDE miscalibration | DES-014 |
| Assignment infeasibility | Constraints + tier-1 |

**Rule:** Worlds must derive from **literature-aligned failure modes** in this artifact — not ad hoc shortlists.

---

## 23. Implementation validation implications

`DESIGN_IMPLEMENTATION_VALIDATION_001` must verify:

1. Code behavior matches **intended conceptual family** (§9–§18)  
2. Outputs include **required contract fields** per family  
3. Helper naming matches behavior (e.g. Balanced ≠ Complete randomization)  
4. Assignment probabilities documented (nominal vs effective under constraints)  
5. Randomization reproducible (`random_seed`, iteration logs for rerandomization)  
6. Block/stratum/pair metadata emitted when applicable  
7. Trim/supergeo metadata emitted when applicable  
8. `concurrent_multi_experiment_compatibility` emitted  
9. Power/MDE joined to design output envelope  
10. Non-dict outputs (trim/supergeo/block) have adapter or remain **BLOCK**

---

## 24. Combination matrix implications

Future `DESIGN_COMBINATION_VALIDATION_MATRIX_001` rows must use:

- **Inventory IDs** (DES-001–DES-031)  
- **Literature-aligned semantics** from this artifact  
- **Geometry IDs** from [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md)  

Dimensions:

| Dimension | Example blocked case |
|-----------|---------------------|
| design × geometry | supergeo × unit_panel_single_cell SCM+JK without bridge |
| design × estimator | trimmedmatch × flat SCM+JK (D5-DES-TRIM) |
| design × inference | rerandomization × naive i.i.d. bootstrap |
| design × readout | aggregate MDE × unit-panel ATT |
| design × concurrency | supergeo × concurrent multi-experiment |
| design × target population | trim × full-population claim |

---

## 25. Governance gates

| Gate | Status |
|------|--------|
| Validates implementation | **No** |
| Statistically validates designs | **No** |
| Authorizes downstream use | **No** |
| MMM/MIP/LLM may recommend from alignment alone | **No** |
| Future authorization path | Implementation validation → statistical validation → combination matrix → guardrails → suitability |

---

## 26. Current status and verdict

**Verdict:** `design_literature_alignment_complete_with_open_conceptual_gaps`

| Metric | Value |
|--------|-------|
| Inventory rows reviewed | 31 / 31 |
| Aligned conceptual family (incl. partial) | 11 design-family rows |
| Bridge-required | 2 (trim, supergeo) |
| Helper/governance rows | 18 |
| Superseded | 1 |
| Validated designs | **0** |
| Contract-complete designs | **0** |
| Open conceptual gaps | 14 (G-DES-001–014) |

**Not claimed:** production-ready, validated, governed, suitable, TrustReport-eligible, CalibrationSignal-eligible, MMM-ready, LLM-ready.

---

## 27. Roadmap

**Next artifact:** **`DESIGN_IMPLEMENTATION_VALIDATION_001`**

| Feeds | Use |
|-------|-----|
| Implementation validation | §23 checks per DES row |
| Statistical protocol | §22 worlds per family |
| Combination matrix | §24 dimensions |
| Guardrails | G-DES gap register |
| Suitability framework | Only after above + contract PASS |

---

## 28. Completion checklist

| Item | Status |
|------|--------|
| Inventory rows reviewed (DES-001–DES-031) | ✅ |
| Literature/methodology families reviewed | ✅ §6 |
| Master alignment table | ✅ §8 |
| Per-family sections | ✅ §9–§19 |
| Conceptual gaps registered | ✅ §21 |
| Contract implications mapped | ✅ §20 |
| Statistical validation implications | ✅ §22 |
| Implementation validation implications | ✅ §23 |
| Combination matrix implications | ✅ §24 |
| Companion roadmap docs updated | ✅ |
| No code changed | ✅ |
| Tests run | ✅ (see validation report) |

---

## 29. Companion doc updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Literature alignment complete; next = implementation validation |
| [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) | Literature alignment consumed inventory |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Literature reinforces required fields |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Next = implementation validation |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Prerequisite for design implementation validation |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Design audit lane status |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Conceptual gaps |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Suitability requires alignment + impl validation |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Literature-aligned semantics required |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Worlds from literature failure modes |

---

*DESIGN-LITERATURE-ALIGNMENT-001 v1.0.0 — Accepted; verdict = design_literature_alignment_complete_with_open_conceptual_gaps; next = DESIGN_IMPLEMENTATION_VALIDATION_001.*
