# D5-DES-STAT-GREEDY-FEASIBILITY-001 Report

**Verdict:** `greedy_feasibility_fixed_requires_statistical_followup` · **Selected policy:** `control_reservation`

## 1. Executive summary

Diagnosed DES-001 greedy_match_markets treatment-pool exhaustion and insufficient control counts at tp≈0.35. Implemented control-reservation feasibility policy with explicit metadata. **No promotion; downstream blocked.**

## 2. Prior failure evidence

- Tier-1 legacy control-floor violations: 836
- tp=0.35 legacy violations: 171

## 3. Current greedy algorithm

Volume-share constrained greedy matching; score-improvement-only assignment; unassigned units left out of control in legacy mode.

## 4. Root-cause analysis

| Hypothesis | Evidence | Reproduced? | Root cause? | Fix implication |
|---|---|---|---|---|
| Volume share vs unit count mismatch | tp=0.35 met by few high-volume treated units | Yes | Yes | Unit-count feasibility preflight |
| Greedy score gate leaves units unassigned | 6/10 unassigned at seed 101 legacy | Yes | Yes | Post-sweep + control reservation |
| No min-control floor | n_control=1 with min threshold 3 | Yes | Yes | min_control_units enforcement |
| Retry solves structural issue | retries=0 in tier-1 | Yes | No | Preflight/cap/reservation |

## 5. Feasibility contract

See `panel_exp/design/greedy_feasibility.py`: n_eligible, requested_n_treated, max_feasible_n_treated, min_control_units, explicit adjustment metadata.

## 6. Candidate policies

- **A_legacy** (`legacy`): Current behavior baseline
- **B_preflight_fail** (`preflight_fail`): Reject infeasible before matching
- **C_feasibility_cap** (`feasibility_cap`): Cap treated count with metadata
- **D_control_reservation** (`control_reservation`): Reserve min control pool

## 7. Worlds and configuration

Worlds: 10 · Seeds: [101, 202, 303, 404, 505] · Replicates: 3

## 8. Metrics

Feasibility, balance/SMD, match quality, contract/guardrail metadata.

## 9. Runtime and run counts

- Attempted: 12000
- Completed: 11940
- Failed: 60
- Elapsed: 285.876s

## 10. Baseline results

Legacy: success 99.50%, control-floor violations 28.01%

## 11. Preflight failure results

B_preflight_fail: success 99.50%, violations 0.00%, adjustment rate 58.12%

## 12. Feasibility-cap results

C_feasibility_cap: success 99.50%, violations 0.00%, adjustment rate 56.45%

## 13. Control-reservation results

D_control_reservation: success 99.50%, violations 0.00%, adjustment rate 58.12%

## 14. tp=0.35 findings

Legacy violations: 171; Fixed violations: 0

## 15. Small-N findings

small_n_control_scarcity and n_units=8 stress minimum control preservation.

## 16. Weak-donor findings

weak_donor_pool with exclusions reduces eligible pool; preflight_fail rejects early.

## 17. Balance tradeoffs

Control reservation may increase control count vs legacy; SMD changes tracked in comparisons.

## 18. Treatment-share fidelity

Requested vs realized tp recorded; adjustments flagged in metadata.

## 19. Retry behavior

Structural issue; retries do not fix without feasibility policy.

## 20. Contract/guardrail behavior

Contract emits; guardrail WARN; downstream blocked; contract_complete_allowed=False.

## 21. Selected fix

**control_reservation** — preflight bounds, test-assignment cap, unassigned sweep to control, explicit feasibility metadata.

## 22. Implementation changes

- `panel_exp/design/greedy_feasibility.py` (new)
- `panel_exp/design/assign.py` — greedy_match_markets feasibility policies

## 23. Regression risks

Default policy changes assignment vs legacy; use `feasibility_policy='legacy'` for baseline.

## 24. Suitability implications

Feasibility improved; statistical suitability still blocked; 0 downstream authorized.

## 25. Remaining limitations

Volume-share vs unit-count tension remains; poor-match worlds still high SMD.

## 26. Follow-up work

- Re-run tier-1 DES-001 subset with fixed policy
- D5-DES-STAT-STRATIFIED-001

## 27. Governance verdict

**greedy_feasibility_fixed_requires_statistical_followup** — no production promotion.
