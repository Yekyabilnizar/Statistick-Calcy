from . import MOD_EN

MOD_EN["petak-jalur-strip-plot"] = dict(
    title="Strip-Plot",
    ringkas="Two factors applied on strips that cross each other.",
    tujuan=[
        "Recognise the strip layout",
        "Determine the three errors",
        "Distinguish it from a split-plot",
    ],
    ide=[
        "In a strip-plot, one factor is applied on horizontal strips and the other on vertical strips, so their crossing forms the interaction plot. It suits cases where both factors need machinery or large-scale treatment, for example tillage type and irrigation type.",
        "There are three errors: error (a) for the row factor, error (b) for the column factor, and error (c) for the interaction. The interaction is usually tested most precisely.",
    ],
    rumus=[
        ["Test", "A against error (a); B against error (b); A×B against error (c)"],
    ],
    langkah=[
        "Define the row-strip and column-strip factors.",
        "Enter the data with a block column, factor A, factor B, and the response.",
        "Read the three errors in the ANOVA.",
    ],
    baca=[
        "Factors A and B are tested with fewer df than the interaction.",
        "The A × B interaction is tested against error (c).",
    ],
    jebakan=[
        "Assuming the structure is the same as a split-plot.",
        "Using the wrong error.",
        "Too few blocks so the df are small.",
    ],
    latihan="Run the sample data and compare its error structure with a split-plot.",
    notasi=[
        "row, column, and interaction errors",
        "levels of the row and column factors",
    ],
    teori=[
        ["Two crossing factors", [
            "In a strip-plot, factor A is applied as horizontal strips and factor B as vertical strips cutting across the whole block; the A×B interaction lies at the crossings of the strips. Two factors that are hard to change are handled in one design.",
        ]],
        ["Three errors", [
            "There are three errors: error (a) for A, error (b) for B, and error (c) for the A×B interaction. The interaction is tested with error (c), which generally has the most df.",
        ]],
        ["Comparison with a split-plot", [
            "In a split-plot, only one factor has large plots; in a strip-plot both factors are large, so the precision of the interaction is high but the precision of the main effects is low.",
        ]],
    ],
    contoh=dict(
        judul="Example: df for a = 3, b = 4, r = 3",
        soal="Compute the df of the three errors.",
        data=None,
        langkah=[
            "Error (a).",
            "Error (b).",
            "Error (c).",
        ],
        simpul="The interaction is tested with 12 df, more sensitive than the main effects (4 and 6 df).",
    ),
    faq=[
        ["An example of a strip-plot case?",
         "Varieties planted in long rows and fertilisation in crossing strips; machinery is impractical on small plots."],
        ["Why three errors?",
         "Because there are three kinds of unit: rows, columns, and crossings."],
        ["Post hoc tests?",
         "The standard error follows the appropriate error, or a weighted pooled one."],
    ],
)

MOD_EN["rancangan-tersarang-nested"] = dict(
    title="Nested Design",
    ringkas="One factor nested within another, with variance components.",
    tujuan=[
        "Distinguish nested from crossed factors",
        "Compute variance components",
        "Determine the error for each test",
    ],
    ide=[
        "Factor B is said to be nested within A if each level of B appears under only one level of A, for example trees within locations or plots within villages. Therefore there is no A × B interaction; what exists is the effect B(A).",
        "This design is often used to partition variability into each level through variance components, and the nested factor is often random.",
    ],
    rumus=[
        ["Model", "Yᵢⱼₖ = μ + αᵢ + β₍ᵢ₎ⱼ + ε₍ᵢⱼ₎ₖ"],
        ["df", "A a − 1; B(A) a(b − 1); error ab(n − 1)"],
    ],
    langkah=[
        "Arrange the data hierarchically: upper level, nested level, response.",
        "Decide whether each factor is fixed or random.",
        "Check B(A) first.",
        "Compute variance components to see the largest source of variability.",
    ],
    baca=[
        "A significant B(A) means variability among nested units is meaningful.",
        "A large variance component shows the level where most variability lies.",
    ],
    jebakan=[
        "Treating the nested factor as a crossed factor.",
        "Using the wrong error to test A.",
        "Misreading variance components as fixed effects.",
    ],
    latihan="Run the sample data and read the variance components; determine which level contributes the most variability.",
    notasi=[
        "factor A",
        "factor B nested within A",
        "replicates",
        "variance component",
    ],
    teori=[
        ["The nested model", [
            "The levels of B are meaningful only within a particular level of A (e.g. trees within an orchard, orchards within a village). There is no A×B interaction because B(j) under A1 differs from B(j) under A2.",
        ]],
        ["ANOVA table", [
            "The degrees of freedom of the nested B are the sum of the df of B within each level of A. The F test for A depends on the model: with A fixed and B random, A is tested with the MS of B(A), not the error.",
        ]],
        ["Variance components", [
            "When the factors are random, the expected mean squares make it possible to estimate variance components, which are useful for deciding at which level replicates should be added.",
        ]],
    ],
    contoh=dict(
        judul="Example: variance components",
        soal="a = 3 orchards, b = 4 trees per orchard, n = 2 leaves. Given MSA = 90, MS B(A) = 20, MSE = 8.",
        data=None,
        langkah=[
            "Test A.",
            "Component of B(A).",
            "Component of A.",
        ],
        simpul="The variability among orchards (8.75) and among trees (6) is larger than among leaves (8 per observation), so additional sampling at the orchard level is more useful.",
    ),
    faq=[
        ["What is the difference from a factorial?",
         "Factorial: all combinations exist (crossed). Nested: B exists only within a particular A."],
        ["Is there an interaction in a nested design?",
         "No, because crossed combinations do not exist."],
        ["Why does the F test for A use the MS of B(A)?",
         "Because the true replicate unit for A is B(A), not the smallest observation."],
    ],
)

