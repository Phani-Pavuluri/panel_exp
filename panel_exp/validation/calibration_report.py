"""
A/A calibration and readiness diagnostics from validation / recovery outputs.

Summarizes null-experiment behavior (FPR, coverage, bias) without changing
estimators, thresholds, or maturity labels.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence

# Readiness warning thresholds (diagnostic only; do not block runs).
MIN_REPLICATIONS_FOR_STABLE_CALIBRATION = 100
MAX_FALSE_POSITIVE_RATE = 0.10
MIN_COVERAGE_UNDER_NULL = 0.90
MIN_POWER_TARGET = 0.80
MIN_RECOVERY_SUCCESS_RATE = 0.90

_NULL_SCENARIO_MARKERS = (
    "aa_zero",
    "aa_null",
    "zero_effect",
    "null_effect",
    "recovery_null",
)
_POSITIVE_SCENARIO_MARKERS = (
    "positive",
    "constant_positive",
    "recovery_positive",
    "lift",
)


def _safe_float(value: Any, default: float = float("nan")) -> float:
    if value is None:
        return default
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def _is_null_scenario(name: str, payload: Mapping[str, Any]) -> bool:
    lowered = name.lower()
    if any(marker in lowered for marker in _NULL_SCENARIO_MARKERS):
        return True
    truth = payload.get("truth")
    if truth is not None and abs(_safe_float(truth)) <= 1e-9:
        return True
    effect = payload.get("true_effect")
    if effect is not None and abs(_safe_float(effect)) <= 1e-9:
        return True
    return False


def _is_positive_scenario(name: str, payload: Mapping[str, Any]) -> bool:
    lowered = name.lower()
    if any(marker in lowered for marker in _POSITIVE_SCENARIO_MARKERS):
        return True
    truth = payload.get("truth")
    if truth is not None and abs(_safe_float(truth)) >= 0.02:
        return True
    effect = payload.get("true_effect")
    if effect is not None and abs(_safe_float(effect)) >= 0.02:
        return True
    return False


def _payload_from_output(item: Any) -> Dict[str, Any]:
    if isinstance(item, Mapping):
        return dict(item)
    if hasattr(item, "to_dict"):
        return dict(item.to_dict())
    return {}


def _scenario_name(payload: Dict[str, Any], default: str = "") -> str:
    return str(
        payload.get("scenario")
        or payload.get("scenario_name")
        or default
    )


@dataclass
class CalibrationReport:
    """Readiness diagnostics from null and lift simulation batteries."""

    n_replications: int = 0
    null_replications: int = 0
    positive_replications: int = 0

    false_positive_rate: float = float("nan")
    false_negative_rate: float = float("nan")
    coverage_under_null: float = float("nan")
    coverage_under_lift: float = float("nan")
    power: float = float("nan")

    mean_interval_width: float = float("nan")
    median_interval_width: float = float("nan")

    bias_under_null: float = float("nan")
    bias_under_lift: float = float("nan")

    recovery_success_rate: float = float("nan")

    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "## Calibration Summary",
            "",
            "> Diagnostic A/A and recovery metrics only; not a production readiness gate.",
            "",
            "### Replication counts",
            f"- **Total replications:** {self.n_replications}",
            f"- **Null (A/A) replications:** {self.null_replications}",
            f"- **Positive-lift replications:** {self.positive_replications}",
            "",
            "### Null experiment behavior",
            f"- **False positive rate:** {_fmt_rate(self.false_positive_rate)}",
            f"- **Coverage under null:** {_fmt_rate(self.coverage_under_null)}",
            f"- **Bias under null:** {_fmt_num(self.bias_under_null)}",
            "",
            "### Lift experiment behavior",
            f"- **Power:** {_fmt_rate(self.power)}",
            f"- **False negative rate:** {_fmt_rate(self.false_negative_rate)}",
            f"- **Coverage under lift:** {_fmt_rate(self.coverage_under_lift)}",
            f"- **Bias under lift:** {_fmt_num(self.bias_under_lift)}",
            "",
            "### Intervals and recovery",
            f"- **Mean interval width:** {_fmt_num(self.mean_interval_width)}",
            f"- **Median interval width:** {_fmt_num(self.median_interval_width)}",
            f"- **Recovery success rate:** {_fmt_rate(self.recovery_success_rate)}",
            "",
        ]
        if self.warnings:
            lines.append("### Calibration warnings")
            for w in self.warnings:
                lines.append(f"- **WARNING:** {w}")
            lines.append("")
        else:
            lines.append("- *No calibration warnings.*")
            lines.append("")
        return "\n".join(lines)


def _fmt_rate(value: float) -> str:
    if value != value:
        return "unknown"
    return f"{value:.4f}"


def _fmt_num(value: float) -> str:
    if value != value:
        return "unknown"
    return f"{value:.6g}"


def compute_calibration_warnings(report: CalibrationReport) -> List[str]:
    """Return diagnostic warnings; does not mutate ``report``."""
    warnings: List[str] = []

    if report.n_replications < MIN_REPLICATIONS_FOR_STABLE_CALIBRATION:
        warnings.append(
            "Calibration estimated from small simulation count "
            f"({report.n_replications} < {MIN_REPLICATIONS_FOR_STABLE_CALIBRATION})"
        )

    fpr = report.false_positive_rate
    if fpr == fpr and fpr > MAX_FALSE_POSITIVE_RATE:
        warnings.append(
            f"False positive rate exceeds expected threshold "
            f"({fpr:.3f} > {MAX_FALSE_POSITIVE_RATE})"
        )

    cov_null = report.coverage_under_null
    if cov_null == cov_null and cov_null < MIN_COVERAGE_UNDER_NULL:
        warnings.append(
            f"Coverage below expected range under null "
            f"({cov_null:.3f} < {MIN_COVERAGE_UNDER_NULL})"
        )

    pwr = report.power
    if pwr == pwr and pwr < MIN_POWER_TARGET:
        warnings.append(
            f"Power below target ({pwr:.3f} < {MIN_POWER_TARGET})"
        )

    rec = report.recovery_success_rate
    if rec == rec and rec < MIN_RECOVERY_SUCCESS_RATE:
        warnings.append(
            f"Recovery instability observed "
            f"({rec:.3f} < {MIN_RECOVERY_SUCCESS_RATE})"
        )

    return warnings


def build_calibration_report(
    *,
    validation_outputs: Optional[Sequence[Any]] = None,
    recovery_outputs: Optional[Sequence[Any]] = None,
    aa_calibration: Optional[Mapping[str, Any]] = None,
    estimator: Optional[str] = None,
) -> CalibrationReport:
    """
    Build a calibration report from optional validation / recovery payloads.

    Does not mutate input objects. Missing fields remain NaN or zero counts.
    Explicit ``aa_calibration`` keys override inferred aggregates when present.
    """
    null_payloads: List[Dict[str, Any]] = []
    positive_payloads: List[Dict[str, Any]] = []
    all_payloads: List[Dict[str, Any]] = []
    width_vals: List[float] = []

    for source in (validation_outputs or (), recovery_outputs or ()):
        for item in source:
            payload = _payload_from_output(item)
            if estimator and payload.get("estimator") not in (
                None,
                estimator,
            ):
                if payload.get("estimator_name") not in (None, estimator):
                    continue
            name = _scenario_name(
                payload,
                default=str(payload.get("estimator_name", payload.get("estimator", ""))),
            )
            n_rep = int(payload.get("n_simulations") or payload.get("n_replications") or 0)
            if n_rep:
                payload = {**payload, "n_replications": n_rep}
            all_payloads.append(payload)

            iw = payload.get("interval_width")
            if iw is not None and math.isfinite(_safe_float(iw)):
                width_vals.append(_safe_float(iw))
            mean_iw = payload.get("mean_interval_width")
            if mean_iw is not None and math.isfinite(_safe_float(mean_iw)):
                width_vals.append(_safe_float(mean_iw))

            if _is_null_scenario(name, payload):
                null_payloads.append(payload)
            elif _is_positive_scenario(name, payload):
                positive_payloads.append(payload)

    def _sum_replications(payloads: Sequence[Mapping[str, Any]]) -> int:
        total = 0
        for p in payloads:
            total += int(p.get("n_simulations") or p.get("n_replications") or 0)
        return total

    def _pick_metric(
        payloads: Sequence[Mapping[str, Any]], *keys: str
    ) -> float:
        for key in keys:
            for p in payloads:
                if key in p:
                    val = _safe_float(p[key])
                    if val == val:
                        return val
        return float("nan")

    def _mean_metric(payloads: Sequence[Mapping[str, Any]], *keys: str) -> float:
        vals: List[float] = []
        for key in keys:
            for p in payloads:
                if key in p:
                    val = _safe_float(p[key])
                    if val == val:
                        vals.append(val)
        return float(sum(vals) / len(vals)) if vals else float("nan")

    n_replications = _sum_replications(all_payloads)
    null_replications = _sum_replications(null_payloads)
    positive_replications = _sum_replications(positive_payloads)

    report = CalibrationReport(
        n_replications=n_replications,
        null_replications=null_replications,
        positive_replications=positive_replications,
        false_positive_rate=_pick_metric(
            null_payloads, "false_positive_rate", "fpr"
        ),
        false_negative_rate=_pick_metric(
            positive_payloads, "false_negative_rate", "fnr"
        ),
        coverage_under_null=_pick_metric(null_payloads, "coverage"),
        coverage_under_lift=_pick_metric(positive_payloads, "coverage"),
        power=_pick_metric(positive_payloads, "power"),
        mean_interval_width=(
            float(sum(width_vals) / len(width_vals)) if width_vals else float("nan")
        ),
        median_interval_width=(
            float(sorted(width_vals)[len(width_vals) // 2])
            if width_vals
            else float("nan")
        ),
        bias_under_null=_pick_metric(null_payloads, "bias"),
        bias_under_lift=_pick_metric(positive_payloads, "bias"),
        recovery_success_rate=_mean_metric(all_payloads, "recovery_success_rate"),
    )

    if aa_calibration:
        ac = dict(aa_calibration)
        merged_warnings = list(ac.get("warnings") or [])
        report = CalibrationReport(
            n_replications=int(ac.get("n_replications", report.n_replications)),
            null_replications=int(
                ac.get("null_replications", report.null_replications)
            ),
            positive_replications=int(
                ac.get("positive_replications", report.positive_replications)
            ),
            false_positive_rate=_safe_float(
                ac.get("false_positive_rate", report.false_positive_rate)
            ),
            false_negative_rate=_safe_float(
                ac.get("false_negative_rate", report.false_negative_rate)
            ),
            coverage_under_null=_safe_float(
                ac.get("coverage_under_null", report.coverage_under_null)
            ),
            coverage_under_lift=_safe_float(
                ac.get("coverage_under_lift", report.coverage_under_lift)
            ),
            power=_safe_float(ac.get("power", report.power)),
            mean_interval_width=_safe_float(
                ac.get("mean_interval_width", report.mean_interval_width)
            ),
            median_interval_width=_safe_float(
                ac.get("median_interval_width", report.median_interval_width)
            ),
            bias_under_null=_safe_float(
                ac.get("bias_under_null", report.bias_under_null)
            ),
            bias_under_lift=_safe_float(
                ac.get("bias_under_lift", report.bias_under_lift)
            ),
            recovery_success_rate=_safe_float(
                ac.get("recovery_success_rate", report.recovery_success_rate)
            ),
            warnings=merged_warnings,
        )
        if not merged_warnings:
            report = CalibrationReport(
                **{
                    **report.to_dict(),
                    "warnings": compute_calibration_warnings(report),
                }
            )
        return report

    return CalibrationReport(
        **{**report.to_dict(), "warnings": compute_calibration_warnings(report)}
    )


def attach_calibration_report(
    target: Dict[str, Any],
    report: CalibrationReport,
    *,
    key: str = "calibration_report",
) -> None:
    """Attach additive calibration diagnostics to ``results`` or ``artifacts``."""
    target[key] = report.to_dict()


def calibration_markdown_from_mapping(
    payload: Optional[Mapping[str, Any]],
) -> str:
    """Render markdown from a calibration dict; empty string if missing."""
    if not payload:
        return ""
    if isinstance(payload, str):
        return payload
    try:
        report = CalibrationReport(
            **{
                k: v
                for k, v in dict(payload).items()
                if k in CalibrationReport.__dataclass_fields__
            }
        )
        if not report.warnings:
            report = CalibrationReport(
                **{**report.to_dict(), "warnings": compute_calibration_warnings(report)}
            )
        return report.to_markdown()
    except (TypeError, ValueError):
        return ""


__all__ = [
    "MIN_COVERAGE_UNDER_NULL",
    "MIN_POWER_TARGET",
    "MIN_REPLICATIONS_FOR_STABLE_CALIBRATION",
    "MIN_RECOVERY_SUCCESS_RATE",
    "MAX_FALSE_POSITIVE_RATE",
    "CalibrationReport",
    "attach_calibration_report",
    "build_calibration_report",
    "calibration_markdown_from_mapping",
    "compute_calibration_warnings",
]
