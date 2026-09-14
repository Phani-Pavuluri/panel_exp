"""Fail-closed single-source lifecycle controls for GeoX execution."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "docs/execution/EXECUTION_STATE.json"
ACTIVE_PATH = ROOT / "docs/execution/ACTIVE_TASK.md"
REPORT_PATH = ROOT / "docs/execution/LATEST_COMPLETION_REPORT.md"
BEGIN_MARKER = "<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->"
END_MARKER = "<!-- END GEOX TASKCTL EXECUTION VIEW -->"
SCHEMA_VERSION = "geox_repo_execution_state_v3"
STATES = frozenset(
    {
        "idle",
        "proposed",
        "authorized",
        "in_progress",
        "blocked",
        "ready_for_review",
        "changes_requested",
        "merged",
        "superseded",
    }
)
TRANSITIONS = {
    "idle": frozenset(),
    "proposed": frozenset({"authorized", "superseded"}),
    "authorized": frozenset({"in_progress", "blocked", "ready_for_review", "superseded"}),
    "in_progress": frozenset({"blocked", "ready_for_review", "superseded"}),
    "blocked": frozenset({"in_progress", "ready_for_review", "superseded"}),
    "ready_for_review": frozenset({"changes_requested", "merged"}),
    "changes_requested": frozenset({"in_progress", "blocked", "ready_for_review", "superseded"}),
    "merged": frozenset(),
    "superseded": frozenset(),
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
PROTECTED_AUTHORITY = (
    "capability_authorizations_changed",
    "package_or_runtime_changes_authorized",
    "producer_certification_authorized",
    "mmm_compatibility_authorized",
    "calibration_signal_authorized",
    "simulation_authorized",
    "planning_authorized",
    "recommendation_authorized",
    "real_data_authorized",
    "runtime_integration_authorized",
    "pilot_authorized",
    "production_authorized",
    "next_task_authorized",
)
SHA_FIELDS = (
    "base_sha",
    "task_authoring_head_sha",
    "authorization_head_sha",
    "authorized_branch_baseline_sha",
    "implementation_commit_sha",
    "reviewed_head_sha",
    "rejected_review_head_sha",
    "rejected_implementation_commit_sha",
    "approval_commit_sha",
)


class TaskControlError(ValueError):
    """Stable reason-coded task-control error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _display(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TaskControlError("E_DOCUMENT_READ", f"cannot read {path}: {exc}") from exc


def load_state(path: Path = STATE_PATH) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
        state = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise TaskControlError("E_STATE_PARSE", str(exc)) from exc
    if not isinstance(state, dict):
        raise TaskControlError("E_STATE_TYPE", "canonical state must be a JSON object")
    validate_state(state)
    return state


def validate_state(state: dict[str, Any]) -> None:
    if state.get("schema_version") != SCHEMA_VERSION:
        raise TaskControlError("E_SCHEMA_VERSION", f"expected {SCHEMA_VERSION}")
    if state.get("status") not in STATES:
        raise TaskControlError("E_STATUS", f"unsupported status: {state.get('status')}")
    required = (
        "task_id", "repository", "execution_mode", "base_branch", "base_sha",
        "task_authoring_head_sha", "authorization_head_sha", "authorized_branch_baseline_sha",
        "feature_branch", "feature_branch_created", "task_execution_authorized",
        "correction_execution_authorized", "merge_authorized", "pr_creation_authorized",
        "implementation_commit_sha", "reviewed_head_sha", "rejected_review_head_sha",
        "rejected_implementation_commit_sha", "approval_commit_sha", "blockers",
        "maximum_correction_cycles", "correction_cycles_completed",
        "correction_cycles_remaining", "review_decision", "local_feature_branch_cleanup",
        "remote_feature_branch_cleanup", *PROTECTED_AUTHORITY,
    )
    missing = [key for key in required if key not in state]
    if missing:
        raise TaskControlError("E_STATE_KEYS", f"missing keys: {', '.join(missing)}")
    if state["repository"] != "Phani-Pavuluri/panel_exp":
        raise TaskControlError("E_STATE_REPOSITORY", "canonical state belongs to another repository")
    if state["execution_mode"] != "branch_and_fast_forward" or state["base_branch"] != "main":
        raise TaskControlError("E_STATE_EXECUTION_MODE", "unsupported execution mode or base branch")
    if state["review_decision"] != state["status"]:
        raise TaskControlError("E_REVIEW_DECISION", "review decision must match lifecycle status")
    for field in (
        "feature_branch_created", "task_execution_authorized",
        "correction_execution_authorized", "merge_authorized", "pr_creation_authorized",
        *PROTECTED_AUTHORITY,
    ):
        if not isinstance(state[field], bool):
            raise TaskControlError("E_BOOLEAN", f"{field} must be boolean")
    for field in SHA_FIELDS:
        value = state[field]
        if value is not None and (not isinstance(value, str) or not SHA_RE.fullmatch(value)):
            raise TaskControlError("E_SHA", f"{field} must be a lowercase 40-character SHA or null")
    if not isinstance(state["feature_branch"], str) or state["feature_branch"] == "main" or not BRANCH_RE.fullmatch(state["feature_branch"]):
        raise TaskControlError("E_BRANCH", "feature branch must be valid and cannot be main")
    counters = tuple(state[key] for key in ("maximum_correction_cycles", "correction_cycles_completed", "correction_cycles_remaining"))
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counters):
        raise TaskControlError("E_CORRECTION_COUNTERS", "correction counters must be non-negative integers")
    if state["correction_cycles_completed"] + state["correction_cycles_remaining"] != state["maximum_correction_cycles"]:
        raise TaskControlError("E_CORRECTION_COUNTERS", "completed plus remaining must equal maximum")
    if not isinstance(state["blockers"], list) or any(not isinstance(item, str) or not item for item in state["blockers"]):
        raise TaskControlError("E_BLOCKERS", "blockers must be a list of nonempty strings")
    if state["merge_authorized"] or state["pr_creation_authorized"]:
        raise TaskControlError("E_AUTHORITY", "merge and PR authority must remain false")
    if any(state[key] for key in PROTECTED_AUTHORITY):
        raise TaskControlError("E_PROTECTED_AUTHORITY", "protected authority must remain false")
    rejected = state["rejected_review_head_sha"], state["rejected_implementation_commit_sha"]
    if (rejected[0] is None) != (rejected[1] is None):
        raise TaskControlError("E_REJECTED_PROVENANCE", "rejected review and implementation evidence must be paired")
    status = state["status"]
    if status in {"authorized", "in_progress"} and (not state["task_execution_authorized"] or state["blockers"]):
        raise TaskControlError("E_EXECUTION_EVIDENCE", f"{status} requires execution authority and no blockers")
    if status == "blocked" and (not state["task_execution_authorized"] or not state["blockers"]):
        raise TaskControlError("E_BLOCKED_EVIDENCE", "blocked requires execution authority and explicit blockers")
    if status == "changes_requested":
        if not state["correction_execution_authorized"] or not state["implementation_commit_sha"]:
            raise TaskControlError("E_CORRECTION_AUTHORITY", "changes requested requires correction authority and implementation")
        if not all(rejected):
            raise TaskControlError("E_REJECTED_PROVENANCE", "changes requested requires rejection provenance")
    if status == "ready_for_review":
        if not state["implementation_commit_sha"] or state["blockers"] or state["correction_execution_authorized"]:
            raise TaskControlError("E_REVIEW_EVIDENCE", "review-ready requires implementation, no blockers, and closed correction authority")
    if status == "merged":
        if state["task_execution_authorized"] or state["correction_execution_authorized"] or not state["reviewed_head_sha"]:
            raise TaskControlError("E_MERGED_EVIDENCE", "merged requires reviewed head and closed execution authority")
        if state["local_feature_branch_cleanup"] != "observed_deleted" or state["remote_feature_branch_cleanup"] != "observed_deleted":
            raise TaskControlError("E_CLEANUP", "merged requires local and remote cleanup evidence")


