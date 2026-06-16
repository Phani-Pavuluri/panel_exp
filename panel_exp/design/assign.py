import copy

import numpy as np
import pandas as pd
from typing import Any, Dict, List, NewType, Optional, Union, Callable
from abc import ABC, abstractmethod
from dtaidistance import dtw
from ..panel_data import PanelDataset, TimePeriod, long_df_to_paneldataset
from .design_metrics import imbalance
from .constraints import (
    prepare_constraint_context,
    validate_assignment_dict,
    balanced_volume_assign,
    bernoulli_complete_assign,
    freeze_assignment,
    freeze_constraint_lists,
)
from .greedy_feasibility import (
    FeasibilityPolicy,
    build_feasibility_metadata,
    compute_greedy_feasibility,
)
from .rng import make_generator

# Base randomizers supported for imbalance computation in Rerandomization
RERANDOMIZATION_IMBALANCE_BASES = frozenset({
    "greedy_match_markets",
    "thinningdesign",
    "balancedrandomization",
    "completerandomization",
    "stratifiedrandomization",
})

# Custom Type for Units
Unit = NewType("Unit", Union[str, int])


class Design(ABC):
    """
    An abstract class defining the interface for experimental design strategies, including methods
    for treatment assignment based on specified control and test constraints.

    Parameters
    ----------
    treatment_probability : float, default=0.5
        Probability of assigning treatment to a unit.
    control_blacklist : List[Unit], optional
        Units that cannot be in the control group.
    test_blacklist : List[Unit], optional
        Units that cannot be in the test group.
    control_test_blacklist : List[Unit], optional
        Units that cannot be in either control or test groups.
    control_whitelist : List[Unit], optional
        Units that can be in the control group.
    test_whitelist : List[Unit], optional
        Units that can be in the test group.
    """

    def __init__(
        self,
        treatment_probability: float = 0.5,
        control_blacklist: Optional[List[Unit]] = None,
        test_blacklist: Optional[List[Unit]] = None,
        control_test_blacklist: Optional[List[Unit]] = None,
        control_whitelist: Optional[List[Unit]] = None,
        test_whitelist: Optional[List[Unit]] = None,
        random_state: Optional[int] = 42,
    ):
        self.treatment_probability = treatment_probability
        self.control_blacklist = control_blacklist or []
        self.test_blacklist = test_blacklist or []
        self.control_test_blacklist = control_test_blacklist or []
        self.control_whitelist = control_whitelist or []
        self.test_whitelist = test_whitelist or []
        self.random_state = random_state
        self._rng = make_generator(random_state)

    def assign(
        self,
        panel_data: PanelDataset,
        control_whitelist: Optional[List[Unit]] = None,
        test_whitelist: Optional[List[Unit]] = None,
        control_blacklist: Optional[List[Unit]] = None,
        test_blacklist: Optional[List[Unit]] = None,
        control_test_blacklist: Optional[List[Unit]] = None,
        treatment_period: Optional[TimePeriod] = None,
        pre_treatment_period: Optional[TimePeriod] = None,
        n_test_grps: Optional[int] = 1
    ) -> PanelDataset:
        """
        Assigns treatments to units in a panel data object based on control and test constraints.

        Parameters
        ----------
        panel_data : PanelDataset
            The panel data object containing the data to which treatment will be assigned.
        control_whitelist : List[Unit], optional
            Units allowed in the control group.
        test_whitelist : List[Unit], optional
            Units allowed in the test group.
        control_blacklist : List[Unit], optional
            Units excluded from the control group.
        test_blacklist : List[Unit], optional
            Units excluded from the test group.
        control_test_blacklist : List[Unit], optional
            Units excluded from both control and test groups.
        treatment_period : TimePeriod, optional
            Time period during which treatment is assigned.
        pre_treatment_period : TimePeriod, optional
            Time period before which treatment is assigned.

        Returns
        -------
        PanelDataset
            Panel data object with updated treatment assignments.
        """
        # Validate that panel_data is provided
        if panel_data is None:
            raise ValueError("Panel data must be provided for assignment.")

        # Use provided lists if they exist, otherwise default to instance attributes
        self.control_blacklist = control_blacklist or self.control_blacklist
        self.test_blacklist = test_blacklist or self.test_blacklist
        self.control_test_blacklist = control_test_blacklist or self.control_test_blacklist
        self.control_whitelist = control_whitelist or self.control_whitelist
        self.test_whitelist = test_whitelist or self.test_whitelist
        self.n_test_grps = n_test_grps

        panel_data = copy.deepcopy(panel_data)

        # Subset data if pre-treatment period is specified (on copy only)
        if pre_treatment_period:
            from panel_exp.design.period_slice import slice_wide_to_time_period

            panel_data.wide_data = slice_wide_to_time_period(
                panel_data.wide_data, pre_treatment_period
            )

        # Assignments with or without blacklists and whitelists
        if not (self.control_blacklist or self.test_blacklist or self.control_test_blacklist):
            assignments = self.assign_all(
                panel_data.wide_data, panel_data.num_units, panel_data.num_timepoints, n_test_grps=n_test_grps
            )
            treated_units = [
                unit for idx, unit in enumerate(panel_data.units) if assignments[idx] == 1
            ]
        else:
            panel_data = panel_data.drop_units(self.control_test_blacklist)
            always_control = self.control_whitelist if len(self.control_whitelist + self.control_blacklist) == panel_data.num_units else []
            always_test = self.test_whitelist if len(self.test_whitelist + self.test_blacklist) == panel_data.num_units else []
            panel_data = panel_data.drop_units(self.control_test_blacklist)

            assignments = self.assign_all(
                wide_data=panel_data.wide_data,
                num_units=panel_data.num_units,
                num_timepoints=panel_data.num_timepoints,
                n_test_grps=n_test_grps,
                always_control=always_control,
                always_test=always_test,
                control_blacklist=self.control_blacklist,
                test_blacklist=self.test_blacklist
            )
            treated_units = [unit for idx, unit in enumerate(panel_data.wide_data.index) if assignments[idx] == 1]

            # Validate no treated units are in the blacklists
            if any(unit in treated_units for unit in self.test_blacklist):
                raise ValueError("Treated units found in the test blacklist.")
            if any(unit in treated_units for unit in self.control_test_blacklist):
                raise ValueError("Treated units found in the control-test blacklist.")

        if treatment_period:
            treatment_period = [treatment_period] * len(treated_units)

        return panel_data.assign_treatment(treated_units, treatment_period)

    @abstractmethod
    def assign_all(
        self, wide_data: pd.DataFrame, num_units: int, num_timepoints: int,
        always_control: Optional[List[Unit]] = None, always_test: Optional[List[Unit]] = None
    ) -> np.array:
        """
        Abstract method to define treatment assignment based on experimental design.

        Parameters
        ----------
        wide_data : pd.DataFrame
            The wide-format panel data with units as rows and time points as columns.
        num_units : int
            Total number of units in the dataset.
        num_timepoints : int
            Total number of time periods in the dataset.
        always_control : List[Unit], optional
            Units that must be assigned to the control group.
        always_test : List[Unit], optional
            Units that must be assigned to the test group.

        Returns
        -------
        np.array
            Array with 0 indicating control and 1 indicating treatment for each unit.
        """
        pass


