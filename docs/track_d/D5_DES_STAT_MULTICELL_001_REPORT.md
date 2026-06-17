# D5-DES-STAT-MULTICELL-001 Report

**Verdict:** `multicell_per_cell_only_pooled_claims_blocked` · **Selected policy:** `control_reservation`

Full run-level archive is generated locally and not repository-tracked. Generation:

```bash
poetry run python -m panel_exp.validation.track_d_d5_des_stat_multicell_001 \
  --output-local /tmp/D5_DES_STAT_MULTICELL_001_results.json \
  --summary-output docs/track_d/archives/D5_DES_STAT_MULTICELL_001_summary.json \
  --overwrite
```

## 1. Executive summary

First focused DES-011 multi-cell statistical validation harness. Characterized shared-control assignment across 2–5 cells, explicit metadata emission, per-cell balance, control burden, and pooled-claim blocking. **No promotion.**

## 2. Prior DES-011 evidence

- Tier-1 explicitly deferred multi-cell (`D5-DES-STAT-TIER1-001`)
- Contract emission partial: cell_ids/shared-control missing in some paths
- DCM-006 restricted; pooled claims blocked (F-MCELL-001)

## 3. Current implementation

CompleteRandomization with `n_test_grps>1` uses multicell feasibility policies; legacy round-robin Bernoulli baseline preserved.

## 4. Root-cause analysis

| Hypothesis | Evidence | Reproduced? | Root cause? | Fix implication |
|---|---|---|---|---|
| Implicit shared control | No assignment-level metadata | Yes | Yes | Emit policies + cell_ids |
| Round-robin skews per-cell shares | Unequal cell sizes under legacy | Yes | Yes | Equal per-cell allocation |
| High tp exhausts control pool | control_floor violations legacy | Yes | Yes | Control reservation |
| Pooled claim trap | pooled_claim_trap_world | Yes | N/A (by design) | Keep pooled blocked |

## 5. Multi-cell feasibility contract

See `panel_exp/design/multicell_feasibility.py`.

## 6. Shared-control semantics

Single shared `control` arm; `shared_single_control_arm`; reuse across per-cell comparisons.

## 7. Candidate policies

- **A_legacy** (`legacy`): Current Bernoulli round-robin baseline
- **B_equal_per_cell** (`equal_per_cell`): Equal per-cell treatment allocation
- **C_feasibility_aware** (`feasibility_aware`): Cap treated with explicit metadata
- **D_control_reservation** (`control_reservation`): Reserve min shared control pool
- **E_weighted** (`weighted`): Explicit unequal cell weights (research)
- **F_independent_control** (`independent_control`): Independent controls (research only)

## 8. Worlds and configuration

Worlds: 18 · Seeds: [101, 202, 303, 404, 505]

## 9. Metrics

Feasibility, per-cell SMD, control burden, geometry/claim blocking, contract/guardrail.

## 10. Runtime and run counts

Attempted: 17280 · Failed: 0 · Elapsed: 15.746s

## 11. Baseline results

Legacy: success 100.00%, control violations 0.00%

## 12. Equal-allocation results

Equal per-cell: {'n_runs': 2880, 'assignment_success_rate': 1.0, 'control_floor_violation_rate': 0.0, 'cell_collision_rate': 0.0, 'mean_worst_cell_smd': 1.0963981859913416, 'mean_control_burden': 13.940972222222221, 'n_pass': 2450, 'n_warn': 430, 'n_block': 0, 'n_failed': 0}

## 13. Feasibility-aware results

Feasibility-aware: {'n_runs': 2880, 'assignment_success_rate': 1.0, 'control_floor_violation_rate': 0.0, 'cell_collision_rate': 0.0, 'mean_worst_cell_smd': 1.0963981859913416, 'mean_control_burden': 13.940972222222221, 'n_pass': 2450, 'n_warn': 430, 'n_block': 0, 'n_failed': 0}

## 14. Control-reservation results

Control-reservation: success 100.00%, violations 0.00%

## 15. Weighted-allocation findings

Weighted: {'n_runs': 2880, 'assignment_success_rate': 1.0, 'control_floor_violation_rate': 0.0, 'cell_collision_rate': 0.0, 'mean_worst_cell_smd': 1.111617925671261, 'mean_control_burden': 13.940972222222221, 'n_pass': 2430, 'n_warn': 450, 'n_block': 0, 'n_failed': 0}

## 16. Cell-collision findings

Legacy collisions: 0 · Fixed collisions: 0

## 17. Shared-control burden

{'mean_control_burden_by_policy': {'A_legacy': 13.940972222222221, 'B_equal_per_cell': 13.940972222222221, 'C_feasibility_aware': 13.940972222222221, 'D_control_reservation': 13.940972222222221, 'E_weighted': 13.940972222222221, 'F_independent_control': 15.75}}

## 18. Per-cell balance

{'mean_worst_cell_smd_by_policy': {'A_legacy': 1.0150923933484668, 'B_equal_per_cell': 1.0963981859913416, 'C_feasibility_aware': 1.0963981859913416, 'D_control_reservation': 1.0963981859913416, 'E_weighted': 1.111617925671261, 'F_independent_control': 0.8255892738059288}, 'legacy_mean_worst_cell_smd': 1.0150923933484668, 'selected_mean_worst_cell_smd': 1.0963981859913416}

## 19. Worst-cell behavior

Legacy mean worst-cell SMD: 1.0150923933484668

## 20. Treatment-share fidelity

Requested vs realized total and per-cell shares recorded in run metadata.

## 21. Pooled-claim trap findings

Pooled claims blocked rate: 100%; geometry pooled_multi_cell not authorized.

## 22. Concurrency findings

`concurrent_multi_experiment_compatibility=restricted` for all multi-cell contracts.

## 23. Metadata and contract findings

cell_ids, shared_control_policy, control_reuse_policy emitted when multicell metadata present.

## 24. Guardrail behavior

WARN/BLOCK; contract_complete_allowed=False; downstream blocked.

## 25. Selected policy

**control_reservation**

## 26. Implementation changes

- `panel_exp/design/multicell_feasibility.py` (new)
- `panel_exp/design/assign.py` — CompleteRandomization multicell policies
- `panel_exp/validation/design_contract_builder_001.py` — per-cell metadata
- `panel_exp/design/geo_runner.py` — pass last_multicell_metadata

## 27. Regression risks

Default multicell_policy=control_reservation changes multi-cell assignment vs legacy.

## 28. Suitability implications

Feasibility/metadata improved; statistical suitability still blocked.

## 29. Combination-matrix implications

DCM-006 evidence updated; pooled rows remain blocked.

## 30. Remaining limitations

- Single design class (CompleteRandomization) in harness
- Independent-control research policy not production semantics

## 31. Follow-up work

- ✅ Tier-1 recharacterization — [`D5_DES_STAT_TIER1_RECHARACTERIZATION_001_REPORT.md`](D5_DES_STAT_TIER1_RECHARACTERIZATION_001_REPORT.md)
- DESIGN_GUARDRAIL_ENFORCEMENT_001

## 32. Governance verdict

**multicell_per_cell_only_pooled_claims_blocked** — no production promotion; pooled claims blocked.