def render(state: dict[str, Any], document: str) -> str:
    if document not in {"active_task", "completion_report"}:
        raise TaskControlError("E_VIEW_DOCUMENT", f"unsupported generated view: {document}")
    title = "# Active Task" if document == "active_task" else "# Execution Completion Report"
    decision = f"**Status:** `{state['status']}`" if document == "active_task" else f"**Current decision:** `{state['status']}`"
    blockers = "none" if not state["blockers"] else "; ".join(state["blockers"])
    fields = (
        ("Task ID", state["task_id"]), ("Repository", state["repository"]),
        ("Execution mode", state["execution_mode"]), ("Base SHA", state["base_sha"]),
        ("Authorization provenance", state["authorization_head_sha"]),
        ("Feature branch", state["feature_branch"]), ("Feature branch created", state["feature_branch_created"]),
        ("Task execution authorized", state["task_execution_authorized"]),
        ("Correction execution authorized", state["correction_execution_authorized"]),
        ("Merge authorized", state["merge_authorized"]), ("PR creation authorized", state["pr_creation_authorized"]),
        ("Implementation commit", state["implementation_commit_sha"]), ("Reviewed head", state["reviewed_head_sha"]),
        ("Rejected review head", state["rejected_review_head_sha"]),
        ("Rejected implementation commit", state["rejected_implementation_commit_sha"]),
        ("Approval commit", state["approval_commit_sha"]), ("Blockers", blockers),
        ("Maximum correction cycles", state["maximum_correction_cycles"]),
        ("Correction cycles completed", state["correction_cycles_completed"]),
        ("Correction cycles remaining", state["correction_cycles_remaining"]),
        ("Review decision", state["review_decision"]),
        ("Local feature-branch cleanup", state["local_feature_branch_cleanup"]),
        ("Remote feature-branch cleanup", state["remote_feature_branch_cleanup"]),
        ("Capability authorizations changed", state["capability_authorizations_changed"]),
    )
    lines = [BEGIN_MARKER, title, "", decision, "", "_Generated from `EXECUTION_STATE.json`; do not edit._", ""]
    lines.extend(f"- **{label}:** `{_display(value)}`" for label, value in fields)
    return "\n".join((*lines, END_MARKER, ""))


