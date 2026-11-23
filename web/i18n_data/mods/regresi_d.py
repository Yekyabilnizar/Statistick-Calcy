from . import MOD_EN

MOD_EN["seleksi-variabel"] = dict(
    title="Variable Selection",
    ringkas="Choose the best set of predictors with forward, backward, stepwise, or best subset.",
    tujuan=[
        "Distinguish the four selection strategies",
        "Use AIC and BIC",
        "Beware of selection bias",
    ],
    ide=[
        "With many candidate predictors, the model with all variables is not necessarily the best. Forward adds variables one at a time, backward removes them from the full model, stepwise combines the two, and best subset evaluates all combinations.",
        "The AIC and BIC criteria balance fit and complexity; BIC is more frugal with variables. Selection uses the same data to choose and to test, so the P-values of the final model are too optimistic.",
    ],
    rumus=[
        ["AIC", "AIC = n·ln(SSE/n) + 2p"],
        ["BIC", "BIC = n·ln(SSE/n) + p·ln n"],
    ],
    langkah=[
        "Decide the candidate predictors on theoretical grounds.",
        "Choose the method and criterion.",
        "Read the step trace.",
        "Check the VIF and assumptions on the final model.",
    ],
    baca=[
        "The selected model is compared with the full model through adjusted R², AIC, and BIC.",
        "Variables that always enter across methods are considered strong.",
    ],
    jebakan=[
        "Treating the selected model as the one true model.",
        "Ignoring subject-matter knowledge.",
        "Not validating on new data.",
    ],
    latihan="Run the sample data with forward and backward, then compare the selected variables.",
    notasi=[
        "Akaike criterion",
        "Bayesian criterion",
        "Mallows statistic",
        "number of parameters",
    ],
    teori=[
        ["Information criteria", [
            "Adding variables always reduces the training error, so we use criteria that penalise complexity. AIC balances fit and the number of parameters; BIC penalises more heavily for large n.",
        ]],
        ["Mallows' Cp and PRESS", [
            "\\(C_p\\) estimates the prediction error of a subset model; a value near \\(p\\) indicates small bias. PRESS is the leave-one-out sum of squared residuals.",
        ]],
        ["Procedures", [
            "Forward selection adds variables one at a time, backward removes one at a time, stepwise combines them. All are greedy and can miss the best model; best subset is more thorough but expensive. The results are optimistically biased; cross-validation is recommended.",
        ]],
    ],
    contoh=dict(
        judul="Example: comparing models with AIC",
        soal="n = 50. Model A: SSE = 120, p = 3. Model B: SSE = 100, p = 6.",
        data=None,
        langkah=[
            "AIC of model A.",
            "AIC of model B.",
        ],
        simpul="Model B has the lower AIC (46.66 < 49.77), so it is chosen despite being more complex.",
    ),
    faq=[
        ["Is stepwise reliable?",
         "Be careful: its P-values are too optimistic. Use it as exploration, then validate."],
        ["AIC or BIC?",
         "AIC for prediction, BIC for finding the true parsimonious model."],
        ["What is cross-validation?",
         "Repeatedly splitting the data to test performance on data not used for estimation."],
    ],
)

