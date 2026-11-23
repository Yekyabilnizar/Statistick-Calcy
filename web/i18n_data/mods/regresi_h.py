from . import MOD_EN

MOD_EN["regresi-spasial-sar-lag"] = dict(
    title="Spatial Regression: SAR (Lag)",
    ringkas="Spatial dependence in the response variable.",
    tujuan=[
        "Understand the spatial weights matrix",
        "Read ρ and direct/indirect effects",
        "Use Moran's I",
    ],
    ide=[
        "In location data, the value of Y in one region is often influenced by Y in neighbouring regions. The SAR model adds a spatial lag term ρWy. Moran's I tests spatial autocorrelation in the residuals of an ordinary regression.",
        "Because neighbouring Y also has an influence, the effect of X splits into a direct effect (on the region itself) and an indirect effect (spillover to other regions).",
    ],
    rumus=[
        ["SAR model", "y = ρWy + Xβ + ε"],
        ["Moran's I", "I = (n/S₀)·(zᵀWz)/(zᵀz)"],
    ],
    langkah=[
        "Prepare the coordinates of each location.",
        "Choose the weights matrix (nearest neighbours or inverse distance).",
        "Run and read ρ.",
        "Read the direct and indirect effects.",
    ],
    baca=[
        "A significant ρ shows spatial dependence in Y.",
        "Total effect = direct + indirect.",
    ],
    jebakan=[
        "An arbitrarily chosen weights matrix.",
        "No Moran's I test.",
        "Ignoring spillover.",
    ],
    latihan="Run the sample data and compare the results with ordinary linear regression.",
    notasi=[
        "spatial weights matrix",
        "spatial lag coefficient",
        "Moran's I",
    ],
    teori=[
        ["The spatial lag model", [
            "SAR (spatial autoregressive) models the response at a location as influenced by the response at neighbouring locations. \\(\\mathbf{W}\\) is a row-normalised neighbourhood matrix so that \\(\\mathbf{W}\\mathbf{y}\\) is the neighbour average.",
        ]],
        ["Direct and indirect effects", [
            "Because of feedback, a change in one predictor affects the location itself (direct) and its neighbours (indirect). The total effect when \\(\\mathbf{W}\\) is row-normalised:",
        ]],
        ["Spatial autocorrelation test", [
            "Moran's I on the OLS residuals checks whether spatial dependence exists. Estimation uses maximum likelihood (OLS is biased).",
        ]],
    ],
    contoh=dict(
        judul="Example: total effect",
        soal="β = 1, ρ = 0.5, row-normalised W.",
        data=None,
        langkah=[
            "Total effect.",
        ],
        simpul="The total effect is 2 times the direct coefficient: half of it comes through neighbour feedback.",
    ),
    faq=[
        ["SAR or SEM?",
         "SAR if neighbour values influence directly (diffusion); SEM if only errors are correlated (unmeasured variables)."],
        ["How do I choose W?",
         "Contiguity (shared border) or distance, according to the logic of interaction."],
        ["Why not OLS?",
         "The spatial lag is endogenous, so OLS is biased."],
    ],
)

