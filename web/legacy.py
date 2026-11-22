"""legacy.py – Regresi Linear (sederhana & berganda) setara halaman lama Streamlit, tanpa statsmodels (numpy/scipy)."""
import numpy as np
import pandas as pd
from scipy import stats

import reg_core as rc
from stats_engine import f4, fmt_p, sig_mark


def run_regression(df, y, xs, intercept=True, alpha=0.05):
    d0 = df[[y] + xs].apply(pd.to_numeric, errors="coerce")
    d = d0.replace([np.inf, -np.inf], np.nan).dropna()
    n, k = len(d), len(xs)
    if n < k + 2:
        raise ValueError(f"Data terlalu sedikit: n = {n}, dibutuhkan minimal {k + 2} pengamatan lengkap.")
    Xv, yv = d[xs].values.astype(float), d[y].values.astype(float)
    X = np.column_stack([np.ones(n), Xv]) if intercept else Xv
    o = rc.ols(X, yv)
    resid, fitted = o["res"], o["fit"]
    p = X.shape[1]
    dfe = n - p
    if dfe < 1:
        raise ValueError("Data terlalu sedikit dibanding jumlah parameter.")
    names = (["Intersep"] if intercept else []) + list(xs)
    s2 = o["rss"] / dfe
    se = np.sqrt(np.clip(np.diag(s2 * o["XtXi"]), 0, None))
    beta = o["beta"]
    with np.errstate(divide="ignore", invalid="ignore"):
        tval = beta / se
    pval = 2 * stats.t.sf(np.abs(tval), dfe)
    crit = stats.t.ppf(1 - alpha / 2, dfe)
    cl = int(round((1 - alpha) * 100))
    sdy = yv.std(ddof=1)
    bstd = [np.nan if (intercept and i == 0) else beta[i] * X[:, i].std(ddof=1) / sdy for i in range(p)]
    coef = pd.DataFrame({"Variabel": names, "Koefisien (B)": beta, "Std. Error": se, "t hitung": tval,
                         "P-value": [fmt_p(v) for v in pval], "Sig.": [sig_mark(v) for v in pval],
                         f"Batas bawah CI {cl}%": beta - crit * se, f"Batas atas CI {cl}%": beta + crit * se,
                         "Beta terstandar": bstd}).round(4)
    sse = o["rss"]
    if intercept:
        sst = float(((yv - yv.mean()) ** 2).sum())
        dfr = p - 1
    else:
        sst = float((yv ** 2).sum())
        dfr = p
    ssr = sst - sse
    msr = ssr / dfr
    F = msr / s2
    pF = float(stats.f.sf(F, dfr, dfe))
    r2 = 1 - sse / sst
    r2a = 1 - (1 - r2) * ((n - 1) if intercept else n) / dfe
    anova = pd.DataFrame([["Regresi", dfr, f4(ssr), f4(msr), f4(F), fmt_p(pF), sig_mark(pF)],
                          ["Sisa (Galat)", dfe, f4(sse), f4(s2), "", "", ""],
                          ["Total", dfr + dfe, f4(sst), "", "", "", ""]],
                         columns=["Sumber Keragaman", "db", "JK", "KT", "F hitung", "P-value", "Sig."])
    parts = []
    for i, nm in enumerate(names):
        b = beta[i]
        if nm == "Intersep":
            parts.append(f"{b:.4f}")
        else:
            parts.append(f"{'+' if b >= 0 else '−'} {abs(b):.4f}·{nm}" if parts else f"{b:.4f}·{nm}")
    eq = "Ŷ = " + " ".join(parts)
    ok = lambda pv: "Terpenuhi" if pv > alpha else "Tidak terpenuhi"
    rows = []
    if 3 <= n <= 5000:
        w, pw = stats.shapiro(resid)
        rows.append(["Shapiro-Wilk", "Galat menyebar normal", f4(w), fmt_p(pw), ok(pw)])
    Xc = X if intercept else np.column_stack([np.ones(n), Xv])
    try:
        lm, _ = rc._aux_lm(Xc, resid ** 2)
        pbp = stats.chi2.sf(lm, Xc.shape[1] - 1)
        rows.append(["Breusch-Pagan", "Ragam galat homogen (homoskedastis)", f4(lm), fmt_p(pbp), ok(pbp)])
    except Exception:  # noqa: BLE001
        pass
    dw = float((np.diff(resid) ** 2).sum() / (resid ** 2).sum())
    rows.append(["Durbin-Watson", "Tidak ada autokorelasi galat", f4(dw), "-",
                 "Terpenuhi (1,5–2,5)" if 1.5 <= dw <= 2.5 else "Perlu diperiksa (di luar 1,5–2,5)"])
    assump = pd.DataFrame(rows, columns=["Uji", "H0 / Asumsi", "Statistik", "P-value", "Kesimpulan"])
    vif = rc.vif_table(Xv, list(xs)) if k >= 2 else None
    H = np.einsum("ij,jk,ik->i", X, o["XtXi"], X)
    rint = resid / np.sqrt(s2 * np.clip(1 - H, 1e-12, None))
    cooks = rint ** 2 / p * H / np.clip(1 - H, 1e-12, None)
    pred_tbl = pd.DataFrame({"Y aktual": yv, "Y prediksi": fitted, "Galat (residual)": resid,
                             "Galat terstandar": resid / np.sqrt(s2), "Cook's D": cooks}, index=d.index).round(4)
    return {"data": d, "y": y, "xs": list(xs), "intercept": intercept, "n": n, "k": k, "n_dropped": len(d0) - n,
            "coef": coef, "anova": anova, "equation": eq, "assump": assump, "vif": vif, "pred_table": pred_tbl,
            "cooks": cooks, "rmse": float(np.sqrt(s2)), "r2": r2, "r2a": r2a, "F": F, "pF": pF, "beta": beta, "names": names,
            "XtXi": o["XtXi"], "s2": s2, "dfe": dfe, "fitted": fitted, "resid": resid, "tcrit": float(crit), "beta_raw": beta,
            "pvals": pval}
