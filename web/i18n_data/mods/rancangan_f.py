from . import MOD_EN

MOD_EN["response-surface-methodology-rsm"] = dict(
    title="Response Surface Methodology (RSM)",
    ringkas="Find the optimum process conditions with a quadratic model in several numeric factors.",
    tujuan=[
        "Understand the CCD and Box-Behnken designs",
        "Read the quadratic model and lack-of-fit",
        "Interpret the stationary point and contours",
    ],
    ide=[
        "RSM models the response as a quadratic function of several coded numeric factors. The CCD (central composite design) adds axial points and centre points to a factorial; Box-Behnken does not use the cube corners, so it is more economical and safer.",
        "The stationary point is where the gradient is zero. Its type (maximum, minimum, saddle) is determined by the signs of the eigenvalues of the quadratic coefficient matrix.",
    ],
    rumus=[
        ["Quadratic model", "Y = β₀ + Σβᵢxᵢ + Σβᵢᵢxᵢ² + Σβᵢⱼxᵢxⱼ + ε"],
        ["Stationary point", "x₀ = −½ B⁻¹ b"],
    ],
    langkah=[
        "Choose a CCD or Box-Behnken with the design generator.",
        "Run the experiment and enter the coded data.",
        "Check the model P, predicted R², and lack-of-fit.",
        "Interpret the stationary point and contour plot, then run a confirmation.",
    ],
    baca=[
        "A non-significant lack-of-fit means the model is adequate.",
        "A stationary point outside the experimental region should not be trusted; use a constrained optimum.",
    ],
    jebakan=[
        "Extrapolating outside the experimental region.",
        "Too few centre points to estimate pure error.",
        "Treating the optimum as truth without confirmation.",
    ],
    latihan="Create a CCD design with the generator, then run the sample data and read the contours and the stationary point.",
    notasi=[
        "coded factors",
        "second-order model coefficients",
        "vector of linear coefficients",
        "matrix of quadratic coefficients",
    ],
    teori=[
        ["The second-order model", [
            "RSM looks for the combination of factors that optimises the response. Near the optimum, the surface is approximated by a second-order polynomial containing linear, quadratic, and interaction effects. Typical designs: central composite (CCD) and Box-Behnken.",
        ]],
        ["The stationary point", [
            "In matrix notation, the stationary point is obtained by setting the gradient to zero. The response at this point is computed by substitution.",
        ]],
        ["Canonical analysis", [
            "The eigenvalues \\(\\lambda_i\\) of the matrix \\(\\mathbf{B}\\) determine the type of stationary point: all negative means a maximum, all positive means a minimum, mixed signs mean a saddle point.",
        ]],
        ["Factor coding and lack of fit", [
            "Factors are coded so they are comparable. The lack-of-fit test uses replicated centre points.",
        ]],
    ],
    contoh=dict(
        judul="Example: the optimum of two factors",
        soal="Coded model: ŷ = 10 + 2x₁ + 3x₂ − x₁² − 2x₂² (no interaction).",
        data=None,
        langkah=[
            "Set the partial derivatives to zero.",
            "The response at that point.",
            "The quadratic coefficients −1 and −2 are negative so the point is a maximum.",
        ],
        simpul="The optimum is at x₁ = 1, x₂ = 0.75 with a predicted response of 12.125.",
    ),
    faq=[
        ["CCD or Box-Behnken?",
         "A CCD contains axial points and can be built in stages; Box-Behnken uses fewer runs with no extreme points."],
        ["What if the stationary point is far outside the experimental region?",
         "Do not extrapolate; follow the path of steepest ascent to a new region."],
        ["What are the centre points for?",
         "Estimating pure error and testing for curvature."],
    ],
)

