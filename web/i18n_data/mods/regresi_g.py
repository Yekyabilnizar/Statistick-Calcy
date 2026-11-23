from . import MOD_EN

MOD_EN["regresi-kuantil"] = dict(
    title="Quantile Regression",
    ringkas="The relationship between X and Y at various quantiles, not just the mean.",
    tujuan=[
        "Understand conditional quantiles",
        "Compare coefficients across quantiles",
        "Know when to use it",
    ],
    ide=[
        "Ordinary regression estimates the conditional mean of Y. Quantile regression estimates a particular quantile, for example the median or the 90% quantile, by minimising asymmetrically weighted absolute errors.",
        "Useful when the effect of X differs at the ends of the distribution, or when there are outliers and unequal variance. Standard errors are obtained by bootstrap.",
    ],
    rumus=[
        ["Objective function", "min Σ ρτ(yᵢ − xᵢᵀβ), ρτ(u) = u(τ − I(u < 0))"],
    ],
    langkah=[
        "Choose quantiles, for example 0.1; 0.5; 0.9.",
        "Run and compare the coefficients across quantiles.",
        "Check the bootstrap confidence intervals.",
    ],
    baca=[
        "Coefficients that differ across quantiles show that the effect of X is not uniform across the distribution of Y.",
        "The median is more resistant to outliers than the mean.",
    ],
    jebakan=[
        "Thinking different quantiles mean the model is broken.",
        "A sample too small for extreme quantiles.",
    ],
    latihan="Run the sample data at several quantiles and explain whether the effect of X changes from the lower to the upper quantiles.",
    notasi=[
        "quantile level (0–1)",
        "pinball loss function",
        "conditional quantile",
    ],
    teori=[
        ["Quantile loss", [
            "Quantile regression models the conditional \\(\\tau\\) quantile of the response, not the mean. The estimator minimises an asymmetric loss: positive and negative residuals are weighted differently. For \\(\\tau=0.5\\) the result is median regression (LAD).",
        ]],
        ["Benefits", [
            "It shows how the effect of predictors differs in the tails of the distribution (for example the lowest 10% and the highest 90%); it is resistant to outliers; it needs no assumption on the error distribution.",
        ]],
        ["Linear programming and inference", [
            "The problem can be written as a linear program. Standard errors are computed by bootstrap or asymptotic formulas. Quantiles computed separately can cross each other in small samples.",
        ]],
    ],
    contoh=dict(
        judul="Example: pinball loss",
        soal="τ = 0.9, residuals u = +2 and u = −2.",
        data=None,
        langkah=[
            "Positive residual (above the line).",
            "Negative residual.",
        ],
        simpul="At τ = 0.9 the line is pulled upward: points above the line are penalised 9 times more heavily, so 90% of the data will lie below the line.",
    ),
    faq=[
        ["What is the difference from ordinary regression?",
         "Ordinary regression models the mean; quantile regression models other parts of the distribution."],
        ["When is it useful?",
         "Unequal variance, a skewed distribution, or interest in extreme values (stunted growth, highest costs)."],
        ["Why do quantiles cross?",
         "Because each τ is estimated separately; small samples and extrapolation make it worse."],
    ],
)

