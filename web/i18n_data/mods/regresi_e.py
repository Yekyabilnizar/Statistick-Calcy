from . import MOD_EN

MOD_EN["principal-component-regression-pcr"] = dict(
    title="Principal Component Regression (PCR)",
    ringkas="Regress Y on the principal components of X, which are uncorrelated.",
    tujuan=[
        "Understand principal components",
        "Choose the number of components",
        "Read the variance explained",
    ],
    ide=[
        "PCA rotates X into mutually perpendicular components, ordered by the variance explained. PCR uses the first few components as predictors so multicollinearity disappears.",
        "Weakness: the components are formed without regard to Y, so a component that is important for X is not necessarily important for Y.",
    ],
    rumus=[
        ["Component", "Zₖ = X vₖ, from the eigenvalues of XᵀX"],
    ],
    langkah=[
        "Standardise X.",
        "Choose the number of components by cross-validation.",
        "Read the variance of X explained.",
        "Transform back to the original coefficients if needed.",
    ],
    baca=[
        "The first component explains the largest variance of X.",
        "The number of components is chosen based on the cross-validated RMSE.",
    ],
    jebakan=[
        "Interpreting a component as a single variable.",
        "Truncating components too early.",
    ],
    latihan="Run the sample data and see how many components are needed to explain 90% of the variance of X.",
    notasi=[
        "eigenvalue of the correlation matrix",
        "eigenvector (loading)",
        "principal component score",
    ],
    teori=[
        ["Principal components", [
            "Principal components are mutually orthogonal linear combinations of the standardised predictors, ordered by variance explained. The score of the k-th component is:",
        ]],
        ["Regression on components", [
            "PCR regresses Y on the first \\(m\\) components (not all of them), thereby handling collinearity and reducing dimension. The coefficients return to the original predictors through the loadings.",
        ]],
        ["Choosing the number of components", [
            "Choose m by cumulative variance proportion (for example 80–95%), a scree plot, or cross-validation. Weakness: the components are formed without looking at Y, so low-variance components that matter for Y may be discarded.",
        ]],
    ],
    contoh=dict(
        judul="Example: proportion of variance",
        soal="Three standardised predictors with eigenvalues 2.4; 0.5; 0.1.",
        data=None,
        langkah=[
            "Total variance = 3.",
            "Cumulative for two components.",
        ],
        simpul="Two components already explain 96.7% of the predictor variance; the third component is nearly useless and signals collinearity.",
    ),
    faq=[
        ["PCR or ridge?",
         "Ridge shrinks all directions; PCR truncates the low-variance directions."],
        ["Are the components easy to interpret?",
         "Often not; look at the loadings to name the components."],
        ["Is standardisation mandatory?",
         "Yes if the predictors have different units."],
    ],
)

MOD_EN["partial-least-squares-pls"] = dict(
    title="Partial Least Squares (PLS)",
    ringkas="Components formed by maximising covariance with Y.",
    tujuan=[
        "Distinguish PLS from PCR",
        "Read the VIP scores",
        "Choose the number of components",
    ],
    ide=[
        "Unlike PCR, PLS forms components with Y in mind, so it uses fewer components and is often more accurate when X is large and correlated.",
        "The VIP score summarises each variable's contribution to Y; VIP ≥ 1 is considered important.",
    ],
    rumus=[
        ["Criterion", "maximise Cov(Xw, y)"],
    ],
    langkah=[
        "Standardise X.",
        "Choose the number of components by cross-validation.",
        "Look at the VIP.",
        "Evaluate the RMSE.",
    ],
    baca=[
        "Variables with VIP ≥ 1 contribute the most.",
        "The cross-validated RMSE assesses predictive ability.",
    ],
    jebakan=[
        "Too many components, causing overfitting.",
        "Treating VIP as a significance test.",
    ],
    latihan="Run the sample data with PCR and PLS and compare the number of components and the RMSE.",
    notasi=[
        "PLS component score",
        "weight",
        "covariance",
    ],
    teori=[
        ["Components that take Y into account", [
            "Unlike PCR, PLS forms components by maximising the covariance between the predictor scores and the response, so the components are relevant for predicting Y even when the predictor variance is small.",
        ]],
        ["The NIPALS algorithm (one response)", [
            "After one component is extracted, X is reduced by the part explained by the component (deflation) and the process is repeated. The final regression uses the scores \\(\\mathbf{t}_1,\\dots,\\mathbf{t}_m\\).",
        ]],
        ["Number of components", [
            "Chosen by cross-validation based on RMSEP or \\(Q^2\\). Too many components cause overfitting.",
        ]],
    ],
    contoh=dict(
        judul="Example: weights of the first component",
        soal="If X′y = (6, 8), the weight w₁ is formed by normalisation.",
        data=None,
        langkah=[
            "Norm.",
            "Weights.",
        ],
        simpul="The second predictor gets a larger weight because its covariance with Y is larger.",
    ),
    faq=[
        ["PLS or PCR?",
         "PLS usually needs fewer components because it looks at Y."],
        ["What cases is it suited to?",
         "More predictors than observations and high correlation (chemometrics, spectra)."],
        ["How is it interpreted?",
         "Look at the weights and the VIP (variable importance in projection)."],
    ],
)

