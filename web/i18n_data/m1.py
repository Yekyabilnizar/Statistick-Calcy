from . import METHODS_EN as M
# slug: (title, desc, tags, when, assume, read)
M["rancangan-acak-lengkap"] = ("Completely Randomized Design (CRD)", "One-way analysis of variance for experiments with homogeneous experimental units, with post-hoc tests and letter groupings.", ["One-way ANOVA", "Post-hoc test", "Assumption tests"],
 "Use CRD when the experimental units are fairly uniform (e.g. a laboratory or greenhouse experiment under controlled conditions) and there is only one treatment factor.",
 "Errors are normally distributed, variances are homogeneous across treatments, and observations are independent. Treatments must be randomly assigned to all experimental units.",
 "Look at the P-value in the ANOVA table: if it is below the significance level (α), treatments have a significant effect. Continue with a post-hoc test; treatments sharing a letter do not differ significantly. The coefficient of variation (KK) indicates the precision of the experiment.")
M["rancangan-acak-kelompok"] = ("Randomized Complete Block Design (RCBD)", "One-way analysis of variance with blocking to control variation in location, time, or replicate.", ["Two-way ANOVA", "Blocking", "Post-hoc test"],
 "Use RCBD when experimental units are not uniform but can be grouped into blocks that are fairly homogeneous inside (sloping land, different times, different operators).",
 "Errors are normal and homogeneous, there is no treatment × block interaction, and each treatment appears once in every block.",
 "Check the treatment effect in the ANOVA table. A significant block effect shows that blocking was effective. Follow up with a post-hoc test on treatments that have a significant effect.")
M["rancangan-bujur-sangkar-latin"] = ("Latin Square Design (LSD)", "Controls two sources of variation at once (rows and columns); each treatment appears once in every row and column.", ["Two-way blocking", "Latin ANOVA"],
 "Use a Latin square when there are two sources of variation that can be controlled simultaneously, e.g. field strips (rows) and a fertility gradient (columns).",
 "Number of rows = number of columns = number of treatments, no interaction between factors, and errors are normal and homogeneous.",
 "Treatments are tested against the error after the row and column effects are removed. If significant, continue with a post-hoc test.")
M["rancangan-graeco-latin"] = ("Graeco-Latin Square Design", "An extension of the Latin square with three blocking sources (rows, columns, and Greek letters) for treatments.", ["Three-way blocking"],
 "Use when three sources of variation need to be controlled in a single t × t experiment.",
 "All four factors are mutually orthogonal (each pair occurs once), with no interaction, and errors are normal and homogeneous.",
 "The treatment effect is tested after rows, columns, and the Greek factor are removed. Error degrees of freedom are small, so conclusions need care.")
M["blok-tidak-lengkap-bib-lattice"] = ("Incomplete Blocks (BIB / Lattice)", "Balanced Incomplete Block and Lattice designs: block-adjusted treatment means and pairwise tests.", ["BIB", "Lattice", "Block-adjusted"],
 "Use when blocks are too small to hold all treatments, so each block contains only some of them.",
 "A balanced design (every pair of treatments meets in the same number of blocks in a BIB), and errors are normal and homogeneous.",
 "Compare block-adjusted means, not raw means. Pairwise tests use the correction you choose.")
M["percobaan-faktorial"] = ("Factorial Experiment", "Two to four factors at once with all their interactions; can include blocks (factorial RCBD).", ["2–4 factors", "Interaction", "Post-hoc test"],
 "Use when you want to test several factors at once and see whether the effect of one factor depends on the level of another (interaction).",
 "Balanced data (every treatment combination has the same number of replicates), and errors are normal and homogeneous.",
 "Check the interaction first. If the interaction is significant, interpret the combination means, not just the main effects.")
M["faktorial-pecahan-fractional-factorial"] = ("Fractional Factorial", "2^(k−p) factorial with alias structure, resolution, main/interaction effects, and Lenth's method.", ["2^(k−p)", "Alias", "Lenth"],
 "Use when there are many factors but few experimental units, so only a fraction (2^(k−p)) of the combinations is run to estimate main effects and low-order interactions.",
 "Higher-order interactions are negligible (sparsity of effects). Factors are coded −1/+1. Aliased effects cannot be separated and are reported together with their aliases.",
 "Look at the effects table: effects marked * or ** are significant. In the Pareto chart and normal probability plot, effects that depart from the straight line are the significant ones. If there are no error degrees of freedom, the test uses Lenth's method, which is exploratory.")
M["petak-terbagi-split-plot"] = ("Split-Plot Design", "One factor on main plots and another on subplots, with a separate error for each.", ["Two errors", "Main plot", "Subplot"],
 "Use when one factor is hard or costly to change (e.g. tillage or irrigation) and is applied to large plots, while the other factor is applied to small plots within them.",
 "Main-plot error and subplot error differ; each is normal and homogeneous. Data are complete and balanced.",
 "The main plot is tested against error (a), while the subplot and the interaction are tested against error (b). Subplot comparisons are usually more precise.")
M["petak-terbagi-dua-kali-split-split-plot"] = ("Split-Split-Plot Design", "Three nested factors: main plot, subplot, and sub-subplot, with three errors.", ["Three errors", "Three factors"],
 "Use when three factors differ in how hard they are to apply, so they are arranged hierarchically.",
 "Three distinct errors, complete and balanced data, and errors normal and homogeneous at every level.",
 "Each level of factor is tested against the error of its own level. Lower-level factors are usually tested more sensitively.")
