#!/usr/bin/env python
"""Run TROP tests without pytest. Use: python run_trop_tests.py"""
import sys
sys.path.insert(0, ".")

from tests.trop_test import (
    test_trop_global_mode_smoke,
    test_trop_local_mode_smoke,
    test_trop_global_positive_effect_recovery,
    test_trop_local_positive_effect_recovery,
    test_trop_period_effects_sanity,
    test_trop_local_mode_semantics,
    test_trop_global_missing_data,
    test_trop_local_missing_data,
    test_trop_inference_override_global_placebo,
    test_trop_inference_override_global_bootstrap,
    test_trop_inference_override_local_placebo,
    test_trop_inference_override_local_bootstrap,
    test_trop_inference_override_local_auto,
    test_trop_bootstrap_fallback_honesty,
    test_trop_cv_mode_default_global,
    test_trop_cv_mode_default_local,
    test_trop_cv_mode_override,
    test_trop_cv_mode_global_obs_routes_through_global_scorer,
    test_trop_cv_mode_local_obs_routes_through_local_scorer,
    test_trop_cv_mode_explicit_global_obs_on_local_estimator,
    test_trop_cv_mode_explicit_local_obs_on_global_estimator,
    test_trop_cv_mode_invalid_raises,
    test_trop_local_diagnostics_placement,
    test_trop_local_counterfactual_tau_consistency,
    test_trop_run_analysis_strengthened,
    test_trop_local_get_component_matrices_raises,
    test_trop_constructor_validation,
)

TESTS = [
    ("test_trop_global_mode_smoke", test_trop_global_mode_smoke),
    ("test_trop_local_mode_smoke", test_trop_local_mode_smoke),
    ("test_trop_global_positive_effect_recovery", test_trop_global_positive_effect_recovery),
    ("test_trop_local_positive_effect_recovery", test_trop_local_positive_effect_recovery),
    ("test_trop_period_effects_sanity", test_trop_period_effects_sanity),
    ("test_trop_local_mode_semantics", test_trop_local_mode_semantics),
    ("test_trop_global_missing_data", test_trop_global_missing_data),
    ("test_trop_local_missing_data", test_trop_local_missing_data),
    ("test_trop_inference_override_global_placebo", test_trop_inference_override_global_placebo),
    ("test_trop_inference_override_global_bootstrap", test_trop_inference_override_global_bootstrap),
    ("test_trop_inference_override_local_placebo", test_trop_inference_override_local_placebo),
    ("test_trop_inference_override_local_bootstrap", test_trop_inference_override_local_bootstrap),
    ("test_trop_inference_override_local_auto", test_trop_inference_override_local_auto),
    ("test_trop_bootstrap_fallback_honesty", test_trop_bootstrap_fallback_honesty),
    ("test_trop_cv_mode_default_global", test_trop_cv_mode_default_global),
    ("test_trop_cv_mode_default_local", test_trop_cv_mode_default_local),
    ("test_trop_cv_mode_override", test_trop_cv_mode_override),
    ("test_trop_cv_mode_global_obs_routes_through_global_scorer", test_trop_cv_mode_global_obs_routes_through_global_scorer),
    ("test_trop_cv_mode_local_obs_routes_through_local_scorer", test_trop_cv_mode_local_obs_routes_through_local_scorer),
    ("test_trop_cv_mode_explicit_global_obs_on_local_estimator", test_trop_cv_mode_explicit_global_obs_on_local_estimator),
    ("test_trop_cv_mode_explicit_local_obs_on_global_estimator", test_trop_cv_mode_explicit_local_obs_on_global_estimator),
    ("test_trop_cv_mode_invalid_raises", test_trop_cv_mode_invalid_raises),
    ("test_trop_local_diagnostics_placement", test_trop_local_diagnostics_placement),
    ("test_trop_local_counterfactual_tau_consistency", test_trop_local_counterfactual_tau_consistency),
    ("test_trop_run_analysis_strengthened", test_trop_run_analysis_strengthened),
    ("test_trop_local_get_component_matrices_raises", test_trop_local_get_component_matrices_raises),
    ("test_trop_constructor_validation", test_trop_constructor_validation),
]

if __name__ == "__main__":
    failed = []
    for name, fn in TESTS:
        try:
            fn()
            print(f"PASS {name}")
        except Exception as e:
            print(f"FAIL {name}: {e}")
            failed.append((name, str(e)))
    if failed:
        print(f"\n{len(failed)} failed: {[n for n, _ in failed]}")
        sys.exit(1)
    print(f"\nAll {len(TESTS)} tests passed.")
    sys.exit(0)
