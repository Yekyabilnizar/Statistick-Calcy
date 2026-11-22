from . import METHODS_EN as M
_RA = "Linear relationship and most of the data follow the model; outliers are a minority of the observations."
_SP = "The data have location coordinates, the spatial weights matrix reflects meaningful proximity, and the model is correctly specified."
M["regresi-robust-m-estimator-huber"] = ("Robust Regression – Huber M-estimator", "Reduces the influence of outliers with Huber weighting (IRLS) and sandwich standard errors.", ["Huber", "Outlier-resistant"],
 "Use when the data contain outliers that distort the ordinary regression line.", _RA,
 "Compare the coefficients with OLS; low-weight observations are outlier candidates.")
M["regresi-robust-tukey-bisquare"] = ("Robust Regression – Tukey Bisquare", "A redescending M-estimator that removes the influence of extreme outliers.", ["Bisquare"],
 "Use when outliers are extreme enough that their influence must be removed entirely.", _RA,
 "Observations with zero weight are excluded from estimation; check whether they really are erroneous data.")
M["regresi-robust-least-trimmed-squares-lts"] = ("Robust Regression – Least Trimmed Squares (LTS)", "A high-breakdown estimator (≈ 50%) that trims the largest residuals.", ["50% breakdown", "Outlier detection"],
 "Use when there are many outliers (up to about half the data) or you need strong outlier detection.", _RA,
 "Observations flagged as outliers are excluded from the final estimate; investigate the cause before discarding data.")
M["regresi-kernel"] = ("Kernel Regression", "Kernel-weighted nonparametric regression with automatic bandwidth selection.", ["Nadaraya-Watson", "Local linear"],
 "Use when the shape of the relationship between X and Y is unknown and you want a smooth curve without a specific functional form.",
 "A smooth (continuous) relationship, independent errors, and data dense enough along X.",
 "A small bandwidth makes the curve wiggly; a large one makes it too smooth. The linearity test shows whether the curve fits better than a straight line.")
M["loess-lowess"] = ("LOESS / LOWESS", "Local polynomial regression with an optimal span and a robust iteration option.", ["Span CV", "LOWESS"],
 "Use to draw a smooth trend curve that follows the data without specifying its functional form.",
 "A smooth relationship and enough data for local regression; robust iterations help when there are outliers.",
 "The span is the proportion of data used at each point; the smaller it is, the more closely the curve follows the data. The confidence band shows the uncertainty of the curve.")
M["regresi-spline"] = ("Spline Regression", "Natural cubic spline or truncated power spline with automatic knots.", ["Spline", "Knots"],
 "Use when the relationship between X and Y is curved and you want a flexible curve that is still a regression model.",
 "Errors are normal and homogeneous; the knots are sufficient to capture the curve shape without overfitting.",
 "The optimal number of knots is chosen by GCV. The linearity test shows whether the nonlinear terms are significant compared with a straight line.")
M["regresi-kuantil"] = ("Quantile Regression", "The X–Y relationship at various quantiles, not just the mean; standard errors by bootstrap.", ["Quantile", "Bootstrap"],
 "Use when you are interested in the effect of X on a particular quantile of Y (e.g. best or worst case), or the error variance is not constant.",
 "Independent observations and a linear conditional quantile model. Normal errors are not required.",
 "Compare coefficients across quantiles: if they differ significantly, the effect of X is not uniform across the distribution of Y. Standard errors and confidence intervals come from the bootstrap.")
M["generalized-additive-model-gam"] = ("Generalized Additive Model (GAM)", "Smooth effects of each variable (penalised spline, GCV) combined with linear effects.", ["s(X)", "Effective degrees of freedom"],
 "Use when some X are nonlinearly related to Y while others are linear, and you want to see the shape of each effect.",
 "Effects are additive (no interaction between variables), and errors are normal and independent.",
 "An edf close to 1 means the effect is almost linear. Compare the GAM with linear regression: if it is significant, the nonlinear component is needed.")
