from . import METHODS_EN as M
_GLM_A = "Observations are independent, the link function is appropriate, and there is no severe multicollinearity. The number of events should be adequate for the number of predictors."
_REG_A = "Basic linear regression assumptions (linear relationship, independent observations). Variables are standardised automatically before estimation."
_BIAS = " Coefficients are deliberately biased in exchange for lower variance, so classical t-tests are not reported; predictive performance is judged by cross-validated RMSE compared with OLS."
M["regresi-linear-sederhana-berganda"] = ("Linear Regression (simple & multiple)", "Linear relationship between one or more X variables and Y: equation, F/t tests, R², classical assumption tests, and a prediction calculator.", ["OLS", "Simple & multiple", "Classical assumption tests", "Prediction calculator"],
 "Use to measure the relationship between one or more X variables and a numeric Y, e.g. the effect of land area, fertiliser, and rainfall on crop yield.",
 "Linear relationship, normally distributed errors with constant variance, no autocorrelation, and no severe multicollinearity among the X variables.",
 "The F test assesses the model as a whole; t tests assess each coefficient. R² is the proportion of the variation in Y explained by the model. On the Prediction tab, enter X values to get a prediction of Y with its confidence interval.")
M["regresi-dummy"] = ("Regression with Dummy Variables", "Regression with numeric and categorical predictors; categories are converted to dummy variables with the first category as the reference.", ["Dummy", "Reference", "Coefficient per category"],
 "Use when some predictors are categories (fertiliser type, location, sex) that must be included in the regression model.",
 "Same as linear regression: linearity, normal and homogeneous errors, no autocorrelation or multicollinearity.",
 "A dummy coefficient is the difference in mean response between that category and the reference category, holding the other variables constant.")
M["regresi-polinomial"] = ("Polynomial Regression", "Higher-degree curve models with a degree-increase test, confidence bands, and degree selection by AIC/BIC.", ["Degree 1–6", "AIC · BIC", "Confidence band"],
 "Use when the relationship between X and Y is curved, e.g. a response that rises and then falls with dose.",
 "Errors are normal and homogeneous, the curve really is polynomial in shape, and the degree is not raised excessively (risk of overfitting).",
 "Choose the lowest degree that is still significant in the degree-increase test and has a small AIC/BIC.")
M["diagnostik-regresi-tanpa-intersep"] = ("Diagnostics & Regression Without Intercept", "Linear regression with complete assumption tests: normality, heteroscedasticity, autocorrelation, multicollinearity, and influential observations.", ["OLS", "VIF · Cook's D", "Classical assumption tests"],
 "Use to explain or predict one numeric variable from one or more other numeric variables.",
 "Linear relationship, normal errors with constant variance, no autocorrelation, and no severe multicollinearity among the independent variables.",
 "Look at R² and the F test for overall fit, the t tests for each coefficient, then check the assumption-test table and influential observations.")
M["regresi-nonlinear"] = ("Nonlinear Regression", "Exponential, logarithmic, power, logistic (growth), Michaelis-Menten, and Gompertz, with comparison of all models.", ["6 models", "Nonlinear least squares", "AIC comparison"],
 "Use when the relationship between X and Y follows a curve of a particular shape, such as growth or enzyme kinetics.",
 "The functional form matches the observed process, errors are normal and homogeneous, and the starting values are reasonable (found automatically).",
 "Compare AIC across models; parameters with small standard errors are more trustworthy.")
M["regresi-logistik-biner"] = ("Binary Logistic Regression", "Two-category response (0/1) with odds ratios, classification, and ROC curve.", ["Odds ratio", "ROC", "Classification"],
 "Use when the response has two categories, such as yes/no, recovered/not, or buy/not buy.", _GLM_A,
 "An odds ratio above 1 means the probability of the event rises as X rises; below 1 means it falls. An AUC close to 1 shows the model separates the groups well.")
M["regresi-probit"] = ("Probit Regression", "Like logistic, with a standard normal link function; often used in dose-response tests.", ["Probit", "ROC"],
 "Use when the response is binary and you prefer a latent normal distribution assumption, common in bioassay.", _GLM_A,
 "Coefficients show the change in the z-score of the event probability per unit of X.")
