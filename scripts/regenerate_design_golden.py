#!/usr/bin/env python3
"""Regenerate tests/fixtures/design_golden baselines."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from panel_exp.design.assign import (
    BalancedRandomization,
    CompleteRandomization,
    StratifiedRandomization,
    greedy_match_markets,
)
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from tests.design_registry_helpers import (
    GOLDEN_DIR,
    assignment_to_golden_payload,
    make_geo_panel,
)

SEED = 42


def main() -> None:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    panel = make_geo_panel(seed=SEED)

    configs = (
        ("greedy_match_markets", greedy_match_markets),
        ("balanced", BalancedRandomization),
        ("complete", CompleteRandomization),
        ("stratified", StratifiedRandomization),
    )
    for label, cls in configs:
        geo = GeoExperimentDesign(
            panel_data=panel,
            base_randomizer_cls=cls,
            random_state=SEED,
            test_lengths=[28],
            n_test_grps=1,
            validate_after_assign=False,
            max_iter=8,
        )
        design = geo.create_design()
        assignment = design.assign(panel_data=panel, n_test_grps=1)
        path = GOLDEN_DIR / f"assignment_{label}.json"
        path.write_text(
            json.dumps(assignment_to_golden_payload(assignment), sort_keys=True, indent=2)
        )
        print(f"wrote {path.name} labels={assignment_to_golden_payload(assignment)['group_labels']}")

    meta = {
        "seed": SEED,
        "n_units": 12,
        "n_times": 50,
        "max_iter": 8,
        "group_labels": ["control", "test_0"],
        "note": "Assignment goldens include group_labels + assignments maps.",
    }
    (GOLDEN_DIR / "meta.json").write_text(json.dumps(meta, indent=2))
    print("done")


if __name__ == "__main__":
    main()