MOD_EN["pengukuran-berulang-repeated-measures"] = dict(
    title="Repeated Measures",
    ringkas="The same subjects are measured repeatedly, so observations are not independent.",
    tujuan=[
        "Understand why independence is violated",
        "Understand sphericity and its corrections",
        "Read within- and between-subject effects",
    ],
    ide=[
        "Repeated measurements on the same subject are correlated, so an ordinary ANOVA is not suitable. This design tests the time effect (within-subject) and the group effect (between-subject) and their interaction, with the advantage that between-subject variation is removed from the error.",
        "A special assumption: sphericity, i.e. the variances of the differences between all pairs of time points are equal. Mauchly's test checks it; if violated, the degrees of freedom are corrected with Greenhouse-Geisser (ε) or Huynh-Feldt.",
    ],
    rumus=[
        ["Correction", "corrected df = ε × df; ε = 1 if sphericity holds"],
    ],
    langkah=[
        "Arrange the data in long format: subject, time, (group), response.",
        "Run and look at Mauchly's test.",
        "If significant, use the P with the GG or HF correction.",
        "Run post hoc tests between time points if needed.",
    ],
    baca=[
        "The corrected P is used when Mauchly's test is significant.",
        "A significant time × group interaction means the pattern of change differs between groups.",
    ],
    jebakan=[
        "Using an ordinary one-way ANOVA.",
        "Ignoring sphericity.",
        "Missing data at some time points reduces the usable subjects.",
    ],
    latihan="Run the sample data and compare the uncorrected P with the Greenhouse-Geisser corrected P; does the conclusion change?",
    notasi=[
        "random subject effect",
        "time/treatment effect",
        "Greenhouse-Geisser correction factor",
        "variance of differences between times",
    ],
    teori=[
        ["The model and correlation across time", [
            "The same subjects are measured repeatedly so the measurements are correlated. The model contains a random subject effect; the remaining error is the subject × time interaction.",
        ]],
        ["Sphericity", [
            "The F test in RM-ANOVA assumes sphericity: the variances of the differences between all pairs of time points are equal. Mauchly's test checks it. If violated, the degrees of freedom are multiplied by a factor \\(\\epsilon\\) (Greenhouse-Geisser or Huynh-Feldt).",
        ]],
        ["Decomposition of the sum of squares", [
            "Between-subject variability is removed from the error, so the time test is more sensitive than an ordinary ANOVA. With n subjects and k time points:",
        ]],
        ["Modern alternatives", [
            "Mixed models with a covariance structure (AR1, unstructured) are more flexible and can handle missing data. For non-normal data, use GEE or GLMM.",
        ]],
    ],
    contoh=dict(
        judul="Example: RM-ANOVA df",
        soal="n = 10 subjects measured at k = 4 time points, Greenhouse-Geisser ε = 0.6.",
        data=None,
        langkah=[
            "Time and error df without correction.",
            "Correct with ε.",
        ],
        simpul="The F test is compared with F(1.8; 16.2), so it is more conservative than F(3; 27).",
    ),
    faq=[
        ["Why not use an ordinary ANOVA?",
         "Observations on the same subject are not independent; the error would be wrong."],
        ["If sphericity is violated?",
         "Use the GG/HF correction, MANOVA, or a mixed model."],
        ["A subject is missing at one time point?",
         "Classical RM-ANOVA drops the subject; a mixed model uses all available data."],
    ],
)
