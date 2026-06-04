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

Next recommended: **D5-STAT-SCM-JK-001**
(only if smoke passes without structural failures).

## 16. What this artifact does not authorize

- Statistical validation · suitability · promotion · TrustReport roles
- CalibrationSignal · MMM · LLM recommendations

## 17. Guardrails

Smoke-pass does not mean validated or suitable.

