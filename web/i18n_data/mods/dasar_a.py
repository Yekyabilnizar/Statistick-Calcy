from . import MOD_EN

MOD_EN["dasar-jenis-data"] = dict(
    title="Data Types and Variables",
    ringkas="Learn about measurement scales and variable roles, because they determine the method of analysis.",
    tujuan=[
        "Distinguish nominal, ordinal, interval, and ratio data",
        "Distinguish response, treatment/factor, and covariate variables",
        "Choose a method family from the type of data",
    ],
    ide=[
        "Every column in a data table has a measurement scale. The scale determines which operations make sense: a mean is only meaningful for numeric data, while categorical data can only be counted.",
        "Besides the scale, decide the role of each column. The response variable (Y) is what is measured as the outcome. A factor or treatment is what the researcher controls, usually a category such as variety or dose. A covariate is an accompanying numeric variable that influences Y but is not the main focus.",
        "Rule of thumb: a continuous numeric response with categorical predictors points to ANOVA and experimental design; a numeric response with numeric predictors points to regression; a binary or count response points to logistic or Poisson regression.",
    ],
    rumus=[
        ["Nominal", "categories without order (sex, variety)"],
        ["Ordinal", "ordered categories (low < medium < high)"],
        ["Interval", "numeric, differences are meaningful, arbitrary zero (temperature in °C)"],
        ["Ratio", "numeric with an absolute zero (weight, height, yield)"],
    ],
    langkah=[
        "Write the research question in one sentence.",
        "Mark which column is the response, which is the factor, and which is the covariate.",
        "Determine the scale of each column.",
        "Match it with a method family in the Method Guide.",
    ],
    baca=[
        "In the calculator, numeric columns appear in the response choices and text columns appear in the factor choices.",
        "Columns of numeric codes such as 1, 2, 3 for categories are read as numeric; change them to text (A, B, C) so they are recognised as a factor.",
    ],
    jebakan=[
        "Treating category codes (1, 2, 3) as real numbers.",
        "Using the mean for ordinal data without consideration.",
        "Mixing up column roles: using a factor as the response.",
    ],
    latihan="Open one of the methods in the calculator, load the sample data, then point out for yourself which column is the response, which is the factor, and which is the covariate before looking at the automatically filled column choices.",
    notasi=[
        "response variable (the measured outcome)",
        "predictor variable or j-th factor",
        "error (the part of Y not explained by the model)",
        "number of observations",
    ],
    teori=[
        ["Four measurement scales", [
            "The measurement scale determines which mathematical operations are meaningful. On a nominal scale, numbers or letters are just labels (variety A, B, C); only frequencies and the mode can be computed. On an ordinal scale there is an order (poor, fair, good) but the distances between categories are not equal, so the median and percentiles are meaningful, while the arithmetic mean is debated.",
            "An interval scale has equal distances but an arbitrary zero, like temperature in °C: 20 °C does not mean \"twice as hot\" as 10 °C. A ratio scale has an absolute zero (weight, height, yield), so ratio comparisons are meaningful and all statistics can be used.",
        ]],
        ["Discrete and continuous variables, and their distributions", [
            "A discrete variable takes only certain values (leaf counts, number of children, recovered or not). A continuous variable can take any value in a range (height, weight, concentration). This difference determines the suitable probability distribution: normal for symmetric continuous data, binomial for binary data, Poisson for counts, gamma for positive right-skewed continuous data.",
            "That is why the calculator has different regression families: choosing a method is essentially choosing the distribution of the response.",
        ]],
        ["The role of variables in a model", [
            "Almost every method in GetComput can be read as one general form: the response equals the part explained by the predictors plus random error. When the predictors are categories (factors), the model is ANOVA and experimental design. When the predictors are numeric, the model is regression. When both are mixed, the model is ANCOVA or regression with dummy variables.",
            "A covariate is a numeric predictor that is not the focus of the research but needs to be adjusted for, for example the initial weight of livestock before being given feed.",
        ]],
        ["Choosing a method family", [
            "Three questions set the direction: (1) what is the scale of the response, (2) what is the scale of the predictors, (3) are the observations independent. A continuous response with categorical predictors points to ANOVA; a continuous response with numeric predictors points to linear regression; a binary or count response points to logistic or Poisson regression; repeated observations on the same subject point to repeated measures or mixed models.",
        ]],
    ],
    contoh=dict(
        judul="Example: setting out the roles and scales of data columns",
        soal="An experiment tests two rice varieties at three fertilizer doses. The recorded columns and their roles are shown below. Determine the scale, role, and suitable method family.",
        data=[
            ["Column", "Example values", "Scale", "Role"],
            ["Variety", "V1, V2", "Nominal", "Factor"],
            ["Dose", "0, 50, 100 kg/ha", "Ratio (treated as categorical)", "Factor"],
            ["Block", "K1 .. K4", "Nominal", "Grouping (block)"],
            ["Plant height", "87.2 cm", "Continuous ratio", "Response"],
            ["Number of tillers", "14", "Discrete ratio", "Other response (count)"],
            ["Preference score", "1 to 5", "Ordinal", "Other response (ordinal)"],
        ],
        langkah=[
            "Two categorical factors and one continuous response mean factorial analysis of variance.",
            "The blocks show that the basic design is an RCBD, so the model is a factorial in RCBD.",
            "If the analysed variable is the number of tillers (a count), move to Poisson or negative binomial regression.",
            "If the analysed variable is the preference score from 1 to 5, consider ordinal logistic regression.",
        ],
        simpul="Data type and column roles determine the method. Settling both before running the calculator avoids an analysis that heads in the wrong direction.",
    ),
    faq=[
        ["Can the codes 1, 2, 3 for categories be analysed as numbers?",
         "No, unless the categories are truly ordered and the spacing makes sense. The codes 1, 2, 3 for variety are just labels. Change them to text (V1, V2, V3) so the calculator treats them as a factor."],
        ["Is a dose of 0, 50, 100 kg a factor or a covariate?",
         "It depends on the goal. If you only want to compare three levels, make it a factor. If you want to estimate the response pattern to dose (for example quadratic), treat it as a numeric variable in regression."],
        ["Why does the data type determine the method?",
         "Because each distribution has a different relationship between mean and variance. Using the wrong method makes standard errors and P-values untrustworthy."],
    ],
)

