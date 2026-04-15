import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.model_selection import train_test_split
from scipy import stats
import random
import matplotlib.pyplot as plt
import seaborn as sns

class TrimmedMatchDesign:

    """
    Initializes the TrimmedMatchDesign class.

    **Trimmed Matching Design Concept:**

    -  Split the pretest time period into two non-overlapping periods: a time period for geo pairing (Tp) and an evaluation time period for power analysis (Te). 
    -  For each n (pairs) ≤ N/2, use data during Tp to generate the optimal subset of n geo pairs from N geos. As a rule of thumb, we recommend n ≥ 10 as too few pairs may make the inference unreliable. 
    -  For each n and the optimal subset of n pairs obtained in the previous step, use data during Te to perform power analysis. 
    -  For each candidate set of geo pairs, randomize geo assignment within each pair, and adjust random imbalance through rerandomization. 
    -  Finally, choose the design which has small enough RMSE or Imbalance according to the configuration for testing. Here additional marketing constraints may apply, e.g. avoiding diminishing returns if too much ad spend, limited ad inventory, etc.

    Parameters
    ----------
    panel_dataset : Panel Dataset
        Panel dataset containing geos as the index and time periods as columns. 
        Values represent sales or conversion metrics.
    n_test_groups : int
        Number of test groups to create.        
    spend_data : DataFrame, optional
        Ad spend data with geos as the index and time periods as columns.
    max_pairs : int, optional
        Maximum number of pairs to create. Defaults to N/2 if None.
    min_pairs : int, optional
        Minimum number of pairs for reliable inference (default: 10).
    response_threshold : float, optional
        Threshold for response balance across groups.
    num_simulations : int, optional
        Number of simulations for robust power analysis (default: 1000).
    trim_rate : float, optional
        Proportion of pairs to trim from the response differences' extremes. Defaults to 0.1.
    iROAS_true : float, optional
        The assumed incremental Return on Ad Spend (iROAS) value for validation. Defaults to 0.2.
    expected_lift : float, optional
        Expected response lift for power analysis. Defaults to 0.3.
    test_size : float, optional
        Fraction of data to use for the evaluation period (Te). Defaults to 0.3.
    imbalance_metric : str, optional
        Metric for imbalance calculation ('l2' for MSE, 'l1' for MAE, 'l_inf' for max error). Defaults to l2.
    confidence_level : float, optional
        Desired confidence level for power analysis (e.g., 0.95 for 95%). Defaults to 0.95.
    pairing_method : str, optional
        Method for pairing geos, either 'distance' (Euclidean) or 'correlation'. Defaults to distance.

    """

    def __init__(self, panel_dataset, n_test_groups=1, spend_data=None, max_pairs=None, min_pairs=10, 
                 response_threshold=0.1, num_simulations=1000, trim_rate=0.1, iROAS_true=0.2, expected_lift=0.3, test_size=0.3, imbalance_metric ='l2', confidence_level=0.95, pairing_method = 'distance'):
        self.panel_dataset = panel_dataset
        self.n_test_groups = n_test_groups        
        self.spend_data = spend_data
        self.max_pairs = max_pairs if max_pairs is not None else len(panel_dataset.wide_data) // 2
        self.min_pairs = min_pairs
        self.response_threshold = response_threshold
        self.num_simulations = num_simulations
        self.trim_rate = trim_rate
        self.iROAS_true = iROAS_true
        self.expected_lift = expected_lift
        self.test_size = test_size
        self.imbalance_metric = imbalance_metric
        self.confidence_level = confidence_level
        self.pairing_method = pairing_method

    def run_design(self, use_imbalance=True):
        """
        Executes the trimmed match design procedure.

        Parameters
        ----------
        use_imbalance : bool
            Whether to use total imbalance for selecting the final design. Default is True.

        Returns
        -------
        best_design : dict
            Dictionary containing the best design based on the selected metric.
        power_results : list
            List of power analysis results for each tested design.
        """
        # Step 1: Split the data into Tp (pairing) and Te (evaluation)
        self.panel_data = self.panel_dataset.wide_data
        n = self.panel_data.shape[1]  # Number of time periods
        self.Tp_data = self.panel_data.iloc[:, :int(n * (1 - self.test_size))]  # Pairing period
        self.Te_data = self.panel_data.iloc[:, int(n * (1 - self.test_size)):]  # Evaluation period

        # Step 2: Calculate responses for training and evaluation periods
        training_responses = self.Tp_data.sum(axis=1)  # Total response for each geo in the training period
        evaluation_responses = self.Te_data.sum(axis=1)  # Total response for each geo in the evaluation period

        if self.spend_data is not None:
            self.Tp_spend = self.spend_data.iloc[:, :int(n * (1 - self.test_size))]
            self.Te_spend = self.spend_data.iloc[:, int(n * (1 - self.test_size)):]
        else:
            self.Tp_spend = None
            self.Te_spend = None

        # Prepare geos and results
        geos = self.panel_data.index.tolist()
        power_results = []  # List to collect results from each iteration

        # Step 3: Generate optimal pairs and evaluate each configuration
        for pair in range(self.min_pairs, self.max_pairs + 1):
            geo_pairs = self.generate_optimal_pairs(self.Tp_data, pair)
            print(f"Number of geo_pairs: {len(geo_pairs)}")

            # Calculate response differences and trim pairs based on distribution tails
            response_differences = [abs(training_responses[geo1] - training_responses[geo2]) for geo1, geo2 in geo_pairs]

            # Step 4: Trim pairs based on response differences
            trimmed_pairs = self.calculate_trimmed_pairs(geo_pairs, response_differences, distribution_based = True)
            print(f"Number of trimmed pairs: {len(trimmed_pairs)}")

            # Step 5: Rerandomize geo assignments into test/control groups
            test_group_assignments, control_group, power_analysis_results, total_imbalance = self.rerandomize_and_check(
                geo_pairs, trimmed_pairs, self.Tp_data, self.spend_data)

            # Collect results for comparison
            power_results.append({
                'geo_pairs': geo_pairs,
                'test_groups': test_group_assignments,
                'control_group': control_group,
                'power_results': power_analysis_results,
                'total_imbalance': total_imbalance
            })

        # Step 6: Loop through all collected results and pick the best one based on the selected metric
        best_score = float('inf')
        best_design = None

        for result in power_results:
            # Loop over power_results within each iteration result
            for group_id, power_result in result['power_results'].items():
                score = result['total_imbalance'] if use_imbalance else power_result.get('avg_rmse')

                if score is not None and score < best_score:
                    best_score = score
                    best_design = {
                        "geo_pairs": result['geo_pairs'],
                        "test_groups": result['test_groups'],
                        "control_group": result['control_group'],
                        "metric": "total_imbalance" if use_imbalance else "avg_rmse",
                        "score": score,
                        "power": power_result['power']
                    }

        # Return the best design based on chosen metric
        return best_design, power_results



    def generate_optimal_pairs(self, data, num_pairs):
        """
        Generate optimal geo pairs based on response data.

        Parameters
        ----------
        data : DataFrame
            DataFrame containing geos as the index and time periods as columns.
        num_pairs : int
            Number of pairs to generate.

        Returns
        -------
        geo_pairs : list of tuples
            List of tuples representing paired geos.
        """
        # Ensure there are enough unique geos to create pairs
        num_geos = data.shape[0]
        if num_geos < 2:
            print("Not enough geos to form pairs.")
            return []
        
        def calculate_correlation(geo1_data, geo2_data):
            return np.corrcoef(geo1_data, geo2_data)[0, 1]  # Correlation between two geos

        if self.pairing_method == 'distance':
            # Calculate pairwise distances based on the response metrics
            distance_matrix = np.zeros((num_geos, num_geos))
            for i in range(num_geos):
                for j in range(i + 1, num_geos):
                    distance_matrix[i, j] = np.linalg.norm(data.iloc[i] - data.iloc[j])
                    distance_matrix[j, i] = distance_matrix[i, j]

            np.fill_diagonal(distance_matrix, np.inf)  # Set self-distance to infinity
            sum_assignment_matrix = distance_matrix


        if self.pairing_method == 'correlation':
            # Calculate correlation matrix based on response metrics
            correlation_matrix = np.zeros((num_geos, num_geos))
            for i in range(num_geos):
                for j in range(i + 1, num_geos):
                    correlation_matrix[i, j] = calculate_correlation(data.iloc[i], data.iloc[j])
                    correlation_matrix[j, i] = correlation_matrix[i, j]

            # Convert the correlation to a distance-like metric (higher values are more similar)
            correlation_matrix = 1 - np.abs(correlation_matrix)

            np.fill_diagonal(correlation_matrix, np.inf)  # Avoid self-pairing by setting diagonal to infinity
            sum_assignment_matrix = correlation_matrix

        # Use linear sum assignment to find the optimal pairs based on the distance matrix
        row_ind, col_ind = linear_sum_assignment(sum_assignment_matrix)

        # Create geo_pairs ensuring that we do not generate pairs with the same elements
        geo_pairs = []
        unique_pairs = set()  # To track unique pairs as tuples

        for i in range(len(row_ind)):
            if row_ind[i] != col_ind[i]:  # Ensure different geos
                geo1 = data.index[row_ind[i]]
                geo2 = data.index[col_ind[i]]
                # Sort the pair to avoid (a,b) and (b,a)
                pair = tuple(sorted((geo1, geo2)))

                # Add to the list if it's a unique pair
                if pair not in unique_pairs:
                    geo_pairs.append(pair)
                    unique_pairs.add(pair)

            # Stop if we have enough pairs
            if len(geo_pairs) >= num_pairs:
                break

        return geo_pairs


    def calculate_trimmed_pairs(self, geo_pairs, response_differences, distribution_based=False):
        """
        Calculate trimmed pairs based on response differences.

        Parameters
        ----------
        geo_pairs : list of tuples
            List of tuples representing paired geos.
        response_differences : list
            List of response differences for each geo pair.
        trim_rate : float
            The proportion of pairs to trim from the top and bottom of the response differences.
        distribution_based : bool, optional
            If True, trims pairs based on distribution tails instead of a fixed rate. Default is False.

        Returns
        -------
        trimmed_pairs : list
            Trimmed geo pairs.
        """
        num_pairs = len(response_differences)

        if distribution_based:
            # Calculate thresholds based on distribution (e.g., removing values in the top and bottom quantiles)
            lower_threshold = np.percentile(response_differences, self.trim_rate * 100 / 2)
            upper_threshold = np.percentile(response_differences, 100 - (self.trim_rate * 100 / 2))

            # Select pairs within the defined range
            trimmed_indices = [i for i, diff in enumerate(response_differences) if lower_threshold <= diff <= upper_threshold]
        
        else:
            # Standard trimming by percentage
            trim_threshold = int(num_pairs * self.trim_rate)
            sorted_indices = np.argsort(response_differences)
            
            # Trim the top and bottom response differences
            trimmed_indices = sorted_indices[trim_threshold:num_pairs - trim_threshold]

        # Return the trimmed pairs
        trimmed_pairs = [geo_pairs[i] for i in trimmed_indices]
        return trimmed_pairs



    def rerandomize_and_check(self, geo_pairs, trimmed_pairs, responses, spend_data=None):
        """
        Rerandomize geos into multiple test groups and one control group,
        and check for imbalance in both response and spend metrics.

        Parameters
        ----------
        geo_pairs : list
            List of paired geos.
        trimmed_pairs : list
            Indices of the trimmed geo pairs.
        responses : DataFrame
            Dataframe containing geos as index and time periods as columns.
        spend_data : Series, optional
            Dataframe containing geos as index and time periods as columns.

        Returns
        -------
        test_group_assignments : dict
            Dictionary mapping test group number to geos assigned to that group.
        control_group : list
            Geos assigned to the control group.
        power_analysis_results : dict
            Power analysis results for each test group.
        """
        
        def imbalance(test_group_assignments, control_group) -> float:
            """
            Calculate the imbalance of the proposed design.
            Options are:
                "l2" for mean squared error
                "l1" for mean absolute error
                "l_inf" for the the L_infinity norm
            """
            imbalance_measures = {}
            control_mean = self.Tp_data.loc[control_group].mean(0)
            test_means = {i: self.Tp_data.loc[group].mean(0) for i, group in test_group_assignments.items()}

            for i,test_mean in test_means.items():

                if self.imbalance_metric == "l2":
                    imbalance = np.mean(np.square(control_mean - test_mean))
                elif self.imbalance_metric == "l1":
                    imbalance =  np.mean(np.abs(control_mean - test_mean))
                elif self.imbalance_metric == "l_inf":
                    imbalance =  np.max(np.abs(control_mean - test_mean))
                else:
                    raise NotImplemented(f"{self.imbalance_metric} is not an implemented imbalance metric")
                
                imbalance_measures[i] = imbalance

            return imbalance_measures
        
        def test_grp_weights(test_group_assignments) -> float:
            test_responses = {i: self.Tp_data.loc[group].sum().sum() for i, group in test_group_assignments.items()}
            total_test_response = sum(test_responses.values())

            weights = {i: test_response / total_test_response for i, test_response in test_responses.items()}

            return weights

        total_imbalance_score = np.inf

        for _ in range(100):

            # Step 1: Initialize test groups and control group
            test_group_assignments = {i: [] for i in range(1, self.n_test_groups + 1)}
            control_group = []

            group_responses = {i: 0 for i in range(1, self.n_test_groups + 1)}
            control_response = 0

            # Step 2: Randomly assign one geo from each pair to a test group and the other to the control group
            total_response = sum(responses.loc[geo1].sum() + responses.loc[geo2].sum() for geo1, geo2 in trimmed_pairs)
            # max_response_per_group = (total_response / (self.n_test_groups + 1)) * (1 + self.response_threshold)  # Allowable response per group
            max_response_per_group = total_response

            for geo1, geo2 in trimmed_pairs:
                geo1_response = responses.loc[geo1].sum()  # Total response for geo1
                geo2_response = responses.loc[geo2].sum()  # Total response for geo2

                # Randomly assign one geo to a test group and the other to the control group
                if np.random.rand() > 0.5:
                    assigned_geo = geo1
                    other_geo = geo2
                else:
                    assigned_geo = geo2
                    other_geo = geo1

                # Shuffle test group indices to randomize the assignment order
                test_groups = list(range(1, self.n_test_groups + 1))
                random.shuffle(test_groups)  # Randomize the test group assignment order

                test_group_assigned = False
                
                # Iterate through the randomly shuffled test groups to find one to assign
                for i in test_groups:
                    if group_responses[i] + geo1_response <= max_response_per_group:
                        test_group_assignments[i].append(assigned_geo)
                        control_group.append(other_geo)
                        group_responses[i] += geo1_response
                        control_response += geo2_response
                        test_group_assigned = True
                        break

                if not test_group_assigned:
                    # If test group limit is reached, randomly assign to any test group
                    random_test_group = np.random.choice(list(test_group_assignments.keys()))
                    test_group_assignments[random_test_group].append(assigned_geo)
                    control_group.append(other_geo)
                    group_responses[random_test_group] += geo1_response
                    control_response += geo2_response

            imbalance_scores = imbalance(test_group_assignments, control_group)
            weights = test_grp_weights(test_group_assignments)

            total_imbalance = sum(weights[i] * imbalance_score for i, imbalance_score in imbalance_scores.items())

            if total_imbalance < total_imbalance_score:
                best_test_group_assignment = test_group_assignments.copy()
                best_control_group_assignment = control_group.copy()
                total_imbalance_score = total_imbalance

                # print(f'chosen design len: {len(trimmed_pairs)}')
                # print(f'len of test: {sum(len(value) for value in best_test_group_assignment.values())}, len of control: {len(best_control_group_assignment)}'

        # Step 4: Perform power analysis for each test group separately
        power_results = {}
        for group_id, test_group in best_test_group_assignment.items():
            geo_pairs_for_test_group = [(geo1, geo2) for geo1, geo2 in geo_pairs if geo1 in test_group or geo2 in test_group]

            # Run power analysis for the current test group
            power_result = self.power_analysis_with_cross_validation(geo_pairs_for_test_group)
            power_results[f'Test Group {group_id}'] = power_result

        return best_test_group_assignment, best_control_group_assignment, power_results, total_imbalance





    def power_analysis_with_cross_validation(self, geo_pairs_for_test_group):
        """
        Perform power analysis using cross-validation for each test and control group combination.

        Parameters
        ----------
        geo_pairs_for_test_group : list of tuples
            List of geo pairs used for the experiment.

        Returns
        -------
        power_result : dict
            Dictionary containing power analysis results, including RMSE and power estimate.
        """

        rmse_list = []
        response_lift_estimates = []  # List to store response lift estimates across simulations

        # Run simulations for power analysis
        for _ in range(self.num_simulations):
            # Randomly assign one geo from each pair to treatment and the other to control
            assignments = []
            for geo1, geo2 in geo_pairs_for_test_group:
                if np.random.rand() > 0.5:
                    assignments.append((geo1, geo2, 'control', 'treatment'))
                else:
                    assignments.append((geo1, geo2, 'treatment', 'control'))

            # Calculate treatment and control group responses during Te
            treatment_responses = []
            control_responses = []
            treatment_spend = []
            control_spend = []

            for geo1, geo2, group1, group2 in assignments:
                if group1 == 'treatment':
                    treatment_responses.append(self.Te_data.loc[geo1].sum())
                    control_responses.append(self.Te_data.loc[geo2].sum())
                    if self.spend_data is not None:
                        treatment_spend.append(self.Te_spend.loc[geo1].sum())
                        control_spend.append(self.Te_spend.loc[geo2].sum())
                else:
                    treatment_responses.append(self.Te_data.loc[geo2].sum())
                    control_responses.append(self.Te_data.loc[geo1].sum())
                    if self.spend_data is not None:
                        treatment_spend.append(self.Te_spend.loc[geo2].sum())
                        control_spend.append(self.Te_spend.loc[geo1].sum())

            # Case 1: Spend data is available, calculate iROAS
            if self.spend_data is not None:
                iROAS_estimated = (np.sum(treatment_responses) - np.sum(control_responses)) / np.sum(treatment_spend)
                
                # Calculate the RMSE (Root Mean Square Error)
                rmse = np.sqrt((iROAS_estimated - self.iROAS_true) ** 2)
                rmse_list.append(rmse)

            # Case 2: Spend data is not available, calculate response lift and power based on MDL
            else:
                control_sum = np.sum(control_responses)
                if control_sum < 1e-5:  # Prevent division by near-zero values
                    control_sum = 1e-5
                response_lift_estimated = (np.sum(treatment_responses) - np.sum(control_responses)) / control_sum

                response_lift_estimates.append(response_lift_estimated)  # Store the estimate across simulations

                # Calculate RMSE for response lift based on expected lift
                rmse = np.sqrt((response_lift_estimated - self.expected_lift) ** 2)
                rmse_list.append(rmse)
        
        # Calculate standard deviation of response lift estimates across simulations
        response_lift_std = np.std(response_lift_estimates)

        # Perform power analysis based on the minimum detectable lift (MDL)
        z = stats.norm.ppf(1 - (1 - self.confidence_level) / 2)  # Z-score for confidence level (e.g., 1.96 for 95%)
        standard_errors = [response_lift_std / np.sqrt(len(geo_pairs_for_test_group))] * self.num_simulations

        # Confidence intervals for each simulation
        ci_lower_bounds = [response_lift - z * se for response_lift, se in zip(response_lift_estimates, standard_errors)]
        ci_upper_bounds = [response_lift + z * se for response_lift, se in zip(response_lift_estimates, standard_errors)]

        # Power is how often the lower bound of the confidence interval exceeds MDL
        # print(f'expected lift: {self.expected_lift}')
        # power = np.mean([1 if ci_lower >= self.expected_lift or ci_lower <= -self.expected_lift else 0 for ci_lower in ci_lower_bounds])

        # Power is calculated as the proportion of simulations where the confidence interval 
        # either exceeds the expected lift (positive effect) or falls below the negative expected lift 
        # (negative effect), indicating a statistically detectable effect in either direction.
        power = np.mean([1 if ci_lower >= self.expected_lift or ci_upper <= -self.expected_lift else 0 for ci_lower, ci_upper in zip(ci_lower_bounds, ci_upper_bounds)])


        # Average RMSE over all simulations
        avg_rmse = np.mean(rmse_list)

        # Power calculation when spend data is available (using iROAS)
        if self.spend_data is not None:
            power = np.mean([1 if abs(iROAS_estimated) >= self.iROAS_true else 0 for iROAS_estimated in rmse_list])

        power_result = {'avg_rmse': avg_rmse, 'power': power}

        return power_result


    def plot_performance_metrics(self, power_results):
        """
        Plots performance metrics like RMSE, power, and imbalance for each test group.

        Parameters
        ----------
        power_results : dict
            Dictionary output from run_design containing power analysis results for each test group, including RMSE, power, and imbalance.

        """
        # Function to extract and append power results from all dicts in the list
        def append_power_results_from_list(data_list):
            extracted_data = {}
            for entry in data_list:
                power_results = entry.get('power_results', {})
                for test_group, results in power_results.items():
                    if test_group not in extracted_data:
                        extracted_data[test_group] = {'avg_rmse': [], 'power': [], 'imbalance': []}
                    # Append new values to the lists
                    extracted_data[test_group]['avg_rmse'].append(results['avg_rmse'])
                    extracted_data[test_group]['power'].append(results['power'])
                    extracted_data[test_group]['imbalance'].append(entry.get('total_imbalance', 0))
            return extracted_data

        # Extract the data from multiple dicts, appending the results
        extracted_results = append_power_results_from_list(power_results)

        # Extract data for plotting
        groups = []
        rmse_values = []
        power_values = []
        imbalance_values = []
        
        for group, metrics in extracted_results.items():
            groups.append(group)
            rmse_values.append(metrics['avg_rmse'])
            power_values.append(metrics['power'])
            imbalance_values.append(metrics['imbalance'])

        # Number of test groups
        num_groups = len(groups)

        # Create subplots dynamically based on the number of test groups, with three charts per group
        fig, axs = plt.subplots(num_groups, 3, figsize=(15, 5))

        # If only one test group, axs will not be a list of lists, so we wrap it in a list
        if num_groups == 1:
            axs = [axs]

        # Loop through each test group and plot the corresponding data
        for i, group in enumerate(groups):
            sns.kdeplot(rmse_values[i], label=f'{group} - RMSE', ax=axs[i][0])
            sns.kdeplot(power_values[i], label=f'{group} - Power', linestyle='--', ax=axs[i][1])
            sns.kdeplot(imbalance_values[i], label=f'{group} - Imbalance', linestyle='-.', ax=axs[i][2])
            
            axs[i][0].set_title(f'{group}: RMSE Distribution')
            axs[i][0].legend()
            axs[i][1].set_title(f'{group}: Power Distribution')
            axs[i][1].legend()
            axs[i][2].set_title(f'{group}: Imbalance Distribution')
            axs[i][2].legend()

        plt.tight_layout()  # Adjust layout to prevent overlap
        plt.show()




