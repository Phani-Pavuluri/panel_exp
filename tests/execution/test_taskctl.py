from __future__ import annotations

import json
import pytest

from panel_exp.execution import taskctl


@pytest.fixture(autouse=True)
def restore_execution_files():
    paths = (taskctl.STATE_PATH, taskctl.ACTIVE_PATH, taskctl.REPORT_PATH)
    before = {path: path.read_bytes() for path in paths}
    yield
    for path, content in before.items():
        path.write_bytes(content)


def _state() -> dict:
    return json.loads(taskctl.STATE_PATH.read_text())


def test_schema_and_correction_invariant() -> None:
    statectl = _state()
    assert statectl["schema_version"] == "geox_repo_execution_state_v3"
    assert "correction_cycles_used" not in statectl
    assert statectl["correction_cycles_completed"] + statectl["correction_cycles_remaining"] == statectl["maximum_correction_cycles"]


def test_transition_graph_is_table_driven() -> None:
    assert taskctl.TRANSITIONS["authorized"] == {"in_progress", "blocked", "ready_for_review", "superseded"}
    assert "approved_for_merge" not in taskctl.STATES
    with pytest.raises(taskctl.TaskControlError, match="E_TRANSITION"):
        taskctl.transition("merged")


def test_transition_requires_explicit_evidence_and_validates_views_first() -> None:
    active = taskctl.ACTIVE_PATH.read_text()
    taskctl.ACTIVE_PATH.write_text(active.replace("**Status:** ready_for_review", "**Status:** authorized", 1))
    try:
        with pytest.raises(taskctl.TaskControlError, match="E_VIEW_DIVERGENCE"):
            taskctl.check()
    finally:
        taskctl.ACTIVE_PATH.write_text(active)


def test_generated_views_are_current_and_idempotent() -> None:
    state = _state()
    for path, document in ((taskctl.ACTIVE_PATH, "active_task"), (taskctl.REPORT_PATH, "completion_report")):
        text = path.read_text()
        assert text.count(taskctl.BEGIN_MARKER) == 1
        assert text.count(taskctl.END_MARKER) == 1
        assert taskctl.replace_view(text, taskctl.render(state, document)) == text
    before = taskctl.ACTIVE_PATH.read_bytes(), taskctl.REPORT_PATH.read_bytes()
    taskctl.sync()
    assert before == (taskctl.ACTIVE_PATH.read_bytes(), taskctl.REPORT_PATH.read_bytes())


def test_markers_fail_closed() -> None:
    state = _state()
    with pytest.raises(taskctl.TaskControlError, match="E_VIEW_MARKERS"):
        taskctl.replace_view("no markers", taskctl.render(state, "active_task"))
    nested = taskctl.BEGIN_MARKER + taskctl.BEGIN_MARKER + taskctl.END_MARKER + taskctl.END_MARKER
    with pytest.raises(taskctl.TaskControlError, match="E_VIEW_MARKERS"):
        taskctl.replace_view(nested, taskctl.render(state, "active_task"))


def test_authority_is_protected() -> None:
    state = _state()
    for key in taskctl.PROTECTED_AUTHORITY:
        if key in state:
            assert state[key] is False


def test_changes_requested_requires_paired_rejection_provenance() -> None:
    state = _state()
    state.update(
        status="in_progress", review_decision="in_progress", blockers=[],
        implementation_commit_sha="a" * 40,
    )
    with pytest.raises(taskctl.TaskControlError, match="E_TRANSITION"):
        taskctl.transition("changes_requested")


def test_merged_requires_review_head_and_cleanup_evidence() -> None:
    state = _state()
    state.update(
        status="ready_for_review", review_decision="ready_for_review", blockers=[],
        implementation_commit_sha="a" * 40,
    )
    with pytest.raises(taskctl.TaskControlError, match="E_TRANSITION"):
        taskctl.transition("merged")


def test_invalid_state_reason_codes() -> None:
    state = _state()
    state["correction_cycles_remaining"] += 1
    with pytest.raises(taskctl.TaskControlError, match="E_CORRECTION_COUNTERS"):
        taskctl.validate_state(state)


def test_blocked_requires_explicit_blocker() -> None:
    state = _state()
    state["status"] = "blocked"
    state["review_decision"] = "blocked"
    state["blockers"] = []
    with pytest.raises(taskctl.TaskControlError, match="E_BLOCKED_EVIDENCE"):
        taskctl.validate_state(state)


def test_ready_for_review_requires_implementation_and_no_blockers() -> None:
    state = _state()
    state["status"] = "ready_for_review"
    state["review_decision"] = "ready_for_review"
    state["implementation_commit_sha"] = None
    with pytest.raises(taskctl.TaskControlError, match="E_REVIEW_EVIDENCE"):
        taskctl.validate_state(state)
