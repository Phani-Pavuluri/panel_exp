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


def valid_completion_evidence() -> dict[str, object]:
    return {
        "changed_paths": ["panel_exp/execution/taskctl.py"],
        "behavior_summary": "Canonical structured evidence is validated and rendered from lifecycle state.",
        "validation_results": [
            {"command": ".venv/bin/python -m pytest -q tests/execution/test_taskctl.py", "result": "passed", "outcome": "passed"}
        ],
        "validation_not_run": [],
        "blockers_and_limitations": [],
        "prohibited_operations": {
            "pr_creation": False,
            "merge": False,
            "squash": False,
            "rebase": False,
            "force_push": False,
        },
    }


def prepare_changes_requested() -> None:
    canonical = state()
    canonical.update(
        status="changes_requested",
        review_decision="changes_requested",
        correction_execution_authorized=True,
        correction_cycles_completed=0,
        correction_cycles_remaining=1,
        implementation_commit_sha="a" * 40,
        rejected_review_head_sha="b" * 40,
        rejected_implementation_commit_sha="c" * 40,
        completion_evidence=valid_completion_evidence(),
    )
    taskctl.STATE_PATH.write_text(json.dumps(canonical, indent=2) + "\n", encoding="utf-8")
    taskctl.sync()


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
        taskctl.transition("proposed")


def test_check_rejects_generated_view_divergence_before_transition() -> None:
    active = taskctl.ACTIVE_PATH.read_text(encoding="utf-8")
    taskctl.ACTIVE_PATH.write_text(active.replace("do not edit", "do not alter", 1), encoding="utf-8")
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
    taskctl.sync()
    first = taskctl.ACTIVE_PATH.read_bytes(), taskctl.REPORT_PATH.read_bytes()
    taskctl.sync()
    assert first == (taskctl.ACTIVE_PATH.read_bytes(), taskctl.REPORT_PATH.read_bytes())
    taskctl.check()


def test_sync_replaces_only_generated_block() -> None:
    original = taskctl.ACTIVE_PATH.read_text(encoding="utf-8")
    prefix, suffix = original.split(taskctl.BEGIN_MARKER, 1)[0], original.split(taskctl.END_MARKER, 1)[1]
    taskctl.ACTIVE_PATH.write_text(original.replace("do not edit", "do not alter", 1), encoding="utf-8")
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
    prepare_changes_requested()
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


def test_ready_for_review_requires_structured_completion_evidence() -> None:
    canonical = state()
    canonical.update(
        status="ready_for_review",
        review_decision="ready_for_review",
        implementation_commit_sha="a" * 40,
        correction_execution_authorized=False,
        completion_evidence=None,
    )
    with pytest.raises(taskctl.TaskControlError, match="E_COMPLETION_EVIDENCE_TYPE"):
        taskctl.validate_state(canonical)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("changed_paths", ["../outside"], "E_COMPLETION_EVIDENCE_PATHS"),
        ("changed_paths", ["panel_exp/execution/taskctl.py", "panel_exp/execution/taskctl.py"], "E_COMPLETION_EVIDENCE_PATHS"),
        ("behavior_summary", "", "E_COMPLETION_EVIDENCE_BEHAVIOR"),
        ("validation_results", [{"command": "x", "result": "failed", "outcome": "failed"}], "E_COMPLETION_EVIDENCE_VALIDATION"),
        ("validation_not_run", [{"command": "x"}], "E_COMPLETION_EVIDENCE_OMITTED"),
        ("prohibited_operations", {"pr_creation": True, "merge": False, "squash": False, "rebase": False, "force_push": False}, "E_COMPLETION_EVIDENCE_PROHIBITED"),
    ),
)
def test_completion_evidence_schema_fails_closed(field: str, value: object, reason: str) -> None:
    canonical = state()
    canonical["completion_evidence"] = valid_completion_evidence()
    canonical["completion_evidence"][field] = value
    canonical.update(status="ready_for_review", review_decision="ready_for_review", implementation_commit_sha="a" * 40)
    with pytest.raises(taskctl.TaskControlError, match=reason):
        taskctl.validate_state(canonical)


def test_completion_report_is_fully_generated() -> None:
    canonical = state()
    canonical["completion_evidence"] = valid_completion_evidence()
    rendered = taskctl.render(canonical, "completion_report")
    assert "## Structured completion evidence" in rendered
    assert "### Changed paths" in rendered
    assert "MIP main pin" in rendered and "MMM main pin" in rendered
    assert rendered.endswith(taskctl.END_MARKER + "\n")
    assert "Implementation has not started" not in rendered


def test_transition_renders_structured_completion_evidence() -> None:
    canonical = state()
    canonical["completion_evidence"] = valid_completion_evidence()
    taskctl.STATE_PATH.write_text(json.dumps(canonical, indent=2) + "\n", encoding="utf-8")
    taskctl.sync()
    taskctl.transition("ready_for_review", implementation_sha="d" * 40)
    report = taskctl.REPORT_PATH.read_text(encoding="utf-8")
    assert "## Structured completion evidence" in report
    assert "panel_exp/execution/taskctl.py" in report
    assert "Implementation has not started" not in report
