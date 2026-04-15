import numpy as np
import pandas as pd
import random
from itertools import combinations
from scipy.spatial.distance import euclidean
from scipy.stats import pearsonr
from multiprocessing import Pool
from dtaidistance import dtw
from scipy.spatial.distance import cosine
from joblib import Parallel, delayed
from sklearn.cluster import KMeans
from tqdm import tqdm  # Import tqdm for progress bar
from pulp import LpProblem, LpVariable, lpSum, LpBinary, value


"""
The Supergeos concept refers to a procedure designed for the strategic grouping of geographic areas (like DMAs, Designated Market Areas) based on their characteristics (such as sales data), typically using clustering techniques. Here’s a summary of the Supergeos design procedure in steps:

1. Data Collection & Preprocessing
Collect the data: Gather sales data or other relevant metrics (e.g., geographic data) for the DMAs or regions over time.
Preprocess the data: Clean the data, handle missing values, normalize/standardize if necessary, and ensure it's ready for clustering.

2. Partitioning Heuristic (K-Means Clustering)
Apply K-Means clustering: Partition the DMAs into an initial set of clusters using a method like K-Means based on the sales patterns or other metrics.
The number of clusters (e.g., n_clusters=5) is predefined, and the DMAs are assigned to clusters that minimize intra-cluster variance.
Handle large clusters: If any cluster has too many DMAs, apply recursive clustering to subdivide it into smaller clusters until all clusters are within a desired size.

3. Supergeo Construction (Combinatorial Supergeo Generation)
Generate combinations: For each cluster, generate all possible combinations of DMAs (or a subset, based on minimum and maximum size constraints) that could form a supergeo (a group of DMAs).
Min & Max size: Define the minimum and maximum size constraints for these combinations to control the group size.

4. Supergeo Pairing (Per-Geo Heuristic)
Create supergeo pairs: Pair each generated supergeo with other supergeos to explore potential groupings based on their total sales or other similarity metrics.
Weight calculation: For each pair of supergeos, calculate a weight (distance or similarity) using metrics such as Euclidean distance, correlation, DTW, or cosine similarity, based on the total sales of each supergeo.

5. Objective Function & Optimization
Formulate the objective: Define an optimization problem where the objective is to minimize the total distance or dissimilarity between paired supergeos based on the calculated weights.
Binary decision variables: Create binary decision variables for each pair of supergeos, indicating whether a pair is selected.
Add constraints:
Ensure that each DMA is assigned to exactly one supergeo.
Supergeo size constraints (min/max).

6. Solving the Optimization Problem
Solve the optimization problem: Use a Mixed-Integer Linear Programming (MILP) solver (e.g., CBC or Gurobi) to determine the optimal pairing of supergeos that minimizes the overall objective function.

7. Result Analysis
Interpret the solution: Analyze the selected supergeo pairs based on the solver’s output. Gather the total sales or other relevant metrics for the selected supergeo pairs.
Output: Generate a DataFrame or other format to display the final selected supergeo pairs and their properties (e.g., total sales, weight).

8. Iterative Refinement (If Needed)
Refinement of clusters: If the generated supergeos do not meet desired characteristics (e.g., size balance, similarity), refine the process by adjusting cluster sizes, the number of clusters, or other constraints and rerun the optimization.
This structured procedure helps in creating optimized groupings (supergeos) that balance similarity in sales or other metrics while maintaining control over the size and composition of these groups.

"""