MOD_EN["generalized-additive-model-gam"] = dict(
    title="Generalised Additive Model (GAM)",
    ringkas="Smooth effects of each variable combined with linear effects.",
    tujuan=[
        "Understand smooth functions",
        "Read the edf",
        "Compare with linear regression",
    ],
    ide=[
        "A GAM replaces the linear term βX with a smooth function f(X) estimated from the data using penalised splines. Each predictor is allowed its own effect shape while remaining additive.",
        "The effective degrees of freedom (edf) express the flexibility of the curve: edf ≈ 1 means nearly linear, larger values mean more curved.",
    ],
    rumus=[
        ["Model", "Y = β₀ + f₁(X₁) + f₂(X₂) + … + ε"],
    ],
    langkah=[
        "Choose the variables expected to be nonlinear as smooth terms.",
        "Run the GAM.",
        "Read the edf and the effect plots.",
        "Compare with linear regression.",
    ],
    baca=[
        "An edf near 1 means the effect is nearly linear.",
        "A significant comparison with the linear model means the nonlinear component is needed.",
    ],
    jebakan=[
        "Including too many smooth terms for a small sample.",
        "Interpreting without the effect plots.",
        "Extrapolation.",
    ],
    latihan="Run the sample data and name which predictors have a nonlinear effect based on the edf.",
    notasi=[
        "smooth function of the j-th predictor",
        "link function",
        "effective degrees of freedom",
    ],
    teori=[
        ["The additive model", [
            "A GAM replaces linear coefficients with smooth functions estimated from the data, but still sums the influence of each predictor. It suits responses from the exponential family through the link function \\(g\\).",
        ]],
        ["Backfitting and penalties", [
            "Each function is estimated in turn by smoothing the partial residuals (backfitting), or simultaneously with penalised splines. The smoothing parameters are chosen by GCV or REML.",
        ]],
        ["Effective degrees of freedom", [
            "An edf near 1 means the relationship is nearly linear; a value well above 1 means curved. The test for each term asks whether the function differs from a constant.",
        ]],
    ],
    contoh=dict(
        judul="Example: interpreting the edf",
        soal="Two smooth terms: edf(x₁) = 1.0 and edf(x₂) = 6.2.",
        data=None,
        langkah=[
            "x₁ with edf 1.0.",
            "x₂ with edf 6.2.",
        ],
        simpul="The effect of x₁ can simply be included as a linear term; x₂ is truly nonlinear.",
    ),
    faq=[
        ["What is the difference from spline regression?",
         "A GAM adds an additive structure over many predictors with automatic penalties."],
        ["Are interactions possible?",
         "Yes, with a smooth surface term \\(f(x_1,x_2)\\)."],
        ["Is there a final equation?",
         "Not a single one; interpret through the plot of each function."],
    ],
)

MOD_EN["regresi-data-panel"] = dict(
    title="Panel Data Regression",
    ringkas="Data on many individuals observed over many time points: Common, Fixed, or Random Effect.",
    tujuan=[
        "Distinguish the three panel models",
        "Use the Chow, Breusch-Pagan LM, and Hausman tests",
        "Choose the best model",
    ],
    ide=[
        "Panel data have individual and time dimensions. Common effect treats all individuals as the same (ordinary regression). Fixed effect gives each individual its own intercept. Random effect treats individual differences as a random component.",
        "Model selection uses three tests: Chow (common vs fixed), Breusch-Pagan LM (common vs random), and Hausman (fixed vs random).",
    ],
    rumus=[
        ["Fixed model", "yᵢₜ = αᵢ + xᵢₜβ + εᵢₜ"],
        ["Random model", "yᵢₜ = α + xᵢₜβ + uᵢ + εᵢₜ"],
    ],
    langkah=[
        "Arrange the data in long format: individual, time, response, predictors.",
        "Run the three models.",
        "Follow the sequence of selection tests.",
        "Read the coefficients of the selected model.",
    ],
    baca=[
        "Follow the recommendation of the test results to choose the best model.",
        "Individual effects show the differences between units.",
    ],
    jebakan=[
        "Ignoring the panel structure so standard errors are too small.",
        "An unbalanced panel without attention.",
        "Hausman with a small sample.",
    ],
    latihan="Run the sample data and write down which panel model is recommended along with the reasons from the three tests.",
    notasi=[
        "individual (unit)",
        "time",
        "individual effect",
        "data deviated from the individual mean",
    ],
    teori=[
        ["The fixed effects model", [
            "Panel data observe the same units repeatedly. The fixed effects model gives each unit its own intercept so unit characteristics that are constant (but unobserved) do not bias the coefficients. The within estimator is computed from data minus each unit's mean.",
        ]],
        ["The random effects model", [
            "The unit effect is treated as random and uncorrelated with the predictors. The result is more efficient and can estimate predictors that do not change over time, but is biased if the assumption is violated. The between-unit share of variance is expressed by the ICC.",
        ]],
        ["The Hausman test", [
            "It compares the fixed and random effects estimators. If they differ significantly, random effects is biased and fixed effects is chosen.",
        ]],
    ],
    contoh=dict(
        judul="Example: the within transformation",
        soal="Unit A is observed three times with y = 4, 6, 8.",
        data=None,
        langkah=[
            "Unit mean.",
            "Deviations.",
        ],
        simpul="Differences in level between units are removed; only within-unit variation is used to estimate β.",
    ),
    faq=[
        ["FE or RE?",
         "Use the Hausman test; if the unit effect may be correlated with predictors, choose FE."],
        ["What about standard errors?",
         "Use cluster-robust standard errors per unit because errors are often correlated within units."],
        ["May time-invariant variables be included in FE?",
         "No; they are eliminated by the within transformation."],
    ],
)

