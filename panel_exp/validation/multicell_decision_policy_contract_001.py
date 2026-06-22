"""MULTICELL-CELL-RELATIONSHIP-AND-DECISION-POLICY-CONTRACT-001.

Governed semantic contract for multi-cell design readouts. Prevents over-claiming
(winner selection, any-cell success, pooled causal readout) without implementing
multiplicity correction or simultaneous inference.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping

CONTRACT_ID = "MULTICELL-CELL-RELATIONSHIP-AND-DECISION-POLICY-CONTRACT-001"
CONTRACT_VERSION = "1.0.0"
_INVESTIGATION_ID = "INV-MULTICELL-CELL-RELATIONSHIP-DECISION-POLICY-001"


class CellRelationship(str, Enum):
    SINGLE_CELL = "SINGLE_CELL"
    PARALLEL_MARGINAL_CELLS = "PARALLEL_MARGINAL_CELLS"
    COMPETING_CELLS = "COMPETING_CELLS"
    POOLED_COMPONENT_CELLS = "POOLED_COMPONENT_CELLS"
    UNKNOWN = "UNKNOWN"


class DecisionPolicy(str, Enum):
    REPORT_EACH_CELL_ONLY = "REPORT_EACH_CELL_ONLY"
    DECLARE_ANY_CELL_SUCCESS = "DECLARE_ANY_CELL_SUCCESS"
    SELECT_OR_RANK_CELLS = "SELECT_OR_RANK_CELLS"
    POOL_CELLS = "POOL_CELLS"


class SharedControlPolicy(str, Enum):
    COMMON_CONTROL = "COMMON_CONTROL"
    DISJOINT_CONTROL = "DISJOINT_CONTROL"
    PARTIAL_OVERLAP = "PARTIAL_OVERLAP"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class MulticellDecisionRequirements:
    cell_relationship: str
    decision_policy: str
    shared_control_policy: str | None
    multiplicity_required: bool
    selection_adjustment_required: bool
    pooled_estimand_required: bool
    shared_control_warning_required: bool
    cross_cell_selection_allowed: bool
    pooled_readout_allowed: bool
    global_success_claim_allowed: bool
    trustreport_global_decision_allowed: bool
    diagnostic_only: bool
    marginal_per_cell_readout_allowed: bool
    allowed_claims: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    warnings: tuple[str, ...]
    readout_label: str
    fail_closed: bool
    invalid_combination: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_cell_relationship(value: str | CellRelationship) -> CellRelationship:
    if isinstance(value, CellRelationship):
        return value
    return CellRelationship(str(value))


def _parse_decision_policy(value: str | DecisionPolicy) -> DecisionPolicy:
    if isinstance(value, DecisionPolicy):
        return value
    return DecisionPolicy(str(value))


def _parse_shared_control_policy(
    value: str | SharedControlPolicy | None,
) -> SharedControlPolicy | None:
    if value is None:
        return None
    if isinstance(value, SharedControlPolicy):
        return value
    return SharedControlPolicy(str(value))


def _shared_control_warning(
  *,
    shared_control_policy: SharedControlPolicy | None,
    control_overlap_fraction: float | None,
) -> bool:
    if shared_control_policy in (SharedControlPolicy.COMMON_CONTROL, SharedControlPolicy.PARTIAL_OVERLAP):
        return True
    if control_overlap_fraction is not None and control_overlap_fraction > 0.0:
        return True
    return False


def _invalid_combination(rel: CellRelationship, pol: DecisionPolicy) -> tuple[bool, str | None]:
    if rel == CellRelationship.SINGLE_CELL and pol in (
        DecisionPolicy.SELECT_OR_RANK_CELLS,
        DecisionPolicy.DECLARE_ANY_CELL_SUCCESS,
        DecisionPolicy.POOL_CELLS,
    ):
        return True, f"{rel.value}+{pol.value} is invalid for single-cell designs"
    if rel == CellRelationship.POOLED_COMPONENT_CELLS and pol == DecisionPolicy.SELECT_OR_RANK_CELLS:
        return True, (
            f"{rel.value}+{pol.value} requires explicit component-selection scope; "
            "fail closed without it"
        )
    return False, None


def _readout_label_parallel_marginal(shared_warning: bool) -> str:
    lines = [
        "Readout mode: marginal per-cell readout.",
        "Cells answer separate business questions.",
        "Cross-cell winner selection is not authorized.",
        "Any-cell success claims are not authorized.",
        "Pooled multi-cell causal readout is not authorized.",
    ]
    if shared_warning:
        lines.append(
            "Cells share control/donor references: interpret estimates as dependent evidence streams."
        )
    return " ".join(lines)


def _readout_label_competing_select() -> str:
    return (
        "Readout mode: competing-cell selection. "
        "Per-cell marginal intervals are insufficient for selection. "
        "Multiplicity/selection-aware inference is required before choosing or ranking cells."
    )


def _readout_label_pooled_component() -> str:
    return (
        "Readout mode: pooled component cells. "
        "A pooled estimand and pooled inference are required. "
        "Per-cell intervals alone do not authorize an aggregate causal claim."
    )


def derive_multicell_decision_requirements(
    cell_relationship: str | CellRelationship,
    decision_policy: str | DecisionPolicy,
    *,
    shared_control_policy: str | SharedControlPolicy | None = None,
    control_overlap_fraction: float | None = None,
    has_corrected_multiplicity_inference: bool = False,
    has_pooled_inference: bool = False,
    component_selection_scope_declared: bool = False,
) -> MulticellDecisionRequirements:
    """Derive governance flags, allowed/blocked claims, and readout labels."""
    rel = _parse_cell_relationship(cell_relationship)
    pol = _parse_decision_policy(decision_policy)
    scp = _parse_shared_control_policy(shared_control_policy)
    shared_warn = _shared_control_warning(
        shared_control_policy=scp,
        control_overlap_fraction=control_overlap_fraction,
    )

    invalid, invalid_reason = _invalid_combination(rel, pol)
    if rel == CellRelationship.POOLED_COMPONENT_CELLS and pol == DecisionPolicy.SELECT_OR_RANK_CELLS:
        if not component_selection_scope_declared:
            invalid = True
            invalid_reason = invalid_reason or "component-selection scope not declared"

    warnings: list[str] = []
    if invalid and invalid_reason:
        warnings.append(invalid_reason)

    # Defaults — fail closed
    multiplicity_required = False
    selection_adjustment_required = False
    pooled_estimand_required = False
    cross_cell_selection_allowed = False
    pooled_readout_allowed = False
    global_success_claim_allowed = False
    trustreport_global_decision_allowed = False
    diagnostic_only = False
    marginal_per_cell_readout_allowed = False
    fail_closed = False
    readout_label = ""

    allowed: set[str] = set()
    blocked: set[str] = {
        "trust_report_global_decision",
        "pooled_multi_cell_causal_claim",
    }

    if rel == CellRelationship.UNKNOWN or invalid:
        diagnostic_only = True
        fail_closed = True
        multiplicity_required = True
        selection_adjustment_required = True
        warnings.append("UNKNOWN or invalid combination — diagnostic-only readout")
        readout_label = "Readout mode: diagnostic only. Multi-cell relationship or decision policy unresolved."
        blocked.update(
            {
                "marginal_per_cell_causal_claim",
                "any_cell_success",
                "winner_selection",
                "rank_order_decision",
                "global_multi_cell_pass_fail",
                "pooled_aggregate_causal_claim",
                "cross_cell_selection",
            }
        )
    elif rel == CellRelationship.SINGLE_CELL:
        multiplicity_required = False
        selection_adjustment_required = False
        pooled_estimand_required = False
        marginal_per_cell_readout_allowed = True
        allowed.add("marginal_per_cell_causal_claim")
        blocked.update({"any_cell_success", "winner_selection", "rank_order_decision", "cross_cell_selection"})
        readout_label = "Readout mode: single-cell readout."
    elif rel == CellRelationship.PARALLEL_MARGINAL_CELLS:
        if pol == DecisionPolicy.REPORT_EACH_CELL_ONLY:
            multiplicity_required = False
            selection_adjustment_required = False
            pooled_estimand_required = False
            marginal_per_cell_readout_allowed = True
            allowed.add("marginal_per_cell_causal_claim")
            blocked.update(
                {
                    "any_cell_success",
                    "winner_selection",
                    "rank_order_decision",
                    "global_multi_cell_pass_fail",
                    "cross_cell_selection",
                }
            )
            readout_label = _readout_label_parallel_marginal(shared_warn)
        elif pol == DecisionPolicy.SELECT_OR_RANK_CELLS:
            multiplicity_required = True
            selection_adjustment_required = True
            cross_cell_selection_allowed = has_corrected_multiplicity_inference
            marginal_per_cell_readout_allowed = True
            allowed.add("marginal_per_cell_descriptive_display")
            blocked.update({"winner_selection", "rank_order_decision", "cross_cell_selection"})
            if not has_corrected_multiplicity_inference:
                warnings.append("Selection/ranking blocked until multiplicity/selection-aware inference exists")
            readout_label = _readout_label_competing_select()
        elif pol == DecisionPolicy.DECLARE_ANY_CELL_SUCCESS:
            multiplicity_required = True
            global_success_claim_allowed = has_corrected_multiplicity_inference
            marginal_per_cell_readout_allowed = True
            allowed.add("marginal_per_cell_descriptive_display")
            blocked.add("any_cell_success")
            if not has_corrected_multiplicity_inference:
                warnings.append("Any-cell success blocked until corrected inference exists")
            readout_label = _readout_label_parallel_marginal(shared_warn)
        elif pol == DecisionPolicy.POOL_CELLS:
            fail_closed = True
            pooled_estimand_required = True
            blocked.add("marginal_per_cell_causal_claim")
            warnings.append("PARALLEL_MARGINAL_CELLS does not authorize pooled causal readout")
            readout_label = _readout_label_parallel_marginal(shared_warn)
    elif rel == CellRelationship.COMPETING_CELLS:
        selection_adjustment_required = True
        if pol == DecisionPolicy.REPORT_EACH_CELL_ONLY:
            multiplicity_required = False
            marginal_per_cell_readout_allowed = True
            allowed.add("marginal_per_cell_descriptive_display")
            blocked.update(
                {
                    "any_cell_success",
                    "winner_selection",
                    "rank_order_decision",
                    "global_multi_cell_pass_fail",
                    "cross_cell_selection",
                }
            )
            warnings.append(
                "Competing cells: marginal display only; decisioning requires selection-aware inference"
            )
            readout_label = (
                "Readout mode: competing-cell descriptive display. "
                "Per-cell marginal intervals may be shown but must not be used for selection."
            )
        elif pol == DecisionPolicy.SELECT_OR_RANK_CELLS:
            multiplicity_required = True
            cross_cell_selection_allowed = has_corrected_multiplicity_inference
            marginal_per_cell_readout_allowed = True
            allowed.add("marginal_per_cell_descriptive_display")
            blocked.update({"winner_selection", "rank_order_decision", "cross_cell_selection"})
            if not has_corrected_multiplicity_inference:
                warnings.append("Winner/rank selection blocked until corrected inference exists")
            readout_label = _readout_label_competing_select()
        elif pol == DecisionPolicy.DECLARE_ANY_CELL_SUCCESS:
            multiplicity_required = True
            global_success_claim_allowed = has_corrected_multiplicity_inference
            marginal_per_cell_readout_allowed = True
            allowed.add("marginal_per_cell_descriptive_display")
            blocked.add("any_cell_success")
            if not has_corrected_multiplicity_inference:
                warnings.append("Any-cell success blocked until corrected inference exists")
            readout_label = _readout_label_competing_select()
        elif pol == DecisionPolicy.POOL_CELLS:
            fail_closed = True
            pooled_estimand_required = True
            warnings.append("COMPETING_CELLS does not authorize pooled causal readout without pooled estimand")
            readout_label = _readout_label_competing_select()
    elif rel == CellRelationship.POOLED_COMPONENT_CELLS:
        pooled_estimand_required = True
        if pol == DecisionPolicy.POOL_CELLS:
            pooled_readout_allowed = has_pooled_inference
            marginal_per_cell_readout_allowed = True
            allowed.add("marginal_per_cell_diagnostic_display")
            blocked.add("pooled_aggregate_causal_claim")
            if not has_pooled_inference:
                warnings.append("Pooled readout blocked until explicit pooled inference exists")
            readout_label = _readout_label_pooled_component()
        else:
            fail_closed = True
            diagnostic_only = True
            warnings.append("POOLED_COMPONENT_CELLS requires POOL_CELLS decision policy for aggregate readout")
            readout_label = _readout_label_pooled_component()

    # TrustReport global decision never authorized without corrected inference
    trustreport_global_decision_allowed = False
    blocked.add("trust_report_global_decision")

    return MulticellDecisionRequirements(
        cell_relationship=rel.value,
        decision_policy=pol.value,
        shared_control_policy=scp.value if scp else None,
        multiplicity_required=multiplicity_required,
        selection_adjustment_required=selection_adjustment_required,
        pooled_estimand_required=pooled_estimand_required,
        shared_control_warning_required=shared_warn,
        cross_cell_selection_allowed=cross_cell_selection_allowed,
        pooled_readout_allowed=pooled_readout_allowed,
        global_success_claim_allowed=global_success_claim_allowed,
        trustreport_global_decision_allowed=trustreport_global_decision_allowed,
        diagnostic_only=diagnostic_only,
        marginal_per_cell_readout_allowed=marginal_per_cell_readout_allowed,
        allowed_claims=tuple(sorted(allowed)),
        blocked_claims=tuple(sorted(blocked)),
        warnings=tuple(warnings),
        readout_label=readout_label,
        fail_closed=fail_closed,
        invalid_combination=invalid,
    )


def validate_multicell_decision_policy(
    cell_relationship: str | CellRelationship,
    decision_policy: str | DecisionPolicy,
    *,
    shared_control_policy: str | SharedControlPolicy | None = None,
    control_overlap_fraction: float | None = None,
    has_corrected_multiplicity_inference: bool = False,
    has_pooled_inference: bool = False,
    component_selection_scope_declared: bool = False,
    requested_claims: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Validate a policy tuple and optional requested claims; fail closed on violations."""
    req = derive_multicell_decision_requirements(
        cell_relationship,
        decision_policy,
        shared_control_policy=shared_control_policy,
        control_overlap_fraction=control_overlap_fraction,
        has_corrected_multiplicity_inference=has_corrected_multiplicity_inference,
        has_pooled_inference=has_pooled_inference,
        component_selection_scope_declared=component_selection_scope_declared,
    )
    violations: list[str] = []
    if req.invalid_combination:
        violations.append(f"invalid combination: {req.cell_relationship}+{req.decision_policy}")
    if req.diagnostic_only and requested_claims:
        violations.append("diagnostic_only policy cannot authorize requested downstream claims")
    if requested_claims:
        for claim in requested_claims:
            if claim in req.blocked_claims:
                violations.append(f"blocked claim requested: {claim}")
    return {
        "contract_id": CONTRACT_ID,
        "contract_version": CONTRACT_VERSION,
        "valid": len(violations) == 0,
        "violations": violations,
        "requirements": req.to_dict(),
    }


def contract_metadata() -> dict[str, Any]:
    return {
        "contract_id": CONTRACT_ID,
        "contract_version": CONTRACT_VERSION,
        "investigation_id": _INVESTIGATION_ID,
        "cell_relationships": [e.value for e in CellRelationship],
        "decision_policies": [e.value for e in DecisionPolicy],
        "shared_control_policies": [e.value for e in SharedControlPolicy],
        "trust_report_authorized": False,
        "trust_report_ready": False,
    }
