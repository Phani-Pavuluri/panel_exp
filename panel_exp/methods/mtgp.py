"""

Methods: MTGP
=================

Implementations of Multi-task Gaussian Process Estimator

"""
import numpy as np
from panel_exp.panel_data import PanelDataset
from panel_exp.impact import ImpactAnalyzer
from numpyro.infer import MCMC, NUTS
from jax import random
from scipy import stats
from jax import numpy as jnp
import numpyro
import numpyro.distributions as dist


def gp_exp_quad_cov(x, sigma, lengthscale):
    """Estimates the covariance using squared exponential kernel"""
    x1 = jnp.expand_dims(x, axis=1)
    x2 = jnp.expand_dims(x, axis=0)
    dists = jnp.power(x1 - x2, 2) / jnp.power(lengthscale, 2)
    return sigma * jnp.exp(-0.5 * dists)

def cholesky_decompose(matrix):
    """Cholesky decomposition with jitter for numeric stability"""
    return jnp.linalg.cholesky(matrix + jnp.eye(matrix.shape[0]) * 1e-9)

def gp_model(N, D, n_k_f, x, y, inv_population, num_treated, control_idx):
    """
    Implements the multi-task Gaussian process model in NumPyro.
    
    :param N:
        Number of time points
    :param D:
        Number of units
    :param n_k_f: 
        Number of latent functions
    :param x: 
        Time points
    :param y: 
        Observed outcomes
    :param inv_population: 
        Inverse population
    :param num_treated: 
        Number of treated units
    :param control_idx: 
        Indices of units under control
    """
    # Normalize data
    xmean = jnp.mean(x)
    xsd = jnp.std(x)
    xn = (x - xmean) / xsd

    # Priors (HalfNormal for scale parameters so they stay positive)
    lengthscale_global = numpyro.sample('lengthscale_global', dist.InverseGamma(5, 5))
    sigma_global = numpyro.sample('sigma_global', dist.HalfNormal(1))
    lengthscale_f = numpyro.sample('lengthscale_f', dist.InverseGamma(5, 5))
    sigma_f = numpyro.sample('sigma_f', dist.HalfNormal(1))
    sigman = numpyro.sample('sigman', dist.HalfNormal(1))
    state_offset = numpyro.sample('state_offset', dist.Normal(0, 1), sample_shape=(D,))
    z_global = numpyro.sample('z_global', dist.Normal(0, 1), sample_shape=(N,))
    z_f = numpyro.sample('z_f', dist.Normal(0, 1), sample_shape=(N, n_k_f))
    k_f = numpyro.sample('k_f', dist.Normal(0, 1), sample_shape=(n_k_f, D))
    global_offset = numpyro.sample('global_offset', dist.Normal(0, 1))

    # Covariances and Cholesky decompositions
    K_f = gp_exp_quad_cov(xn, sigma_f, lengthscale_f)
    L_f = cholesky_decompose(K_f)

    # Construct the covariance for a global trend
    K_global = gp_exp_quad_cov(xn, sigma_global, lengthscale_global)
    L_global = cholesky_decompose(K_global)

    # Index only the likelihood of the units under control
    control_idx = jnp.array(control_idx)
    y = jnp.asarray(y)
    inv_population = jnp.asarray(inv_population)

    # Likelihood (jnp for JAX tracing)
    # All terms must be (D, N): state_offset (D,1)*ones(1,N), global trend (1,N), factor (N,D).T
    factor_term = jnp.matmul(jnp.matmul(L_f, z_f), k_f)  # (N, n_k_f) @ (n_k_f, D) = (N, D)
    mu = (global_offset + jnp.outer(state_offset, jnp.ones(N)) + jnp.matmul(L_global, z_global.reshape(N, 1)).T + factor_term.T)
    f = mu.reshape(-1)[control_idx]
    y_obs = y.reshape(-1)[control_idx]
    inv_pop = inv_population.reshape(-1)[control_idx]

    numpyro.sample('y_obs', dist.Normal(f, sigman * jnp.sqrt(inv_pop)), obs=y_obs)

    # Generated quantities: mu is (D, N), inv_population is (N, D) -> transpose to match
    inv_pop_full = jnp.reshape(inv_population, (N, D)).T  # (D, N)
    numpyro.sample('y_inf', dist.Normal(mu, sigman * jnp.sqrt(inv_pop_full)).mask(False))

class MTGP(ImpactAnalyzer):
    """
    Bayesian Multi-task modeling of causal effects, implementing
    Eli Ben-Michael. David Arbour. Avi Feller. Alexander Franks. Steven Raphael.
    "Estimating the effects of a California gun control program with multitask Gaussian processes."
    Ann. Appl. Stat. 17 (2) 985 - 1016, June 2023.
    https://doi.org/10.1214/22-AOAS1654
    
    parameters
    ----------
    :param inference: Inference method to use. Currently only Bayesian inference is supported.
    :param alpha: Significance level for confidence intervals
    :param latent_rank: Rank of latent functions
    
    methods
    -------
    fit_data(panel):
        Take a PanelDataset and return X, y for the model
    fit_model():
        Fit the model. Call fit_data(panel) first to set panel_data.
    """
    def __init__(self, inference: str = "Bayesian", alpha: float = 0.1, latent_rank: int = 5):
        if inference != "Bayesian":
            raise ValueError("Only Bayesian inference supported")
        self.inference = inference
        self.alpha = alpha
        self.latent_rank = latent_rank
        self.ppf = stats.norm.ppf(alpha / 2 + (1 - alpha))  # two-sided


    def fit_data(self, panel: PanelDataset): 
        self.panel_data = panel

        # if population isn't passed in just pass in one for everyone
        if self.panel_data.populations is None:
            inv_populations = np.ones((self.panel_data.num_timepoints, self.panel_data.num_units))
        else:
            inv_populations = 1 / self.panel_data.populations

        # get a pandas dataframe with treated points set to nan
        masked_data = self.panel_data.untreated_mask()
        control_indices = self.panel_data.get_control_indices()

        model_data = {
            'N': self.panel_data.num_timepoints,
            'D': self.panel_data.num_units,
            'n_k_f': self.latent_rank,
            'x': np.asarray(self.panel_data.times),
            # pass in the masked data to prevent leakage
            'y': np.asarray(masked_data).tolist(),
            'inv_population': inv_populations,
            'num_treated': (self.panel_data.num_timepoints * self.panel_data.num_units) - control_indices.shape[0],
            'control_idx': control_indices,
        }

        return model_data

    def fit_model(self):
        model_data = self.fit_data(self.panel_data)

        # assign model function; data passed via mcmc.run(**model_data)
        self.model = gp_model
        
        # set the random seed
        rng_key = random.PRNGKey(0)
        # split the random key
        rng_key, rng_key_ = random.split(rng_key)

        # run inference
        kernel = NUTS(self.model)
        mcmc = MCMC(kernel, num_warmup=500, num_samples=1000, num_chains=1)
        mcmc.run(rng_key_, **model_data)
        self.mcmc = mcmc

        return mcmc
