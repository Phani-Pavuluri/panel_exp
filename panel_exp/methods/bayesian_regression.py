"""
Methods: Bayesian TBR
======================================== 

This BayesianTBR model is built for multivariate regression analysis and accommodates multiple control units (de-aggregated) as well as a single aggregated control unit. It is particularly suitable for cases where extrapolation is necessary and can handle various prior distributions for coefficients.

Notes:

- **Multiple Control Units**: Supports both de-aggregated (multiple) and aggregated (single) control units.
- **Inference**: Uses MCMC with the No-U-Turn Sampler (NUTS) for efficient sampling.
- **Extrapolation**: This model leverages Bayesian priors and extrapolates beyond observed data.
- **Flexible Priors**: Allows specification of different priors for coefficients (Normal, Student-T, LogNormal, Multivariate Normal, Dirichlet).
- **Posterior Prediction**: Generates posterior predictions with credible intervals.

Steps:

1. **Initialize and Configure Model**: Define inference options, prior distributions, and number of samples.
2. **Data Preparation**: Fit data from `PanelDataset` for treated and control units.
3. **Define Model Structure**: Sample priors based on specified distribution type and construct a linear regression model.
4. **Run MCMC**: Use NUTS to sample from the posterior, fit the model, and make predictions with credible intervals.
5. **Posterior Analysis**: Access summary statistics, trace, and posterior plots for model diagnostics.
"""

import matplotlib.pyplot as plt 
import arviz as az
import jax.numpy as jnp
import numpy as np
from jax import random 
import numpyro
import pandas as pd
import numpy as np

import jax.random as jrandom
from scipy.stats import norm
from numpyro import sample, plate
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS

from functools import partial
from typing import Callable, Optional 
from panel_exp.panel_data import PanelDataset
from panel_exp.impact import ImpactAnalyzer
from scipy import stats 
from numpyro.infer import MCMC, NUTS, Predictive
from numpyro.handlers import substitute, trace


class standardize:
    """
    Class for standardizing a numpy array
    x = numpy array

    """

    def __init__(self, x):
        self.x = x
        self.std = np.std(x, axis=0)
        self.mean = np.mean(x, axis=0)

    def transform(self, x):
        return (x - self.mean) / self.std

    def inverse_transform(self, z):
        return z * self.std + self.mean


# Extend MCMC class to include predict method
class BayesianMCMC(MCMC):
    """Extended MCMC class to include prediction and summary statistics methods.
    -----------
    :param kernel: NUTS kernel for sampling
    :param num_warmup: Number of warmup steps
    :param num_samples: Number of samples
    :param x_scalar: Scaler for input data
    :param y_scalar: Scaler for output data
    
    Methods
    -------
    predict(X_new) -> predictions 
        Predict mean and credible intervals for new data
    summary_stats() 
        Display summary statistics for the MCMC model
    """

    def __init__(self, kernel, num_warmup, num_samples, x_scalar=None, y_scalar=None):
        super().__init__(kernel, num_warmup=num_warmup, num_samples=num_samples)
        self.x_scalar = x_scalar  # Store the x_scalar
        self.y_scalar = y_scalar  # Store the y_scalar  
        
    

    def predict(self, X_new):
        """
        Predicts the mean and credible intervals for new data based on the MCMC samples,
        and applies inverse transformation to bring predictions back to the original scale.
        :param X_new: New data (observations) for which to predict outcomes. Shape (N_new, num_predictors).
        :returns:
            Predictions. Inverse-transformed predictions for new data.
        """

        # Access scalers from the instance of BayesianTBR
        X_transformed = self.x_scalar.transform(X_new)  # Transform the input data using x_scalar
        # X_transformed = X_new  

        # x_scalar = standardize(X_new)
        samples = self.get_samples()
        coeff_samples = samples['coeffs']  # Shape (num_samples, num_predictors)
        intercept_samples = samples['intercept']  # Shape (num_samples,)

        # Calculate predicted means for each posterior sample
        predictions = intercept_samples[:, ].reshape(self.num_samples,1) + jnp.dot(coeff_samples.reshape(self.num_samples,X_transformed.shape[1]), X_transformed.T)

        # Average predictions across all samples
        # predictions_mean = jnp.mean(predictions, axis=1)
        
        # Inverse transform the predictions back to the original scale using y_scalar
        predictions_original_scale = self.y_scalar.inverse_transform(predictions)

        return predictions_original_scale
    
    def summary_stats(self):
        """
        Displays summary statistics for the MCMC model, including trace and posterior plots.
        
        """

        # Convert MCMC samples to InferenceData object for ArviZ
        idata = az.from_numpyro(self)

        # Display trace plot
        print("Displaying trace plot...")
        az.plot_trace(idata)
        plt.show()  # Ensure the trace plot is shown

        # Display posterior plot
        print("Displaying posterior plot...")
        az.plot_posterior(idata)
        plt.show()  # Ensure the posterior plot is shown

        # Print summary statistics
        print("Summary statistics:")
        summary = az.summary(idata)
        
        return summary




