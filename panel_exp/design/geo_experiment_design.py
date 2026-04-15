import pandas as pd
import numpy as np
from typing import Optional, List
from abc import ABCMeta
import copy
from panel_exp.design import Rerandomization, greedy_match_markets
from panel_exp.panel_data import long_df_to_paneldataset, PanelDataset
from panel_exp.design.power import PowerAnalysis
from panel_exp.methods.tbr import TBRRidge
import matplotlib.pyplot as plt


class GeoExperimentDesign:
    """
    Class for creating a geo-based experiment by enabling users to select a design method of their choice (from CompleteRandomization, ThinningDesign, greedy_match_markets).
    Supports creating multiple test groups, customizing group assignments through whitelist and blacklist options, and selecting inference methods.
    Outputs the optimal selection of test and control markets, incorporating power analysis and Minimum Detectable Effects (MDE) metrics.

    Parameters:
    ----------
    data : DataFrame
        The panel dataset containing the geos and KPI values.
    n_test_grps : int
        Number of test groups to create.
    treatment_probability : float
        Probability of assigning a unit to the treatment group.
    max_iter : int
        Maximum number of iterations for rerandomization.
    imbalance_metric : str
        Metric to use for measuring imbalance (Default is "l2" but options include - "l2", "l1", "l_inf", "rmse", "mape", "smape", "wmae", "cosine", "hellinger", "variance_ratio").
    base_randomizer_cls : Optional[type]
        The base randomizer class to use for the rerandomization design. Defaults to greedy_match_markets.
    test_whitelist : list
        List of geos that must be included in the test group.
    control_whitelist : list
        List of geos that must be included in the control group.
    test_blacklist : list
        List of geos that must not be included in the test group.
    control_blacklist : list
        List of geos that must not be included in the control group.
    control_test_blacklist : list
        List of geos that must not be included in either test or control group.
    kpi : str
        The key performance indicator (KPI) used for experiment evaluation.
    base_cls : type
        The base class for the randomizer used in rerandomization.
    """

    def __init__(self, 
             panel_data: PanelDataset,  
             n_test_grps: Optional[int] = 1,
             treatment_probability: Optional[float] = None,
             imbalance_metric: Optional[str] = 'l2',
             base_randomizer_cls: Optional[type] = None,
             test_whitelist: Optional[List[str]] = None,
             control_whitelist: Optional[List[str]] = None,
             test_blacklist: Optional[List[str]] = None,
             control_blacklist: Optional[List[str]] = None,
             control_test_blacklist: Optional[List[str]] = None,
             inference: Optional[str] = 'Kfold',
             base_cls: Optional[type] = greedy_match_markets,
             n_sample_prc: float = 0.3,
             ci_version: int = 1,
             train_length: Optional[int] = None,
             test_lengths: List[int] = [28, 56, 91],
             njobs=-1,
             **design_kwargs):
    
        self.panel_data = panel_data
        self.n_test_grps = n_test_grps
        self.treatment_probability = treatment_probability
        self.imbalance_metric = imbalance_metric
        self.base_randomizer_cls = base_randomizer_cls or greedy_match_markets
        self.test_whitelist = test_whitelist or []
        self.control_whitelist = control_whitelist or []
        self.test_blacklist = test_blacklist or []
        self.control_blacklist = control_blacklist or []
        self.control_test_blacklist = control_test_blacklist or []
        self.inference = inference
        self.base_cls = base_cls
        self.n_sample_prc = n_sample_prc
        self.ci_version = ci_version
        self.test_lengths = test_lengths
        self.njobs = njobs
        self.design_kwargs = design_kwargs

        total_days = self.panel_data.wide_data.shape[1]
        max_test_length = max(self.test_lengths)

        # Default to 60% of the total days
        if train_length is None:
            suggested_train_length = int(total_days * 0.6)

            if suggested_train_length + max_test_length <= total_days:
                train_length = suggested_train_length
                print(f"[INFO] Train length set to 60% of total time units: {train_length}")
            elif total_days > max_test_length:
                train_length = total_days - max_test_length
                print(f"[WARNING] 60% train length not feasible. Train length adjusted to {train_length} to accommodate max test length of {max_test_length} time units.")
            else:
                print(f"[ERROR] Max test length ({max_test_length}) exceeds total available time units ({total_days}). Please adjust test_lengths.")
                raise ValueError("Test lengths exceed available data range.")
        else:
            # User provided a train_length: validate it
            if train_length + max_test_length > total_days:
                print(f"[WARNING] Provided train_length {train_length} + max test_length {max_test_length} exceeds available time units {total_days}.")
                if total_days > max_test_length:
                    train_length = total_days - max_test_length
                    print(f"[INFO] Train length adjusted to {train_length} to fit within available time units.")
                else:
                    print(f"[ERROR] Max test length ({max_test_length}) exceeds total available time units ({total_days}). Please adjust test_lengths.")
                    raise ValueError("Test lengths exceed available data range.")

        self.train_length = train_length



    def designs(self, n_test_grps: int = None, 
                treatment_probability: float = None,
                max_iter: Optional[int] = 10000, 
                imbalance_metric: Optional[str] = 'l2', 
                base_randomizer_cls: Optional[ABCMeta] = greedy_match_markets, 
                **design_kwargs) -> Rerandomization:
        """
        Function to create a Rerandomization design with the given parameters.

        Parameters
        ----------
        n_test_grps : int, optional
            Number of test groups.
        treatment_probability : float, optional
            Probability of assigning treatment to a unit.
        max_iter : int, optional
            Maximum number of iterations for rerandomization.
        imbalance_metric : str, optional
            Metric used to measure imbalance between groups ('l2' by default).
        base_randomizer_cls : callable, optional
            The base randomizer class to use (default is greedy_match_markets).
        design_kwargs : additional keyword arguments
            Additional arguments passed to the design class.

        Returns
        -------
        Rerandomization
            A rerandomization design instance.
        """
        if treatment_probability is None:
            treatment_probability = n_test_grps / (n_test_grps + 1)

        else:
            treatment_probability = treatment_probability 
        
        return Rerandomization(
            treatment_probability=treatment_probability, 
            max_iter=max_iter, 
            base_randomizer_cls=base_randomizer_cls, 
            **design_kwargs
        )
    
    def create_design(self) -> 'Rerandomization':
        """
        Creates a rerandomization design object based on the parameters.

        Returns:
        --------
        Rerandomization:
            A rerandomization design object.
        """
        
        return self.designs(n_test_grps=self.n_test_grps, 
                            treatment_probability=self.treatment_probability, 
                            imbalance_metric=self.imbalance_metric, 
                            base_randomizer_cls=self.base_randomizer_cls, 
                            **self.design_kwargs)

    def run_design(self) -> tuple:  # No need to pass data here
        """
        Runs the geo experiment design process by creating test and control groups and performing MDE calculations.

        Returns:
        --------
        tuple:
            Two DataFrames containing the MDE values and percentages.
        """
        print(f'choosen design: {self.base_randomizer_cls.__name__.lower()}')
        if any(keyword in self.base_randomizer_cls.__name__.lower() for keyword in ['greedy_match_markets','thinningdesign','completerandomization','stratifiedrandomization']):
            
            if any(keyword in self.base_randomizer_cls.__name__.lower() for keyword in ['completerandomization','stratifiedrandomization']):
                print("\n⚠️ Whitelist and blacklist constraints are not respected in Complete/Stratified Randomization.")
                print("   If needed, please remove those units from the dataset manually before applying this method.\n")

            design = self.create_design()

            rs_dp_grps = design.assign(panel_data=self.panel_data,
                    treatment_period=None,
                    pre_treatment_period = None,
                    test_whitelist=self.test_whitelist,
                    test_blacklist=self.test_blacklist,
                    control_whitelist=self.control_whitelist,
                    control_blacklist=self.control_blacklist,
                    control_test_blacklist=self.control_test_blacklist,
                    n_test_grps = self.n_test_grps)

            return self._calculate_sensitivity_metrics(rs_dp_grps, 'control')

    def _calculate_sensitivity_metrics(self, rs_dp_grps: dict, control: str) -> tuple:
        """
        Calculates sensitivity metrics for test and control groups identified above.

        Parameters:
        -----------
        rs_dp_grps : dict
            The assigned test and control groups.
        control : str
            The control group identifier.

        Returns:
        --------
        tuple:
            Four DataFrames:
            - MDE percentage values
            - MDE KPI values
            - Summary of power analysis (pa_df)
            - Power curve DataFrames for different test lengths (power_df)
        """
        mde_val_df = pd.DataFrame()
        mde_prc_df = pd.DataFrame()
        power_results_df = pd.DataFrame()

        for grp in [grp for grp in rs_dp_grps.keys() if grp != control]:
            self.pds = copy.deepcopy(self.panel_data)
            self.pds.wide_data = self.pds.wide_data.loc[rs_dp_grps[grp] + rs_dp_grps[control]]
            self.pds.treated_units = rs_dp_grps[grp]

            mde_val, mde_percent, pa_obj1, pa_obj2 = self._run_power_analysis()

            # Dynamically update column names based on test_lengths
            val_columns = [f"{int(length / 7)}wk_val" for length in self.test_lengths] + ['control_dmas', 'test_dmas']
            percent_columns = [f"{int(length / 7)}wk_percent" for length in self.test_lengths] + ['control_dmas', 'test_dmas']
            columns_pa = [f"{int(length / 7)}wk_pa_obj1" for length in self.test_lengths] + \
                [f"{int(length / 7)}wk_pa_obj2" for length in self.test_lengths] + \
                ['control_dmas', 'test_dmas']

            # Add control and test groups to MDE DataFrames
            mde_val.extend([rs_dp_grps[control], rs_dp_grps[grp]])
            mde_percent.extend([rs_dp_grps[control], rs_dp_grps[grp]])

            # Store MDE values and percentages
            mde_val_df = pd.concat([mde_val_df, pd.DataFrame([mde_val], columns=val_columns)], axis=0)
            mde_prc_df = pd.concat([mde_prc_df, pd.DataFrame([mde_percent], columns=percent_columns)], axis=0)

            # Create a list to hold pa_obj1 and pa_obj2 for each test length
            pa_obj1_list = [pa_obj1[length] for length in self.test_lengths]  # pa_obj1 is a dict or list
            pa_obj2_list = [pa_obj2[length] for length in self.test_lengths]  # pa_obj2 is a dict or list

            # Combine pa_obj1 and pa_obj2 with control and test groups
            pa_obj_combined_list = pa_obj1_list + pa_obj2_list + [rs_dp_grps[control], rs_dp_grps[grp]]

            # Create a single DataFrame with both pa_obj1 and pa_obj2
            power_results_df = pd.concat([power_results_df,pd.DataFrame([pa_obj_combined_list], columns=columns_pa)],axis=0)

            # Calculate the test and control percentages
            mde_prc_df['test_prc'] = mde_prc_df['test_dmas'].apply(lambda x: np.round(self.panel_data.wide_data.T[x].sum().sum()*100 / self.panel_data.wide_data.sum().sum(), 2))
            mde_prc_df['control_prc'] = mde_prc_df['control_dmas'].apply(lambda x: np.round(self.panel_data.wide_data.T[x].sum().sum()*100 / self.panel_data.wide_data.sum().sum(), 2))

            mde_val_df['test_prc'] = mde_val_df['test_dmas'].apply(lambda x: np.round(self.panel_data.wide_data.T[x].sum().sum()*100 / self.panel_data.wide_data.sum().sum(), 2))
            mde_val_df['control_prc'] = mde_val_df['control_dmas'].apply(lambda x: np.round(self.panel_data.wide_data.T[x].sum().sum()*100 / self.panel_data.wide_data.sum().sum(), 2))

            power_results_df['test_prc'] = power_results_df['test_dmas'].apply(lambda x: np.round(self.panel_data.wide_data.T[x].sum().sum()*100 / self.panel_data.wide_data.sum().sum(), 2))
            power_results_df['control_prc'] = power_results_df['control_dmas'].apply(lambda x: np.round(self.panel_data.wide_data.T[x].sum().sum()*100 / self.panel_data.wide_data.sum().sum(), 2))

        return (
            mde_prc_df.reset_index(drop=True),
            mde_val_df.reset_index(drop=True),
            power_results_df.reset_index(drop=True)
        )


    # def _run_power_analysis(self) -> tuple:
    #     """
    #     Runs power analysis for the given panel data.

    #     Returns:
    #     --------
    #     tuple:
    #         A list of MDE KPI values and MDE percentage values for different test lengths.
    #     """
    #     mde_val = []
    #     mde_percent = []
    #     pa_df = pd.DataFrame()

    #     # Use self.pds directly, or fall back to self.panel_data if pds isn't set
    #     data = self.pds if hasattr(self, 'pds') and self.pds is not None else self.panel_data

    #     for test_length in self.test_lengths:
    #         control_units = pd.DataFrame(
    #             data.wide_data.loc[
    #                 [unit for unit in data.units if unit not in data.treated_units]
    #             ].sum(axis=0),
    #             columns=['control']
    #         )
    #         treated_units = pd.DataFrame(data.wide_data.loc[data.treated_units].sum(axis=0), columns=['treated'])
    #         wide_agg = pd.concat([treated_units, control_units], axis=1)
    #         pds = PanelDataset(wide_agg.T, treated_units=['treated'])

    #         pa = PowerAnalysis(
    #             pds,
    #             model=TBRRidge,
    #             inference=self.inference,
    #             test_length=test_length,
    #             train_length=self.train_length,
    #             njobs=-1,
    #             n_sample_prc=self.n_sample_prc,
    #             ci_version=self.ci_version
    #         )
    #         pa.run_analysis()

    #         # data for generating power curve
    #         power_curve_df = (1-pd.pivot_table(pa.output_df, index='prc_effect', columns='iteration', values='mean_ss').mean(axis=1)).reset_index()
    #         power_curve_df.columns = ['prc_effect', 'power']
            
    #         # Add the test_length column before concatenating
    #         result_df = pa.summary().T.copy(deep=True)
    #         result_df['test_length'] = test_length
            
    #         # Concatenate the results to pa_df
    #         pa_df = pd.concat([pa_df, result_df], axis=0)
            
    #         # Store MDE KPI and MDE Percent
    #         mde_val.append(result_df['MDE KPI'][0])
    #         mde_percent.append(result_df['MDE Percent'][0])

    #     return mde_val, mde_percent, pa_df


    def _run_power_analysis(self) -> tuple:
        """
        Runs power analysis for the given panel data.

        Returns:
        --------
        tuple:
            - A list of MDE KPI values.
            - A list of MDE percentage values.
            - A dictionary containing summary results (`pa_df`) and power curve DataFrames (`power_curve_df`) for different test lengths.
        """
        mde_val = []
        mde_percent = []
        
        # Create empty dictionaries to store pa_df and power_curve_df for each test length
        pa_df_dict = {}
        power_curve_dict = {}

        # Use self.pds directly, or fall back to self.panel_data if pds isn't set
        data = self.pds if hasattr(self, 'pds') and self.pds is not None else self.panel_data

        for test_length in self.test_lengths:
            control_units = pd.DataFrame(
                data.wide_data.loc[
                    [unit for unit in data.units if unit not in data.treated_units]
                ].sum(axis=0),
                columns=['control']
            )
            treated_units = pd.DataFrame(data.wide_data.loc[data.treated_units].sum(axis=0), columns=['treated'])
            wide_agg = pd.concat([treated_units, control_units], axis=1)
            self.power_pds = PanelDataset(wide_agg.T, treated_units=['treated'])

            pa = PowerAnalysis(
                self.power_pds,
                model=TBRRidge,
                inference=self.inference,
                test_length=test_length,
                train_length=self.train_length,
                njobs=self.njobs,
                n_sample_prc=self.n_sample_prc,
                ci_version=self.ci_version
            )
            pa.run_analysis()

            # Generate power_curve_df
            power_curve_df = (1 - pd.pivot_table(
                pa.output_df,
                index='prc_effect',
                columns='iteration',
                values='mean_ss'
            ).mean(axis=1)).reset_index()

            power_curve_df.columns = ['prc_effect', 'power']

            # Store power_curve_df in dictionary
            power_curve_dict[test_length] = power_curve_df

            # Store summarized results (pa_df)
            result_df = pa.summary().T.copy(deep=True)
            result_df['test_length'] = test_length

            # Save pa_df in dictionary for current test length
            pa_df_dict[test_length] = result_df

            # Store MDE KPI and MDE Percent values
            mde_val.append(result_df['MDE KPI'][0])
            mde_percent.append(result_df['MDE Percent'][0])

        # Return all outputs
        return mde_val, mde_percent, pa_df_dict, power_curve_dict


    def plot_power_curve(pa_df_combined, test_length_label):
        # Extract the corresponding column
        key = f'{test_length_label}_pa_obj2'
        es_og = pa_df_combined.reset_index().loc[0, key]

        # Extract MDE and power
        mde_values = es_og['prc_effect'].reset_index(drop=True)
        power_values = es_og['power'].reset_index(drop=True)

        # Masks for both sides
        neg_mask = (power_values >= 0.8) & (mde_values < 0)
        pos_mask = (power_values >= 0.8) & (mde_values > 0)

        mde_neg = mde_values[neg_mask].iloc[-1] if neg_mask.any() else None  # closest to 0 from left
        mde_pos = mde_values[pos_mask].iloc[0] if pos_mask.any() else None   # closest to 0 from right

        # Plot power curve
        plt.plot(mde_values, power_values, label="Power Curve", color='blue')
        plt.axhline(0.8, color='red', linestyle='--', label="Power = 0.8")

        # Annotate MDEs
        if mde_neg is not None:
            plt.axvline(mde_neg, color='green', linestyle='--', label=f"L_MDE: {np.round(mde_neg, 4)}")

        if mde_pos is not None:
            plt.axvline(mde_pos, color='orange', linestyle='--', label=f"H_MDE: {np.round(mde_pos, 4)}")

        # Subtitle info
        days_map = {'4wk': 28, '8wk': 56, '13wk': 91}
        days = days_map.get(test_length_label, 'N/A')

        mde_text = f"MDEs: {np.round(mde_neg, 4) if mde_neg else 'N/A'}, {np.round(mde_pos, 4) if mde_pos else 'N/A'}"

        plt.title(f"Power Curve Simulation @ 0.8", fontsize=15, pad=15)
        plt.suptitle(f"Test Length: {days} days\n{mde_text}", y=0.92)

        plt.xlabel("Effect Size (MDE)")
        plt.ylabel("Power")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.show()