class StratifiedRandomization(Design):
    """
    Stratified Randomization Experimental Design class, which assigns units to control and treatment groups
    based on percentile-based stratification of a covariate.

    Parameters
    ----------
    treatment_probability : float
        Probability of assigning treatment to a unit in the dataset.

    Methods
    -------
    assign(panel_data, treatment_period, pre_treatment_period, control_whitelist, test_whitelist, control_blacklist, test_blacklist, control_test_blacklist, n_test_grps):
        Assigns units to control and treatment groups based on stratified randomization.
    """

    def assign_all(self, wide_data: pd.DataFrame, num_units: int, num_timepoints: int) -> np.array:
        """
        Method to assign all units in the dataset. Currently not implemented.

        Raises
        ------
        Exception
            Always raises an exception as it is not implemented.
        """
        raise Exception()

    def assign(self,
        panel_data: PanelDataset,
        treatment_period: Optional[TimePeriod] = None,
        pre_treatment_period: Optional[TimePeriod] = None,
        control_whitelist: Optional[List[Unit]] = [],
        test_whitelist: Optional[List[Unit]] = [],
        control_blacklist: Optional[List[Unit]] = [],
        test_blacklist: Optional[List[Unit]] = [],
        control_test_blacklist: Optional[List[Unit]] = [],
        n_test_grps: Optional[int] = 1,
        n_percentiles: Optional[int] = 10) -> Dict[str, List[str]]:
        """
        Assigns units to control and multiple test groups using percentile-based stratification
        with volume balancing within strata. Whitelist/blacklist constraints are enforced.

        Parameters
        ----------
        panel_data : PanelDataset
            The panel dataset in wide format with units as rows and time periods as columns.
        treatment_period : TimePeriod, optional
            Period during which the treatment is applied.
        pre_treatment_period : TimePeriod, optional
            Period before treatment for pre-treatment balance checks.
        control_whitelist : List[Unit], optional
            Ignored. Must be handled before calling the function.
        test_whitelist : List[Unit], optional
            Ignored. Must be handled before calling the function.
        control_blacklist : List[Unit], optional
            Ignored. Must be handled before calling the function.
        test_blacklist : List[Unit], optional
            Ignored. Must be handled before calling the function.
        control_test_blacklist : List[Unit], optional
            Ignored. Must be handled before calling the function.
        n_test_grps : int, optional
            Number of test groups to create.
        n_percentiles : int, optional
            Number of percentiles (strata) to divide the DMAs into.

        Returns
        -------
        dict
            A dictionary with keys "control" and "test_0", "test_1", ..., for each test group.
        """

        wide = panel_data.wide_data
        ctx = prepare_constraint_context(
            wide,
            self.treatment_probability,
            n_test_grps,
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )
        rng = self._rng
        control_group = list(ctx.pinned_control)
        test_groups = {f"test_{i}": list(ctx.pinned_test[f"test_{i}"]) for i in range(n_test_grps)}
        total_volume = float(wide.sum().sum())
        if total_volume <= 0:
            raise ValueError("Total KPI volume must be positive for stratified assignment.")
        group_shares = {"control": sum(float(wide.loc[u].sum()) / total_volume for u in control_group)}
        for i in range(n_test_grps):
            key = f"test_{i}"
            group_shares[key] = sum(float(wide.loc[u].sum()) / total_volume for u in test_groups[key])
        target_shares = {
            "control": 1 - self.treatment_probability,
            **{f"test_{i}": self.treatment_probability / n_test_grps for i in range(n_test_grps)},
        }
        free_units = list(ctx.free_units)
        if free_units:
            covariate_values = wide.loc[free_units].mean(axis=1)
            percentiles = np.linspace(0, 100, n_percentiles + 1)
            stratum_labels = np.percentile(covariate_values.values, percentiles)
            strata = np.digitize(covariate_values.values, bins=stratum_labels, right=True)
            stratified_df = pd.DataFrame({"DMA": covariate_values.index, "Stratum": strata})
            for stratum in range(1, n_percentiles + 1):
                stratum_units = stratified_df[stratified_df["Stratum"] == stratum]["DMA"].tolist()
                rng.shuffle(stratum_units)
                for unit in stratum_units:
                    unit_share = float(wide.loc[unit].sum()) / total_volume
                    share_gaps = {g: target_shares[g] - group_shares[g] for g in target_shares}
                    best_group = max(share_gaps, key=share_gaps.get)
                    if best_group == "control":
                        control_group.append(unit)
                    else:
                        test_groups[best_group].append(unit)
                    group_shares[best_group] += unit_share
        assignment = {"control": control_group, **test_groups}
        validate_assignment_dict(
            assignment,
            ctx,
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )
        return freeze_assignment(assignment)


class BalancedRandomization(Design):
    """Volume-balanced assignment to KPI share targets (not Bernoulli randomization)."""

    def assign_all(self, wide_data: pd.DataFrame, num_units: int, num_timepoints: int) -> np.array:
        raise NotImplementedError("Use assign() returning a group dictionary.")

    def assign(
        self,
        panel_data: PanelDataset,
        treatment_period: Optional[TimePeriod] = None,
        pre_treatment_period: Optional[TimePeriod] = None,
        control_whitelist: Optional[List[Unit]] = None,
        test_whitelist: Optional[List[Unit]] = None,
        control_blacklist: Optional[List[Unit]] = None,
        test_blacklist: Optional[List[Unit]] = None,
        control_test_blacklist: Optional[List[Unit]] = None,
        n_test_grps: Optional[int] = 1,
    ) -> Dict[str, List]:
        wide = panel_data.wide_data
        ctx = prepare_constraint_context(
            wide,
            self.treatment_probability,
            n_test_grps,
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )
        assignment = balanced_volume_assign(wide, ctx, self._rng)
        validate_assignment_dict(
            assignment,
            ctx,
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )
        return freeze_assignment(assignment)


class CompleteRandomization(Design):
    """Bernoulli complete randomization with whitelist/blacklist enforcement."""

    def assign_all(self, wide_data: pd.DataFrame, num_units: int, num_timepoints: int) -> np.array:
        raise NotImplementedError("Use assign() returning a group dictionary.")

    def assign(
        self,
        panel_data: PanelDataset,
        treatment_period: Optional[TimePeriod] = None,
        pre_treatment_period: Optional[TimePeriod] = None,
        control_whitelist: Optional[List[Unit]] = None,
        test_whitelist: Optional[List[Unit]] = None,
        control_blacklist: Optional[List[Unit]] = None,
        test_blacklist: Optional[List[Unit]] = None,
        control_test_blacklist: Optional[List[Unit]] = None,
        n_test_grps: Optional[int] = 1,
    ) -> Dict[str, List]:
        wide = panel_data.wide_data
        ctx = prepare_constraint_context(
            wide,
            self.treatment_probability,
            n_test_grps,
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )
        assignment = bernoulli_complete_assign(wide, ctx, self._rng)
        validate_assignment_dict(
            assignment,
            ctx,
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )
        return freeze_assignment(assignment)


    # def assign_all(
    #     self,
    #     wide_data: pd.DataFrame,
    #     num_units: int,
    #     num_timepoints: int,
    #     always_control: Optional[List[Unit]] = None,
    #     always_test: Optional[List[Unit]] = None,
    #     control_blacklist: Optional[List[Unit]] = None,
    #     test_blacklist: Optional[List[Unit]] = None
    # ) -> np.ndarray:
    #     """
    #     Assigns units to control and treatment groups based on complete randomization.

    #     Parameters
    #     ----------
    #     wide_data : pd.DataFrame
    #         The panel dataset in wide format with units as rows and time periods as columns.
    #     num_units : int
    #         Total number of units in the dataset.
    #     num_timepoints : int
    #         Number of time points in the dataset.
    #     always_control : List[Unit], optional
    #         Units that must always be assigned to the control group.
    #     always_test : List[Unit], optional
    #         Units that must always be assigned to the treatment group.
    #     control_blacklist : List[Unit], optional
    #         Units that cannot be assigned to the control group.
    #     test_blacklist : List[Unit], optional
    #         Units that cannot be assigned to the treatment group.

    #     Returns
    #     -------
    #     np.ndarray
    #         Array where 0 represents control and 1 represents treatment for each unit.

    #     Raises
    #     ------
    #     ValueError
    #         If constraints cannot be satisfied due to insufficient units.
    #     """

    #     # Initialize lists if None to prevent mutable default arguments
    #     always_control = always_control or []
    #     always_test = always_test or []
    #     control_blacklist = control_blacklist or []
    #     test_blacklist = test_blacklist or []

    #     # Calculate the number of units that can be freely assigned after applying "always" lists
    #     adjusted_num_units = num_units - len(always_control) - len(always_test)
    #     if adjusted_num_units < 0:
    #         raise ValueError("More units are required in 'always' lists than available.")

    #     # Adjust treatment probability to account for units already assigned to the treatment group
    #     adjusted_treatment_probability = (
    #         (num_units * self.treatment_probability - len(always_test)) / adjusted_num_units
    #     )

    #     # Calculate required number of treated and control units
    #     num_treated_units = floor(adjusted_treatment_probability * (adjusted_num_units - len(test_blacklist)))
    #     num_control_units = adjusted_num_units - num_treated_units - len(control_blacklist)
    #     if num_control_units < 0:
    #         raise ValueError("Insufficient units available to satisfy control group constraints.")

    #     # Create an assignment array for the remaining units and shuffle for random assignment
    #     assignments_possible = np.concatenate([np.zeros(num_control_units), np.ones(num_treated_units)])
    #     np.random.shuffle(assignments_possible)

    #     # Initialize assignment list for each unit in wide_data
    #     treatments = [None] * num_units
    #     counter = 0

    #     for idx, unit in enumerate(wide_data.index):
    #         if unit in always_control:
    #             treatments[idx] = 0
    #         elif unit in always_test:
    #             treatments[idx] = 1
    #         else:
    #             treatments[idx] = assignments_possible[counter]
    #             counter += 1

    #     # Validate that "always" lists are respected in the final assignments
    #     if any(treatments[wide_data.index.get_loc(unit)] != 1 for unit in always_test):
    #         raise ValueError("Some units in 'always_test' list are not assigned to treatment.")
    #     if any(treatments[wide_data.index.get_loc(unit)] != 0 for unit in always_control):
    #         raise ValueError("Some units in 'always_control' list are not assigned to control.")

    #     return np.array(treatments)


