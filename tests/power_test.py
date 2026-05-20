

import numpy as np
import pandas as pd
import sys 
sys.path.insert(0, '..')

#from panel_exp.inference import conformal
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.methods.tbr import TBRRidge
from panel_exp.design import power


def test_power_train_test():
	long_df = pd.read_csv('tests/fixtures/power_geo.csv')
	long_df = long_df[long_df.time < 91]
	wide_df = pd.pivot_table(long_df, index='location', columns='time', values='Y')
	pds = PanelDataset(wide_df  )

	control_units = pd.DataFrame(wide_df.loc[[unit for unit in pds.units if unit not in ['chicago', 'cincinnati', 'houston', 'portland', 'honolulu']]] ).T
	treated_units = pd.DataFrame(wide_df.loc[['chicago', 'cincinnati', 'houston', 'portland']].mean(axis=0), columns=['treated'])
	wide_agg = pd.concat([treated_units, control_units], axis=1)

	L = len(wide_df.columns)
	test_length = 7

	panel_data = PanelDataset(wide_agg.T, treated_units=['treated'], treated_periods=[TimePeriod(start=L - test_length)])



	# this test checks that train tests indices are also in consecutive order, except once in which the 
	# indices roll over i.e. if there is 90 data points as some point the train or test indices 
	# will look like [87,88,89,0,1,2]

	# test with specific train_length
	pa = power.PowerAnalysis(panel_data
                         , TBRRidge
                         , 'Kfold'
                         , test_length
                         , train_length=5
                         , mx_effect=.25 
                         , n_jobs=10)

	indices = pa.train_test_indices_f()
	matrix = []
	for window in indices:
	    matrix.append(list(window[0]) + list(window[1]))

	m = np.array(matrix)

	assert (pd.DataFrame(m<np.roll(m, 1, axis=1))).sum(axis=1).sum() == pa.L, "train_test_indices_f is failing unit test!"

	# check fake effect
	indices = pa.train_test_indices_f()
	train = indices[0][0]
	test = indices[0][1]
	mod_df = pd.concat([pa.panel.wide_data.T.iloc[train], pa.panel.wide_data.T.iloc[test]]).reset_index(drop=True)
	mod_pds = PanelDataset(mod_df.T, [TimePeriod(start=pa.train_length ) for _ in range(len(pa.panel.treated_units))], pa.panel.treated_units)
	pa.mean_value = pa.panel.wide_data.loc[pa.panel.treated_units].mean().mean()
	test_df = pa.fake_effect(mod_pds, .3*pa.mean_value)
	assert np.isclose((test_df.wide_data - mod_pds.wide_data).sum().sum() , .3*pa.mean_value * pa.test_length), "Fake Effect Failed Unit Test"


	# test with default train length
	pa = power.PowerAnalysis(panel_data
                         , TBRRidge
                         , 'Kfold'
                         , test_length
                         , mx_effect=.25 
                         , n_jobs=10)

	indices = pa.train_test_indices_f()
	matrix = []
	for window in indices:
	    matrix.append(list(window[0]) + list(window[1]))

	m = np.array(matrix)

	assert (pd.DataFrame(m<np.roll(m, 1, axis=1))).sum(axis=1).sum() == pa.L, "train_test_indices_f is failing unit test!"

		# check fake effect
	indices = pa.train_test_indices_f()
	train = indices[0][0]
	test = indices[0][1]
	mod_df = pd.concat([pa.panel.wide_data.T.iloc[train], pa.panel.wide_data.T.iloc[test]]).reset_index(drop=True)
	mod_pds = PanelDataset(mod_df.T, [TimePeriod(start=pa.train_length ) for _ in range(len(pa.panel.treated_units))], pa.panel.treated_units)
	pa.mean_value = pa.panel.wide_data.loc[pa.panel.treated_units].mean().mean()
	test_df = pa.fake_effect(mod_pds, .3*pa.mean_value)
	assert np.isclose((test_df.wide_data - mod_pds.wide_data).sum().sum() , .3*pa.mean_value * pa.test_length), "Fake Effect Failed Unit Test"


