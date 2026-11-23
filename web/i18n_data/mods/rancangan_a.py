from . import MOD_EN

MOD_EN["rancangan-acak-lengkap"] = dict(
    title="Completely Randomised Design (CRD)",
    ringkas="The simplest design: treatments are fully randomised over homogeneous experimental units.",
    tujuan=[
        "Know when a CRD is suitable",
        "Understand the model and the one-factor ANOVA table",
        "Carry out and read post hoc tests",
    ],
    ide=[
        "A CRD is used when the experimental units are fairly uniform (controlled greenhouse, homogeneous material, animals of the same kind). All treatments are assigned to experimental units at random without blocking.",
        "Its strengths are simplicity and flexibility: the number of replicates may differ between treatments, and the error degrees of freedom are large. Its weakness is that if the environment is not really homogeneous, environmental variability goes into the error and lowers the sensitivity of the test.",
    ],
    rumus=[
        ["Model", "Yᵢⱼ = μ + τᵢ + εᵢⱼ"],
        ["df", "treatment t − 1; error n − t; total n − 1"],
        ["Test", "F = treatment MS / error MS"],
    ],
    langkah=[
        "Randomise the treatments over all experimental units.",
        "Measure the response and enter the data (treatment column, response column).",
        "Check the assumptions: normality and homogeneity of variance.",
        "Read the ANOVA table, then run a post hoc test if F is significant.",
    ],
    baca=[
        "Look at the treatment P-value; significant means some treatments differ.",
        "A small CV means a precise experiment.",
        "The letter notation shows groups of equivalent treatments.",
    ],
    jebakan=[
        "Using a CRD when there is a clear gradient in location or time (use an RCBD).",
        "Dropping lost replicates without recording it.",
        "Ignoring the assumption checks.",
    ],
    latihan="Load the sample data, run it, then test the effect of the post hoc test: switch to Tukey and see whether the letter grouping changes. Then change one data value to be very large and see its effect on F and the assumptions.",
    notasi=[
        "observation of treatment i, replicate j",
        "grand mean",
        "effect of treatment i",
        "error",
        "number of treatments and replicates",
    ],
    teori=[
        ["Linear model and assumptions", [
            "A CRD is used when the experimental units are homogeneous so that treatments can be assigned at random to all units. Each observation is modelled as the grand mean, a treatment effect, and a random error. In the fixed-effects model, the treatment effects are constrained to sum to zero.",
        ]],
        ["The CRD ANOVA table", [
            "The correction factor \\(FK\\) is the squared grand total divided by the number of observations. Sums of squares are computed from the CF, so there is no need to compute deviations one by one. The error degrees of freedom \\(t(r-1)\\) come from \\(tr-1\\) minus \\(t-1\\).",
        ]],
        ["Unequal replicates", [
            "If treatment i has \\(r_i\\) replicates, the formulas adjust. The standard error of the difference of two means also changes, so post hoc tests use the harmonic mean or pairwise calculations.",
        ]],
        ["Efficiency and when a CRD is appropriate", [
            "A CRD is the simplest and gives the most error degrees of freedom, but all unit variability enters the error. If the land or material is not homogeneous, the error balloons and an RCBD is better.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: feeds in a CRD",
        soal="Weight gain (kg) of three feeds with four animals per feed. Complete the ANOVA table.",
        data=[
            ["Feed", "R1", "R2", "R3", "R4", "Total"],
            ["A", "5", "6", "7", "6", "24"],
            ["B", "8", "9", "7", "8", "32"],
            ["C", "10", "11", "9", "10", "40"],
        ],
        langkah=[
            "Grand total 96, number of observations 12.",
            "The sum of squares of all values is 806.",
            "Treatment sum of squares from each feed total.",
            "Error, mean squares, and F.",
        ],
        simpul="The feed has a highly significant effect. CV = √0.667 / 8 × 100% = 10.2%.",
    ),
    faq=[
        ["When is a CRD chosen?",
         "When the experimental units are uniform, for example a laboratory experiment or a controlled greenhouse."],
        ["May a CRD be used on sloping land?",
         "Not recommended. A slope creates a fertility gradient that accumulates in the error; use an RCBD with blocks cutting across the slope."],
        ["What is the minimum number of replicates?",
         "Aim for at least 12 error df; for example with 4 treatments, \\(t(r-1)\\ge12\\) means \\(r\\ge4\\)."],
    ],
)

MOD_EN["rancangan-acak-kelompok"] = dict(
    title="Randomised Complete Block Design (RCBD)",
    ringkas="Control one source of variability by grouping similar units.",
    tujuan=[
        "Decide when blocking is useful",
        "Read ANOVA with a block effect",
        "Assess the relative efficiency compared with a CRD",
    ],
    ide=[
        "In an RCBD, the experimental units are divided into blocks that are homogeneous within, for example by location, day, or initial weight. Each treatment appears once in every block and is randomised within the block.",
        "Variability between blocks is removed from the error, so the treatment test is more sensitive if the blocks really differ.",
    ],
    rumus=[
        ["Model", "Yᵢⱼ = μ + τᵢ + βⱼ + εᵢⱼ"],
        ["df", "treatment t − 1; block b − 1; error (t − 1)(b − 1)"],
        ["Relative efficiency", "RE = [(b − 1)·MSB + b(t − 1)·MSE] / [(bt − 1)·MSE]"],
    ],
    langkah=[
        "Form blocks based on a known source of variability.",
        "Randomise treatments separately within each block.",
        "Enter the data: treatment, block, response.",
        "Read the ANOVA, then run a post hoc test on treatments.",
    ],
    baca=[
        "RE > 1 means an RCBD is more efficient than a CRD for these data.",
        "A non-significant block effect does not mean blocks should be dropped from the analysis; the design already uses them.",
        "The treatment × block interaction is assumed absent; an interaction plot helps check this.",
    ],
    jebakan=[
        "Using blocks unrelated to the variability of the response.",
        "Missing data in one cell makes the table unbalanced.",
        "Interpreting blocks as treatments.",
    ],
    latihan="Run the sample data, look at the block effect and the relative efficiency, then compare the concept with a CRD on the same data.",
    notasi=[
        "effect of block j",
        "number of blocks",
        "(t−1)(b−1)",
        "relative efficiency of the RCBD versus the CRD",
    ],
    teori=[
        ["The RCBD model", [
            "Experimental units are grouped so that they are fairly homogeneous within a block; each treatment appears once in every block. The block effect is removed from the error.",
        ]],
        ["Decomposition of the sum of squares", [
            "Besides the treatment component, there is a block component. The error is the remainder, with degrees of freedom equal to the product \\((t-1)(b-1)\\).",
        ]],
        ["Relative efficiency versus a CRD", [
            "If blocking is effective, the error variance falls. The relative efficiency estimates how many times as many CRD replicates would be needed to match the precision of the RCBD. A value above 1 means blocking pays off.",
        ]],
        ["Missing data", [
            "If one observation is missing, its value is estimated with the formula below, then the error df is reduced by one. T is the total of the treatment with the missing value, B the total of its block, and G the grand total of the available observations.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: an RCBD with four blocks",
        soal="The same feed data, now arranged in 4 blocks (dams).",
        data=[
            ["Feed", "B1", "B2", "B3", "B4"],
            ["A", "5", "6", "7", "6"],
            ["B", "8", "9", "7", "8"],
            ["C", "10", "11", "9", "10"],
        ],
        langkah=[
            "Block totals: 23, 26, 23, 24. Block SS.",
            "Treatment SS stays 32, total 38, so the error.",
            "F for treatment and block.",
        ],
        simpul="The treatment is significant. The block is not significant (F = 1.0), so blocking did not help here and the error df fell from 9 to 6.",
    ),
    faq=[
        ["What should I do if the block is not significant?",
         "Still analyse it as an RCBD; blocking is part of the design, not a decision made after seeing the results."],
        ["May there be a treatment × block interaction?",
         "The RCBD model assumes none. If you suspect one, use an interaction plot or Tukey's additivity test."],
        ["Why are the error df fewer than in a CRD?",
         "Because \\(b-1\\) degrees of freedom are used for blocks. This price is paid for a smaller error."],
    ],
)

MOD_EN["rancangan-bujur-sangkar-latin"] = dict(
    title="Latin Square Design",
    ringkas="Control two sources of variability (rows and columns) at once.",
    tujuan=[
        "Recognise the layout of a Latin square",
        "Read a three-effect ANOVA",
        "Know its limitations",
    ],
    ide=[
        "A Latin square is t × t: each treatment appears exactly once in every row and every column. It suits two perpendicular gradients, for example soil fertility from north to south and slope from east to west.",
        "The number of replicates equals the number of treatments, so the design is only practical for t of roughly 3 to 8, and no interaction among rows, columns, and treatments is assumed.",
    ],
    rumus=[
        ["Model", "Yᵢⱼₖ = μ + ρᵢ + γⱼ + τₖ + εᵢⱼₖ"],
        ["df", "treatment, row, column each t − 1; error (t − 1)(t − 2)"],
    ],
    langkah=[
        "Construct a Latin square and randomise its rows and columns.",
        "Record the row, column, and treatment of each unit.",
        "Enter the data with three grouping columns and one response.",
        "Read the ANOVA and continue with a post hoc test.",
    ],
    baca=[
        "The treatment is tested after the effects of rows and columns are removed.",
        "A significant row or column effect shows the control was useful.",
    ],
    jebakan=[
        "With a small t, the error df are very few (t = 3 gives only 2).",
        "Missing data make the analysis more complicated.",
        "Ignoring the possibility of interaction.",
    ],
    latihan="Run the sample data and notice that every treatment appears once in each row and column. Compare the error df with an RCBD for the same number of treatments.",
    notasi=[
        "row and column effects",
        "size of the square (number of treatments = rows = columns)",
        "(t−1)(t−2)",
    ],
    teori=[
        ["Model and layout", [
            "This design controls two directions of variability at once (rows and columns). Each treatment appears exactly once in every row and every column. It requires \\(t\\times t\\) units.",
        ]],
        ["The ANOVA table", [
            "The total degrees of freedom \\(t^2-1\\) are split into rows, columns, treatments (each \\(t-1\\)) and error \\((t-1)(t-2)\\). Because the error gets few df for small \\(t\\), the design is generally used for \\(t\\) between 4 and 8.",
        ]],
        ["Efficiency and limitations", [
            "The efficiency of the Latin square relative to an RCBD with rows as blocks shows the benefit of controlling columns. The design assumes no interaction among rows, columns, and treatments.",
        ]],
    ],
    contoh=dict(
        judul="Example: degrees of freedom of a 4×4 Latin square",
        soal="Set out the df table for a Latin square with 4 treatments.",
        data=[
            ["Source", "df"],
            ["Row", "3"],
            ["Column", "3"],
            ["Treatment", "3"],
            ["Error", "6"],
            ["Total", "15"],
        ],
        langkah=[
            "Total units 16, total df 15.",
            "The error is the remainder.",
        ],
        simpul="Only 6 df for error at t = 4, so the test is underpowered; repeat the square if needed.",
    ),
    faq=[
        ["When is a Latin square used?",
         "When there are two perpendicular sources of variability, e.g. fertility from north to south and moisture from east to west."],
        ["Does it need randomising?",
         "Yes: choose a standard Latin square at random, then randomise the rows, columns, and treatment assignment."],
        ["Why is t = 3 rarely used?",
         "The error df are only 2, so the critical F value is very large (19.0) and the test has almost no power."],
    ],
)
