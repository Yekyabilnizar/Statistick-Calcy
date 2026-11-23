from . import MOD_EN

MOD_EN["regresi-linear-sederhana-berganda"] = dict(
    title="Linear Regression (Simple and Multiple)",
    ringkas="Express Y as a linear function of one or several X and test it.",
    tujuan=[
        "Understand the model and least squares estimation",
        "Read the F test, t tests, and R²",
        "Use the prediction calculator with CI and PI",
    ],
    ide=[
        "Linear regression finds the line (or plane) that minimises the sum of squared residuals. The coefficient βⱼ is the average change in Y when Xⱼ rises by one unit with the other variables held fixed.",
        "The F test assesses whether the model as a whole is better than just using the mean of Y. The t tests assess each coefficient. R² is the proportion of variability in Y explained; adjusted R² penalises adding useless variables.",
    ],
    rumus=[
        ["Model", "Y = β₀ + β₁X₁ + … + βₖXₖ + ε"],
        ["Estimator", "b = (XᵀX)⁻¹ Xᵀy"],
        ["R²", "R² = 1 − SSE / SSTO"],
        ["t test", "t = bⱼ / SE(bⱼ), df = n − k − 1"],
    ],
    langkah=[
        "Draw a scatter plot.",
        "Choose Y and X, run the regression.",
        "Read the F test, R², and coefficients.",
        "Check the assumptions and influential observations.",
        "Use the Prediction tab if the goal is forecasting.",
    ],
    baca=[
        "A positive coefficient means Y rises when X rises; read it in the original units.",
        "Standardised betas help compare the influence of X variables with different units.",
        "A high R² does not guarantee a correct model; check the residuals.",
    ],
    jebakan=[
        "Using the model outside the range of X (extrapolation).",
        "Concluding causation from correlation.",
        "Adding variables just to raise R².",
    ],
    latihan="Run the sample data, then open the Prediction tab and enter X values inside and outside the data range; compare the width of the CI and PI and read the extrapolation warning.",
    notasi=[
        "response vector (n×1)",
        "design matrix (n×(k+1))",
        "coefficient vector",
        "hat matrix",
        "coefficient of determination",
    ],
    teori=[
        ["The model in matrix form", [
            "Multiple linear regression models the response as a linear combination of k predictors. In matrix form, the first column of X contains 1s for the intercept. The least squares estimator minimises the sum of squared residuals and has a closed form.",
        ]],
        ["Decomposition of variability", [
            "As in ANOVA, the total variability is split into the part explained by the regression and the error. The error variance is estimated by the error mean square with df \\(n-k-1\\).",
        ]],
        ["The F test and t tests", [
            "The F test tests \\(H_0:\\beta_1=\\dots=\\beta_k=0\\), i.e. whether the model is better than the mean alone. The t tests test individual coefficients. Adjusted \\(R^2\\) accounts for the number of predictors.",
        ]],
        ["Prediction intervals", [
            "For a new point \\(\\mathbf{x}_0\\), the confidence interval for the mean and the prediction interval for one observation differ by the 1 under the square root. Both are narrowest near the predictor means and widen under extrapolation.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: simple regression",
        soal="Dose (x) and yield (y) on six plots.",
        data=[
            ["x", "2", "4", "5", "7", "8", "10"],
            ["y", "3", "6", "7", "10", "11", "14"],
        ],
        langkah=[
            "Slope and intercept from least squares.",
            "SSE and error mean square (df = 4).",
            "R² and the prediction at x = 6.",
            "An example of adjusted R² for another model with R² = 0.80, n = 20, k = 3.",
        ],
        simpul="The line ŷ = 0.357 + 1.357x explains 99.8% of the variability. Adjusted R² is always lower than R² and falls when useless predictors are added.",
    ),
    faq=[
        ["Why does R² keep rising as predictors are added?",
         "Because the SSE never rises when a column is added. Use adjusted R², AIC, or cross-validation."],
        ["What does a coefficient mean in multiple regression?",
         "The average change in Y per one-unit increase in \\(X_j\\) with the other predictors held fixed."],
        ["Why is the PI wider than the CI?",
         "The PI includes the individual variance \\(\\sigma^2\\) in addition to the uncertainty of the line."],
    ],
)

MOD_EN["regresi-dummy"] = dict(
    title="Regression with Dummy Variables",
    ringkas="Bring categorical predictors into regression by turning them into 0/1 variables.",
    tujuan=[
        "Understand dummy coding and the reference category",
        "Read dummy coefficients",
        "Avoid dummy variable pitfalls",
    ],
    ide=[
        "Categories cannot be put directly into an equation. For a factor with m categories, m − 1 dummy variables valued 0 or 1 are created; one category becomes the reference.",
        "A dummy coefficient is the difference in mean response between that category and the reference category, holding other variables fixed. Regression with dummies is equivalent to ANOVA, and becomes ANCOVA when mixed with numeric predictors.",
    ],
    rumus=[
        ["Model", "Y = β₀ + β₁D₁ + β₂D₂ + … + γX + ε"],
        ["Meaning of β₀", "mean of Y for the reference category (when X = 0)"],
    ],
    langkah=[
        "Decide the reference category (calculator: the first category).",
        "Choose the response, the numeric predictors, and the categorical predictors.",
        "Read the coefficients and their tests.",
    ],
    baca=[
        "A positive D coefficient: that category is higher than the reference.",
        "Changing the reference changes the coefficients but not the model's predictions.",
    ],
    jebakan=[
        "Including all m dummies together with the intercept (the dummy variable trap).",
        "Thinking a dummy coefficient compares two non-reference categories.",
        "Categories with very few observations.",
    ],
    latihan="Run the sample data, note the reference category, then compute for yourself the difference in mean response of the other categories from the reference and match it with the coefficients.",
    notasi=[
        "dummy variable for category k (0/1)",
        "number of categories",
        "mean of the reference category",
        "covariate coefficient",
    ],
    teori=[
        ["Dummy coding", [
            "A factor with \\(m\\) categories is represented by \\(m-1\\) dummy variables; one category becomes the reference. Including \\(m\\) dummies together with the intercept creates perfect collinearity (the dummy variable trap) because the sum of all dummies equals the intercept column.",
        ]],
        ["Model and interpretation", [
            "In a model without covariates, the intercept is the reference mean and each dummy coefficient is the difference between that category's mean and the reference; this model is equivalent to one-way ANOVA. With a covariate X, each category gets a parallel line with a different intercept (equivalent to ANCOVA).",
        ]],
        ["Dummy × covariate interaction", [
            "If slopes may differ between categories, add the product of the dummy and X. The product coefficient is the difference in slope from the reference.",
        ]],
    ],
    contoh=dict(
        judul="Example: three varieties",
        soal="Mean yield of variety A (reference) = 6, B = 8, C = 10.",
        data=None,
        langkah=[
            "The intercept is the reference mean.",
            "A dummy coefficient is the difference from the reference.",
            "Prediction for variety C.",
        ],
        simpul="The dummy model gives the same means as ANOVA; the t tests on b_B and b_C compare against A.",
    ),
    faq=[
        ["Why m−1 dummies?",
         "Because m dummies and the intercept are linearly dependent."],
        ["Does changing the reference change the conclusions?",
         "The coefficients and t tests change, but the predictions and the overall F test stay the same."],
        ["How do I compare two non-reference categories?",
         "Test the contrast \\(\\beta_B-\\beta_C\\), or change the reference."],
    ],
)

MOD_EN["regresi-polinomial"] = dict(
    title="Polynomial Regression",
    ringkas="Model a curve by adding powers of X.",
    tujuan=[
        "Understand higher-degree models",
        "Choose the degree with the degree-increase test and AIC/BIC",
        "Recognise the danger of overfitting",
    ],
    ide=[
        "When the relationship between X and Y is curved, add X², X³, and so on. The model remains linear in its coefficients so it can be estimated by least squares.",
        "Choose the lowest degree that is still significant. A degree that is too high follows the noise (overfitting) and behaves wildly at the ends of the range.",
    ],
    rumus=[
        ["Model", "Y = β₀ + β₁X + β₂X² + … + β_dX^d + ε"],
        ["AIC", "AIC = n·ln(SSE/n) + 2p"],
    ],
    langkah=[
        "Look at the scatter plot.",
        "Try degree 1 up to a reasonable maximum.",
        "Use the degree-increase test and AIC/BIC.",
        "Choose the lowest adequate degree.",
    ],
    baca=[
        "If the highest-degree term is significant, the degree increase is useful.",
        "The lowest AIC/BIC is chosen; if they disagree, favour BIC for a simpler model.",
    ],
    jebakan=[
        "Choosing a high degree just because R² rises.",
        "Extrapolation.",
        "Collinearity among power terms; centre X if needed.",
    ],
    latihan="Run the sample data and compare degrees 1, 2, and 3. Choose one and explain your reason with AIC and the degree-increase test.",
    notasi=[
        "predictor (preferably centred)",
        "polynomial degree",
        "extreme point",
        "coefficient of the j-th power",
    ],
    teori=[
        ["The polynomial model", [
            "Polynomial regression remains linear in the coefficients even though it is curved in x. So all linear regression theory applies. Choose the degree as parsimoniously as possible; a high degree causes oscillation.",
        ]],
        ["Extreme point and curvature", [
            "For a quadratic model, the optimum is at the point below; a negative quadratic coefficient indicates a maximum, a positive one a minimum. The point must lie within the data range to be meaningful.",
        ]],
        ["Degree selection and collinearity", [
            "The powers x and x² are highly correlated. Centring \\(x\\) (subtracting the mean) reduces collinearity. The degree is chosen through a sequential F test (extra SS) or AIC.",
        ]],
    ],
    contoh=dict(
        judul="Example: the optimum dose",
        soal="Model yield = 20 + 6·dose − 0.5·dose² (dose in units of 10 kg/ha).",
        data=None,
        langkah=[
            "The optimum dose.",
            "The yield at the optimum dose.",
        ],
        simpul="The maximum yield is 38 at a dose of 60 kg/ha. Beyond 60 the yield declines.",
    ),
    faq=[
        ["Can a polynomial be used for prediction outside the data?",
         "Dangerous: polynomials blow up outside the range."],
        ["Why centre x?",
         "It reduces the collinearity between x and x² and stabilises estimation."],
        ["When should a spline be chosen?",
         "When local curvature and a high degree are needed."],
    ],
)

MOD_EN["diagnostik-regresi-tanpa-intersep"] = dict(
    title="Diagnostics and Regression Without Intercept",
    ringkas="A complete check of regression assumptions, plus a model through the origin.",
    tujuan=[
        "Run tests of normality, heteroscedasticity, autocorrelation, and multicollinearity",
        "Read Cook's D and leverage",
        "Know when to drop the intercept",
    ],
    ide=[
        "Regression diagnostics check the classical assumptions: normal residuals (Shapiro-Wilk, Jarque-Bera, Anderson-Darling), constant variance (Breusch-Pagan, White, Glejser), no autocorrelation (Durbin-Watson, Breusch-Godfrey), and no multicollinearity (VIF).",
        "Influential observations are checked through Cook's D and leverage. Regression without an intercept forces the line through the origin; it is used only if theoretically Y = 0 when X = 0, and its R² is not comparable with that of a model with an intercept.",
    ],
    rumus=[
        ["Durbin-Watson", "DW ≈ 2 means no autocorrelation"],
        ["VIF", "VIFⱼ = 1 / (1 − Rⱼ²); > 10 is problematic"],
        ["Cook's D", "rough threshold 4/n"],
    ],
    langkah=[
        "Run the model and read the assumption test table.",
        "Look at the residual plots and Cook's D.",
        "Check the VIF of each predictor.",
        "Remedy: transformation, remove collinear variables, or a robust method.",
    ],
    baca=[
        "P > α in an assumption test means no evidence of violation.",
        "A Cook's D above the threshold means that observation is highly influential; trace the cause.",
    ],
    jebakan=[
        "Relying on a single test.",
        "Removing influential observations without a substantive reason.",
        "Dropping the intercept to raise R².",
    ],
    latihan="Run the sample data and make a small table: which assumptions are met, which are not, and the action you would suggest.",
    notasi=[
        "leverage",
        "studentised residual",
        "Cook's distance",
        "variance inflation factor",
    ],
    teori=[
        ["Leverage and standardised residuals", [
            "Leverage \\(h_{ii}\\) is the diagonal of the hat matrix; it measures how far a point is from the centre of the predictors. The studentised residual standardises the residual while accounting for leverage.",
        ]],
        ["Influential observations", [
            "Cook's distance combines residual and leverage. Points with \\(D_i\\) above about \\(4/n\\) (or above 1) deserve a check. A rough leverage threshold is \\(2p/n\\).",
        ]],
        ["Multicollinearity", [
            "The VIF measures the inflation of coefficient variance. A VIF above 10 (or tolerance \\(1/VIF<0.1\\)) indicates serious collinearity.",
        ]],
        ["Regression without an intercept", [
            "The line is forced through the origin. The slope estimator changes, and \\(R^2\\) is computed against the uncentred sum of squares so it cannot be compared with a model with an intercept. Use it only when there is a strong theoretical reason.",
        ]],
    ],
    contoh=dict(
        judul="Example: leverage and Cook's D for data x = 2…10",
        soal="In the regression of y on x (n = 6, p = 2, x̄ = 6, Sxx = 42), check the point x = 10 (e = 0.0714; s² = 0.0357).",
        data=None,
        langkah=[
            "Leverage.",
            "Studentised residual.",
            "Cook's distance.",
        ],
        simpul="Leverage is high (0.548) because the point is at the end, but the residual is small so D = 0.19 < 0.67 (4/n): the point is not a problem.",
    ),
    faq=[
        ["Should influential points be deleted?",
         "Not automatically. Check the correctness of the data; compare the results with and without the point."],
        ["High VIF, what now?",
         "Combine variables, drop one, or use ridge/PCR."],
        ["Why does R² without an intercept look higher?",
         "Because it is compared against \\(\\sum y^2\\), not deviations from the mean."],
    ],
)
