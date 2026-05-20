"""
Estimator and inference-mode maturity metadata.

Maturity reflects validation and operational readiness, not statistical
superiority. Implemented != validated != production-safe.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Tuple


class EstimatorMaturity(str, Enum):
    """Practical readiness for use (evidence-based, not algorithm prestige)."""

    PRODUCTION_SAFE = "production_safe"
    EXPERT_REVIEW = "expert_review"
    RESEARCH_ONLY = "research_only"
    UNVALIDATED = "unvalidated"


MATURITY_DOC = (
    "Maturity reflects validation and operational readiness, not statistical "
    "superiority. Ratings are conservative and evidence-based. "
    "PRODUCTION_SAFE requires broad coverage/FPR/power validation—not smoke tests "
    "alone. Point-estimate-only inference is never production-safe for decisions."
)


@dataclass(frozen=True)
class EstimatorMetadata:
    """Readiness metadata for one registered estimator."""

    name: str
    maturity: EstimatorMaturity
    rationale: Tuple[str, ...]
    assumptions: Tuple[str, ...]
    class_name: str
    module_path: str
    synthetic_validation: bool = False
    optional_dependencies: Tuple[str, ...] = ()
    inference_support: Tuple[str, ...] = ()
    known_limitations: Tuple[str, ...] = ()

    def to_evidence_dict(self) -> Dict[str, Any]:
        return {
            "estimator_maturity": self.maturity.value,
            "estimator_assumptions": list(self.assumptions),
            "estimator_rationale": list(self.rationale),
            "estimator_synthetic_validation": self.synthetic_validation,
            "estimator_optional_dependencies": list(self.optional_dependencies),
            "estimator_known_limitations": list(self.known_limitations),
        }


@dataclass(frozen=True)
class InferenceModeMaturityMetadata:
    """Readiness metadata for a registered inference mode."""

    name: str
    maturity: EstimatorMaturity
    rationale: Tuple[str, ...]
    assumptions: Tuple[str, ...] = ()
    known_limitations: Tuple[str, ...] = ()
    optional_dependencies: Tuple[str, ...] = ()

    def to_evidence_dict(self) -> Dict[str, Any]:
        return {
            "inference_mode_maturity": self.maturity.value,
            "inference_mode_rationale": list(self.rationale),
            "inference_mode_assumptions": list(self.assumptions),
            "inference_mode_known_limitations": list(self.known_limitations),
            "inference_mode_optional_dependencies": list(self.optional_dependencies),
        }


def _est(
    name: str,
    maturity: EstimatorMaturity,
    class_name: str,
    module_path: str,
    *,
    rationale: Tuple[str, ...],
    assumptions: Tuple[str, ...],
    synthetic_validation: bool = False,
    optional_dependencies: Tuple[str, ...] = (),
    inference_support: Tuple[str, ...] = (),
    known_limitations: Tuple[str, ...] = (),
) -> EstimatorMetadata:
    return EstimatorMetadata(
        name=name,
        maturity=maturity,
        rationale=rationale,
        assumptions=assumptions,
        class_name=class_name,
        module_path=module_path,
        synthetic_validation=synthetic_validation,
        optional_dependencies=optional_dependencies,
        inference_support=inference_support,
        known_limitations=known_limitations,
    )


_ESTIMATOR_CATALOG: Tuple[EstimatorMetadata, ...] = (
    _est(
        "SCM",
        EstimatorMaturity.EXPERT_REVIEW,
        "SyntheticControl",
        "panel_exp.methods.scm",
        rationale=(
            "Synthetic recovery smoke and validation-runner configs exist.",
            "SCM optimization can fail or vary by platform; needs adequate donors.",
        ),
        assumptions=(
            "Donor pool can approximate treated unit pre-trends.",
            "Weighting scheme matches the panel structure.",
        ),
        synthetic_validation=True,
        inference_support=(
            "point_estimate",
            "UnitJackKnife",
            "JKP",
            "Bayesian",
            "BlockResidualBootstrap",
            "Conformal",
            "Kfold",
            "Placebo",
            "TimeSeriesKfold",
        ),
        known_limitations=("Requires sufficient controls; scipy optimizer sensitivity.",),
    ),
    _est(
        "AugSynth",
        EstimatorMaturity.UNVALIDATED,
        "AugSynth",
        "panel_exp.methods.scm",
        rationale=("Implemented; limited dedicated synthetic recovery evidence in-repo.",),
        assumptions=("Augmented SCM structure matches the panel.",),
        inference_support=("point_estimate", "Kfold", "Conformal"),
        known_limitations=("Less automated validation than CVXPY SCM variants.",),
    ),
    _est(
        "SyntheticControlCVXPY",
        EstimatorMaturity.EXPERT_REVIEW,
        "SyntheticControlCVXPY",
        "panel_exp.methods.scm",
        rationale=("tests/test_scm.py covers filters, regularization, and valid weights.",),
        assumptions=("CVXPY formulation appropriate for donor simplex/ridge.",),
        optional_dependencies=("cvxpy",),
        inference_support=("point_estimate", "Kfold", "Conformal", "BlockResidualBootstrap"),
        known_limitations=("Solver-dependent; review donor correlations.",),
    ),
    _est(
        "AugSynthCVXPY",
        EstimatorMaturity.EXPERT_REVIEW,
        "AugSynthCVXPY",
        "panel_exp.methods.scm",
        rationale=("Covered by tests/test_scm.py with SyntheticControlCVXPY.",),
        assumptions=("Augmented outcomes and weights correctly specified.",),
        optional_dependencies=("cvxpy",),
        inference_support=("point_estimate", "Kfold", "Conformal"),
        known_limitations=("More complex than base SCM.",),
    ),
    _est(
        "TBR",
        EstimatorMaturity.EXPERT_REVIEW,
        "TBR",
        "panel_exp.methods.tbr",
        rationale=("Less smoke/validation coverage than TBRRidge in-repo.",),
        assumptions=("Linear pre-period structure continues post treatment.",),
        inference_support=("point_estimate", "UnitJackKnife", "JKP", "Kfold"),
        known_limitations=("Prefer TBRRidge for default workflows.",),
    ),
    _est(
        "TBRRidge",
        EstimatorMaturity.EXPERT_REVIEW,
        "TBRRidge",
        "panel_exp.methods.tbr",
        rationale=(
            "TBRRidge has useful recovery and regression coverage, but production-safe "
            "status requires broader coverage/FPR/power validation. Use with expert review.",
            "Recovery smoke and registry equivalence tests are insufficient alone.",
        ),
        assumptions=(
            "Ridge on normalized pre-period trends.",
            "Treated and controls comparable after normalization.",
        ),
        synthetic_validation=True,
        inference_support=(
            "point_estimate",
            "UnitJackKnife",
            "JKP",
            "Bayesian",
            "BlockResidualBootstrap",
            "Conformal",
            "Kfold",
            "TimeSeriesKfold",
        ),
        known_limitations=(
            "Registry Bayesian mode on TBRRidge is not full BayesianTBR MCMC.",
        ),
    ),
    _est(
        "TBRAutoSARIMAX",
        EstimatorMaturity.EXPERT_REVIEW,
        "TBRAutoSARIMAX",
        "panel_exp.methods.tbr",
        rationale=("Auto-ARIMA search; not in default validation runner.",),
        assumptions=("ARIMA orders stable; pmdarima search appropriate.",),
        optional_dependencies=("pmdarima", "statsmodels"),
        inference_support=("point_estimate",),
        known_limitations=("Runtime and model-selection review required.",),
    ),
    _est(
        "BayesianTBR",
        EstimatorMaturity.RESEARCH_ONLY,
        "BayesianTBR",
        "panel_exp.methods.bayesian_regression",
        rationale=(
            "Skipped in EstimatorValidationRunner (JAX stack).",
            "MCMC cost; pinned jax/jaxlib needed for reproducibility.",
        ),
        assumptions=("NUTS MCMC adequate; priors match panel.",),
        optional_dependencies=("jax", "jaxlib", "numpyro", "arviz"),
        inference_support=("Bayesian",),
        known_limitations=("Exploratory; convergence diagnostics required.",),
    ),
    _est(
        "BayesianTBRHorseShoe",
        EstimatorMaturity.RESEARCH_ONLY,
        "BayesianTBRHorseShoe",
        "panel_exp.methods.bayesian_regression",
        rationale=("Same validation gaps and optional deps as BayesianTBR.",),
        assumptions=("Horseshoe sparsity prior appropriate.",),
        optional_dependencies=("jax", "jaxlib", "numpyro", "arviz"),
        inference_support=("Bayesian",),
        known_limitations=("Research-only MCMC path.",),
    ),
    _est(
        "DID",
        EstimatorMaturity.EXPERT_REVIEW,
        "DID",
        "panel_exp.methods.DID",
        rationale=("In default_estimator_configs; not parametrized in recovery smoke.",),
        assumptions=("Parallel trends; treatment timing correct.",),
        synthetic_validation=True,
        inference_support=("point_estimate",),
        known_limitations=("Pooled vs unit timing choices need expert review.",),
    ),
    _est(
        "SyntheticDID",
        EstimatorMaturity.RESEARCH_ONLY,
        "SyntheticDID",
        "panel_exp.methods.synthetic_did",
        rationale=(
            "Skipped in validation runner; synthetic_did tests have fixture limitations.",
        ),
        assumptions=("SDID factor/weight model appropriate.",),
        inference_support=("point_estimate",),
        known_limitations=("Limited stable recovery automation in CI.",),
    ),
    _est(
        "TROP",
        EstimatorMaturity.RESEARCH_ONLY,
        "TROP",
        "panel_exp.methods.triply_robust_est",
        rationale=("Skipped in validation runner; tests/trop_test.py only.",),
        assumptions=("Triply robust structure per implementation.",),
        inference_support=("point_estimate",),
        known_limitations=("Large config space; expert tuning required.",),
    ),
    _est(
        "MTGP",
        EstimatorMaturity.RESEARCH_ONLY,
        "MTGP",
        "panel_exp.methods.mtgp",
        rationale=("Skipped in validation runner; Bayesian MCMC GP.",),
        assumptions=("GP prior fits panel; Bayesian-only path.",),
        optional_dependencies=("jax", "jaxlib", "numpyro"),
        inference_support=("Bayesian",),
        known_limitations=("Experimental runtime and stability.",),
    ),
)

_INFERENCE_MODE_CATALOG: Tuple[InferenceModeMaturityMetadata, ...] = (
    InferenceModeMaturityMetadata(
        "point_estimate",
        EstimatorMaturity.EXPERT_REVIEW,
        rationale=(
            "Point estimate mode is computationally simple but provides no interval "
            "uncertainty; decision use requires expert review or external uncertainty evidence.",
        ),
        assumptions=("Point path is deterministic given a fitted model.",),
        known_limitations=("No path-level uncertainty intervals.",),
    ),
    InferenceModeMaturityMetadata(
        "UnitJackKnife",
        EstimatorMaturity.EXPERT_REVIEW,
        rationale=("Registry equivalence tests; needs >=2 control units.",),
        assumptions=("Unit-level jackknife appropriate.",),
    ),
    InferenceModeMaturityMetadata(
        "JKP",
        EstimatorMaturity.EXPERT_REVIEW,
        rationale=("Registry golden/equivalence coverage.",),
    ),
    InferenceModeMaturityMetadata(
        "Bayesian",
        EstimatorMaturity.RESEARCH_ONLY,
        rationale=(
            "JAX/numpyro stack; registry handler not equivalent to full BayesianTBR MCMC.",
        ),
        optional_dependencies=("jax", "jaxlib", "numpyro"),
        known_limitations=("Unstable optional dependency path without pins.",),
    ),
    InferenceModeMaturityMetadata(
        "BlockResidualBootstrap",
        EstimatorMaturity.EXPERT_REVIEW,
        rationale=("Golden fixtures and registry tests.",),
        assumptions=("Block residuals approximate temporal dependence.",),
    ),
    InferenceModeMaturityMetadata(
        "Conformal",
        EstimatorMaturity.EXPERT_REVIEW,
        rationale=("Registry tests; conformal assumptions on residuals.",),
        assumptions=("Exchangeability/split behavior adequate.",),
    ),
    InferenceModeMaturityMetadata(
        "Kfold",
        EstimatorMaturity.EXPERT_REVIEW,
        rationale=("Golden fixtures; reproducible when random_state set.",),
        assumptions=("Panel K-fold appropriate for pre-treatment fit.",),
    ),
    InferenceModeMaturityMetadata(
        "Placebo",
        EstimatorMaturity.EXPERT_REVIEW,
        rationale=(
            "Registry tests; placebo bands may vary by platform (optimizer path).",
        ),
        assumptions=("Enough placebos; inversion CI interpretable.",),
        known_limitations=("Coverage-based bands, not classical analytical CIs.",),
    ),
    InferenceModeMaturityMetadata(
        "TimeSeriesKfold",
        EstimatorMaturity.EXPERT_REVIEW,
        rationale=("Registry golden tests.",),
        assumptions=("Temporal blocking appropriate.",),
    ),
)

_CLASS_TO_KEY: Dict[str, str] = {m.class_name: m.name for m in _ESTIMATOR_CATALOG}
_NAME_TO_META: Dict[str, EstimatorMetadata] = {m.name: m for m in _ESTIMATOR_CATALOG}
_INFERENCE_NAME_TO_META: Dict[str, InferenceModeMaturityMetadata] = {
    m.name: m for m in _INFERENCE_MODE_CATALOG
}


def get_inference_mode_metadata(mode_name: str) -> InferenceModeMaturityMetadata:
    """Return maturity metadata for an inference mode; raises KeyError if unknown."""
    try:
        return _INFERENCE_NAME_TO_META[mode_name]
    except KeyError as exc:
        raise KeyError(
            f"Unknown inference mode {mode_name!r}; known modes: {sorted(_INFERENCE_NAME_TO_META)}"
        ) from exc


def merge_maturity_into_results(
    results: Dict[str, Any],
    analyzer: Any,
    inference_mode_name: str,
) -> None:
    """Add maturity fields into results['inference_metadata'] without changing estimates."""
    existing = dict(results.get("inference_metadata") or {})
    class_name = analyzer.__class__.__name__
    registry_key = _CLASS_TO_KEY.get(class_name)
    if registry_key is not None:
        existing.update(_NAME_TO_META[registry_key].to_evidence_dict())
    else:
        existing.update(
            {
                "estimator_maturity": EstimatorMaturity.UNVALIDATED.value,
                "estimator_assumptions": [],
                "estimator_rationale": [
                    f"No maturity catalog entry for class {class_name!r}."
                ],
                "estimator_synthetic_validation": False,
            }
        )
    existing.update(get_inference_mode_metadata(inference_mode_name).to_evidence_dict())
    results["inference_metadata"] = existing


__all__ = [
    "EstimatorMaturity",
    "EstimatorMetadata",
    "InferenceModeMaturityMetadata",
    "MATURITY_DOC",
    "merge_maturity_into_results",
    "get_inference_mode_metadata",
]
