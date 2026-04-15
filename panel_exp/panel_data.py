"""

Core: panel_data
=================

A module for storing panel data in a wide format and providing methods for accessing and manipulating the data

"""


from __future__ import annotations
from functools import reduce
import operator
import numpy as np
import pandas as pd
import scipy.stats as st
from dataclasses import dataclass

from matplotlib import pyplot as plt
from typing import Dict, List, NewType, Optional, Tuple, Union
from abc import (
    ABC,
    abstractmethod,
)

import seaborn as sns
sns.set_style('darkgrid')

# datatypes for panel data times and units
Timestamp = NewType(
    "Timestamp", Union[np.datetime64, int, pd._libs.tslibs.timestamps.Timestamp]
)
timestamp_types = (np.datetime64, int, pd._libs.tslibs.timestamps.Timestamp)
Unit = NewType("Unit", Union[str, int])
unit_types = (str, int)


@dataclass
class TimePeriod:
    """
    A class for storing the start treatement and end treatment timestamps.

    :param start: Optional[Timestamp] = None
    :param end: Optional[Timestamp] = None

    .. code-block:: python

        from panel_exp import panel_data
        panel_data.TimePeriod(2012, 2015)

        # if multiple units are treated and not aggregated, you need to pass a TimePeriod object for each one. In the same order you pass units.
        treated_periods = [panel_data.TimePeriod(2012)]

    """
    start: Optional[Timestamp] = None
    end: Optional[Timestamp] = None