M["petak-jalur-strip-plot"] = ("Strip-Plot Design", "Two factors applied in horizontal and vertical strips that cross each other.", ["Crossed strips", "Three errors"],
 "Use when both factors are hard to apply on small plots, e.g. tillage in one direction and irrigation type in the perpendicular direction.",
 "Data are complete and balanced, errors are normal and homogeneous. Factor A, factor B, and the interaction are tested with different errors.",
 "Factor A is tested against error (a), B against error (b), and the A × B interaction against error (c).")
M["rancangan-tersarang-nested"] = ("Nested Design", "Factor B nested within factor A (e.g. trees within locations), with variance components.", ["B(A)", "Variance components"],
 "Use when the levels of factor B only make sense within one level of factor A, e.g. different trees at each location.",
 "Errors are normal and homogeneous; if B is random, the B effects are normally distributed.",
 "Check the B(A) effect first. Variance components show how much of the variation comes from each level.")
M["pengukuran-berulang-repeated-measures"] = ("Repeated Measures", "The same subjects measured repeatedly; includes Mauchly's sphericity test and Greenhouse-Geisser and Huynh-Feldt corrections.", ["Within-subject", "Sphericity", "GG · HF"],
 "Use when the same subjects are measured at several times or conditions, so observations on the same subject are correlated.",
 "Sphericity (equal variances of differences between all pairs of times), normality, and complete data for every subject.",
 "If sphericity is violated (significant Mauchly test), use the Greenhouse-Geisser or Huynh-Feldt corrected P-value.")
M["rancangan-cross-over"] = ("Cross-Over Design", "Each subject receives all treatments in turn in a set sequence, with period and carry-over effects.", ["Sequence", "Period", "Carry-over"],
 "Use when each subject serves as its own control by receiving several treatments in different periods.",
 "No meaningful carry-over effect (a sufficient washout period is needed), and errors are normal and homogeneous.",
 "Check the treatment, period, and sequence effects. A significant sequence effect may indicate carry-over.")
M["ancova-analisis-kovarians"] = ("ANCOVA (Analysis of Covariance)", "Compares groups after accounting for a numeric covariate, with a test of homogeneity of slopes.", ["Covariate", "Adjusted means", "Slope test"],
 "Use when a numeric variable influences the response and cannot be controlled, e.g. the initial body weight of livestock.",
 "Regression slopes are equal across groups (no group × covariate interaction), the relationship is linear, and errors are normal and homogeneous.",
 "Check the homogeneity-of-slopes test first. If it holds, compare the adjusted means between groups.")
M["manova"] = ("MANOVA", "Several responses at once: Pillai, Wilks, Hotelling-Lawley, Roy, Box's M test, and univariate ANOVAs.", ["Pillai · Wilks", "Box's M"],
 "Use when several correlated response variables are measured together on each experimental unit, e.g. plant height, weight, and protein content.",
 "Responses are multivariate normal, covariance matrices are homogeneous across groups (Box's M test), and observations are independent.",
 "Start with the multivariate tests (Pillai, Wilks, Hotelling-Lawley, Roy). If significant, look at the univariate ANOVAs per response with Bonferroni-corrected P-values to see which responses differ. Pillai is the most robust when Box's M is significant.")
M["response-surface-methodology-rsm"] = ("Response Surface Methodology (RSM)", "Quadratic model (CCD or Box-Behnken), stationary point, response-surface contours, and optimum.", ["CCD · Box-Behnken", "Contour", "Optimisation"],
 "Use to find the optimum process conditions (temperature, time, concentration) from sequential experiments such as Central Composite or Box-Behnken.",
 "A second-order polynomial adequately represents the response surface near the optimum, errors are normal and homogeneous, and factors can be set precisely.",
 "Check the model P, predicted R², and lack of fit (non-significant means the model is adequate). The stationary point is a maximum, minimum, or saddle; if it lies outside the experimental region, use a constrained optimum. The contour plot shows the response surface.")
M["rancangan-campuran-mixture"] = ("Mixture Design", "Components with a fixed total proportion: Scheffé model, ternary diagram, and optimum composition.", ["Scheffé", "Ternary diagram"],
 "Use when the response depends on the proportions of mixture components that sum to a fixed total (100%), such as dough, feed, or fertiliser formulations.",
 "Component proportions sum to 1 (or 100%) in every run, the no-intercept Scheffé model is appropriate, and errors are normal and homogeneous.",
 "Linear coefficients show the response of pure components; a positive interaction coefficient means synergy, a negative one means antagonism. The ternary diagram and optimum table show the best composition.")
M["metode-taguchi"] = ("Taguchi Method", "Orthogonal arrays with signal-to-noise ratio, factor ranking, S/N ANOVA, and the optimal combination.", ["S/N ratio", "Orthogonal array"],
 "Use to design processes that are robust to noise with few experiments, through orthogonal arrays (L4, L8, L9, and so on).",
 "Control factors are arranged by an orthogonal array, replicates represent noise variation, and interactions between factors are assumed small.",
 "Choose the factor levels with the highest S/N ratio. The delta ranking shows the most influential factor; S/N ANOVA tests its significance. Run a confirmation experiment at the optimal combination.")
