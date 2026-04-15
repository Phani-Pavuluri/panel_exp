import unittest
from panel_exp.panel_data import long_df_to_paneldataset, TimePeriod
from panel_exp.design.assign import greedy_match_markets
import pandas as pd
import numpy as np

class greedy_market_match_test:

    def get_results():

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
            "y": [1, 2, 3, 4, 5, 6, 1, 2, 3, 2, 3, 5, 3, 4, 5]})

        df["date"] = pd.to_datetime(df["date"])
        df["geo"] = df["geo"].astype(str)
        df["y"] = df["y"].astype(float)

        c_whitelist = ['2']
        t_whitelist = ['1']
        c_blacklist = ['1']
        t_blacklist = ['2']
        c_t_blacklist = ['4']
        treated_times = TimePeriod(pd.to_datetime("2020-01-02"),pd.to_datetime("2020-01-03"))
        treated_units=['1']

        panel_dataset = long_df_to_paneldataset(
            df,
            time_column="date",
            unit_column="geo",
            value_column="y",
            treated_start_times=pd.to_datetime("2020-01-02"),
            treated_units=treated_units)

        gm = greedy_match_markets(func_to_optimize='corr')
        results = gm.assign(panel_data=panel_dataset,treatment_period=treated_times,control_whitelist=c_whitelist,test_whitelist=t_whitelist,control_blacklist=c_blacklist,test_blacklist=t_blacklist,control_test_blacklist=c_t_blacklist) 

        return results,df,treated_units


class TestMethods(unittest.TestCase):

    def test_greedy_match_output(self):
        results,input_df,treated_units = greedy_market_match_test.get_results()
        self.assertTrue(len(treated_units) >= 1, 'treated units cannot be empty')    
        self.assertTrue(len(set(results.wide_data.index.values.tolist()) - set(treated_units)) >= 1, 'control units cannot be empty')  
        self.assertTrue(len(results.wide_data.index.values) <= input_df.geo.nunique(), 'resulted panel data cannot have more units than raw data')  
        self.assertTrue(results.wide_data.sum().sum() <= input_df.y.sum(), 'resulted panel data cannot have response sum greater than input raw data')
        self.assertTrue(len(results.wide_data.columns.values) == input_df.date.nunique(), 'resulted panel data should contain same number of timepoints as raw data')
        self.assertFalse(results.wide_data.isnull().all(axis=1).any(), 'all values cannot be nan/empty for any treated or control unit')  

if __name__ == "__main__":
    unittest.main()