@dataclass
class PanelDataset:
    """
    A class for storing panel data in a wide format and providing methods for accessing and manipulating the data.
    
    .. code-block:: python
        
        from panel_exp import panel_data

        # load data
        d1 = pd.read_csv("kansas_parsed.csv")
        d1.columns = ['un', 'value', 'treated', 'fips', 'time_unit', 'unit']

        # transform long data format into wide data of n units X t time periods.
        wide = pd.pivot_table(d1, index='time_unit', columns='unit', values='value', aggfunc=sum, fill_value=0).T

        # list of treated units
        treated_units = ['Kansas']

        # list of TimePeriod instances that contain treatment start and end timestamps for each treated unit.
        treated_periods = [panel_data.TimePeriod(2012)]

        # initialize class
        pds = panel_data.PanelDataset(wide, treated_periods, treated_units)
        
        pds.summarize()
    
    Parameters
    ----------
    :param : wide_data
        Required. A n_units x n_time dataframe
    :param : treated_periods 
        Optional[List[TimePeriod]] = None
    :param : treated_units
        Optional[List[TimePeriod]] = None
    
    Attributes
    ----------
    wide_data : pd.DataFrame
        A n_units x n_time dataframe.
    treated_periods : Optional[List[TimePeriod]], optional
        List of TimePeriod instances that contain treatment start and end timestamps for each treated unit, by default None.
    treated_units : Optional[List[Unit]], optional
        List of treated units, by default None.

    Methods
    -------
    __post_init__()
        Validates and processes the treated periods and units.
    unit_index(unit: str) -> int
        Returns the index of a unit in the wide dataframe.
    treatment_start_index(unit: str) -> int
        Returns the index for the start time of treatment for a given unit.
    is_single_treatment() -> bool
        Returns true if there is one treated unit, false otherwise.
    num_timepoints() -> int
        Returns the number of timepoints in the panel dataset.
    num_units() -> int
        Returns the number of units in the panel dataset.
    num_control_units() -> int
        Returns the number of control units in the panel dataset.
    units() -> np.ndarray
        Returns an array of all units.
    control_units() -> list
        Returns a list of control units.
    times() -> np.ndarray
        Returns an array of all time periods.
    num_treated_time_periods() -> np.ndarray
        Returns an array containing the treated time length of treated units.
    get_control_indices() -> np.ndarray
        Returns an array of all control indices.
    untreated_mask() -> pd.DataFrame
        Returns a DataFrame in which the treated units during the treated times are masked with NaN.
    treated_series() -> pd.Series
        Returns a series of the treated units over time with the option to aggregate.
    drop_units() -> PanelDataset
        Returns a new PanelDataset with the specified units dropped.
    """

    # wide_data is an n_units x n_time dataframe
    wide_data: pd.DataFrame

    # treated times in original format
    treated_periods: Optional[List[TimePeriod]] = None
    # treated units in original format
    treated_units: Optional[List[Unit]] = None
    
    # optional covariates
    # currently ignored
    #covariates: Optional[np.ndarray] = None

    # optional auxillary information of the
    # relative population of each unit
    #populations: Optional[np.ndarray] = None

    def __post_init__(self):
        """
        Validates and processes the treated periods and units.
        """
        # add value error if treated times passed and not treated units
        if (self.treated_periods is not None) and (self.treated_units is None):
            raise ValueError("If passing treated periods you must pass treated units")
        if (self.treated_periods is not None) and (
            not isinstance(self.treated_periods, List)
        ):
            self.treated_periods = [self.treated_periods]
        if (self.treated_units is not None) and (
            not isinstance(self.treated_units, List)
        ):
            self.treated_units = [self.treated_units]

        if (self.treated_periods is not None) and (self.treated_units is not None):
            if len(self.treated_periods) != len(self.treated_units):
                raise ValueError(
                    "Length of treated_periods must be equal to the length of treated_units."
                    + f"Found {len(self.treated_periods)} and {len(self.treated_units)}"
                )
            
            if len(set([t.start for t in self.treated_periods])) > 1:
                raise ValueError("Staggered Adoption not currently supported") # add warning for stagered adoption

        if self.treated_periods is not None:
            # set the treated_idxs and treated_unit_idxs using wide_df and
            # treated_units and treated_times
            self.treated_start_idxs: List[int] = [
                self.wide_data.columns.get_loc(period.start)
                for period in self.treated_periods
            ]
            self.treated_end_idxs: List[int] = [
                self.wide_data.columns.get_loc(period.end)
                if period.end is not None
                else self.wide_data.columns.shape[0]-1 # I think we want to change this to self.wide_data.columns.shape[0] - 1, so it doesn't through out of bounds error
                for period in self.treated_periods
            ]

            self.test_start =  np.unique([t.start for t in self.treated_periods])[0]
            if self.treated_periods[0].end is None:
                self.test_end = self.wide_data.columns.values[-1]
            else:
                self.test_end = self.treated_periods[0].end

            self.time_start = self.wide_data.columns.values[0]
            self.time_end = self.wide_data.columns.values[-1]
            self.post_treated_periods = self.wide_data.columns.get_loc(self.time_end) - self.wide_data.columns.get_loc(self.test_end)

        if self.treated_units is not None:
            self.treated_unit_idxs: List[int] = [
                self.wide_data.index.get_loc(unit) for unit in self.treated_units
            ]

        self.agg_instructions = None



    def unit_index(self, unit: str) -> int:
        """
        Returns the index of a unit in the wide dataframe.

        Parameters
        ----------
        unit : str
            The unit to find the index for.

        Returns
        -------
        int
            The index of the unit.
        """
        return self.wide_data.index.get_loc(unit)

    def treatment_start_index(self, unit: str) -> int:
        """
        Returns the index for the start time of treatment for a given unit.

        Parameters
        ----------
        unit : str
            The unit to find the treatment start index for.

        Returns
        -------
        int
            The index for the start time of treatment.
        """
        if self.treated_units is None:
            raise Exception("No treated units are currently set")
        unit_idx = self.treated_units.index(unit)
        return self.treated_start_idxs[unit_idx]

    @property
    def is_single_treatment(self) -> bool:
        """
        Returns true if there is one treated unit, false otherwise.

        Returns
        -------
        bool
            True if there is one treated unit, false otherwise.
        """
        # maybe remove exception. IMO if there are 0 treatments we shouldn't raise error just return false?
        if self.treated_units is None:
            raise Exception("No treated units are currently set")
        return len(self.treated_units) == 1

    @property
    def num_timepoints(self) -> int:
        """
        Returns the number of timepoints in the panel dataset.

        Returns
        -------
        int
            The number of timepoints.
        """
        return self.wide_data.shape[1]

    @property
    def num_units(self) -> int:
        """
        Returns the number of units in the panel dataset.

        Returns
        -------
        int
            The number of units.
        """
        return self.wide_data.shape[0]

    @property
    def num_control_units(self) -> int:
        """
        Returns the number of control units in the panel dataset.

        Returns
        -------
        int
            The number of control units.
        """
        # CB change 10/2/23 to include 0 control units if panel dataset being used for design
        if self.treated_units:
            return self.num_units - len(self.treated_units)
        else:
            return 0

    @property
    def units(self) -> np.ndarray:
        """
        Returns an array of all units.

        Returns
        -------
        np.ndarray
            Array of all units.
        """
        return self.wide_data.index.values

    @property
    def control_units(self) -> list:
        """
        Returns a list of control units.

        Returns
        -------
        list
            List of control units.
        """
        return [unit for unit in self.units if unit not in self.treated_units]

    @property
    def times(self) -> np.ndarray:
        """
        Returns an array of all time periods.

        Returns
        -------
        np.ndarray
            Array of all time periods.
        """
        return self.wide_data.columns.values

    @property
    def num_treated_time_periods(self) -> np.ndarray:
        """
        Returns an array containing the treated time length of treated units.

        Returns
        -------
        np.ndarray
            Array containing the treated time length of treated units.
        """
        return (np.array(self.treated_end_idxs) - np.array(self.treated_start_idxs))+1

    def get_control_indices(self) -> np.ndarray:
        """
        Returns an array of all control indices.

        Returns
        -------
        np.ndarray
            Array of all control indices.
        """
        mask = self.untreated_mask()
        return np.where(mask.notnull().values)[0]

    def untreated_mask(self) -> pd.DataFrame:
        """
        Returns a DataFrame in which the treated units during the treated times are masked with Nan

        Returns
        -------
        pd.DataFrame
            DataFrame in which the treated units during the treated times are masked with Nan
        """ 
        
        # change: cb 10/3/23 changing loop to take len as treated_units is a list
        masked_data = self.wide_data.copy()
        if self.treated_units is not None:
            for i in range(len(self.treated_units)):
                unit_idx = self.treated_unit_idxs[i]
                start_time_idx = self.treated_start_idxs[i]
                end_time_idx = self.treated_end_idxs[i]
                masked_data.iloc[unit_idx, start_time_idx:end_time_idx] = np.nan
        return masked_data

    def treated_series(
        self,
        treated_units: Optional[Union[List[Unit], Unit]] = None, 
        period: str = "full",
        aggregation_fun: Optional[Union(str, Callable)] = None,
    ) -> pd.Series:
        """
        Returns a series of the treated units over time with the option to aggregate.

        Parameters
        ----------
        treated_units : Optional[Union[List[Unit], Unit]], optional
            The units to return the series for. If None, returns the single treated unit if there is only one, otherwise raises an exception, by default None.
        period : str, optional
            The period to return the series for. Can be "full", "pre", or "post", by default "full".
        aggregation_fun : Optional[Union[str, Callable]], optional
            The function to use to aggregate the series. If None, returns the raw series. If a string, must be one of "mean", "median", "sum", "min", "max". If a callable, must take a pandas series and return a single value, by default None.

        Returns
        -------
        pd.Series
            A series of the treated units over time with the option to aggregate.

        Example
        -------
        .. code-block:: python

            d1 = pd.read_csv("kansas_parsed.csv")
            d1.columns = ['un', 'value', 'treated', 'fips', 'time_unit', 'unit']
            wide = pd.pivot_table(d1, index='time_unit', columns='unit', values='value', aggfunc=sum, fill_value=0).T
            treated_units = ['Kansas']
            treated_periods = [panel_data.TimePeriod(2012)]

            p_data.treated_series()
            # p_data.treated_series(["Kansas"], period="full")
            # p_data.treated_series(["Kansas"], period="pre")
            # p_data.treated_series(["Kansas"], period="post")
        """
        # Returns a tuple of the control and test dataframes for a given unit
        if treated_units is None:
            if self.is_single_treatment:
                treated_units = [self.treated_units[0]]
            else:
                raise Exception(
                    "The treated unit must be specified if there are multiple treatments"
                )
        elif not isinstance(treated_units, List):
            treated_units = [treated_units]

        if (
            (len(treated_units) > 1)
            and (period != "full")
            and not np.all(
                np.array(
                    np.diff([self.treatment_start_index(u) for u in treated_units])
                )
                == 0
            )
        ):
            raise Exception("All treatment periods must be the same for treated units")

        # treated_unit_idx = self.unit_index(treated_unit)
        test_df = self.wide_data.loc[treated_units]
        if period == "pre":
            start_time_idx = self.treatment_start_index(treated_units[0])
            test_df = test_df.iloc[:, :start_time_idx]
        elif period == "post":
            start_time_idx = self.treatment_start_index(treated_units[0])
            test_df = test_df.iloc[:, start_time_idx:]
        elif period != "full":
            raise NotImplemented(f"{period} is not a supported time period")
        if (aggregation_fun is not None) and len(treated_units) > 1:
            test_df = test_df.agg(func=aggregation_fun, axis=0)
        return test_df

    def drop_units(self, units: Union[List[Unit], Unit]) -> PanelDataset:
        """
        Returns a new PanelDataset with the specified units dropped.

        Parameters
        ----------
        units : Union[List[Unit], Unit]
            The units to drop.

        Returns
        -------
        PanelDataset
            A new PanelDataset with the specified units dropped.
        """
        df = self.wide_data.drop(units, axis=0)
        #if self.covariates is not None:
        #    raise NotImplemented()
        #if self.populations is not None:
        #    raise NotImplemented()
        return PanelDataset(
            df, treated_periods=self.treated_periods, treated_units=self.treated_units
        )

    def drop_period(self, time_period_drop: Timestamp) -> PanelDataset:
        """
        Returns a new PanelDataset with all the time points between the start and end time in the time_period_drop dropped.

        Parameters
        ----------
        time_period_drop : Timestamp
            The time period to drop.

        Returns
        -------
        PanelDataset
            A new PanelDataset with the specified time dropped.
        """
        df  = self.wide_data.loc[:, time_period_drop.start:time_period_drop.end]

 
        return PanelDataset(
            df, treated_periods=self.treated_periods, treated_units=self.treated_units
        )

    def control_series(
        self,
        treated_units: Optional[Union[List[Union], Unit]] = None,
        period="full",
        aggregation_fun: Optional[Union(str, Callable)] = None,
    ) -> pd.DataFrame:
        """
        Returns a dataframe of the control units over time with the option to aggregate.

        Parameters
        ----------
        treated_units : Optional[Union[List[Unit], Unit]], optional
            The units to return the series for. If None, returns the single treated unit if there is only one, otherwise raises an exception, by default None.
        period : str, optional
            The period to return the series for. Can be "full", "pre", or "post", by default "full".
        aggregation_fun : Optional[Union[str, Callable]], optional
            The function to use to aggregate the series. If None, returns the raw series. If a string, must be one of "mean", "median", "sum", "min", "max". If a callable, must take a pandas series and return a single value, by default None.

        Returns
        -------
        pd.DataFrame
            A pandas dataframe of the control units over time, aggregated if specified.
        """
        if treated_units is None:
            if self.is_single_treatment:
                treated_units = [self.treated_units[0]]
            else:
                raise Exception(
                    "The treated unit must be specified if there are multiple treatments"
                )
        elif not isinstance(treated_units, List):
            treated_units = [treated_units]

        if period != "full" and not np.all(
            np.array(np.diff([self.treatment_start_index(u) for u in treated_units]))
            == 0
        ):
            raise Exception("All treatment periods must be the same for treated units")
        control_df = self.wide_data.drop(treated_units, axis=0)
        if period == "pre":
            start_time_idx = self.treatment_start_index(treated_units[0])
            control_df = control_df.iloc[:, :start_time_idx]
        elif period == "post":
            start_time_idx = self.treatment_start_index(treated_units[0])
            control_df = control_df.iloc[:, start_time_idx:]
        elif period != "full":
            raise NotImplemented(f"{period} is not a supported time period")

        # Aggregate if necessary
        if (aggregation_fun is not None) and len(treated_units) > 1:
            control_df = control_df.agg(func=aggregation_fun, axis=0)

        return control_df

    def split_control_test_units(
        self,
        treated_units: Optional[Union[List[Unit], Unit]] = None,
        period="pre",
        treatment_aggregation_fun: Optional[Union(str, Callable)] = None,
        control_aggregation_fun: Optional[Union(str, Callable)] = None,
    ) -> Tuple[pd.DataFrame, Union[pd.DataFrame, pd.Series]]:
        """
        Returns a tuple of the control and test dataframes for a set of given test units.

        Parameters
        ----------
        treated_units : Optional[Union[List[Unit], Unit]], optional
            The units to return the series for. If None, returns the single treated unit if there is only one, otherwise raises an exception, by default None.
        period : str, optional
            The period to return the series for. Can be "full", "pre", or "post", by default "pre".
        treatment_aggregation_fun : Optional[Union[str, Callable]], optional
            The function to use to aggregate the series. If None, returns the raw series. If a string, must be one of "mean", "median", "sum", "min", "max". If a callable, must take a pandas series and return a single value, by default None.
        control_aggregation_fun : Optional[Union[str, Callable]], optional
            The function to use to aggregate the series. If None, returns the raw series. If a string, must be one of "mean", "median", "sum", "min", "max". If a callable, must take a pandas series and return a single value, by default None.

        Returns
        -------
        tuple
            A tuple of the control and test dataframes for a given unit, aggregated if specified.
        """
        # Returns a tuple of the control and test dataframes for a given unit
        if treated_units is None:
            if self.is_single_treatment:
                treated_units = [self.treated_units[0]]
            else:
                raise Exception(
                    "The treated unit must be specified if there are multiple treatments"
                )
        control_df = self.control_series(
            treated_units=treated_units,
            period=period,
            aggregation_fun=control_aggregation_fun,
        )
        test_df = self.treated_series(
            treated_units=treated_units,
            period=period,
            aggregation_fun=treatment_aggregation_fun,
        )
        return control_df, test_df

    def assign_treatment(
        self,
        treated_units: Union[List[Unit], Unit],
        treatment_periods: Union[List[Timestamp], Timestamp],
    ) -> PanelDataset:
        """
        Returns a new PanelDataset with the specified units assigned to the specified treatment periods to be treated units.

        Parameters
        ----------
        treated_units : Union[List[Unit], Unit]
            The units to assign to treatment.
        treatment_periods : Union[List[Timestamp], Timestamp]
            The periods to assign the units to treatment.

        Returns
        -------
        PanelDataset
            A new PanelDataset with the specified units assigned to treatment.
        """
        #if self.treated_units is not None:
        #    raise NotImplemented(
        #        "Adding assignments to a previously treated dataset is not currently supported"
        #    )
        return PanelDataset(
            self.wide_data,
            treated_periods=treatment_periods,
            treated_units=treated_units,
            #covariates=self.covariates,
            #populations=self.populations,
        )

    def summarize(self) -> str:
        """
        Creates a summary of the panel dataset, giving the total number of time points, units, and treated units and their corresponding treatment periods in a human readable format.
        """
        summary = f"""
        Panel Dataset Summary
        ---------------------
        Number of time points: {self.num_timepoints}
        Number of units: {self.num_units}
        Number of treated units: {len(self.treated_units) if self.treated_units is not None else 0}
        Treated units: {self.treated_units}
        Treated periods: {self.treated_periods}
        """
        return summary

    def plot_line(self, figsize=(17,7), legend=False):
        """
        Plots control and treated units over time.

        Parameters
        ----------
        figsize : tuple, optional
            The size of the figure, by default (17, 7).
        legend : bool, optional
            Whether to display the legend, by default False.

        Returns
        -------
        None
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        

        fig, axs = plt.subplots(1,1,figsize=figsize)
        self.wide_data.T[self.treated_units].plot( ax=axs, color='red', label='Test Unit/s', legend=legend )
        self.wide_data.T[self.control_units].plot( ax=axs, color='blue', alpha=.2 , label="Control Unit/s", legend=legend)
        axs.axvline(self.treated_periods[0].start, label="Treatment Start Time", color='black', linestyle='dashed')
        if self.treated_periods[0].end is not None:
            axs.axvline(self.treated_periods[0].end, label="Treatment End Time", color='black', linestyle='dashed')
        

        test_path = mpatches.Patch(color='red', label='Test Unit/s')
        control_path = mpatches.Patch(color='blue', alpha=.2 , label="Control Unit/s")
        start_end_path = mpatches.Patch(color='black', linestyle='dashed',  label="Start/End")
        plt.legend(handles=[test_path, control_path, start_end_path])
        axs.set_title("Control and Test Units OverTime", fontsize=15)
        
    def plot_scatter(self, agg_func = 'sum', figsize=(17,7), legend=False):
        """
        Scatter plots control and treated units.

        Parameters
        ----------
        figsize : tuple, optional
            The size of the figure, by default (17, 7).
        legend : bool, optional
            Whether to display the legend, by default False.

        Returns
        -------
        None
        """
        assert agg_func in ['sum', 'mean'], "agg_func must be either 'sum' or 'mean'"
        
        import matplotlib.pyplot as plt
        
        if agg_func == 'sum':
            pre_test_control = self.wide_data.T[self.control_units][:self.treated_start_idxs[0]].sum(axis=1)
            pre_test_treated = self.wide_data.T[self.treated_units][:self.treated_start_idxs[0]].sum(axis=1)
            plt.scatter(pre_test_control, pre_test_treated, color='blue', alpha=.2, label='Pre Treatment')
            
            post_test_control = self.wide_data.T[self.control_units][self.treated_start_idxs[0]:].sum(axis=1)
            post_test_treated = self.wide_data.T[self.treated_units][self.treated_start_idxs[0]:].sum(axis=1)
            plt.scatter(post_test_control, post_test_treated, color='red', alpha=.3, label='Post Treatment')
            plt.xlabel("Control Units")
            plt.ylabel("Treated Units")
            plt.legend()
            
        if agg_func == 'mean':
            pre_test_control = self.wide_data.T[self.control_units][:self.treated_start_idxs[0]].mean(axis=1)
            pre_test_treated = self.wide_data.T[self.treated_units][:self.treated_start_idxs[0]].mean(axis=1)
            plt.scatter(pre_test_control, pre_test_treated, color='blue', alpha=.2, label='Pre Treatment')
            
            post_test_control = self.wide_data.T[self.control_units][self.treated_start_idxs[0]:].mean(axis=1)
            post_test_treated = self.wide_data.T[self.treated_units][self.treated_start_idxs[0]:].mean(axis=1)
            plt.scatter(post_test_control, post_test_treated, color='red', alpha=.3, label='Post Treatment')
            plt.xlabel("Control Units")
            plt.ylabel("Treated Units")
            plt.legend()
            
        # TBD Implement Pair Plot
        '''
        if agg_func == 'none':
            pre_test_control = self.wide_data.T[self.control_units][:self.treated_start_idxs[0]] 
            pre_test_treated = self.wide_data.T[self.treated_units][:self.treated_start_idxs[0]] 
            plt.scatter(pre_test_control, pre_test_treated, color='blue', alpha=.2, label='Pre Treatment')
            
            post_test_control = self.wide_data.T[self.control_units][self.treated_start_idxs[0]:] 
            post_test_treated = self.wide_data.T[self.treated_units][self.treated_start_idxs[0]:] 
            plt.scatter(post_test_control, post_test_treated, color='red', alpha=.3, label='Post Treatment')
            plt.xlabel("Control Units")
            plt.ylabel("Treated Units")
            plt.legend()
        '''
        plt.title("Scatter Plot of Control and Treated Units")
        


    def __str__(self) -> str:
        return self.summarize()

    def __repr__(self) -> str:
        return self.summarize()

    @property
    def long_data(self) -> pd.DataFrame:
        """
        :returns: a long dataframe of the data
        """
        d = self.wide_data.melt(ignore_index=False).reset_index()
        d.columns = ['unit', 'time_unit', 'value']
        return d


def long_df_to_paneldataset(
    df: pd.DataFrame,
    time_column: str,
    unit_column: str,
    value_column: str,
    treated_units: Optional[Union[List[Unit], Unit]] = None,
    treated_start_times: Optional[Union[List[Timestamp], Timestamp]] = None,
    treated_end_times: Optional[Union[List[Timestamp], Timestamp]] = None,
) -> PanelDataset:
    """
    Takes a long dataframe and returns a PanelDataset.

    :param df {pd.DataFrame}. Long dataframe
    :param time_column {str}. Column to use as index
    :param unit_column {str}. Column to use as wide columns
    :param value_column {str}. Column to use as values
    :param treated_units {Union[List[int], int]}. Indexes of treated unit
    :param treated_start_times {Union[List[Timestamp], Timestamp]}. Start times of treatment
    :param treated_end_times {Optional[Union[List[Timestamp], Timestamp]]}. End times of treatment


    .. code-block:: python

        long_df = pd.read_csv('kansas_parsed.csv')
        long_df.columns = ['un', 'value', 'treated', 'fips', 'time_unit', 'unit']
        panel_data = long_df_to_paneldataset(long_df, "time_unit", "unit", "value", ["Kansas"], 2012)

    """
    # wide data should be a dataframe with units as rows and timepoints as columns
    df = df.set_index(unit_column)
    df = df.pivot(columns=time_column, values=value_column)
    # cast to list if single unit
    if (treated_units is not None) and isinstance(treated_units, unit_types):
        treated_units = [treated_units]
    if (treated_start_times is not None) and isinstance(
        treated_start_times, timestamp_types
    ):
        treated_start_times = [treated_start_times]

    if treated_end_times is not None:
        if isinstance(treated_end_times, timestamp_types):
            treated_end_times = [treated_end_times]
        assert (
            (len(treated_units) == len(treated_start_times) == len(treated_end_times)),
            "The number of treated units, start times, and end times must be equal",
        )
        treated_periods = [
            TimePeriod(start, end)
            for start, end in zip(treated_start_times, treated_end_times)
        ]
    elif treated_start_times is not None:
        assert (
            (len(treated_units) == len(treated_start_times)),
            "The number of treated units and start times must be equal",
        )
        treated_periods = [TimePeriod(start) for start in treated_start_times]
    else:
        treated_periods = None

    return PanelDataset(
        wide_data=df,
        treated_periods=treated_periods,
        treated_units=treated_units,
    )
