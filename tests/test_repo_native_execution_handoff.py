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
    if state["implementation_commit_sha"] is not None:
        assert state["implementation_commit_sha"] in report
    for path in (
        "panel_exp/contracts/geox_governed_experiment_readout.py",
        "tests/fixtures/geox_governed_readouts",
        "tests/fixtures/geox_numerical_truth",
        "docs/ROADMAP_V4.md",
        "docs/OPEN_INVESTIGATIONS.md",
        "docs/track_d",
        "docs/FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001.md",
    ):
        assert (ROOT / path).exists()
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


def test_lean_repository_delivery_standard_is_adopted():
    text = (ROOT / "docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md").read_text()
    for term in ("one independently mergeable outcome", "execution-blocking design questions", "one correction cycle", "deferred successors"):
        assert term in text


def test_codex_invocation_and_terminal_outcome_rules_are_adopted():
    text = (ROOT / "docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md").read_text()
    for term in ("invocation-only", "durable", "ready_for_review", "blocked", "changes_requested"):
        assert term in text


def test_risk_tier_and_durable_receipt_rules_are_adopted():
    text = (ROOT / "docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md").read_text()
    for term in ("Tier 1", "Tier 2", "Tier 3", "freeze the task tree", "counts", "authority"):
        assert term in text


def test_repository_context_index_is_navigation_only():
    text = (ROOT / "docs/execution/REPOSITORY_CONTEXT_INDEX.md").read_text()
    assert "stable navigation, not a mirror" in text
    assert "EXECUTION_STATE.json" in text and "ACTIVE_TASK.md" in text
