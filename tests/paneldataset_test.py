import pytest

from panel_exp.panel_data import long_df_to_paneldataset
import numpy as np
import pandas as pd


def test_long_df_to_paneldataset():
    df = pd.DataFrame(
        {
            "unit": [1, 1, 1, 2, 2, 2],
            "date": [
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
            ],
            "y": [1, 2, 3, 4, 5, 6],
        }
    )
    df["date"] = pd.to_datetime(df["date"])
    df["unit"] = df["unit"].astype(str)
    df["y"] = df["y"].astype(float)

    treated_time = pd.to_datetime("2020-01-02")

    panel_dataset = long_df_to_paneldataset(
        df,
        time_column="date",
        unit_column="unit",
        value_column="y",
        treated_start_times=treated_time,
        treated_units="1",
    )
    assert panel_dataset.wide_data.shape == (2, 3)
    assert np.all(
        panel_dataset.wide_data.columns.tolist()
        == pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])
    )
    assert panel_dataset.wide_data.index.tolist() == ["1", "2"]

    assert panel_dataset.wide_data.iloc[:, 0].tolist() == [1, 4]
    assert panel_dataset.wide_data.iloc[:, 1].tolist() == [2, 5]
    assert panel_dataset.wide_data.iloc[:, 2].tolist() == [3, 6]
    assert panel_dataset.treated_periods[0].start == pd.to_datetime("2020-01-02")
