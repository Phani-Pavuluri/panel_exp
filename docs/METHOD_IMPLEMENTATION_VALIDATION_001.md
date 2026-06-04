# METHOD-IMPLEMENTATION-VALIDATION-001

**Document ID:** METHOD-IMPLEMENTATION-VALIDATION-001  
**Type:** Layer 3 implementation and architecture validation — **read-only**  
**Status:** **complete** (register + generator + code inspection)  
**Date:** 2026-06-04  
**Parent program:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) Layer 3

**Machine-readable register:** [`track_d/archives/METHOD_IMPLEMENTATION_VALIDATION_001.json`](track_d/archives/METHOD_IMPLEMENTATION_VALIDATION_001.json) (29 rows; regenerate: `python -m panel_exp.validation.method_implementation_validation_001`)

**Generator:** [`panel_exp/validation/method_implementation_validation_001.py`](../panel_exp/validation/method_implementation_validation_001.py)

**Primary inputs:** [`METHOD_CODE_INVENTORY_001.md`](METHOD_CODE_INVENTORY_001.md) · [`METHOD_LITERATURE_ALIGNMENT_001.md`](METHOD_LITERATURE_ALIGNMENT_001.md) · Layer 1–2 JSON archives

**Evidence inputs (not final authority):** Track D D1–D5 · AugSynth P1–P6 · fidelity audit G1–G8 · JK calibration · Conformal failure · TBR/TBRRidge · supergeo/trim · F-INF-003 · COMBO/AUDIT-010

**Guardrails:** No trust roles · no promotion · no behavior change · no OC in this artifact

---

## 1. Purpose

Answer **“Did we implement what we think we implemented?”** for the code-derived method universe.

Layer 3 checks whether repo **code paths** match the contracts in Layer 2 literature alignment — identity, estimand, geometry, design fidelity, inference semantics, and orchestration — **without** assigning evidence roles or running statistical OC.

| Question | Layer 3 answers |
|----------|----------------|
| Do method names match behavior? | Identity + alias collision rows |
| Do outputs match claimed estimand? | Estimand fidelity per variant |
| Are invalid geometries blocked? | Geometry + `unsupported_geometry_not_blocked` |
| What must be fixed before OC? | Gap register → Layer 4 |

**Not answered here:** primary/secondary/directional roles · production readiness · TrustReport eligibility.

---

## 2. Relationship to METHOD_VALIDATION_PROGRAM_001

| Program layer | Status |
|---------------|--------|
| Layer 1 — Code inventory | ✅ |
| Layer 2 — Literature alignment | ✅ |
| **Layer 3 — Implementation validation** | ✅ **This artifact** |
| Layer 4 — Statistical validation protocol | **Next** |
| Layer 5 — Combination matrix | Blocked until Layer 4 per family |

---

## 3. Inputs from Layer 1 and Layer 2

- **Layer 1:** 44 inventory items — canonical names, modules, `inventory_status`  
- **Layer 2:** 24 literature families — `repo_alignment_status`, Layer 3/4 question lists  

**Coverage rule:** Every Layer 2 `family_id` has ≥1 Layer 3 row (`coverage.missing_layer2_family_ids` must be empty). Two orchestration rows (`ORCH-001`, `ORCH-002`) extend coverage beyond literature families.

---

## 4. Validation method

| Step | Action |
|------|--------|
| 1 | Load Layer 1 + Layer 2 JSON |
| 2 | Inspect `panel_exp/design/`, `methods/`, `inference/`, `impact.py` (read-only) |
| 3 | Reconcile prior audit IDs (D1, G1–G8, F-GEO, F-INF, COMBO) |
| 4 | Score eight dimensions per row (identity, estimand, geometry, design, estimator, inference, orchestration, audits) |
| 5 | Assign `implementation_validation_status` from allowed enum |
| 6 | Emit JSON; `promotion_allowed` and `trust_role_allowed` always **false** |

**Code inspection hooks (examples):**

- `geo_runner.py` sets `pre_treatment_period` when `train_length > 0`  
- `greedy_match_markets` slices `wide` when `pre_treatment_period` is passed  
- `SyntheticControlCVXPY` docstring: penalty **not used in OSQP solve** (G1)  
- `TBR` asserts pre-aggregated 1×1 geometry  
- `Rerandomization` balances on pre-period slice when provided  

---

## 5. Design implementation validation

