from . import MOD_EN

MOD_EN["mixed-effect-model"] = dict(
    title="Mixed Effect Model",
    ringkas="Fixed and random effects for grouped or repeated data.",
    tujuan=[
        "Distinguish fixed and random effects",
        "Read the ICC",
        "Understand REML",
    ],
    ide=[
        "Grouped data (students within classes, patients within hospitals) are not independent. A mixed model adds random effects for the group (the intercept, and if needed the slope) in addition to fixed effects that are read like ordinary regression.",
        "The ICC (intraclass correlation coefficient) is the proportion of variance that comes from differences between groups. A small ICC means ordinary regression may be enough. Estimation uses REML.",
    ],
    rumus=[
        ["Model", "yᵢⱼ = xᵢⱼβ + uⱼ + εᵢⱼ"],
        ["ICC", "ICC = σ²ᵤ / (σ²ᵤ + σ²ε)"],
    ],
    langkah=[
        "Determine the group column.",
        "Determine the random effects (intercept, and slope if needed).",
        "Run and read the ICC.",
        "Read the fixed effects.",
    ],
    baca=[
        "A high ICC means large differences between groups.",
        "The marginal R² covers fixed effects only; the conditional one includes random effects.",
    ],
    jebakan=[
        "Ignoring the group structure.",
        "Too few groups to estimate the random variance.",
        "A random slope without enough data.",
    ],
    latihan="Run the sample data, read the ICC, and decide whether ordinary regression is enough.",
    notasi=[
        "random effect",
        "random effects design matrix",
        "random effect variance",
        "intraclass correlation",
    ],
    teori=[
        ["The linear mixed model", [
            "A mixed model contains fixed effects (of interest) and random effects (variation among groups, subjects, or blocks). It handles grouped data, repeated measures, and unbalanced data.",
        ]],
        ["Variance structure and the ICC", [
            "The total variance of an observation is split into between-group and error components. The correlation of two observations in the same group is the ICC.",
        ]],
        ["REML estimation", [
            "Variance components are estimated by REML, which removes the small-sample bias of MLE. Fixed effects are tested with Wald or F tests with Satterthwaite/Kenward-Roger df. Models are compared with AIC (REML is valid only if the fixed effects are the same).",
        ]],
    ],
    contoh=dict(
        judul="Example: ICC",
        soal="σ²_b = 4 (between groups), σ² = 6 (error).",
        data=None,
        langkah=[
            "ICC.",
        ],
        simpul="40% of the variance comes from between groups; two observations in the same group correlate at 0.4.",
    ),
    faq=[
        ["Fixed or random effect?",
         "Random if the levels are a sample from a larger population and you want to generalise; fixed if the levels themselves are of interest."],
        ["How do I test a random effect?",
         "A likelihood ratio test; remember the P-value on the boundary of the parameter space is more conservative (halved)."],
        ["Why not ordinary ANOVA?",
         "Ordinary ANOVA ignores the correlation within groups."],
    ],
)