def replace_view(text: str, block: str) -> str:
    begins, ends = text.count(BEGIN_MARKER), text.count(END_MARKER)
    if begins != 1 or ends != 1:
        raise TaskControlError("E_VIEW_MARKERS", "document must contain exactly one marker pair")
    begin, end = text.index(BEGIN_MARKER), text.index(END_MARKER)
    if end < begin:
        raise TaskControlError("E_VIEW_MARKERS", "generated markers are reversed")
    suffix = end + len(END_MARKER)
    if suffix < len(text) and text[suffix] == "\n":
        suffix += 1
    return text[:begin] + block + text[suffix:]


def _write_atomically(path: Path, content: str) -> None:
    encoded = content.encode("utf-8")
    if path.read_bytes() == encoded:
        return
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _candidate_views(state: dict[str, Any]) -> tuple[str, str]:
    active = replace_view(_read(ACTIVE_PATH), render(state, "active_task"))
    report = replace_view(_read(REPORT_PATH), render(state, "completion_report"))
    return active, report


def sync() -> None:
    state = load_state()
    active, report = _candidate_views(state)
    _write_atomically(ACTIVE_PATH, active)
    _write_atomically(REPORT_PATH, report)


def check() -> None:
    state = load_state()
    active, report = _candidate_views(state)
    if active != _read(ACTIVE_PATH) or report != _read(REPORT_PATH):
        raise TaskControlError("E_VIEW_DIVERGENCE", "generated views diverge from canonical state")


def transition(
    target: str,
    *,
    implementation_sha: str | None = None,
    complete_correction: bool = False,
) -> None:
    state = load_state()
    check()
    if target not in STATES:
        raise TaskControlError("E_STATUS", f"unsupported status: {target}")
    if target not in TRANSITIONS[state["status"]]:
        raise TaskControlError("E_TRANSITION", f"cannot transition {state['status']} -> {target}")
    if target != "ready_for_review":
        raise TaskControlError("E_TRANSITION_EVIDENCE", "only review-ready completion is available to this task")
    if not implementation_sha or not SHA_RE.fullmatch(implementation_sha):
        raise TaskControlError("E_TRANSITION_EVIDENCE", "review-ready requires an implementation SHA")
    if state["status"] == "changes_requested" and not complete_correction:
        raise TaskControlError("E_TRANSITION_CORRECTION", "correction completion must be explicit")
    candidate = copy.deepcopy(state)
    candidate["status"] = "ready_for_review"
    candidate["review_decision"] = "ready_for_review"
    candidate["implementation_commit_sha"] = implementation_sha
    candidate["blockers"] = []
    candidate["correction_execution_authorized"] = False
    if state["status"] == "changes_requested":
        candidate["correction_cycles_completed"] += 1
        candidate["correction_cycles_remaining"] -= 1
    for key in PROTECTED_AUTHORITY:
        if candidate[key] != state[key]:
            raise TaskControlError("E_PROTECTED_AUTHORITY", f"transition cannot change {key}")
    validate_state(candidate)
    active, report = _candidate_views(candidate)
    _write_atomically(STATE_PATH, json.dumps(candidate, indent=2) + "\n")
    _write_atomically(ACTIVE_PATH, active)
    _write_atomically(REPORT_PATH, report)


def main() -> int:
    parser = argparse.ArgumentParser(prog="taskctl")
    command = parser.add_subparsers(dest="command", required=True)
    command.add_parser("check")
    command.add_parser("sync")
    transition_parser = command.add_parser("transition")
    transition_parser.add_argument("--to", required=True, choices=sorted(STATES))
    transition_parser.add_argument("--implementation-sha")
    transition_parser.add_argument("--complete-correction", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "check":
            check()
        elif args.command == "sync":
            sync()
        else:
            transition(args.to, implementation_sha=args.implementation_sha, complete_correction=args.complete_correction)
    except TaskControlError as exc:
        print(exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