M["regresi-data-panel"] = ("Panel Data Regression", "Common, Fixed, and Random Effects with the Chow, Breusch-Pagan LM, and Hausman tests to choose the best model.", ["CEM · FEM · REM", "Chow · BP-LM · Hausman"],
 "Use when individuals (provinces, companies, subjects) are observed repeatedly over several time periods.",
 "Balanced or nearly balanced panel data; errors are independent across entities. Model choice uses the sequence of Chow, Breusch-Pagan LM, and Hausman tests.",
 "Follow the best-model recommendation from the test sequence: Common, Fixed, or Random Effects. Compare the coefficients of the three models and check the individual effects.")
M["regresi-deret-waktu-arimax"] = ("Time Series Regression (ARIMAX)", "Regression with ARIMA(p,d,q) errors: autocorrelation correction, Ljung-Box test, and error ACF.", ["ARIMAX", "Ljung-Box", "ACF"],
 "Use when the data are in time order and the ordinary regression errors are autocorrelated, so they need to be modelled with ARIMA.",
 "Regularly spaced sequential data, errors after the ARIMA model are no longer autocorrelated, and the series (after differencing) is stationary.",
 "Check the Ljung-Box test and the error ACF: if not significant, the autocorrelation has been handled. Compare AIC/BIC to choose the orders p, d, q.")
M["regresi-spasial-sar-lag"] = ("Spatial Regression – SAR (Lag)", "Spatial dependence in the response variable: ρ, direct/indirect effects, and Moran's I.", ["SAR", "Moran's I", "Spillover"],
 "Use when the value of Y at one location is influenced by the Y values at neighbouring locations (spatial spillover).", _SP,
 "A significant ρ indicates spatial dependence in Y; direct and indirect effects describe the spillover.")
M["regresi-spasial-sem-error"] = ("Spatial Regression – SEM (Error)", "Spatial dependence in the errors: λ, LM tests, and Moran's I of the errors.", ["SEM", "Moran's I"],
 "Use when model errors are correlated across nearby locations because of unobserved variables.", _SP,
 "A significant λ indicates spatial dependence in the errors; check the Moran's I of the residuals.")
M["geographically-weighted-regression-gwr"] = ("Geographically Weighted Regression (GWR)", "Coefficients that differ by location (spatial nonstationarity), coefficient maps, and comparison with OLS.", ["GWR", "Coefficient map", "AICc"],
 "Use when the relationship between X and Y is suspected to differ between locations (spatial nonstationarity).",
 "Enough data around each location and accurate coordinates; the bandwidth determines how local the coefficients are.",
 "Compare AICc with global OLS. Coefficient maps and local R² show where the influence of X is strong or weak.")
M["mixed-effect-model"] = ("Mixed Effects Model", "Fixed + random effects (intercept and slope) with REML; ICC and marginal/conditional R².", ["REML", "ICC", "Random slope"],
 "Use when data are nested or clustered (students within classes, plots within locations, repeated measurements on individuals).",
 "Random effects are normally distributed, errors are normal and homogeneous, and there are enough groups to estimate the variance components.",
 "The ICC shows the proportion of variance due to differences between groups. If the ICC is small, ordinary OLS may be enough. Fixed effects are read like ordinary regression.")
M["regresi-cox-survival"] = ("Cox Regression (Survival)", "Cox proportional hazards: hazard ratios, concordance, Kaplan-Meier curves, and PH assumption tests.", ["Hazard ratio", "Kaplan-Meier", "C-index"],
 "Use to analyse time until an event (death, relapse, failure) when some observations are censored.",
 "Proportional hazards (a constant hazard ratio over time), non-informative censoring, and independent observations.",
 "A hazard ratio above 1 means the risk rises; below 1 means it falls. Check the PH assumption test and the Kaplan-Meier curves; a C-index close to 1 shows good discrimination.")
M["regresi-tobit"] = ("Tobit Regression", "Regression for censored data (left/right); latent coefficients, marginal effects, and an OLS comparison.", ["Censoring", "Marginal effects"],
 "Use when the response piles up at a limit (e.g. many zeros) so the data are censored.",
 "The latent error is normally distributed with constant variance; the censoring limit is known and the same for all observations.",
 "Coefficients describe the relationship on the latent variable; marginal effects show the effect on the observed value. Compare with OLS, which is biased when many data are censored.")
