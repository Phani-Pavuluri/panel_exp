import networkx as nx
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.linalg import pinv
from scipy import sparse
from .assign import Design


import warnings

warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")


class MatchedPair(Design):
    """
    Design Class corresponding to the Matched Pair Experimental Design

    
    Attributes
    ----------
    X : array-like, shape (n_samples, n_features)

    blocks : list of lists
        List of matched pairs of units
    
    L : sparse matrix corresponding to the adjacency matrix of the graph of matched pairs
    
    Methods
    -------
    fit(X)
        Fit the design to the data X

    assign(X)
        Assign treatment to the units in X after fitting the design to the data X

    matching_design_k
        Obtain a matching design for the given panel_data object with at most k other units for the given time period
    """
    def fit(self, X):
        """
        Fit the design to the data X

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The data to fit the design to and assigns it into matched pairs in self.blocks and the adjacency matrix in self.L
        
        Returns
        -------
        None
        """
        self.X = X
        s = pinv(np.cov(X, rowvar=0))
        n = len(X)
        n2 = n / 2
        D = squareform(pdist(X, "mahalanobis", VI=s))
        self.blocks = [
            [a, b] for a, b in nx.matching.max_weight_matching(nx.Graph(-D), True)
        ]
        self.L = np.zeros(D.shape)
        for left, right in self.blocks:
            self.L[left, right] = 1
            self.L[right, left] = 1
        self.L = sparse.csr_matrix(self.L)

    def assign(self, X):
        """
        Create an assignment matrix A corresponding to the fit of the design to the data X

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The data to assign treatment to
        
        
        Returns
        -------
        A : array-like, shape (n_samples,)
            The assignment matrix corresponding to the treatment assignment of the units in X
        """
        if X is None:
            X = self.X
        elif X is self.X:
            pass
        else:
            raise ValueError("Can't go out of sample here.")
        N = X.shape[0]
        A = np.array([0] * N)
        for block in self.blocks:
            M = len(block)
            En_trt = M / 2
            n_trt = int(max(1, np.floor(En_trt)))
            n_ctl = int(max(1, np.floor(M - En_trt)))
            n_extra = int(np.floor(M - n_trt - n_ctl))
            a_extra = int(np.random.choice([0, 1], 1)[0])
            n_trt += a_extra * n_extra
            trted = np.random.choice(M, n_trt, replace=False)
            for unit in trted:
                A[block[unit]] = 1
        return A
    
    def sum_max_k(self, v, available_vertices, k):
        """
        Obtain the sum of the k maximum elements in v among the available vertices and the k maximum elements in v

        Parameters
        ----------
        v : array-like
            The array for which to obtain the sum of the k maximum elements
        
        available_vertices : set
            The set of available vertices

        k : int
            The number of maximum elements to sum

        Returns
        -------
        sum_max_k : float
            The sum of the k maximum elements in v among the available vertices

        indices : array-like
            The k maximum elements in v
        """

        v = np.array(v)
        
        # replace the values of v that are not in available_vertices with -inf
        for i in range(len(v)):
            if i not in available_vertices:
                v[i] = -np.inf
        
        if len(available_vertices) >= k:
            return np.sum(np.sort(v)[-k:]), np.argsort(v)[-k:]
        else:
            return np.sum(np.sort(v)[-len(available_vertices):]), np.argsort(v)[-len(available_vertices):]


    # the matching design is a function that takes as input a panel_data object
    # and returns a matched treatment assignment of a unit to at most k other units for the given time period
    def matching_design_k(self, panel_data, k=1):
        """
        Obtain a matching design for the given panel_data object with at most k other units for the given time period
        
        Parameters
        ----------
        panel_data : PanelData
            The panel data object for which to obtain the matching design
        
        k : int, optional
            The maximum number of units to match to for each unit
        
        Returns
        -------
        matching : dict
            A dictionary containing the matched pairs of units
        
        """

        # access the wide data frame from panel_data
        df = panel_data.wide_df
        nunits = df.shape[0]
        ntime = df.shape[1]

        covariate_matrix = panel_data.wide_data.values

        # obtain a similarity matrix ffrom covariate_matrix by taking pairwise l2 distances between rows of covariate_matrix
        similarity_matrix = np.zeros((nunits, nunits))
        for i in range(nunits):
            for j in range(nunits):
                similarity_matrix[i, j] = np.linalg.norm(covariate_matrix[i, :] - covariate_matrix[j, :])
        
        # obtain a greedy matching by taking the argmax of the similarity matrix and then removing the matched rows and columns from the similarity matrix
        # repeat until all units are matched
        matched_vertices = set([i for i in range(nunits)])
        matching = {}
        max_similarity = 0.0
        while len(matched_vertices) > 0:
            for i in matched_vertices:
                similarity_vi, vi_matched_vertices = self.sum_max_k(similarity_matrix[i, :], matched_vertices, k)
                if similarity_vi > max_similarity:
                    max_similarity = similarity_vi
                    max_similarity_vertex = i
                    max_similarity_matched_vertices = vi_matched_vertices
                
            matching[max_similarity_vertex] = max_similarity_matched_vertices
            matched_vertices.remove(max_similarity_vertex)
            for i in max_similarity_matched_vertices:
                matched_vertices.remove(i)
                
            max_similarity = 0.0

        return matching
    
            
    # add whitelist/blacklist to all matching designs
    # control and test for the effect of the whitelist/blacklist
    # multiple experiments with different whitelist/blacklist

