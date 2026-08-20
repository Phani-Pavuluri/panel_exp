"""Single-source lifecycle controls for GeoX repository execution."""

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
STATES = {
    "idle", "proposed", "authorized", "in_progress", "blocked",
    "ready_for_review", "changes_requested", "merged", "superseded",
}
TRANSITIONS = {
    "idle": set(),
    "proposed": {"authorized", "superseded"},
    "authorized": {"in_progress", "blocked", "ready_for_review", "superseded"},
    "in_progress": {"blocked", "ready_for_review", "superseded"},
    "blocked": {"in_progress", "ready_for_review", "superseded"},
    "ready_for_review": {"changes_requested", "merged"},
    "changes_requested": {"in_progress", "blocked", "ready_for_review", "superseded"},
    "merged": set(),
    "superseded": set(),
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
PROTECTED_AUTHORITY = (
    "capability_authorizations_changed", "package_or_runtime_changes_authorized",
    "producer_certification_authorized", "mmm_compatibility_authorized",
    "calibration_signal_authorized", "simulation_authorized", "planning_authorized",
    "recommendation_authorized", "real_data_authorized", "runtime_integration_authorized",
    "pilot_authorized", "production_authorized", "next_task_authorized",
)


class TaskControlError(ValueError):
    """Stable, machine-readable task-control failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _display(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def load_state(path: Path = STATE_PATH) -> dict[str, Any]:
    try:
        state = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise TaskControlError("E_STATE_PARSE", str(exc)) from exc
    validate_state(state)
    return state


def validate_state(state: dict[str, Any]) -> None:
    if state.get("schema_version") != SCHEMA_VERSION:
        raise TaskControlError("E_SCHEMA_VERSION", "state is not geox_repo_execution_state_v3")
    status = state.get("status")
    if status not in STATES:
        raise TaskControlError("E_STATUS", f"unsupported status: {status}")
    required = (
        "task_id", "repository", "execution_mode", "base_sha", "task_authoring_head_sha",
        "authorization_head_sha", "authorized_branch_baseline_sha",
        "feature_branch", "feature_branch_created", "task_execution_authorized",
        "correction_execution_authorized", "merge_authorized", "pr_creation_authorized",
        "implementation_commit_sha", "reviewed_head_sha", "rejected_review_head_sha",
        "rejected_implementation_commit_sha", "approval_commit_sha", "blockers",
        "maximum_correction_cycles", "correction_cycles_completed",
        "correction_cycles_remaining", "capability_authorizations_changed",
    )
    missing = [key for key in required if key not in state]
    if missing:
        raise TaskControlError("E_STATE_KEYS", f"missing keys: {', '.join(missing)}")
    if state.get("repository") != "Phani-Pavuluri/panel_exp":
        raise TaskControlError("E_STATE_REPOSITORY", "canonical state belongs to another repository")
    if state.get("execution_mode") != "branch_and_fast_forward":
        raise TaskControlError("E_STATE_EXECUTION_MODE", "unsupported execution mode")
    if state.get("review_decision") != status:
        raise TaskControlError("E_REVIEW_DECISION", "review_decision must match status")
    for field in ("feature_branch_created", "task_execution_authorized",
                  "correction_execution_authorized", "merge_authorized",
                  "pr_creation_authorized", "capability_authorizations_changed"):
        if not isinstance(state.get(field), bool):
            raise TaskControlError("E_BOOLEAN", f"{field} must be boolean")
    for field in ("base_sha", "task_authoring_head_sha", "authorization_head_sha",
                  "authorized_branch_baseline_sha", "reviewed_head_sha",
                  "rejected_review_head_sha", "rejected_implementation_commit_sha",
                  "implementation_commit_sha", "approval_commit_sha"):
        value = state.get(field)
        if value is not None and (not isinstance(value, str) or not SHA_RE.fullmatch(value)):
            raise TaskControlError("E_SHA", f"{field} must be lowercase 40-character SHA or null")
    branch = state.get("feature_branch")
    if not isinstance(branch, str) or branch == "main" or not BRANCH_RE.fullmatch(branch):
        raise TaskControlError("E_BRANCH", "feature_branch must be a valid non-main branch")
    maximum = state["maximum_correction_cycles"]
    completed = state["correction_cycles_completed"]
    remaining = state["correction_cycles_remaining"]
    if any(not isinstance(value, int) or value < 0 for value in (maximum, completed, remaining)):
        raise TaskControlError("E_CORRECTION_COUNTERS", "correction counters must be non-negative integers")
    if completed + remaining != maximum:
        raise TaskControlError("E_CORRECTION_COUNTERS", "completed plus remaining must equal maximum")
    if not isinstance(state["blockers"], list) or any(not isinstance(x, str) for x in state["blockers"]):
        raise TaskControlError("E_BLOCKERS", "blockers must be a list of strings")
    if state["merge_authorized"] or state["pr_creation_authorized"]:
        raise TaskControlError("E_AUTHORITY", "merge and PR authority must remain false")
    if (state["rejected_review_head_sha"] is None) != (state["rejected_implementation_commit_sha"] is None):
        raise TaskControlError("E_REJECTED_PROVENANCE", "rejected review and implementation SHAs must be paired")
    if status == "authorized" and (not state["task_execution_authorized"] or state["blockers"]):
        raise TaskControlError("E_AUTHORIZED", "authorized requires execution authority and no blockers")
    if status == "in_progress" and (not state["task_execution_authorized"] or state["blockers"]):
        raise TaskControlError("E_IN_PROGRESS", "in_progress requires execution authority and no blockers")
    if status == "blocked" and (not state["task_execution_authorized"] or not state["blockers"]):
        raise TaskControlError("E_BLOCKED_EVIDENCE", "blocked requires execution authority and explicit blockers")
    if status == "blocked" and not state["blockers"]:
        raise TaskControlError("E_BLOCKED_EVIDENCE", "blocked state requires explicit blockers")
    if status == "ready_for_review" and (not state["implementation_commit_sha"] or state["blockers"]):
        raise TaskControlError("E_REVIEW_EVIDENCE", "ready_for_review requires implementation evidence and no blockers")
    if status == "changes_requested":
        if not state["correction_execution_authorized"] or not state["implementation_commit_sha"]:
            raise TaskControlError("E_CORRECTION_AUTHORITY", "changes_requested requires correction authority and implementation")
        if not state["rejected_review_head_sha"] or not state["rejected_implementation_commit_sha"]:
            raise TaskControlError("E_REJECTED_PROVENANCE", "changes_requested requires paired rejected provenance")
    if status == "merged" and (not state["reviewed_head_sha"] or state["task_execution_authorized"] or state["correction_execution_authorized"]):
        raise TaskControlError("E_MERGED_EVIDENCE", "merged requires reviewed head and closed execution authority")
    if status == "merged" and (state.get("local_feature_branch_cleanup") != "observed_deleted" or state.get("remote_feature_branch_cleanup") != "observed_deleted"):
        raise TaskControlError("E_CLEANUP", "merged requires explicit local and remote cleanup evidence")


def render(state: dict[str, Any], document: str) -> str:
    if document not in {"active_task", "completion_report"}:
        raise TaskControlError("E_VIEW_DOCUMENT", f"unsupported document: {document}")
    title = "# Active Task" if document == "active_task" else "# Execution Completion Report"
    decision = (f"**Status:** {state['status']}" if document == "active_task"
                else f"**Current decision:** `{state['status']}`")
    blockers = "none" if not state["blockers"] else ", ".join(state["blockers"])
    fields = (
        ("Task ID", state["task_id"]), ("Repository", state["repository"]),
        ("Execution mode", state["execution_mode"]), ("Base SHA", state["base_sha"]),
        ("Authorization provenance", state["authorization_head_sha"]),
        ("Feature branch", state["feature_branch"]),
        ("Feature branch created", state["feature_branch_created"]),
        ("Task execution authorized", state["task_execution_authorized"]),
        ("Correction execution authorized", state["correction_execution_authorized"]),
        ("Merge authorized", state["merge_authorized"]),
        ("PR creation authorized", state["pr_creation_authorized"]),
        ("Implementation commit", state["implementation_commit_sha"]),
        ("Reviewed head", state["reviewed_head_sha"]),
        ("Rejected review head", state["rejected_review_head_sha"]),
        ("Rejected implementation commit", state["rejected_implementation_commit_sha"]),
        ("Approval commit", state["approval_commit_sha"]), ("Blockers", blockers),
        ("Maximum correction cycles", state["maximum_correction_cycles"]),
        ("Correction cycles completed", state["correction_cycles_completed"]),
        ("Correction cycles remaining", state["correction_cycles_remaining"]),
        ("Review decision", state.get("review_decision")),
        ("Local feature-branch cleanup", state.get("local_feature_branch_cleanup")),
        ("Remote feature-branch cleanup", state.get("remote_feature_branch_cleanup")),
        ("Capability authorizations changed", state["capability_authorizations_changed"]),
    )
    lines = [BEGIN_MARKER, title, "", decision, "",
             "_Generated from `EXECUTION_STATE.json`; do not edit._", ""]
    lines.extend(f"- **{label}:** `{_display(value)}`" for label, value in fields)
    lines.extend((END_MARKER, ""))
    return "\n".join(lines)


def replace_view(text: str, block: str) -> str:
    if text.count(BEGIN_MARKER) != 1 or text.count(END_MARKER) != 1:
        raise TaskControlError("E_VIEW_MARKERS", "document must contain exactly one marker pair")
    begin = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER)
    if end < begin:
        raise TaskControlError("E_VIEW_MARKERS", "generated markers are reversed")
    inner = text[begin + len(BEGIN_MARKER):end]
    if BEGIN_MARKER in inner or END_MARKER in inner:
        raise TaskControlError("E_VIEW_MARKERS", "generated markers cannot be nested")
    suffix = end + len(END_MARKER)
    if suffix < len(text) and text[suffix] == "\n":
        suffix += 1
    return text[:begin] + block + text[suffix:]


def _insert_initial_view(text: str, block: str) -> str:
    if BEGIN_MARKER not in text and END_MARKER not in text:
        return block + text
    return replace_view(text, block)


def sync() -> None:
    state = load_state()
    active = replace_view(ACTIVE_PATH.read_text(), render(state, "active_task"))
    report = replace_view(REPORT_PATH.read_text(), render(state, "completion_report"))
    for path, content in ((ACTIVE_PATH, active), (REPORT_PATH, report)):
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "w") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)


def check() -> None:
    state = load_state()
    for path, document in ((ACTIVE_PATH, "active_task"), (REPORT_PATH, "completion_report")):
        text = path.read_text()
        if replace_view(text, render(state, document)) != text:
            raise TaskControlError("E_VIEW_DIVERGENCE", f"{path.name} diverges from canonical state")


def transition(target: str, *, implementation_sha: str | None = None,
               rejected_review_sha: str | None = None,
               rejected_implementation_sha: str | None = None,
               reviewed_head_sha: str | None = None,
               blockers: list[str] | None = None,
               clear_blockers: bool = False,
               authorize_execution: bool = False,
               authorize_correction: bool = False,
               complete_correction: bool = False,
               authorization_head_sha: str | None = None,
               task_authoring_head_sha: str | None = None,
               local_cleanup: str | None = None,
               remote_cleanup: str | None = None) -> None:
    state = load_state()
    check()
    if target not in STATES:
        raise TaskControlError("E_STATUS", f"unsupported status: {target}")
    if target not in TRANSITIONS[state["status"]]:
        raise TaskControlError("E_TRANSITION", f"cannot transition {state['status']} -> {target}")
    candidate = copy.deepcopy(state)
    candidate["status"] = target
    candidate["review_decision"] = target
    if clear_blockers:
        candidate["blockers"] = []
    if blockers:
        candidate["blockers"] = list(blockers)
    if implementation_sha is not None:
        candidate["implementation_commit_sha"] = implementation_sha
    if target == "authorized":
        if not authorize_execution or not authorization_head_sha or not task_authoring_head_sha:
            raise TaskControlError("E_TRANSITION_EVIDENCE", "authorized requires explicit authorization provenance")
        candidate["task_execution_authorized"] = True
        candidate["authorization_head_sha"] = authorization_head_sha
        candidate["task_authoring_head_sha"] = task_authoring_head_sha
    elif target == "blocked":
        if not blockers:
            raise TaskControlError("E_TRANSITION_BLOCKER", "blocked requires explicit blockers")
    elif target == "ready_for_review":
        if not implementation_sha:
            raise TaskControlError("E_TRANSITION_EVIDENCE", "ready_for_review requires implementation SHA")
        if state["blockers"] and not clear_blockers:
            raise TaskControlError("E_TRANSITION_BLOCKER", "clear blockers explicitly before review")
        candidate["blockers"] = []
        candidate["correction_execution_authorized"] = False
        if state["status"] == "changes_requested":
            if not complete_correction:
                raise TaskControlError("E_TRANSITION_CORRECTION", "correction completion must be explicit")
            candidate["correction_cycles_completed"] += 1
            candidate["correction_cycles_remaining"] -= 1
    elif target == "changes_requested":
        if not authorize_correction or not rejected_review_sha or not rejected_implementation_sha:
            raise TaskControlError("E_TRANSITION_EVIDENCE", "changes_requested requires rejection provenance and correction authorization")
        candidate["rejected_review_head_sha"] = rejected_review_sha
        candidate["rejected_implementation_commit_sha"] = rejected_implementation_sha
        candidate["correction_execution_authorized"] = True
    elif target == "merged":
        if not reviewed_head_sha or local_cleanup != "observed_deleted" or remote_cleanup != "observed_deleted":
            raise TaskControlError("E_TRANSITION_EVIDENCE", "merged requires reviewed head and explicit cleanup evidence")
        candidate["reviewed_head_sha"] = reviewed_head_sha
        candidate["task_execution_authorized"] = False
        candidate["correction_execution_authorized"] = False
        candidate["feature_branch_created"] = False
        candidate["local_feature_branch_cleanup"] = local_cleanup
        candidate["remote_feature_branch_cleanup"] = remote_cleanup
    elif target in {"idle", "superseded"}:
        candidate["task_execution_authorized"] = False
        candidate["correction_execution_authorized"] = False
    for key in PROTECTED_AUTHORITY:
        if candidate.get(key) != state.get(key):
            raise TaskControlError("E_PROTECTED_AUTHORITY", f"transition cannot change {key}")
    validate_state(candidate)
    active = replace_view(ACTIVE_PATH.read_text(), render(candidate, "active_task"))
    report = replace_view(REPORT_PATH.read_text(), render(candidate, "completion_report"))
    state_text = json.dumps(candidate, indent=2) + "\n"
    replacements = ((STATE_PATH, state_text), (ACTIVE_PATH, active), (REPORT_PATH, report))
    temps: list[tuple[Path, str]] = []
    try:
        for path, content in replacements:
            fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
            with os.fdopen(fd, "w") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            temps.append((path, temp_name))
        for path, temp_name in temps:
            os.replace(temp_name, path)
    finally:
        for _, temp_name in temps:
            if os.path.exists(temp_name):
                os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser(prog="taskctl")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    sub.add_parser("sync")
    transition_parser = sub.add_parser("transition")
    transition_parser.add_argument("--to", required=True, choices=sorted(STATES))
    transition_parser.add_argument("--implementation-sha")
    transition_parser.add_argument("--rejected-review-sha")
    transition_parser.add_argument("--rejected-implementation-sha")
    transition_parser.add_argument("--reviewed-head-sha")
    transition_parser.add_argument("--blocker", action="append", default=[])
    transition_parser.add_argument("--clear-blockers", action="store_true")
    transition_parser.add_argument("--authorize-execution", action="store_true")
    transition_parser.add_argument("--authorize-correction", action="store_true")
    transition_parser.add_argument("--complete-correction", action="store_true")
    transition_parser.add_argument("--authorization-head-sha")
    transition_parser.add_argument("--task-authoring-head-sha")
    transition_parser.add_argument("--local-branch-cleanup")
    transition_parser.add_argument("--remote-branch-cleanup")
    args = parser.parse_args()
    try:
        if args.command == "check":
            check()
        elif args.command == "sync":
            sync()
        else:
            transition(args.to, implementation_sha=args.implementation_sha,
                       rejected_review_sha=args.rejected_review_sha,
                       rejected_implementation_sha=args.rejected_implementation_sha,
                       reviewed_head_sha=args.reviewed_head_sha, blockers=args.blocker,
                       clear_blockers=args.clear_blockers,
                       authorize_execution=args.authorize_execution,
                       authorize_correction=args.authorize_correction,
                       complete_correction=args.complete_correction,
                       authorization_head_sha=args.authorization_head_sha,
                       task_authoring_head_sha=args.task_authoring_head_sha,
                       local_cleanup=args.local_branch_cleanup,
                       remote_cleanup=args.remote_branch_cleanup)
    except TaskControlError as exc:
        print(str(exc))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