M["regresi-logistik-multinomial"] = ("Multinomial Logistic Regression", "Nominal response variable with three or more classes; the first class is the reference.", ["Nominal ≥ 3 classes", "Relative odds ratio"],
 "Use when the response is an unordered category with three or more classes, such as a choice, a type of disease, or a brand.",
 "Independent observations, independence of irrelevant alternatives, and enough observations per class. No perfect separation.",
 "The first class is the reference. Exp(coefficient) is the odds ratio relative to the reference class for a one-unit increase in X; see the classification accuracy for the precision of the model.")
M["regresi-logistik-ordinal"] = ("Ordinal Logistic Regression", "Ordered response (proportional odds): coefficients, thresholds, odds ratios, and goodness-of-fit tests.", ["Proportional odds", "Threshold"],
 "Use when the response is an ordered category, such as a 1–5 satisfaction scale or a low–medium–high severity level.",
 "Proportional odds (the effect of X is the same at all thresholds), independent observations, and clearly ordered categories.",
 "A positive coefficient raises the probability of being in a higher category; exp(coefficient) is the cumulative odds ratio. Thresholds separate adjacent categories.")
M["regresi-poisson"] = ("Poisson Regression", "Count response (0, 1, 2, ...) with rate ratios and an overdispersion test.", ["Rate ratio", "Overdispersion"],
 "Use when the response is a count of events, such as the number of pests or visits.", _GLM_A,
 "Exp(coefficient) is the rate ratio. Check dispersion: if it is far above 1, consider negative binomial.")
M["regresi-binomial-negatif"] = ("Negative Binomial Regression", "For count data with overdispersion (variance greater than the mean).", ["Overdispersion", "Rate ratio"],
 "Use when count data show variance far above the mean so that Poisson does not fit.", _GLM_A,
 "A dispersion parameter α significantly different from 0 justifies this model over Poisson.")
M["regresi-gamma"] = ("Gamma Regression", "Positive, right-skewed response (cost, duration) with a log link.", ["Log link", "Positive response"],
 "Use when the response is always positive and right-skewed, such as cost, waiting time, or concentration.", _GLM_A,
 "Exp(coefficient) is the ratio of change in mean response per unit of X.")
M["seleksi-variabel"] = ("Variable Selection", "Forward, backward, stepwise, and best subset by AIC or BIC, with step trace and model comparison.", ["Forward · Backward", "Stepwise", "Best subset"],
 "Use when there are many candidate X variables and you want the set that best explains Y.",
 "Linear regression assumptions hold. P-values in the selected model tend to be too optimistic because the variables were chosen from the same data.",
 "Compare the selected model with the full model (adjusted R², AIC, BIC). The step trace shows variables entering or leaving; check VIF in the final model.")
M["regresi-ridge"] = ("Ridge Regression", "L2 coefficient shrinkage for multicollinearity; λ is chosen by cross-validation.", ["L2", "Cross-validation"],
 "Use when the X variables are strongly correlated and you want more stable coefficients.", _REG_A,
 "Coefficients shrink toward zero without being removed; the larger λ is, the stronger the shrinkage." + _BIAS)
M["regresi-lasso"] = ("LASSO Regression", "L1 shrinkage that also selects variables (coefficients become exactly zero).", ["L1", "Variable selection"],
 "Use when there are many X variables and you want to select the important ones at the same time.", _REG_A,
 "A coefficient that becomes exactly zero means the variable is dropped from the model." + _BIAS)
M["elastic-net"] = ("Elastic Net", "A combination of L1 and L2 penalties for correlated predictors.", ["L1 + L2"],
 "Use when X variables are correlated and numerous, so LASSO alone is unstable.", _REG_A,
 "The L1 ratio sets the balance between variable selection (LASSO) and shrinkage (Ridge)." + _BIAS)
M["principal-component-regression-pcr"] = ("Principal Component Regression (PCR)", "Regression on principal components to handle multicollinearity.", ["PCA", "Principal components"],
 "Use when X is highly correlated and you want to regress Y on the principal components of X.", _REG_A,
 "The number of components is chosen by cross-validation; see the variance of X explained by each component." + _BIAS)
M["partial-least-squares-pls"] = ("Partial Least Squares (PLS)", "Regression on components that maximise covariance with Y (NIPALS algorithm).", ["NIPALS", "Latent components"],
 "Use when X is numerous and correlated, and you want the components most relevant to Y.", _REG_A,
 "Variables with VIP ≥ 1 contribute most to explaining Y." + _BIAS)
