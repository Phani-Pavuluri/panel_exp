"""Review workflow helpers — diagnostics separate from core ``run_analysis`` outputs."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from panel_exp.diagnostics.estimator_diagnostics import (
    attach_estimator_diagnostics,
    collect_estimator_diagnostics,
)

DIAGNOSTICS_VERSION = "1.0"


def build_estimator_review(
    estimator: Any,
    results: Optional[Mapping[str, Any]] = None,
    *,
    attach: bool = False,
) -> Dict[str, Any]:
    """
  Build a review payload from a fitted estimator without mutating core results by default.

  Parameters
  ----------
  estimator :
      Fitted analyzer (e.g. after ``run_analysis``).
  results :
      Optional results mapping; defaults to ``estimator.results`` when present.
  attach :
      When True, write ``estimator_diagnostics`` onto ``results`` (same dict object passed
      or resolved from the estimator).

  Returns
  -------
  dict
      ``{"estimator_diagnostics": ..., "diagnostics_version": "1.0"}``
  """
    resolved = results
    if resolved is None:
        resolved = getattr(estimator, "results", None)
    if resolved is None:
        raise ValueError(
            "build_estimator_review requires results or an estimator with .results "
            "after run_analysis."
        )

    diagnostics = collect_estimator_diagnostics(estimator, resolved)
    review: Dict[str, Any] = {
        "estimator_diagnostics": diagnostics,
        "diagnostics_version": DIAGNOSTICS_VERSION,
    }
    if attach:
        attach_estimator_diagnostics(resolved, diagnostics)
    return review
