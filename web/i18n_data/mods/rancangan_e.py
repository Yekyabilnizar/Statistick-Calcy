from . import MOD_EN

MOD_EN["rancangan-cross-over"] = dict(
    title="Cross-Over Design",
    ringkas="Each subject receives all treatments in turn, in a given sequence.",
    tujuan=[
        "Understand treatment, period, and sequence effects",
        "Recognise the risk of carry-over",
        "Determine the wash-out",
    ],
    ide=[
        "In a cross-over, each subject is its own control: treatment A then B in some subjects, B then A in others. This removes between-subject variability and saves on the number of subjects.",
        "The risk is carry-over, i.e. the effect of the first-period treatment carrying into the second period. A rest period (wash-out) is placed between periods. A significant sequence effect suggests carry-over.",
    ],
    rumus=[
        ["2×2 model", "Yᵢⱼₖ = μ + ρᵢ(sequence) + πⱼ(period) + τₖ(treatment) + subject + ε"],
    ],
    langkah=[
        "Assign subjects to sequences at random.",
        "Allow a sufficiently long wash-out.",
        "Enter the data: subject, sequence, period, treatment, response.",
        "Read the treatment, period, and sequence effects.",
    ],
    baca=[
        "The treatment effect is the main target.",
        "A significant sequence/carry-over effect reduces confidence in the treatment effect.",
    ],
    jebakan=[
        "A wash-out that is too short.",
        "The period effect confounds the treatment if the sequences are unbalanced.",
        "Subjects dropping out mid-experiment.",
    ],
    latihan="Run the sample data, check the sequence effect, and write a conclusion about the possibility of carry-over.",
    notasi=[
        "period effect",
        "treatment effect",
        "residual (carry-over) effect",
        "subject",
    ],
    teori=[
        ["The idea", [
            "Each subject receives all treatments in sequence (e.g. AB and BA) with a washout period in between. The subject acts as its own control so between-subject variability drops out of the treatment comparison.",
        ]],
        ["Estimating the treatment effect in a 2×2", [
            "The treatment estimate is obtained from the period differences within each sequence. With \\(d_{AB}\\) and \\(d_{BA}\\) the mean between-period differences (period 1 minus period 2) in the AB and BA sequences:",
        ]],
        ["Carry-over test", [
            "If a residual effect exists, the treatment comparison is biased. The preliminary test uses the sum of the two periods per subject compared between sequences; if significant, only period 1 data are used.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: a 2×2 cross-over",
        soal="Mean period differences (P1−P2): sequence AB = 4.0 and sequence BA = −2.0.",
        data=None,
        langkah=[
            "Estimate the treatment difference.",
        ],
        simpul="Treatment A is on average 3 units higher than B after removing the period effect.",
    ),
    faq=[
        ["When is a cross-over suitable?",
         "Stable chronic conditions and treatment effects that fade quickly (sufficient washout)."],
        ["What is a washout?",
         "A pause between periods so that the effect of the previous treatment disappears."],
        ["What about dropouts?",
         "Subjects leaving before period 2 slightly reduce power; analyse with a mixed model."],
    ],
)

MOD_EN["ancova-analisis-kovarians"] = dict(
    title="ANCOVA (Analysis of Covariance)",
    ringkas="Compare groups after adjusting for the influence of a numeric covariate.",
    tujuan=[
        "Understand the role of the covariate",
        "Test homogeneity of slopes",
        "Read adjusted means",
    ],
    ide=[
        "ANCOVA combines ANOVA and regression. A covariate (for example initial weight) that is related to the response is adjusted for, so the error shrinks and group comparisons are fairer.",
        "The main assumption is equal regression slopes across groups (no covariate × group interaction). If violated, the adjusted means have no single meaning.",
    ],
    rumus=[
        ["Model", "Yᵢⱼ = μ + τᵢ + β(Xᵢⱼ − X̄) + εᵢⱼ"],
        ["Adjusted mean", "Ȳᵢ(adj) = Ȳᵢ − b(X̄ᵢ − X̄)"],
    ],
    langkah=[
        "Choose a covariate that is not affected by the treatment.",
        "Test homogeneity of slopes.",
        "If satisfied, read the adjusted mean comparisons.",
        "Run post hoc tests on the adjusted means.",
    ],
    baca=[
        "A non-significant covariate × group interaction: the assumption is met.",
        "Compare the raw and adjusted means to see the effect of the adjustment.",
    ],
    jebakan=[
        "A covariate that is itself affected by the treatment.",
        "Ignoring the test of homogeneity of slopes.",
        "Using a covariate unrelated to the response.",
    ],
    latihan="Run the sample data and compare the raw means with the adjusted means.",
    notasi=[
        "covariate",
        "common covariate slope",
        "covariate mean",
        "adjusted mean",
    ],
    teori=[
        ["Model", [
            "ANCOVA combines ANOVA with regression: the response is corrected for a numeric covariate (e.g. initial weight) so that the error decreases and treatment comparisons become fairer. Assuming equal slopes in all groups:",
        ]],
        ["Coefficient and adjusted means", [
            "The common slope is estimated from the within-group sums of products and squares (E denotes the error component). The adjusted mean moves each treatment mean to the covariate value of the grand mean.",
        ]],
        ["Adjusted sums of squares", [
            "The error SS is reduced by the regression on the covariate, and the error df decrease by one.",
        ]],
        ["The equal-slopes assumption", [
            "The treatment × covariate interaction test must be non-significant. If significant, ANCOVA is invalid and the treatment effect must be reported at specific covariate values.",
        ]],
    ],
    contoh=dict(
        judul="Example: adjusted means",
        soal="Three treatments; covariate means per treatment 3, 4, 5 (grand mean 4); response means 6.0; 9.0; 12.0; β̂ = 2.0.",
        data=None,
        langkah=[
            "Treatment 1.",
            "Treatment 2.",
            "Treatment 3.",
        ],
        simpul="The true differences among treatments are smaller (8, 9, 10) than they look raw (6, 9, 12), because part is due to covariate differences.",
    ),
    faq=[
        ["When should ANCOVA be used?",
         "When there is a numeric variable that is correlated with the response and not affected by the treatment."],
        ["May the covariate be affected by the treatment?",
         "No. The covariate is measured before the treatment; if affected by it, the adjustment removes part of the real effect."],
        ["How do I check for equal slopes?",
         "Add the treatment × covariate interaction and test it with F."],
    ],
)

MOD_EN["manova"] = dict(
    title="MANOVA",
    ringkas="ANOVA for several responses at once, taking the correlation among responses into account.",
    tujuan=[
        "Understand when MANOVA is used",
        "Distinguish the Pillai, Wilks, Hotelling-Lawley, and Roy statistics",
        "Read Box's M test",
    ],
    ide=[
        "When there are several correlated responses, analysing them one at a time ignores the correlation and raises the chance of a type I error. MANOVA tests differences in the mean vector among groups simultaneously.",
        "Assumptions: multivariate normality and equality of covariance matrices across groups (checked with Box's M test). The Pillai statistic is the most robust when the covariance assumption is violated.",
    ],
    rumus=[
        ["Wilks", "Λ = |E| / |H + E|"],
        ["Pillai", "V = tr[H(H + E)⁻¹]"],
    ],
    langkah=[
        "Choose responses that are theoretically related.",
        "Run MANOVA and look at Box's M.",
        "If the multivariate test is significant, look at the univariate ANOVAs with Bonferroni correction.",
        "Run post hoc tests as needed.",
    ],
    baca=[
        "A significant multivariate test means the mean vectors differ; the univariate ANOVAs indicate which response.",
        "If Box's M is significant, rely on Pillai.",
    ],
    jebakan=[
        "Uncorrelated responses so MANOVA has no benefit.",
        "A sample size too small for the number of responses.",
        "Ignoring the correction in follow-up univariate tests.",
    ],
    latihan="Run the sample data and compare the results of the four multivariate test statistics and Box's M.",
    notasi=[
        "hypothesis sums-of-squares-and-products matrix",
        "error matrix",
        "Wilks' lambda",
        "number of responses",
    ],
    teori=[
        ["Vector responses", [
            "MANOVA tests mean differences on several correlated responses at once, preserving the overall type I error. Each observation is a vector.",
        ]],
        ["Test statistics", [
            "Four common statistics are formed from the eigenvalues \\(\\lambda_s\\) of the matrix \\(\\mathbf{E}^{-1}\\mathbf{H}\\): Wilks, Pillai, Hotelling-Lawley, and Roy. Wilks is the most popular; Pillai is the most robust to violated assumptions.",
        ]],
        ["Assumptions", [
            "Multivariate normality, equality of covariance matrices (Box's M test), and independence. With small sample sizes and many responses, power drops; the number of observations per group should exceed \\(p\\).",
        ]],
        ["Follow-up", [
            "If MANOVA is significant, run univariate ANOVAs per response with Bonferroni correction, or discriminant analysis to see the combination of responses that separates the groups best.",
        ]],
    ],
    contoh=dict(
        judul="Example: Wilks from eigenvalues",
        soal="Two groups, p = 2 responses; eigenvalues of E⁻¹H: λ₁ = 1.5 and λ₂ = 0.",
        data=None,
        langkah=[
            "Wilks' lambda.",
            "Pillai.",
        ],
        simpul="A Wilks of 0.40 means 60% of the combined variability is explained by the groups; check the P value from the F transformation.",
    ),
    faq=[
        ["Why not just separate ANOVAs?",
         "That ignores the correlation among responses and inflates the type I error."],
        ["Which statistic should be used?",
         "Pillai if the assumptions are doubtful; Wilks if the assumptions are good."],
        ["What is the maximum number of responses?",
         "Aim for \\(p<n-t\\); generally few responses are substantively relevant."],
    ],
)
