from . import MOD_EN

MOD_EN["rancangan-graeco-latin"] = dict(
    title="Graeco-Latin Square Design",
    ringkas="An extension of the Latin square for three blocking sources, using two orthogonal Latin squares.",
    tujuan=[
        "Understand the structure of rows, columns, and Greek letters",
        "Read an ANOVA with a very small error",
        "Be aware of the limits on the number of treatments",
    ],
    ide=[
        "This design superimposes two orthogonal Latin squares: one for the treatment (Latin letters) and one for a third blocking factor (Greek letters). Now three sources of variability are controlled.",
        "The size t must be at least 4 and no such design exists for t = 6 (t = 3 leaves no error degrees of freedom), and the error df are small, namely (t − 1)(t − 3). For t = 4 there are only 3 error df.",
    ],
    rumus=[
        ["Model", "Yᵢⱼₖₗ = μ + ρᵢ + γⱼ + τₖ + ωₗ + εᵢⱼₖₗ"],
        ["Error df", "(t − 1)(t − 3)"],
    ],
    langkah=[
        "Construct two orthogonal Latin squares.",
        "Record the row, column, treatment, and Greek letter of each unit.",
        "Enter the data and run.",
        "Read the treatment effect carefully because the error df are small.",
    ],
    baca=[
        "The treatment effect is tested after the three blocking effects are removed.",
        "A small error makes the test underpowered; only large effects will be detected.",
    ],
    jebakan=[
        "Using this design when only one or two sources of variability really exist.",
        "Assuming the design is always better than a Latin square.",
        "Interactions between factors are ignored.",
    ],
    latihan="Run the sample data, look at the ANOVA table, and compare the error df with a Latin square at the same t.",
    notasi=[
        "effect of the Latin treatment",
        "effect of the Greek letter (third blocking factor)",
        "size",
        "(t−1)(t−3)",
    ],
    teori=[
        ["Two orthogonal Latin squares", [
            "The Graeco-Latin design superimposes two orthogonal Latin squares so that every pair of a Latin and a Greek letter appears exactly once. In this way three sources of blocking can be controlled together with the treatment.",
        ]],
        ["Degrees of freedom", [
            "There are now four components of \\(t-1\\) df each, so the error is left with only \\((t-1)(t-3)\\). A 3×3 square has no error df, and for 6×6 there is no orthogonal pair.",
        ]],
        ["Conditions for existence", [
            "Pairs of orthogonal Latin squares exist for all sizes \\(t\\ge3\\) except \\(t=6\\). So the available sizes are 3, 4, 5, 7, 8, 9, and so on; for \\(t=3\\) no error df remain.",
        ]],
    ],
    contoh=dict(
        judul="Example: df of a Latin square vs a Graeco-Latin square",
        soal="Compare the error df for t = 5 in the two designs.",
        data=None,
        langkah=[
            "Latin square.",
            "Graeco-Latin.",
        ],
        simpul="Adding one blocking factor sacrifices 4 error df.",
    ),
    faq=[
        ["When should a Graeco-Latin design be used?",
         "When there are three sources of variability at once and resources are limited; e.g. day, operator, and machine."],
        ["What is the risk?",
         "Very few error df, and the no-interaction assumption becomes stronger."],
        ["Are there alternatives?",
         "Yes: a Latin square or RCBD with combined blocks, or a mixed model."],
    ],
)

MOD_EN["blok-tidak-lengkap-bib-lattice"] = dict(
    title="Incomplete Blocks (BIB / Lattice)",
    ringkas="When a block cannot hold all treatments: each block holds only some, but in a balanced way.",
    tujuan=[
        "Understand the balanced incomplete block (BIB)",
        "Know the parameters t, b, r, k, λ",
        "Read block-adjusted means",
    ],
    ide=[
        "When the number of treatments is larger than the size of a homogeneous block, each block holds k < t treatments. In a BIB every pair of treatments meets in the same block λ times, so all pairs are compared with the same precision.",
        "Because treatments do not appear in all blocks, raw means are biased by blocks. The means must be adjusted using inter-block information. The Lattice design is a family of incomplete blocks for t = k².",
    ],
    rumus=[
        ["Relationships", "bk = rt and λ(t − 1) = r(k − 1)"],
        ["Efficiency", "E = λt / (rk)"],
        ["Adjusted mean", "computed from the raw mean minus the block effect"],
    ],
    langkah=[
        "Choose a design with parameters (t, b, r, k, λ) that satisfy the relationships above.",
        "Enter the data: treatment, block, response.",
        "Read the block-adjusted means.",
        "Make pairwise comparisons with the chosen correction.",
    ],
    baca=[
        "Compare the adjusted means, not the raw means.",
        "An efficiency below 1 shows the price paid for using small blocks.",
    ],
    jebakan=[
        "Using raw means for comparisons.",
        "Designing unbalanced blocks without realising it.",
        "Ignoring the block effect in the degrees of freedom.",
    ],
    latihan="Run the sample data. Compare the raw means and the adjusted means for a few treatments, then explain the difference.",
    notasi=[
        "number of treatments",
        "number of blocks",
        "block size (k < t)",
        "replicates per treatment",
        "number of blocks containing the same pair of treatments",
        "efficiency factor",
    ],
    teori=[
        ["BIB parameter relationships", [
            "In a BIB (balanced incomplete block) each block holds only \\(k<t\\) treatments, but every pair of treatments appears together \\(\\lambda\\) times. The parameters are tied by two equations; both must be integers.",
        ]],
        ["Efficiency", [
            "Because comparisons are made between incomplete blocks, the precision is slightly lower than with complete blocks. The efficiency factor \\(E<1\\) expresses this; the closer to 1 the better.",
        ]],
        ["Block-adjusted means", [
            "Treatment means must be adjusted because each treatment is not in all blocks. With \\(Q_i\\) the difference between the treatment total and the average of the totals of the blocks it appears in:",
        ]],
        ["Lattice", [
            "A lattice is a special framework for \\(t=k^2\\) treatments (for example 25 varieties in blocks of 5). A simple lattice uses two sets of replicates, a balanced lattice uses \\(k+1\\). The adjustment formulas are basically the same, but the replicate structure is arranged.",
        ]],
    ],
    contoh=dict(
        judul="Example: checking BIB parameters",
        soal="t = 7 treatments, block size k = 3, b = 7 blocks. Find r, λ, and E.",
        data=None,
        langkah=[
            "From tr = bk.",
            "From λ(t−1) = r(k−1).",
            "Efficiency.",
        ],
        simpul="The design is valid (all integers) with an efficiency of 77.8% compared with complete blocks.",
    ),
    faq=[
        ["Why can't all parameters be used?",
         "Because r and λ must be integers; only certain combinations exist."],
        ["When should a BIB be chosen?",
         "When there are too many treatments for one homogeneous block, for example twin animals with only 2 per group."],
        ["What about ordinary means?",
         "Raw means are biased; use the adjusted means."],
    ],
)