MOD_EN["regresi-deret-waktu-arimax"] = dict(
    title="Time Series Regression (ARIMAX)",
    ringkas="Regression with autocorrelated errors modelled by ARIMA.",
    tujuan=[
        "Understand error autocorrelation",
        "Read the ACF and Ljung-Box",
        "Choose the orders p, d, q",
    ],
    ide=[
        "In time-ordered data, errors are often correlated with previous errors so ordinary regression estimates standard errors that are too small. ARIMAX adds an ARIMA(p,d,q) structure to the regression errors.",
        "p is the autoregressive order, d the differencing to remove trend, q the moving-average order. The adequacy of the model is checked with the Ljung-Box test and the ACF of the errors.",
    ],
    rumus=[
        ["Model", "yₜ = xₜβ + ηₜ, ηₜ ~ ARIMA(p, d, q)"],
    ],
    langkah=[
        "Order the data by time.",
        "Start from small orders.",
        "Check Ljung-Box and the ACF of the errors.",
        "Compare AIC/BIC across orders.",
    ],
    baca=[
        "A non-significant Ljung-Box means autocorrelation has been handled.",
        "The lowest AIC/BIC shows the suggested order.",
    ],
    jebakan=[
        "Shuffling the time order.",
        "An order that is too high.",
        "Non-stationary data without differencing.",
    ],
    latihan="Run the sample data and compare Ljung-Box before and after adding AR orders.",
    notasi=[
        "AR coefficient",
        "MA coefficient",
        "degree of differencing",
        "backshift operator",
    ],
    teori=[
        ["The ARIMAX model", [
            "ARIMAX adds regression on external predictors into an ARIMA time series model: the regression errors follow an ARMA process so correlation across time is not ignored. The backshift operator \\(B\\) shifts time: \\(By_t=y_{t-1}\\).",
        ]],
        ["Stationarity and differencing", [
            "Non-stationary series are differenced until stationary (ADF test). For a stationary AR(1), \\(|\\phi|<1\\) is required, and its variance is:",
        ]],
        ["Identification and diagnostics", [
            "The order \\((p,d,q)\\) is chosen from the ACF/PACF and AIC. Residuals should behave like white noise; the Ljung-Box test checks this.",
        ]],
    ],
    contoh=dict(
        judul="Example: AR(1) variance",
        soal="φ = 0.6; σ² = 1.",
        data=None,
        langkah=[
            "Variance.",
            "Lag-2 correlation.",
        ],
        simpul="The variance is 1.56 and the autocorrelation declines geometrically.",
    ),
    faq=[
        ["Are predictors differenced too?",
         "Yes, if the response series is differenced, the predictors must be too."],
        ["Why not ordinary OLS?",
         "Autocorrelated errors make standard errors wrong."],
        ["Does forecasting need future predictor values?",
         "Yes; they must be known or forecast."],
    ],
)
