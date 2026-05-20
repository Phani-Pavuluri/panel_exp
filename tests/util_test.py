import pytest


# UTIL Tests
from panel_exp.util import standardize
import numpy as np
import pandas as pd


def test_standardize_one():
    # test if properly standarizes single numpy array

    data_c1 = np.random.normal(100, 10, 1000)

    mean_c1 = np.mean(data_c1)
    std_c1 = np.std(data_c1)

    s1 = standardize(data_c1)

    assert np.isclose(s1.transform(data_c1).mean(), 0), "Test Failed"
    assert np.isclose(s1.transform(data_c1).std(), 1), "Test Failed"

    assert np.isclose(
        s1.inverse_transform(s1.transform(data_c1)).mean(), mean_c1
    ), "Test Failed"
    assert np.isclose(
        s1.inverse_transform(s1.transform(data_c1)).std(), std_c1
    ), "Test Failed"


def test_standardize_two():
    # test if properly standarizes pandas df columnwise

    data_c1 = np.random.normal(100, 10, 1000)
    data_c2 = np.random.normal(150, 10, 1000)

    mean_c1 = np.mean(data_c1)
    std_c1 = np.std(data_c1)

    mean_c2 = np.mean(data_c2)
    std_c2 = np.std(data_c2)

    df = pd.DataFrame({"c1": data_c1, "c2": data_c2})

    s1 = standardize(df)

    assert np.isclose(s1.transform(df).mean(axis=0).c1, 0), "Test Failed"
    assert np.isclose(s1.transform(df).mean(axis=0).c2, 0), "Test Failed"

    assert np.isclose(s1.transform(df).std(axis=0).c1, 1, rtol=1e-03), "Test Failed"
    assert np.isclose(s1.transform(df).std(axis=0).c2, 1, rtol=1e-03), "Test Failed"

    assert np.isclose(
        s1.inverse_transform(s1.transform(df)).mean(axis=0).c1, mean_c1
    ), "Test Failed"
    assert np.isclose(
        s1.inverse_transform(s1.transform(df)).mean(axis=0).c2, mean_c2
    ), "Test Failed"

    assert np.isclose(
        s1.inverse_transform(s1.transform(df)).std(axis=0).c1, std_c1, rtol=1e-03
    ), "Test Failed"
    assert np.isclose(
        s1.inverse_transform(s1.transform(df)).std(axis=0).c2, std_c2, rtol=1e-03
    ), "Test Failed"

    assert np.isclose(
        s1.inverse_transform(s1.transform(df)).c1.sum(), data_c1.sum()
    ), "Test Failed"
    assert np.isclose(
        s1.inverse_transform(s1.transform(df)).c2.sum(), data_c2.sum()
    ), "Test Failed"


def test_standardize_three():
    # test to see if properly standardizes numpy array columwise

    data_c1 = np.random.normal(100, 10, 1000)
    data_c2 = np.random.normal(150, 10, 1000)

    mean_c1 = np.mean(data_c1)
    std_c1 = np.std(data_c1)

    mean_c2 = np.mean(data_c2)
    std_c2 = np.std(data_c2)

    np_arr = np.vstack([data_c1, data_c2]).T

    s1 = standardize(np_arr)

    assert np.isclose(s1.transform(np_arr).mean(axis=0)[0], 0), "Test Failed"
    assert np.isclose(s1.transform(np_arr).mean(axis=0)[1], 0), "Test Failed"

    assert np.isclose(s1.transform(np_arr).std(axis=0)[0], 1), "Test Failed"
    assert np.isclose(s1.transform(np_arr).std(axis=0)[1], 1), "Test Failed"

    assert np.isclose(
        s1.inverse_transform(s1.transform(np_arr)).mean(axis=0)[0], mean_c1
    ), "Test Failed"
    assert np.isclose(
        s1.inverse_transform(s1.transform(np_arr)).mean(axis=0)[1], mean_c2
    ), "Test Failed"

    assert np.isclose(
        s1.inverse_transform(s1.transform(np_arr)).std(axis=0)[0], std_c1
    ), "Test Failed"
    assert np.isclose(
        s1.inverse_transform(s1.transform(np_arr)).std(axis=0)[1], std_c2
    ), "Test Failed"

    assert np.isclose(
        s1.inverse_transform(s1.transform(np_arr))[:, 0].sum(), data_c1.sum()
    ), "Test Failed"
    assert np.isclose(
        s1.inverse_transform(s1.transform(np_arr))[:, 1].sum(), data_c2.sum()
    ), "Test Failed"
