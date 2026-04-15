"""
Inference: Conformal
====================

Implementations of conformal inference for panel estimators.

Summary of recent changes
-------------------------
1. Removed nested inference when fitting the inner estimator. The conformal
   routine now strips inference-related kwargs before constructing the model
   so the base estimator is fit without recursively triggering inference.

2. Simplified the cross_conformal_single interface by removing unused
   inference kwargs and tightening the function signatures.

3. Replaced the previous circular residual permutation (np.roll based) with
   a simpler calibration using pre-treatment residual magnitudes. The test
   statistic now compares the treated-period residual against the empirical
   distribution of pre-period residuals.

4. Added helper `_strip_inference_kwargs` to ensure parameters like
   `inference`, `alpha`, `nulls`, and other inference-layer settings are not
   passed into the inner estimator fit.

5. Minor numerical stability improvements:
   - explicit float conversion for p-values
   - safer residual handling via numpy arrays

These changes significantly reduce the risk of inflated conformal confidence
intervals caused by nested inference and unstable residual permutations.
"""

    
import numpy as np
import pandas as pd
from panel_exp.panel_data import PanelDataset, TimePeriod

def _strip_inference_kwargs(kwargs):
    """Remove inference-layer kwargs before fitting the inner base estimator."""
    blocked = {
        'inference',
        'alpha',
        'nulls',
        'k',
        'debias_flag',
        'block_scheme',
        'n_jobs',
        'random_state',
        'show_progress',
        'plot_1',
        'plot_2',
        'use_rmspe_filter',
        'max_pre_rmspe_multiple',
        'return_stats',
    }
    return {k: v for k, v in kwargs.items() if k not in blocked}

def cross_conformal_single(df, model, unit, start, end, alpha, nulls):
    """Implementation of conformal inference for panel data for single time period.
    
    :param df: 
        DataFrame
    :param model: 
        Model to be used for estimation
    :param unit: 
        unit to be tested
    :param start: 
        start time period
    :param end: 
        end time period
    :param alpha: 
        alpha probability 0-1.
    :param nulls: 
        list of null effects to test
    :param inference_kwargs: 
        additional arguments for inference
    """
    
    def aug_pds(df, null, unit, start, period):
        '''Alters the PanelData to include the fake effect for a specific unit and a specific time period.
        
        :param df: 
            DataFrame
        :param null: 
            null effect to be tested
        ;param unit: 
            unit to be tested
        :param start: 
            start time period
        :param period: 
            time period to be tested
        '''
        pre_full = df.T[df.T.index<start].T
        post_full_single = df.T[df.T.index==period].T
        post_full_single.loc[unit]-=null

        aug_df = pd.concat([pre_full , post_full_single], axis=1)

        aug_pds = PanelDataset(aug_df.copy(), [TimePeriod(period, period)], [unit])

        return aug_pds


    def p_val_single(model, aug_pds, start):
        '''Calculates the p-value for a single time period, unit and simulated effect. 
        
        :param model: 
            Model to be used for estimation
        :param aug_pds: 
            augmented panel dataset
        :param start: 
            start time period
        :param inference_kwargs: 
            additional arguments for inference
        '''

        
        try:
            model.run_analysis(aug_pds)
        except (AttributeError, TypeError, ValueError):
            return np.nan

        if model.results.get('y') is None or model.results.get('y_hat') is None:
            return np.nan
        residuals = np.asarray(model.results['y'] - model.results['y_hat'], dtype=float)

        pre_mask = np.asarray(aug_pds.times < start)
        test_mask = np.asarray((aug_pds.times >= start) & (aug_pds.times <= start))

        pre_residuals = residuals[pre_mask]
        test_residuals = residuals[test_mask]

        if test_residuals.size == 0:
            return np.nan

        if pre_residuals.size == 0:
            statistics = np.abs(test_residuals)
        else:
            block_permutations = np.concatenate([
                np.abs(test_residuals),
                np.abs(pre_residuals)
            ])
            statistics = np.asarray(block_permutations, dtype=float)

        p_val = float(np.mean(statistics >= statistics[0]))

        return p_val
    
    def test_statistic(u_hat, q=1, axis=0):
        '''Calculates the test statistic for a given set of residuals
        
        :param u_hat: 
            residuals
        '''
        return (np.abs(u_hat) ** q).mean(axis=axis) ** (1/q)
    
    

    temp_df = df.copy()
    
    upper = []
    lower = []
    
    t = temp_df.columns.copy()

    # loop through each treated time period
    for period in t[(t>=start)&(t<=end)]:

        pvl = []
        for null in nulls:

            apds = aug_pds(temp_df, null, unit, start, period)
            p_val = p_val_single(model, apds, period)
            pvl.append([null, p_val ])

        pvl = pd.DataFrame(pvl)
        pvl.columns = ['effect', 'p_value']

        pvl = pvl.dropna(subset=['p_value'])
        if pvl.empty:
            lower.append(np.nan)
            upper.append(np.nan)
            continue
    
        lower.append(pvl[pvl.p_value>=alpha].effect.min())
        upper.append(pvl[pvl.p_value>=alpha].effect.max())
            
    # this needs to be fixed when time series end is longer than treatment period. 
    return np.concatenate([np.full(temp_df.shape[1]-len(lower), np.nan), lower]), np.concatenate([np.full(temp_df.shape[1]-len(upper), np.nan), upper])
    
    
    
def conformal(panel, model, alpha, nulls, **inference_kwargs):
    '''Implementation of conformal inference for panel data.
    
    The first function here, loops through the treated time periods and calculates the lower and upper bounds for each treated unit.
    
    :param panel: 
        PanelDataset
    :param model: 
        Model to be used for estimation
    :param alpha: 
        alpha probability 0-1. 
    :param nulls: 
        list of null effects to test
    
    '''
    
    lower_nd = np.zeros((panel.num_timepoints, len(panel.treated_units)))
    upper_nd = np.zeros((panel.num_timepoints, len(panel.treated_units)))
    
    model_kwargs = _strip_inference_kwargs(inference_kwargs)
    
    for treated in range(len(panel.treated_units)):


        pds_temp = PanelDataset(panel.wide_data.copy(), panel.treated_periods[treated], panel.treated_units[treated])
        
        if panel.treated_periods[treated].end is None:
            start = panel.treated_periods[treated].start
            end = panel.times[-1]
        else:
            start = panel.treated_periods[treated].start
            end = panel.treated_periods[treated].end
            
        lower, upper = cross_conformal_single(panel.wide_data.copy()
                                     , model(full_model=True, **model_kwargs)
                                     , panel.treated_units[treated]
                                     , start
                                     , end
                                     , alpha
                                     , nulls
                                     )
        
        lower_nd[:,treated] = lower
        upper_nd[:,treated] = upper

    if len(panel.treated_units) == 1:
        lower_nd = lower_nd.reshape(-1)
        upper_nd = upper_nd.reshape(-1)

    return lower_nd, upper_nd 

        


    
    