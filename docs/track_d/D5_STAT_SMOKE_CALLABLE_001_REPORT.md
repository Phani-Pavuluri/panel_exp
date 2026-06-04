# D5-STAT-SMOKE-CALLABLE-001 Report

**Artifact ID:** D5-STAT-SMOKE-CALLABLE-001
**Type:** Smoke / schema / callability / orientation / guard battery
**Overall verdict:** `smoke_pass_with_caveats`

## 1. Purpose

First evidence-execution step after the suitability framework. Verifies callable
paths on tiny deterministic fixtures and records expected-blocked combinations
without executing them.

## 2. Relationship to suitability framework

Inputs from `DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001` — OC-ready does
**not** imply suitable or statistically validated.

## 13. Results summary

- Total rows: 30
- Executed: 11
- Expected blocked: 16
- Skipped (no probe): 3
- Failures: 0
- Callable pass: 11

## 14. Overall verdict

`smoke_pass_with_caveats`

## 15. Follow-up actions

**D5-STAT-SCM-JK-001:** ✅ Level B characterization complete — see [`D5_STAT_SCM_JK_001_REPORT.md`](D5_STAT_SCM_JK_001_REPORT.md).

**D5-STAT-AUGSYNTH-POINT-001:** ✅ Level B point characterization complete — see [`D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](D5_STAT_AUGSYNTH_POINT_001_REPORT.md).

TBR aggregate Level B: ✅ **D5-STAT-TBR-AGG-001** (`characterization_mixed_requires_followup`). Next recommended: **D5-STAT-DID-BOOTSTRAP-001** per Layer 5 queue.

## 16. What this artifact does not authorize

- Statistical validation · suitability · promotion · TrustReport roles
- CalibrationSignal · MMM · LLM recommendations

## 17. Guardrails

Smoke-pass does not mean validated or suitable.

