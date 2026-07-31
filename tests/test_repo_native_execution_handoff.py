import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
SHA = re.compile(r"^[0-9a-f]{40}$")
STATUSES = {"idle", "proposed", "authorized", "in_progress", "blocked", "ready_for_review", "changes_requested", "merged", "superseded"}


def test_v2_state_contract_and_pins():
    state = json.loads((ROOT / "docs/execution/EXECUTION_STATE.json").read_text())
    task = (ROOT / "docs/execution/ACTIVE_TASK.md").read_text()
    report = (ROOT / "docs/execution/LATEST_COMPLETION_REPORT.md").read_text()
    context = (ROOT / "docs/execution/REPOSITORY_CONTEXT_INDEX.md").read_text()
    assert state["schema_version"] == "geox_repo_execution_state_v2"
    assert state["status"] in STATUSES and "approved_for_merge" not in STATUSES
    for key in ("base_sha", "authorization_head_sha", "reviewed_head_sha", "implementation_commit_sha", "approval_commit_sha"):
        assert state.get(key) is None or SHA.fullmatch(state[key])
    status_match = re.search(r"^\*\*Status:\*\*\s*([a-z_]+)", task, re.MULTILINE)
    assert status_match and status_match.group(1) == state["status"]
    for pin in (state["canonical_mip_standard_commit"], state["canonical_mmm_workflow_commit"]):
        assert all(pin in text for text in (task, report, context))
    assert all(state["task_id"] in text for text in (task, report, context))
    assert state["merge_authorized"] is False
    assert state["capability_authorizations_changed"] is False


def test_bootstrap_and_merge_protocol_are_fail_closed():
    agents = (ROOT / "AGENTS.md").read_text()
    assert agents.index("Classify") < agents.index("fetch") < agents.index("switch main") < agents.index("pull --ff-only") < agents.index("main == origin/main")
    assert ".codex/" in agents and "docs/tasks/" in agents
    assert "git merge --ff-only" in agents and "one closure commit" in agents
    assert "approved_for_merge" in agents


def test_status_invariants_are_closure_safe():
    state = json.loads((ROOT / "docs/execution/EXECUTION_STATE.json").read_text())
    status = state["status"]
    if status == "authorized":
        assert state["task_execution_authorized"] and not state["merge_authorized"]
        assert state["implementation_commit_sha"] is None and state["reviewed_head_sha"] is None and state["approval_commit_sha"] is None and not state["blockers"]
    elif status == "blocked":
        assert state["task_execution_authorized"] and not state["merge_authorized"] and state["reviewed_head_sha"] is None and state["approval_commit_sha"] is None and state["blockers"]
    elif status == "ready_for_review":
        assert state["task_execution_authorized"] and not state["merge_authorized"]
        assert SHA.fullmatch(state["implementation_commit_sha"]) and state["reviewed_head_sha"] is None and state["approval_commit_sha"] is None and not state["blockers"]
    elif status == "merged":
        assert not state["task_execution_authorized"] and not state["merge_authorized"]
        assert SHA.fullmatch(state["implementation_commit_sha"])
        assert SHA.fullmatch(state["reviewed_head_sha"]) and state["approval_commit_sha"] is None and not state["blockers"]
