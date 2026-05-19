"""
Post-assignment design validation gate.

Returns typed PASS / WARN / FAIL checks. Blocking failures should prevent
production-style analysis when policy requires it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from panel_exp.design.constraints import validate_assignment_dict, ConstraintContext, prepare_constraint_context
from panel_exp.spec import InterferenceAssumption


class ValidationStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass
class ValidationCheck:
    """Single validation gate result (``metric`` is the stable check name)."""

    metric: str
    status: ValidationStatus
    threshold: Optional[float]
    value: Optional[float]
    message: str
    blocking: bool

    @property
    def check_name(self) -> str:
        return self.metric

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["check_name"] = self.check_name
        return d


@dataclass
class DesignValidationResult:
    checks: List[ValidationCheck]
    status: ValidationStatus
    blocking_failures: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "blocking_failures": self.blocking_failures,
            "checks": [c.to_dict() for c in self.checks],
        }

    @property
    def passed(self) -> bool:
        return self.status != ValidationStatus.FAIL

    def raise_if_blocking(self) -> None:
        if self.blocking_failures:
            raise ValueError(
                "Design validation failed (blocking): "
                + "; ".join(self.blocking_failures)
            )


def _worst_status(checks: List[ValidationCheck]) -> ValidationStatus:
    if any(c.status == ValidationStatus.FAIL for c in checks):
        return ValidationStatus.FAIL
    if any(c.status == ValidationStatus.WARN for c in checks):
        return ValidationStatus.WARN
    return ValidationStatus.PASS


def standardized_mean_difference(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size == 0 or b.size == 0:
        return float("nan")
    var_a, var_b = np.var(a, ddof=1), np.var(b, ddof=1)
    pooled = np.sqrt((var_a + var_b) / 2.0) if (var_a + var_b) > 0 else 0.0
    if pooled == 0:
        return 0.0 if np.mean(a) == np.mean(b) else float("inf")
    return float(abs(np.mean(a) - np.mean(b)) / pooled)


def validate_design(
    wide_data: pd.DataFrame,
    assignment: Dict[str, List],
    *,
    n_test_grps: int = 1,
    treatment_probability: float = 0.5,
    control_whitelist: Optional[List] = None,
    test_whitelist: Optional[List] = None,
    control_blacklist: Optional[List] = None,
    test_blacklist: Optional[List] = None,
    control_test_blacklist: Optional[List] = None,
    min_control_units: int = 2,
    min_test_units: int = 1,
    min_pre_period_length: int = 14,
    srm_tolerance: float = 0.10,
    kpi_mass_tolerance: float = 0.15,
    smd_warn_threshold: float = 0.25,
    smd_fail_threshold: float = 0.50,
    interference: InterferenceAssumption = InterferenceAssumption.UNKNOWN,
    block_on_fail: bool = True,
) -> DesignValidationResult:
    """
    Run design validation checks after assignment.

    Parameters
    ----------
    wide_data : unit x time KPI matrix used for design
    assignment : dict with control, test_0, ...
    """
    checks: List[ValidationCheck] = []

    try:
        ctx = prepare_constraint_context(
            wide_data,
            treatment_probability,
            n_test_grps,
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )
        validate_assignment_dict(
            assignment,
            ctx,
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )
        checks.append(
            ValidationCheck(
                metric="whitelist_blacklist",
                status=ValidationStatus.PASS,
                threshold=None,
                value=None,
                message="Whitelist/blacklist constraints satisfied.",
                blocking=True,
            )
        )
    except ValueError as exc:
        checks.append(
            ValidationCheck(
                metric="whitelist_blacklist",
                status=ValidationStatus.FAIL,
                threshold=None,
                value=None,
                message=str(exc),
                blocking=True,
            )
        )
        ctx = None

    control = [str(u) for u in assignment.get("control", [])]
    test_units = []
    test_keys = [f"test_{i}" for i in range(n_test_grps)]
    for k in test_keys:
        test_units.extend(assignment.get(k, []))

    unit_index = {str(u) for u in wide_data.index.tolist()}
    assigned_all: List[str] = []
    seen: set[str] = set()
    for u in control + test_units:
        if u not in unit_index:
            checks.append(
                ValidationCheck(
                    metric="assigned_unknown_units",
                    status=ValidationStatus.FAIL,
                    threshold=None,
                    value=None,
                    message=f"Assigned unit {u!r} not in input panel.",
                    blocking=True,
                )
            )
        if u in seen:
            checks.append(
                ValidationCheck(
                    metric="duplicate_assignment",
                    status=ValidationStatus.FAIL,
                    threshold=None,
                    value=None,
                    message=f"Unit {u!r} assigned to more than one arm.",
                    blocking=True,
                )
            )
        seen.add(u)
        assigned_all.append(u)

    overlap_control_test = set(control) & set(test_units)
    if overlap_control_test:
        checks.append(
            ValidationCheck(
                metric="overlapping_arms",
                status=ValidationStatus.FAIL,
                threshold=None,
                value=None,
                message=f"Units in both control and test: {sorted(overlap_control_test)}",
                blocking=True,
            )
        )
    elif assigned_all and not any(
        c.metric in ("assigned_unknown_units", "duplicate_assignment") and c.status == ValidationStatus.FAIL
        for c in checks
    ):
        checks.append(
            ValidationCheck(
                metric="assignment_integrity",
                status=ValidationStatus.PASS,
                threshold=None,
                value=float(len(assigned_all)),
                message="No duplicate or unknown unit assignments.",
                blocking=True,
            )
        )

    control_valid = [u for u in control if u in unit_index]
    test_valid = [u for u in test_units if u in unit_index]

    n_control, n_test = len(control), len(test_units)
    n_total = n_control + n_test

    if n_control < min_control_units:
        checks.append(
            ValidationCheck(
                metric="min_control_units",
                status=ValidationStatus.FAIL,
                threshold=float(min_control_units),
                value=float(n_control),
                message=f"Control count {n_control} < minimum {min_control_units}.",
                blocking=True,
            )
        )
    else:
        checks.append(
            ValidationCheck(
                metric="min_control_units",
                status=ValidationStatus.PASS,
                threshold=float(min_control_units),
                value=float(n_control),
                message="Sufficient control units.",
                blocking=True,
            )
        )

    if n_test < min_test_units:
        checks.append(
            ValidationCheck(
                metric="min_test_units",
                status=ValidationStatus.FAIL,
                threshold=float(min_test_units),
                value=float(n_test),
                message=f"Test count {n_test} < minimum {min_test_units}.",
                blocking=True,
            )
        )
    else:
        checks.append(
            ValidationCheck(
                metric="min_test_units",
                status=ValidationStatus.PASS,
                threshold=float(min_test_units),
                value=float(n_test),
                message="Sufficient test units.",
                blocking=True,
            )
        )

    n_time = wide_data.shape[1]
    if n_time < min_pre_period_length:
        checks.append(
            ValidationCheck(
                metric="pre_period_length",
                status=ValidationStatus.FAIL,
                threshold=float(min_pre_period_length),
                value=float(n_time),
                message=f"Panel has {n_time} periods < minimum {min_pre_period_length}.",
                blocking=True,
            )
        )
    else:
        checks.append(
            ValidationCheck(
                metric="pre_period_length",
                status=ValidationStatus.PASS,
                threshold=float(min_pre_period_length),
                value=float(n_time),
                message="Pre-period length acceptable.",
                blocking=False,
            )
        )

    if n_total > 0:
        observed_test_share = n_test / n_total
        share_gap = abs(observed_test_share - treatment_probability)
        srm_status = (
            ValidationStatus.PASS
            if share_gap <= srm_tolerance
            else ValidationStatus.WARN
        )
        checks.append(
            ValidationCheck(
                metric="srm_unit_share",
                status=srm_status,
                threshold=srm_tolerance,
                value=share_gap,
                message=(
                    f"Unit-count treatment share {observed_test_share:.3f} vs "
                    f"target {treatment_probability:.3f} (gap {share_gap:.3f})."
                ),
                blocking=False,
            )
        )

        total_mass = float(wide_data.sum().sum())
        if total_mass > 0:
            ctrl_mass = (
                float(wide_data.loc[control_valid].sum().sum()) if control_valid else 0.0
            )
            test_mass = (
                float(wide_data.loc[test_valid].sum().sum()) if test_valid else 0.0
            )
            observed_mass_share = test_mass / (ctrl_mass + test_mass + 1e-12)
            mass_gap = abs(observed_mass_share - treatment_probability)
            mass_status = (
                ValidationStatus.PASS
                if mass_gap <= kpi_mass_tolerance
                else ValidationStatus.WARN
            )
            checks.append(
                ValidationCheck(
                    metric="kpi_mass_balance",
                    status=mass_status,
                    threshold=kpi_mass_tolerance,
                    value=mass_gap,
                    message=(
                        f"KPI mass treatment share {observed_mass_share:.3f} vs "
                        f"target {treatment_probability:.3f}."
                    ),
                    blocking=False,
                )
            )

        pre_cov = wide_data.mean(axis=1)
        if control_valid and test_valid:
            smd = standardized_mean_difference(
                pre_cov.loc[control_valid].values, pre_cov.loc[test_valid].values
            )
            if smd >= smd_fail_threshold:
                smd_status = ValidationStatus.FAIL
            elif smd >= smd_warn_threshold:
                smd_status = ValidationStatus.WARN
            else:
                smd_status = ValidationStatus.PASS
            checks.append(
                ValidationCheck(
                    metric="covariate_smd",
                    status=smd_status,
                    threshold=smd_warn_threshold,
                    value=smd,
                    message=f"Pre-period mean KPI SMD = {smd:.3f}.",
                    blocking=smd_status == ValidationStatus.FAIL,
                )
            )

    if interference == InterferenceAssumption.UNKNOWN:
        checks.append(
            ValidationCheck(
                metric="interference_assumption",
                status=ValidationStatus.WARN,
                threshold=None,
                value=None,
                message=(
                    "Interference assumption is unknown. Geo media experiments may "
                    "violate no-interference; spillover detection is not automated."
                ),
                blocking=False,
            )
        )
    elif interference == InterferenceAssumption.PARTIAL_INTERFERENCE:
        checks.append(
            ValidationCheck(
                metric="interference_assumption",
                status=ValidationStatus.WARN,
                threshold=None,
                value=None,
                message="Partial interference declared; analyze with caution.",
                blocking=False,
            )
        )

    status = _worst_status(checks)
    blocking_failures = [
        c.message for c in checks if c.blocking and c.status == ValidationStatus.FAIL
    ]
    result = DesignValidationResult(
        checks=checks, status=status, blocking_failures=blocking_failures
    )
    if block_on_fail:
        result.raise_if_blocking()
    return result
