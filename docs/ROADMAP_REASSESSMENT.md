# panel_exp roadmap reassessment

**Status:** living document  
**Last reviewed:** 2026-05-20  

**Source:**

- `geox_agent_audit_template.md` (audit dimensions; template not present in-repo at initial write)
- Package state: **v0.2.1**
- Full suite status: **474 passed, 1 skipped** (`poetry run pytest tests/ -q`)

**Repo state:** branch `estimator-maturity-metadata` (post-merge with `main`).

---

## How to use this document

**Purpose:**

- Guide roadmap prioritization
- Identify overengineering risk
- Track remaining causal/statistical gaps
- Prevent feature work from outrunning validation

**Rules:**

- Update after major architecture changes
- Update after estimator additions
- Update after validation coverage changes (see `docs/VALIDATION_COVERAGE.md`)
- Update after maturity promotions

**Audit basis:** Geo-experiment package review (algorithm validity, artifact/policy layers, causal gaps, maturity, power/MDE, interference). This report follows the audit dimensions requested in the reassessment task.

---

## 1. Current verdict

**panel_exp is a credible geo-experimentation toolkit for design, estimation, and uncertainty—with strong operational discipline—but it is not yet a self-certifying causal inference product.**

The package is best positioned as:

- **Strong** for geo design orchestration, explicit experiment contracts (`DesignSpec` / evidence hashes), inference-mode semantics, and conservative “readiness” reporting.
- **Adequate** for SCM / ridge-TBR / pooled-DID workflows when used with expert review and documented assumptions.
- **Immature** for production go/no-go automation, spillover-aware causal claims, and estimators that depend on heavy optional stacks (Bayesian MCMC, SDID, TROP).

Recent work (maturity metadata, recovery/calibration readouts, experiment cards, readiness profiles, run bundles, schema contracts) **improves auditability and reviewer ergonomics** without changing core estimators. That is the right separation—but it increases surface area that must be kept coherent.

**Bottom line:** Continue as an internal/expert-review platform. Do not market automated decision-ready outputs until validation breadth, interference handling, and power semantics are clearer to end users.

---

## 2. What is now strong

### Algorithm and inference discipline (unchanged math, clearer contracts)

- **Explicit interval semantics** (`panel_exp/inference_result.py`, `panel_exp/inference/uncertainty.md`): confidence vs credible vs conformal vs placebo bands vs unavailable—reduces misinterpretation of `y_lower` / `y_upper`.
- **Inference registry equivalence tests** and golden fixtures: regression protection for legacy `results` key shapes across modes.
- **Core estimators remain implemented with tests:** SCM (incl. CVXPY path), TBRRidge, DID, SDID, TROP—each with targeted test modules; CVXPY/OSQP guarded by optional-dep helpers.
- **Counterfactual stability utilities** (`panel_exp/utils/counterfactual_stability_tests.py`): donor/weight diagnostics for SCM-family fits (non-fatal, appropriate for review workflows).

### Design and experiment setup

- **Geo experiment orchestration** with business constraints (whitelist/blacklist, rerandomization, power integration) via `GeoExperimentDesign`.
- **Assignment hardening** and registry-based design dispatch; clear split between geo-run-supported vs registered-only designs (README “code truth”).
- **Post-assignment validation gates** (`panel_exp/design/validation.py`): blocking failures vs warnings; interference assumption surfaced at design time.

### Evidence, maturity, and validation infrastructure

- **Immutable evidence model** with deterministic hashes (`panel_exp/evidence.py`, `evidence_hash.py`): `spec_hash`, `assignment_hash`, structure fingerprint—suitable for audit trails.
- **Conservative maturity catalog** (`panel_exp/method_metadata.py`): **no** `production_safe` ratings; smoke/recovery explicitly insufficient for promotion (`tests/test_estimator_maturity.py`).
- **Measured maturity evidence** (`validation/maturity_evidence.py`) **does not** auto-upgrade catalog labels—correct policy.
- **Synthetic validation stack** isolated from production imports (`tests/test_validation_production_isolation.py`).
- **Recovery runner + calibration report** provide reproducible null/lift diagnostics (FPR, coverage, power on positive scenarios) without blocking runs.