class SupergeoModel:
    """
    A class to model supergeographic clustering and pairing for sales data.

    Attributes:
    -----------
    panel_data : PanelDataset
        A panel dataset with DMAs as the index and time periods as columns.
    n_clusters : int
        Number of clusters for KMeans partitioning heuristic.
    weight_method : str
        Method to calculate the weight between supergeo pairs.

    Methods:
    --------
    run_model() :
        Executes the supergeo modeling procedure.
    """
    
    def __init__(self, panel_data: pd.DataFrame, n_clusters=5, weight_method='correlation'):
        """
        Initializes the SupergeoModel class.

        Parameters:
        -----------
        panel_data : pd.DataFrame
            Panel dataset with DMAs as index and time periods as columns.
        n_clusters : int, optional
            Number of clusters for KMeans partitioning heuristic. Default is 5.
        weight_method : str, optional
            Method to calculate the weight between supergeo pairs. Options: 'euclidean', 'correlation', 'dtw', 'cosine'.
        """
        self.panel_data = panel_data
        self.n_clusters = n_clusters
        self.weight_method = weight_method
        self.sales = panel_data.values
        self.dmas = panel_data.index.tolist()
        self.N, self.T = self.sales.shape  # N DMAs, T time periods
        self.supergeo_vars = {}
        self.pair_vars = {}
        self.created_pairs = set()
    
    def partitioning_heuristic(self):
        """
        Applies KMeans clustering to partition DMAs into clusters.

        Returns:
        --------
        dict
            A dictionary where keys are cluster indices and values are lists of DMAs assigned to each cluster.
        """
        kmeans_model = KMeans(n_clusters=self.n_clusters, n_init=10, random_state=0).fit(self.sales)
        clusters = kmeans_model.labels_

        cluster_dict = {}
        for city_index, cluster_index in enumerate(clusters):
            if cluster_index not in cluster_dict:
                cluster_dict[cluster_index] = []
            cluster_dict[cluster_index].append(city_index)

        return cluster_dict

    def per_geo_heuristic(self, supergeo_combos):
        """
        Calculates the weight for each supergeo pair and sorts the pairs by weight.

        Parameters:
        -----------
        supergeo_combos : list
            List of supergeo combinations.

        Returns:
        --------
        list
            List of tuples, where each tuple contains a pair of supergeos and their calculated weight.
        """
        scale = 1000
        pairs_with_weights = []
        for i, supergeo1 in enumerate(supergeo_combos):
            for j, supergeo2 in enumerate(supergeo_combos):
                if i < j:
                    weight = self.calculate_weight(supergeo1, supergeo2) * scale
                    if weight is not None:
                        pairs_with_weights.append(((supergeo1, supergeo2), weight))

        pairs_with_weights.sort(key=lambda x: x[1])
        return pairs_with_weights

    def find_largest_cluster(self, clusters):
        """
        Recursively finds the largest cluster among the given clusters.

        Parameters:
        -----------
        clusters : dict
            Dictionary of clusters, where values can be lists or nested dictionaries.

        Returns:
        --------
        list
            The largest cluster found.
        """
        largest_cluster = None
        largest_size = 0

        for cluster_data in clusters.values():
            if isinstance(cluster_data, dict):
                _, sub_cluster = self.find_largest_cluster(cluster_data)
                cluster_size = len(sub_cluster)
            else:
                cluster_size = len(cluster_data)
                sub_cluster = cluster_data

            if cluster_size > largest_size:
                largest_size = cluster_size
                largest_cluster = sub_cluster

        return largest_cluster

    def calculate_min_max_sizes(self, total_elements, min_fraction=0.1, max_fraction=0.5):
        """
        Calculates the minimum and maximum sizes for generating supergeo combinations based on the total number of elements.

        Parameters:
        -----------
        total_elements : int
            Total number of elements in the cluster.
        min_fraction : float, optional
            Fraction of total elements for minimum size.
        max_fraction : float, optional
            Fraction of total elements for maximum size.

        Returns:
        --------
        tuple
            Minimum and maximum sizes for supergeo combinations.
        """
        min_size = max(1, int(total_elements * min_fraction))
        max_size = max(min_size, int(total_elements * max_fraction))
        return min_size, max_size

    def generate_combinations(self, cities, min_size, max_size, seed=None):
        """
        Lazily generates combinations of cities (DMAs) of sizes between min_size and max_size.

        Parameters:
        -----------
        cities : list
            List of DMAs.
        min_size : int
            Minimum size of the combinations.
        max_size : int
            Maximum size of the combinations.
        seed : int, optional
            Random seed for shuffling cities before combination generation.

        Yields:
        -------
        tuple
            A combination of DMAs.
        """
        if seed is not None:
            random.seed(seed)
        for size in range(min_size, max_size + 1):
            random.shuffle(cities)
            for combo in combinations(cities, size):
                yield combo

    def create_supergeo_pairs(self, combinations_generator):
        """
        Lazily generates pairs of supergeo combinations.

        Parameters:
        -----------
        combinations_generator : generator
            A generator that yields supergeo combinations.

        Yields:
        -------
        tuple
            A pair of supergeo combinations.
        """
        for i, combo1 in enumerate(combinations_generator):
            for j, combo2 in enumerate(combinations_generator):
                if i < j:
                    yield combo1, combo2

    def total_sales_for_supergeo(self, combo):
        """
        Calculates the total sales over time for a given supergeo.

        Parameters:
        -----------
        combo : tuple
            A combination of DMAs representing a supergeo.

        Returns:
        --------
        array
            Array of total sales across all time periods for the supergeo.
        """
        return np.sum(self.sales[list(combo)], axis=0)

    def calculate_weight(self, supergeo1, supergeo2):
        """
        Calculates the weight (distance) between two supergeo combinations using the specified method.

        Parameters:
        -----------
        supergeo1 : tuple
            First supergeo combination.
        supergeo2 : tuple
            Second supergeo combination.

        Returns:
        --------
        float
            The calculated weight between the two supergeos.
        """
        total_sales1 = self.total_sales_for_supergeo(supergeo1)
        total_sales2 = self.total_sales_for_supergeo(supergeo2)
        
        try:
            if self.weight_method == 'euclidean':
                return abs(euclidean(total_sales1, total_sales2))
            elif self.weight_method == 'correlation':
                return max(0, 1 - pearsonr(total_sales1, total_sales2)[0])
            elif self.weight_method == 'dtw':
                return dtw.distance(total_sales1, total_sales2)
            elif self.weight_method == 'cosine':
                return abs(cosine(total_sales1, total_sales2))
            else:
                raise ValueError("Unknown method.")
        except Exception as e:
            print(f"Error calculating weight for {supergeo1}, {supergeo2}: {e}")
            return np.inf

    def process_pairs(self, pair_generator):
        """
        Processes supergeo pairs and calculates their weights lazily.

        Parameters:
        -----------
        pair_generator : generator
            Generator yielding pairs of supergeo combinations.

        Yields:
        -------
        tuple
            A pair of supergeos and their calculated weight.
        """
        for supergeo1, supergeo2 in pair_generator:
            weight = self.calculate_weight(supergeo1, supergeo2)
            if weight is not None:
                yield (supergeo1, supergeo2), weight
            else:
                print(f"Skipping pair: ({supergeo1}, {supergeo2}) due to None weight")
                yield (supergeo1, supergeo2), float('inf')

    def run_design(self):
        """
        Executes the supergeo modeling procedure and solves the optimization problem.

        Returns:
        --------
        pd.DataFrame
            DataFrame containing the results with selected supergeo pairs and their total sales.
        """
        # Start of the main function logic
        clusters = self.partitioning_heuristic()
        largest_cluster_elements = self.find_largest_cluster(clusters)
        total_elements = len(largest_cluster_elements)

        print(f'elements in the cluster: {largest_cluster_elements}')

        min_size, max_size = self.calculate_min_max_sizes(total_elements, min_fraction=0.1, max_fraction=0.5)
        min_size, max_size = 2, 5
        
        supergeo_combinations_generator = self.generate_combinations(largest_cluster_elements, min_size, max_size, seed=42)

        # Generate supergeo combinations, pairs and store them
        supergeo_combos = list(supergeo_combinations_generator)
        sorted_supergeo_pairs = self.per_geo_heuristic(supergeo_combos)

        print(f'min: {min_size}, max: {max_size}')
        print(f"len of supergeo_combos {len(supergeo_combos)}, len of pairs {len(sorted_supergeo_pairs)}")
        print(f'combos: {supergeo_combos[:5]}, pairs: {sorted_supergeo_pairs[:5]}')

        # Initialize PuLP problem
        problem = LpProblem("Supergeo_With_Weights_Generator", LpMinimize)

        # Create binary decision variables for pairs on-the-fly
        pair_vars = {}
        objective_terms = []

        # Process sorted pairs
        for (supergeo1, supergeo2), weight in sorted_supergeo_pairs:
            # Only create pair_vars if the weight is valid
            if weight is not None:
                pair_var = LpVariable(f"pair_{supergeo1}_{supergeo2}", cat=LpBinary)
                pair_vars[(supergeo1, supergeo2)] = pair_var

                # Add to the objective function dynamically
                if pair_var is not None:
                    term = pair_var * weight * lpSum(
                        (self.total_sales_for_supergeo(supergeo1)[t] - self.total_sales_for_supergeo(supergeo2)[t]) ** 2
                        for t in range(self.T))
                    objective_terms.append(term)
                else:
                    print(f"Skipping pair: ({supergeo1}, {supergeo2}) due to None pair_var")
            else:
                print(f"Skipping pair: ({supergeo1}, {supergeo2}) due to None weight")
        
        # Set the objective function once after accumulating all terms
        problem += lpSum(objective_terms)

        # Create binary decision variables for supergeos
        for combo in supergeo_combos:
            self.supergeo_vars[combo] = LpVariable(f"supergeo_{combo}", cat=LpBinary)

        # Constraints: Ensure each city is assigned to exactly one supergeo
        for city in range(self.N):
            problem += lpSum(self.supergeo_vars[combo] for combo in supergeo_combos if city in combo) == 1

        # Solve the problem
        problem.solve()

        # Gather results into a DataFrame
        result_data = []
        for (supergeo1, supergeo2) in pair_vars.keys():
            print(f'supergeos: {(supergeo1, supergeo2)}, pair vars: {value(pair_vars[(supergeo1, supergeo2)])}')
            if value(pair_vars[(supergeo1, supergeo2)]) > 0.5:  # If the pair is selected
                total_sales_1 = self.total_sales_for_supergeo(supergeo1)
                total_sales_2 = self.total_sales_for_supergeo(supergeo2)
                result_data.append({
                    'Supergeo_1': supergeo1,
                    'Supergeo_2': supergeo2,
                    'Total_Sales_1': total_sales_1.tolist(),
                    'Total_Sales_2': total_sales_2.tolist()
                })

        result_df = pd.DataFrame(result_data)
        return result_df



