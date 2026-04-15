# analysis_helper

import pandas as pd 
from panel_exp.panel_data import long_df_to_paneldataset, PanelDataset, TimePeriod
from panel_exp.impact import ImpactAnalyzer

from typing import NewType
from typing import Type
from typing import NamedTuple


def pds_create(df: pd.DataFrame, 
          cloud: str, 
          kpi: str, 
          aggregation: str, 
          de_mean: bool, 
          test: list, 
          control: list, 
          start_date: str, 
          end_date: str, 
          analysis_start_date: str) -> PanelDataset:
    """This will take in arguments and create a Panel Dataset for analysis with Panel Exp Package. 

    Args:
        df (pd.DataFrame): Long DataFrame that contains date, dma, segment and KPI information.
        cloud (str): What cloud should we create the PDS for.
        kpi (str): What KPI we like to analyze. 
        aggregation (str): How should we aggregate test results: none, sum, mean
        de_mean (bool): Should we de-mean the results.
        test (list): List of dma_ids in the test group.
        control (list): List of dma_ids in the control group.
        start_date (str): Start date of test in format "YYYY-MM-DD"
        end_date (str): End date of test in format "YYYY-MM-DD"
        analysis_start_date (str): At what point do we want to start the analysis. Typically 1-2 years of pre-test data before test start date. Format "YYYY-MM-DD"

    Returns:
        PanelDataset: Returns a Panel Dataset to be used for further analysis. 
    """
    
    if cloud:
        if cloud.lower() == 'dme':
            segments = ("ACROBAT DC", "ACROBAT CC", "INDIVIDUAL" , "PHOTOGRAPHY" , "HED", "K12+EEA", "TEAM", "STUDENT")
            df = df[df.cc_segment.isin(segments)]
        elif cloud.lower() == 'dc':
            segments = ("ACROBAT DC", "ACROBAT CC")
            df = df[df.cc_segment.isin(segments)]
        elif cloud.lower() == 'cc':
            segments = ("INDIVIDUAL" , "PHOTOGRAPHY" , "HED", "K12+EEA", "TEAM", "STUDENT")
            df = df[df.cc_segment.isin(segments)]
        
    test = [int(t) for t in test]
    control = [int(c) for c in control]
    
    #df['dma_id'] = df['dma_id'].astype(int)
    
    if not end_date:
        end_date = df.date_date.max()
        
    if analysis_start_date:
        df = df[df.date_date >= analysis_start_date]
    
    if aggregation.lower() == 'none':
        df = df[(df.dma_id.isin(test+control)) & (df.date_date<=end_date)]

        wide_df = pd.pivot_table(df[df.dma_id.isin(test+control)]
                                , index='dma_id'
                                , columns='date_date'
                                , values=kpi.lower()
                                , fill_value=0
                                , aggfunc='sum') 
        
        wag = (wide_df - wide_df.mean(axis=0))
        if de_mean:
            wag = (wide_df - wide_df.mean(axis=0))
            pds = PanelDataset(wag, treated_units=test, treated_periods=[TimePeriod(start=start_date) for _ in range(len(test))])
        else:
            pds = PanelDataset(wide_df, treated_units=test, treated_periods=[TimePeriod(start=start_date) for _ in range(len(test))])


        

    if aggregation.lower() != 'none':
        df = df[(df.dma_id.isin(test+control)) & (df.date_date<=end_date)]

        wide_df = pd.pivot_table(df[df.dma_id.isin(test+control)]
                                , index='dma_id'
                                , columns='date_date'
                                , values=kpi.lower()
                                , fill_value=0
                                , aggfunc='sum') 
        
        control_units = wide_df[wide_df.index.isin(control)] .T
        if aggregation.lower() == 'mean':
            treated_units = pd.DataFrame(wide_df[wide_df.index.isin(test)].mean(axis=0), columns=['treated']) 
            wide_agg = pd.concat([treated_units, control_units], axis=1)
        if aggregation.lower() == 'sum':
            treated_units = pd.DataFrame(wide_df[wide_df.index.isin(test)].sum(axis=0), columns=['treated']) 
            wide_agg = pd.concat([treated_units, control_units], axis=1)

        if de_mean:
            wag = (wide_agg - wide_agg.mean(axis=0))
            pds = PanelDataset(wag.T, treated_units=['treated'], treated_periods=[TimePeriod(start=start_date) ])
        else:
            pds = PanelDataset(wide_agg.T, treated_units=['treated'], treated_periods=[TimePeriod(start=start_date) ])
    
    return pds 


def results_to_dfs(est: Type[ImpactAnalyzer]
                   , pds: PanelDataset) -> NamedTuple:
    
    """Takes in a PanelExp Model i.e. TBR, SCM, etc. in which run_analysis has already been called and formats results as pd.DataFrames
    that will be used in Dash graphing. 
    
    Args:
        est (ImpactAnalyzer): Takes in a fitted panel_exp model i.e. TBR, SCM, etc.
        pds (PanelDataset): Takes in the Panel Dataset used in fitted model. 

    Returns:
        NamedTuple: NamedTuple that contains result DataFrames. 
    """
    
    from collections import namedtuple
    
    Results = namedtuple('result_dfs', ['dfv1', 'dfv2', 'dfv3'])

    
    # DF for first graph 
    results_v1_df = pd.concat([pd.DataFrame(est.results['times'], columns=['time'])
                            , pd.DataFrame(est.results['y'], columns = ["y_{}".format(unit) for unit in pds.treated_units])
                            , pd.DataFrame(est.results['y_hat'], columns = ["yhat_{}".format(unit) for unit in pds.treated_units])] , axis=1)

    # DF for first graph 
    results_v2_df = pd.concat([pd.DataFrame(est.results['times'], columns=['time'])
                            , pd.DataFrame(est.results['y']-est.results['y_hat'], columns = pds.treated_units)] , axis=1)

    # DF for first graph 
    results_v3_df = pd.concat([pd.DataFrame(est.results['times'], columns=['time'])
           , pd.concat([ pd.DataFrame(est.results['y']-est.results['y_hat'])[:-est.panel_data.num_treated_time_periods[0]] , pd.DataFrame(est.results['y']-est.results['y_hat'])[-est.panel_data.num_treated_time_periods[0]:].cumsum() ])
           ] , axis=1)
    
    R = Results(results_v1_df, results_v2_df, results_v3_df)
    
    return R
    
    