class ThinningDesign(Design):
    """
    Thinning Design Experimental Class based on the "Kernel Thinning" algorithm by Dwivedi & Mackey (2021).
    This class assigns units to control and test groups using the Thinning Design algorithm while respecting specified
    control and test whitelists/blacklists.

    Parameters
    ----------
    treatment_probability : float
        Probability of assigning treatment to a unit.
    delta : float, optional
        Probability of failure to hold imbalance bounds (default is 0.5).

    Methods
    -------
    assign_all(wide_data, num_units, num_timepoints, always_control, always_test, control_blacklist, test_blacklist):
        Assigns units to control and treatment groups based on the Thinning Design algorithm.
    """

    def __init__(
        self,
        treatment_probability: float,
        delta: float = 0.5,
        random_state: Optional[int] = 42,
    ):
        super().__init__(treatment_probability, random_state=random_state)
        self.delta = delta

    def assign_all(self, wide_data: pd.DataFrame, num_units: int, num_timepoints: int) -> np.array:
        """
        Method to assign all units in the dataset. Currently not implemented.

        Raises
        ------
        Exception
            Always raises an exception as it is not implemented.
        """
        raise Exception()

    def assign(
        self,
        panel_data: PanelDataset,
        treatment_period: Optional[TimePeriod] = None,
        pre_treatment_period: Optional[TimePeriod] = None,
        control_whitelist: Optional[List[Unit]] = None,
        test_whitelist: Optional[List[Unit]] = None,
        control_blacklist: Optional[List[Unit]] = None,
        test_blacklist: Optional[List[Unit]] = None,
        control_test_blacklist: Optional[List[Unit]] = None,
        n_test_grps: Optional[int] = 1,
    ) -> Dict[str, List]:
        """
        Assigns units to one control group and multiple test groups using the Thinning Design algorithm.

        Parameters
        ----------
        wide_data : pd.DataFrame
            Panel data in wide format with units as rows and time periods as columns.
        num_units : int
            Total number of units in the dataset.
        num_timepoints : int
            Total number of time points in the dataset.
        n_test_grps : int
            Number of test groups to create.
        always_control : List[Unit], optional
            Units that must always be assigned to the control group.
        always_test : List[Unit], optional
            Units that must always be assigned to the treatment groups.
        control_blacklist : List[Unit], optional
            Units that cannot be assigned to the control group.
        test_blacklist : List[Unit], optional
            Units that cannot be assigned to the test groups.

        Returns
        -------
        dict
            A dictionary with keys "control" and "test_0", "test_1", ..., for each test group.

        Raises
        ------
        ValueError
            If treatment probability is not within [0, 1].
        """

        if not (0 <= self.treatment_probability <= 1):
            raise ValueError("Treatment probability must be between 0 and 1.")

        wide = panel_data.wide_data
        ctx = prepare_constraint_context(
            wide,
            self.treatment_probability,
            n_test_grps,
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )

        treatment_probability_per_group = self.treatment_probability / n_test_grps
        num_timepoints = len(wide.columns)
        w_i = np.zeros(num_timepoints)
        alpha = 0.5 * np.log(4.0 * max(len(ctx.all_units), 1) / self.delta)
        value_plus = 2.0 * (1 - self.treatment_probability)
        value_minus = -2.0 * self.treatment_probability

        control_group = list(ctx.pinned_control)
        test_groups = {f"test_{i}": list(ctx.pinned_test[f"test_{i}"]) for i in range(n_test_grps)}

        max_row_norm = np.max(np.linalg.norm(wide.values, axis=1))
        if max_row_norm <= 0:
            max_row_norm = 1.0
        total_volume = float(wide.sum().sum())
        if total_volume <= 0:
            raise ValueError("Total KPI volume must be positive for thinning assignment.")

        control_share = sum(float(wide.loc[u].sum()) / total_volume for u in control_group)
        test_shares = {
            f"test_{i}": sum(float(wide.loc[u].sum()) / total_volume for u in test_groups[f"test_{i}"])
            for i in range(n_test_grps)
        }

        free_order = list(ctx.free_units)
        self._rng.shuffle(free_order)

        for unit in free_order:
            x = wide.loc[unit].values / max_row_norm
            dot_product = float(x @ w_i)
            unit_share = float(wide.loc[unit].sum()) / total_volume

            if dot_product > alpha:
                if control_share + unit_share <= (1 - self.treatment_probability):
                    control_group.append(unit)
                    control_share += unit_share
                    w_i += value_minus * x * abs(dot_product / alpha)
            elif dot_product < -alpha:
                group_keys = list(test_groups.keys())
                self._rng.shuffle(group_keys)
                for group_key in group_keys:
                    if test_shares[group_key] + unit_share <= treatment_probability_per_group:
                        test_groups[group_key].append(unit)
                        test_shares[group_key] += unit_share
                        w_i += value_plus * x * abs(dot_product / alpha)
                        break
            else:
                p_i = treatment_probability_per_group * (1 - dot_product / alpha)
                if self._rng.random() < p_i:
                    group_keys = list(test_groups.keys())
                    self._rng.shuffle(group_keys)
                    for group_key in group_keys:
                        if test_shares[group_key] + unit_share <= treatment_probability_per_group:
                            test_groups[group_key].append(unit)
                            test_shares[group_key] += unit_share
                            w_i += value_plus * x
                            break
                elif control_share + unit_share <= (1 - self.treatment_probability):
                    control_group.append(unit)
                    control_share += unit_share
                    w_i += value_minus * x

        assignment = freeze_assignment({"control": control_group, **test_groups})
        validate_assignment_dict(
            assignment,
            ctx,
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )
        return assignment

    

    # def assign_all(
    #     self,
    #     wide_data: pd.DataFrame,
    #     num_units: int,
    #     num_timepoints: int,
    #     always_control: Optional[List[Unit]] = None,
    #     always_test: Optional[List[Unit]] = None,
    #     control_blacklist: Optional[List[Unit]] = None,
    #     test_blacklist: Optional[List[Unit]] = None
    # ) -> np.ndarray:
    #     """
    #     Assigns units to control and test groups using the Thinning Design algorithm while respecting specified control and test lists.

    #     Parameters
    #     ----------
    #     wide_data : pd.DataFrame
    #         Panel data in wide format with units as rows and time periods as columns.
    #     num_units : int
    #         Total number of units in the dataset.
    #     num_timepoints : int
    #         Total number of time points in the dataset.
    #     always_control : List[Unit], optional
    #         Units that must always be assigned to the control group.
    #     always_test : List[Unit], optional
    #         Units that must always be assigned to the treatment group.
    #     control_blacklist : List[Unit], optional
    #         Units that cannot be assigned to the control group.
    #     test_blacklist : List[Unit], optional
    #         Units that cannot be assigned to the treatment group.

    #     Returns
    #     -------
    #     np.ndarray
    #         Array where 0 represents control and 1 represents treatment for each unit.

    #     Raises
    #     ------
    #     ValueError
    #         If treatment probability is not within [0, 1].
    #     """

    #     # Set default lists if None to avoid mutable defaults
    #     always_control = always_control or []
    #     always_test = always_test or []
    #     control_blacklist = control_blacklist or []
    #     test_blacklist = test_blacklist or []

    #     # Ensure treatment probability is valid
    #     if not (0 <= self.treatment_probability <= 1):
    #         raise ValueError("Treatment probability must be between 0 and 1.")

    #     # Initialize variables for the thinning algorithm
    #     w_i = np.zeros(num_timepoints)  # Initialize weight vector
    #     alpha = 0.5 * np.log(4.0 * num_units / self.delta)
    #     value_plus = 2.0 * (1 - self.treatment_probability)
    #     value_minus = -2.0 * self.treatment_probability
    #     treatments = []

    #     # Normalize rows of the dataset
    #     max_row_norm = np.max(np.linalg.norm(wide_data.values, axis=1))

    #     for unit, x in wide_data.iterrows():
    #         # Assign units in the always_control or always_test lists
    #         if unit in always_control:
    #             treatments.append(0)
    #             continue
    #         elif unit in always_test:
    #             treatments.append(1)
    #             continue

    #         # Normalize the feature vector
    #         x = x.values / max_row_norm
    #         dot_product = x @ w_i

    #         # Determine the assignment based on the dot product and alpha threshold
    #         if dot_product > alpha:
    #             assignment = 0  # Control
    #             w_i += value_minus * x * abs(dot_product / alpha)
    #         elif dot_product < -alpha:
    #             assignment = 1  # Treatment
    #             w_i += value_plus * x * abs(dot_product / alpha)
    #         else:
    #             # Assign based on probability p_i
    #             p_i = self.treatment_probability * (1 - dot_product / alpha)
    #             assignment = 1 if np.random.rand() < p_i else 0

    #         treatments.append(assignment)

    #         # Update w_i based on the assignment
    #         w_i += (value_plus if assignment == 1 else value_minus) * x

    #     # Verify that "must" lists are respected
    #     if any(treatments[wide_data.index.get_loc(unit)] != 1 for unit in always_test):
    #         raise ValueError("Some 'always_test' units are not assigned to the test group.")
    #     if any(treatments[wide_data.index.get_loc(unit)] != 0 for unit in always_control):
    #         raise ValueError("Some 'always_control' units are not assigned to the control group.")

    #     return np.array(treatments)


