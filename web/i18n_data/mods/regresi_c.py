from . import MOD_EN

MOD_EN["regresi-logistik-ordinal"] = dict(
    title="Ordinal Logistic Regression",
    ringkas="An ordered response (low, medium, high) with the proportional odds assumption.",
    tujuan=[
        "Understand the proportional odds model",
        "Read the thresholds",
        "Interpret cumulative odds ratios",
    ],
    ide=[
        "An ordinal response makes use of the order of the categories. The model models the cumulative odds of being in a category ≤ j. One set of coefficients applies to all cut-points, the proportional odds assumption, while the intercepts (thresholds) differ for each boundary.",
        "A positive coefficient raises the probability of being in a higher category; exp(β) is the cumulative odds ratio.",
    ],
    rumus=[
        ["Model", "ln[P(Y ≤ j) / P(Y > j)] = θⱼ − βX"],
    ],
    langkah=[
        "Make sure the categories are ordered correctly.",
        "Run the model.",
        "Read β, the cumulative OR, and the thresholds.",
        "Check the goodness-of-fit test.",
    ],
    baca=[
        "A threshold separates adjacent categories.",
        "The cumulative OR is the same for all cut-points thanks to the proportional odds assumption.",
    ],
    jebakan=[
        "Reversed category order.",
        "The proportional odds assumption is violated.",
        "Categories that are too sparse.",
    ],
    latihan="Run the sample data and translate one coefficient into everyday language.",
    notasi=[
        "k-th cut-point",
        "linear index",
        "ordered categories 1..K",
    ],
    teori=[
        ["The proportional odds model", [
            "For an ordinal response, cumulative probabilities are modelled with one set of coefficients \\(\\boldsymbol{\\beta}\\) and \\(K-1\\) thresholds. The proportional odds assumption: the effect of the predictors is the same at all cut-points.",
        ]],
        ["Probability of each category", [
            "The category probability is obtained from the difference of successive cumulative probabilities.",
        ]],
        ["Interpretation", [
            "\\(e^{\\beta}\\) is the odds ratio of being in a lower category (or a higher one, depending on the sign) per unit of x. The assumption is checked with the Brant test.",
        ]],
    ],
    contoh=dict(
        judul="Example: three categories",
        soal="θ₁ = −1, θ₂ = 1, η = 0.5.",
        data=None,
        langkah=[
            "Cumulative.",
            "Probability of each category.",
        ],
        simpul="The middle category is the most likely. The three probabilities sum to 1.",
    ),
    faq=[
        ["Why is ordinal better than multinomial?",
         "It has fewer parameters and makes use of the order."],
        ["If proportional odds is violated?",
         "Use a partial proportional odds model or multinomial."],
        ["Is a 1–5 Likert scale ordinal?",
         "Yes, the distances are not necessarily equal."],
    ],
)

MOD_EN["regresi-poisson"] = dict(
    title="Poisson Regression",
    ringkas="Model count data (0, 1, 2, ...) with rate ratios.",
    tujuan=[
        "Understand the log link function",
        "Read the incidence rate ratio",
        "Check for overdispersion",
    ],
    ide=[
        "Count data such as the number of events, visits, or specimens have a variance that depends on the mean. Poisson regression models ln(mean) as a linear function of X, assuming variance = mean.",
        "Exp(β) is the rate ratio: the factor by which the mean count is multiplied for a one-unit rise in X.",
    ],
    rumus=[
        ["Model", "ln(μ) = β₀ + β₁X₁ + …"],
        ["Rate ratio", "IRR = e^β"],
        ["Dispersion", "φ = deviance / df; ≈ 1 matches the assumption"],
    ],
    langkah=[
        "Make sure the response is a non-negative integer.",
        "Run the model.",
        "Check the dispersion.",
        "If φ is far above 1, move to negative binomial.",
    ],
    baca=[
        "An IRR of 1.2 means the mean count rises 20% per unit of X.",
        "Overdispersion makes standard errors too small so tests are too easily significant.",
    ],
    jebakan=[
        "Ignoring overdispersion.",
        "Counts from different exposure periods without an offset.",
        "Excess zeros.",
    ],
    latihan="Run the sample data and check the dispersion; decide whether the model is adequate.",
    notasi=[
        "mean count",
        "incidence rate ratio",
        "log exposure",
        "deviance",
    ],
    teori=[
        ["The model", [
            "For count data, the response is modelled as Poisson with a log link so the mean is always positive. In the Poisson distribution, the mean equals the variance.",
        ]],
        ["Interpretation and offset", [
            "\\(e^{\\beta}\\) is the incidence rate ratio (IRR). If exposure differs (area, time), add an offset \\(\\ln(t_i)\\) with a fixed coefficient of 1.",
        ]],
        ["Overdispersion", [
            "If the variance exceeds the mean (overdispersion), standard errors are too small. The dispersion statistic is near 1 when the model fits; values well above 1 suggest negative binomial or quasi-Poisson.",
        ]],
    ],
    contoh=dict(
        judul="Example: IRR and the probability of zero",
        soal="Coefficient β = 0.3 for dose; μ = 2 for a given observation.",
        data=None,
        langkah=[
            "IRR.",
            "Probability of a zero count at μ = 2.",
        ],
        simpul="Each unit of dose raises the event rate by 35%. With a mean of 2, 13.5% of observations are expected to be zero.",
    ),
    faq=[
        ["How do I detect overdispersion?",
         "Divide the Pearson statistic by the df; a value above about 1.5 is suspicious."],
        ["When should an offset be used?",
         "When observation periods or areas differ."],
        ["Many zeros?",
         "Consider a zero-inflated or hurdle model."],
    ],
)

