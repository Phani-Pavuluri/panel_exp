#!/usr/bin/env python3
"""
End-to-end decision workflow example (design → experiment card).

Demonstrates additive, non-blocking validation and readiness artifacts.
Run: poetry run python examples/decision_workflow_example.py
"""

from __future__ import annotations

from typing import Any, Dict, List

from panel_exp.artifacts.experiment_card import build_experiment_card
from panel_exp.design.validation import ValidationCheck, ValidationStatus
from panel_exp.evidence import DesignEvidence
from panel_exp.method_metadata import merge_maturity_into_results
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.policy.readiness import attach_readiness_assessment, build_readiness_assessment
from panel_exp.spec import InterferenceAssumption, spec_from_geo_design
from panel_exp.validation.calibration_report import attach_calibration_report, build_calibration_report
from panel_exp.validation.maturity_evidence import attach_maturity_evidence, build_maturity_evidence
from panel_exp.validation.recovery_runner import RecoveryRunner

# Lightweight synthetic panel (fixed seed for reproducibility).
import numpy as np
import pandas as pd


def _make_panel(seed: int = 0) -> PanelDataset:
    rng = np.random.default_rng(seed)
    n_time, treat_start = 24, 18
    y = np.linspace(1000, 1200, n_time) + rng.normal(0, 25, n_time)
    rows = [y]
    geos = ["treated"]
    for i in range(4):
        rows.append(
            np.linspace(800 + 50 * i, 960 + 50 * i, n_time) + rng.normal(0, 20, n_time)
        )
        geos.append(f"ctrl_{i}")
    wide = pd.DataFrame(np.vstack(rows), index=geos, columns=range(n_time))
    return PanelDataset(wide, [TimePeriod(treat_start, None)], ["treated"])


def _validation_summary() -> Dict[str, Any]:
    check = ValidationCheck(
        metric="interference_assumption",
        status=ValidationStatus.PASS,
        threshold=None,
        value=None,
        message="No interference declared for this design.",
        blocking=False,
    )
    return {"status": "PASS", "blocking_failures": [], "checks": [check.to_dict()]}


def run_decision_workflow(*, seed: int = 0) -> Dict[str, Any]:
    """
    Run the full advisory workflow and return artifact payloads.

    Does not block execution or change estimator outputs.
    """
    panel = _make_panel(seed=seed)
    assignment = {"control": ["ctrl_0", "ctrl_1", "ctrl_2", "ctrl_3"], "test_0": ["treated"]}
    spec = spec_from_geo_design(
        "decision-workflow-demo",
        "y",
        "geo",
        "period",
        TimePeriod(0, 18),
        TimePeriod(18, 24),
        "balancedrandomization",
        random_state=seed,
        interference=InterferenceAssumption.NO_INTERFERENCE,
        estimator="TBRRidge",
    )

    # Estimator + inference (point estimate for speed).
    estimator = TBRRidge(inference=None, alpha=0.05)
    estimator.run_analysis(panel)
    merge_maturity_into_results(estimator.results, estimator, "point_estimate")

    # Recovery validation (diagnostic; small Monte Carlo budget).
    recovery_outputs: List[Dict[str, Any]] = [
        RecoveryRunner(
            "DID",
            "recovery_null_effect",
            n_simulations=1,
            random_state=seed,
        ).run(),
        RecoveryRunner(
            "DID",
            "recovery_positive_effect",
            n_simulations=1,
            random_state=seed + 1,
        ).run(),
    ]

    calibration_report = build_calibration_report(
        recovery_outputs=recovery_outputs,
        estimator="DID",
    )
    maturity_evidence = build_maturity_evidence(
        "TBRRidge",
        estimator.estimator_metadata,
        calibration_report=calibration_report,
        recovery_outputs=recovery_outputs,
    )
    readiness = build_readiness_assessment(
        inference_metadata=estimator.results.get("inference_metadata"),
        validation_summary=_validation_summary(),
        calibration_report=calibration_report,
        maturity_evidence=maturity_evidence,
        interference_assumption="no_interference",
    )

    artifacts: Dict[str, Any] = {}
    attach_calibration_report(artifacts, calibration_report)
    attach_maturity_evidence(artifacts, maturity_evidence)
    attach_readiness_assessment(artifacts, readiness)

    evidence = DesignEvidence.from_assignment(
        spec,
        assignment,
        validation_summary=_validation_summary(),
        inference_metadata=dict(estimator.results.get("inference_metadata") or {}),
        artifacts=artifacts,
        created_at="2026-05-20T12:00:00+00:00",
    )
    card = build_experiment_card(evidence)
    markdown = card.to_markdown()

    return {
        "calibration_report": calibration_report.to_dict(),
        "maturity_evidence": maturity_evidence.to_dict(),
        "readiness_assessment": readiness.to_dict(),
        "card_markdown": markdown,
    }


def main() -> None:
    result = run_decision_workflow()
    print(result["card_markdown"])
    print("\n--- readiness status ---")
    print(result["readiness_assessment"]["status"])


if __name__ == "__main__":
    main()
