#!/usr/bin/env python3
"""Regenerate tests/fixtures/inference_golden/*.npz baselines."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from panel_exp.methods.scm import SyntheticControl
from panel_exp.methods.tbr import TBRRidge
from tests.inference_registry_helpers import make_scm_panel, make_tbr_panel

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "inference_golden"


def _save(mode: str, results: dict, keys: tuple[str, ...]) -> None:
    payload = {k: np.asarray(results[k], dtype=float) for k in keys if k in results}
    path = OUT / f"{mode}.npz"
    np.savez_compressed(path, **payload)
    print(f"wrote {path.name}: {sorted(payload)}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    est = TBRRidge(inference=None, alpha=0.05)
    est.run_analysis(make_tbr_panel(seed=42))
    _save("point_estimate", est.results, ("y_hat",))
    est = TBRRidge(inference="UnitJackKnife", alpha=0.05)
    est.run_analysis(make_tbr_panel(seed=42))
    _save("UnitJackKnife", est.results, ("y_hat", "y_lower", "y_upper"))

    est = TBRRidge(inference="JKP", alpha=0.05)
    est.run_analysis(make_tbr_panel(seed=42, n_time=35, treat_start=20))
    _save("JKP", est.results, ("y_hat", "y_lower", "y_upper"))

    for mode in ("Kfold", "Conformal"):
        est = TBRRidge(inference=mode, alpha=0.05)
        est.run_analysis(make_tbr_panel(seed=42))
        _save(mode, est.results, ("y_hat", "y_lower", "y_upper"))

    est = TBRRidge(inference="BlockResidualBootstrap", alpha=0.05)
    est.run_analysis(
        make_tbr_panel(seed=42),
        n_bootstrap=25,
        block_length=4,
        show_progress=False,
        random_state=42,
    )
    _save(
        "BlockResidualBootstrap",
        est.results,
        (
            "y_hat",
            "y_lower",
            "y_upper",
            "effect_cumulative_brb",
            "effect_ci_lower_cumulative_brb",
            "effect_ci_upper_cumulative_brb",
        ),
    )

    est = TBRRidge(inference="TimeSeriesKfold", alpha=0.05)
    est.run_analysis(make_tbr_panel(seed=42), k=3, show_progress=False, n_jobs=1)
    _save(
        "TimeSeriesKfold",
        est.results,
        (
            "y_hat",
            "y_lower",
            "y_upper",
            "effect_cumulative_tsk",
            "effect_ci_lower_cumulative_tsk",
            "effect_ci_upper_cumulative_tsk",
        ),
    )

    est = SyntheticControl(inference="Placebo", alpha=0.05)
    est.run_analysis(make_scm_panel(seed=42, n_ctrl=6))
    _save(
        "Placebo",
        est.results,
        ("y_hat", "y_lower", "y_upper", "effect_ci_lower_inversion", "effect_ci_upper_inversion"),
    )

    try:
        import jax  # noqa: F401

        est = TBRRidge(inference="Bayesian", alpha=0.05)
        est.run_analysis(make_tbr_panel(seed=99))
        _save("Bayesian", est.results, ("y_hat", "y_lower", "y_upper"))
    except ImportError:
        print("skip Bayesian (jax not installed)")


if __name__ == "__main__":
    main()
