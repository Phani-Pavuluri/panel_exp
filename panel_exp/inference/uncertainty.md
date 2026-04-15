Possible panel data uncertainty for python package

Questions

Questions about use cases:
* Single treated unit vs. multiple treated units? 
* Simultaneous adoption vs. staggered adoption

Target estimand:
* Missing Y(0) for single treated unit? 
* Average of missing Y(0) for all units? 

Uncertainty over time:
* Pointwise confidence intervals
* Simultaneous confidence bounds 



Approaches to uncertainty quantification

- Uncertainty over units
- Unit Jackknife
- Unit Jackknife+
- Unit Bootstrap
- Unit Permutation


Uncertainty over time
- Time conformal inference
- Time jackknife+


Model-based uncertainty
- Bayesian intervals
- Regression-based standard errors


Unit Jackknife

[reference: https://www.aeaweb.org/articles?id=10.1257/aer.20190159] 

For each i = 1, …, N in control group:
Estimate -i,j, T, missing (average) control potential outcome for treated unit j for each post-treatment time T > T0, without unit i in training sample; Compute  -j,T= Yj,T --i,j,T

Compute jackknife variance for each post-treatment time T > T0
Vjack = N-1N(-j,T-T)2
Where T is the original (non-jackknife) estimate

[Can immediately extend to bootstrap]



Unit Jackknife+

[reference: https://arxiv.org/abs/1905.02928] 

[Do not implement for now; statistical properties still unclear]




Time Jackknife+

[reference: https://arxiv.org/abs/1905.02928] 

For each t in 1 to T0:
Estimate -t,j,T, panel data prediction for treated unit j for each post-treatment time period T > T0, without pre-treatment time t < T0 in training sample
Estimate -t,j,t, panel data prediction for treated unit j at time period t < T0, without t in training sample; compute (absolute) residual  R-t= |Yj,t --t,j, t| 

For Normal quantile , compute for each post-treatment time T > T0
Lower CI bound: q/2(-t,j,T -R-t) 
Upper CI bound: q1-/2(-t,j,T +R-t) 


Conformal inference over time

[reference: https://arxiv.org/abs/1712.09089]


For pointwise uncertainty, repeat for each post-treatment time T > T0 ; otherwise, modify for average treatment effect statistic

Choose test function f; default is absolute value of difference; can use other statistics targeting other estimands

Estimate j,T, the standard panel data prediction for post-treatment time T using all pre-treatment time periods; Compute test function fT= |Yj,T -j,T|

For each t in 1 to T0 
Estimate -t,j,t, panel data prediction for treated unit j for time t, including post-treatment time T > T0  in training sample; Compute test function ft= |Yj,t --t,j, t|

Compute (one-sided) p-value for null of no effect:
p = 1T0+1tI[ft>fT]



Model-based uncertainty

[Reference: https://projecteuclid.org/journals/annals-of-applied-statistics/volume-17/issue-2/Estimating-the-effects-of-a-California-gun-control-program-with/10.1214/22-AOAS1654.short] 

[... report computed uncertainty intervals?]