### Artifact / policy layers (recent)

- **Experiment card** (`artifacts/experiment_card.py`): human-readable synthesis of design, inference maturity, validation metadata, optional calibration/readiness blocks.
- **Readiness assessment** (`policy/readiness.py`): advisory, profile-based (exploratory / standard / strict), non-blocking—aligns with expert-review culture.
- **Run artifact bundle** (`artifacts/run_bundle.py`): portable JSON export for reviewers/archival—opt-in, does not alter `results`.
- **Schema compatibility contracts** (`tests/fixtures/artifact_schemas/`, `tests/test_artifact_schema_compatibility.py`): guards accidental breaking changes to export shapes.
- **Documentation of decision workflow** (README, `gh-pages/_sources/user_guide.md.txt`) and runnable examples (`examples/decision_workflow_example.py`, `readiness_profile_comparison.py`).

### Power / MDE honesty

- **Simulation-based MDE** with documented semantics (`MDE_SEMANTICS` in `panel_exp/design/power.py`): `classical_power: False`, `planning_use: ranking_and_sensitivity_only`.
- **A/A calibration helper** on null simulation rows (`evaluate_aa_calibration`)—diagnostic FPR/coverage, not a gate.

---

## 3. What remains weak

### Causal / statistical gaps

| Gap | Detail |
|-----|--------|
| **Estimand ambiguity** | `uncertainty.md` still lists open questions (single vs multiple treated, staggered adoption, target estimand). Package does not enforce a single ATT definition across estimators. |
| **Incomplete validation coverage** | `EstimatorValidationRunner` **skips** TROP, Bayesian, MTGP, SDID (`SKIPPED_ESTIMATORS` in `validation/runner.py`). Recovery battery extends DID/TBR/TBRRidge/TROP wiring but TROP smoke often yields empty metrics. |
| **AugSynth / legacy paths** | `AugSynth` rated `unvalidated`; limited recovery evidence. |
| **Platform-sensitive inference** | Placebo and some SCM optimizations vary by solver/OS; fixtures document non-portable goldens (`tests/fixtures/README.md`). |
| **Bayesian path split** | Registry `Bayesian` on TBRRidge ≠ full `BayesianTBR` MCMC; easy to misuse without reading catalog rationale. |
| **SDID limitations** | Documented fixture/window issues; research-only maturity. |

### Interference and spillover

- Interference is **declared metadata only** (`InterferenceAssumption` in `spec.py`); package does **not** estimate spillovers or adjust estimands.
- `spillover_estimation_available: False` is explicit in evidence metadata—good—but users can still over-interpret `no_interference` PASS checks as empirical verification.
- Readiness `standard`/`strict` reject unknown interference; **exploratory** allows it—appropriate, but geo marketing experiments often need partial-interference workflows that are not modeled.

### Power / MDE validity (for planning)

- MDE is **not** classical minimum detectable effect; it is “smallest grid effect where simulated interval coverage drops below threshold.”
- Depends on estimator + inference + window sampling + `ci_version` heuristics—sensitive to configuration.
- Null calibration warns below 30 replications; no committed power golden fixtures.
- Parallel `n_jobs` and estimator stochasticity can complicate reproducibility unless `random_state` is set consistently.

### Maturity evidence vs catalog

- Catalog labels remain **expert_review** / **research_only** for all shipped estimators despite new recovery/calibration tooling—**intentionally conservative**, but means “maturity evidence” is explanatory, not a promotion mechanism.
- No external benchmark studies linked (GeoLift, market matching papers, etc.)—in-repo synthetic worlds are stylized.

### Documentation drift

- `gh-pages/` user guide still contains long legacy notebook flows (`pretest_analysis`, old design comparison dashboards) that **do not match** shipped wheel API.
- No `docs/` tree except this reassessment file; hosted docs may mislead relative to README “code truth.”

---

## 4. What is overbuilt or premature

These components are **not wrong**, but their **ratio of machinery to proven decision value** is high for v0.2.1.