MOD_EN["regresi-robust-m-estimator-huber"] = dict(
    title="Robust Regression: Huber M-estimator",
    ringkas="Reduce the influence of outliers through weighting.",
    tujuan=[
        "Understand Huber weighting",
        "Compare with OLS",
        "Flag outliers through weights",
    ],
    ide=[
        "Least squares is very sensitive to outliers. The Huber M-estimator minimises a loss function that is quadratic for small residuals and linear for large residuals, so extreme observations are given lower weight. Estimation is iterative (IRLS).",
    ],
    rumus=[
        ["Huber weight", "w = 1 if |r| ≤ c; w = c/|r| if |r| > c"],
        ["Constant", "c = 1.345 (95% efficiency)"],
    ],
    langkah=[
        "Run OLS and Huber.",
        "Compare the coefficients.",
        "Check the observations with low weights.",
        "Trace the cause of the outliers.",
    ],
    baca=[
        "A large difference between OLS and Huber indicates influential outliers.",
        "Low weights flag candidate outliers.",
    ],
    jebakan=[
        "Deleting outliers without a clear cause.",
        "Assuming robust methods solve high leverage.",
    ],
    latihan="Run the sample data, compare the coefficients with OLS, and name the observation with the lowest weight.",
    notasi=[
        "loss function",
        "influence function",
        "weight",
        "tuning constant (1.345)",
        "robust scale (MAD)",
    ],
    teori=[
        ["The idea of an M-estimator", [
            "Least squares is very sensitive to outliers because the quadratic loss grows quickly. An M-estimator replaces the square with a loss function that grows more slowly for large residuals.",
        ]],
        ["The Huber function", [
            "Huber is quadratic for small residuals and linear for large ones. With \\(k=1.345\\), 95% efficiency is achieved when errors are normal while resisting outliers.",
        ]],
        ["IRLS", [
            "The solution is obtained by repeated weighted least squares: weights are computed from the current residuals and the coefficients are updated until convergence.",
        ]],
    ],
    contoh=dict(
        judul="Example: Huber weights",
        soal="Standardised residuals u = 0.8 and u = 2.",
        data=None,
        langkah=[
            "u = 0.8 (≤ 1.345).",
            "u = 2.",
        ],
        simpul="The distant observation is given a weight of 0.67, so its influence is reduced but it is not thrown away.",
    ),
    faq=[
        ["Is Huber resistant to high leverage?",
         "Not entirely; an M-estimator resists outliers in the Y direction, but not outliers in X space."],
        ["Why use the MAD?",
         "Because the standard deviation itself is affected by outliers."],
        ["When is it used?",
         "When there are a few moderate outliers in the response."],
    ],
)

MOD_EN["regresi-robust-tukey-bisquare"] = dict(
    title="Robust Regression: Tukey Bisquare",
    ringkas="A redescending M-estimator that gives zero weight to extreme outliers.",
    tujuan=[
        "Distinguish Huber from bisquare",
        "Understand zero weights",
        "Examine the discarded data",
    ],
    ide=[
        "In bisquare, the weight declines and then becomes zero for very large residuals, so extreme outliers no longer influence the estimate. It is stronger than Huber but sensitive to the starting values.",
    ],
    rumus=[
        ["Constant", "c = 4.685 (95% efficiency)"],
    ],
    langkah=[
        "Run bisquare.",
        "Look at the observations with zero weight.",
        "Check whether those data are erroneous or genuinely valid observations.",
        "Compare with OLS and Huber.",
    ],
    baca=[
        "Observations with zero weight are excluded from estimation.",
        "Compare the three methods to gauge the impact of outliers.",
    ],
    jebakan=[
        "Not examining the discarded data.",
        "Poor starting values.",
    ],
    latihan="Run the sample data and compare the OLS, Huber, and bisquare coefficients.",
    notasi=[
        "tuning constant (4.685)",
        "bisquare weight",
        "standardised residual",
    ],
    teori=[
        ["The redescending function", [
            "Unlike Huber, bisquare gives zero weight to very large residuals (redescending) so extreme outliers are fully ignored. With \\(c=4.685\\) it has 95% efficiency under normal errors.",
        ]],
        ["The nonconvex problem", [
            "Because the loss is not convex, there may be several local minima. A robust starting value (e.g. from Huber or LTS) is important so that IRLS does not stop at a wrong solution.",
        ]],
        ["Comparison", [
            "Huber: the weight falls gradually and is never zero. Bisquare: the weight becomes zero beyond \\(c\\). Bisquare is more resistant, but more sensitive to initialisation.",
        ]],
    ],
    contoh=dict(
        judul="Example: bisquare weights",
        soal="Standardised residuals u = 2 and u = 5.",
        data=None,
        langkah=[
            "u = 2.",
            "u = 5 (> 4.685).",
        ],
        simpul="A residual of 2 still has a weight of 0.67, whereas a residual of 5 is discarded entirely.",
    ),
    faq=[
        ["Huber or bisquare?",
         "Bisquare if there are extreme outliers; Huber for mild outliers."],
        ["Why is a robust starting value needed?",
         "Because the loss is nonconvex."],
        ["What is the breakdown point?",
         "The maximum proportion of outliers an estimator can tolerate; an M-estimator with a good starting value can reach 50%."],
    ],
)
