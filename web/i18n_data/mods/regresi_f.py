from . import MOD_EN

MOD_EN["regresi-robust-least-trimmed-squares-lts"] = dict(
    title="Robust Regression: Least Trimmed Squares (LTS)",
    ringkas="An estimator with a high breakdown point through trimming the largest residuals.",
    tujuan=[
        "Understand the breakdown point",
        "Understand residual trimming",
        "Flag outliers",
    ],
    ide=[
        "LTS minimises only the sum of squares of the h smallest residuals, ignoring the rest. The method resists up to about 50% outliers (high breakdown point), so it suits heavily contaminated data.",
        "Observations flagged as outliers are excluded from the final estimate.",
    ],
    rumus=[
        ["Criterion", "min Σ₍ᵢ₌₁₎ʰ r²₍ᵢ₎"],
    ],
    langkah=[
        "Run LTS.",
        "Look at the flagged observations.",
        "Trace the cause.",
        "Compare with OLS.",
    ],
    baca=[
        "Outlier observations are excluded from the final estimate.",
        "Efficiency is lower than an M-estimator on clean data.",
    ],
    jebakan=[
        "Using it on clean data (loss of efficiency).",
        "Discarding data without investigation.",
    ],
    latihan="Run the sample data and name the observations flagged as outliers.",
    notasi=[
        "number of observations used",
        "ordered squared residuals",
        "sample size and parameters",
    ],
    teori=[
        ["The objective function", [
            "LTS minimises the sum of only the \\(h\\) smallest squared residuals, so observations with large residuals are fully ignored. The maximum breakdown point of 50% is reached at \\(h\\approx(n+p+1)/2\\).",
        ]],
        ["Algorithm", [
            "Because it is combinatorial, LTS is computed with many random starts and C-steps (concentration steps): choose the h points with the smallest residuals, recompute OLS, repeat until no decrease.",
        ]],
        ["Outlier detection", [
            "Residuals from the LTS model, divided by a robust scale, reveal outliers: those exceeding 2.5 are considered outliers. Weakness: low efficiency, so LTS results are usually used as starting values for an efficient estimator.",
        ]],
    ],
    contoh=dict(
        judul="Example: the number of points h",
        soal="n = 10, p = 2.",
        data=None,
        langkah=[
            "Compute h.",
        ],
        simpul="Only 6 of the 10 points are used to determine the line; up to 4 outliers can be tolerated.",
    ),
    faq=[
        ["Why is its efficiency low?",
         "Because it discards part of the data even if it is good."],
        ["How are LTS results used?",
         "As an initial estimator or to flag outliers, followed by an MM-estimator."],
        ["What is the breakdown point?",
         "The largest percentage of contaminated data that does not make the estimate arbitrary; LTS reaches almost 50%."],
    ],
)

MOD_EN["regresi-kernel"] = dict(
    title="Kernel Regression",
    ringkas="Nonparametric kernel-weighted regression with automatic bandwidth.",
    tujuan=[
        "Understand the locally weighted average",
        "Choose the bandwidth",
        "Test linearity",
    ],
    ide=[
        "Kernel regression estimates Y at each point as a weighted average of nearby observations; weights decline with distance through a kernel function. No particular functional form is assumed.",
        "The bandwidth h controls smoothness: a small one gives a wiggly curve (large variance), a large one gives an over-smooth curve (large bias).",
    ],
    rumus=[
        ["Nadaraya-Watson", "m̂(x) = Σ K((x − xᵢ)/h) yᵢ / Σ K((x − xᵢ)/h)"],
    ],
    langkah=[
        "Look at the scatter plot.",
        "Choose an automatic bandwidth (cross-validation).",
        "Read the curve and band.",
        "Test linearity.",
    ],
    baca=[
        "A significant linearity test means the curve fits better than a straight line.",
        "Set h manually to see the effect.",
    ],
    jebakan=[
        "Extrapolation.",
        "An unsuitable bandwidth.",
        "Edge effects (bias at the ends of the data).",
    ],
    latihan="Run the sample data and change the bandwidth from small to large; describe how the curve changes.",
    notasi=[
        "kernel function",
        "window width (bandwidth)",
        "estimated regression function",
    ],
    teori=[
        ["The Nadaraya-Watson estimator", [
            "Kernel regression does not assume a functional form; the prediction at x is a weighted average of the observations, with weights that decline with distance from x. A common kernel is the Gaussian.",
        ]],
        ["Bias, variance, and bandwidth", [
            "A small bandwidth gives a wiggly curve (large variance, small bias); a large bandwidth gives an over-smooth curve (large bias). It is chosen by leave-one-out cross-validation.",
        ]],
        ["Edge effects", [
            "At the edges of the data range, the weighted average becomes biased because neighbours lie on only one side. Local linear regression (LOESS) corrects this.",
        ]],
    ],
    contoh=dict(
        judul="Example: prediction at x = 3",
        soal="x = 1,2,3,4,5; y = 2,4,5,4,6; Gaussian kernel h = 1.",
        data=[
            ["x", "1", "2", "3", "4", "5"],
            ["y", "2", "4", "5", "4", "6"],
        ],
        langkah=[
            "Weights (without the constant) at x = 3.",
            "Weighted average.",
        ],
        simpul="The prediction is 4.40, slightly below 5 because the surrounding observations are smaller.",
    ),
    faq=[
        ["What about the bandwidth?",
         "Use cross-validation; make sure it is not too small."],
        ["What is its weakness?",
         "The curse of dimensionality: difficult with many predictors."],
        ["Is there a final equation?",
         "No, only the estimated curve."],
    ],
)

