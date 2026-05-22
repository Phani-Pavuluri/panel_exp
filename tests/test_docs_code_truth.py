"""Documentation consistency checks against the method registry and code truth."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from panel_exp.method_metadata import EstimatorMaturity
from panel_exp.method_registry import get_method_registry

REPO_ROOT = Path(__file__).resolve().parents[1]

DOC_PATHS = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "gh-pages" / "_sources" / "user_guide.md.txt",
    REPO_ROOT / "docs" / "VALIDATION_COVERAGE.md",
    REPO_ROOT / "docs" / "ROADMAP_REASSESSMENT.md",
    REPO_ROOT / "examples" / "README.md",
)

RESEARCH_ONLY_DOC_NAMES = frozenset(
    {"BayesianTBR", "BayesianTBRHorseShoe", "SyntheticDID", "TROP", "MTGP"}
)

SUPPORTED_WORKFLOW_MARKERS = (
    "SCM",
    "TBRRidge",
    "TBR",
    "DID",
    "design orchestration",
    "experiment card",
    "readiness",
    "calibration",
    "run bundle",
)

LEGACY_BANNER = "Legacy example — not current package contract"

PROMOTING_PRODUCTION_SAFE = re.compile(
    r"(?<!no )(?<!not )(?<!zero )production[_\s-]?safe\s+(estimator|mode|workflow|rating)",
    re.IGNORECASE,
)


def _read_doc(path: Path) -> str:
    assert path.is_file(), f"Missing doc file: {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def registry():
    return get_method_registry()


def test_research_only_estimators_in_registry(registry):
    for name in RESEARCH_ONLY_DOC_NAMES:
        assert name in registry.list_estimator_names()
        assert registry.metadata(name).maturity == EstimatorMaturity.RESEARCH_ONLY


def test_supported_workflow_estimators_exist(registry):
    for name in ("SCM", "TBRRidge", "DID"):
        assert name in registry.list_estimator_names()
        assert registry.metadata(name).maturity == EstimatorMaturity.EXPERT_REVIEW


def test_no_production_safe_estimators_in_catalog(registry):
    for name in registry.list_estimator_names():
        assert registry.metadata(name).maturity != EstimatorMaturity.PRODUCTION_SAFE


def test_user_guide_lists_supported_and_research_only_sections():
    text = _read_doc(REPO_ROOT / "gh-pages" / "_sources" / "user_guide.md.txt")
    assert "## Current Package Status" in text
    assert "### Supported (shipped workflows)" in text
    assert "### Research-only (catalog)" in text
    for name in RESEARCH_ONLY_DOC_NAMES:
        assert name in text


def test_supported_workflow_mentioned_in_readme():
    text = _read_doc(REPO_ROOT / "README.md")
    lowered = text.lower()
    for marker in SUPPORTED_WORKFLOW_MARKERS:
        assert marker.lower() in lowered or marker in text


def test_no_removed_panel_exp_util_module_in_published_docs():
    for path in DOC_PATHS:
        text = _read_doc(path)
        assert "panel_exp.util" not in text or "removed" in text.lower() or "not shipped" in text.lower()


def test_pretest_analysis_mentions_legacy_context_in_published_docs():
    for path in (REPO_ROOT / "README.md", REPO_ROOT / "gh-pages" / "_sources" / "user_guide.md.txt"):
        text = _read_doc(path)
        if "pretest_analysis" not in text:
            continue
        assert (
            "legacy" in text.lower()
            or "not shipped" in text.lower()
            or "not current" in text.lower()
        )


def test_production_safe_not_advertised_in_docs():
    for path in DOC_PATHS:
        text = _read_doc(path)
        match = PROMOTING_PRODUCTION_SAFE.search(text)
        assert match is None, (
            f"{path.name} appears to advertise production_safe: {match.group(0)!r}"
        )


def test_legacy_dashboard_sections_have_banner():
    text = _read_doc(REPO_ROOT / "gh-pages" / "_sources" / "user_guide.md.txt")
    assert LEGACY_BANNER in text
    assert text.index(LEGACY_BANNER) < text.index("create_design_comparison_dashboard")


def test_decision_workflow_includes_run_bundle():
    for path in (REPO_ROOT / "README.md", REPO_ROOT / "gh-pages" / "_sources" / "user_guide.md.txt"):
        text = _read_doc(path)
        assert "Run Bundle" in text or "run bundle" in text.lower()
        assert "VALIDATION_COVERAGE" in text or "validation coverage" in text.lower()


def test_doc_drift_audit_file_exists():
    assert (REPO_ROOT / "docs" / "DOC_DRIFT_AUDIT.md").is_file()