MOD_EN["rancangan-campuran-mixture"] = dict(
    title="Mixture Design",
    ringkas="The response depends on component proportions that always total 100%.",
    tujuan=[
        "Understand the proportion-sum constraint",
        "Read the Scheffé model",
        "Interpret synergy and antagonism",
    ],
    ide=[
        "In a mixture (feed formulation, dough, pesticide), the component proportions sum to 1, so the components are not free. The regression model is built without an intercept with mixture terms (the Scheffé model).",
        "The linear coefficients give the response of the pure component. A positive interaction coefficient indicates synergy (the blend is better than the linear average), a negative one indicates antagonism.",
    ],
    rumus=[
        ["Constraint", "x₁ + x₂ + … + x_q = 1"],
        ["Quadratic model", "Y = Σβᵢxᵢ + Σβᵢⱼxᵢxⱼ"],
    ],
    langkah=[
        "Define the components and their proportion limits.",
        "Enter the proportion and response data.",
        "Read the coefficients and the triangle diagram.",
        "Find the optimum composition and confirm.",
    ],
    baca=[
        "The triangle diagram shows the response surface in composition space.",
        "The optimum is the composition with the best response within the limits.",
    ],
    jebakan=[
        "Adding an intercept, which makes the model unidentifiable.",
        "Proportions that do not sum to 1.",
        "Interpreting coefficients as in ordinary regression.",
    ],
    latihan="Run the sample data and read the mixture coefficients; identify the pair of components that is synergistic.",
    notasi=[
        "proportion of component i",
        "number of components",
        "mixture coefficient",
    ],
    teori=[
        ["The mixture constraint", [
            "In a mixture experiment, the response depends on the proportions of the components, not absolute amounts. Proportions are non-negative and sum to one, so the experimental region is a simplex, not a cube.",
        ]],
        ["The Scheffé model", [
            "Because the proportions sum to a fixed value, the model has no separate intercept. The Scheffé linear and quadratic models:",
        ]],
        ["Interpreting the coefficients", [
            "\\(\\beta_i\\) is the predicted response of pure component i. A positive coefficient \\(\\beta_{ij}\\) indicates synergy, a negative one antagonism, compared with the weighted average of the pure responses.",
        ]],
        ["Designs", [
            "A simplex-lattice \\(\\{q,m\\}\\) uses proportions \\(0,1/m,\\dots,1\\); a simplex-centroid uses all subset centroids.",
        ]],
    ],
    contoh=dict(
        judul="Example: a two-component mixture",
        soal="β₁ = 10, β₂ = 14, β₁₂ = 8. Prediction for a 50:50 mixture.",
        data=None,
        langkah=[
            "Substitute x₁ = x₂ = 0.5.",
        ],
        simpul="The mean of the pure responses is 12; the blend gives 14, so there is a synergy of 2.",
    ),
    faq=[
        ["Why is there no intercept?",
         "Because \\(x_1+\\dots+x_q=1\\), so the intercept is collinear with the components."],
        ["What if there are lower bounds?",
         "Use pseudo-components to reconstruct the simplex."],
        ["When is it used?",
         "Feed formulations, dough, pesticides, and blended materials."],
    ],
)

MOD_EN["metode-taguchi"] = dict(
    title="The Taguchi Method",
    ringkas="Orthogonal arrays and the signal-to-noise ratio for robust design.",
    tujuan=[
        "Understand orthogonal arrays and the S/N ratio",
        "Read the delta ranking and the S/N ANOVA",
        "Carry out a confirmation experiment",
    ],
    ide=[
        "The Taguchi method uses orthogonal arrays (for example L9) to test many factors with few runs, then evaluates each combination with the S/N (signal-to-noise) ratio, which expresses robustness against noise.",
        "Three common S/N types: larger-the-better, smaller-the-better, and nominal-the-best. The level with the highest S/N is chosen for each factor.",
    ],
    rumus=[
        ["Larger-the-better", "S/N = −10 log₁₀[(1/n) Σ 1/yᵢ²]"],
        ["Smaller-the-better", "S/N = −10 log₁₀[(1/n) Σ yᵢ²]"],
    ],
    langkah=[
        "Choose the orthogonal array and S/N type according to the goal.",
        "Enter the data for each run.",
        "Read the S/N response table and the delta ranking.",
        "Run a confirmation experiment at the optimum combination.",
    ],
    baca=[
        "The largest delta shows the most influential factor.",
        "The S/N ANOVA tests significance; confirmation is a must.",
    ],
    jebakan=[
        "Using the wrong S/N type.",
        "Ignoring interactions in a saturated array.",
        "Not running a confirmation experiment.",
    ],
    latihan="Run the sample data, note the factor with the largest delta, and determine the optimum combination.",
    notasi=[
        "mean response",
        "response variance",
        "signal-to-noise ratio (dB)",
        "orthogonal array",
    ],
    teori=[
        ["The SN ratio", [
            "Taguchi uses orthogonal arrays to minimise the number of runs and the SN ratio to choose factor levels that make the response both good and stable. The SN ratio is computed from repeated observations, and larger is always better.",
        ]],
        ["Other types", [
            "For a specific target use nominal-the-best, and for smaller-the-better use the third form.",
        ]],
        ["Orthogonal arrays and factor effects", [
            "Arrays such as \\(L_8(2^7)\\) estimate 7 two-level factors in only 8 runs. The effect of each factor is the difference in mean SN at each level; the level with the highest SN is chosen.",
        ]],
    ],
    contoh=dict(
        judul="Example: SN for three observations",
        soal="Responses 20, 22, 21; the larger-the-better case.",
        data=None,
        langkah=[
            "Mean of the inverse squares.",
            "SN.",
        ],
        simpul="The configuration with the higher SN is both better and more consistent.",
    ),
    faq=[
        ["Why SN rather than just the mean?",
         "SN combines the level and variability of the response, so it picks settings that are robust to noise."],
        ["Does Taguchi ignore interactions?",
         "Yes, they are generally assumed small; they can be mapped onto special columns."],
        ["How does it relate to fractional factorials?",
         "Orthogonal arrays are essentially fractional factorials; the main difference lies in the SN analysis."],
    ],
)