MOD_EN["loess-lowess"] = dict(
    title="LOESS / LOWESS",
    ringkas="Local polynomial regression with an optimal span.",
    tujuan=[
        "Understand the span",
        "Understand robust iteration",
        "Read the confidence band",
    ],
    ide=[
        "LOESS fits a low-degree polynomial at each point using a fraction of the nearest data (the span), with tricube weights. The result is a smooth curve without a global model.",
        "Robust iteration down-weights outliers so the curve is not pulled by extreme data.",
    ],
    rumus=[
        ["Span", "the proportion of data used at each point, 0 < span ≤ 1"],
    ],
    langkah=[
        "Look at the scatter plot.",
        "Choose the optimal span or set it yourself.",
        "Turn on robust iteration if there are outliers.",
        "Read the curve and band.",
    ],
    baca=[
        "A small span follows the data more closely; a large one is smoother.",
        "The confidence band shows the uncertainty of the curve.",
    ],
    jebakan=[
        "A span that is too small, following the noise.",
        "Interpreting without the uncertainty band.",
    ],
    latihan="Run the sample data with several span values and compare the curves.",
    notasi=[
        "proportion of data in the window (span)",
        "tricube weight",
        "distance to the point x",
    ],
    teori=[
        ["Locally weighted linear regression", [
            "At each point x, LOESS fits a weighted line (or quadratic) using only the nearest fraction \\(q\\) of the data. Weights decline according to the tricube function and are zero outside the window.",
        ]],
        ["Robustification (LOWESS)", [
            "LOWESS adds iterations of robust (bisquare) weights based on residuals to suppress outliers.",
        ]],
        ["Choosing the span", [
            "A small span (e.g. 0.2) follows the data closely but is wiggly; a large span (0.8) is smooth. Choose with AICc or cross-validation.",
        ]],
    ],
    contoh=dict(
        judul="Example: tricube weight",
        soal="A point at half the window width, d/h = 0.5.",
        data=None,
        langkah=[
            "Weight.",
        ],
        simpul="A point at half the window distance still has a weight of 0.67, whereas a point at the window edge has a weight of 0.",
    ),
    faq=[
        ["LOESS or kernel?",
         "LOESS fits a local polynomial so it is better at the edges."],
        ["What is LOWESS for?",
         "Protecting the curve from outliers."],
        ["Can it forecast outside the data?",
         "Not recommended."],
    ],
)

MOD_EN["regresi-spline"] = dict(
    title="Spline Regression",
    ringkas="A piecewise curve joined smoothly at knots.",
    tujuan=[
        "Understand knots and the spline basis",
        "Choose the number of knots with GCV",
        "Test linearity",
    ],
    ide=[
        "A spline divides the range of X with knots and fits a cubic polynomial in each segment, joined so as to be smooth. A natural cubic spline is constrained to be linear beyond the data boundaries, so it is more stable at the ends.",
        "The number of knots is chosen through GCV (generalised cross-validation). A spline remains linear in its coefficients so it is estimated by least squares.",
    ],
    rumus=[
        ["Model", "Y = β₀ + Σ βⱼ Bⱼ(X) + ε"],
    ],
    langkah=[
        "Look at the scatter plot.",
        "Choose the spline type and number of knots.",
        "Read the curve and the linearity test.",
        "Compare with a polynomial.",
    ],
    baca=[
        "A significant linearity test means nonlinear terms are needed.",
        "Too many knots cause overfitting.",
    ],
    jebakan=[
        "Too many knots.",
        "Extrapolation outside the data.",
    ],
    latihan="Run the sample data and compare a spline with a polynomial on the same data.",
    notasi=[
        "knot",
        "truncated power function",
        "number of knots",
    ],
    teori=[
        ["Truncated power basis", [
            "A cubic spline is a cubic polynomial per segment joined smoothly at the knots (continuous up to the second derivative). In basis form it is a linear model so it is estimated with OLS.",
        ]],
        ["Degrees of freedom", [
            "A cubic spline with K knots has \\(K+4\\) parameters (including the intercept). A natural spline adds linear constraints at the ends so it has \\(K+1\\) parameters and is more stable at the edges.",
        ]],
        ["Penalised (smoothing) splines", [
            "Instead of choosing knots, a smoothing spline places a knot at every point and penalises the roughness of the curve. The parameter \\(\\lambda\\) controls smoothness.",
        ]],
    ],
    contoh=dict(
        judul="Example: number of parameters",
        soal="A cubic spline with 3 knots.",
        data=None,
        langkah=[
            "Ordinary cubic.",
            "Natural spline.",
        ],
        simpul="A cubic spline needs 7 parameters; a natural spline only 4, more economical and more stable at the edges.",
    ),
    faq=[
        ["Where should knots be placed?",
         "At the data quantiles or at points of change."],
        ["Why a natural spline?",
         "A cubic polynomial can blow up at the edges; the linear constraint tames it."],
        ["Spline or polynomial?",
         "A spline is more local and does not oscillate."],
    ],
)