class Rerandomization(Design):
    """
    Rerandomization design class to assign units to treatment and control groups, aiming to minimize imbalance 
    over a specified number of iterations using a base randomization method.

    Parameters
    ----------
    treatment_probability : float
        Probability of assigning treatment to a unit.
    max_iter : int, optional
        Maximum number of iterations allowed for rerandomization (default is 1000).
    target_imbalance : float, optional
        Target imbalance value below which the assignment is considered optimal (default is 1e-2).
    imbalance_metric : str, optional
        Metric used to calculate imbalance ('l2', 'rmse', 'mae'). Default is 'l2'.
    base_randomizer_cls : Callable, optional
        Base randomizer class to use (default is CompleteRandomization).
    **base_randomizer_kwargs : Additional keyword arguments
        Additional arguments passed to the base randomizer class.

    Methods
    -------
    assign(panel_data, treatment_period, pre_treatment_period, control_whitelist, test_whitelist, control_blacklist, test_blacklist, control_test_blacklist):
        Assign units to treatment and control groups using rerandomization to minimize imbalance.
    """

    def __init__(
        self,
        treatment_probability: float,
        max_iter: int = 1000,
        target_imbalance: float = 1e-2,
        imbalance_metric: str = "l2",
        base_randomizer_cls: Optional[Callable] = None,
        **base_randomizer_kwargs
    ):
        super().__init__(treatment_probability=treatment_probability)
        
        # Initialize base randomizer (default is BalancedRandomization)
        if base_randomizer_cls is None:
            self.base_randomizer = BalancedRandomization(
                treatment_probability=treatment_probability,
                random_state=base_randomizer_kwargs.get("random_state"),
            )
        else:
            kwargs = dict(base_randomizer_kwargs)
            if "random_state" not in kwargs:
                kwargs["random_state"] = None
            self.base_randomizer = base_randomizer_cls(
                treatment_probability=treatment_probability, **kwargs
            )

        self.metric = imbalance_metric
        self.target_imbalance = target_imbalance
        self.max_iter = max_iter

    def assign_all(
        self,
        wide_data: pd.DataFrame,
        num_units: int,
        num_timepoints: int,
        always_control: List[Unit],
        always_test: List[Unit]
    ) -> np.ndarray:
        """
        Raises an exception, as assign_all is not supported in Rerandomization design.

        Raises
        ------
        NotImplementedError
            Always raises this exception, as assign_all is not implemented.
        """
        raise NotImplementedError("assign_all is not supported in Rerandomization design.")

    def assign(
        self,
        panel_data: PanelDataset,
        treatment_period: Optional[TimePeriod] = None,
        pre_treatment_period: Optional[TimePeriod] = None,
        control_whitelist: Optional[List[Unit]] = None,
        test_whitelist: Optional[List[Unit]] = None,
        control_blacklist: Optional[List[Unit]] = None,
        test_blacklist: Optional[List[Unit]] = None,
        control_test_blacklist: Optional[List[Unit]] = None,
        n_test_grps: Optional[int] = 1
    ) -> PanelDataset:
        """
        Assigns units to treatment and control groups using rerandomization to minimize imbalance.

        Parameters
        ----------
        panel_data : PanelDataset
            Panel dataset with units as rows and time periods as columns.
        treatment_period : TimePeriod, optional
            Period during which the treatment is applied.
        pre_treatment_period : TimePeriod, optional
            Period before treatment for pre-treatment balance checks.
        control_whitelist : List[Unit], optional
            Units that must be included in the control group.
        test_whitelist : List[Unit], optional
            Units that must be included in the test group.
        control_blacklist : List[Unit], optional
            Units that must be excluded from the control group.
        test_blacklist : List[Unit], optional
            Units that must be excluded from the test group.
        control_test_blacklist : List[Unit], optional
            Units that must be excluded from both control and test groups.

        Returns
        -------
        PanelDataset
            The optimal assignment of units to treatment or control based on minimized imbalance.

        Raises
        ------
        ValueError
            If imbalance calculation fails or is invalid.
        """
        # Set default lists if None to avoid mutable defaults
        control_whitelist = control_whitelist or []
        test_whitelist = test_whitelist or []
        control_blacklist = control_blacklist or []
        test_blacklist = test_blacklist or []
        control_test_blacklist = control_test_blacklist or []

        base_name = type(self.base_randomizer).__name__.lower()
        if not any(k in base_name for k in RERANDOMIZATION_IMBALANCE_BASES):
            supported = ", ".join(sorted(RERANDOMIZATION_IMBALANCE_BASES))
            raise ValueError(
                f"Rerandomization base {type(self.base_randomizer).__name__!r} does not support "
                f"imbalance evaluation. Supported bases: {supported}."
            )

        imbalance_val = np.inf
        cur_iter = 0
        best_assignment = None
        eval_period = pre_treatment_period or treatment_period

        while (imbalance_val > self.target_imbalance) and (cur_iter < self.max_iter):
            panel = self.base_randomizer.assign(
                panel_data=panel_data,
                treatment_period=treatment_period,
                pre_treatment_period=pre_treatment_period,
                control_whitelist=control_whitelist,
                test_whitelist=test_whitelist,
                control_blacklist=control_blacklist,
                test_blacklist=test_blacklist,
                control_test_blacklist=control_test_blacklist,
                n_test_grps=n_test_grps,
            )
            balance_panel = panel_data
            if pre_treatment_period is not None:
                from panel_exp.design.period_slice import slice_wide_to_time_period

                balance_panel = copy.deepcopy(panel_data)
                balance_panel.wide_data = slice_wide_to_time_period(
                    panel_data.wide_data, pre_treatment_period
                )
            cur_imbalance = _compute_assignment_imbalance(
                balance_panel,
                panel,
                n_test_grps,
                eval_period,
                self.metric,
            )
            if cur_imbalance < imbalance_val:
                best_assignment = panel
                imbalance_val = cur_imbalance
            cur_iter += 1
            if imbalance_val <= self.target_imbalance:
                break

        if best_assignment is None:
            raise RuntimeError(
                f"Rerandomization failed after {self.max_iter} iterations; "
                f"no valid assignment produced (final imbalance {imbalance_val})."
            )
        return best_assignment


def _eval_period_clipped(
    panel_data: PanelDataset,
    period: Optional[TimePeriod],
) -> TimePeriod:
    """Map a requested period to labels present on ``panel_data.wide_data``."""
    cols = panel_data.wide_data.columns
    lo, hi = cols.min(), cols.max()
    if period is None:
        return TimePeriod(lo, hi)
    start = period.start if period.start in cols else lo
    end = period.end if period.end in cols else hi
    return TimePeriod(start, end)