class BayesianTBR(ImpactAnalyzer):
    """Bayesian Treatment-Based Regression model for control and treated units in a panel dataset.
    
    
    -----------
    :param inference: Inference method for the model (default: Bayesian)
    :param alpha: Significance level for credible intervals (default: 0.1)
    :param full_model: Boolean flag to indicate whether to use full model (default: False)
    :param num_samples: Number of samples for MCMC (default: 2000)
    :param coeff_dist: Distribution type for coefficients (default: 'normal'). Options include multivariate_normal, studentT, lognormal, multivariate_normal, dirichlet.
    
    Methods
    --------
    fit_data(panel_data):
        Take a PanelDataset and return X, y for the model 
    fit_model():
        Internal method to fit the model 
    """
    
    def __init__(self 
                 , alpha: float = 0.1
                 , full_model = False
                 , num_samples = 2000
                 , coeff_dist='normal'):
        
        self.inference = "Bayesian"
        self.alpha = alpha
        #self.model_args = **model_args  
        self.ppf = stats.norm.ppf(self.alpha / 2 + (1 - self.alpha))  # two-sided
        self.full_model = full_model
        self.num_samples = num_samples
        self.coeff_dist = coeff_dist


    def fit_data(self, panel: PanelDataset):
        self.panel_data = panel 

        if self.full_model:
            y = self.panel_data.treated_series(treated_units = self.panel_data.treated_units , period='full').values.T.flatten()
            X = self.panel_data.control_series(treated_units = self.panel_data.treated_units , period='full').values.T


        if not self.full_model:
            y = self.panel_data.treated_series(self.panel_data.treated_units).values.T 
            X = self.panel_data.control_series(self.panel_data.treated_units).values.T
            
        return X, y   
    
    
    def model(self, rng_key_, X, y):
        # X is assumed to be a 2D array where each column is a predictor, and each row is an observation
        num_predictors = X.shape[1]  # Get the number of predictors
        mu = jnp.mean(X, axis=0)
        alpha = jnp.ones(num_predictors)  # Prior for Dirichlet distribution, can be tuned

        if num_predictors > 1:
            # Sample coefficients based on the chosen distribution

            if self.coeff_dist == 'normal':
                coeffs = numpyro.sample("coeffs", dist.Normal(0, 1).expand([num_predictors]))
            elif self.coeff_dist == 'studentT':
                nu = numpyro.sample("nu", dist.Gamma(2.0, 0.1))  # nu > 0, to control tail heaviness
                scale = numpyro.sample("scale", dist.HalfNormal(1.0))  # Hierarchical prior for the scale
                coeffs = numpyro.sample("coeffs", dist.StudentT(df=nu, loc=jnp.zeros(num_predictors), scale=scale))
            elif self.coeff_dist == 'lognormal':
                coeffs = numpyro.sample("coeffs", dist.LogNormal(0, 1).expand([num_predictors]))
            elif self.coeff_dist == 'multivariate_normal':
                coeffs = numpyro.sample("coeffs", dist.MultivariateNormal(loc=mu, covariance_matrix=jnp.cov(X.T)))
            elif self.coeff_dist == 'dirichlet':
                coeffs = numpyro.sample("coeffs", dist.Dirichlet(alpha))
            else:
                raise ValueError(f"Unknown coefficient distribution: {self.coeff_dist}")
            
        else:
            if (self.coeff_dist == 'normal') or (self.coeff_dist == 'multivariate_normal'):
                coeffs = numpyro.sample("coeffs", dist.Normal(0, 1))
            elif self.coeff_dist == 'studentT':
                nu = numpyro.sample("nu", dist.Gamma(2.0, 0.1))  # nu > 0, to control tail heaviness
                scale = numpyro.sample("scale", dist.HalfNormal(1.0))  # Hierarchical prior for the scale
                coeffs = numpyro.sample("coeffs", dist.StudentT(df=nu, loc=0, scale=scale))
            elif self.coeff_dist == 'lognormal':
                coeffs = numpyro.sample("coeffs", dist.LogNormal(0, 1))
            elif self.coeff_dist == 'dirichlet':
                coeffs = numpyro.sample("coeffs", dist.Dirichlet(alpha))
            else:
                raise ValueError(f"Unknown coefficient distribution: {self.coeff_dist}")

        # Sample intercept
        intercept = numpyro.sample("intercept", dist.Normal(0, 10))

        # Sample sigma (standard deviation of noise)
        sigma = numpyro.sample("sigma", dist.HalfNormal(1))

        # Calculate the linear combination of predictors and coefficients
        mu = intercept + jnp.dot(X, coeffs)

        # draw posterior samples using NUTS sampling
        numpyro.sample("obs", dist.Normal(mu, sigma), obs=y)      



    def fit_model(self):
        X, y = self.fit_data(self.panel_data)
        # Apply standardization
        self.x_scalar = standardize(X)  
        self.y_scalar = standardize(y)  

        # # Transform the data
        X = self.x_scalar.transform(X)
        y = self.y_scalar.transform(y)
        
        if self.full_model:
            y_pre = y
            X_pre = X

        if not self.full_model:
            y_pre = y[: self.panel_data.treated_start_idxs[0]]
            X_pre = X[: self.panel_data.treated_start_idxs[0]]

        # Assuming df has multiple predictors as columns
        # X = X_pre
        # y = y_pre  # Target variable

        rng_key = random.PRNGKey(0)
        rng_key, rng_key_ = random.split(rng_key)

        # Prepare the model function with bound arguments
        # model_with_rng = partial(self.model, rng_key_)

        # Run NUTS
        # kernel = NUTS(model_with_rng)


        original_model_method = self.__class__.model
        def model_wrapper(X, y):
            return original_model_method(self, rng_key_, X, y)
        
        kernel = NUTS(model_wrapper)
        self.mcmc = BayesianMCMC(kernel, num_warmup=2000, num_samples=self.num_samples, x_scalar=self.x_scalar, y_scalar=self.y_scalar)
        self.mcmc.run(rng_key_, X=X_pre, y=y_pre)
        
        return self.mcmc
    