| family_id | implementation | status | Key finding |
|-----------|----------------|--------|-------------|
| DES-GMM-001 | greedy_match_markets | `implementation_validated_with_caveats` | geo_runner passes pre-period when `train_length` set; direct `assign()` without period still risks INV-D1-001 |
| DES-RERAND-001 | rerandomization_wrapper | `implementation_validated_with_caveats` | Not in `list_names()`; imbalance uses pre-period slice |
| DES-TIER1-RAND-001 | tier-1 randomizers | `implementation_validated_with_caveats` | geo-run OK; design–readout story ≠ matched markets |
| DES-SUPERGEO-001 | supergeos | `unsupported_geometry_not_blocked` | `geo_run_supported=False` but flat SCM+JK invalid without bridge (F-GEO-003) |
| DES-TRIM-001 | trimmedmatch | `unsupported_geometry_not_blocked` | Pair geometry; F-GEO-004 bridge missing |
| DES-LEGACY-BLOCK-001 | quickblock/matchedpair | `deprecated_or_quarantine_candidate` | Not geo-run |

---

## 6. Estimator implementation validation

| family_id | variants | status | Key gaps |
|-----------|----------|--------|----------|
| EST-SCM-001 | SyntheticControlCVXPY, SyntheticControl, legacy fn | CVXPY: `with_caveats`; scipy: `gap`; legacy: `quarantine` | SCM alias collision; G4 OSQP objective; `full_model` leakage |
| EST-AUGSYNTH-001 | AugSynthCVXPY, AugSynth | CVXPY: `gap`; non-CVXPY: `research_only` | G1 penalty unused on OSQP; G4/G7/G8; JK/Conformal blocked |
| EST-TBR-001 | TBR | `with_caveats` | Aggregate asserts present; TBR vs TBRRidge naming collision |
| EST-TBRRIDGE-001 | TBRRidge | `gap` | JK/JKP null FPR; POW-EST-001 agg2 vs unit |
| EST-DID-001 | DID | `with_caveats` | Embedded bootstrap ≠ registry BRB |
| EST-SDID-001 | SyntheticDID | `research_only_not_validated` | Runner skip |
| EST-RESEARCH-* | BayesianTBR, TROP, MTGP | `research_only` / `quarantine` | INV-015 Bayesian registry mismatch |

---

## 7. Inference implementation validation

| family_id | mode | status | Key gaps |
|-----------|------|--------|----------|
| INF-POINT-001 | point_estimate | `implementation_validated` | Diagnostic only |
| INF-JK-001 | UnitJackKnife | `implementation_gap` | TBRRidge FPR; AugSynth strata; aggregate misuse |
| INF-JKP-001 | JKP | `implementation_gap` | Pooled-CF on TBRRidge |
| INF-KFOLD-001 | Kfold | `with_caveats` | Diagnostic extension |
| INF-TSKFOLD-001 | TimeSeriesKfold | `with_caveats` | POSTFIX orientation — re-verify exports |
| INF-BRB-001 | BlockResidualBootstrap | `with_caveats` | Not generic “Bootstrap”; DEF-002 ordering |
| INF-CONFORMAL-001 | Conformal | `implementation_gap` | IMPL-CONF-001; AugSynth blocked |
| INF-PLACEBO-001 | Placebo | `with_caveats` | Falsification only; inference not estimator |
| INF-BAYES-REG-001 | Bayesian | `architecture_gap` | Registry handler ≠ BayesianTBR MCMC |
| INF-DID-BOOT-001 | DID_native_bootstrap | `with_caveats` | Not in inference registry |

---

## 8. Orchestration / registry / alias validation

| row | finding |
|-----|---------|
| **ORCH-001 GeoExperimentDesign** | `with_caveats` — train_length → pre_period in geo_runner; POW-EST-001 power vs analysis estimator mismatch |
| **ORCH-002 ImpactAnalyzer** | `architecture_gap` — central dispatch; invalid combos should be explicit (COMBO-001) |
| **Registry** | SCM catalog name maps to multiple classes (`identity_collision`) |
| **Design registry** | `list_names()` omits rerandomization wrapper name |
| **Bootstrap naming** | BRB registry vs DID embedded bootstrap — distinct paths |

---

## 9. Known issue reconciliation