MOD_EN["regresi-ridge"] = dict(
    title="Ridge Regression",
    ringkas="Shrink coefficients with an L2 penalty to handle multicollinearity.",
    tujuan=[
        "Understand the L2 penalty and λ",
        "Choose λ by cross-validation",
        "Read the shrunken coefficients",
    ],
    ide=[
        "When predictors are highly correlated, least squares coefficients become unstable. Ridge adds a penalty on the sum of squared coefficients so the coefficients shrink toward zero but do not become zero.",
        "The penalty produces a small bias with a much smaller variance, so prediction error often improves. Because of the bias, classical t tests are not used.",
    ],
    rumus=[
        ["Objective function", "min Σ(y − Xβ)² + λ Σβⱼ²"],
        ["Solution", "b = (XᵀX + λI)⁻¹ Xᵀy"],
    ],
    langkah=[
        "Standardise X.",
        "Choose λ by cross-validation.",
        "Read the shrunken coefficients.",
        "Assess performance with the cross-validated RMSE.",
    ],
    baca=[
        "The larger λ, the stronger the shrinkage.",
        "Coefficients are not tested with t; the values are used for prediction.",
    ],
    jebakan=[
        "Forgetting to standardise the variables.",
        "Interpreting coefficients as in OLS.",
        "Assuming Ridge selects variables (it does not).",
    ],
    latihan="Run the sample data and compare the Ridge coefficients with linear regression on correlated variables.",
    notasi=[
        "shrinkage parameter",
        "ridge coefficients",
        "effective degrees of freedom",
    ],
    teori=[
        ["The objective function", [
            "Ridge adds a squared penalty on the coefficients so they shrink toward zero and the estimation is stabilised when predictors are collinear. Predictors are standardised first; the intercept is not penalised.",
        ]],
        ["Bias and variance", [
            "Ridge trades a little bias for a larger reduction in variance, so the mean squared error can be smaller than OLS. At \\(\\lambda=0\\) the result is OLS; as \\(\\lambda\\to\\infty\\) the coefficients go to zero.",
        ]],
        ["Choosing λ", [
            "\\(\\lambda\\) is chosen by cross-validation or GCV. Ridge does not select variables; all coefficients remain non-zero.",
        ]],
    ],
    contoh=dict(
        judul="Example: one predictor",
        soal="Centred data with Sxy = 57, Sxx = 42, λ = 10.",
        data=None,
        langkah=[
            "OLS.",
            "Ridge.",
        ],
        simpul="Ridge shrinks the coefficient from 1.357 to 1.096 (down 19%).",
    ),
    faq=[
        ["Why standardise?",
         "The penalty depends on the variable scale; without standardisation, small-scale variables are over-penalised."],
        ["Does ridge give P-values?",
         "Not by default; the focus is prediction."],
        ["When does ridge excel?",
         "Many predictors with high correlation."],
    ],
)

MOD_EN["regresi-lasso"] = dict(
    title="LASSO Regression",
    ringkas="An L1 penalty that also selects variables.",
    tujuan=[
        "Understand the L1 penalty",
        "Recognise coefficients that become zero",
        "Choose λ",
    ],
    ide=[
        "LASSO adds a penalty on the sum of absolute values of the coefficients. As a result some coefficients become exactly zero, so the model selects variables while estimating.",
        "It suits cases with many predictors of which only some matter. When predictors are correlated, LASSO tends to pick one of them at random.",
    ],
    rumus=[
        ["Objective function", "min Σ(y − Xβ)² + λ Σ|βⱼ|"],
    ],
    langkah=[
        "Standardise X.",
        "Choose λ by cross-validation.",
        "Look at the variables with zero coefficients.",
        "Assess predictive performance.",
    ],
    baca=[
        "A zero coefficient means the variable is excluded.",
        "Coefficients are deliberately biased; there are no t tests.",
    ],
    jebakan=[
        "Assuming a dropped variable is surely unrelated.",
        "High correlation makes the choice unstable.",
        "Interpreting classical P-values.",
    ],
    latihan="Run the sample data and note the variables that become zero; compare with the stepwise selection result.",
    notasi=[
        "L1 penalty parameter",
        "soft-threshold operator",
        "LASSO coefficient",
    ],
    teori=[
        ["The L1 penalty", [
            "LASSO uses a penalty on the sum of absolute values of the coefficients. Its special property: some coefficients are exactly zero so it performs variable selection at the same time.",
        ]],
        ["Soft-threshold", [
            "For orthonormal predictors, the LASSO solution is the OLS coefficient shifted toward zero by \\(\\lambda\\) and cut to zero if smaller than \\(\\lambda\\). In the general case it is solved by coordinate descent.",
        ]],
        ["Regularisation path and choosing λ", [
            "The coefficient path shows variables entering one by one as \\(\\lambda\\) shrinks. \\(\\lambda\\) is chosen by cross-validation (the 1-SE rule picks a more parsimonious model). LASSO is less stable with highly correlated predictors; it tends to pick one of them.",
        ]],
    ],
    contoh=dict(
        judul="Example: soft-threshold",
        soal="Standardised OLS coefficients z = 3, 0.8, and −2; λ = 1.",
        data=None,
        langkah=[
            "z = 3.",
            "z = 0.8 (smaller than λ).",
            "z = −2.",
        ],
        simpul="The second coefficient is eliminated (zero); the others shrink by 1 unit.",
    ),
    faq=[
        ["What is the difference from ridge?",
         "Ridge shrinks, LASSO shrinks and selects."],
        ["What about correlated predictors?",
         "LASSO picks one at random; use elastic net."],
        ["Are LASSO coefficients biased?",
         "Yes, biased toward zero; they can be re-estimated with OLS on the selected variables (relaxed LASSO)."],
    ],
)