def _compute_assignment_imbalance(
    panel_data: PanelDataset,
    assignment: Dict[str, List],
    n_test_grps: int,
    treatment_period: Optional[TimePeriod],
    metric: str,
) -> float:
    """Sum imbalance across test arms vs shared control."""
    treatment_period = _eval_period_clipped(panel_data, treatment_period)
    wide_reset = panel_data.wide_data.reset_index()
    unit_col = wide_reset.columns[0]
    data = wide_reset.melt(id_vars=unit_col, var_name="time", value_name="value")
    total = 0.0
    for test_group in [f"test_{i}" for i in range(n_test_grps)]:
        units = assignment[test_group] + assignment["control"]
        trmd_data = data[data[unit_col].isin(units)]
        imbalance_panel_data = long_df_to_paneldataset(
            trmd_data,
            "time",
            unit_col,
            "value",
            assignment[test_group],
            [treatment_period.start] * len(assignment[test_group]),
            [treatment_period.end] * len(assignment[test_group]),
        )
        norm = np.max(np.linalg.norm(imbalance_panel_data.wide_data.values, axis=1))
        if norm > 0:
            imbalance_panel_data.wide_data = imbalance_panel_data.wide_data / norm
        imbalance_panel_data.wide_data = imbalance_panel_data.wide_data.fillna(0)
        total += imbalance(imbalance_panel_data, metric=metric)
    return total

    