MOD_EN["percobaan-faktorial"] = dict(
    title="Factorial Experiments",
    ringkas="Two or more factors studied together, including their interaction.",
    tujuan=[
        "Distinguish main effects from interaction",
        "Read a factorial ANOVA",
        "Interpret a significant interaction",
    ],
    ide=[
        "In a factorial, the treatments are combinations of all levels of each factor. Its advantages: it is efficient (each observation gives information about all factors) and it makes it possible to detect interaction, i.e. when the effect of one factor depends on the level of another.",
        "The base design may be a CRD or an RCBD. The calculator supports two to four factors with all interactions, and a block option.",
    ],
    rumus=[
        ["Two-factor model", "Yᵢⱼₖ = μ + αᵢ + βⱼ + (αβ)ᵢⱼ + εᵢⱼₖ"],
        ["df", "A a − 1; B b − 1; A×B (a − 1)(b − 1)"],
    ],
    langkah=[
        "Define the factors and their levels.",
        "Make sure all combinations have replicates.",
        "Enter the data: response and factor columns (and block if any).",
        "Check the interaction first.",
    ],
    baca=[
        "If the interaction is significant, interpret the combination means; main effects can be misleading.",
        "If the interaction is not significant, interpret each main effect.",
        "Interaction plot: parallel lines mean no interaction, crossing lines mean strong interaction.",
    ],
    jebakan=[
        "Looking only at main effects when the interaction is significant.",
        "Combinations without replicates, so the interaction cannot be tested.",
        "Adding too many factors so that the number of treatments balloons.",
    ],
    latihan="Run the sample data, look at the interaction in the table and chart, then explain in your own words whether the effect of one factor depends on the other.",
    notasi=[
        "main effects of factors A and B",
        "A×B interaction",
        "levels of factors A and B",
        "replicates",
    ],
    teori=[
        ["Model and effects", [
            "A factorial experiment tests several factors at once, with all combinations of levels. Besides main effects, the model contains interaction: if non-zero, the effect of one factor depends on the level of the other.",
        ]],
        ["Decomposition and df", [
            "The treatment sum of squares is split into three orthogonal components. The interaction degrees of freedom are the product of the df of its main effects.",
        ]],
        ["Simple effects and main effects", [
            "The simple effect of A is the effect of A at one level of B; the main effect is their average. If the interaction is significant, main effects are misleading and interpretation is done through simple effects.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: a 2×2 factorial in a CRD",
        soal="Factor A (two varieties) × B (two doses), r = 3. Cell means: a1b1 = 11, a1b2 = 17, a2b1 = 14, a2b2 = 23; within-cell error 8 (df 8).",
        data=[
            ["", "b1", "b2", "Mean of A"],
            ["a1", "11", "17", "14"],
            ["a2", "14", "23", "18.5"],
            ["Mean of B", "12.5", "20", "16.25"],
        ],
        langkah=[
            "Main effect of A (6 observations per level).",
            "Main effect of B.",
            "Interaction from the remainder of the treatment SS.",
            "MSE = 8/8 = 1, so F for A, B, AB.",
        ],
        simpul="All three are significant. Because the interaction is significant, the dose effect is larger for variety 2 (difference 9) than for variety 1 (difference 6).",
    ),
    faq=[
        ["Why is a factorial better than a one-factor experiment?",
         "It is efficient (each observation serves all effects) and makes it possible to estimate interaction."],
        ["If the interaction is significant, what is reported?",
         "Simple effects or the table of cell means, not the main effects."],
        ["What are the error df?",
         "\\(ab(r-1)\\) in a CRD; \\((ab-1)(r-1)\\) in an RCBD."],
    ],
)