| Audit ID | Topic | Layer 3 status |
|----------|-------|----------------|
| **INV-D1-001** | Pre-period matching leakage | **Mitigated** on geo_runner path when `train_length>0`; **residual risk** on direct assign |
| **G1** | AugSynth penalty unused OSQP | **Confirmed** in `scm.py` docstring |
| **G4** | SCM pre-RMSE / OSQP leg | **Open** — `implementation_gap` AugSynthCVXPY |
| **G7** | Level vs relative summary | **Open** — estimand export review |
| **G8** | Hull diagnostic proxy | **Open** — diagnostic metadata |
| **IMPL-CONF-001** | Conformal band mismatch | **Open** — AugSynth+Conformal blocked |
| **GAP-TBR-TBRR-001** | TBR vs TBRRidge collision | **identity_collision** rows |
| **INV-D2-001** | `full_model` leakage | **Open** SCM paths |
| **INV-015** | Bayesian registry ≠ MCMC | **architecture_gap** |
| **F-GEO-003/004** | supergeo/trim bridges | **unsupported_geometry_not_blocked** |
| **POW-EST-001** | Power TBRRidge agg2 vs SCM+JK | **orchestration** gap |
| **F-INF-003** | Interval orientation | **TS-Kfold/Conformal** — POSTFIX applied; re-verify |
| **IMPL-JK-001** | AugSynth+JK unsafe strata | **implementation_gap** |

Full list: JSON `known_gap_register`.

---

## 10. Implementation gap register

Rows with `implementation_validation_status` = **`implementation_gap`** (fix before Layer 4 on that path):

- SyntheticControl (scipy) — parity vs CVXPY  
- AugSynthCVXPY — G1/G4/G7/G8  
- TBRRidge — JK/JKP pivots  
- UnitJackKnife, JKP, Conformal — semantics / pairing  
- SyntheticControl legacy path — quarantine  

---

## 11. Architecture gap register

| Status | Rows |
|--------|------|
| `architecture_gap` | ImpactAnalyzer dispatch; registry Bayesian handler |
| `unsupported_geometry_not_blocked` | supergeos, trimmedmatch (registry blocks geo-run but combo invalid if forced) |
| `identity_collision` | SCM alias; TBR/TBRRidge product naming |

---

## 12. Quarantine / deprecation candidates

| implementation | status |
|----------------|--------|
| synthetic_control() | `deprecated_or_quarantine_candidate` |
| quickblock, matchedpair | `deprecated_or_quarantine_candidate` |
| AugSynth (non-CVXPY) | `research_only_not_validated` |
| TROP, MTGP | `research_only_not_validated` |

---

## 13. Items ready for Layer 4 statistical validation

Families with `implementation_validated` or `implementation_validated_with_caveats` **and** no blocking geometry gap:

- tier-1 designs + greedy_match_markets (with INV-D1 caller audit)  
- point_estimate  
- TBR aggregate (geometry enforced)  
- Placebo (SCM, single-treated scope)  
- BlockResidualBootstrap on TBRRidge (DEF-002 verified)  
- DID embedded bootstrap (relative CI policy still open)  

Layer 4 still required — Layer 3 is **not** statistical proof.

---

## 14. Items blocked before Layer 4

| Blocker | Families |
|---------|----------|
| Geometry bridge | supergeos, trimmedmatch |
| Fidelity G1–G8 | AugSynthCVXPY |
| Conformal redesign | AugSynth+Conformal |
| JK calibration | AugSynth+JK, TBRRidge+JK/JKP |
| Research fidelity | SyntheticDID, TROP, MTGP, BayesianTBR |
| Registry Bayesian misuse | TBRRidge+Bayesian |

---

## 15. Next artifact: METHOD_STATISTICAL_VALIDATION_PROTOCOL_001

**Layer 4** defines synthetic worlds, metrics, and OC archives per family where Layer 3 status is not `implementation_gap` / `architecture_gap` / blocked geometry.

**Inputs:** This register · Layer 2 statistical_validation_needed lists · existing D5 JSON archives (reconcile, do not copy trust roles).

---

## 16. Guardrails

- **No** primary / secondary / directional labels  
- **No** promotion (`promotion_allowed: false` on every JSON row)  
- **No** estimator, inference, or design behavior change in this PR  
- **No** OC execution  
- **No** TrustReport / F-DECISION / CalibrationSignal / MMM / LLM change  
- Prior audits inform **gaps**, not automatic pass/fail without code check  

---

## 17. Stop condition

| Criterion | Status |
|-----------|--------|
| Layer 2 family coverage | ✅ 24/24 |
| Code-informed rows | ✅ 29 rows |
| Known gap register | ✅ 13 IDs |
| Layer 4 ready/blocked lists | ✅ §13–§14 |
| JSON + tests | ✅ |
| Roadmap updates | ✅ |

---

*METHOD-IMPLEMENTATION-VALIDATION-001 v1.0.0 — Layer 3 complete; Layer 4 statistical validation protocol is next.*
