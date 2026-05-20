import copy

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from joblib import Parallel, delayed
from tqdm import tqdm

from panel_exp.design.rng import make_generator
from panel_exp.panel_data import PanelDataset, TimePeriod

sns.set_style("darkgrid")


class PowerAnalysis:
    """
    Simulation-based pre-test power analysis.

    **MDE definition:** minimum simulated percent effect such that the
    inference method's interval covers zero on at least ``power`` (default 0.8)
    of sliding train/test windows. This is **not** a closed-form analytic MDE.

    :param panel: Required. A PanelDataset
    :param model: Required. The model to use to construct a synthetic control.
    :param inference: Required. Method used to create confidence intervals.
    :param test_length: Required. The length of the test period.
    :param train_length: Default=None. The length of pre-test data to use.
    :param mx_effect: Default = 0.5. Maximum absolute percent effect to simulate.
    :param n_sample_prc: Default = 1. Fraction of train/test windows to sample.
    :param n_jobs: Default = 1. Parallel jobs.
    :param random_state: Seed for reproducible window subsampling and effects.
    :param alpha: Significance level for intervals (default 0.05 → 95% intervals).
    """

    def __init__(
        self,
        panel,
        model,
        inference,
        test_length,
        power=0.8,
        train_length=None,
        alpha=0.05,
        mx_effect=0.5,
        n_sample_prc=1,
        n_jobs=1,
        ci_version=1,
        random_state=42,
        **kw_args,
    ):
        self.panel = panel
        self.model = model
        self.inference = inference
        self.L = len(panel.times)
        self.test_length = test_length
        self.power = power
        self.train_length = train_length
        self.mx_effect = mx_effect
        self.n_jobs = n_jobs
        self.n_sample_prc = n_sample_prc
        self.alpha = alpha
        self.ci_version = ci_version
        self.random_state = random_state
        self._rng = make_generator(random_state)
        self.kw_args = kw_args



    def train_test_indices_f(self):
        """
        This method returns indices for simulated pre-test and test periods.
        """

        if not self.train_length:
            self.train_length = self.L-self.test_length
            
        assert self.train_length + self.test_length <= self.L, "Train + Test Length must be less or equal to available data points "
        train_test_indices = []

        for i in range(self.L):
            train = [(i + j) % self.L for j in range(self.train_length)]
            test = [
                (i + self.train_length + j) % self.L for j in range(self.test_length)
            ]
            train_test_indices.append([train, test])
    
        return train_test_indices

    def fake_effect(self, mod_pds, effect = 0):
        """
        This method returns a modifed PanelDataset that has a 'fake' effect added it to it.
        """
        mod_fe_pds = copy.deepcopy(mod_pds)

        mask = np.tile(~(mod_pds.times>=mod_pds.times[mod_pds.treated_start_idxs[0]])&(mod_pds.times<=mod_pds.times[mod_pds.treated_end_idxs[0]-1])
                , (mod_fe_pds.wide_data.loc[mod_fe_pds.treated_units].shape[0],1) ) 
        
        mod_fe_pds.wide_data.loc[mod_fe_pds.treated_units] = mod_fe_pds.wide_data.loc[mod_fe_pds.treated_units].where(mask
                                                                    , mod_fe_pds.wide_data.loc[mod_fe_pds.treated_units]+effect.reshape(-1,1)
                                                                    )
        return mod_fe_pds


    def effect_sample(self, percent_effect, value_effect, mod_pds, iteration , true_test = None):
        """
        This method returns the results of the estimated causal effect for a specified fake effect.
        """
        mod_fe_pds = self.fake_effect(mod_pds, value_effect)
        est = self.model(self.inference)

        est.run_analysis(mod_fe_pds )
        
        cum_effect = (est.results['y'] - est.results['y_hat'])[-self.test_length:].sum()
        mean_effect = (est.results['y'] - est.results['y_hat'])[-self.test_length:].mean()
        
        cum_effect_low = (est.results['y'] - est.results['y_lower'])[-self.test_length:].sum()
        cum_effect_high = (est.results['y'] - est.results['y_upper'])[-self.test_length:].sum()

        mean_effect_low = (est.results['y'] - est.results['y_lower'])[-self.test_length:].mean()
        mean_effect_high = (est.results['y'] - est.results['y_upper'])[-self.test_length:].mean()
        
        mean_ss = mean_effect_low <= 0 <= mean_effect_high
        cum_ss = cum_effect_low <= 0 <= cum_effect_high
        bias = (est.results['y'] - est.results['y_hat'])[:-self.test_length].mean()
        y_actuals = est.results['y'][-self.test_length:].sum()

        if true_test:
            est.model.predict()

        return [iteration, round(percent_effect,2) , bias, value_effect.mean(), (value_effect * self.test_length).sum() , cum_effect_low, cum_effect, cum_effect_high, mean_effect_low, mean_effect, mean_effect_high, mean_ss, cum_ss, y_actuals]


    def analysis(self):
        """
        Method that executes all steps in analysis. 
        :param: ci_version. Default = 1. Version of confidence interval to use.
        """


        self.tt = self.train_test_indices_f()
        output = []
        iteration = 0 

        if len(self.panel.treated_units) == 1:
            self.mean_value = self.panel.wide_data.loc[self.panel.treated_units].mean().mean()
        elif len(self.panel.treated_units) > 1:
            self.mean_value = self.panel.wide_data.loc[self.panel.treated_units].mean(axis=1).values

        if self.ci_version == 1:
            percent_effect = np.concatenate( [ np.linspace(-self.mx_effect, 0 , 25), np.linspace(0, self.mx_effect , 25)[1:]])
        
        if self.ci_version == 2:
            percent_effect = np.zeros(1)
        
        self.output_df = pd.DataFrame([], columns=['iteration', 'prc_effect', 'bias', 't_effect', 't_cum_effect',  'cum_effect_low', 'cum_effect', 'cum_effect_high', 'mean_effect_low', 'mean_effect', 'mean_effect_high', 'mean_ss', 'cum_ss'])
        
        n_keep = max(1, int(len(self.tt) * self.n_sample_prc))
        idx = self._rng.choice(len(self.tt), size=n_keep, replace=False)
        self.tt = [self.tt[i] for i in sorted(idx)]

        for k in tqdm(self.tt):
            train = k[0]
            test = k[1]
            mod_df = pd.concat([self.panel.wide_data.T.iloc[train], self.panel.wide_data.T.iloc[test]]).reset_index(drop=True)
            mod_pds = PanelDataset(mod_df.T, [TimePeriod(start=self.train_length) for _ in range(len(self.panel.treated_units))], self.panel.treated_units)
            
            output = Parallel(n_jobs=self.n_jobs)(delayed(self.effect_sample)(effect, effect*self.mean_value, mod_pds, iteration) for effect in percent_effect)
            # print(output.columns)
            iteration += 1
            self.output_df = pd.concat([self.output_df, pd.DataFrame(output, columns=['iteration','prc_effect','bias', 't_effect', 't_cum_effect', 'cum_effect_low', 'cum_effect', 'cum_effect_high', 'mean_effect_low', 'mean_effect', 'mean_effect_high', 'mean_ss', 'cum_ss','y_actuals'])])


        prc = (1-pd.pivot_table(self.output_df, index='prc_effect', columns='iteration', values='mean_ss').mean(axis=1))>=self.power
        cum_effect = (1-pd.pivot_table(self.output_df, index='t_cum_effect', columns='iteration', values='mean_ss').mean(axis=1))>=self.power
        self.n_simulations = len(self.tt * len(percent_effect))

                    
        if self.ci_version == 1: 
            
            self.mde_kpi_cumulative = cum_effect.index[min(loc for loc, val in enumerate(cum_effect.values) if not val)-1]
            self.mde_percent = prc.index[min(loc for loc, val in enumerate(prc.values) if not val)-1] 

            # Calculate Standard Error and CI for MDE in CI Version 1
            se_cum_effect = self.output_df[self.output_df.prc_effect == self.mde_percent].cum_effect.std() / np.sqrt(len(self.output_df[self.output_df.prc_effect == self.mde_percent]))
            ci_lower = self.mde_kpi_cumulative - 1.96 * se_cum_effect
            ci_upper = self.mde_kpi_cumulative + 1.96 * se_cum_effect
            self.error_rate = (ci_upper - ci_lower) / 2
                    
        if self.ci_version == 2:
            self.mde_kpi_cumulative =  1.96*(self.output_df[self.output_df.prc_effect == 0].cum_effect.std())
            self.output_df['cum_effect'] = self.output_df['cum_effect'].abs()
            # np.percentile(self.output_df[self.output_df.prc_effect == 0].cum_effect,99) 
            self.mde_percent = round(self.mde_kpi_cumulative /np.mean(self.output_df[self.output_df.prc_effect == 0].y_actuals),2)

            # Calculate Standard Error and CI for MDE in CI Version 2
            se_cum_effect_v2 = self.output_df[self.output_df.prc_effect == 0].cum_effect.std() / np.sqrt(len(self.output_df[self.output_df.prc_effect == 0]))
            ci_lower_v2 = self.mde_kpi_cumulative - 1.96 * se_cum_effect_v2
            ci_upper_v2 = self.mde_kpi_cumulative + 1.96 * se_cum_effect_v2
            self.error_rate = (ci_upper_v2 - ci_lower_v2) / 2



    def run_analysis(self):
        """
        Method to run complete power analysis. 
        """
        self.analysis()

    def plot_power_curve(self, x_axis='percent_effect' ):
        """
        Method to plot power curves.
        
        :param: x_axis. Default = percent effect. Expreses effect size as percent. Can be: percent_effect, total_effect, weekly_effect
        """
        # options fo x axis
        assert x_axis in ['percent_effect', 'total_effect', 'weekly_effect']

        # map readable input to abbreviated column name 
        i = ['percent_effect', 'total_effect', 'weekly_effect'].index(x_axis)
        x = ['prc_effect', 't_cum_effect', 't_effect'][i]

        es = (1-pd.pivot_table(self.output_df, index=x, columns='iteration', values='mean_ss').mean(axis=1))>=self.power

        if max(loc for loc, val in enumerate(es.values) if not val)+1 == es.values.shape[0]:
            raise ValueError("No MDE Found. Try Larger Effects and/or Longer Training Period")

        _low = es.index[max(loc for loc, val in enumerate(es.values) if not val)+1]
        high = es.index[min(loc for loc, val in enumerate(es.values) if not val)-1]

        plt.plot(1-pd.pivot_table(self.output_df, index=x, columns='iteration', values='mean_ss').mean(axis=1))
        plt.axhline(self.power)
        # plt.axvline(low, label='Lower MDE: %s' % low)
        # plt.axvline(high, label='Upper MDE: %s' % high)
        plt.title("Power Curve Simulation @ %s" % self.power, fontsize=15,   pad=15)
        plt.suptitle("Test Length: %s days \n MDE: %s" % (self.test_length, np.abs(high)),   y=.05 )

        # plt.axvline(np.percentile(self.output_df[self.output_df.prc_effect == 0].cum_effect, 99), color='red', label='Lower MDE: %s' % low)
        # plt.axvline(np.percentile(self.output_df[self.output_df.prc_effect == 0].cum_effect, 1), color='red', label='Upper MDE: %s' % high)

    def summary(self):
        info_1 = pd.DataFrame({"Parameters": [self.model.__name__, self.inference, self.test_length, self.n_simulations,  'Statistics' , self.mde_percent, self.mde_kpi_cumulative , self.power, (1-self.output_df[self.output_df.prc_effect==0].cum_ss.mean())*2, self.error_rate] }
              , index=['Model', 'Inference', 'Test Length', 'Number of Simulations', ' ', 'MDE Percent', 'MDE KPI', 'Power', 'Type 1 Error Rate', 'Error Rate (CI)']
              )
        
        # from IPython.display import display, HTML

        # display(HTML(info_1.to_html()))

        return info_1


