from . import MOD_EN

MOD_EN["regresi-nonlinear"] = dict(
    title="Nonlinear Regression",
    ringkas="Growth and kinetic curves that are not linear in their parameters.",
    tujuan=[
        "Know six common models",
        "Compare models with AIC",
        "Read biological parameters",
    ],
    ide=[
        "Some processes follow curves that are nonlinear in the parameters: exponential, logistic, and Gompertz growth; Michaelis-Menten enzyme kinetics; and logarithmic and power forms.",
        "Estimation is done by iterative nonlinear least squares from starting values. The parameters have physical meaning (asymptote, rate, inflection point), so they are easy to interpret.",
    ],
    rumus=[
        ["Logistic", "Y = K / (1 + e^(−r(x − x₀)))"],
        ["Michaelis-Menten", "Y = Vmax·x / (Km + x)"],
        ["Exponential", "Y = a·e^(bx)"],
    ],
    langkah=[
        "Look at the shape of the data scatter.",
        "Run all models and look at the AIC comparison.",
        "Choose a model that is theoretically plausible with a low AIC.",
        "Read the parameters and their standard errors.",
    ],
    baca=[
        "A smaller AIC = a relatively better model.",
        "A small standard error means the parameter is trustworthy.",
    ],
    jebakan=[
        "Poor starting values make the iteration fail to converge.",
        "Choosing a model from R² alone.",
        "Using data that do not cover an important phase (for example the asymptote has not been reached).",
    ],
    latihan="Run the sample data and compare all models. Choose one and explain the biological meaning of its parameters.",
    notasi=[
        "function nonlinear in the parameters",
        "Jacobian matrix",
        "Michaelis-Menten parameters",
    ],
    teori=[
        ["Models and nonlinear least squares", [
            "A nonlinear model is not linear in its parameters, so there is no closed form. The parameters are obtained by iteratively minimising \\(S(\\theta)\\).",
        ]],
        ["Gauss-Newton and Levenberg-Marquardt", [
            "Gauss-Newton linearises f around the current guess and solves a linear least squares problem for the step. Levenberg-Marquardt adds a damping term \\(\\lambda\\) to remain stable when the initial guess is far off.",
        ]],
        ["Common models", [
            "Michaelis-Menten for saturating kinetics, logistic for growth, exponential for decay. Good starting values are often obtained from linearisation or by inspecting the graph.",
        ]],
        ["Inference", [
            "Standard errors come from the asymptotic covariance matrix; confidence intervals are approximate and can worsen in small samples.",
        ]],
    ],
    contoh=dict(
        judul="Example: Michaelis-Menten",
        soal="Vmax = 10, Km = 2. Compute the rate for S = 2 and S = 18.",
        data=None,
        langkah=[
            "At S = Km, the rate is half the maximum.",
            "At S = 18.",
        ],
        simpul="Km is the concentration at half the maximum rate; at large S the rate approaches Vmax = 10.",
    ),
    faq=[
        ["Why are starting values important?",
         "The optimisation can stop at a local minimum or fail to converge."],
        ["May I linearise (Lineweaver-Burk)?",
         "Acceptable as a starting value, but the transformation changes the error structure; it is better to estimate directly."],
        ["How do I choose a model?",
         "Compare AIC and residual plots; consider the biological meaning of the parameters."],
    ],
)