MOD_EN["elastic-net"] = dict(
    title="Elastic Net",
    ringkas="A combination of L1 and L2 penalties for correlated predictors.",
    tujuan=[
        "Understand the L1 ratio",
        "Choose among Ridge, LASSO, and Elastic Net",
        "Read the results",
    ],
    ide=[
        "Elastic Net combines LASSO and Ridge. The L1 ratio sets the balance: 1 equals LASSO, 0 equals Ridge. This method is good for groups of correlated predictors because it tends to include all members of the group.",
    ],
    rumus=[
        ["Objective function", "min Σ(y − Xβ)² + λ[α Σ|βⱼ| + (1 − α)/2 Σβⱼ²]"],
    ],
    langkah=[
        "Standardise X.",
        "Choose the L1 ratio and λ.",
        "Read the coefficients.",
        "Assess the cross-validated RMSE.",
    ],
    baca=[
        "A large L1 ratio gives results similar to LASSO; a small one similar to Ridge.",
        "Choose the ratio with the smallest RMSE.",
    ],
    jebakan=[
        "Choosing the ratio without validation.",
        "Interpreting coefficients as causal effects.",
    ],
    latihan="Run the sample data with several L1 ratios and see the effect on the number of zero coefficients.",
    notasi=[
        "L1/L2 mixing weight (0 to 1)",
        "penalty strength",
    ],
    teori=[
        ["A mix of L1 and L2", [
            "Elastic net combines the strengths of LASSO (selection) and ridge (stability with correlated predictors). \\(\\alpha=1\\) is LASSO, \\(\\alpha=0\\) is ridge.",
        ]],
        ["Coordinate updates", [
            "For standardised predictors, the update of one coefficient is a soft-threshold that is then divided by the ridge factor.",
        ]],
        ["Grouping effect", [
            "The squared penalty makes highly correlated predictors receive similar coefficients and enter or leave together (the grouping effect). \\(\\alpha\\) and \\(\\lambda\\) are chosen together by cross-validation.",
        ]],
    ],
    contoh=dict(
        judul="Example: updating one coefficient",
        soal="z = 3, λ = 1, α = 0.5.",
        data=None,
        langkah=[
            "Soft-threshold with λα = 0.5.",
            "Divide by 1 + λ(1 − α) = 1.5.",
        ],
        simpul="The coefficient shrinks from 3 to 1.667 (stronger than pure LASSO, which gives 2).",
    ),
    faq=[
        ["When is elastic net chosen?",
         "When there are more predictors than observations, or many are correlated."],
        ["What α?",
         "Try 0.25, 0.5, 0.75 and choose by cross-validation."],
        ["Is standardisation needed?",
         "Yes."],
    ],
)