MOD_EN["regresi-binomial-negatif"] = dict(
    title="Negative Binomial Regression",
    ringkas="An alternative to Poisson when the count variance is larger than the mean.",
    tujuan=[
        "Understand overdispersion",
        "Read the dispersion parameter α",
        "Choose between Poisson and negative binomial",
    ],
    ide=[
        "In much real count data, the variance exceeds the mean (overdispersion) because of unobserved heterogeneity. The negative binomial adds a dispersion parameter α that raises the variance: Var = μ + αμ².",
        "If α differs significantly from 0, the negative binomial is more appropriate than Poisson.",
    ],
    rumus=[
        ["Variance", "Var(Y) = μ + αμ²"],
        ["Rate ratio", "IRR = e^β"],
    ],
    langkah=[
        "Run Poisson and check the dispersion.",
        "If overdispersed, run the negative binomial.",
        "Read α and the IRR.",
        "Compare AIC.",
    ],
    baca=[
        "A significant α > 0 justifies this model.",
        "The IRR is read as in Poisson.",
    ],
    jebakan=[
        "Using it on counts with excess zeros without considering a zero-inflated model.",
        "Skipping the comparison with Poisson.",
    ],
    latihan="Run the sample data with Poisson and negative binomial and compare the standard errors and AIC.",
    notasi=[
        "dispersion parameter",
        "mean",
        "variance",
    ],
    teori=[
        ["Quadratic variance", [
            "The negative binomial adds a dispersion parameter \\(\\alpha\\) so the variance exceeds the mean. It can be viewed as a Poisson-gamma mixture. When \\(\\alpha\\to0\\) the result is Poisson.",
        ]],
        ["Probability", [
            "With \\(\\theta=1/\\alpha\\), the probability function uses the gamma function. The coefficients \\(\\beta\\) are estimated by maximum likelihood together with \\(\\alpha\\).",
        ]],
        ["Choosing against Poisson", [
            "The likelihood ratio test of \\(\\alpha=0\\) (on the boundary of the parameter space) or AIC compares the two models. The interpretation of coefficients remains the IRR.",
        ]],
    ],
    contoh=dict(
        judul="Example: negative binomial variance",
        soal="μ = 4, α = 0.5.",
        data=None,
        langkah=[
            "Variance.",
        ],
        simpul="A variance of 12 far exceeds the mean of 4; a Poisson model would underestimate standard errors and reject too often.",
    ),
    faq=[
        ["When is it better than Poisson?",
         "When overdispersion is significant."],
        ["What is the difference from quasi-Poisson?",
         "Quasi-Poisson only inflates the standard errors; NB models the actual distribution so it gives a likelihood and AIC."],
        ["Must α be positive?",
         "Yes; α = 0 is Poisson."],
    ],
)

MOD_EN["regresi-gamma"] = dict(
    title="Gamma Regression",
    ringkas="A positive, right-skewed continuous response such as cost or duration.",
    tujuan=[
        "Understand the gamma distribution and the log link",
        "Read the ratio of change in the mean",
        "Choose a gamma GLM over a log transformation",
    ],
    ide=[
        "A positive response that skews to the right (cost, length of stay, duration) does not fit normal errors. Gamma regression models the mean response with a log link and a constant coefficient of variation.",
        "Exp(β) is the ratio of change in the mean response per unit of X.",
    ],
    rumus=[
        ["Model", "ln(μ) = β₀ + β₁X₁ + …"],
        ["Variance", "Var(Y) = φμ²"],
    ],
    langkah=[
        "Make sure the response is > 0.",
        "Run the model and check the residuals.",
        "Read exp(β) as a ratio.",
        "Compare with regression on ln(Y) if needed.",
    ],
    baca=[
        "exp(β) = 1.10 means the mean response rises 10% per unit of X.",
        "The deviance and residuals assess fit.",
    ],
    jebakan=[
        "A response with zero or negative values.",
        "Interpreting β as an absolute change.",
        "Ignoring the influence of outliers.",
    ],
    latihan="Run the sample data and explain one coefficient as a percentage change.",
    notasi=[
        "mean",
        "dispersion parameter",
        "link function",
    ],
    teori=[
        ["The gamma distribution in a GLM", [
            "For a positive, right-skewed continuous response (cost, duration, concentration), the gamma distribution has a constant coefficient of variation: the variance is proportional to the square of the mean.",
        ]],
        ["Link function", [
            "The log link gives multiplicative effects and guarantees a positive mean; the inverse (canonical) link is also common. Coefficients with a log link are interpreted as ratios of means.",
        ]],
        ["Dispersion and deviance", [
            "The dispersion is estimated from the Pearson statistic. Fit is assessed with the deviance and residual plots.",
        ]],
    ],
    contoh=dict(
        judul="Example: log link",
        soal="ln μ = 1 + 0.2·x.",
        data=None,
        langkah=[
            "Mean at x = 5.",
            "Ratio per unit of x.",
        ],
        simpul="Each one-unit rise in x raises the mean response by 22.1%.",
    ),
    faq=[
        ["Gamma or log transformation?",
         "A gamma GLM models the mean on the original scale; log-normal models the mean of the log. The results can differ."],
        ["Can the response be zero?",
         "No, the response must be positive."],
        ["Why choose the log link?",
         "Multiplicative effects and a guaranteed positive mean."],
    ],
)