MOD_EN["regresi-logistik-biner"] = dict(
    title="Binary Logistic Regression",
    ringkas="Model the probability of a two-category event (0/1) from predictors.",
    tujuan=[
        "Understand the logit link and the odds ratio",
        "Read the Wald test, LR test, and Hosmer-Lemeshow",
        "Assess the model with the classification table and ROC/AUC",
    ],
    ide=[
        "When the response has only two possible outcomes (recovered/not, passed/not), linear regression is unsuitable because predictions can fall outside [0,1]. Logistic regression models the log odds as a linear function of X.",
        "Coefficients are read through the odds ratio, OR = e^β: the factor by which the odds of the event are multiplied for a one-unit increase in X.",
    ],
    rumus=[
        ["Model", "ln[p / (1 − p)] = β₀ + β₁X₁ + … + βₖXₖ"],
        ["Probability", "p = 1 / (1 + e^−(β₀ + βX))"],
        ["Odds ratio", "OR = e^β"],
    ],
    langkah=[
        "Code the response as 0/1.",
        "Run the model and read the coefficients and ORs.",
        "Check Hosmer-Lemeshow for fit.",
        "Assess discrimination with ROC/AUC.",
    ],
    baca=[
        "OR > 1: the event is more likely as X rises; OR < 1: less likely; OR = 1: no effect.",
        "An AUC of 0.5 equals guessing; near 1 means discriminating well.",
        "A non-significant Hosmer-Lemeshow means adequate fit.",
    ],
    jebakan=[
        "Calling the OR a relative risk.",
        "Too few events per predictor.",
        "Perfect separation makes coefficients infinite.",
    ],
    latihan="Run the sample data, compute the predicted probability for one case by hand from the coefficients, then match it with the intuition from the OR.",
    notasi=[
        "probability of the event",
        "log odds",
        "odds ratio",
        "log-likelihood",
    ],
    teori=[
        ["The logit model", [
            "For a binary response (0/1), the probability is modelled through the logit function so the result always lies between 0 and 1. A coefficient expresses the change in log-odds per unit of the predictor.",
        ]],
        ["Maximum likelihood estimation", [
            "The coefficients are estimated by maximising the log-likelihood through IRLS (Newton-Raphson) iterations. There is no closed form.",
        ]],
        ["Odds ratios and tests", [
            "The exponent of a coefficient is the odds ratio. The Wald test uses \\(z=b/SE\\); the likelihood ratio test compares the model with a model without predictors. McFadden's pseudo-R² and the AUC assess fit and discrimination.",
        ]],
    ],
    contoh=dict(
        judul="Example: from logit to probability",
        soal="Model logit = −4 + 0.5·x. Compute the probability for x = 10 and the odds ratio per unit of x.",
        data=None,
        langkah=[
            "Logit.",
            "Probability.",
            "Odds ratio.",
        ],
        simpul="At x = 10 the probability is 73.1%. Each one-unit rise in x multiplies the odds by 1.649 (up 64.9%).",
    ),
    faq=[
        ["What is the difference between odds and probability?",
         "Odds = p/(1−p). A probability of 0.731 equals odds of 2.72."],
        ["What is perfect separation?",
         "When one predictor separates 0 and 1 perfectly, the MLE is infinite; use the Firth penalty."],
        ["How large a sample is enough?",
         "Rough rule: at least 10 events per predictor."],
    ],
)

MOD_EN["regresi-probit"] = dict(
    title="Probit Regression",
    ringkas="Like logistic, but using the standard normal link function.",
    tujuan=[
        "Understand the probit link function",
        "Compare it with logit",
        "Read dose-response results",
    ],
    ide=[
        "Probit models the probability with the standard normal distribution function: Φ⁻¹(p) = β₀ + βX. Its shape is similar to logit, with slightly lighter tails.",
        "Probit is common in toxicology and dose-response tests, for example estimating the LD50, the dose that kills 50% of individuals.",
    ],
    rumus=[
        ["Model", "Φ⁻¹(p) = β₀ + β₁X"],
        ["LD50", "x = −β₀ / β₁"],
    ],
    langkah=[
        "Code the response as 0/1 or a proportion.",
        "Run the model.",
        "Read the coefficients in z-scores and the classification.",
        "Compare with logit if needed.",
    ],
    baca=[
        "A coefficient is the change in the z-score of the probability per unit of X.",
        "Logit and probit predictions are generally very similar.",
    ],
    jebakan=[
        "Reading coefficients as odds ratios.",
        "Choosing probit only out of habit.",
        "Dose data without a range containing the 50% response.",
    ],
    latihan="Run the sample data with probit and logit, then compare their predicted probabilities for several X values.",
    notasi=[
        "standard normal distribution function",
        "inverse (probit)",
        "latent variable",
    ],
    teori=[
        ["The probit model", [
            "Probit uses the standard normal distribution function as the link, rather than the logistic. Theoretically there is a continuous latent variable \\(y^*\\) and \\(y=1\\) when \\(y^*>0\\).",
        ]],
        ["Marginal effects", [
            "A probit coefficient does not directly give the change in probability. The change in probability per unit of x depends on the evaluation point, with \\(\\phi\\) the standard normal density.",
        ]],
        ["Probit versus logit", [
            "The two are nearly identical, except that the logit tails are heavier. Logit coefficients are roughly 1.6 to 1.8 times probit coefficients. Probit is used in toxicology (dose-response, LD50).",
        ]],
    ],
    contoh=dict(
        judul="Example: a probit probability",
        soal="Linear index η = 0.5.",
        data=None,
        langkah=[
            "Probability.",
            "Marginal effect with β = 0.8.",
        ],
        simpul="The probability is 69.1%; a one-unit rise in x adds about 28 percentage points of probability at this point.",
    ),
    faq=[
        ["Logit or probit?",
         "The results are nearly the same; logit makes odds interpretation easy, probit is common in bioassay."],
        ["How do I compute the LD50?",
         "The dose with probability 0.5, i.e. when η = 0."],
        ["Should dose be log-transformed?",
         "Usually yes, because the response is more symmetric on log-dose."],
    ],
)

