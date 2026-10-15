"""Fail-closed single-source lifecycle controls for GeoX execution."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "docs/execution/EXECUTION_STATE.json"
ACTIVE_PATH = ROOT / "docs/execution/ACTIVE_TASK.md"
REPORT_PATH = ROOT / "docs/execution/LATEST_COMPLETION_REPORT.md"
BEGIN_MARKER = "<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->"
END_MARKER = "<!-- END GEOX TASKCTL EXECUTION VIEW -->"
SCHEMA_VERSION = "geox_repo_execution_state_v5"
LEGACY_SCHEMA_VERSION_V3 = "geox_repo_execution_state_v3"
SUPPORTED_TARGET_SCHEMAS = frozenset(
    {
        "geox_repo_execution_state_v3",
        "geox_repo_execution_state_v4",
    }
)
REJECTION_HISTORY_KEY = "rejection_history"
TARGET_DISPOSITION_BLOCKED = "blocked"
REJECTION_ENTRY_KEYS = frozenset(
    {
        "target_repository",
        "target_task_id",
        "target_branch",
        "target_head_sha",
        "target_implementation_sha",
        "target_authorization_head_sha",
        "target_branch_baseline_sha",
        "target_schema_version",
        "target_disposition",
        "target_counters",
        "prior_rejected_review_head_sha",
        "prior_rejected_implementation_commit_sha",
        "finding",
        "resolution_condition",
        "live_main_sha",
        "blockers",
    }
)
TARGET_COUNTER_KEYS = frozenset({"maximum", "completed", "remaining"})
TARGET_STATE_PATH = "docs/execution/EXECUTION_STATE.json"
RECORDABLE_LIVE_STATUSES = frozenset({"authorized", "in_progress"})
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


def _validate_target_counters(counters: object) -> None:
    if not isinstance(counters, dict):
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", "target counters must be an object")
    if set(counters) != TARGET_COUNTER_KEYS:
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", "target counters have incorrect keys")
    values = tuple(counters[key] for key in ("maximum", "completed", "remaining"))
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in values):
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", "target counters must be non-negative integers")
    if counters["completed"] + counters["remaining"] != counters["maximum"]:
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", "target completed plus remaining must equal maximum")


def _validate_rejection_entry(entry: object) -> None:
    if not isinstance(entry, dict):
        raise TaskControlError("E_REJECTION_EVIDENCE", "rejection history entry must be an object")
    missing = REJECTION_ENTRY_KEYS - entry.keys()
    if missing:
        raise TaskControlError("E_REJECTION_EVIDENCE", f"rejection entry missing keys: {', '.join(sorted(missing))}")
    extra = entry.keys() - REJECTION_ENTRY_KEYS
    if extra:
        raise TaskControlError("E_REJECTION_EVIDENCE", f"rejection entry unexpected keys: {', '.join(sorted(extra))}")
    if entry["target_repository"] != "Phani-Pavuluri/panel_exp":
        raise TaskControlError("E_REJECTION_IDENTITY", "rejection entry belongs to another repository")
    for field in ("target_task_id", "target_branch"):
        value = entry[field]
        if not isinstance(value, str) or not value.strip():
            raise TaskControlError("E_REJECTION_IDENTITY", f"rejection entry {field} must be a nonempty string")
    for field in (
        "target_head_sha",
        "target_implementation_sha",
        "target_authorization_head_sha",
        "target_branch_baseline_sha",
        "live_main_sha",
    ):
        value = entry[field]
        if not isinstance(value, str) or not SHA_RE.fullmatch(value):
            raise TaskControlError("E_SHA", f"rejection entry {field} must be a lowercase 40-character SHA")
    if not isinstance(entry.get("target_schema_version"), str) or entry["target_schema_version"] not in SUPPORTED_TARGET_SCHEMAS:
        raise TaskControlError("E_REJECTION_SCHEMA", "rejection entry targets an unsupported schema")
    if entry["target_disposition"] != TARGET_DISPOSITION_BLOCKED:
        raise TaskControlError("E_REJECTION_EVIDENCE", "rejection entry disposition must be blocked")
    _validate_target_counters(entry["target_counters"])
    if entry["target_counters"]["remaining"] != 0 or entry["target_counters"]["completed"] != entry["target_counters"]["maximum"]:
        raise TaskControlError("E_REJECTION_BUDGET", "rejection entry target must be exhausted")
    prior = entry["prior_rejected_review_head_sha"], entry["prior_rejected_implementation_commit_sha"]
    for value in prior:
        if value is not None and (not isinstance(value, str) or not SHA_RE.fullmatch(value)):
            raise TaskControlError("E_SHA", "prior rejected provenance must be SHAs or null")
    if (prior[0] is None) != (prior[1] is None):
        raise TaskControlError("E_REJECTED_PROVENANCE", "prior rejected provenance must be paired")
    for field in ("finding", "resolution_condition"):
        value = entry[field]
        if not isinstance(value, str) or not value.strip():
            raise TaskControlError("E_REJECTION_EVIDENCE", f"rejection entry {field} must be nonempty")
    if entry["target_head_sha"] not in entry["finding"] or entry["target_implementation_sha"] not in entry["finding"]:
        raise TaskControlError("E_REJECTION_EVIDENCE", "rejection entry finding must name head and implementation")
    blockers = entry["blockers"]
    if not isinstance(blockers, list) or not blockers or any(not isinstance(item, str) or not item.strip() for item in blockers):
        raise TaskControlError("E_BLOCKERS", "rejection entry blockers must be a nonempty list of nonempty strings")
    if len(set(blockers)) != len(blockers):
        raise TaskControlError("E_BLOCKERS", "rejection entry blockers must be unique")


def validate_state(state: dict[str, Any]) -> None:
    schema = state.get("schema_version")
    if schema not in {SCHEMA_VERSION, LEGACY_SCHEMA_VERSION_V3}:
        raise TaskControlError("E_SCHEMA_VERSION", f"expected {SCHEMA_VERSION}")
    if schema == LEGACY_SCHEMA_VERSION_V3 and REJECTION_HISTORY_KEY in state:
        raise TaskControlError("E_STATE_KEYS", "v3 state must not carry rejection history")
    if schema == SCHEMA_VERSION:
        if "completion_evidence" in state:
            raise TaskControlError("E_STATE_KEYS", "route-only v5 state must not carry completion evidence")
        history = state.get(REJECTION_HISTORY_KEY)
        if not isinstance(history, list):
            raise TaskControlError("E_STATE_KEYS", "v5 state requires a rejection history list")
        for entry in history:
            _validate_rejection_entry(entry)
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


def _render_rejection_history(state: dict[str, Any]) -> list[str]:
    lines = ["", "## Rejection history", ""]
    history = state.get(REJECTION_HISTORY_KEY)
    if not isinstance(history, list):
        raise TaskControlError("E_STATE_KEYS", "v5 state requires a rejection history list")
    if not history:
        return [*lines, "- none"]
    for entry in history:
        _validate_rejection_entry(entry)
        counters = entry["target_counters"]
        assert isinstance(counters, dict)
        prior_review = _display(entry["prior_rejected_review_head_sha"])
        prior_implementation = _display(entry["prior_rejected_implementation_commit_sha"])
        lines.append(
            f"- `{entry['target_task_id']}` on `{entry['target_branch']}` "
            f"head `{entry['target_head_sha']}` implementation `{entry['target_implementation_sha']}` "
            f"(schema `{entry['target_schema_version']}`, disposition `{entry['target_disposition']}`)"
        )
        lines.append(
            f"  - authorization `{entry['target_authorization_head_sha']}`, "
            f"baseline `{entry['target_branch_baseline_sha']}`, "
            f"counters {counters['maximum']}/{counters['completed']}/{counters['remaining']}, "
            f"prior `{prior_review}` / `{prior_implementation}`"
        )
        lines.append(f"  - finding: {entry['finding']}")
        lines.append(f"  - resolution: {entry['resolution_condition']}")
        lines.append(f"  - live main `{entry['live_main_sha']}`; blockers: {'; '.join(entry['blockers'])}")
    return lines


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
    if document == "completion_report" and state.get("schema_version") == SCHEMA_VERSION:
        lines.extend(_render_rejection_history(state))
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


def _rendered_views(state: dict[str, Any], active_text: str, report_text: str) -> tuple[str, str]:
    return (
        replace_view(active_text, render(state, "active_task")),
        replace_view(report_text, render(state, "completion_report")),
    )


def _candidate_views(state: dict[str, Any]) -> tuple[str, str]:
    return _rendered_views(state, _read(ACTIVE_PATH), _read(REPORT_PATH))


def sync(
    *,
    state_path: Path = STATE_PATH,
    active_path: Path = ACTIVE_PATH,
    report_path: Path = REPORT_PATH,
) -> None:
    state = load_state(state_path)
    active, report = _rendered_views(state, _read(active_path), _read(report_path))
    _write_atomically(active_path, active)
    _write_atomically(report_path, report)


def check(
    *,
    state_path: Path = STATE_PATH,
    active_path: Path = ACTIVE_PATH,
    report_path: Path = REPORT_PATH,
) -> None:
    state = load_state(state_path)
    active, report = _rendered_views(state, _read(active_path), _read(report_path))
    if active != _read(active_path) or report != _read(report_path):
        raise TaskControlError("E_VIEW_DIVERGENCE", "generated views diverge from canonical state")


class _GitError(Exception):
    """Internal git plumbing failure; callers map it to a stable reason code."""

    def __init__(self, argv: list[str], returncode: int | None, stderr: str) -> None:
        super().__init__(f"git {' '.join(argv)} failed: {stderr.strip() or returncode}")
        self.argv = argv
        self.returncode = returncode


def _git_bytes(repo: Path, *args: str) -> bytes:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise _GitError(["git", *args], None, str(exc)) from exc
    if proc.returncode != 0:
        raise _GitError(["git", *args], proc.returncode, proc.stderr.decode("utf-8", errors="replace"))
    return proc.stdout


def _git(repo: Path, *args: str) -> str:
    try:
        return _git_bytes(repo, *args).decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise _GitError(["git", *args], 0, f"non-utf8 output: {exc}") from exc


def _git_is_ancestor(repo: Path, ancestor: str, head: str) -> bool:
    try:
        _git(repo, "merge-base", "--is-ancestor", ancestor, head)
    except _GitError as exc:
        if exc.returncode == 1:
            return False
        raise
    return True


BLOB_REQUIRED_KEYS = frozenset(
    {
        "repository",
        "execution_mode",
        "base_branch",
        "task_id",
        "feature_branch",
        "status",
        "authorization_head_sha",
        "authorized_branch_baseline_sha",
        "implementation_commit_sha",
        "rejected_review_head_sha",
        "rejected_implementation_commit_sha",
        "task_execution_authorized",
        "correction_execution_authorized",
        "maximum_correction_cycles",
        "correction_cycles_completed",
        "correction_cycles_remaining",
        "blockers",
        "merge_authorized",
        "pr_creation_authorized",
        *PROTECTED_AUTHORITY,
    }
)


def _read_target_blob(repo: Path, head: str) -> dict[str, Any]:
    try:
        raw = _git_bytes(repo, "show", f"{head}:{TARGET_STATE_PATH}")
    except _GitError as exc:
        raise TaskControlError("E_REJECTION_BLOB_MISSING", f"cannot produce target blob at {head}: {exc}") from exc
    try:
        text = raw.decode("utf-8")
        blob = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", f"target blob is unreadable: {exc}") from exc
    if not isinstance(blob, dict):
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", "target blob must be a JSON object")
    if not isinstance(blob.get("schema_version"), str) or blob.get("schema_version") not in SUPPORTED_TARGET_SCHEMAS:
        raise TaskControlError("E_REJECTION_SCHEMA", "target blob schema is not supported")
    missing = BLOB_REQUIRED_KEYS - blob.keys()
    if missing:
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", f"target blob missing keys: {', '.join(sorted(missing))}")
    for field in ("repository", "task_id", "feature_branch", "status", "execution_mode", "base_branch"):
        if not isinstance(blob[field], str):
            raise TaskControlError("E_REJECTION_BLOB_CORRUPT", f"target blob {field} must be a string")
    if blob["execution_mode"] != "branch_and_fast_forward" or blob["base_branch"] != "main":
        raise TaskControlError("E_REJECTION_IDENTITY", "target blob execution regime is not supported")
    for field in (
        "task_execution_authorized",
        "correction_execution_authorized",
        "merge_authorized",
        "pr_creation_authorized",
        *PROTECTED_AUTHORITY,
    ):
        if not isinstance(blob[field], bool):
            raise TaskControlError("E_REJECTION_BLOB_CORRUPT", f"target blob {field} must be a boolean")
    for field in ("authorization_head_sha", "authorized_branch_baseline_sha", "implementation_commit_sha"):
        value = blob[field]
        if not isinstance(value, str) or not SHA_RE.fullmatch(value):
            raise TaskControlError("E_REJECTION_BLOB_CORRUPT", f"target blob {field} must be a SHA")
    rejected = blob["rejected_review_head_sha"], blob["rejected_implementation_commit_sha"]
    for value in rejected:
        if value is not None and (not isinstance(value, str) or not SHA_RE.fullmatch(value)):
            raise TaskControlError("E_REJECTION_BLOB_CORRUPT", "target blob rejected provenance must be SHAs or null")
    if (rejected[0] is None) != (rejected[1] is None):
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", "target blob rejected provenance must be paired")
    if not isinstance(blob["blockers"], list):
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", "target blob blockers must be a list")
    return blob


def _normalize_blockers(blockers: object) -> list[str]:
    if not isinstance(blockers, list) or not blockers:
        raise TaskControlError("E_BLOCKERS", "blockers must be a nonempty list")
    normalized = []
    for item in blockers:
        if not isinstance(item, str) or not item.strip():
            raise TaskControlError("E_BLOCKERS", "blockers must contain nonempty strings")
        candidate_item = item.strip()
        if candidate_item not in normalized:
            normalized.append(candidate_item)
    return normalized


def record_rejection(
    *,
    dependency_id: str,
    rejected_head_sha: str,
    rejected_implementation_sha: str,
    blockers: list[str],
    finding: str,
    resolution_condition: str,
    live_main_sha: str | None = None,
    state_path: Path = STATE_PATH,
    active_path: Path = ACTIVE_PATH,
    report_path: Path = REPORT_PATH,
    repo: Path = ROOT,
) -> dict[str, Any]:
    state = load_state(state_path)
    active_text, report_text = _read(active_path), _read(report_path)
    expected_active, expected_report = _rendered_views(state, active_text, report_text)
    if expected_active != active_text or expected_report != report_text:
        raise TaskControlError("E_VIEW_DIVERGENCE", "generated views diverge from canonical state")
    for label, sha in (("rejected head", rejected_head_sha), ("rejected implementation", rejected_implementation_sha)):
        if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
            raise TaskControlError("E_SHA", f"{label} must be a lowercase 40-character SHA")
    if live_main_sha is not None and (not isinstance(live_main_sha, str) or not SHA_RE.fullmatch(live_main_sha)):
        raise TaskControlError("E_SHA", "live main must be a lowercase 40-character SHA or null")
    if not isinstance(dependency_id, str) or not dependency_id.strip():
        raise TaskControlError("E_REJECTION_IDENTITY", "dependency id must be a nonempty string")
    normalized_blockers = _normalize_blockers(blockers)
    for label, text in (("finding", finding), ("resolution condition", resolution_condition)):
        if not isinstance(text, str) or not text.strip():
            raise TaskControlError("E_REJECTION_EVIDENCE", f"{label} must be nonempty")
    if state.get("status") not in RECORDABLE_LIVE_STATUSES:
        raise TaskControlError("E_TRANSITION", "live task cannot record a rejection from its status")
    if not state.get("task_execution_authorized"):
        raise TaskControlError("E_REJECTION_IDENTITY", "live task lacks execution authority")
    if state.get("correction_execution_authorized"):
        raise TaskControlError("E_TRANSITION", "live task has open correction authority")
    if state.get("blockers"):
        raise TaskControlError("E_TRANSITION", "live task has blockers")
    if state.get("merge_authorized") or state.get("pr_creation_authorized"):
        raise TaskControlError("E_AUTHORITY", "merge and PR authority must remain false")
    if any(state.get(key) for key in PROTECTED_AUTHORITY):
        raise TaskControlError("E_PROTECTED_AUTHORITY", "protected authority must remain false")
    try:
        current_branch = _git(repo, "branch", "--show-current")
        head_sha = _git(repo, "rev-parse", "HEAD")
    except _GitError as exc:
        raise TaskControlError("E_REJECTION_IDENTITY", f"cannot establish live branch identity: {exc}") from exc
    if current_branch != state.get("feature_branch"):
        raise TaskControlError("E_REJECTION_IDENTITY", "checked-out branch differs from live feature branch")
    for field in ("authorization_head_sha", "authorized_branch_baseline_sha"):
        value = state[field]
        if not isinstance(value, str) or not SHA_RE.fullmatch(value):
            raise TaskControlError("E_REJECTION_IDENTITY", "live authorization SHAs must be valid")
        try:
            anchored = _git_is_ancestor(repo, value, head_sha)
        except _GitError as exc:
            raise TaskControlError("E_REJECTION_IDENTITY", f"cannot verify live authorization ancestry: {exc}") from exc
        if not anchored:
            raise TaskControlError("E_REJECTION_IDENTITY", "live authorization is not an ancestor of HEAD")
    try:
        origin_url = _git(repo, "remote", "get-url", "origin")
    except _GitError as exc:
        raise TaskControlError("E_REJECTION_IDENTITY", f"cannot verify live repository origin identity: {exc}") from exc
    if state.get("repository") not in origin_url:
        raise TaskControlError("E_REJECTION_IDENTITY", "live repository origin identity mismatch")
    try:
        tracked = _git(repo, "status", "--porcelain=v1", "--untracked-files=no")
    except _GitError as exc:
        raise TaskControlError("E_REJECTION_IDENTITY", f"cannot verify clean tracked worktree: {exc}") from exc
    if tracked:
        raise TaskControlError("E_TRANSITION", "tracked worktree is not clean")
    pin = next(
        (
            item
            for item in state.get("dependencies", [])
            if isinstance(item, dict) and item.get("dependency_id") == dependency_id
        ),
        None,
    )
    if pin is None:
        raise TaskControlError("E_REJECTION_IDENTITY", "dependency pin is missing")
    if pin.get("remote_head_sha") != rejected_head_sha or pin.get("implementation_commit_sha") != rejected_implementation_sha:
        raise TaskControlError("E_REJECTION_IDENTITY", "dependency pin disagrees with rejected head and implementation")
    try:
        _git(repo, "fetch", "--prune", "origin")
    except _GitError as exc:
        raise TaskControlError("E_STALE_MAIN", f"cannot observe live main: {exc}") from exc
    try:
        main_sha = _git(repo, "rev-parse", "main")
        origin_main_sha = _git(repo, "rev-parse", "origin/main")
    except _GitError as exc:
        raise TaskControlError("E_STALE_MAIN", f"cannot observe live main: {exc}") from exc
    if main_sha != origin_main_sha:
        raise TaskControlError("E_STALE_MAIN", "live main differs from origin main")
    if live_main_sha is not None and live_main_sha != origin_main_sha:
        raise TaskControlError("E_STALE_MAIN", "supplied live main differs from observed origin main")
    try:
        object_type = _git(repo, "cat-file", "-t", rejected_head_sha)
    except _GitError as exc:
        raise TaskControlError("E_REJECTION_BLOB_MISSING", f"cannot type rejected head: {exc}") from exc
    if object_type != "commit":
        raise TaskControlError("E_REJECTION_HEAD", "rejected head is not a commit")
    blob = _read_target_blob(repo, rejected_head_sha)
    if blob.get("repository") != state.get("repository"):
        raise TaskControlError("E_REJECTION_IDENTITY", "target blob belongs to another repository")
    if blob.get("task_id") != pin.get("task_id") or blob.get("feature_branch") != pin.get("branch"):
        raise TaskControlError("E_REJECTION_IDENTITY", "target blob identity disagrees with dependency pin")
    if blob.get("status") != "ready_for_review":
        raise TaskControlError("E_TRANSITION", "target is not review-ready")
    if not blob.get("task_execution_authorized"):
        raise TaskControlError("E_TRANSITION", "target lacks execution authority")
    if blob.get("correction_execution_authorized"):
        raise TaskControlError("E_REJECTION_BUDGET", "target correction authority is open")
    if blob.get("blockers"):
        raise TaskControlError("E_TRANSITION", "target has blockers")
    if blob.get("merge_authorized") or blob.get("pr_creation_authorized"):
        raise TaskControlError("E_AUTHORITY", "target merge or PR authority is set")
    if any(blob.get(key) for key in PROTECTED_AUTHORITY):
        raise TaskControlError("E_PROTECTED_AUTHORITY", "target protected authority is set")
    counters = tuple(blob.get(key) for key in ("maximum_correction_cycles", "correction_cycles_completed", "correction_cycles_remaining"))
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counters):
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", "target counters must be non-negative integers")
    if counters[1] + counters[2] != counters[0]:
        raise TaskControlError("E_REJECTION_BLOB_CORRUPT", "target completed plus remaining must equal maximum")
    if counters[2] != 0 or counters[1] != counters[0]:
        raise TaskControlError("E_REJECTION_BUDGET", "target is not exhausted")
    if rejected_implementation_sha != blob.get("implementation_commit_sha"):
        raise TaskControlError("E_REJECTION_IMPLEMENTATION", "rejected implementation disagrees with target blob")
    for field, code in (
        ("implementation_commit_sha", "E_REJECTION_IMPLEMENTATION"),
        ("authorization_head_sha", "E_REJECTION_IDENTITY"),
        ("authorized_branch_baseline_sha", "E_REJECTION_IDENTITY"),
    ):
        try:
            anchored = _git_is_ancestor(repo, blob[field], rejected_head_sha)
        except _GitError as exc:
            raise TaskControlError(code, f"cannot verify target ancestry: {exc}") from exc
        if not anchored:
            raise TaskControlError(code, "target ancestry is not anchored at the rejected head")
    try:
        remote_line = _git(repo, "ls-remote", "origin", f"refs/heads/{blob['feature_branch']}")
    except _GitError as exc:
        raise TaskControlError("E_REJECTION_BLOB_MISSING", f"cannot observe target remote ref: {exc}") from exc
    remote_heads = [line.split("\t", 1)[0] for line in remote_line.splitlines() if line.strip()]
    if len(remote_heads) != 1 or remote_heads[0] != rejected_head_sha:
        raise TaskControlError("E_REJECTION_HEAD", "observed target remote ref disagrees with rejected head")
    if rejected_head_sha not in finding or rejected_implementation_sha not in finding:
        raise TaskControlError("E_REJECTION_EVIDENCE", "finding must name rejected head and implementation")
    history = state.get(REJECTION_HISTORY_KEY, [])
    if any(
        isinstance(item, dict)
        and item.get("target_head_sha") == rejected_head_sha
        and item.get("target_implementation_sha") == rejected_implementation_sha
        for item in history
    ):
        raise TaskControlError("E_TRANSITION", "rejection is already recorded")
    entry = {
        "target_repository": blob["repository"],
        "target_task_id": blob["task_id"],
        "target_branch": blob["feature_branch"],
        "target_head_sha": rejected_head_sha,
        "target_implementation_sha": rejected_implementation_sha,
        "target_authorization_head_sha": blob["authorization_head_sha"],
        "target_branch_baseline_sha": blob["authorized_branch_baseline_sha"],
        "target_schema_version": blob["schema_version"],
        "target_disposition": TARGET_DISPOSITION_BLOCKED,
        "target_counters": {
            "maximum": blob["maximum_correction_cycles"],
            "completed": blob["correction_cycles_completed"],
            "remaining": blob["correction_cycles_remaining"],
        },
        "prior_rejected_review_head_sha": blob["rejected_review_head_sha"],
        "prior_rejected_implementation_commit_sha": blob["rejected_implementation_commit_sha"],
        "finding": finding.strip(),
        "resolution_condition": resolution_condition.strip(),
        "live_main_sha": origin_main_sha,
        "blockers": normalized_blockers,
    }
    candidate = copy.deepcopy(state)
    if candidate.get("schema_version") == LEGACY_SCHEMA_VERSION_V3:
        candidate["schema_version"] = SCHEMA_VERSION
        candidate[REJECTION_HISTORY_KEY] = []
    candidate[REJECTION_HISTORY_KEY].append(entry)
    for key in PROTECTED_AUTHORITY:
        if candidate[key] != state[key]:
            raise TaskControlError("E_PROTECTED_AUTHORITY", f"record cannot change {key}")
    validate_state(candidate)
    active, report = _rendered_views(candidate, active_text, report_text)
    _write_atomically(state_path, json.dumps(candidate, indent=2) + "\n")
    _write_atomically(active_path, active)
    _write_atomically(report_path, report)
    return entry


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
    record_parser = command.add_parser("record-rejection")
    record_parser.add_argument("--dependency-id", required=True)
    record_parser.add_argument("--rejected-head", required=True)
    record_parser.add_argument("--rejected-implementation", required=True)
    record_parser.add_argument("--blocker", required=True, action="append")
    record_parser.add_argument("--finding", required=True)
    record_parser.add_argument("--resolution-condition", required=True)
    record_parser.add_argument("--live-main")
    args = parser.parse_args()
    try:
        if args.command == "check":
            check()
        elif args.command == "sync":
            sync()
        elif args.command == "record-rejection":
            record_rejection(
                dependency_id=args.dependency_id,
                rejected_head_sha=args.rejected_head,
                rejected_implementation_sha=args.rejected_implementation,
                blockers=args.blocker,
                finding=args.finding,
                resolution_condition=args.resolution_condition,
                live_main_sha=args.live_main,
            )
        else:
            transition(args.to, implementation_sha=args.implementation_sha, complete_correction=args.complete_correction)
    except TaskControlError as exc:
        print(exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
