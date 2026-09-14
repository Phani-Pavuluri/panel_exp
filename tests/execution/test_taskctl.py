"""Focused contract tests for GeoX task-control lifecycle state."""

from __future__ import annotations

import json

import pytest

from panel_exp.execution import taskctl


@pytest.fixture(autouse=True)
def restore_execution_files() -> None:
    paths = (taskctl.STATE_PATH, taskctl.ACTIVE_PATH, taskctl.REPORT_PATH)
    before = {path: path.read_bytes() for path in paths}
    yield
    for path, content in before.items():
        path.write_bytes(content)


def state() -> dict[str, object]:
    return json.loads(taskctl.STATE_PATH.read_text(encoding="utf-8"))


def test_schema_migration_and_correction_invariant() -> None:
    canonical = state()
    taskctl.validate_state(canonical)
    assert canonical["schema_version"] == taskctl.SCHEMA_VERSION
    assert "correction_cycles_used" not in canonical
    assert canonical["correction_cycles_completed"] + canonical["correction_cycles_remaining"] == canonical["maximum_correction_cycles"]


def test_transition_table_excludes_forbidden_approval_state() -> None:
    assert taskctl.TRANSITIONS["changes_requested"] == frozenset({"in_progress", "blocked", "ready_for_review", "superseded"})
    assert "approved_for_merge" not in taskctl.STATES
    with pytest.raises(taskctl.TaskControlError, match="E_TRANSITION"):
        taskctl.transition("merged")


def test_check_rejects_generated_view_divergence_before_transition() -> None:
    active = taskctl.ACTIVE_PATH.read_text(encoding="utf-8")
    taskctl.ACTIVE_PATH.write_text(active.replace("`changes_requested`", "`in_progress`", 1), encoding="utf-8")
    with pytest.raises(taskctl.TaskControlError, match="E_VIEW_DIVERGENCE"):
        taskctl.transition("ready_for_review", implementation_sha="a" * 40, complete_correction=True)


@pytest.mark.parametrize(
    "document",
    (
        "no markers",
        taskctl.BEGIN_MARKER + taskctl.END_MARKER + taskctl.BEGIN_MARKER,
        taskctl.END_MARKER + taskctl.BEGIN_MARKER,
        taskctl.BEGIN_MARKER + taskctl.BEGIN_MARKER + taskctl.END_MARKER + taskctl.END_MARKER,
    ),
)
def test_missing_duplicate_reversed_and_nested_markers_fail_closed(document: str) -> None:
    with pytest.raises(taskctl.TaskControlError, match="E_VIEW_MARKERS"):
        taskctl.replace_view(document, taskctl.render(state(), "active_task"))


def test_generated_view_sync_is_byte_preserving_and_idempotent() -> None:
    before = taskctl.ACTIVE_PATH.read_bytes(), taskctl.REPORT_PATH.read_bytes()
    taskctl.sync()
    assert before == (taskctl.ACTIVE_PATH.read_bytes(), taskctl.REPORT_PATH.read_bytes())
    taskctl.check()


def test_sync_replaces_only_generated_block() -> None:
    original = taskctl.ACTIVE_PATH.read_text(encoding="utf-8")
    prefix, suffix = original.split(taskctl.BEGIN_MARKER, 1)[0], original.split(taskctl.END_MARKER, 1)[1]
    taskctl.ACTIVE_PATH.write_text(original.replace("`changes_requested`", "`blocked`", 1), encoding="utf-8")
    taskctl.sync()
    synchronized = taskctl.ACTIVE_PATH.read_text(encoding="utf-8")
    assert synchronized.startswith(prefix + taskctl.BEGIN_MARKER)
    assert synchronized.endswith(suffix)
    taskctl.check()


def test_reason_codes_for_invalid_counters_and_blocked_evidence() -> None:
    canonical = state()
    canonical["correction_cycles_remaining"] = 2
    with pytest.raises(taskctl.TaskControlError, match="E_CORRECTION_COUNTERS"):
        taskctl.validate_state(canonical)
    canonical = state()
    canonical.update(status="blocked", review_decision="blocked", blockers=[])
    with pytest.raises(taskctl.TaskControlError, match="E_BLOCKED_EVIDENCE"):
        taskctl.validate_state(canonical)


def test_protected_authorities_cannot_be_introduced() -> None:
    canonical = state()
    for authority in taskctl.PROTECTED_AUTHORITY:
        assert canonical[authority] is False
    canonical["runtime_integration_authorized"] = True
    with pytest.raises(taskctl.TaskControlError, match="E_PROTECTED_AUTHORITY"):
        taskctl.validate_state(canonical)


def test_correction_closure_requires_explicit_evidence_and_updates_counters() -> None:
    with pytest.raises(taskctl.TaskControlError, match="E_TRANSITION_CORRECTION"):
        taskctl.transition("ready_for_review", implementation_sha="b" * 40)
    taskctl.transition("ready_for_review", implementation_sha="b" * 40, complete_correction=True)
    canonical = state()
    assert canonical["status"] == "ready_for_review"
    assert canonical["review_decision"] == "ready_for_review"
    assert canonical["implementation_commit_sha"] == "b" * 40
    assert canonical["correction_cycles_completed"] == 1
    assert canonical["correction_cycles_remaining"] == 0
    assert canonical["correction_execution_authorized"] is False
    taskctl.check()


def test_ready_for_review_requires_implementation_and_closed_correction_authority() -> None:
    canonical = state()
    canonical.update(
        status="ready_for_review",
        review_decision="ready_for_review",
        implementation_commit_sha=None,
        correction_execution_authorized=False,
    )
    with pytest.raises(taskctl.TaskControlError, match="E_REVIEW_EVIDENCE"):
        taskctl.validate_state(canonical)