MOD_EN["regresi-logistik-multinomial"] = dict(
    title="Multinomial Logistic Regression",
    ringkas="A nominal response with three or more classes.",
    tujuan=[
        "Understand the reference class",
        "Read relative odds ratios",
        "Assess classification accuracy",
    ],
    ide=[
        "For a nominal response with no order (type of choice, disease category), the model compares each class with one reference class through a set of logit equations.",
        "Exp(β) is the relative odds ratio: the change in the odds of being in that class versus the reference class, for a one-unit rise in X.",
    ],
    rumus=[
        ["Model", "ln[P(class j) / P(reference)] = β₀ⱼ + β₁ⱼX₁ + …"],
    ],
    langkah=[
        "Determine the reference class.",
        "Run the model.",
        "Read the relative OR of each class.",
        "Check the classification accuracy.",
    ],
    baca=[
        "A relative OR is read against the reference class, not against other classes.",
        "A high accuracy must be compared with the proportion of the largest class.",
    ],
    jebakan=[
        "Using it on ordinal data (ordinal logistic is more appropriate).",
        "Classes with little data.",
        "Interpreting an OR without naming the reference.",
    ],
    latihan="Run the sample data, change the reference reading, and explain one relative odds ratio in your own words.",
    notasi=[
        "number of categories",
        "coefficient of category k versus the reference",
        "linear index of category k",
    ],
    teori=[
        ["The softmax model", [
            "A nominal response with \\(K\\) categories is modelled with one category as the reference and \\(K-1\\) logit equations. The probability of each category is formed with the softmax function and sums to one.",
        ]],
        ["Interpreting coefficients", [
            "The exponent of a coefficient is the relative risk ratio of category k versus the reference. The model assumes independence of irrelevant alternatives (IIA).",
        ]],
        ["Likelihood", [
            "The log-likelihood is the sum of the log-probabilities of the observed categories. Fit is assessed with pseudo-R², classification accuracy, and AIC.",
        ]],
    ],
    contoh=dict(
        judul="Example: softmax with three categories",
        soal="Index η = (1; 0.5; 0).",
        data=None,
        langkah=[
            "Exponents.",
            "The denominator is 5.367, hence the probabilities.",
        ],
        simpul="The first category is the most likely (50.6%); the three probabilities sum to 1.",
    ),
    faq=[
        ["What if the categories are ordered?",
         "Use ordinal logistic, which has fewer parameters."],
        ["What is IIA?",
         "The ratio of probabilities of two categories does not depend on the other categories; it is violated when there is a similar alternative."],
        ["How do I choose the reference?",
         "Choose a meaningful or the largest category; the predictions do not change."],
    ],
)