MOD_EN["regresi-cox-survival"] = dict(
    title="Cox Regression (Survival)",
    ringkas="Analysis of time to event with censored data.",
    tujuan=[
        "Understand censoring, Kaplan-Meier curves, and the hazard",
        "Read the hazard ratio",
        "Check the proportional hazards assumption",
    ],
    ide=[
        "In time-to-event data (death, equipment failure), some subjects have not experienced the event by the end of observation; their time is censored. Cox regression models the hazard rate without specifying the baseline shape over time.",
        "The hazard ratio (HR) is the multiplier of the instantaneous risk per one-unit rise in X. The key assumption: the hazard ratio is constant over time (proportional hazards).",
    ],
    rumus=[
        ["Model", "h(t | x) = h₀(t)·exp(β₁x₁ + … + βₖxₖ)"],
        ["Hazard ratio", "HR = e^β"],
    ],
    langkah=[
        "Prepare the time column and the event status (1) or censored (0).",
        "Run the model.",
        "Read the HR and the C-index.",
        "Check the PH assumption and the Kaplan-Meier curves.",
    ],
    baca=[
        "HR > 1: risk rises; HR < 1: risk falls.",
        "A C-index near 1 means good discrimination.",
    ],
    jebakan=[
        "Treating censored data as events.",
        "Ignoring the PH assumption.",
        "Too few events.",
    ],
    latihan="Run the sample data and explain one hazard ratio in everyday language.",
    notasi=[
        "hazard function",
        "survival function",
        "hazard ratio",
        "event indicator (1) or censored (0)",
    ],
    teori=[
        ["The proportional hazards model", [
            "Cox regression models the hazard (instantaneous event rate) without specifying the baseline hazard \\(h_0(t)\\). Predictors multiply the hazard by a factor that is constant over time (proportional).",
        ]],
        ["Partial likelihood", [
            "Coefficients are estimated by maximising the partial likelihood, which compares the subject who has the event with all those still at risk at that time, so \\(h_0\\) drops out. Censored data take part as members of the risk set.",
        ]],
        ["The proportionality assumption", [
            "The assumption is tested with Schoenfeld residuals; if violated, use strata or interactions with time. Fit: concordance (C-index).",
        ]],
    ],
    contoh=dict(
        judul="Example: hazard ratio",
        soal="Coefficient β = 0.7 for treatment.",
        data=None,
        langkah=[
            "HR.",
        ],
        simpul="The group with x = 1 has an event rate 2.01 times that of the reference group at every time.",
    ),
    faq=[
        ["What is censoring?",
         "The subject has not experienced the event when observation ends or is lost to follow-up."],
        ["Does an HR of 2 mean survival time is twice as short?",
         "Not exactly; the HR refers to the instantaneous event rate, not the length of time."],
        ["What if there are tied times?",
         "Use tie handling (Efron or Breslow)."],
    ],
)

MOD_EN["regresi-tobit"] = dict(
    title="Tobit Regression",
    ringkas="Regression for censored data, for example many responses with a value of zero.",
    tujuan=[
        "Understand left/right censoring",
        "Read latent coefficients and marginal effects",
        "Compare with OLS",
    ],
    ide=[
        "In censored data, the true response is not observed beyond a certain limit (for example spending that cannot be negative, or a measuring instrument with an upper limit). OLS on such data is biased.",
        "Tobit models the true latent variable y*, with the observed y = the limit if y* passes the limit. Coefficients describe the relationship on y*, whereas marginal effects describe the effect on the observed value.",
    ],
    rumus=[
        ["Latent model", "y* = xβ + ε, y = max(0, y*)"],
    ],
    langkah=[
        "Determine the censoring limit (left/right).",
        "Run the model.",
        "Read the latent coefficients and marginal effects.",
        "Compare with OLS.",
    ],
    baca=[
        "Use marginal effects for interpretation on the observed value.",
        "OLS usually underestimates the effect when there is a lot of censoring.",
    ],
    jebakan=[
        "Reading Tobit coefficients as effects on the observed Y.",
        "A wrong censoring limit.",
        "Violated normality of errors.",
    ],
    latihan="Run the sample data and compare the Tobit coefficients with OLS.",
    notasi=[
        "latent variable",
        "censoring limit",
        "standard normal density and distribution",
        "inverse Mills ratio",
    ],
    teori=[
        ["The censored latent variable", [
            "Tobit is used when the response is censored at a limit (e.g. zero): many observations pile up at the limit even though the underlying variable is continuous. Only \\(y=\\max(y^*,c)\\) is observed.",
        ]],
        ["Likelihood", [
            "Uncensored observations contribute the density, censored observations contribute the probability of falling below the limit (c = 0).",
        ]],
        ["Marginal effects", [
            "The coefficient \\(\\beta\\) is the effect on the latent variable. The effect on the observed value depends on the probability of being uncensored and the conditional mean:",
        ]],
    ],
    contoh=dict(
        judul="Example: conditional mean",
        soal="μ = xβ = 1 and σ = 2 with censoring at zero.",
        data=None,
        langkah=[
            "a = μ/σ.",
            "Mills ratio.",
            "Conditional mean given uncensored.",
        ],
        simpul="About 69% of observations are uncensored, and their mean is 2.02. The marginal effect on the observed mean = β × 0.691.",
    ),
    faq=[
        ["Why not OLS?",
         "OLS on censored data is biased toward zero."],
        ["Tobit or two-part (hurdle)?",
         "Tobit assumes the decision 'not zero' and the size of the value are determined by the same process."],
        ["Is normality important?",
         "Yes; Tobit is sensitive to violations of normality and unequal variance."],
    ],
)