class greedy_match_markets(Design):
    """
    Initializes the greedy_match_markets class.

    **Greedy Match Markets Algorithm:** 
    This algorithm creates test and control groups by greedily maximizing the score of a given function (such as correlation_score, l2_distance, dtw distance, etc.) between the groups. 
    In each iteration, the algorithm augments the control or one of the test groups with a randomly selected new DMA (Designated Market Area) if the score of the given function improves as a result.
    
    **Stepwise Summary:**

    1.  Initialize test and control groups with whitelisted DMAs if provided, otherwise randomly assign DMAs.
    2.  Remove blacklisted DMAs from both test and control groups.
    3.  Greedily optimize the score of a specified function (e.g., correlation) by augmenting the test and control groups with new DMAs.
    4.  Ensure balanced assignments between test and control groups.
    5.  Iterate the process to find optimal market pairs, ensuring that treatment/control shares remain within a specified threshold.
    6.  Return the finalized test and control groups and update the panel data.

    Parameters
    ----------
    func_to_optimize : str, optional
        Function to optimize for the matching (e.g., 'corr' for correlation, 'dtw' for dynamic time warping, 'l2_imbalance' for l2 imbalance). Default is 'corr'.
    treatment_probability : float, optional
        The proportion of units to be assigned to the treatment group. Default is 0.5.
    split_type : str, optional
        Defines the way the test group is formed (e.g., 'kpi_share' for share-based split). Default is 'kpi_share'.

    Methods
    -------    
    assign(panel_data, treatment_period, control_whitelist, test_whitelist, control_blacklist, test_blacklist, control_test_blacklist, samples):
        Assign units to treatment and control groups by greedily optimizing for correlation or dtw distance or l2_imbalance.

    """

    def __init__(
        self,
        func_to_optimize: Optional[str] = "corr",
        treatment_probability: Optional[float] = 0.5,
        split_type: Optional[str] = "kpi_share",
        random_state: Optional[int] = 42,
        min_control_units: int = 1,
        feasibility_policy: FeasibilityPolicy = "control_reservation",
    ):
        super().__init__(treatment_probability, random_state=random_state)
        self.func_to_optimize = func_to_optimize
        self.treatment_probability = treatment_probability
        self.split_type = split_type
        self.min_control_units = max(1, int(min_control_units))
        self.feasibility_policy: FeasibilityPolicy = feasibility_policy
        self.last_feasibility_metadata: dict[str, Any] | None = None

    def assign_all(self, wide_data: pd.DataFrame, num_units: int, num_timepoints: int) -> np.array:
        """
        Method to assign all units in the dataset. Currently not implemented.

        Raises
        ------
        Exception
            Always raises an exception as it is not implemented.
        """
        raise Exception()

    @staticmethod
    def _count_test_units(r: dict, n_test_grps: int) -> int:
        return sum(len(r[f"test_{i}"]) for i in range(n_test_grps))

    def _can_assign_to_test(
        self,
        r: dict,
        *,
        n_test_grps: int,
        feasibility,
        dma_list: list,
        unit_index: int,
        unit: str,
        assigned: set,
        test_whitelist: list,
        control_blacklist: list,
    ) -> bool:
        if self.feasibility_policy == "legacy":
            return True
        n_test = self._count_test_units(r, n_test_grps)
        if n_test + 1 > feasibility.max_feasible_n_treated:
            return False
        if self.feasibility_policy == "feasibility_cap":
            return True
        remaining = [
            u
            for u in dma_list[unit_index + 1 :]
            if u not in assigned and u != unit
        ]
        potential_control = len(r["control"]) + len(
            [
                u
                for u in remaining
                if u not in test_whitelist and u not in control_blacklist
            ]
        )
        return potential_control >= feasibility.min_control_units

    def _sweep_unassigned_to_control(
        self,
        r: dict,
        *,
        ctx,
        n_test_grps: int,
        control_blacklist: list,
        test_blacklist: list,
    ) -> None:
        assigned = set(r["control"]) | {
            u for i in range(n_test_grps) for u in r[f"test_{i}"]
        }
        for unit in ctx.all_units:
            if unit in assigned or unit in ctx.excluded:
                continue
            if unit in control_blacklist or unit in test_blacklist:
                continue
            r["control"].append(unit)
            assigned.add(unit)

    def assign(
        self,
        panel_data: PanelDataset,
        treatment_period: Optional[TimePeriod] = None,
        pre_treatment_period: Optional[TimePeriod] = None,
        control_whitelist: Optional[List[Unit]] = None,
        test_whitelist: Optional[List[Unit]] = None,
        control_blacklist: Optional[List[Unit]] = None,
        test_blacklist: Optional[List[Unit]] = None,
        control_test_blacklist: Optional[List[Unit]] = None,
        n_test_grps: Optional[int] = 1,
    ) -> Dict[str, List]:
    
        """
        Assigns DMAs to test and control groups based on predefined rules and optimizations.
        
        Parameters
        ----------
        panel_data : PanelDataset
            The dataset with DMAs and corresponding time-series values.
        treatment_period : TimePeriod, optional
            The period in which the treatment is applied (default is the entire dataset time range).
        pre_treatment_period : TimePeriod, optional
            The period before treatment for reference or balancing.
        control_whitelist : list, optional
            List of DMAs that should always be included in the control group.
        test_whitelist : list, optional
            List of DMAs that should always be included in the test group.
        control_blacklist : list, optional
            List of DMAs to be excluded from the control group.
        test_blacklist : list, optional
            List of DMAs to be excluded from the test group.
        control_test_blacklist : list, optional
            List of DMAs to be excluded from both the test and control groups.
        n_test_grps : int, optional
            Number of test groups to simultaneously create. Default is 1.

        Returns
        -------
        np.ndarray :
            Updated panel dataset with the assigned test and control groups.
        """

        cw, tw, cb, tb, ctb = freeze_constraint_lists(
            control_whitelist,
            test_whitelist,
            control_blacklist,
            test_blacklist,
            control_test_blacklist,
        )
        wide = panel_data.wide_data
        if pre_treatment_period is not None:
            from panel_exp.design.period_slice import slice_wide_to_time_period

            wide = slice_wide_to_time_period(wide, pre_treatment_period)
        ctx = prepare_constraint_context(
            wide,
            self.treatment_probability,
            n_test_grps,
            cw,
            tw,
            cb,
            tb,
            ctb,
        )
        n_assignable = len([u for u in ctx.all_units if u not in ctx.excluded])
        pinned_test = sum(len(v) for v in ctx.pinned_test.values())
        feasibility = compute_greedy_feasibility(
            n_assignable=n_assignable,
            treatment_probability=self.treatment_probability,
            n_test_grps=n_test_grps,
            pinned_control=len(ctx.pinned_control),
            pinned_test=pinned_test,
            min_control_units=self.min_control_units,
            policy=self.feasibility_policy,
        )
        if self.feasibility_policy == "preflight_fail" and not feasibility.feasible:
            raise ValueError(
                f"Greedy assignment infeasible: {feasibility.feasibility_reason} "
                f"(requested_n_treated={feasibility.requested_n_treated}, "
                f"max_feasible_n_treated={feasibility.max_feasible_n_treated}, "
                f"min_control_units={feasibility.min_control_units})."
            )

        # Function to compute the correlation between control and test groups.
        def corr_func(df, x, y):
            return np.abs(np.corrcoef(df[x].sum(axis=1), df[y].sum(axis=1))[0][1])

        # Function to compute the dynamic time warping (DTW) distance between control and test groups.
        def dtw_distance(df, x, y):
            return round(dtw.distance(df[x].sum(axis=1).values, df[y].sum(axis=1).values))

        normalized_data = wide.copy()
        row_norm = np.max(np.linalg.norm(normalized_data.values, axis=1))
        if row_norm > 0:
            normalized_data = normalized_data / row_norm
        data = normalized_data.reset_index().melt(id_vars=normalized_data.index.name)

        if treatment_period is None:
            treatment_period = TimePeriod(
                normalized_data.columns.min(), normalized_data.columns.max()
            )

        sales_df = wide.T.copy()

        r = {
            "control": list(ctx.pinned_control),
            "control_share": [0],
            "test_share": 0,
            "test_grps_share": [0] * n_test_grps,
        }
        for i in range(n_test_grps):
            r[f"test_{i}"] = list(ctx.pinned_test[f"test_{i}"])

        free_pool = list(ctx.free_units)
        self._rng.shuffle(free_pool)
        pool_i = 0
        if not r["control"]:
            if pool_i >= len(free_pool):
                raise ValueError("No units available to seed control group.")
            r["control"] = [free_pool[pool_i]]
            pool_i += 1
        for i in range(n_test_grps):
            if not r[f"test_{i}"]:
                if pool_i >= len(free_pool):
                    raise ValueError(f"No units available to seed test_{i}.")
                r[f"test_{i}"] = [free_pool[pool_i]]
                pool_i += 1

        assigned = set(r["control"]) | {
            u for i in range(n_test_grps) for u in r[f"test_{i}"]
        }
        dma_list = [
            u for u in ctx.all_units if u not in ctx.excluded and u not in assigned
        ]
        self._rng.shuffle(dma_list)

        for unit_idx, c in enumerate(dma_list):
            # Skip DMAs already assigned
            if c in r["control"] or any(c in r[f"test_{i}"] for i in range(n_test_grps)):
                continue

            assigned = set(r["control"]) | {
                u for i in range(n_test_grps) for u in r[f"test_{i}"]
            }

            best_score = -np.inf
            best_assignment = None
            _temp_r = None  # Placeholder for the best temporary group assignment

            # Calculate the current overall score for the entire setup
            current_score = np.mean([
                corr_func(sales_df, r["control"], r[f"test_{i}"]) if self.func_to_optimize == "corr" else
                -dtw_distance(sales_df, r["control"], r[f"test_{i}"]) if self.func_to_optimize == "dtw" else
                -imbalance(long_df_to_paneldataset(
                    data[data[data.columns[0]].isin(r["control"] + r[f"test_{i}"])],
                    data.columns[1], data.columns[0], data.columns[2],
                    treated_units=r[f"test_{i}"]
                ))
                for i in range(n_test_grps)
            ])

            # Handle Control Whitelist with Size Constraint
            if c in cw:
                control_share = r["control_share"][0] + sales_df[c].sum(axis=0) / sales_df.sum(axis=1).sum()
                if control_share <= 1 - self.treatment_probability:  # Ensure size constraint is respected
                    temp_control = r["control"] + [c]
                    temp_test_groups = [r[f"test_{i}"] for i in range(n_test_grps)]

                    # Calculate the new overall score
                    new_score = np.mean([
                        corr_func(sales_df, temp_control, temp_test_groups[i]) if self.func_to_optimize == "corr" else
                        -dtw_distance(sales_df, temp_control, temp_test_groups[i]) if self.func_to_optimize == "dtw" else
                        -imbalance(long_df_to_paneldataset(
                            data[data[data.columns[0]].isin(temp_control + temp_test_groups[i])],
                            data.columns[1], data.columns[0], data.columns[2],
                            treated_units=temp_test_groups[i]
                        )) for i in range(n_test_grps)
                    ])

                    # Check if the new score improves upon the current score
                    if new_score > current_score and new_score > best_score:
                        best_score = new_score
                        best_assignment = "control"
                        _temp_r = temp_control

            # Handle Test Whitelist with Size Constraint
            for i in range(n_test_grps):
                if c in tw:
                    test_share = r["test_grps_share"][i] + sales_df[c].sum(axis=0) / sales_df.sum(axis=1).sum()
                    if test_share <= self.treatment_probability/n_test_grps:  # Ensure size constraint is respected
                        temp_control = r["control"]
                        temp_test_groups = [r[f"test_{j}"] for j in range(n_test_grps)]
                        temp_test_groups[i] = temp_test_groups[i] + [c]

                        # Calculate the new overall score
                        new_score = np.mean([
                            corr_func(sales_df, temp_control, temp_test_groups[j]) if self.func_to_optimize == "corr" else
                            -dtw_distance(sales_df, temp_control, temp_test_groups[j]) if self.func_to_optimize == "dtw" else
                            -imbalance(long_df_to_paneldataset(
                                data[data[data.columns[0]].isin(temp_control + temp_test_groups[j])],
                                data.columns[1], data.columns[0], data.columns[2],
                                treated_units=temp_test_groups[j]
                            )) for j in range(n_test_grps)
                        ])

                        # Check if the new score improves upon the current score
                        if new_score > current_score and new_score > best_score:
                            best_score = new_score
                            best_assignment = f"test_{i}"
                            _temp_r = temp_test_groups[i]

            # Handle Non-Whitelisted DMAs (Regular Optimization)
            if c not in cw and c not in tw:
                # Try assigning to control group
                control_share = r["control_share"][0] + sales_df[c].sum(axis=0) / sales_df.sum(axis=1).sum()
                if control_share <= 1 - self.treatment_probability:
                    temp_control = r["control"] + [c]
                    temp_test_groups = [r[f"test_{i}"] for i in range(n_test_grps)]

                    # Calculate the new overall score
                    new_score = np.mean([
                        corr_func(sales_df, temp_control, temp_test_groups[i]) if self.func_to_optimize == "corr" else
                        -dtw_distance(sales_df, temp_control, temp_test_groups[i]) if self.func_to_optimize == "dtw" else
                        -imbalance(long_df_to_paneldataset(
                            data[data[data.columns[0]].isin(temp_control + temp_test_groups[i])],
                            data.columns[1], data.columns[0], data.columns[2],
                            treated_units=temp_test_groups[i]
                        )) for i in range(n_test_grps)
                    ])

                    # Check if the new score improves upon the current score
                    if new_score > current_score and new_score > best_score:
                        best_score = new_score
                        best_assignment = "control"

                # Try assigning to test groups
                for i in range(n_test_grps):
                    test_share = r["test_grps_share"][i] + sales_df[c].sum(axis=0) / sales_df.sum(axis=1).sum()
                    if test_share <= self.treatment_probability/n_test_grps:
                        temp_control = r["control"]
                        temp_test_groups = [r[f"test_{j}"] for j in range(n_test_grps)]
                        temp_test_groups[i] = temp_test_groups[i] + [c]

                        # Calculate the new overall score
                        new_score = np.mean([
                            corr_func(sales_df, temp_control, temp_test_groups[j]) if self.func_to_optimize == "corr" else
                            -dtw_distance(sales_df, temp_control, temp_test_groups[j]) if self.func_to_optimize == "dtw" else
                            -imbalance(long_df_to_paneldataset(
                                data[data[data.columns[0]].isin(temp_control + temp_test_groups[j])],
                                data.columns[1], data.columns[0], data.columns[2],
                                treated_units=temp_test_groups[j]
                            )) for j in range(n_test_grps)
                        ])

                        # Check if the new score improves upon the current score
                        if new_score > current_score and new_score > best_score:
                            best_score = new_score
                            best_assignment = f"test_{i}"

            # Apply the best assignment
            if best_assignment == "control":
                r["control"].append(c)
            elif best_assignment and best_assignment.startswith("test_"):
                if self._can_assign_to_test(
                    r,
                    n_test_grps=n_test_grps,
                    feasibility=feasibility,
                    dma_list=dma_list,
                    unit_index=unit_idx,
                    unit=c,
                    assigned=assigned,
                    test_whitelist=tw,
                    control_blacklist=cb,
                ):
                    group_index = int(best_assignment.split("_")[1])
                    r[f"test_{group_index}"].append(c)

            # Update shares
            r["control_share"] = [
                sales_df[r["control"]].sum(axis=1).sum() / sales_df.sum(axis=1).sum()
            ]
            r["test_grps_share"] = [
                sales_df[r[f"test_{j}"]].sum(axis=1).sum() / sales_df.sum(axis=1).sum()
                for j in range(n_test_grps)
            ]
            r["test_share"] = sum(r["test_grps_share"])

        if self.feasibility_policy != "legacy":
            self._sweep_unassigned_to_control(
                r,
                ctx=ctx,
                n_test_grps=n_test_grps,
                control_blacklist=cb,
                test_blacklist=tb,
            )

        result = {
            "control": r["control"],
            **{f"test_{i}": r[f"test_{i}"] for i in range(n_test_grps)},
        }
        validate_assignment_dict(result, ctx, cw, tw, cb, tb, ctb)
        realized_n_treated = self._count_test_units(result, n_test_grps)
        realized_n_control = len(result["control"])
        n_assigned = realized_n_treated + realized_n_control
        candidate_pool_exhausted = n_assigned < n_assignable
        feasibility_adjusted = (
            self.feasibility_policy != "legacy"
            and (
                realized_n_treated < feasibility.requested_n_treated
                or candidate_pool_exhausted
            )
        )
        if self.feasibility_policy == "legacy":
            self.last_feasibility_metadata = None
        else:
            self.last_feasibility_metadata = build_feasibility_metadata(
                feasibility,
                realized_n_treated=realized_n_treated,
                realized_n_control=realized_n_control,
                feasibility_adjusted=feasibility_adjusted,
                candidate_pool_exhausted=candidate_pool_exhausted,
            )
        return freeze_assignment(result)




    ## Creating multiple test simultaneously w/o size constraints on groups

    # def assign(self,
    #     panel_data: PanelDataset,
    #     treatment_period: Optional[TimePeriod] = None,
    #     pre_treatment_period: Optional[TimePeriod] = None,
    #     control_whitelist: Optional[List[Unit]] = [],
    #     test_whitelist: Optional[List[Unit]] = [],
    #     control_blacklist: Optional[List[Unit]] = [],
    #     test_blacklist: Optional[List[Unit]] = [],
    #     control_test_blacklist: Optional[List[Unit]] = [],
    #     n_test_grps: Optional[int] = 1) -> np.ndarray:
    
    #     """
    #     Assigns DMAs to test and control groups based on predefined rules and optimizations.
        
    #     Parameters
    #     ----------
    #     panel_data : PanelDataset
    #         The dataset with DMAs and corresponding time-series values.
    #     treatment_period : TimePeriod, optional
    #         The period in which the treatment is applied (default is the entire dataset time range).
    #     pre_treatment_period : TimePeriod, optional
    #         The period before treatment for reference or balancing.
    #     control_whitelist : list, optional
    #         List of DMAs that should always be included in the control group.
    #     test_whitelist : list, optional
    #         List of DMAs that should always be included in the test group.
    #     control_blacklist : list, optional
    #         List of DMAs to be excluded from the control group.
    #     test_blacklist : list, optional
    #         List of DMAs to be excluded from the test group.
    #     control_test_blacklist : list, optional
    #         List of DMAs to be excluded from both the test and control groups.
    #     n_test_grps : int, optional
    #         Number of test groups to simultaneously create. Default is 1.

    #     Returns
    #     -------
    #     np.ndarray :
    #         Updated panel dataset with the assigned test and control groups.
    #     """

    #     self.control_blacklist = control_blacklist
    #     self.control_whitelist = control_whitelist
    #     self.test_blacklist = test_blacklist
    #     self.test_whitelist = test_whitelist
    #     self.control_test_blacklist = control_test_blacklist
    #     self.n_test_grps = n_test_grps

    #     # Function to compute the correlation between control and test groups.
    #     def corr_func(df, x, y):
    #         return np.abs(np.corrcoef(df[x].sum(axis=1), df[y].sum(axis=1))[0][1])

    #     # Function to compute the dynamic time warping (DTW) distance between control and test groups.
    #     def dtw_distance(df, x, y):
    #         return round(dtw.distance(df[x].sum(axis=1).values, df[y].sum(axis=1).values))
        
    #     panel_data.wide_data = panel_data.wide_data / np.max(np.linalg.norm(panel_data.wide_data.values, axis=1))
    #     data = panel_data.wide_data.reset_index().melt(id_vars=panel_data.wide_data.index.name)
        
    #     if treatment_period is None:
    #         treatment_period = TimePeriod(panel_data.wide_data.columns.min(), panel_data.wide_data.columns.max())
        
    #     sales_df = panel_data.wide_data.T.copy()
    #     dma_list = sales_df.columns.tolist()
    #     matched_market_pairs = []
        
    #     control_test_blacklist += [dma for dma in test_blacklist if dma in control_blacklist]
    #     dma_list = list(set(dma_list) - set(control_test_blacklist))
    #     np.random.shuffle(dma_list)
        
    #     # for _ in range(samples):
    #     r = {}
        
    #     control_list = list(set(dma_list) - set(control_blacklist + test_whitelist))
    #     np.random.shuffle(control_list)
    #     r['control'] = [control_list[0]] if not control_whitelist else control_whitelist
        
    #     test_lists = [list(set(dma_list) - set(test_blacklist + control_whitelist + r['control'])) for _ in range(n_test_grps)]
    #     for test_list in test_lists:
    #         np.random.shuffle(test_list)
        
    #     for i in range(n_test_grps):
    #         r[f'test_{i}'] = [test_dma_list[i]] if i < len(test_whitelist) else [test_list[i + 1]]


    #     ref_aa_score = -np.inf
    #     np.random.shuffle(dma_list)
        
    #     for c in dma_list:
    #         if c not in set(r['control']).union(*[r[f'test_{i}'] for i in range(n_test_grps)]):
    #             tracker = {'g_%s' % _: None for _ in range(n_test_grps+1)}
            
    #         if (c in control_whitelist) or (c in test_blacklist):
    #             start = 0 
    #             end = 1
                
    #         elif c in test_whitelist or (c in control_blacklist):
    #             start = 1 
    #             end = n_test_grps+1

    #         elif c in control_test_blacklist:
    #             start = 0 
    #             end = 0
                
    #         else:
    #             start = 0
    #             end = n_test_grps+1

    #         # print(c,start,end)
                
    #         for pointer in range(start,end): # try adding market to each group, which one improves score the most if at all 
    #             ctrl = r['control'].copy()
    #             g1 = [r['test_%s' % k].copy() for k in range(n_test_grps)]
    #             groups = [ctrl] + g1
    #             groups[pointer] = np.append(groups[pointer], c)

    #             if self.func_to_optimize == 'corr':
    #                 score = np.mean([corr_func(sales_df, groups[0], groups[k]) for k in range(1,n_test_grps+1)])
    #             elif self.func_to_optimize == 'dtw':
    #                 score = -np.mean([dtw_distance(sales_df, groups[0], groups[k]) for k in range(1,n_test_grps+1)])
    #             else:
    #                 score = -np.mean([imbalance(long_df_to_paneldataset(
    #                     data[data[data.columns[0]].isin(groups[0] + groups[k])],
    #                     data.columns[1], data.columns[0], data.columns[2], treated_units=r['test_%s' %k])
    #                 ) for k in range(1,n_test_grps+1)])

    #             if (score > ref_aa_score):
    #                 tracker = {'g_%s' % _: groups[_] for _ in range(n_test_grps+1)}.copy()
    #                 ref_aa_score = score 
    #             # print(c,ref_aa_score,score)

    #         if tracker['g_0'] is not None:
    #             r['control'] = list(tracker['g_0'])
    #             for _ in range(1, n_test_grps+1):
    #                 r['test_%s' % str(int(_)-1)] = list(tracker['g_%s' % _])
    #             # r['score'] = [ref_aa_score]

    #         r['control_share'] = [sales_df[r['control']].sum(axis=1).sum()/sales_df.sum(axis=1).sum()]
    #         r['test_grps_share'] = [sales_df[r['test_%s' %_]].sum(axis=1).sum() for _ in range(n_test_grps)]/sales_df.sum(axis=1).sum()
    #         r['test_share'] = [sum(r['test_grps_share'])]
            
    #     # print(c,r)
    #     matched_market_pairs.append(r.copy()) 

        
    #     return matched_market_pairs[0]


    ## Creating single test group at a time with size constraints
    
    # def assign(
    #     self,
    #     panel_data: PanelDataset,
    #     treatment_period: Optional[TimePeriod] = None,
    #     pre_treatment_period: Optional[TimePeriod] = None,
    #     control_whitelist: Optional[List[Unit]] = [],
    #     test_whitelist: Optional[List[Unit]] = [],
    #     control_blacklist: Optional[List[Unit]] = [],
    #     test_blacklist: Optional[List[Unit]] = [],
    #     control_test_blacklist: Optional[List[Unit]] = [],
    #     samples: Optional[int] = 1) -> np.ndarray:
    #     """
    #     Assigns DMAs to test and control groups based on predefined rules and optimizations.
        
    #     Parameters
    #     ----------
    #     panel_data : PanelDataset
    #         The dataset with DMAs and corresponding time-series values.
    #     treatment_period : TimePeriod, optional
    #         The period in which the treatment is applied (default is the entire dataset time range).
    #     pre_treatment_period : TimePeriod, optional
    #         The period before treatment for reference or balancing.
    #     control_whitelist : list, optional
    #         List of DMAs that should always be included in the control group.
    #     test_whitelist : list, optional
    #         List of DMAs that should always be included in the test group.
    #     control_blacklist : list, optional
    #         List of DMAs to be excluded from the control group.
    #     test_blacklist : list, optional
    #         List of DMAs to be excluded from the test group.
    #     control_test_blacklist : list, optional
    #         List of DMAs to be excluded from both the test and control groups.
    #     samples : int, optional
    #         Number of iterations to run the optimization process. Default is 1.

    #     Returns
    #     -------
    #     np.ndarray :
    #         Updated panel dataset with the assigned test and control groups.
    #     """

    #     self.control_blacklist = control_blacklist
    #     self.control_whitelist = control_whitelist
    #     self.test_blacklist = test_blacklist
    #     self.test_whitelist = test_whitelist
    #     self.control_test_blacklist = control_test_blacklist
    #     self.samples = samples

    #     # Function to compute the correlation between control and test groups.
    #     def corr_func(df, x, y):
    #         return np.abs(np.corrcoef(df[x].sum(axis=1), df[y].sum(axis=1))[0][1])

    #     # Function to compute the dynamic time warping (DTW) distance between control and test groups.
    #     def dtw_distance(df, x, y):
    #         return round(dtw.distance(df[x].sum(axis=1).values, df[y].sum(axis=1).values))

    #     # Normalize each row of wide data
    #     panel_data.wide_data = panel_data.wide_data / np.max(np.linalg.norm(panel_data.wide_data.values, axis=1))
    #     data = panel_data.wide_data.reset_index().melt(id_vars=panel_data.wide_data.index.name)

    #     if treatment_period is None:
    #         treatment_period = TimePeriod(panel_data.wide_data.columns.min(), panel_data.wide_data.columns.max())

    #     # Prepare sales data and DMA list for optimization
    #     sales_df = panel_data.wide_data.T.copy()
    #     dma_list = sales_df.columns.tolist()
    #     matched_market_pairs = []

    #     # Handle blacklisted DMAs
    #     control_test_blacklist = control_test_blacklist + [dma for dma in [dma for dma in test_blacklist if dma in control_blacklist] if dma not in control_test_blacklist]
    #     if len(control_test_blacklist) > 0:
    #         dma_list = list(set(sales_df.columns) - set(control_test_blacklist))
    #         np.random.shuffle(dma_list)

    #     # Initialize test and control groups with whitelisted DMAs or random DMAs
    #     for _ in range(samples):
    #         r = {}
    #         # Control group initialization
    #         if len(control_whitelist) > 0:
    #             r['control'] = control_whitelist if len(control_whitelist) + len(control_blacklist) == len(panel_data.units) else [control_whitelist[0]]
    #             always_control = len(control_whitelist)
    #         else:
    #             control_list = list(set(dma_list) - set(control_blacklist + test_whitelist))
    #             np.random.shuffle(control_list)
    #             r['control'] = [control_list[0]]

    #         # Test group initialization
    #         test_list = list(set(dma_list) - set(test_blacklist + control_whitelist + r['control']))
    #         np.random.shuffle(test_list)

    #         if len(test_whitelist) > 0:
    #             r['test'] = test_whitelist if len(test_whitelist) + len(test_blacklist) == len(panel_data.units) else [(test_whitelist+test_list)[0]]
    #         else:
    #             r['test'] = [test_list[0]]

    #         # Initialize score and perform greedy optimization by augmenting groups with new DMAs
    #         if self.func_to_optimize == 'corr':
    #             ref_aa_score = corr_func(sales_df, r['control'], r['test'])
            
    #         if self.func_to_optimize == 'dtw':
    #             ref_aa_score = -dtw_distance(sales_df, r['control'], r['test'])

    #         if self.func_to_optimize == 'l2_imbalance':
    #             ref_aa_score = -imbalance(long_df_to_paneldataset(data[data[data.columns[0]].isin(r['control'] + r['test'])], data.columns[1], data.columns[0], data.columns[2], treated_units=r['test']))

    #         # Greedy optimization for new DMA/geo assignment
    #         np.random.shuffle(dma_list)
    #         for c in dma_list:
    #             if c not in list(set(chain(*list([r['control']] + [r['test']])))):
    #                 tracker = {'g_0' : None, 'g_1': None}

    #                 if self.split_type == 'kpi_share':
    #                     if sales_df[r['test'] + [c]].sum(axis=1).sum() * 100 / sales_df.sum(axis=1).sum() <= self.treatment_probability * 100:
    #                         pass
    #                     else:
    #                         break

    #                 if (control_whitelist is not None or test_blacklist is not None) and (c in control_whitelist or c in test_blacklist):
    #                     start = 0 
    #                     end = 1
                        
    #                 elif (test_whitelist is not None or control_blacklist is not None) and (c in test_whitelist or c in control_blacklist):
    #                     start = 1 
    #                     end = 2

    #                 elif (control_test_blacklist is not None) and (c in control_test_blacklist):
    #                     start = 0 
    #                     end = 0
                        
    #                 else:
    #                     start = 0
    #                     end = 2
                        
    #                 for pointer in range(start, end): 
    #                     ctrl = r['control'].copy()
    #                     g1 = [r['test'].copy()]
    #                     groups = [ctrl] + g1
    #                     groups[pointer].append(c)

    #                     scores = []
                        
    #                     if self.func_to_optimize == 'corr':
    #                         scores.append(abs(np.mean(np.array(corr_func(sales_df, groups[0], groups[1])))))

    #                     if self.func_to_optimize == 'dtw':
    #                         scores.append(-abs(np.mean(np.array(dtw_distance(sales_df, groups[0], groups[1])))))
                        
    #                     if self.func_to_optimize == 'imbalance':
    #                         scores.append(-abs(np.mean(np.array(imbalance(long_df_to_paneldataset(data[data[data.columns[0]].isin(groups[0] + groups[1])], time_column=data.columns[1], unit_column=data.columns[0], value_column=data.columns[2], treated_units=groups[1]))))))

    #                     avg_score = np.mean(scores)

    #                     if (avg_score > ref_aa_score):
    #                         tracker = {'g_0': groups[0], 'g_1': groups[1]}.copy()
    #                         ref_aa_score = avg_score 

    #                 if tracker['g_0'] is not None:
    #                     r['control'] = list(str(int(i)) if (type(i)==float or type(i)==int) else i for i in tracker['g_0'])
    #                     r['test'] = list(str(int(i)) if (type(i)==float or type(i)==int) else i for i in tracker['g_1'])
    #                     r['avg_score'] = [ref_aa_score]
                    
    #                     r['control_share'] = [sales_df[r['control']].sum(axis=1).sum() * 100 / sales_df.sum(axis=1).sum()]
    #                     r['test_share'] = [sales_df[r['test']].sum(axis=1).sum() * 100 / sales_df.sum(axis=1).sum()]

    #         matched_market_pairs.append(r.copy())

    #     # Create DataFrame to store matched pairs
    #     mm_test_grp_df = pd.DataFrame(matched_market_pairs)

    #     # Trim the panel dataset with the test and control geos identified above
    #     selected_geos = mm_test_grp_df.loc[0, 'control'] + mm_test_grp_df.loc[0, 'test']
    #     mm_trmd_data = data[data[data.columns[0]].isin(selected_geos)]

    #     # Create panel data with test geos
    #     panel_data = long_df_to_paneldataset(
    #         mm_trmd_data, 
    #         data.columns[1], 
    #         data.columns[0], 
    #         data.columns[2], 
    #         mm_test_grp_df.loc[0, 'test'],
    #         [treatment_period.start] * len(mm_test_grp_df.loc[0, 'test']),
    #         [treatment_period.end] * len(mm_test_grp_df.loc[0, 'test'])
    #     )

    #     # Fill any missing data with 0
    #     panel_data.wide_data = panel_data.wide_data.fillna(0)

    #     return panel_data