| Layer | Assessment |
|-------|------------|
| **Readiness profiles (3) + calibration + maturity evidence + validation_metadata + experiment card + run bundle** | Useful for review packets, but **six overlapping summaries** of similar metrics (FPR, coverage, power, warnings). Risk of reviewer fatigue unless UI/tooling consumes bundles. |
| **Run artifact bundle + experiment card markdown + nested evidence JSON** | Redundant human and machine views; bundle duplicates large `evidence` subtree. Acceptable for archival export; premature as a required pipeline step. |
| **Schema snapshot suite (5 fixtures)** | Valuable CI guardrail; premature to add more versions (`v2`) until external consumers exist. |
| **Decision workflow examples (2 scripts)** | Good onboarding; premature to add more examples before stabilizing public API exports in `panel_exp.__init__` (only partial artifact exports today). |
| **Strict readiness profile** | Conceptually right for high-stakes review; **premature** as a default recommendation without empirical calibration of thresholds on real geo studies (thresholds are reasonable but arbitrary). |
| **Production-safe enum** | Exists but unused—correctly empty; keeping the enum without a promotion playbook may confuse newcomers. |

**Not overbuilt (keep):** evidence hashing, inference semantics, production isolation test, optional-dep guards, maturity catalog with no auto-promotion, simulation MDE semantics block.

---

## 5. Top 5 next PRs

Prioritized for **causal validity and reviewer trust**, not more policy surface.

### PR 1 — Validation coverage expansion (or explicit skip contract)

**Goal:** Close the gap between “13 estimators in registry” and “3–4 in automated validation.”

- Either add minimal smoke/recovery paths for **SDID** and **Bayesian** (pinned JAX) with documented skips on failure, **or** publish a single `VALIDATION_COVERAGE.md` matrix: estimator × scenario × inference × CI availability × skip reason.
- Align `RecoveryRunner` battery with `EstimatorValidationRunner` skip list.

**Why:** Maturity evidence is only credible when coverage is honest and bounded.

### PR 2 — Estimand and inference prespecification helpers

**Goal:** Reduce causal misinterpretation without changing estimator math.

- Add `ExperimentSpec` / evidence fields: `target_estimand` (e.g. `relative_att_post`), `treated_units_mode`, `inference_mode_declared`.
- Experiment card section: “Estimand & uncertainty contract.”

**Why:** Addresses top open questions in `uncertainty.md` at documentation/contract layer.

### PR 3 — Interference / spillover review packet (metadata-only)

**Goal:** Support `partial_interference` workflows without building spillover estimation.

- Design validation: require `spillover_notes` or adjacency metadata when partial interference declared.
- Readiness: optional WARN (not block) when partial declared without spillover diagnostics attached.
- Card: checklist section (contamination, holdout geos, ad saturation).

**Why:** Biggest external validity gap for geo; metadata-only scope is achievable.

### PR 4 — Power analysis user contract + null-calibration fixtures

**Goal:** Make MDE/planning defensible in reviews.

- Export `MDE_SEMANTICS` on `PowerAnalysis.summary()` / evidence artifacts.
- Document effect grid units (% vs absolute) in README/user guide (short).
- Add small committed null-simulation fixture test (≥30 reps) for `evaluate_aa_calibration` stability.

**Why:** Power is often sold as “MDE” to stakeholders; semantics must be impossible to misread.

### PR 5 — Documentation reconciliation (gh-pages vs README truth)

**Goal:** Stop dual sources of truth.

- Trim or banner legacy sections in `gh-pages/_sources/user_guide.md.txt` (pretest, stale APIs).
- Point hosted docs to README decision workflow + artifact exports.

**Why:** Prevents algorithmically fine code from being undermined by obsolete docs—not a code change, but high leverage.

---

## 6. Items to pause

Pause means **no new features** until consumers or research justify them.