class BayesianTBRHorseShoe(ImpactAnalyzer):
    def __init__(self, alpha=0.1, full_model=False, num_samples=2000):
        self.inference = "Bayesian"
        self.alpha = alpha
        self.ppf = stats.norm.ppf(self.alpha / 2 + (1 - self.alpha))
        self.full_model = full_model
        self.num_samples = num_samples
        self.mcmc = None  # To store the MCMC object
        self.posterior_samples = None 
        
    def fit_data(self, panel: PanelDataset): 
        self.panel_data = panel
        
        y = self.panel_data.treated_series(self.panel_data.treated_units).values.T 
        X = self.panel_data.control_series(self.panel_data.treated_units).values.T
            
        return X, y   

    @staticmethod
    def model_fn(X, y=None):
        """
        Bayesian regression model with Horseshoe prior.

        :param X: array-like, shape (n_samples, n_features)
            Predictor variables (control units).
        :param y: array-like, shape (n_samples,), optional
            Response variable (treated unit). If None, the model can be used for prediction.
        """
        num_predictors = X.shape[1]
        # Horseshoe prior parameters
        tau = numpyro.sample("tau", dist.HalfCauchy(1.0))
        lam = numpyro.sample("lam", dist.HalfCauchy(jnp.ones(num_predictors)))
        coeffs = numpyro.sample("coeffs", dist.Normal(0.0, lam * tau))

        intercept = numpyro.sample("intercept", dist.Normal(0.0, 10.0))
        sigma = numpyro.sample("sigma", dist.HalfNormal(1.0))

        mu = intercept + jnp.dot(X, coeffs)
        
        # Print shapes
        print("X shape:", X.shape)
        print("coeffs shape:", coeffs.shape)
        print("mu shape:", mu.shape)
        print("sigma shape:", sigma.shape)
        if y is not None:
            print("y shape:", y.shape)

        with numpyro.plate('data', X.shape[0], dim=-1):
            numpyro.sample('obs', dist.Normal(mu, sigma), obs=y)

    def fit_model(self):
        rng_key = random.PRNGKey(0)
        X, y = self.fit_data(self.panel_data)
        
        # Apply standardization
        self.x_scalar = standardize(X)
        self.y_scalar = standardize(y.reshape(-1, 1))  # Ensure y is 2D for StandardScaler

        # Transform the data
        X = self.x_scalar.transform(X)
        y = self.y_scalar.transform(y.reshape(-1, 1)).flatten()  # Flatten back to 1D

        y_pre = y[: self.panel_data.treated_start_idxs[0]]
        X_pre = X[: self.panel_data.treated_start_idxs[0]]

        # Print shapes for debugging
        print("X_pre shape:", X_pre.shape)
        print("y_pre shape:", y_pre.shape)

        # Proceed with MCMC sampling
        # kernel = NUTS(self.model_function)
        # self.mcmc = MCMC(kernel, num_warmup=1000, num_samples=self.num_samples)

        self.model_function = self.model_fn
        # original_model_method = self.__class__.model_fn
        def model_wrapper(X, y):
            return self.model_function(X, y)
        
        kernel = NUTS(model_wrapper)
        self.mcmc = MCMC(kernel, num_warmup=2000, num_samples=self.num_samples)

        self.mcmc.run(rng_key, X=X_pre, y=y_pre)
        self.posterior_samples = self.mcmc.get_samples()

        # Run a trace to inspect shapes
        from numpyro import handlers
        from numpyro.util import format_shapes
        
        # Run a trace to inspect shapes
        with handlers.trace() as tr:
            with handlers.seed(rng_seed=rng_key):
                self.model_function(X_pre, y=y_pre)
        print(format_shapes(tr))

        return self
    
    def predict(self, X_new):
        self.X_new = X_new
        if self.posterior_samples is None:
            raise RuntimeError("Model must be fitted using fit_model() before calling predict().")

        if X_new.ndim == 1:
            X_new = X_new.reshape(-1, 1)

        X_new_transformed = self.x_scalar.transform(X_new)  

        predictive = Predictive(
            self.model_function,
            posterior_samples=self.posterior_samples,
            return_sites=["obs"],
            parallel=True
        )
        rng_key = random.PRNGKey(1)
        predictions = predictive(rng_key, X=X_new_transformed)
        y_pred_samples = predictions['obs']
        predictions_original_scale = self.y_scalar.inverse_transform(y_pred_samples)

        return predictions_original_scale
    
    def predict_single_sample(self, X_new, sample_index=0):
        if X_new.ndim == 1:
            X_new = X_new.reshape(-1, 1)

        X_new_transformed = self.x_scalar.transform(X_new)

        # Extract a single sample
        single_sample = {k: v[sample_index] for k, v in self.posterior_samples.items()}

        # Substitute parameters
        model = substitute(self.model_function, data=single_sample)
        model_trace = trace(model).get_trace(X=X_new_transformed)

        y_pred = model_trace['obs']['value']
        y_pred_original_scale = self.y_scalar.inverse_transform(y_pred)

        return y_pred_original_scale
