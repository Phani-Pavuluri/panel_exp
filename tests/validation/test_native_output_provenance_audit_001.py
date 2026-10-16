"""Standing provenance audit for native outputs (existing fields only).

Asserts that produced native evidence resolves to its inputs plus code
version, distinguishing builder-computed identities (recomputed in-test)
from caller-supplied passthrough (asserted equal to caller input) and
shape-only metadata (code_version, created_at). ReadoutEvidence carries no
package/input-hash fields by construction; that limitation is asserted, not
assumed. No production behavior is changed by these tests.
"""

from __future__ import annotations

from typing import Any

import pytest

from panel_exp import evidence as evidence_module
from panel_exp.design.assign import CompleteRandomization
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.evidence import (
    EVIDENCE_VERSION,
    ExperimentEvidence,
    input_data_hash_from_wide,
)
from panel_exp.evidence_hash import assignment_hash
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.estimator_readout_adapter_001 import ADAPTER_VERSION
from panel_exp.validation.readout_boundary_builder_001 import (
    BUILDER_VERSION,
    build_guarded_readout,
)
from panel_exp.artifacts.run_bundle import build_run_artifact_bundle
from tests.design_registry_helpers import make_geo_panel


def _stub_mde(monkeypatch) -> None:
    def _fake_metrics(self, *args, **kwargs):
        import pandas as pd

        empty = pd.DataFrame()
        return empty, empty, empty

    monkeypatch.setattr(GeoExperimentDesign, "_calculate_sensitivity_metrics", _fake_metrics)


def _prov_spec() -> Any:
    return spec_from_geo_design(
        "prov-test",
        "outcome",
        "unit",
        "time",
        pre_period=TimePeriod(start=0, end=20),
        experiment_period=TimePeriod(start=20, end=None),
        design_method="completerandomization",
    )


_PROV_ASSIGNMENT = {"control": ["u0"], "test_0": ["u1"]}


def test_design_evidence_provenance_resolves() -> None:
    panel = make_geo_panel(seed=7, n_units=10, n_times=40)
    spec = _prov_spec()
    input_hash = input_data_hash_from_wide(panel.wide_data)
    evidence = ExperimentEvidence.build(
        spec, dict(_PROV_ASSIGNMENT), input_data_hash=input_hash
    )
    assert evidence.spec_hash == spec.content_hash()
    assert evidence.assignment_hash == assignment_hash(_PROV_ASSIGNMENT)
    assert evidence.input_data_hash == input_hash
    assert evidence.package_version == evidence_module.__version__
    assert evidence.evidence_version == EVIDENCE_VERSION
    assert evidence.code_version is None or (
        isinstance(evidence.code_version, str) and evidence.code_version.strip()
    )


def test_assignment_override_is_scoped_passthrough() -> None:
    spec = _prov_spec()
    override = "f" * 40
    evidence = ExperimentEvidence.build(
        spec, dict(_PROV_ASSIGNMENT), assignment_hash_override=override
    )
    assert evidence.assignment_hash == override
    assert evidence.spec_hash == spec.content_hash()
    assert evidence.package_version == evidence_module.__version__


def test_pipeline_evidence_provenance_resolves(monkeypatch) -> None:
    _stub_mde(monkeypatch)
    panel = make_geo_panel(seed=7, n_units=10, n_times=40)
    geo = GeoExperimentDesign(
        panel_data=panel,
        base_randomizer_cls=CompleteRandomization,
        n_test_grps=1,
        random_state=11,
        validate_after_assign=False,
        test_lengths=[28],
        max_iter=5,
    )
    geo.run_design()
    assert geo.last_evidence is not None
    evidence = geo.last_evidence
    assert evidence.package_version == evidence_module.__version__
    assert evidence.evidence_version == EVIDENCE_VERSION
    assert evidence.input_data_hash == input_data_hash_from_wide(panel.wide_data)
    assert evidence.spec_hash == evidence.design.spec_hash
    assert evidence.assignment_hash == evidence.design.assignment_hash
    assert evidence.code_version is None or (
        isinstance(evidence.code_version, str) and evidence.code_version.strip()
    )


def test_readout_evidence_owned_fields_only() -> None:
    result = build_guarded_readout(
        design_evidence={"experiment_id": "prov", "design_name": "complete_randomization"},
        estimator_id="prov-estimator",
        enforce=False,
    )
    assert result.evidence_version == EVIDENCE_VERSION
    assert result.builder_version == BUILDER_VERSION
    assert not hasattr(result, "package_version")
    assert result.created_at is not None and isinstance(result.created_at, str)


def test_run_bundle_lineage_passthrough() -> None:
    panel = make_geo_panel(seed=7, n_units=10, n_times=40)
    spec = _prov_spec()
    evidence = ExperimentEvidence.build(
        spec,
        dict(_PROV_ASSIGNMENT),
        input_data_hash=input_data_hash_from_wide(panel.wide_data),
    )
    bundle = build_run_artifact_bundle(evidence=evidence)
    lineage = dict(bundle.lineage)
    assert lineage["evidence_version"] == evidence.evidence_version
    assert lineage["spec_hash"] == evidence.spec_hash
    assert lineage["assignment_hash"] == evidence.assignment_hash
    assert lineage["package_version"] == evidence.package_version
    assert lineage["input_structure_hash"] == evidence.input_structure_hash
    assert lineage["input_structure_hash"] == evidence.input_data_hash
    assert lineage["code_version"] == evidence.code_version
    assert "input_data_hash" not in lineage


def test_run_bundle_mapping_path_carries_input_data_hash_and_drops_none() -> None:
    panel = make_geo_panel(seed=7, n_units=10, n_times=40)
    spec = _prov_spec()
    evidence = ExperimentEvidence.build(
        spec,
        dict(_PROV_ASSIGNMENT),
        input_data_hash=input_data_hash_from_wide(panel.wide_data),
    )
    mapping = dict(evidence.to_dict())
    assert mapping["input_data_hash"] is not None
    bundle = build_run_artifact_bundle(evidence=mapping)
    lineage = dict(bundle.lineage)
    assert lineage["input_data_hash"] == mapping["input_data_hash"]
    assert lineage["input_structure_hash"] == mapping["input_structure_hash"]
    sparsified = dict(mapping)
    sparsified["code_version"] = None
    sparse_lineage = dict(build_run_artifact_bundle(evidence=sparsified).lineage)
    assert "code_version" not in sparse_lineage
    assert sparse_lineage["input_data_hash"] == mapping["input_data_hash"]