| Item | Reason |
|------|--------|
| **Automated readiness gates / blocking on `NOT_READY_*`** | Culture is explicitly non-blocking; gates would fight advisory design. |
| **`production_safe` promotions** | No estimator meets stated bar; wait for external benchmarks + high replication counts. |
| **Additional artifact schema versions** | No external consumers; v1 contracts sufficient. |
| **More readiness profiles or ML-based readiness** | Three profiles cover exploration; tuning thresholds without data is noise. |
| **`panel_exp.pretest_analysis` revival** | Not shipped; duplicative of `PowerAnalysis` + design validation. |
| **Full spillover estimation module** | Research project; not a quick PR. |
| **TROP productionization** | Weak donor warnings, heavy tuning; keep research-only. |
| **BayesianTBR as default inference** | JAX pin helps CI; MCMC cost and convergence burden remain. |
| **HTML docs auto-build pipeline** | Sphinx deps exist but site is static; only invest if doc owner assigned. |
| **Auto-attach run bundles to every `run_analysis`** | Opt-in export is correct; auto-attach bloats `results` and confuses downstream ML pipelines. |
| **Jackknife+ / time Jackknife+** | Correctly deferred per `uncertainty.md`; statistical properties unclear. |

---

## 7. Algorithmic / research recommendations

### Estimation and inference

1. **Pre-register estimand per study** — Relative post-period ATT vs cumulative lift; align SCM/TBR/DID reporting to that choice in cards and evidence.
2. **Match inference mode to panel geometry** — Single treated geo → jackknife/placebo with donor-count checks; many treated → prefer aggregated paths and explicit pooling rules (DID pooled vs unit paths).
3. **Treat placebo bands as placebo bands** — Do not report them as “95% CI” in stakeholder decks; package semantics already say this—enforce in templates.
4. **SCM donor pool diagnostics before inference** — Run counterfactual stability checks when CVXPY SCM used; document donor correlation filters already in tests.
5. **SDID/TROP** — Keep research-only until staggered-timing synthetic scenarios show stable recovery across seeds (≥50 replications per scenario for any promotion discussion).

### Design and power

6. **Use power curves for ranking designs, not absolute MDE claims** — Compare designs on grid ordering and A/A FPR from `evaluate_aa_calibration`, not a single MDE point estimate.
7. **Always set `random_state`** on power and inference for audit reproducibility.
8. **Report null-replication count** alongside any FPR from power simulations.

### Validation and maturity

9. **Separate “catalog maturity” from “study-specific calibration”** — Catalog stays conservative; per-study `maturity_evidence` + `calibration_report` document this dataset’s null behavior.
10. **Increase Monte Carlo budget before stakeholder-facing readiness** — `MIN_REPLICATIONS_FOR_STABLE_CALIBRATION = 100` in calibration report is a good norm; recovery tests often use 1–5 reps (fine for CI, not for claims).

### Interference

11. **Default `InterferenceAssumption.UNKNOWN` should trigger explicit review** — Already in readiness `standard`; keep exploratory for internal R&D only.
12. **For geo lift studies, plan holdout / buffer markets in design metadata** — Even without estimation, recording buffer geos in `spillover_notes` improves auditability.

### Research backlog (outside package scope but informs roadmap)

- Benchmark against published geo lift frameworks on common panels (retail, synthetic, public datasets).
- Simulation study: coverage/FPR of placebo vs jackknife vs block bootstrap under geo correlation structures declared in `partial_interference`.
- Clarify staggered adoption path for SDID (timing heterogeneity scenarios already sketched in `synthetic_scenarios.py`—needs statistical write-up).

---

## Summary table

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Core SCM/TBR/DID algorithms | **B+** | Usable with expert review; tests exist |
| Inference semantics | **A-** | Best-in-class clarity for this repo size |
| Design / assignment | **B+** | Strong orchestration; geo-run allowlist narrow |
| Validation / recovery | **B** | Good framework; incomplete estimator coverage |
| Maturity system | **B+** | Conservative, honest; evidence additive |
| Artifact / policy layers | **B** | Useful, somewhat layered; not overblocking |
| Power / MDE | **C+** | Honest simulation semantics; easy to mis-sell |
| Spillover / interference | **D+** | Metadata only; no inference |
| Docs coherence | **C** | README good; gh-pages stale |
| Production readiness | **Expert-review tool** | Not automated decision platform |

---

*Generated as a read-only reassessment. No package code, tests, or README were modified.*
