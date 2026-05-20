"""Legacy greedy_match_markets smoke test (constraint-contract aware)."""

import unittest

import pandas as pd

from panel_exp.design.assign import greedy_match_markets
from panel_exp.panel_data import TimePeriod, long_df_to_paneldataset


def _build_panel_and_assign():
    df = pd.DataFrame(
        {
            "geo": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5],
            "date": [
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
            ],
            "y": [1, 2, 3, 4, 5, 6, 1, 2, 3, 2, 3, 5, 3, 4, 5],
        }
    )
    df["date"] = pd.to_datetime(df["date"])
    df["geo"] = df["geo"].astype(str)
    df["y"] = df["y"].astype(float)

    # Constraint contract: whitelisted units must be assignable to their arm.
    # Legacy fixture used control_whitelist "2" with test_blacklist "2" (excluded) and
    # test_whitelist "1" with control_blacklist "1" (excluded) — impossible under validation.
    control_whitelist = ["3"]
    test_whitelist = ["5"]
    control_blacklist = ["1"]
    test_blacklist = ["2"]
    control_test_blacklist = ["4"]
    treated_times = TimePeriod(
        pd.to_datetime("2020-01-02"), pd.to_datetime("2020-01-03")
    )
    treated_units = ["5"]

    panel_dataset = long_df_to_paneldataset(
        df,
        time_column="date",
        unit_column="geo",
        value_column="y",
        treated_start_times=pd.to_datetime("2020-01-02"),
        treated_units=treated_units,
    )

    gm = greedy_match_markets(func_to_optimize="corr")
    assignment = gm.assign(
        panel_data=panel_dataset,
        treatment_period=treated_times,
        control_whitelist=control_whitelist,
        test_whitelist=test_whitelist,
        control_blacklist=control_blacklist,
        test_blacklist=test_blacklist,
        control_test_blacklist=control_test_blacklist,
    )
    return assignment, df, treated_units


class TestMethods(unittest.TestCase):
    def test_greedy_match_output(self):
        assignment, input_df, treated_units = _build_panel_and_assign()
        all_units = set(input_df["geo"].unique())
        assigned = set(assignment["control"]) | set(assignment["test_0"])

        self.assertGreaterEqual(len(treated_units), 1)
        self.assertGreaterEqual(len(assignment["control"]), 1)
        self.assertLessEqual(len(assigned), len(all_units))
        self.assertIn("5", assignment["test_0"])
        self.assertIn("3", assignment["control"])
        self.assertNotIn("4", assigned)
        self.assertNotIn("2", assigned)


if __name__ == "__main__":
    unittest.main()
