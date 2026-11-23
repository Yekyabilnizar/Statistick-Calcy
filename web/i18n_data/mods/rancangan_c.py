from . import MOD_EN

MOD_EN["faktorial-pecahan-fractional-factorial"] = dict(
    title="Fractional Factorial",
    ringkas="Screen many factors with only some of the combinations, at the cost of aliasing.",
    tujuan=[
        "Understand the 2^(k−p) notation and generators",
        "Read the resolution and alias structure",
        "Know Lenth's method",
    ],
    ide=[
        "A full 2^k factorial balloons quickly. A 2^(k−p) fractional factorial runs only 1/2^p of all combinations, on condition that some effects are 'merged' (aliased): they cannot be distinguished from each other. The underlying assumption is the sparsity principle: higher-order interactions are generally small.",
        "Resolution expresses quality: III (main effects aliased with two-factor interactions), IV (main effects clear, two-factor interactions aliased with each other), V (main effects and two-factor interactions clear of each other).",
    ],
    rumus=[
        ["Example", "2^(5−1) with E = ABCD: 16 runs, defining relation I = ABCDE, resolution V"],
        ["Lenth's method", "estimates the error from the effects themselves when there are no error df"],
    ],
    langkah=[
        "Choose a generator and look at the alias structure.",
        "Run with the design generator, or enter the experimental data.",
        "Read the effects table and the Pareto/normal probability plot.",
        "Carry out a confirmation experiment.",
    ],
    baca=[
        "Effects that deviate from the straight line on the normal probability plot are real effects.",
        "In unreplicated designs, the test uses Lenth's method and is exploratory.",
    ],
    jebakan=[
        "Interpreting effects without paying attention to aliasing.",
        "Choosing resolution III when interactions are suspected to be important.",
        "Treating Lenth's result as proof.",
    ],
    latihan="Open the design generator, create a 2^(5−1) with generator E=ABCD, look at the defining relation and aliases, then run the analysis with the sample data.",
    notasi=[
        "fractional factorial with k factors, 2^p times smaller",
        "generator relation",
        "design resolution",
        "coded factor −1/+1",
    ],
    teori=[
        ["The idea of a fraction", [
            "A full factorial with \\(k\\) two-level factors needs \\(2^k\\) runs. A fractional factorial runs only \\(2^{k-p}\\) combinations, sacrificing some higher-order interactions that are assumed small.",
        ]],
        ["Generator relation and aliases", [
            "An additional factor is defined as an interaction of other factors, e.g. \\(D=ABC\\). The defining relation \\(I=ABCD\\) determines the alias structure: effects that cannot be distinguished. The alias of an effect is obtained by multiplying it by the defining relation, with the rule \\(A^2=I\\).",
        ]],
        ["Resolution", [
            "Resolution is the length of the shortest word in the defining relation. Resolution III: main effects aliased with two-factor interactions. Resolution IV: main effects free of aliasing with two-factor interactions, but two-factor interactions aliased with each other. Resolution V: main effects and two-factor interactions not aliased with each other.",
        ]],
        ["Estimating effects", [
            "The effect of a factor is the difference between the mean at the high and low levels; for a 2-level design with N runs, the contrast is divided by N/2.",
        ]],
    ],
    contoh=dict(
        judul="Example: 2^{4−1} with D = ABC",
        soal="Four factors, only 8 runs. Determine the defining relation, resolution, and aliases.",
        data=None,
        langkah=[
            "D = ABC, so multiply both sides by D.",
            "Word length 4, so resolution IV.",
            "Aliases of some effects.",
        ],
        simpul="Main effects are safe from two-factor interactions, but AB cannot be distinguished from CD. This fraction saves half the runs.",
    ),
    faq=[
        ["When should a fractional factorial be used?",
         "The screening stage: many factors, limited resources, and high-order interactions assumed small."],
        ["What is a resolution III design?",
         "The most economical design; main effects are aliased with two-factor interactions; only for initial screening."],
        ["How can aliases be resolved?",
         "Run the complementary fraction or a fold-over."],
    ],
)