MOD_EN["dasar-statistik-deskriptif"] = dict(
    title="Descriptive Statistics",
    ringkas="Summarise data with measures of centre and spread before further analysis.",
    tujuan=[
        "Compute the mean, standard deviation, standard error, and coefficient of variation",
        "Distinguish the standard deviation (SD) from the standard error (SE)",
        "Read the descriptive table in the calculator results",
    ],
    ide=[
        "Measures of centre answer 'where is the centre of the data': mean, median, mode. Measures of spread answer 'how spread out': variance, standard deviation, range.",
        "The SD describes the spread of individual data. The SE describes the precision of the sample mean as an estimate of the population mean, so it gets smaller as replicates increase. The coefficient of variation (CV) expresses the SD relative to the mean in percent, useful for comparing variability between variables with different units.",
    ],
    rumus=[
        ["Mean", "x̄ = Σx / n"],
        ["Variance", "s² = Σ(x − x̄)² / (n − 1)"],
        ["Standard deviation", "s = √s²"],
        ["Standard error", "SE = s / √n"],
        ["CV", "CV = (s / x̄) × 100%"],
    ],
    langkah=[
        "Sort and look at the data; check for extreme values.",
        "Compute the mean and SD per group.",
        "Compute the SE if you want to show error bars on a chart.",
        "Report n, the mean, and the SD (or SE) together.",
    ],
    baca=[
        "Sample data 4, 6, 8, 10, 12: mean 8; variance (16+4+0+4+16)/4 = 10; SD = 3.162; SE = 3.162/√5 = 1.414; CV = 39.5%.",
        "In the calculator results, the columns N, Mean, SD, SE, Min, Max are the descriptive statistics per treatment.",
    ],
    jebakan=[
        "Mixing up SD and SE without stating which one is used in the chart.",
        "Using the CV on data whose mean is close to zero.",
        "Ignoring outliers that shift the mean.",
    ],
    latihan="Run the CRD with the sample data. Look at the descriptive table, then switch the chart error bars between SD and SE and notice how their length changes.",
    notasi=[
        "sample mean",
        "sample variance and standard deviation",
        "standard error of the mean",
        "coefficient of variation",
        "sample size",
    ],
    teori=[
        ["Measures of centre", [
            "The arithmetic mean is the balance point of the data: the sum of deviations from the mean is always zero. The mean is sensitive to outliers. The median is the middle value after sorting; it is resistant to outliers, so it suits strongly skewed data better. The mode is the most frequent value.",
            "When observations have different weights (for example the mean across groups of different sizes), use a weighted mean.",
        ]],
        ["Measures of spread", [
            "The sample variance is the mean of squared deviations, with divisor \\(n-1\\) (Bessel's correction) so that it is an unbiased estimate of the population variance. The divisor \\(n-1\\) arises because one degree of freedom is used to estimate \\(\\bar{x}\\). The standard deviation is the square root of the variance, so its unit is the same as the data.",
            "The range (maximum minus minimum) and the interquartile range \\(IQR=Q_3-Q_1\\) are simple measures of spread; the IQR is resistant to outliers.",
        ]],
        ["Standard error and coefficient of variation", [
            "The standard deviation describes the spread of individual data, whereas the standard error (SE) describes the precision of the sample mean as an estimate of the population mean. The SE shrinks with the square root of the sample size: to double the precision, the number of replicates must be four times as large.",
            "The coefficient of variation expresses the standard deviation relative to the mean in percent, useful for comparing the variability of two variables with different units. In field experiments the CV is often reported as a measure of experimental precision.",
        ]],
        ["Shape of the distribution: skewness and kurtosis", [
            "Skewness is zero for symmetric data, positive if the right tail is longer, and negative if the left tail is longer. Kurtosis expresses how heavy the tails are compared with the normal distribution. Both help assess whether the normality assumption is reasonable before a formal test.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: eight observations",
        soal="Eight plots gave harvest weights (kg): 12, 15, 14, 10, 18, 16, 13, 17. Compute the measures of centre and spread.",
        data=[
            ["Plot", "1", "2", "3", "4", "5", "6", "7", "8"],
            ["Weight (kg)", "12", "15", "14", "10", "18", "16", "13", "17"],
        ],
        langkah=[
            "Mean: the sum of all values, 115, divided by 8.",
            "Median: sort to 10, 12, 13, 14, 15, 16, 17, 18; the middle value is the mean of the 4th and 5th values.",
            "Sum of squared deviations.",
            "Variance and standard deviation with divisor n − 1 = 7.",
            "Standard error and coefficient of variation.",
        ],
        simpul="The mean is 14.375 kg with a standard deviation of 2.669 kg. The mean and median are nearly equal (14.375 and 14.5), indicating a fairly symmetric distribution. A CV of 18.6% indicates moderate variability.",
    ),
    faq=[
        ["Why is the divisor n − 1 and not n?",
         "Because \\(\\bar{x}\\) is computed from the same data, deviations from \\(\\bar{x}\\) tend to be smaller than deviations from the true population mean. The divisor \\(n-1\\) corrects this bias so that \\(E(s^2)=\\sigma^2\\)."],
        ["When should I use the SD and when the SE on a chart?",
         "Use the SD to describe the spread of the data; the SE to describe the precision of the mean. State your choice in the chart caption, because SE bars are always shorter."],
        ["What CV counts as good?",
         "There is no single threshold; it depends on the commodity and type of experiment. In field experiments a CV below about 20% is often considered good, but compare with similar experiments."],
    ],
)

MOD_EN["dasar-distribusi-normal"] = dict(
    title="The Normal Distribution",
    ringkas="The bell shape that underlies most parametric tests.",
    tujuan=[
        "Understand the features of the normal distribution and z-values",
        "Know why normality matters",
        "Read the Q-Q plot and the normality test",
    ],
    ide=[
        "The normal distribution is a symmetric bell shape with two parameters: the mean μ and the standard deviation σ. About 68% of the data lie within μ ± 1σ, 95% within μ ± 2σ, and 99.7% within μ ± 3σ.",
        "The standardised value z states how far a value is from the mean in units of standard deviation. With z we can compute probabilities from the standard normal table.",
        "The central limit theorem states that sample means tend to be normal even if the original data are not, provided the sample is large enough. That is why the t-test and ANOVA are fairly robust to mild departures from normality, but not to severe outliers or very small samples.",
    ],
    rumus=[
        ["Standardised value", "z = (x − μ) / σ"],
        ["Example", "x = 85, μ = 70, σ = 10 → z = 1.5; probability below ≈ 0.933"],
    ],
    langkah=[
        "Draw a histogram or a Q-Q plot of the residuals.",
        "Run a normality test (Shapiro-Wilk for small to medium samples).",
        "If the departure is severe, consider a transformation or a nonparametric/robust method.",
    ],
    baca=[
        "Q-Q plot: points following the diagonal line mean normal; an S-curve or deviating tails mean not normal.",
        "Shapiro-Wilk test: P > α means no evidence of departure from normality.",
        "Normality is checked on the model residuals, not on the raw data of all groups pooled together.",
    ],
    jebakan=[
        "Testing normality of the raw data when the model has several groups.",
        "Relying only on a formal test with a very large sample (almost always 'significant') or a very small one (low power).",
        "Assuming 'not significant' means 'definitely normal'.",
    ],
    latihan="Run Regression Diagnostics in the calculator, open the residual plot and assumption test tab, then match the shape of the Q-Q plot with the Shapiro-Wilk result.",
    notasi=[
        "population mean",
        "population standard deviation",
        "standardised value",
        "standard normal cumulative distribution function",
        "Shapiro-Wilk statistic",
    ],
    teori=[
        ["Density function and the standardised value", [
            "The normal distribution is fully determined by two parameters, the mean \\(\\mu\\) and the standard deviation \\(\\sigma\\). Its curve is a symmetric bell. By standardising \\(z=(x-\\mu)/\\sigma\\), every normal distribution can be read from one table, the standard normal distribution \\(N(0,1)\\).",
        ]],
        ["The empirical rule", [
            "About 68% of the data lie within one standard deviation of the mean, 95% within 1.96 standard deviations, and 99.7% within three standard deviations. The value 1.96 is what appears in the 95% confidence interval.",
        ]],
        ["The central limit theorem", [
            "The mean of a random sample from any population with finite variance tends to be normally distributed when \\(n\\) is large enough. This is why the t-test and ANOVA are fairly robust to mild departures from normality in samples that are not too small. For very small samples or severe outliers, however, this approximation does not help.",
        ]],
        ["Checking normality", [
            "A Q-Q plot compares the quantiles of the data with theoretical normal quantiles; points following the diagonal line indicate normality. The Shapiro-Wilk test summarises this in one statistic \\(W\\) that is close to 1 when the data are normal; \\(P>\\alpha\\) means no evidence of departure. In models with several groups, normality is checked on the residuals, not on the pooled raw data.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: probabilities under the normal distribution",
        soal="The exam scores of a class are approximately normally distributed with a mean of 70 and a standard deviation of 10. What is the probability that a score exceeds 85, and between which two values do 95% of scores lie?",
        data=None,
        langkah=[
            "Standardise the value 85.",
            "The probability of a score below 85 is read from the standard normal distribution function; the probability above it is the complement.",
            "The central 95% limits use z = 1.96.",
        ],
        simpul="About 6.7% of students score above 85, and 95% of scores lie between 50.4 and 89.6.",
    ),
    faq=[
        ["My data are not normal; may ANOVA not be used?",
         "Not automatically. If the sample is large enough and the data balanced, ANOVA is fairly robust. Check the residual plots. If the violation is severe, try a transformation (log, square root) or a robust/nonparametric method."],
        ["Why is the normality test almost always significant in large samples?",
         "Because with a large n, any tiny departure becomes detectable, even if it has no practical effect. So look at the Q-Q plot too, not just the P-value."],
        ["What is the difference between \\(z\\) and \\(t\\)?",
         "Both are standardised values. \\(t\\) is used when the population standard deviation is unknown and estimated from the sample; its distribution has heavier tails and approaches the normal when \\(n\\) is large."],
    ],
)

MOD_EN["dasar-uji-hipotesis"] = dict(
    title="Hypothesis Testing and the P-value",
    ringkas="The logic of statistical decision-making: hypotheses, the test statistic, the P-value, and the significance level.",
    tujuan=[
        "Formulate H₀ and H₁",
        "Interpret the P-value and the significance level α",
        "Understand type I error, type II error, and power",
    ],
    ide=[
        "A hypothesis test compares two statements. H₀ (the null hypothesis) states there is no effect or difference; H₁ states there is. We compute a test statistic from the data, then ask: if H₀ were true, how rare is a result this extreme?",
        "That answer is the P-value. If P ≤ α (commonly 0.05), H₀ is rejected and the result is called significant. The P-value is not the probability that H₀ is true, and not a measure of effect size.",
        "A type I error is rejecting a true H₀ (probability α). A type II error is failing to reject a false H₀ (probability β). Power = 1 − β, which rises with more replicates, a larger effect, or a smaller error.",
    ],
    rumus=[
        ["One-sample t-test", "t = (x̄ − μ₀) / (s / √n), df = n − 1"],
        ["Example", "n = 25, x̄ = 52, μ₀ = 50, s = 5 → t = 2.0; df = 24; P (two-sided) ≈ 0.057 → not significant at α = 0.05"],
        ["Markers in tables", "** P < 0.01 · * P < 0.05 · ns P ≥ 0.05"],
    ],
    langkah=[
        "Formulate H₀ and H₁.",
        "Set α before looking at the data.",
        "Compute the test statistic and the P-value.",
        "Decide, then report the effect size and confidence interval, not just 'significant'.",
    ],
    baca=[
        "In the calculator's ANOVA table, the P-value column and the ** / * / ns markers are the result of this decision.",
        "P = 0.057 and P = 0.049 are not meaningfully different in practice; do not treat 0.05 as a wall.",
    ],
    jebakan=[
        "Interpreting P = 0.03 as 'a 3% probability that H₀ is true'.",
        "Changing α after seeing the results.",
        "Concluding 'no effect' from a non-significant result in a small sample.",
    ],
    latihan="Run the CRD with the sample data, change the significance level α from 0.01 to 0.05 to 0.10, and observe how the significance markers in the ANOVA table change.",
    notasi=[
        "null and alternative hypotheses",
        "significance level (probability of type I error)",
        "probability of type II error",
        "power",
        "t test statistic",
        "Cohen's effect size",
    ],
    teori=[
        ["The hypothesis testing framework", [
            "A hypothesis test compares two statements. \\(H_0\\) states there is no effect or difference; \\(H_1\\) states there is. We compute a test statistic from the data, then ask: if \\(H_0\\) were true, how rare is a result this close or this extreme? The answer is the P-value.",
            "The P-value is not the probability that \\(H_0\\) is true, and not a measure of effect size. The P-value only measures how incompatible the data are with \\(H_0\\).",
        ]],
        ["The one-sample t-test", [
            "To test whether a population mean equals a reference value \\(\\mu_0\\), the statistic \\(t\\) measures the distance of the sample mean from \\(\\mu_0\\) in units of standard error. Under \\(H_0\\), \\(t\\) follows a t distribution with \\(n-1\\) degrees of freedom. Decision: reject \\(H_0\\) if \\(|t|\\) exceeds the critical value, or equivalently if \\(P\\le\\alpha\\).",
        ]],
        ["Type I error, type II error, and power", [
            "A type I error is rejecting a true \\(H_0\\); its probability is \\(\\alpha\\). A type II error is failing to reject a false \\(H_0\\); its probability is \\(\\beta\\). Power \\(1-\\beta\\) is the probability of detecting an effect that truly exists. Power rises with more replicates, a larger effect, a smaller error, or a looser \\(\\alpha\\).",
            "To compare two means with the difference to detect \\(\\delta\\) and standard deviation \\(\\sigma\\), the sample size per group is approximately:",
        ]],
        ["Effect size, not just significant or not", [
            "A significant result is not always practically important, and a non-significant result does not always mean there is no effect. Report an effect size, for example Cohen's \\(d\\), together with a confidence interval. Rough guide: \\(d\\approx0.2\\) small, \\(0.5\\) medium, \\(0.8\\) large.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: a one-sample t-test",
        soal="The mean weight of a product should be 50 g. A sample of 16 items gives a mean of 52.8 g with a standard deviation of 4 g. Does the mean deviate from 50 g at α = 0.05?",
        data=None,
        langkah=[
            "Formulate the hypotheses.",
            "Compute the test statistic with df = 15.",
            "Compare with the critical value t(0.975; 15) = 2.131. Since 2.8 > 2.131, H₀ is rejected; the two-sided P-value = 0.0135.",
            "Compute the effect size.",
        ],
        simpul="The mean weight differs significantly from 50 g (t = 2.80; P = 0.0135) with a medium-to-large effect size (d = 0.70).",
    ),
    faq=[
        ["Does P = 0.051 mean there is no effect?",
         "No. P = 0.051 and P = 0.049 hardly differ as evidence. Report the number, the effect size, and the confidence interval, not just \"significant\" or \"not significant\"."],
        ["May I raise α after seeing the results?",
         "No. α must be set before looking at the data; changing it afterwards inflates the type I error."],
        ["What is the difference between a one-sided and a two-sided test?",
         "A two-sided test checks for a difference in both directions (\\(\\neq\\)); a one-sided test only in one direction (\\(>\\) or \\(<\\)) and must be decided before seeing the data. The calculator uses a two-sided test unless stated otherwise."],
    ],
)

MOD_EN["dasar-selang-kepercayaan"] = dict(
    title="Confidence Intervals",
    ringkas="A range of plausible values for a population parameter, more informative than the P-value alone.",
    tujuan=[
        "Compute a confidence interval for the mean",
        "Interpret the confidence level correctly",
        "Distinguish a confidence interval from a prediction interval",
    ],
    ide=[
        "A 95% confidence interval (CI) is a range built by a procedure that, when repeated many times, contains the true parameter in 95% of repetitions. A narrow interval means a precise estimator.",
        "A confidence interval speaks about the mean. A prediction interval (PI) speaks about one new observation, so it is always wider because it includes individual variability.",
    ],
    rumus=[
        ["CI for the mean", "x̄ ± t(α/2; n−1) · s/√n"],
        ["Example", "x̄ = 52, s = 5, n = 25: 52 ± 2.064 × 1 = [49.94 ; 54.06]"],
        ["Width", "shrinks as n rises or s falls"],
    ],
    langkah=[
        "Compute the mean and the standard error.",
        "Take the t value from the table with df = n − 1.",
        "Form the lower and upper limits.",
        "Check whether the reference value (for example 50) lies inside the interval.",
    ],
    baca=[
        "If the interval contains the null hypothesis value, the two-sided test at the corresponding α is not significant, and vice versa.",
        "In the regression Prediction Calculator, the CI for the mean of Y and the PI for a new observation are shown side by side.",
    ],
    jebakan=[
        "Saying 'the probability that the parameter lies in this interval is 95%'.",
        "Using the CI to predict a single observation.",
        "Comparing two means only by looking at whether the intervals overlap.",
    ],
    latihan="Run Linear Regression, open the Prediction tab, enter an X value in the middle of the data range and then outside the range, and compare the width of the CI and PI in both cases.",
    notasi=[
        "sample mean",
        "critical value of the t distribution",
        "standard error",
        "margin of error",
        "prediction interval",
    ],
    teori=[
        ["Confidence interval for a mean", [
            "A \\((1-\\alpha)\\times100\\%\\) confidence interval (CI) is built from the sample mean plus and minus the margin of error, i.e. the critical t value times the standard error. The correct interpretation: if the experiment were repeated many times and the CI computed the same way, \\((1-\\alpha)\\times100\\%\\) of those intervals would contain the true population mean. One particular interval does not have a \"95% probability\" of containing the parameter; it either contains it or it does not.",
        ]],
        ["Confidence interval for the difference of two means", [
            "For two groups with pooled variance \\(s_p^2\\), the interval for the difference of means uses the standard error of the difference. If the interval does not contain zero, the difference between the two means is significant at the corresponding \\(\\alpha\\). The interval gives more information than the P-value because it shows the size and precision of the difference.",
        ]],
        ["Prediction interval", [
            "A confidence interval speaks about the mean, whereas a prediction interval speaks about one new observation. The prediction interval is wider because it includes individual variability \\(s^2\\) in addition to the uncertainty of the mean.",
        ]],
        ["Determining sample size from the margin of error", [
            "If the desired margin of error is \\(E\\) and the standard deviation is estimated as \\(\\sigma\\), the number of observations needed is approximately as follows (normal approximation; round up).",
        ]],
    ],
    contoh=dict(
        judul="Worked example: CI and PI from the same sample",
        soal="From a sample of n = 16 we obtain a mean of 52.8 and a standard deviation of 4. Compute the 95% CI for the mean, the 95% PI for one new observation, and the sample size needed for a margin of error of 1 unit.",
        data=None,
        langkah=[
            "Critical value t(0.975; 15) = 2.131 and standard error s/√n = 4/4 = 1.",
            "95% CI for the mean.",
            "95% PI for one new observation.",
            "Sample size for a margin of error E = 1 with σ ≈ 4.",
        ],
        simpul="The CI is narrow (50.67 to 54.93) because it concerns the mean, whereas the PI is much wider (44.01 to 61.59) because it concerns a single observation. To narrow the CI to ±1, about 62 observations are needed.",
    ),
    faq=[
        ["Do overlapping intervals mean the difference is not significant?",
         "Not always. Two CIs can overlap slightly even though the difference between them is significant. Use the CI for the difference rather than comparing two CIs visually."],
        ["Why is the PI wider than the CI?",
         "The CI only contains the uncertainty in estimating the mean, which shrinks with n. The PI also contains individual variability, which does not vanish even when n is large."],
        ["What is the relationship between a CI and a hypothesis test?",
         "A \\((1-\\alpha)\\) CI that contains the value \\(\\mu_0\\) is equivalent to a non-significant two-sided test at level \\(\\alpha\\) for \\(H_0:\\mu=\\mu_0\\)."],
    ],
)

MOD_EN["dasar-asumsi-residual"] = dict(
    title="Model Assumptions and Residuals",
    ringkas="The conditions that make test results trustworthy, and how to check them through residuals.",
    tujuan=[
        "Know the four assumptions: normality, homogeneity of variance, independence, linearity",
        "Read residual plots",
        "Choose an action when an assumption is violated",
    ],
    ide=[
        "A statistical model writes an observation as the part explained by the model plus error. The residual e = y − ŷ is the estimate of the error. The assumptions made about the error: normally distributed, equal variance across all groups or predicted values, independent, and (in regression) a linear relationship.",
        "Mild violations are often harmless, especially with balanced data. Severe violations alter P-values and confidence intervals so that conclusions are misleading.",
    ],
    rumus=[
        ["Residual", "eᵢ = yᵢ − ŷᵢ"],
        ["Normality", "Shapiro-Wilk, Q-Q plot"],
        ["Homogeneity of variance", "Levene, Bartlett, Breusch-Pagan"],
        ["Independence", "Durbin-Watson, proper randomisation"],
    ],
    langkah=[
        "Run the analysis and save the residuals.",
        "Look at the residuals vs fitted plot: points should be scattered randomly without a funnel or curved pattern.",
        "Look at the Q-Q plot and the formal tests.",
        "If violated: transformation (log, square root), robust methods, nonparametric methods, or another model (GLM).",
    ],
    baca=[
        "A funnel pattern in residuals vs fitted indicates non-homogeneous variance.",
        "A curved pattern indicates a nonlinear relationship: add a quadratic term or use a nonlinear method.",
        "A repeating sequential pattern indicates autocorrelation: consider a time series model.",
    ],
    jebakan=[
        "Relying only on formal tests without looking at the plots.",
        "Deleting data to 'pass the assumptions'.",
        "Ignoring independence, even though faulty randomisation cannot be repaired statistically.",
    ],
    latihan="Run Regression Diagnostics with the sample data and read the Assumption Tests tab and the residual plots. Decide which assumptions are met and which are doubtful.",
    notasi=[
        "residual of observation i",
        "model predicted value",
        "error variance",
        "Durbin-Watson statistic",
        "variance inflation factor of the j-th variable",
    ],
    teori=[
        ["Residuals and the four assumptions", [
            "A residual is the difference between the actual value and the model's predicted value, and is an estimate of the error. In the general linear model the errors are assumed to be (1) normally distributed, (2) of equal variance for all observations, (3) independent, and (4) the mean-predictor relationship has the form given by the model (linearity in regression). Residuals computed from a correct model look like random noise.",
        ]],
        ["Homogeneity of variance", [
            "Unequal variance across groups (in ANOVA) or across predicted values (in regression) is called heteroscedasticity. In ANOVA the Levene or Bartlett test is used; in regression, Breusch-Pagan, White, or Glejser. The Levene statistic is essentially an ANOVA on the absolute deviations from the group median/mean:",
        ]],
        ["Independence and autocorrelation", [
            "Independence is guaranteed mainly by randomisation during the experiment; statistics cannot repair it afterwards. For sequential data, error autocorrelation is tested with Durbin-Watson: a value near 2 means no autocorrelation, near 0 means positive autocorrelation, and near 4 negative autocorrelation.",
        ]],
        ["Multicollinearity in regression", [
            "When predictors are highly correlated with one another, the coefficients become unstable. The VIF measures how much the variance of a coefficient is inflated because of the correlation of that variable with the other predictors; \\(R_j^2\\) is the coefficient of determination of the regression of \\(X_j\\) on the other predictors. A VIF above 10 is considered problematic.",
        ]],
        ["Actions when assumptions are violated", [
            "Normality violated: transformation (log, square root), robust methods, nonparametric methods, or a GLM. Unequal variance: transformation, weighted least squares, or robust standard errors. Autocorrelation: a time series model or random effects. Multicollinearity: remove collinear variables, ridge regression, or PCR.",
        ]],
    ],
    contoh=dict(
        judul="Worked example: residuals of a regression line",
        soal="The regression line \\(\\hat{y}=0.357+1.357x\\) is fitted to the following data. Compute the residuals and check their properties.",
        data=[
            ["x", "2", "4", "5", "7", "8", "10"],
            ["y", "3", "6", "7", "10", "11", "14"],
        ],
        langkah=[
            "Compute the predicted value for each x, for example for x = 2 and x = 4.",
            "The residual is y minus the prediction.",
            "All residuals: −0.071; 0.214; −0.143; 0.143; −0.214; 0.071. Their sum is zero, and the sum of squared residuals is the SSE.",
            "The Durbin-Watson statistic.",
        ],
        simpul="The residuals are very small and sum to zero, as expected from least squares. A value of d = 3.5 suggests the residual signs alternate, but with only 6 points the autocorrelation test is not meaningful. In practice, also check the residual plots.",
    ),
    faq=[
        ["Why is the sum of residuals always zero?",
         "In regression with an intercept, the least squares normal equations require \\(\\sum e_i=0\\). In regression without an intercept this property does not hold."],
        ["Which is more important, normality or homogeneity of variance?",
         "Usually homogeneity of variance and independence affect the validity of the F test more than normality does, especially with balanced data."],
        ["May I delete outliers so the assumptions are met?",
         "Do not delete just to pass a test. Trace the cause. If it is a recording error, correct it; if the observation is valid, use a robust method."],
    ],
)
