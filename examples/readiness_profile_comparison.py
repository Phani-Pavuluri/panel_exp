#!/usr/bin/env python3
"""
Compare readiness assessments under exploratory, standard, and strict profiles.

Uses mocked evidence inputs (no estimator fit) so the same signals are evaluated
under each profile. Advisory only; does not block runs.

Run: poetry run python examples/readiness_profile_comparison.py
"""

from __future__ import annotations

from typing import Any, Dict, List

from panel_exp.policy.readiness import ReadinessProfile, build_readiness_assessment
from panel_exp.validation.calibration_report import CalibrationReport


def _borderline_inputs() -> Dict[str, Any]:
    """Shared inputs where profiles diverge on calibration strictness."""
    return {
        "inference_metadata": {
            "estimator_maturity": "expert_review",
            "inference_mode_maturity": "expert_review",
            "intervals_available": True,
            "path_interval_type": "confidence_interval",
        },
        "validation_summary": {"status": "PASS", "blocking_failures": [], "checks": []},
        "calibration_report": CalibrationReport(
            false_positive_rate=0.08,
            coverage_under_null=0.92,
            power=0.85,
            recovery_success_rate=0.92,
        ),
        "interference_assumption": "no_interference",
    }


def compare_readiness_profiles(
    inputs: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """
    Evaluate the same readiness inputs under all three profiles.

    Returns one summary dict per profile (does not mutate ``inputs``).
    """
    base = dict(inputs or _borderline_inputs())
    inference_metadata = dict(base.get("inference_metadata") or {})
    validation_summary = (
        dict(base["validation_summary"])
        if base.get("validation_summary") is not None
        else None
    )
    calibration_report = base.get("calibration_report")
    maturity_evidence = base.get("maturity_evidence")
    evidence_warnings = base.get("evidence_warnings")
    evidence_errors = base.get("evidence_errors")
    interference_assumption = base.get("interference_assumption")

    summaries: List[Dict[str, Any]] = []
    for profile in (
        ReadinessProfile.EXPLORATORY,
        ReadinessProfile.STANDARD,
        ReadinessProfile.STRICT,
    ):
        assessment = build_readiness_assessment(
            inference_metadata=inference_metadata,
            validation_summary=validation_summary,
            calibration_report=calibration_report,
            maturity_evidence=maturity_evidence,
            evidence_warnings=evidence_warnings,
            evidence_errors=evidence_errors,
            interference_assumption=interference_assumption,
            profile=profile,
        )
        summaries.append(
            {
                "profile": assessment.profile_name,
                "status": assessment.status.value,
                "reasons": list(assessment.reasons),
                "recommended_actions": list(assessment.recommended_actions),
            }
        )
    return summaries


def _print_comparison(summaries: List[Dict[str, Any]]) -> None:
    print("Readiness profile comparison (same evidence inputs)\n")
    print("> Advisory only. Profiles do not block execution or prove causal truth.\n")
    for row in summaries:
        print(f"--- profile: {row['profile']} ---")
        print(f"status: {row['status']}")
        print("reasons:")
        for reason in row["reasons"]:
            print(f"  - {reason}")
        print("recommended_actions:")
        for action in row["recommended_actions"]:
            print(f"  - {action}")
        print()


def main() -> None:
    summaries = compare_readiness_profiles()
    _print_comparison(summaries)


if __name__ == "__main__":
    main()