MOD_EN["petak-terbagi-split-plot"] = dict(
    title="Split-Plot",
    ringkas="One factor on the main plot, another on the subplot, with two errors.",
    tujuan=[
        "Recognise when a split-plot is used",
        "Determine the error for each test",
        "Read an ANOVA with two errors",
    ],
    ide=[
        "A split-plot suits cases where one factor is hard to control on small units (for example irrigation or tillage), so it is placed on large plots (main plots), while the other factor is randomised on subplots inside them.",
        "Because there are two levels of randomisation, there are two errors: error (a) for the main plot and error (b) for the subplot. The subplot and its interaction are tested more precisely.",
    ],
    rumus=[
        ["Model", "Yᵢⱼₖ = μ + ρᵢ + αⱼ + δᵢⱼ + βₖ + (αβ)ⱼₖ + εᵢⱼₖ"],
        ["Test", "A is tested against error (a) = δ; B and A×B against error (b) = ε"],
    ],
    langkah=[
        "Determine the main-plot factor and the subplot factor.",
        "Record the block/replicate.",
        "Enter the data: block, main plot, subplot, response.",
        "Read the ANOVA with two errors.",
    ],
    baca=[
        "The main plot is tested against error (a), with fewer df, so it is less sensitive.",
        "The subplot and interaction are tested against error (b).",
    ],
    jebakan=[
        "Using an ordinary factorial ANOVA so the main plot is tested against the wrong error.",
        "Swapping the roles of the main-plot and subplot factors.",
        "Assuming all effects are tested with equal precision.",
    ],
    latihan="Run the sample data, note the error used for the main-plot test and for the subplot test, then compare their degrees of freedom.",
    notasi=[
        "main-plot effect",
        "subplot effect",
        "main-plot error (a)",
        "subplot error (b)",
    ],
    teori=[
        ["The two-error model", [
            "A factor that is hard to change (e.g. tillage) is placed on the main plot, a factor that is easy to change on the subplot. Because there are two levels of experimental unit, there are two errors: error (a) for the main plot and error (b) for the subplot and interaction.",
        ]],
        ["ANOVA table (RCBD, r blocks)", [
            "The main-plot factor is tested with error (a) with df \\((a-1)(r-1)\\); the subplot and interaction are tested with error (b) with df \\(a(b-1)(r-1)\\). The subplot is usually measured more precisely.",
        ]],
        ["Standard errors for post hoc tests", [
            "The difference between two subplot means within the same main plot uses error (b). The difference between two main-plot means at the same or different subplots uses a pooled error.",
        ]],
    ],
    contoh=dict(
        judul="Example: split-plot df structure",
        soal="a = 3 tillage methods (main plot), b = 4 varieties (subplot), r = 3 blocks.",
        data=[
            ["Source", "df"],
            ["Block", "2"],
            ["A (main plot)", "2"],
            ["Error (a)", "4"],
            ["B (subplot)", "3"],
            ["A×B", "6"],
            ["Error (b)", "18"],
            ["Total", "35"],
        ],
        langkah=[
            "Error (a).",
            "Error (b).",
            "Check the total.",
        ],
        simpul="Factor A is tested with only 4 error df, so it is less sensitive; B and A×B are tested with 18 df so they are more sensitive.",
    ),
    faq=[
        ["Why two errors?",
         "Because there are two sizes of experimental unit: the main plot and the subplot."],
        ["Which factor goes on the main plot?",
         "A factor that needs a large area, or one whose effect is less important to study precisely."],
        ["What happens if it is analysed as an ordinary factorial?",
         "The test for A is too optimistic (the error is too small)."],
    ],
)

MOD_EN["petak-terbagi-dua-kali-split-split-plot"] = dict(
    title="Split-Split-Plot",
    ringkas="Three nested factors with three errors.",
    tujuan=[
        "Understand three levels of randomisation",
        "Determine errors (a), (b), and (c)",
        "Interpret a three-way interaction",
    ],
    ide=[
        "A split-split-plot adds a third level: sub-subplots within the subplot. The factor at the lowest level is placed on the smallest unit.",
        "Each level has its own error. The lower the level, the more error degrees of freedom there generally are and the more sensitive the test.",
    ],
    rumus=[
        ["Test", "A against error (a); B and A×B against error (b); C, A×C, B×C, A×B×C against error (c)"],
    ],
    langkah=[
        "Assign each factor to a level, from main plot to sub-subplot.",
        "Enter the data with a block column, three factors, and the response.",
        "Read the three-error ANOVA.",
    ],
    baca=[
        "The factor at the lower level is usually tested more sensitively.",
        "A significant three-way interaction is hard to interpret; use plots and combination means.",
    ],
    jebakan=[
        "Assigning factors to the wrong level.",
        "Too few degrees of freedom in error (a).",
        "Treating it as an ordinary factorial.",
    ],
    latihan="Run the sample data and note the error used for each effect.",
    notasi=[
        "main-plot, subplot, and sub-subplot factors",
        "three errors",
    ],
    teori=[
        ["Three levels of experimental unit", [
            "An extension of the split-plot with a third factor on the sub-subplots. There are three errors: (a) for A, (b) for B and A×B, and (c) for C, A×C, B×C, and A×B×C.",
        ]],
        ["Error degrees of freedom", [
            "Each error is tied to one level of unit: the deeper the level, the more df.",
        ]],
        ["When to use it", [
            "When three factors have different difficulty of application, e.g. irrigation, variety, dose. The complexity is high, so the size of the experiment and the interpretation of interactions need to be considered.",
        ]],
    ],
    contoh=dict(
        judul="Example: df for a = 2, b = 3, c = 2, r = 3",
        soal="Compute the df of the three errors and the total.",
        data=None,
        langkah=[
            "Error (a).",
            "Error (b).",
            "Error (c).",
            "Total observations 36.",
        ],
        simpul="Factor A is tested with only 2 df, so it has almost no power.",
    ),
    faq=[
        ["Should I use a mixed model instead?",
         "Yes, a mixed model with random effects is more flexible, especially with unbalanced data."],
        ["Which is the most sensitive?",
         "Factor C (sub-subplots) is the most sensitive because it has the most error df."],
        ["What is the risk in choosing factors?",
         "The most important factor should be placed at the lowest level (smallest error)."],
    ],
)
