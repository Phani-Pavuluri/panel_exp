#!/usr/bin/env python3
"""Regenerate tests/fixtures/inference_golden/*.npz baselines."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from panel_exp.methods.scm import SyntheticControl
from panel_exp.methods.tbr import TBRRidge
from tests.inference_registry_helpers import make_scm_panel, make_tbr_panel

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "inference_golden"

MODE_CHOICES = (
    "point_estimate",
    "UnitJackKnife",
    "JKP",
    "Kfold",
    "Conformal",
    "BlockResidualBootstrap",
    "TimeSeriesKfold",
    "Placebo",
    "Bayesian",
)


def _save(mode: str, results: dict, keys: tuple[str, ...]) -> None:
    payload = {k: np.asarray(results[k], dtype=float) for k in keys if k in results}
    path = OUT / f"{mode}.npz"
    np.savez_compressed(path, **payload)
    print(f"wrote {path.name}: {sorted(payload)}")


def _regenerate_point_estimate() -> None:
    est = TBRRidge(inference=None, alpha=0.05)
    est.run_analysis(make_tbr_panel(seed=42))
    _save("point_estimate", est.results, ("y_hat",))


def _regenerate_unit_jackknife() -> None:
    est = TBRRidge(inference="UnitJackKnife", alpha=0.05)
    est.run_analysis(make_tbr_panel(seed=42))
    _save("UnitJackKnife", est.results, ("y_hat", "y_lower", "y_upper"))


def _regenerate_jkp() -> None:
    est = TBRRidge(inference="JKP", alpha=0.05)
    est.run_analysis(make_tbr_panel(seed=42, n_time=35, treat_start=20))
    _save("JKP", est.results, ("y_hat", "y_lower", "y_upper"))


def _regenerate_kfold() -> None:
    est = TBRRidge(inference="Kfold", alpha=0.05)
    est.run_analysis(make_tbr_panel(seed=42))
    _save("Kfold", est.results, ("y_hat", "y_lower", "y_upper"))


def _regenerate_conformal() -> None:
    est = TBRRidge(inference="Conformal", alpha=0.05)
    est.run_analysis(make_tbr_panel(seed=42))
    _save("Conformal", est.results, ("y_hat", "y_lower", "y_upper"))


def _regenerate_block_residual_bootstrap() -> None:
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


def _regenerate_timeseries_kfold() -> None:
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


def _regenerate_placebo() -> None:
    est = SyntheticControl(inference="Placebo", alpha=0.05)
    est.run_analysis(make_scm_panel(seed=42, n_ctrl=6))
    _save(
        "Placebo",
        est.results,
        ("y_hat", "y_lower", "y_upper", "effect_ci_lower_inversion", "effect_ci_upper_inversion"),
    )


def _regenerate_bayesian() -> None:
    try:
        import jax  # noqa: F401
    except ImportError:
        print("skip Bayesian (jax not installed)")
        return

    est = TBRRidge(inference="Bayesian", alpha=0.05)
    est.run_analysis(make_tbr_panel(seed=99))
    _save("Bayesian", est.results, ("y_hat", "y_lower", "y_upper"))


_REGENERATORS = {
    "point_estimate": _regenerate_point_estimate,
    "UnitJackKnife": _regenerate_unit_jackknife,
    "JKP": _regenerate_jkp,
    "Kfold": _regenerate_kfold,
    "Conformal": _regenerate_conformal,
    "BlockResidualBootstrap": _regenerate_block_residual_bootstrap,
    "TimeSeriesKfold": _regenerate_timeseries_kfold,
    "Placebo": _regenerate_placebo,
    "Bayesian": _regenerate_bayesian,
}

_DEFAULT_ORDER = (
    "point_estimate",
    "UnitJackKnife",
    "JKP",
    "Kfold",
    "Conformal",
    "BlockResidualBootstrap",
    "TimeSeriesKfold",
    "Placebo",
    "Bayesian",
)


def main(modes: tuple[str, ...] | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    selected = modes if modes is not None else _DEFAULT_ORDER
    for mode in selected:
        _REGENERATORS[mode]()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=MODE_CHOICES,
        default=None,
        help="Regenerate a single fixture; default regenerates all modes.",
    )
    args = parser.parse_args()
    main((args.mode,) if args.mode is not None else None)
