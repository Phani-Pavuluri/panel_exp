"""
INVESTIGATION_LIFECYCLE_AND_HANDOFF_CONTRACT_001 — open investigation registry and artifact handoff.

Authoritative registry: docs/governance/OPEN_INVESTIGATIONS_001.json
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Sequence

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

InvestigationStatus = Literal[
    "OPEN",
    "PLANNED",
    "IN_PROGRESS",
    "BLOCKED",
    "DEFERRED_WITH_TRIGGER",
    "RESOLVED",
    "WONT_FIX",
    "SUPERSEDED",
]

ACTIVE_STATUSES = frozenset({"OPEN", "PLANNED", "IN_PROGRESS", "BLOCKED", "DEFERRED_WITH_TRIGGER"})
TERMINAL_STATUSES = frozenset({"RESOLVED", "WONT_FIX", "SUPERSEDED"})

REQUIRED_HANDOFF_KEYS = frozenset(
    {"follow_up_issues", "resolved_issues", "terminal_dispositions", "next_artifact"}
)

RESIDUAL_LANGUAGE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bissue remains\b",
        r"\binconclusive\b",
        r"\bblocked pending\b",
        r"\brequires remediation\b",
        r"\bcalibration caveat\b",
        r"\bfuture work\b",
        r"\bvariance\b.{0,40}\bunresolved\b",
        r"\bunresolved\b.{0,40}\bvariance\b",
        r"\bvariance issue remains\b",
        r"\bnull calibration\b.{0,40}\bcaveat\b",
    )
)

INVESTIGATION_ID_PATTERN = re.compile(r"INV-[A-Z0-9-]+-\d{3}")

REQUIRED_REPORT_HANDOFF_HEADING = "## Residual Issues and Handoff"

HANDOFF_REPORT_SUBSECTIONS = (
    "Resolved in this artifact",
    "New investigations opened",
    "Existing investigations updated",
    "Deferred issues",
    "Explicit exclusions",
    "Revisit trigger",
    "Required decision checkpoint",
    "Next artifact",
)


@dataclass(frozen=True)
class InvestigationRecord:
    investigation_id: str
    title: str
    status: InvestigationStatus
    priority: str
    discovered_by: str
    affected_combination: str
    problem_class: tuple[str, ...]
    current_decision: str
    blocked_roles: tuple[str, ...]
    target_artifact: str | None
    revisit_trigger: str | None
    decision_checkpoint: str | None
    blocking_policy: str | None
    terminal_decisions: tuple[str, ...]
    resolution_artifact: str | None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RegistryValidationIssue:
    code: str
    message: str
    investigation_id: str | None = None


def load_registry(path: Path | None = None) -> dict[str, Any]:
    registry_path = path or DEFAULT_REGISTRY_PATH
    return json.loads(registry_path.read_text(encoding="utf-8"))


def _parse_investigation(raw: dict[str, Any]) -> InvestigationRecord:
    return InvestigationRecord(
        investigation_id=str(raw["investigation_id"]),
        title=str(raw["title"]),
        status=raw["status"],
        priority=str(raw.get("priority", "")),
        discovered_by=str(raw.get("discovered_by", "")),
        affected_combination=str(raw.get("affected_combination", "")),
        problem_class=tuple(raw.get("problem_class") or ()),
        current_decision=str(raw.get("current_decision", "")),
        blocked_roles=tuple(raw.get("blocked_roles") or ()),
        target_artifact=raw.get("target_artifact"),
        revisit_trigger=raw.get("revisit_trigger"),
        decision_checkpoint=raw.get("decision_checkpoint"),
        blocking_policy=raw.get("blocking_policy"),
        terminal_decisions=tuple(raw.get("terminal_decisions") or ()),
        resolution_artifact=raw.get("resolution_artifact"),
        evidence=dict(raw.get("evidence") or {}),
    )


def investigations_by_id(registry: dict[str, Any] | None = None) -> dict[str, InvestigationRecord]:
    reg = registry if registry is not None else load_registry()
    return {_parse_investigation(item).investigation_id: _parse_investigation(item) for item in reg["investigations"]}


def validate_registry(registry: dict[str, Any] | None = None) -> list[RegistryValidationIssue]:
    reg = registry if registry is not None else load_registry()
    issues: list[RegistryValidationIssue] = []
    allowed_status = set(reg.get("status_vocabulary") or [])
    seen: set[str] = set()
    artifact_ids = {inv["investigation_id"] for inv in reg.get("investigations", [])}
    artifact_ids.update(
        inv.get("discovered_by", "")
        for inv in reg.get("investigations", [])
        if inv.get("discovered_by")
    )
    artifact_ids.update(
        inv.get("resolution_artifact", "")
        for inv in reg.get("investigations", [])
        if inv.get("resolution_artifact")
    )
    artifact_ids.update(
        inv.get("target_artifact", "")
        for inv in reg.get("investigations", [])
        if inv.get("target_artifact")
    )

    for raw in reg.get("investigations", []):
        inv_id = raw.get("investigation_id", "")
        if not inv_id:
            issues.append(RegistryValidationIssue("missing_id", "Investigation missing investigation_id"))
            continue
        if inv_id in seen:
            issues.append(RegistryValidationIssue("duplicate_id", f"Duplicate investigation_id: {inv_id}", inv_id))
        seen.add(inv_id)

        status = raw.get("status")
        if status not in allowed_status:
            issues.append(
                RegistryValidationIssue("invalid_status", f"Status {status!r} not in vocabulary", inv_id)
            )

        if status in ACTIVE_STATUSES:
            if not raw.get("revisit_trigger"):
                issues.append(
                    RegistryValidationIssue(
                        "missing_revisit_trigger",
                        "Active investigation missing revisit_trigger",
                        inv_id,
                    )
                )
            if not raw.get("decision_checkpoint"):
                issues.append(
                    RegistryValidationIssue(
                        "missing_decision_checkpoint",
                        "Active investigation missing decision_checkpoint",
                        inv_id,
                    )
                )
            if not raw.get("blocking_policy"):
                issues.append(
                    RegistryValidationIssue(
                        "missing_blocking_policy",
                        "Active investigation missing blocking_policy",
                        inv_id,
                    )
                )

        if status == "RESOLVED" and not raw.get("resolution_artifact"):
            issues.append(
                RegistryValidationIssue(
                    "resolved_without_artifact",
                    "RESOLVED investigation missing resolution_artifact",
                    inv_id,
                )
            )

    for binding in reg.get("roadmap_lane_bindings", []):
        if binding.get("status") != "complete":
            continue
        open_ids = binding.get("open_investigations") or []
        if open_ids and not binding.get("next_artifact"):
            issues.append(
                RegistryValidationIssue(
                    "complete_lane_open_without_next",
                    f"Lane {binding.get('lane_id')} complete with open issues but no next_artifact",
                )
            )

    return issues


def validate_artifact_handoff(
    summary: dict[str, Any],
    *,
    registry: dict[str, Any] | None = None,
) -> list[RegistryValidationIssue]:
    issues: list[RegistryValidationIssue] = []
    by_id = investigations_by_id(registry)
    handoff = summary.get("investigation_handoff")
    if not isinstance(handoff, dict):
        return [
            RegistryValidationIssue(
                "missing_handoff",
                f"Artifact {summary.get('artifact_id')} missing investigation_handoff block",
            )
        ]

    missing = REQUIRED_HANDOFF_KEYS - set(handoff.keys())
    if missing:
        issues.append(
            RegistryValidationIssue(
                "incomplete_handoff",
                f"Missing handoff keys: {sorted(missing)}",
            )
        )
        return issues

    for key in ("follow_up_issues", "resolved_issues", "terminal_dispositions"):
        if not isinstance(handoff.get(key), list):
            issues.append(RegistryValidationIssue("invalid_handoff_list", f"{key} must be a list"))
            continue
        for inv_id in handoff[key]:
            if inv_id not in by_id:
                issues.append(
                    RegistryValidationIssue(
                        "unknown_investigation_ref",
                        f"Handoff references unknown investigation: {inv_id}",
                        str(inv_id),
                    )
                )

    if handoff.get("next_artifact") is None and handoff.get("follow_up_issues"):
        issues.append(
            RegistryValidationIssue(
                "follow_up_without_next",
                "follow_up_issues present but next_artifact is null",
            )
        )

    return issues


def find_unlinked_residual_language(text: str) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if INVESTIGATION_ID_PATTERN.search(line):
            continue
        if REQUIRED_REPORT_HANDOFF_HEADING in line:
            continue
        for pattern in RESIDUAL_LANGUAGE_PATTERNS:
            if pattern.search(line):
                hits.append((line_no, line.strip()))
                break
    return hits


def validate_report_handoff_section(text: str, *, artifact_id: str | None = None) -> list[RegistryValidationIssue]:
    issues: list[RegistryValidationIssue] = []
    if REQUIRED_REPORT_HANDOFF_HEADING not in text:
        issues.append(
            RegistryValidationIssue(
                "missing_handoff_section",
                f"Report {artifact_id or ''} missing '{REQUIRED_REPORT_HANDOFF_HEADING}'",
            )
        )
        return issues

    section = text.split(REQUIRED_REPORT_HANDOFF_HEADING, 1)[1]
    for subsection in HANDOFF_REPORT_SUBSECTIONS:
        if subsection not in section:
            issues.append(
                RegistryValidationIssue(
                    "missing_handoff_subsection",
                    f"Handoff section missing subsection: {subsection}",
                )
            )

    body_before_handoff = text.split(REQUIRED_REPORT_HANDOFF_HEADING, 1)[0]
    for line_no, line in find_unlinked_residual_language(body_before_handoff):
        issues.append(
            RegistryValidationIssue(
                "unlinked_residual_language",
                f"Line {line_no}: residual language without investigation ID: {line[:120]}",
            )
        )
    return issues


def build_investigation_handoff(
    *,
    follow_up_issues: Sequence[str],
    resolved_issues: Sequence[str],
    terminal_dispositions: Sequence[str],
    next_artifact: str | None,
) -> dict[str, Any]:
    return {
        "follow_up_issues": list(follow_up_issues),
        "resolved_issues": list(resolved_issues),
        "terminal_dispositions": list(terminal_dispositions),
        "next_artifact": next_artifact,
    }


def format_handoff_report_section(
    *,
    resolved_in_artifact: Sequence[str],
    new_investigations: Sequence[str],
    updated_investigations: Sequence[str],
    deferred_issues: Sequence[str],
    explicit_exclusions: Sequence[str],
    revisit_trigger: str,
    decision_checkpoint: str,
    next_artifact: str | None,
) -> list[str]:
    def _lines(label: str, items: Sequence[str], *, none_ok: bool = False) -> list[str]:
        if not items and none_ok:
            return [f"**{label}:** none", ""]
        if not items:
            return [f"**{label}:**", ""]
        return [f"**{label}:**", *[f"- {item}" for item in items], ""]

    lines = [
        REQUIRED_REPORT_HANDOFF_HEADING,
        "",
        *_lines("Resolved in this artifact", resolved_in_artifact, none_ok=True),
        *_lines("New investigations opened", new_investigations, none_ok=True),
        *_lines("Existing investigations updated", updated_investigations, none_ok=True),
        *_lines("Deferred issues", deferred_issues, none_ok=True),
        *_lines("Explicit exclusions", explicit_exclusions, none_ok=True),
        f"**Revisit trigger:** {revisit_trigger}",
        "",
        f"**Required decision checkpoint:** {decision_checkpoint}",
        "",
        f"**Next artifact:** {next_artifact or 'none'}",
        "",
    ]
    return lines


def reconciliation_rows(registry: dict[str, Any] | None = None) -> list[dict[str, str]]:
    """Milestone reconciliation table rows for DCM / TrustReport checkpoints."""
    reg = registry if registry is not None else load_registry()
    rows: list[dict[str, str]] = []
    for inv in investigations_by_id(reg).values():
        required_now = "Yes" if inv.status in {"OPEN", "BLOCKED", "IN_PROGRESS"} else "No"
        if inv.investigation_id == "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001":
            required_now = "Yes before DCM-005"
        if inv.investigation_id == "INV-TBRRIDGE-KFOLD-NULL-FPR-001":
            required_now = "Pending lane"
        decision = inv.current_decision
        if inv.status == "RESOLVED":
            decision = "closed by correction artifact"
        rows.append(
            {
                "investigation": inv.title,
                "status": inv.status,
                "evidence_changed": "Yes" if inv.evidence else "Pending lane",
                "required_now": required_now,
                "decision": decision,
            }
        )
    return rows
