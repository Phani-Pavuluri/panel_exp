from panel_exp.artifacts import build_geox_governed_readout_package_entrypoint
from panel_exp.contracts.geox_governed_experiment_readout import build_example_geox_stale_readout, build_example_geox_success_readout


def test_builder_preserves_readout_and_blocks_transport() -> None:
    readout = build_example_geox_success_readout()
    result, envelope = build_geox_governed_readout_package_entrypoint(readout, envelope_metadata={"created_at": "2026-01-01T00:00:00Z", "request_id": "req-1", "input_data_fingerprint": "sha256:fixture", "schema_hash": "sha256:schema"})
    assert result == readout
    assert envelope.authorization_status.value == "blocked"
    assert envelope.mip_consumption_status.value == "blocked"


def test_freshness_is_reference_time_deterministic() -> None:
    readout = build_example_geox_stale_readout()
    result, _ = build_geox_governed_readout_package_entrypoint(
        readout, valid_through="2026-01-01T00:00:00Z", reference_time="2026-01-02T00:00:00Z",
        envelope_metadata={"created_at": "2025-01-01T00:00:00Z", "request_id": "req-1", "input_data_fingerprint": "sha256:fixture", "schema_hash": "sha256:schema"}
    )
    assert result.freshness_status == "stale"