MOD_EN["regresi-spasial-sem-error"] = dict(
    title="Spatial Regression: SEM (Error)",
    ringkas="Spatial dependence in the errors.",
    tujuan=[
        "Distinguish SEM from SAR",
        "Read λ",
        "Check Moran's I of the residuals",
    ],
    ide=[
        "In SEM, spatial dependence is in the errors: unobserved factors that are correlated across regions. The model adds a parameter λ on the errors.",
        "Compared with SAR, SEM does not produce spillover effects of X; it only improves efficiency and standard errors.",
    ],
    rumus=[
        ["SEM model", "y = Xβ + u, u = λWu + ε"],
    ],
    langkah=[
        "Run OLS and test Moran's I of the residuals.",
        "If there is error autocorrelation, run SEM.",
        "Read λ.",
        "Check Moran's I of the SEM residuals.",
    ],
    baca=[
        "A significant λ shows spatial dependence in the errors.",
        "The LM tests help choose between SAR and SEM.",
    ],
    jebakan=[
        "Choosing SAR vs SEM wrongly.",
        "An arbitrary weights matrix.",
    ],
    latihan="Run the sample data with SAR and SEM and compare.",
    notasi=[
        "spatial error coefficient",
        "spatially autocorrelated error",
    ],
    teori=[
        ["The spatial error model", [
            "In SEM, spatial dependence exists only in the errors, representing unmeasured factors that vary spatially. The coefficients \\(\\boldsymbol{\\beta}\\) are still interpreted as in ordinary regression.",
        ]],
        ["Error covariance", [
            "The errors have a non-diagonal covariance, so OLS is unbiased but inefficient and its standard errors are wrong. Estimation uses MLE or GLS.",
        ]],
        ["Selection tests", [
            "Lagrange Multiplier tests (LM-lag and LM-error), along with their robust versions, help choose between SAR and SEM.",
        ]],
    ],
    contoh=dict(
        judul="Example: error transformation",
        soal="λ = 0.4; mean neighbour error u_W = 2.5; ε = 0.5.",
        data=None,
        langkah=[
            "Location error.",
        ],
        simpul="The location error of 1.5 partly comes from neighbours (1.0) and partly is random (0.5).",
    ),
    faq=[
        ["How is the coefficient β interpreted?",
         "The same as in ordinary regression; there are no spillover effects."],
        ["Why still use SEM?",
         "To improve standard errors and efficiency."],
        ["How do I compare SAR and SEM?",
         "AIC and the LM tests."],
    ],
)

MOD_EN["geographically-weighted-regression-gwr"] = dict(
    title="Geographically Weighted Regression (GWR)",
    ringkas="Coefficients that differ at each location.",
    tujuan=[
        "Understand spatial nonstationarity",
        "Read the coefficient map",
        "Compare with OLS through AICc",
    ],
    ide=[
        "GWR fits a separate regression at each location, with weights that decline with distance. The result is coefficients that change by location so relationships that differ between regions become visible.",
        "The bandwidth determines how local the model is. Coefficient maps and local R² help find regions where the effect of X is strong or weak.",
    ],
    rumus=[
        ["Model", "yᵢ = β₀(uᵢ, vᵢ) + Σ βⱼ(uᵢ, vᵢ) xᵢⱼ + εᵢ"],
    ],
    langkah=[
        "Prepare the coordinates.",
        "Choose the bandwidth (AICc).",
        "Compare the AICc with OLS.",
        "Read the coefficient maps.",
    ],
    baca=[
        "An AICc lower than OLS justifies GWR.",
        "Strongly varying coefficients indicate nonstationarity.",
    ],
    jebakan=[
        "Too few samples per location.",
        "Local collinearity.",
        "Interpreting maps without tests.",
    ],
    latihan="Run the sample data and name the regions where the effect of X is strongest.",
    notasi=[
        "coordinates of location i",
        "geographic weights matrix",
        "bandwidth",
    ],
    teori=[
        ["Coefficients that change by location", [
            "GWR fits a separate regression at every location with weights that decline with distance, so the coefficients become a map (spatial nonstationarity). The result at each location is a weighted least squares.",
        ]],
        ["Kernel function and bandwidth", [
            "Gaussian weights decline smoothly; a bisquare kernel cuts off at distance b. The bandwidth is chosen by AICc or cross-validation; an adaptive bandwidth uses only the nearest neighbours.",
        ]],
        ["Nonstationarity test", [
            "A test compares GWR with the global model; coefficient maps and local t values should be interpreted carefully because of multiple testing and local collinearity.",
        ]],
    ],
    contoh=dict(
        judul="Example: Gaussian weight",
        soal="A point at distance d = b from the focal location.",
        data=None,
        langkah=[
            "Weight.",
        ],
        simpul="At a distance equal to the bandwidth the weight is still 0.61; at d = 2b the weight falls to 0.135.",
    ),
    faq=[
        ["When is GWR used?",
         "When the X–Y relationship is suspected to differ between regions."],
        ["What about local collinearity?",
         "It can be severe; check the local VIF."],
        ["Fixed or adaptive bandwidth?",
         "Adaptive when the density of points is not uniform."],
    ],
)
