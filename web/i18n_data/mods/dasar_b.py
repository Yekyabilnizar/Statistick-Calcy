from . import MOD_EN

MOD_EN["dasar-prinsip-rancangan"] = dict(
    title="Principles of Experimental Design",
    ringkas="Replication, randomisation, and local control: the three pillars that make causal conclusions valid.",
    tujuan=[
        "Define experimental unit, factor, level, and treatment",
        "Apply replication, randomisation, and blocking",
        "Avoid pseudoreplication",
    ],
    ide=[
        "An experiment applies treatments to experimental units, then measures a response. A factor is the variable being compared (for example fertilizer dose), levels are its values (0, 50, 100 kg), and a treatment is a combination of levels.",
        "Replication gives an estimate of experimental error and increases precision. Randomisation removes systematic bias and justifies the statistical test. Local control, i.e. grouping similar units into blocks, separates known variability from the error.",
        "Pseudoreplication occurs when repeated observations on one experimental unit are treated as independent replicates, for example 10 leaves from one pot treated as 10 replicates. A true replicate is an experimental unit that receives the treatment separately.",
    ],
    rumus=[
        ["Basic model", "Yᵢⱼ = μ + τᵢ + εᵢⱼ"],
        ["Degrees of freedom", "treatment t − 1; error t(r − 1) in a completely randomised design"],
    ],
    langkah=[
        "Define the experimental unit and the objective.",
        "Determine the factors, levels, and number of replicates.",
        "Choose the design: homogeneous → completely randomised; one source of variability → blocks; two sources → Latin square.",
        "Randomise the placement of treatments, then record the data.",
    ],
    baca=[
        "The suitable design can be seen from the data structure: a treatment column, a block column if any, and a response column.",
        "The number of replicates determines the error degrees of freedom; too few replicates make the test underpowered.",
    ],
    jebakan=[
        "Not randomising because 'it is easier to do in sequence'.",
        "Using blocks unrelated to the variability of the response.",
        "Pseudoreplication.",
    ],
    latihan="Open the Method Guide, choose the experimental situation most similar to your research, then open the suggested method.",
    notasi=[
        "number of treatments",
        "number of replicates",
        "experimental error variance",
        "effect of the i-th treatment",
        "minimum difference to be detected",
    ],
    teori=[
        ["Replication: replicates raise precision", [
            "Replication is the repetition of a treatment on separate experimental units. It is needed to estimate experimental error and to increase precision. The variance of a treatment mean falls in inverse proportion to the number of replicates; the difference of two means has twice that variance.",
        ]],
        ["Randomisation: the basis of a valid test", [
            "Randomly assigning treatments to experimental units removes systematic bias and justifies the assumption of independent errors. Without randomisation, differences in outcome may merely reflect differences in location or time, not the treatment.",
        ]],
        ["Local control: blocking", [
            "Similar experimental units are grouped into blocks. Variability between blocks is removed from the error, so the error becomes smaller and the test more sensitive. As a result, the model adds a block effect \\(\\beta_j\\), and the error degrees of freedom decrease by \\(b-1\\).",
        ]],
        ["Determining the number of replicates", [
            "The number of replicates can be determined from the minimum difference to detect \\(\\delta\\), the error standard deviation \\(\\sigma\\), the significance level, and the desired power. The approximate formula below uses normal values; in practice the result is slightly larger because the t distribution is used. As a rule of thumb, the error degrees of freedom should be at least 12 to 15.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: how many replicates are needed?",
        soal="From a pilot experiment the error standard deviation is σ ≈ 1.5 ton/ha. The researcher wants to detect a difference between two treatments of δ = 2 ton/ha with α = 0.05 and 80% power.",
        data=None,
        langkah=[
            "The z value for two-sided α = 0.05 is 1.96, and for 80% power it is 0.8416.",
            "Insert into the formula.",
            "Round up to 9 replicates. Because the normal approximation slightly understates the requirement, 9 to 10 replicates is safer.",
        ],
        simpul="About 9 to 10 replicates per treatment are needed to detect a difference of 2 ton/ha with 80% power. With fewer replicates, a difference of that size may go undetected.",
    ),
    faq=[
        ["Are 10 measurements from one pot the same as 10 replicates?",
         "No. That is pseudoreplication. A true replicate is an experimental unit that receives the treatment separately. Repeated measurements on one pot only estimate measurement error."],
        ["When should I use blocks?",
         "When there is a source of variability known before the experiment (soil fertility, day, initial weight) that can be used to group units into homogeneous groups."],
        ["May a non-significant block be dropped from the analysis?",
         "The design already involves blocks, so the analysis still follows the design. Dropping the block after seeing the results can invalidate the test."],
    ],
)

MOD_EN["dasar-anova"] = dict(
    title="The Concept of Analysis of Variance (ANOVA)",
    ringkas="Split the total variability into treatment and error parts, then test it with F.",
    tujuan=[
        "Understand the decomposition of sums of squares",
        "Compute F and read the ANOVA table",
        "Know when ANOVA is used",
    ],
    ide=[
        "ANOVA tests whether the means of several groups are equal. The idea: the total variability in the data is split into variability between groups (due to treatment) and variability within groups (error). If the between-group variability is much larger than the error, the treatment has an effect.",
        "That comparison is made by dividing each sum of squares by its degrees of freedom, giving the mean square (MS). The F statistic = treatment MS / error MS, compared with the F distribution.",
    ],
    rumus=[
        ["Decomposition", "SS total = SS treatment + SS error"],
        ["Mean square", "MS = SS / df"],
        ["Test statistic", "F = treatment MS / error MS"],
        ["Example", "Group A: 4,5,6; B: 6,7,8; C: 8,9,10. SSTR = 24, SSE = 6, df = 2 and 6, MSTR = 12, MSE = 1, F = 12, P = 0.008 (**)"],
    ],
    langkah=[
        "Compute the grand mean and each group mean.",
        "Compute the treatment SS and the error SS.",
        "Divide by df to get the MS, then compute F.",
        "If F is significant, continue with a post hoc test.",
    ],
    baca=[
        "A large F and small P: at least one group differs from the others; ANOVA does not say which group.",
        "The CV in the table shows the precision of the experiment; the smaller the better.",
        "With a non-significant F, post hoc tests are generally not carried out.",
    ],
    jebakan=[
        "Thinking a significant F means all groups differ.",
        "Using ANOVA on data that severely violate the assumptions without transformation.",
        "Using many t-tests instead of ANOVA, which inflates the type I error.",
    ],
    latihan="Run the CRD with the sample data. Match the SS, df, MS, and F in the table with the formulas above, then change one data value and watch how F changes.",
    notasi=[
        "j-th observation in the i-th treatment",
        "mean of treatment i",
        "grand mean",
        "sum of squares and mean square",
        "F test statistic",
    ],
    teori=[
        ["Model and hypotheses", [
            "One-way analysis of variance models each observation as the grand mean plus a treatment effect and error. The null hypothesis: all treatment effects equal zero or, equivalently, all treatment means are equal.",
        ]],
        ["Decomposition of the sum of squares", [
            "The total variability is split into two disjoint parts: variability between treatments (explained by the treatment) and variability within treatments (error). This decomposition holds exactly because the cross term is zero.",
        ]],
        ["Mean squares and the F test", [
            "Dividing a sum of squares by its degrees of freedom gives a mean square. If \\(H_0\\) is true, both mean squares estimate \\(\\sigma^2\\), so their ratio is close to 1. If the treatment has an effect, the treatment mean square estimates \\(\\sigma^2\\) plus an effect term, so F grows.",
        ]],
        ["Expected mean squares", [
            "The expected value of the error MS is always \\(\\sigma^2\\), whereas the expected value of the treatment MS contains an extra term that depends on how large the treatment effects are. This is why F is tested in the right tail only.",
        ]],
        ["Relationship with the t-test", [
            "For two treatments, the F test is identical to the two-sample t-test through the relationship \\(F=t^2\\). ANOVA extends that idea to three or more groups without inflating the type I error as happens when many pairwise t-tests are performed.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: three treatments, four replicates",
        soal="Three feeds are each tested on four animals. The weight gains (kg) are recorded as in the table. Carry out the analysis of variance.",
        data=[
            ["Feed", "R1", "R2", "R3", "R4", "Mean"],
            ["A", "5", "6", "7", "6", "6"],
            ["B", "8", "9", "7", "8", "8"],
            ["C", "10", "11", "9", "10", "10"],
        ],
        langkah=[
            "Grand mean.",
            "Treatment SS: the number of replicates times the sum of squared deviations of the treatment means.",
            "Error SS: deviation of each observation from its treatment mean (each treatment contributes 2).",
            "Degrees of freedom and mean squares.",
            "The F statistic is compared with F(0.95; 2, 9) = 4.26.",
        ],
        simpul="F = 24.0 far exceeds 4.26 (P = 0.00025, highly significant): the feed affects weight gain. The next step is a post hoc test to find out which feeds differ.",
    ),
    faq=[
        ["If F is significant, do all treatments differ?",
         "No. A significant F only means at least one treatment differs. A post hoc test shows which."],
        ["What happens when the replicates are unequal?",
         "ANOVA can still be carried out; only the treatment SS formula uses \\(\\sum n_i(\\bar{y}_{i\\cdot}-\\bar{y}_{\\cdot\\cdot})^2\\). Imbalance makes the test less robust to unequal variances."],
        ["Why not just perform many t-tests?",
         "With \\(m\\) tests at \\(\\alpha=0.05\\), the probability of at least one false positive becomes \\(1-(0.95)^m\\). For three pairs it is already 14.3%. ANOVA keeps one overall test at \\(\\alpha\\)."],
    ],
)

MOD_EN["dasar-uji-lanjut"] = dict(
    title="Post Hoc Tests",
    ringkas="After a significant F: which groups differ, and how to control the type I error.",
    tujuan=[
        "Know LSD, DMRT, Tukey, Scheffé, and Dunnett",
        "Choose a post hoc test according to the goal",
        "Read the letter notation",
    ],
    ide=[
        "Post hoc tests compare means pairwise after a significant ANOVA. The more comparisons, the greater the chance of finding spurious 'differences'. A strict test controls the familywise type I error across all comparisons; a liberal test has more power but is riskier.",
        "The order from most liberal to strictest is roughly: LSD, DMRT (Duncan), Tukey (HSD), Scheffé. Dunnett is specifically for comparing all treatments against one control.",
    ],
    rumus=[
        ["LSD", "LSD = t(α/2; error df) · √(2·MSE / r)"],
        ["Example", "MSE = 1, r = 3, df = 6: LSD = 2.447 × 0.816 = 2.00; difference between means of A and B = 2 → borderline significant"],
        ["Letter notation", "means sharing the same letter are not significantly different"],
    ],
    langkah=[
        "Do it only if the F test is significant.",
        "Choose the test according to the goal: all pairs → Tukey; against a control → Dunnett; exploration → LSD or DMRT.",
        "Sort the means and assign letters.",
        "Report the test used.",
    ],
    baca=[
        "In the calculator, changing the post hoc test immediately recomputes the letters and the comparison table.",
        "The same letter = not significantly different; different letters = significantly different at the chosen α.",
    ],
    jebakan=[
        "Running LSD on many treatments without acknowledging the type I error risk.",
        "Choosing the test that gives the 'best' result.",
        "Using a post hoc test when F is not significant.",
    ],
    latihan="Run the CRD with the sample data, then switch the post hoc test from LSD to Tukey and Scheffé. Note whether any pair's letters change and explain why.",
    notasi=[
        "error mean square",
        "replicates per treatment",
        "error degrees of freedom",
        "studentised range value",
        "familywise type I error",
    ],
    teori=[
        ["The multiple comparison problem", [
            "With \\(t\\) treatments there are \\(t(t-1)/2\\) pairs. If each pair is tested separately at \\(\\alpha=0.05\\), the probability of at least one wrong conclusion across the whole family of tests (familywise type I error) far exceeds 0.05. Different post hoc tests control this at different levels of strictness.",
        ]],
        ["LSD and DMRT", [
            "The Least Significant Difference (LSD) is an ordinary t-test with pooled error: two means differ if their difference exceeds \\(LSD\\). It is the most powerful but does not control the familywise type I error. DMRT (Duncan) uses critical values that increase with the rank distance between means, so it is slightly stricter, but still liberal.",
        ]],
        ["Tukey (HSD) and Scheffé", [
            "Tukey uses the studentised range distribution and therefore controls the familywise type I error for all pairs. Scheffé is the most conservative because it protects all linear contrasts, not just pairs. Use Tukey when only pairs are of interest, and Scheffé when complex contrasts are tested after seeing the data.",
        ]],
        ["Dunnett: comparison with a control", [
            "When the goal is only to compare each treatment with one control, Dunnett is more powerful than Tukey because only \\(t-1\\) comparisons are controlled, not all pairs. The choice of control must be decided before seeing the data.",
        ]],
        ["Letter notation", [
            "After the means are sorted, treatments that are not significantly different are given the same letter. Two treatments with different letters differ significantly according to the chosen test. Always state the type of post hoc test and the significance level used.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: LSD and HSD on the feed ANOVA example",
        soal="Continue the feed ANOVA example: mean A = 6, B = 8, C = 10; MSE = 0.667; r = 4; error df = 9. Carry out the LSD and Tukey post hoc tests at α = 0.05.",
        data=None,
        langkah=[
            "Critical value t(0.975; 9) = 2.262.",
            "Value q(0.05; 3, 9) = 3.949.",
            "Compare each difference with the benchmark.",
            "Since all differences exceed both the LSD and the HSD, the three means differ significantly.",
        ],
        simpul="At α = 0.05 feeds A, B, and C differ significantly from one another: A (a), B (b), C (c). With Scheffé the benchmark is 1.685, still below 2, so the conclusion is the same.",
    ),
    faq=[
        ["Which post hoc test should I use?",
         "If all pairs are of interest, Tukey is the standard choice. If there is a control, Dunnett. LSD is reasonable only when there are few treatments or the F test is already significant and you accept a looser familywise error."],
        ["Why can the letters change when the post hoc test is changed?",
         "Because the benchmark values differ. A stricter test has a larger benchmark, so fewer pairs are significant."],
        ["May a post hoc test be done when F is not significant?",
         "Generally not, because there is no evidence of a difference at the overall level. A post hoc test after a non-significant F can produce spurious findings."],
    ],
)

MOD_EN["dasar-korelasi"] = dict(
    title="Correlation",
    ringkas="Measure the strength and direction of the linear relationship between two numeric variables.",
    tujuan=[
        "Compute and interpret the correlation coefficient r",
        "Distinguish correlation from causation",
        "Relate r to the regression R²",
    ],
    ide=[
        "The Pearson correlation coefficient r ranges from −1 to +1. The sign shows the direction, the absolute value shows the strength of the linear relationship. A value of 0 means no linear relationship, not no relationship at all.",
        "In simple linear regression, R² = r². That is, r² is the proportion of the variability in Y explained by X. A high correlation does not prove causation, because a third variable may influence both.",
    ],
    rumus=[
        ["Correlation", "r = Σ(x − x̄)(y − ȳ) / √[Σ(x − x̄)² · Σ(y − ȳ)²]"],
        ["Example", "x = 1..5, y = 2,4,5,4,5 → r = 6/√60 = 0.775; r² = 0.60"],
    ],
    langkah=[
        "Draw a scatter plot first.",
        "Compute r and its test.",
        "Check for outliers that can change r drastically.",
        "If the goal is prediction, continue to regression.",
    ],
    baca=[
        "The correlation heatmap in the regression results shows which pairs of variables are strongly correlated; pairs of X with a very high correlation are potential multicollinearity.",
        "With a small n, an apparently large r may be non-significant: r = 0.775 with n = 5 has P = 0.12.",
    ],
    jebakan=[
        "Concluding causation from correlation.",
        "Using r for a curved relationship.",
        "Ignoring outliers or a narrow data range.",
    ],
    latihan="Run Linear Regression with the sample data, look at the correlation heatmap and the scatter plot, then compare R² with the squared correlation of X and Y.",
    notasi=[
        "Pearson correlation coefficient",
        "coefficient of determination",
        "sum of products of deviations",
        "slope of the regression line",
        "Spearman correlation",
    ],
    teori=[
        ["Covariance and correlation", [
            "The sample covariance measures whether two variables move together, but its value depends on the units. The Pearson correlation standardises it so that it always lies between \\(-1\\) and \\(+1\\). The sign shows the direction; the absolute value shows the strength of the linear relationship. A value of zero only means no linear relationship, not no relationship at all.",
        ]],
        ["Testing the significance of a correlation", [
            "To test \\(H_0:\\rho=0\\), r is converted into a t statistic with \\(n-2\\) degrees of freedom. In small samples, an apparently large r may be non-significant. For a confidence interval for r, the Fisher transformation is used so that its distribution is close to normal.",
        ]],
        ["Relationship with simple linear regression", [
            "The regression line \\(y=a+bx\\) has a slope directly related to the correlation, and the squared correlation equals the coefficient of determination \\(R^2\\), the proportion of the variability in \\(y\\) explained by \\(x\\). Correlation does not prove causation: both may be influenced by a third variable.",
        ]],
        ["Spearman rank correlation", [
            "When the data are ordinal or their distribution is far from normal, or the relationship is monotonic but not linear, use the Spearman correlation, which is the Pearson correlation on the ranks of the data. If there are no ties, a simple formula uses the rank differences \\(d_i\\).",
        ]],
    ],
    contoh=dict(
        judul="Worked example: correlation and regression line",
        soal="Six observations of fertilizer dose (x) and yield (y) are shown below. Compute the correlation, slope, intercept, and their significance test.",
        data=[
            ["x", "2", "4", "5", "7", "8", "10"],
            ["y", "3", "6", "7", "10", "11", "14"],
        ],
        langkah=[
            "Means: x̄ = 6 and ȳ = 8.5. Sums of squares and cross-products of deviations:",
            "Correlation.",
            "Slope and intercept.",
            "Correlation test with df = 4.",
        ],
        simpul="The relationship between x and y is almost perfectly linear (r = 0.999; R² = 99.8%). The regression line is ŷ = 0.357 + 1.357x: each additional unit of dose raises the yield by 1.357 units on average.",
    ),
    faq=[
        ["Does a high correlation mean x causes y?",
         "No. Correlation only shows association. Causation requires a design (randomisation) or a strong substantive argument."],
        ["Why is the r from my data not significant even though it looks large?",
         "In small samples, a large r can occur by chance. Example: r = 0.775 with n = 5 only has P = 0.12."],
        ["When should I use Spearman rather than Pearson?",
         "When the data are ordinal, there are strong outliers, or the relationship is monotonic but curved. Spearman uses ranks so it is resistant to outliers."],
    ],
)
