"""Focused contract tests for GeoX task-control lifecycle state."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from panel_exp.execution import taskctl


GIT = shutil.which("git")
needs_git = pytest.mark.skipif(GIT is None, reason="git is required for rejection-record fixtures")

TARGET_BRANCH = "feat/fixture-target-001"
LIVE_BRANCH = "feat/fixture-record-001"
DEPENDENCY_ID = "DEP-FIXTURE-001"


@pytest.fixture(autouse=True)
def restore_execution_files() -> None:
    paths = (taskctl.STATE_PATH, taskctl.ACTIVE_PATH, taskctl.REPORT_PATH)
    before = {path: path.read_bytes() for path in paths}
    yield
    for path, content in before.items():
        path.write_bytes(content)


def state() -> dict[str, object]:
    return json.loads(taskctl.STATE_PATH.read_text(encoding="utf-8"))


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
    before = taskctl.ACTIVE_PATH.read_bytes(), taskctl.REPORT_PATH.read_bytes()
    taskctl.sync()
    assert before == (taskctl.ACTIVE_PATH.read_bytes(), taskctl.REPORT_PATH.read_bytes())
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


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run([GIT, "-C", str(repo), *args], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"
    return proc.stdout.strip()


def _commit(repo: Path, rel: str, content: bytes | str, message: str) -> str:
    target = repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        target.write_bytes(content)
    else:
        target.write_text(content, encoding="utf-8")
    _git(repo, "add", rel)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _target_variant(fixture: dict[str, Any], content: bytes | str, message: str) -> str:
    work = fixture["work"]
    _git(work, "checkout", "-q", TARGET_BRANCH)
    try:
        return _commit(work, taskctl.TARGET_STATE_PATH, content, message)
    finally:
        _git(work, "checkout", "-q", LIVE_BRANCH)


def _target_blob(
    *,
    task_id: str = "GEOX_FIXTURE_TARGET_001",
    branch: str = TARGET_BRANCH,
    status: str = "ready_for_review",
    schema: str = "geox_repo_execution_state_v3",
    implementation: str,
    authorization: str,
    baseline: str,
    prior: tuple[str | None, str | None],
    maximum: int = 1,
    completed: int = 1,
    remaining: int = 0,
    correction_open: bool = False,
    task_authorized: bool = True,
    blockers: list[str] | None = None,
    protected_true: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blob: dict[str, Any] = {
        "schema_version": schema,
        "repository": "Phani-Pavuluri/panel_exp",
        "task_id": task_id,
        "execution_mode": "branch_and_fast_forward",
        "base_branch": "main",
        "status": status,
        "feature_branch": branch,
        "authorization_head_sha": authorization,
        "authorized_branch_baseline_sha": baseline,
        "implementation_commit_sha": implementation,
        "rejected_review_head_sha": prior[0],
        "rejected_implementation_commit_sha": prior[1],
        "task_execution_authorized": task_authorized,
        "correction_execution_authorized": correction_open,
        "maximum_correction_cycles": maximum,
        "correction_cycles_completed": completed,
        "correction_cycles_remaining": remaining,
        "blockers": blockers if blockers is not None else [],
        "merge_authorized": False,
        "pr_creation_authorized": False,
    }
    for authority in taskctl.PROTECTED_AUTHORITY:
        blob[authority] = authority == protected_true
    if extra:
        blob.update(extra)
    return blob


def _live_state(base_sha: str, branch: str, head: str, implementation: str, **overrides: Any) -> dict[str, Any]:
    canonical: dict[str, Any] = {
        "schema_version": "geox_repo_execution_state_v3",
        "repository": "Phani-Pavuluri/panel_exp",
        "task_id": "GEOX_FIXTURE_RECORD_001",
        "execution_mode": "branch_and_fast_forward",
        "base_branch": "main",
        "status": "authorized",
        "base_sha": base_sha,
        "task_authoring_head_sha": base_sha,
        "authorization_head_sha": base_sha,
        "authorized_branch_baseline_sha": base_sha,
        "feature_branch": branch,
        "feature_branch_created": True,
        "task_execution_authorized": True,
        "correction_execution_authorized": False,
        "merge_authorized": False,
        "pr_creation_authorized": False,
        "implementation_commit_sha": None,
        "reviewed_head_sha": None,
        "rejected_review_head_sha": None,
        "rejected_implementation_commit_sha": None,
        "approval_commit_sha": None,
        "local_feature_branch_cleanup": None,
        "remote_feature_branch_cleanup": None,
        "capability_authorizations_changed": False,
        "blockers": [],
        "maximum_correction_cycles": 1,
        "correction_cycles_completed": 0,
        "correction_cycles_remaining": 1,
        "review_decision": "authorized",
        "dependencies": [
            {
                "dependency_id": DEPENDENCY_ID,
                "repository": "Phani-Pavuluri/panel_exp",
                "task_id": "GEOX_FIXTURE_TARGET_001",
                "branch": TARGET_BRANCH,
                "remote_head_sha": head,
                "implementation_commit_sha": implementation,
            }
        ],
    }
    for authority in taskctl.PROTECTED_AUTHORITY:
        canonical[authority] = False
    canonical.update(overrides)
    if canonical.get("status") in {"blocked", "changes_requested", "ready_for_review"}:
        canonical["review_decision"] = canonical["status"]
    return canonical


_FIXTURE_DOC = (
    taskctl.BEGIN_MARKER + "\n# Fixture\n" + taskctl.END_MARKER + "\nhuman suffix\n"
)


@pytest.fixture
def record_fixture(tmp_path: Path) -> dict[str, Any]:
    remote = tmp_path / "remotes" / "Phani-Pavuluri" / "panel_exp.git"
    remote.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [GIT, "init", "--bare", "-q", str(remote)], capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0, f"git init --bare failed: {proc.stderr}"
    work = tmp_path / "work"
    work.mkdir()
    _git(work, "init", "-q")
    _git(work, "config", "user.email", "fixture@example.com")
    _git(work, "config", "user.name", "Fixture")
    _git(work, "remote", "add", "origin", str(remote))
    _git(work, "checkout", "-q", "-b", "main")
    main0 = _commit(work, "README.md", "seed\n", "seed main")
    _git(work, "checkout", "-q", "-b", TARGET_BRANCH, main0)
    implementation = _commit(work, "target_impl.txt", "implementation\n", "target implementation")
    prior_review = _commit(work, "target_more.txt", "more work\n", "target follow-up")
    blob = _target_blob(
        implementation=implementation,
        authorization=main0,
        baseline=main0,
        prior=(prior_review, implementation),
    )
    head = _commit(
        work,
        taskctl.TARGET_STATE_PATH,
        json.dumps(blob, indent=2) + "\n",
        "target review-ready head",
    )
    _git(work, "push", "-q", "origin", "main", TARGET_BRANCH)
    _git(work, "checkout", "-q", "-b", LIVE_BRANCH, main0)
    live = _live_state(main0, LIVE_BRANCH, head, implementation)
    state_path = work / "docs" / "execution" / "EXECUTION_STATE.json"
    active_path = work / "docs" / "execution" / "ACTIVE_TASK.md"
    report_path = work / "docs" / "execution" / "LATEST_COMPLETION_REPORT.md"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
    active_path.write_text(taskctl.render(live, "active_task") + "human suffix\n", encoding="utf-8")
    report_path.write_text(taskctl.render(live, "completion_report") + "human suffix\n", encoding="utf-8")
    taskctl.validate_state(live)
    _git(work, "add", "-A")
    _git(work, "commit", "-q", "-m", "fixture live state")
    return {
        "work": work,
        "state_path": state_path,
        "active_path": active_path,
        "report_path": report_path,
        "main0": main0,
        "head": head,
        "implementation": implementation,
        "prior_review": prior_review,
        "live": live,
    }


def _retarget_pin(fixture: dict[str, Any], head: str, implementation: str | None = None) -> None:
    live = json.loads(fixture["state_path"].read_text(encoding="utf-8"))
    for dependency in live["dependencies"]:
        if dependency["dependency_id"] == DEPENDENCY_ID:
            dependency["remote_head_sha"] = head
            if implementation is not None:
                dependency["implementation_commit_sha"] = implementation
    fixture["state_path"].write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
    taskctl.sync(
        state_path=fixture["state_path"],
        active_path=fixture["active_path"],
        report_path=fixture["report_path"],
    )
    work = fixture["work"]
    assert _git(work, "branch", "--show-current") == LIVE_BRANCH
    _git(work, "add", "docs/execution/EXECUTION_STATE.json")
    _git(work, "commit", "-q", "-m", "retarget pin")


def _record(fixture: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    head = overrides.pop("rejected_head_sha", fixture["head"])
    implementation = overrides.pop("rejected_implementation_sha", fixture["implementation"])
    params: dict[str, Any] = {
        "dependency_id": DEPENDENCY_ID,
        "rejected_head_sha": head,
        "rejected_implementation_sha": implementation,
        "blockers": ["Independent rejection of exhausted review-ready head"],
        "finding": (
            f"Independent finding names {head} and {implementation}: "
            "malformed completion evidence accepted before rendering on the exhausted head."
        ),
        "resolution_condition": "Fresh completion-evidence recovery after merged record; old branch immutable.",
        "state_path": fixture["state_path"],
        "active_path": fixture["active_path"],
        "report_path": fixture["report_path"],
        "repo": fixture["work"],
    }
    params.update(overrides)
    return taskctl.record_rejection(**params)


@needs_git
def test_v3_read_check_render_unchanged_without_history(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    before = (
        fixture["state_path"].read_bytes(),
        fixture["active_path"].read_bytes(),
        fixture["report_path"].read_bytes(),
    )
    taskctl.check(
        state_path=fixture["state_path"],
        active_path=fixture["active_path"],
        report_path=fixture["report_path"],
    )
    taskctl.sync(
        state_path=fixture["state_path"],
        active_path=fixture["active_path"],
        report_path=fixture["report_path"],
    )
    after = (
        fixture["state_path"].read_bytes(),
        fixture["active_path"].read_bytes(),
        fixture["report_path"].read_bytes(),
    )
    assert before == after
    assert json.loads(before[0])["schema_version"] == "geox_repo_execution_state_v3"
    assert taskctl.REJECTION_HISTORY_KEY not in json.loads(before[0])


@needs_git
def test_record_rejection_success_appends_prior_lineage_and_preserves_live(
    record_fixture: dict[str, Any],
) -> None:
    fixture = record_fixture
    active_before = fixture["active_path"].read_bytes()
    entry = _record(fixture)
    assert entry["target_task_id"] == "GEOX_FIXTURE_TARGET_001"
    assert entry["target_branch"] == TARGET_BRANCH
    assert entry["target_head_sha"] == fixture["head"]
    assert entry["target_implementation_sha"] == fixture["implementation"]
    assert entry["target_authorization_head_sha"] == fixture["main0"]
    assert entry["target_disposition"] == "blocked"
    assert entry["target_counters"] == {"maximum": 1, "completed": 1, "remaining": 0}
    assert entry["prior_rejected_review_head_sha"] == fixture["prior_review"]
    assert entry["prior_rejected_implementation_commit_sha"] == fixture["implementation"]
    assert entry["live_main_sha"] == _git(fixture["work"], "rev-parse", "origin/main")
    canonical = json.loads(fixture["state_path"].read_text(encoding="utf-8"))
    assert canonical["schema_version"] == "geox_repo_execution_state_v5"
    assert len(canonical["rejection_history"]) == 1
    for key, value in fixture["live"].items():
        if key in {"schema_version", "rejection_history"}:
            continue
        assert canonical[key] == value
    assert canonical["status"] == "authorized"
    assert canonical["rejected_review_head_sha"] is None
    assert canonical["approval_commit_sha"] is None
    assert fixture["active_path"].read_bytes() == active_before
    report = fixture["report_path"].read_text(encoding="utf-8")
    assert "Rejection history" in report
    assert fixture["head"] in report
    assert report.endswith("human suffix\n")
    taskctl.check(
        state_path=fixture["state_path"],
        active_path=fixture["active_path"],
        report_path=fixture["report_path"],
    )


@needs_git
@pytest.mark.parametrize(
    "field,value",
    (
        ("repository", "Other/other"),
        ("task_id", "GEOX_WRONG_TASK"),
        ("feature_branch", "feat/wrong-branch"),
    ),
)
def test_record_rejection_target_identity_mismatch(
    record_fixture: dict[str, Any], field: str, value: str
) -> None:
    fixture = record_fixture
    blob = _target_blob(
        implementation=fixture["implementation"],
        authorization=fixture["main0"],
        baseline=fixture["main0"],
        prior=(fixture["prior_review"], fixture["implementation"]),
    )
    blob[field] = value
    divergent = _target_variant(
        fixture, json.dumps(blob, indent=2) + "\n", "variant blob"
    )
    _retarget_pin(fixture, divergent)
    with pytest.raises(taskctl.TaskControlError, match="E_REJECTION_IDENTITY"):
        _record(fixture, rejected_head_sha=divergent)


@needs_git
def test_record_rejection_pin_disagreement(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    with pytest.raises(taskctl.TaskControlError, match="E_REJECTION_IDENTITY"):
        _record(fixture, dependency_id="DEP-UNKNOWN")
    other = _commit(fixture["work"], "other.txt", "other\n", "unrelated commit")
    with pytest.raises(taskctl.TaskControlError, match="E_REJECTION_IDENTITY"):
        _record(fixture, rejected_head_sha=other)


@needs_git
def test_record_rejection_remote_head_disagreement(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    work = fixture["work"]
    _git(work, "checkout", "-q", TARGET_BRANCH)
    blob = _target_blob(
        implementation=fixture["implementation"],
        authorization=fixture["main0"],
        baseline=fixture["main0"],
        prior=(fixture["prior_review"], fixture["implementation"]),
        extra={"advanced_tip": True},
    )
    advanced = _commit(work, taskctl.TARGET_STATE_PATH, json.dumps(blob, indent=2) + "\n", "advanced tip")
    assert advanced != fixture["head"]
    _git(work, "push", "-q", "origin", TARGET_BRANCH)
    _git(work, "checkout", "-q", LIVE_BRANCH)
    with pytest.raises(taskctl.TaskControlError, match="E_REJECTION_HEAD"):
        _record(fixture)


@needs_git
def test_record_rejection_non_commit_head(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    tree = _git(fixture["work"], "rev-parse", f"{fixture['head']}^{{tree}}")
    assert tree != fixture["head"]
    _retarget_pin(fixture, tree)
    with pytest.raises(taskctl.TaskControlError, match="E_REJECTION_HEAD"):
        _record(fixture, rejected_head_sha=tree)


@needs_git
def test_record_rejection_implementation_mismatch_or_unrelated(
    record_fixture: dict[str, Any],
) -> None:
    fixture = record_fixture
    _retarget_pin(fixture, fixture["head"], "d" * 40)
    with pytest.raises(taskctl.TaskControlError, match="E_REJECTION_IMPLEMENTATION"):
        _record(fixture, rejected_implementation_sha="d" * 40)


@needs_git
def test_record_rejection_implementation_not_ancestor(
    record_fixture: dict[str, Any],
) -> None:
    fixture = record_fixture
    live_tip = _git(fixture["work"], "rev-parse", LIVE_BRANCH)
    blob = _target_blob(
        implementation=live_tip,
        authorization=fixture["main0"],
        baseline=fixture["main0"],
        prior=(fixture["prior_review"], live_tip),
    )
    divergent = _target_variant(fixture, json.dumps(blob, indent=2) + "\n", "non-ancestor impl blob")
    _retarget_pin(fixture, divergent, live_tip)
    with pytest.raises(taskctl.TaskControlError, match="E_REJECTION_IMPLEMENTATION"):
        _record(fixture, rejected_head_sha=divergent, rejected_implementation_sha=live_tip)


@needs_git
def test_record_rejection_target_authorization_ancestry(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    live_tip = _git(fixture["work"], "rev-parse", LIVE_BRANCH)
    blob = _target_blob(
        implementation=fixture["implementation"],
        authorization=live_tip,
        baseline=fixture["main0"],
        prior=(fixture["prior_review"], fixture["implementation"]),
    )
    divergent = _target_variant(
        fixture, json.dumps(blob, indent=2) + "\n", "variant auth blob"
    )
    _retarget_pin(fixture, divergent)
    with pytest.raises(taskctl.TaskControlError, match="E_REJECTION_IDENTITY"):
        _record(fixture, rejected_head_sha=divergent)


@needs_git
@pytest.mark.parametrize(
    "mutate,code",
    (
        ("status", "E_TRANSITION"),
        ("budget", "E_REJECTION_BUDGET"),
        ("correction", "E_REJECTION_BUDGET"),
        ("blockers", "E_TRANSITION"),
        ("task_authority", "E_TRANSITION"),
        ("protected", "E_PROTECTED_AUTHORITY"),
    ),
)
def test_record_rejection_target_lifecycle(record_fixture: dict[str, Any], mutate: str, code: str) -> None:
    fixture = record_fixture
    kwargs: dict[str, Any] = {
        "implementation": fixture["implementation"],
        "authorization": fixture["main0"],
        "baseline": fixture["main0"],
        "prior": (fixture["prior_review"], fixture["implementation"]),
    }
    if mutate == "status":
        kwargs["status"] = "in_progress"
    elif mutate == "budget":
        kwargs["completed"] = 0
        kwargs["remaining"] = 1
    elif mutate == "correction":
        kwargs["correction_open"] = True
    elif mutate == "blockers":
        kwargs["blockers"] = ["still blocked"]
    elif mutate == "task_authority":
        kwargs["task_authorized"] = False
    elif mutate == "protected":
        kwargs["protected_true"] = "simulation_authorized"
    blob = _target_blob(**kwargs)
    divergent = _target_variant(fixture, json.dumps(blob, indent=2) + "\n", "variant lifecycle blob")
    _retarget_pin(fixture, divergent)
    with pytest.raises(taskctl.TaskControlError, match=code):
        _record(fixture, rejected_head_sha=divergent)


@needs_git
def test_record_rejection_live_branch_mismatch(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    _git(fixture["work"], "checkout", "-q", "-b", "feat/fixture-other")
    with pytest.raises(taskctl.TaskControlError, match="E_REJECTION_IDENTITY"):
        _record(fixture)


@needs_git
@pytest.mark.parametrize("status", ("blocked", "changes_requested", "ready_for_review"))
def test_record_rejection_live_status_not_recordable(
    record_fixture: dict[str, Any], status: str
) -> None:
    fixture = record_fixture
    live = dict(fixture["live"])
    live.update(status=status, review_decision=status)
    if status == "blocked":
        live["blockers"] = ["live blocker"]
    if status == "changes_requested":
        live.update(
            correction_execution_authorized=True,
            implementation_commit_sha="b" * 40,
            rejected_review_head_sha="c" * 40,
            rejected_implementation_commit_sha="d" * 40,
        )
    if status == "ready_for_review":
        live["implementation_commit_sha"] = "b" * 40
    taskctl.validate_state(live)
    fixture["state_path"].write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
    taskctl.sync(
        state_path=fixture["state_path"],
        active_path=fixture["active_path"],
        report_path=fixture["report_path"],
    )
    with pytest.raises(taskctl.TaskControlError, match="E_TRANSITION"):
        _record(fixture)


@needs_git
def test_record_rejection_dirty_worktree(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    readme = fixture["work"] / "README.md"
    with readme.open("a", encoding="utf-8") as handle:
        handle.write("uncommitted\n")
    with pytest.raises(taskctl.TaskControlError, match="E_TRANSITION"):
        _record(fixture)


@needs_git
def test_record_rejection_stale_main(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    with pytest.raises(taskctl.TaskControlError, match="E_STALE_MAIN"):
        _record(fixture, live_main_sha="0" * 40)
    work = fixture["work"]
    _git(work, "checkout", "-q", "main")
    _commit(work, "drift.txt", "drift\n", "unpushed main drift")
    _git(work, "checkout", "-q", LIVE_BRANCH)
    with pytest.raises(taskctl.TaskControlError, match="E_STALE_MAIN"):
        _record(fixture)


@needs_git
@pytest.mark.parametrize(
    "mutate,code",
    (
        ("prefix", "E_SHA"),
        ("blank_blocker", "E_BLOCKERS"),
        ("blank_finding", "E_REJECTION_EVIDENCE"),
        ("finding_without_shas", "E_REJECTION_EVIDENCE"),
        ("blank_resolution", "E_REJECTION_EVIDENCE"),
        ("empty_dependency", "E_REJECTION_IDENTITY"),
    ),
)
def test_record_rejection_malformed_inputs(
    record_fixture: dict[str, Any], mutate: str, code: str
) -> None:
    fixture = record_fixture
    kwargs: dict[str, Any] = {}
    if mutate == "prefix":
        kwargs["rejected_head_sha"] = fixture["head"][:7]
    elif mutate == "blank_blocker":
        kwargs["blockers"] = ["   "]
    elif mutate == "blank_finding":
        kwargs["finding"] = "   "
    elif mutate == "finding_without_shas":
        kwargs["finding"] = "a finding that names nothing verifiable"
    elif mutate == "blank_resolution":
        kwargs["resolution_condition"] = ""
    elif mutate == "empty_dependency":
        kwargs["dependency_id"] = ""
    with pytest.raises(taskctl.TaskControlError, match=code):
        _record(fixture, **kwargs)


@needs_git
def test_record_rejection_deduplicates_blockers(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    entry = _record(fixture, blockers=["durable blocker", " durable blocker ", "other"])
    assert entry["blockers"] == ["durable blocker", "other"]


@needs_git
@pytest.mark.parametrize(
    "variant,code",
    (
        ("missing_path", "E_REJECTION_BLOB_MISSING"),
        ("invalid_json", "E_REJECTION_BLOB_CORRUPT"),
        ("wrong_shape", "E_REJECTION_BLOB_CORRUPT"),
        ("missing_keys", "E_REJECTION_BLOB_CORRUPT"),
        ("unsupported_schema", "E_REJECTION_SCHEMA"),
    ),
)
def test_record_rejection_blob_failures(
    record_fixture: dict[str, Any], variant: str, code: str
) -> None:
    fixture = record_fixture
    work = fixture["work"]
    if variant == "missing_path":
        _git(work, "checkout", "-q", TARGET_BRANCH)
        try:
            _git(work, "rm", "-q", taskctl.TARGET_STATE_PATH)
            _git(work, "commit", "-q", "-m", "commit without blob")
            dangling = _git(work, "rev-parse", "HEAD")
        finally:
            _git(work, "checkout", "-q", LIVE_BRANCH)
    elif variant == "invalid_json":
        dangling = _target_variant(fixture, b"{\xff not json", "invalid blob")
    elif variant == "wrong_shape":
        dangling = _target_variant(fixture, "[1, 2]\n", "list blob")
    elif variant == "missing_keys":
        dangling = _target_variant(
            fixture,
            json.dumps({"schema_version": "geox_repo_execution_state_v3"}) + "\n",
            "keyless blob",
        )
    else:
        blob = _target_blob(
            implementation=fixture["implementation"],
            authorization=fixture["main0"],
            baseline=fixture["main0"],
            prior=(fixture["prior_review"], fixture["implementation"]),
        )
        blob["schema_version"] = "geox_repo_execution_state_v5"
        dangling = _target_variant(
            fixture, json.dumps(blob, indent=2) + "\n", "v5 blob"
        )
    _retarget_pin(fixture, dangling)
    with pytest.raises(taskctl.TaskControlError, match=code):
        _record(fixture, rejected_head_sha=dangling)


@needs_git
def test_record_rejection_accepts_v3_and_v4_targets(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    entry = _record(fixture)
    assert entry["target_schema_version"] == "geox_repo_execution_state_v3"
    work = fixture["work"]
    _git(
        work,
        "add",
        "docs/execution/EXECUTION_STATE.json",
        "docs/execution/ACTIVE_TASK.md",
        "docs/execution/LATEST_COMPLETION_REPORT.md",
    )
    _git(work, "commit", "-q", "-m", "first rejection record")
    _git(work, "checkout", "-q", TARGET_BRANCH)
    blob = _target_blob(
        implementation=fixture["implementation"],
        authorization=fixture["main0"],
        baseline=fixture["main0"],
        prior=(fixture["prior_review"], fixture["implementation"]),
        extra={"completion_evidence": {"anything": True}},
    )
    blob["schema_version"] = "geox_repo_execution_state_v4"
    advanced = _commit(work, taskctl.TARGET_STATE_PATH, json.dumps(blob, indent=2) + "\n", "v4 blob")
    _git(work, "push", "-q", "origin", TARGET_BRANCH)
    _git(work, "checkout", "-q", LIVE_BRANCH)
    live = json.loads(fixture["state_path"].read_text(encoding="utf-8"))
    for dependency in live["dependencies"]:
        if dependency["dependency_id"] == DEPENDENCY_ID:
            dependency["remote_head_sha"] = advanced
    fixture["state_path"].write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
    taskctl.sync(
        state_path=fixture["state_path"],
        active_path=fixture["active_path"],
        report_path=fixture["report_path"],
    )
    _git(work, "add", "docs/execution/EXECUTION_STATE.json")
    _git(work, "commit", "-q", "-m", "retarget pin to v4 head")
    entry = _record(fixture, rejected_head_sha=advanced)
    assert entry["target_schema_version"] == "geox_repo_execution_state_v4"
    assert len(json.loads(fixture["state_path"].read_text(encoding="utf-8"))["rejection_history"]) == 2


@needs_git
def test_record_rejection_duplicate_fails_without_write(
    record_fixture: dict[str, Any],
) -> None:
    fixture = record_fixture
    _record(fixture)
    before = (
        fixture["state_path"].read_bytes(),
        fixture["active_path"].read_bytes(),
        fixture["report_path"].read_bytes(),
    )
    with pytest.raises(taskctl.TaskControlError, match="E_TRANSITION"):
        _record(fixture)
    after = (
        fixture["state_path"].read_bytes(),
        fixture["active_path"].read_bytes(),
        fixture["report_path"].read_bytes(),
    )
    assert before == after
    assert len(json.loads(before[0])["rejection_history"]) == 1


@needs_git
def test_record_rejection_invalid_changes_no_tracked_file(
    record_fixture: dict[str, Any],
) -> None:
    fixture = record_fixture
    before = (
        fixture["state_path"].read_bytes(),
        fixture["active_path"].read_bytes(),
        fixture["report_path"].read_bytes(),
    )
    _retarget_pin(fixture, "e" * 40)
    pinned = (
        fixture["state_path"].read_bytes(),
        fixture["active_path"].read_bytes(),
        fixture["report_path"].read_bytes(),
    )
    with pytest.raises(taskctl.TaskControlError, match="E_REJECTION_BLOB_MISSING"):
        _record(fixture, rejected_head_sha="e" * 40)
    assert pinned == (
        fixture["state_path"].read_bytes(),
        fixture["active_path"].read_bytes(),
        fixture["report_path"].read_bytes(),
    )
    assert before != pinned


@needs_git
def test_interrupted_state_view_recovery(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    stale_report = fixture["report_path"].read_bytes()
    _record(fixture)
    state_bytes = fixture["state_path"].read_bytes()
    fixture["report_path"].write_bytes(stale_report)
    with pytest.raises(taskctl.TaskControlError, match="E_VIEW_DIVERGENCE"):
        taskctl.check(
            state_path=fixture["state_path"],
            active_path=fixture["active_path"],
            report_path=fixture["report_path"],
        )
    taskctl.sync(
        state_path=fixture["state_path"],
        active_path=fixture["active_path"],
        report_path=fixture["report_path"],
    )
    assert fixture["state_path"].read_bytes() == state_bytes
    taskctl.check(
        state_path=fixture["state_path"],
        active_path=fixture["active_path"],
        report_path=fixture["report_path"],
    )
    with pytest.raises(taskctl.TaskControlError, match="E_TRANSITION"):
        _record(fixture)
    assert len(json.loads(fixture["state_path"].read_text(encoding="utf-8"))["rejection_history"]) == 1


@needs_git
def test_v5_history_renders_deterministically(record_fixture: dict[str, Any]) -> None:
    fixture = record_fixture
    _record(fixture)
    canonical = json.loads(fixture["state_path"].read_text(encoding="utf-8"))
    first = taskctl.render(canonical, "completion_report")
    assert taskctl.render(canonical, "completion_report") == first
    assert "Rejection history" in first
    assert fixture["head"] in first
    before = fixture["report_path"].read_bytes(), fixture["active_path"].read_bytes()
    taskctl.sync(
        state_path=fixture["state_path"],
        active_path=fixture["active_path"],
        report_path=fixture["report_path"],
    )
    assert (fixture["report_path"].read_bytes(), fixture["active_path"].read_bytes()) == before


def _v5_state_with_entry(**updates: Any) -> dict[str, Any]:
    canonical = json.loads(taskctl.STATE_PATH.read_text(encoding="utf-8"))
    canonical["schema_version"] = taskctl.SCHEMA_VERSION
    canonical["rejection_history"] = [
        {
            "target_repository": "Phani-Pavuluri/panel_exp",
            "target_task_id": "GEOX_FIXTURE_TARGET_001",
            "target_branch": TARGET_BRANCH,
            "target_head_sha": "a" * 40,
            "target_implementation_sha": "b" * 40,
            "target_authorization_head_sha": "c" * 40,
            "target_branch_baseline_sha": "d" * 40,
            "target_schema_version": "geox_repo_execution_state_v4",
            "target_disposition": "blocked",
            "target_counters": {"maximum": 1, "completed": 1, "remaining": 0},
            "prior_rejected_review_head_sha": "e" * 40,
            "prior_rejected_implementation_commit_sha": "f" * 40,
            "finding": "finding names " + "a" * 40 + " and " + "b" * 40,
            "resolution_condition": "fresh recovery after merged record",
            "live_main_sha": "9" * 40,
            "blockers": ["durable blocker"],
        }
    ]
    canonical["rejection_history"][0].update(updates)
    return canonical


@pytest.mark.parametrize(
    "updates,code",
    (
        ({"target_repository": "Other/other"}, "E_REJECTION_IDENTITY"),
        ({"target_disposition": "approved"}, "E_REJECTION_EVIDENCE"),
        ({"target_schema_version": "geox_repo_execution_state_v5"}, "E_REJECTION_SCHEMA"),
        ({"target_head_sha": "short"}, "E_SHA"),
        ({"finding": "names nothing"}, "E_REJECTION_EVIDENCE"),
        ({"resolution_condition": "  "}, "E_REJECTION_EVIDENCE"),
        ({"blockers": []}, "E_BLOCKERS"),
        ({"blockers": ["x", "x"]}, "E_BLOCKERS"),
        ({"target_counters": {"maximum": 1, "completed": 0, "remaining": 1}}, "E_REJECTION_BUDGET"),
        ({"prior_rejected_review_head_sha": None}, "E_REJECTED_PROVENANCE"),
        ({"target_task_id": ""}, "E_REJECTION_IDENTITY"),
    ),
)
def test_malformed_history_entry_fails_closed(updates: dict[str, Any], code: str) -> None:
    with pytest.raises(taskctl.TaskControlError, match=code):
        taskctl.validate_state(_v5_state_with_entry(**updates))


def test_schema_boundaries_fail_closed() -> None:
    canonical = json.loads(taskctl.STATE_PATH.read_text(encoding="utf-8"))
    legacy = dict(canonical)
    legacy["schema_version"] = taskctl.LEGACY_SCHEMA_VERSION_V3
    legacy["rejection_history"] = []
    with pytest.raises(taskctl.TaskControlError, match="E_STATE_KEYS"):
        taskctl.validate_state(legacy)
    current = _v5_state_with_entry()
    current["completion_evidence"] = {"anything": True}
    with pytest.raises(taskctl.TaskControlError, match="E_STATE_KEYS"):
        taskctl.validate_state(current)
    current = _v5_state_with_entry()
    current["schema_version"] = "geox_repo_execution_state_v4"
    with pytest.raises(taskctl.TaskControlError, match="E_SCHEMA_VERSION"):
        taskctl.validate_state(current)
    taskctl.validate_state(_v5_state_with_entry())
