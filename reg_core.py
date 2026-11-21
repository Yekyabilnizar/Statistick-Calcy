"""
reg_core.py
Inti regresi StatCalc: utilitas, spesifikasi grafik, uji asumsi/diagnostik, regresi polinomial,
regresi nonlinear dan GLM (logistik, probit, Poisson, binomial negatif, gamma; multinomial & ordinal).
Semua fungsi (kecuali multinomial/ordinal) hanya memakai numpy + scipy sehingga mudah diuji.
"""
import itertools

import numpy as np
import pandas as pd
from scipy import stats, optimize
from scipy.special import gammaln, expit

from stats_engine import f4, fmt_p, sig_mark


# ============================================================================
# Utilitas umum
# ============================================================================
def ols(X, y):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n, p = X.shape
    XtXi = np.linalg.pinv(X.T @ X)
    beta = XtXi @ X.T @ y
    fit = X @ beta
    res = y - fit
    rss = float(res @ res)
    rank = int(np.linalg.matrix_rank(X))
    dfe = n - rank
    s2 = rss / dfe if dfe > 0 else np.nan
    cov = s2 * XtXi
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    return {"beta": beta, "se": se, "fit": fit, "res": res, "rss": rss, "dfe": dfe, "s2": s2, "cov": cov,
            "XtXi": XtXi, "n": n, "p": p, "rank": rank}


def coef_table(names, beta, se, dist="t", dfe=None, alpha=0.05, extra=None):
    beta, se = np.asarray(beta, float), np.asarray(se, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        stat = beta / se
    if dist == "t":
        p = 2 * stats.t.sf(np.abs(stat), dfe)
        crit = stats.t.ppf(1 - alpha / 2, dfe)
        sname = "t hitung"
    else:
        p = 2 * stats.norm.sf(np.abs(stat))
        crit = stats.norm.ppf(1 - alpha / 2)
        sname = "z hitung"
    cl = int(round((1 - alpha) * 100))
    t = pd.DataFrame({"Variabel": names, "Koefisien (B)": beta, "Std. Error": se, sname: stat,
                      "P-value": [fmt_p(x) for x in p], "Sig.": [sig_mark(x) if np.isfinite(x) else "" for x in p],
                      f"Batas bawah CI {cl}%": beta - crit * se, f"Batas atas CI {cl}%": beta + crit * se})
    if extra:
        for k, v in extra.items():
            t[k] = v
    return t.round(4)


def numeric_frame(df, cols):
    return df[cols].apply(pd.to_numeric, errors="coerce").dropna()


def build_X(df, y, xs_num, xs_cat=()):
    """Matriks desain dengan konstanta; variabel kategorik -> dummy (level pertama = referensi)."""
    cols = [y] + list(xs_num) + list(xs_cat)
    d = df[cols].copy()
    d[y] = pd.to_numeric(d[y], errors="coerce")
    for c in xs_num:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna()
    parts = [d[list(xs_num)]] if xs_num else []
    refs = {}
    for c in xs_cat:
        lv = sorted(pd.unique(d[c].astype(str)))
        refs[c] = lv[0]
        for l in lv[1:]:
            parts.append(pd.Series((d[c].astype(str) == l).astype(float), name=f"{c}[{l}]"))
    X = pd.concat(parts, axis=1) if parts else pd.DataFrame(index=d.index)
    X.insert(0, "Intersep", 1.0)
    return d, X, refs


# ---------------------------------------------------------------------------
# Spesifikasi grafik (dirender oleh ui.draw_spec)
# ---------------------------------------------------------------------------
def spec_xy(title, xl, yl, series, band=None, xlog=False, vlines=None, hlines=None):
    return {"kind": "xy", "title": title, "xlabel": xl, "ylabel": yl, "series": series, "band": band,
            "xlog": xlog, "vlines": vlines or [], "hlines": hlines or []}


def spec_bar(title, xl, yl, x, y, err=None, horizontal=False):
    return {"kind": "bar", "title": title, "xlabel": xl, "ylabel": yl, "x": list(x), "y": list(y),
            "err": None if err is None else list(err), "horizontal": horizontal}


def spec_heat(title, z, xlabels, ylabels, zmid=None):
    return {"kind": "heat", "title": title, "z": np.asarray(z), "x": list(xlabels), "y": list(ylabels), "zmid": zmid}


def spec_contour(title, xl, yl, x, y, z, px=None, py=None):
    return {"kind": "contour", "title": title, "xlabel": xl, "ylabel": yl, "x": x, "y": y, "z": z, "px": px, "py": py}


def spec_hist(title, values, xl="Galat"):
    return {"kind": "hist", "title": title, "values": np.asarray(values), "xlabel": xl}


def spec_qq(title, values):
    return {"kind": "qq", "title": title, "values": np.asarray(values)}


def resid_specs(fitted, resid):
    return [spec_xy("Galat vs Nilai Prediksi", "Nilai prediksi", "Galat",
                    [{"x": fitted, "y": resid, "mode": "markers", "name": "Galat"}], hlines=[0.0]),
            spec_qq("Normal Q-Q Plot Galat", resid),
            spec_hist("Histogram Galat", resid)]


def std_result(kind, title, data, kpis, tables, plots, notes=None, eq=None, warn=None, extra=None):
    return {"kind": kind, "title": title, "data": data, "kpis": kpis, "tables": tables, "plots": plots,
            "notes": notes or [], "eq": eq, "warn": warn or [], "extra": extra or {}}


def aic_ols(rss, n, k):
    return n * np.log(rss / n) + 2 * (k + 1)


def bic_ols(rss, n, k):
    return n * np.log(rss / n) + np.log(n) * (k + 1)


# ============================================================================
# Uji asumsi & diagnostik regresi (numpy/scipy)
# ============================================================================
def _lilliefors_p(z, n_sim=2000, seed=0):
    d_obs = stats.kstest((z - z.mean()) / z.std(ddof=1), "norm").statistic
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(n_sim):
        s = rng.standard_normal(len(z))
        if stats.kstest((s - s.mean()) / s.std(ddof=1), "norm").statistic >= d_obs:
            cnt += 1
    return d_obs, (cnt + 1) / (n_sim + 1)


def _aux_lm(X, target):
    """LM = n R^2 dari regresi bantu 'target' pada X (X sudah memuat konstanta)."""
    o = ols(X, target)
    tss = float(((target - target.mean()) ** 2).sum())
    r2 = 1 - o["rss"] / tss if tss > 0 else 0.0
    return len(target) * r2, o


def vif_table(Xv, names):
    """Xv: matriks tanpa konstanta."""
    rows = []
    n, k = Xv.shape
    for j in range(k):
        others = np.delete(Xv, j, axis=1)
        Z = np.column_stack([np.ones(n), others]) if k > 1 else np.ones((n, 1))
        o = ols(Z, Xv[:, j])
        tss = float(((Xv[:, j] - Xv[:, j].mean()) ** 2).sum())
        r2 = 1 - o["rss"] / tss if tss > 0 else 0
        vif = 1 / (1 - r2) if r2 < 1 else np.inf
        rows.append([names[j], vif, 1 / vif if np.isfinite(vif) else 0.0,
                     "Multikolinearitas tinggi (>10)" if vif > 10 else "Perlu diperhatikan (5–10)" if vif > 5 else "Aman (<5)"])
    return pd.DataFrame(rows, columns=["Variabel", "VIF", "Tolerance", "Keterangan"]).round(4)


def run_diagnostics(df, y, xs, intercept=True, alpha=0.05, bg_lags=2):
    d = numeric_frame(df, [y] + list(xs))
    n, k = len(d), len(xs)
    if n < k + 3:
        raise ValueError(f"Data terlalu sedikit: n = {n}, minimal {k + 3} pengamatan lengkap.")
    Xv = d[list(xs)].values.astype(float)
    yv = d[y].values.astype(float)
    X = np.column_stack([np.ones(n), Xv]) if intercept else Xv
    o = ols(X, yv)
    e, fit, p = o["res"], o["fit"], o["rank"]
    s2 = o["rss"] / (n - p)
    ok = lambda pv: "Terpenuhi" if pv > alpha else "Tidak terpenuhi"

    norm_rows = []
    if 3 <= n <= 5000:
        w, pw = stats.shapiro(e)
        norm_rows.append(["Shapiro-Wilk", "Galat menyebar normal", w, fmt_p(pw), ok(pw)])
    if n >= 8:
        jb, pj = stats.jarque_bera(e)
        norm_rows.append(["Jarque-Bera", "Skewness = 0 dan kurtosis berlebih = 0", jb, fmt_p(pj), ok(pj)])
    dks, pks = _lilliefors_p(e)
    norm_rows.append(["Kolmogorov-Smirnov (Lilliefors, simulasi)", "Galat menyebar normal", dks, fmt_p(pks), ok(pks)])
    ad = stats.anderson(e, dist="norm")
    idx = {0.01: 4, 0.05: 2, 0.10: 1}.get(round(alpha, 2), 2)
    crit = ad.critical_values[idx]
    norm_rows.append(["Anderson-Darling", f"A² < nilai kritis ({crit:.3f})", ad.statistic, "-",
                      "Terpenuhi" if ad.statistic < crit else "Tidak terpenuhi"])
    normal = pd.DataFrame(norm_rows, columns=["Uji", "H0 / Asumsi", "Statistik", "P-value", "Kesimpulan"])

    het_rows = []
    Xc = X if intercept else np.column_stack([np.ones(n), Xv])
    kk = Xc.shape[1] - 1
    lm, _ = _aux_lm(Xc, e ** 2)
    pbp = stats.chi2.sf(lm, kk)
    het_rows.append(["Breusch-Pagan (Koenker)", "Ragam galat homogen", lm, fmt_p(pbp), ok(pbp)])
    cols = [np.ones(n)] + [Xv[:, j] for j in range(k)]
    for i, j in itertools.combinations_with_replacement(range(k), 2):
        cols.append(Xv[:, i] * Xv[:, j])
    W = np.column_stack(cols)
    keep = [0]
    for j in range(1, W.shape[1]):
        t = np.column_stack([W[:, keep], W[:, j]])
        if np.linalg.matrix_rank(t) > len(keep):
            keep.append(j)
    W = W[:, keep]
    if W.shape[0] > W.shape[1] + 1:
        lmw, _ = _aux_lm(W, e ** 2)
        pw_ = stats.chi2.sf(lmw, W.shape[1] - 1)
        het_rows.append(["White", "Ragam galat homogen", lmw, fmt_p(pw_), ok(pw_)])
    og = ols(Xc, np.abs(e))
    tssg = float(((np.abs(e) - np.abs(e).mean()) ** 2).sum())
    Fg = ((tssg - og["rss"]) / kk) / (og["rss"] / (n - Xc.shape[1])) if kk > 0 and og["rss"] > 0 else np.nan
    pg = stats.f.sf(Fg, kk, n - Xc.shape[1]) if np.isfinite(Fg) else np.nan
    het_rows.append(["Glejser (|galat| ~ X)", "Ragam galat homogen", Fg, fmt_p(pg), ok(pg) if np.isfinite(pg) else "-"])
    hetero = pd.DataFrame(het_rows, columns=["Uji", "H0 / Asumsi", "Statistik", "P-value", "Kesimpulan"])

    dw = float((np.diff(e) ** 2).sum() / (e ** 2).sum())
    ac_rows = [["Durbin-Watson", "Tidak ada autokorelasi (≈ 2)", dw, "-",
                "Terpenuhi (1,5–2,5)" if 1.5 <= dw <= 2.5 else "Perlu diperiksa (di luar 1,5–2,5)"]]
    for m in range(1, bg_lags + 1):
        lag = np.column_stack([np.concatenate([np.zeros(l), e[:-l]]) for l in range(1, m + 1)])
        lmb, _ = _aux_lm(np.column_stack([Xc, lag]), e)
        pb = stats.chi2.sf(lmb, m)
        ac_rows.append([f"Breusch-Godfrey (lag {m})", f"Tidak ada autokorelasi orde ≤ {m}", lmb, fmt_p(pb), ok(pb)])
    auto = pd.DataFrame(ac_rows, columns=["Uji", "H0 / Asumsi", "Statistik", "P-value", "Kesimpulan"])

    vif = vif_table(Xv, list(xs)) if k >= 2 else None
    cond = None
    if k >= 2:
        Z = (Xv - Xv.mean(0)) / Xv.std(0, ddof=1)
        sv = np.linalg.svd(Z, compute_uv=False)
        cond = float(sv[0] / sv[-1])

    H = np.einsum("ij,jk,ik->i", X, o["XtXi"], X)
    r_int = e / np.sqrt(s2 * np.clip(1 - H, 1e-12, None))
    t_ext = r_int * np.sqrt((n - p - 1) / np.clip(n - p - r_int ** 2, 1e-12, None))
    cook = r_int ** 2 / p * H / np.clip(1 - H, 1e-12, None)
    dffits = t_ext * np.sqrt(H / np.clip(1 - H, 1e-12, None))
    flag = []
    for i in range(n):
        f = []
        if H[i] > 2 * p / n:
            f.append("leverage tinggi")
        if cook[i] > 4 / n:
            f.append("Cook's D > 4/n")
        if abs(t_ext[i]) > 3:
            f.append("outlier (|t|>3)")
        if abs(dffits[i]) > 2 * np.sqrt(p / n):
            f.append("DFFITS besar")
        flag.append(", ".join(f))
    infl = pd.DataFrame({"Pengamatan": d.index.astype(str), "Y": yv, "Prediksi": fit, "Galat": e,
                         "Leverage (h)": H, "Galat stud. (eksternal)": t_ext, "Cook's D": cook, "DFFITS": dffits,
                         "Catatan": flag}).round(4)

    plots = resid_specs(fit, e)
    plots += [spec_bar("Jarak Cook (Pengamatan Berpengaruh)", "Pengamatan", "Cook's D", [str(i) for i in d.index], cook),
              spec_xy("Leverage vs Galat Terstudentisasi", "Leverage (h)", "Galat terstudentisasi (eksternal)",
                      [{"x": H, "y": t_ext, "mode": "markers", "name": "Pengamatan"}], hlines=[0.0, 3.0, -3.0],
                      vlines=[2 * p / n])]
    n_bad = sum(1 for t in (normal, hetero, auto) for v in t["Kesimpulan"] if v.startswith(("Tidak", "Perlu")))
    nflag = sum(1 for f in flag if f)
    notes = []
    for nm, t in (("Normalitas galat", normal), ("Homoskedastisitas", hetero), ("Autokorelasi", auto)):
        bad = [r["Uji"] for _, r in t.iterrows() if r["Kesimpulan"].startswith(("Tidak", "Perlu"))]
        notes.append(f"**{nm}:** " + ("seluruh uji terpenuhi." if not bad else "tidak terpenuhi menurut " + ", ".join(bad) + "."))
    if vif is not None:
        hi = vif[vif["VIF"] > 10]["Variabel"].tolist()
        notes.append("**Multikolinearitas:** " + ("semua VIF < 10 (aman)." if not hi else "VIF > 10 pada " + ", ".join(hi) + "."))
    notes.append(f"**Pengamatan berpengaruh:** {nflag} dari {n} pengamatan ditandai (lihat tabel Pengaruh).")
    notes.append("Autokorelasi bermakna jika data berurutan (deret waktu); urutan baris dianggap urutan waktu.")
    tables = {"Normalitas galat": normal, "Homoskedastisitas": hetero, "Autokorelasi": auto}
    if vif is not None:
        tables["Multikolinearitas (VIF)"] = vif
    tables["Pengamatan berpengaruh"] = infl
    kp = [("n", n), ("Jumlah X", k), ("Durbin-Watson", f"{dw:.3f}"), ("Uji tak terpenuhi", n_bad),
          ("Pengamatan ditandai", nflag)] + ([("Condition number", f"{cond:.1f}")] if cond else [])
    return std_result("diag", "Diagnostik Regresi", d, kp, tables, plots, notes=notes,
                      extra={"fitted": fit, "resid": e})


# ============================================================================
# Regresi polinomial
# ============================================================================
def poly_degree_table(df, x, y, max_degree=5):
    d = numeric_frame(df, [x, y])
    xv, yv = d[x].values.astype(float), d[y].values.astype(float)
    n = len(yv)
    sst = float(((yv - yv.mean()) ** 2).sum())
    rows, prev = [], None
    for g in range(1, max_degree + 1):
        if n <= g + 1:
            break
        X = np.vander(xv - xv.mean(), g + 1, increasing=True)
        o = ols(X, yv)
        r2 = 1 - o["rss"] / sst
        r2a = 1 - (o["rss"] / o["dfe"]) / (sst / (n - 1))
        Fc, pc = np.nan, np.nan
        if prev is not None and o["dfe"] > 0:
            Fc = (prev - o["rss"]) / (o["rss"] / o["dfe"])
            pc = stats.f.sf(Fc, 1, o["dfe"])
        rows.append([g, r2, r2a, np.sqrt(o["rss"] / o["dfe"]) if o["dfe"] > 0 else np.nan,
                     aic_ols(o["rss"], n, g + 1), bic_ols(o["rss"], n, g + 1), Fc, fmt_p(pc) if not np.isnan(pc) else "-"])
        prev = o["rss"]
    t = pd.DataFrame(rows, columns=["Derajat", "R²", "R² Adjusted", "RMSE", "AIC", "BIC", "F tambahan suku", "P-value tambahan"]).round(4)
    best = int(t.loc[t["BIC"].idxmin(), "Derajat"])
    return t, best


def run_polynomial(df, x, y, degree, center=True, alpha=0.05):
    d = numeric_frame(df, [x, y])
    xv, yv = d[x].values.astype(float), d[y].values.astype(float)
    n = len(yv)
    if n <= degree + 1:
        raise ValueError(f"Data terlalu sedikit untuk polinomial derajat {degree} (n = {n}).")
    m = xv.mean() if center else 0.0
    X = np.vander(xv - m, degree + 1, increasing=True)
    o = ols(X, yv)
    names = ["Intersep"] + [(f"({x}−{m:.3g})" if center else x) + ("" if k == 1 else f"^{k}") for k in range(1, degree + 1)]
    tbl = coef_table(names, o["beta"], o["se"], "t", o["dfe"], alpha)
    sst = float(((yv - yv.mean()) ** 2).sum())
    r2 = 1 - o["rss"] / sst
    r2a = 1 - (o["rss"] / o["dfe"]) / (sst / (n - 1))
    ssr = sst - o["rss"]
    Fm = (ssr / degree) / o["s2"]
    pm = float(stats.f.sf(Fm, degree, o["dfe"]))
    anova = pd.DataFrame([["Regresi", degree, f4(ssr), f4(ssr / degree), f4(Fm), fmt_p(pm), sig_mark(pm)],
                          ["Galat", o["dfe"], f4(o["rss"]), f4(o["s2"]), "", "", ""],
                          ["Total", n - 1, f4(sst), "", "", "", ""]],
                         columns=["Sumber Keragaman", "db", "JK", "KT", "F hitung", "P-value", "Sig."])
    dtab, best = poly_degree_table(df, x, y, max(5, degree))
    g = np.linspace(xv.min(), xv.max(), 120)
    G = np.vander(g - m, degree + 1, increasing=True)
    fg = G @ o["beta"]
    sg = np.sqrt(np.einsum("ij,jk,ik->i", G, o["cov"], G))
    tc = stats.t.ppf(1 - alpha / 2, o["dfe"])
    plots = [spec_xy(f"Kurva Polinomial Derajat {degree} ({y} ~ {x})", x, y,
                     [{"x": xv, "y": yv, "mode": "markers", "name": "Data"},
                      {"x": g, "y": fg, "mode": "lines", "name": f"Derajat {degree}"}],
                     band={"x": g, "lo": fg - tc * sg, "hi": fg + tc * sg, "name": f"CI {int((1 - alpha) * 100)}%"})]
    plots += resid_specs(o["fit"], o["res"])
    b = o["beta"]
    eq = "Ŷ = " + " ".join((f"{b[0]:.4f}" if k == 0 else f"{'+' if b[k] >= 0 else '−'} {abs(b[k]):.4f}·{names[k]}")
                           for k in range(len(b)))
    ext = None
    if degree == 2 and b[2] != 0:
        ext = m - b[1] / (2 * b[2])
    notes = [f"**Uji simultan:** F = {Fm:.3f}, P = {fmt_p(pm)} → model {'signifikan' if pm < alpha else 'tidak signifikan'}.",
             f"**R² adjusted** = {r2a:.4f}. Derajat terbaik menurut BIC: **{best}** (lihat tabel pemilihan derajat).",
             "Suku berderajat tertinggi yang tidak nyata menandakan derajat bisa diturunkan."]
    if ext is not None:
        notes.append(f"**Titik ekstrem kuadratik** pada {x} ≈ {ext:.4f} ({'maksimum' if b[2] < 0 else 'minimum'}).")
    if center:
        notes.append(f"X dipusatkan pada rata-ratanya ({m:.4g}) untuk mengurangi multikolinearitas antar-suku.")
    return std_result("poly", f"Regresi Polinomial Derajat {degree}", d,
                      [("n", n), ("R²", f"{r2:.4f}"), ("R² Adjusted", f"{r2a:.4f}"), ("F hitung", f"{Fm:.3f}"),
                       ("P-value (F)", fmt_p(pm)), ("RMSE", f"{np.sqrt(o['s2']):.4f}")],
                      {"Koefisien": tbl, "ANOVA": anova, "Pemilihan derajat": dtab,
                       "Nilai aktual & prediksi": pd.DataFrame({x: xv, y: yv, "Prediksi": o["fit"], "Galat": o["res"]}).round(4)},
                      plots, notes=notes, eq=eq, extra={"fitted": o["fit"], "resid": o["res"], "best_degree": best})


# ============================================================================
# Regresi nonlinear
# ============================================================================
def _p0_exp(x, y):
    c = []
    if (y > 0).all():
        b, la = np.polyfit(x, np.log(y), 1)
        c.append([np.exp(la), b])
    c += [[float(np.mean(y)), 0.01], [float(np.mean(y)), -0.01], [float(y[0]) or 1.0, 0.1]]
    return c


def _p0_log(x, y):
    return [[float(np.mean(y)), 1.0],
            [float(y.min()), float(y.max() - y.min()) / max(np.log(x.max() / max(x.min(), 1e-9)), 1e-9)]]


def _p0_pow(x, y):
    c = []
    if (x > 0).all() and (y > 0).all():
        b, la = np.polyfit(np.log(x), np.log(y), 1)
        c.append([np.exp(la), b])
    c += [[1.0, 1.0], [1.0, 0.5], [float(np.mean(y)), 1.0]]
    return c


def _p0_logistic(x, y):
    K = float(y.max()) * 1.1 or 1.0
    x0 = float(x[np.argmin(np.abs(y - K / 2))])
    rng = float(x.max() - x.min()) or 1.0
    return [[K, r, x0] for r in (4 / rng, 8 / rng, 1.5 / rng, -4 / rng)]


def _p0_mm(x, y):
    return [[float(y.max()) * 1.2 or 1.0, float(np.median(x)) or 1.0], [float(y.max()) * 2, float(x.max())]]


def _p0_gomp(x, y):
    a = float(y.max()) * 1.1 or 1.0
    rng = float(x.max() - x.min()) or 1.0
    return [[a, b, cc] for cc in (4 / rng, 1 / rng, 10 / rng, 2 / rng) for b in (2.0, 5.0, 1.0, 8.0)]


NL_MODELS = {
    "Eksponensial": {"f": lambda x, a, b: a * np.exp(b * x), "par": ["a", "b"], "eq": "Y = a·exp(b·X)", "p0": _p0_exp, "pos_x": False},
    "Logaritmik": {"f": lambda x, a, b: a + b * np.log(x), "par": ["a", "b"], "eq": "Y = a + b·ln(X)", "p0": _p0_log, "pos_x": True},
    "Power (pangkat)": {"f": lambda x, a, b: a * np.power(x, b), "par": ["a", "b"], "eq": "Y = a·X^b", "p0": _p0_pow, "pos_x": True},
    "Logistik (pertumbuhan)": {"f": lambda x, K, r, x0: K / (1 + np.exp(-r * (x - x0))), "par": ["K", "r", "x0"],
                               "eq": "Y = K / (1 + exp(−r·(X − x0)))", "p0": _p0_logistic, "pos_x": False},
    "Michaelis-Menten": {"f": lambda x, V, K: V * x / (K + x), "par": ["Vmax", "Km"], "eq": "Y = Vmax·X / (Km + X)", "p0": _p0_mm, "pos_x": False},
    "Gompertz": {"f": lambda x, a, b, c: a * np.exp(-b * np.exp(-c * x)), "par": ["a", "b", "c"],
                 "eq": "Y = a·exp(−b·exp(−c·X))", "p0": _p0_gomp, "pos_x": False},
}


def _fit_nl(model, x, y):
    spec = NL_MODELS[model]
    if spec["pos_x"] and (x <= 0).any():
        raise ValueError(f"Model {model} memerlukan X > 0.")
    best = None
    for p0 in spec["p0"](x, y):
        try:
            with np.errstate(all="ignore"):
                popt, pcov = optimize.curve_fit(spec["f"], x, y, p0=p0, maxfev=60000)
            rss = float(((y - spec["f"](x, *popt)) ** 2).sum())
            if np.isfinite(rss) and (best is None or rss < best[0]):
                best = (rss, popt, pcov)
        except Exception:
            continue
    if best is None:
        raise ValueError(f"Model {model} tidak konvergen untuk data ini. Coba model lain atau periksa data.")
    return best


def _num_grad(f, x, popt):
    g = []
    for j in range(len(popt)):
        h = 1e-6 * max(abs(popt[j]), 1.0)
        a, b = popt.copy(), popt.copy()
        a[j] += h
        b[j] -= h
        g.append((f(x, *a) - f(x, *b)) / (2 * h))
    return np.column_stack(g)


def run_nonlinear(df, x, y, model, alpha=0.05):
    d = numeric_frame(df, [x, y])
    xv, yv = d[x].values.astype(float), d[y].values.astype(float)
    n = len(yv)
    spec = NL_MODELS[model]
    npar = len(spec["par"])
    if n <= npar + 1:
        raise ValueError(f"Data terlalu sedikit untuk model {model} ({npar} parameter).")
    rss, popt, pcov = _fit_nl(model, xv, yv)
    dfe = n - npar
    se = np.sqrt(np.clip(np.diag(pcov), 0, None))
    tbl = coef_table(spec["par"], popt, se, "t", dfe, alpha).rename(columns={"Variabel": "Parameter"})
    fit = spec["f"](xv, *popt)
    res = yv - fit
    sst = float(((yv - yv.mean()) ** 2).sum())
    r2 = 1 - rss / sst
    r2a = 1 - (rss / dfe) / (sst / (n - 1))
    g = np.linspace(xv.min(), xv.max(), 150)
    fg = spec["f"](g, *popt)
    J = _num_grad(spec["f"], g, popt)
    sg = np.sqrt(np.clip(np.einsum("ij,jk,ik->i", J, pcov, J), 0, None))
    tcrit = stats.t.ppf(1 - alpha / 2, dfe)
    plots = [spec_xy(f"Kurva {model} ({y} ~ {x})", x, y,
                     [{"x": xv, "y": yv, "mode": "markers", "name": "Data"}, {"x": g, "y": fg, "mode": "lines", "name": model}],
                     band={"x": g, "lo": fg - tcrit * sg, "hi": fg + tcrit * sg, "name": f"CI {int((1 - alpha) * 100)}% rata-rata"})]
    plots += resid_specs(fit, res)
    rows = []
    for m in NL_MODELS:
        try:
            r_, _, _ = _fit_nl(m, xv, yv)
            k_ = len(NL_MODELS[m]["par"])
            rows.append([m, k_, 1 - r_ / sst, np.sqrt(r_ / (n - k_)) if n > k_ else np.nan, aic_ols(r_, n, k_), bic_ols(r_, n, k_)])
        except Exception:
            rows.append([m, len(NL_MODELS[m]["par"]), np.nan, np.nan, np.nan, np.nan])
    cmp_ = pd.DataFrame(rows, columns=["Model", "Parameter", "R² (pseudo)", "RMSE", "AIC", "BIC"]).sort_values("AIC").round(4)
    eq = f"{spec['eq']}   dengan " + ", ".join(f"{p} = {v:.4f}" for p, v in zip(spec["par"], popt))
    notes = [f"**Model {model}** menjelaskan {r2 * 100:.2f}% keragaman {y} (R² pseudo = 1 − JKG/JKT; R² adjusted = {r2a:.4f}).",
             "Uji t pada parameter menguji H₀: parameter = 0 (galat baku dari aproksimasi linear di sekitar taksiran).",
             f"Pembanding antar model memakai AIC (lebih kecil lebih baik); model dengan AIC terendah: **{cmp_.iloc[0]['Model']}**."]
    pred = pd.DataFrame({x: xv, y: yv, "Prediksi": fit, "Galat": res}).round(4)
    return std_result("nonlinear", f"Regresi Nonlinear – {model}", d,
                      [("n", n), ("R² (pseudo)", f"{r2:.4f}"), ("R² Adjusted", f"{r2a:.4f}"), ("RMSE", f"{np.sqrt(rss / dfe):.4f}"),
                       ("AIC", f"{aic_ols(rss, n, npar):.2f}"), ("Parameter", npar)],
                      {"Parameter": tbl, "Perbandingan model": cmp_, "Nilai aktual & prediksi": pred}, plots, notes=notes, eq=eq,
                      extra={"fitted": fit, "resid": res})


# ============================================================================
# GLM (IRLS) – binomial (logit/probit), Poisson, binomial negatif, gamma
# ============================================================================
def _mu_from_eta(eta, family, link):
    if family == "binomial":
        return expit(eta) if link == "logit" else stats.norm.cdf(eta)
    return np.exp(np.clip(eta, -30, 30))


def _dev_i(y, mu, family, alpha_nb=None):
    """Kontribusi deviance tiap pengamatan."""
    mu = np.clip(mu, 1e-10, None)
    if family == "binomial":
        mu = np.clip(mu, 1e-10, 1 - 1e-10)
        return -2 * (y * np.log(mu) + (1 - y) * np.log(1 - mu))
    ylog = np.where(y > 0, y * np.log(np.where(y > 0, y, 1) / mu), 0.0)
    if family == "poisson":
        return 2 * (ylog - (y - mu))
    if family == "nb":
        a = alpha_nb
        return 2 * (ylog - (y + 1 / a) * np.log((1 + a * y) / (1 + a * mu)))
    return 2 * (-np.log(y / mu) + (y - mu) / mu)


def _deviance(y, mu, family, alpha_nb=None):
    return float(_dev_i(y, mu, family, alpha_nb).sum())


def _irls(X, y, family, link, alpha_nb=None, maxit=100, tol=1e-10):
    n, p = X.shape
    if family == "binomial":
        mu = (y + 0.5) / 2
    elif family in ("poisson", "nb"):
        mu = y + 0.5
    else:
        mu = np.where(y > 0, y, y[y > 0].mean())
    if family == "binomial":
        eta = np.log(mu / (1 - mu)) if link == "logit" else stats.norm.ppf(mu)
    else:
        eta = np.log(mu)
    beta = np.zeros(p)
    dev_old = np.inf
    conv = False
    it = 0
    for it in range(maxit):
        if family == "binomial" and link == "logit":
            mu = expit(eta)
            dmu = mu * (1 - mu)
            var = dmu
        elif family == "binomial":
            mu = stats.norm.cdf(eta)
            dmu = stats.norm.pdf(eta)
            var = mu * (1 - mu)
        else:
            mu = np.exp(np.clip(eta, -30, 30))
            dmu = mu
            var = mu if family == "poisson" else (mu + alpha_nb * mu ** 2 if family == "nb" else mu ** 2)
        dmu = np.clip(dmu, 1e-10, None)
        var = np.clip(var, 1e-10, None)
        W = dmu ** 2 / var
        z = eta + (y - mu) / dmu
        XtW = X.T * W
        try:
            beta_new = np.linalg.solve(XtW @ X, XtW @ z)
        except np.linalg.LinAlgError:
            beta_new = np.linalg.lstsq(XtW @ X, XtW @ z, rcond=None)[0]
        eta = X @ beta_new
        dev = _deviance(y, _mu_from_eta(eta, family, link), family, alpha_nb)
        if abs(dev - dev_old) / (abs(dev) + 0.1) < tol:
            beta, conv = beta_new, True
            break
        beta, dev_old = beta_new, dev
    mu = _mu_from_eta(X @ beta, family, link)
    if family == "binomial" and link == "logit":
        W = mu * (1 - mu)
    elif family == "binomial":
        W = stats.norm.pdf(X @ beta) ** 2 / np.clip(mu * (1 - mu), 1e-10, None)
    elif family == "poisson":
        W = mu
    elif family == "nb":
        W = mu / (1 + alpha_nb * mu)
    else:
        W = np.ones(n)
    W = np.clip(W, 1e-10, None)
    return {"beta": beta, "mu": mu, "W": W, "cov_u": np.linalg.pinv(X.T @ (X * W[:, None])), "conv": conv, "iter": it + 1}


def _loglik(y, mu, family, alpha_nb=None, phi=None):
    mu = np.clip(mu, 1e-10, None)
    if family == "binomial":
        mu = np.clip(mu, 1e-10, 1 - 1e-10)
        return float(np.sum(y * np.log(mu) + (1 - y) * np.log(1 - mu)))
    if family == "poisson":
        return float(np.sum(y * np.log(mu) - mu - gammaln(y + 1)))
    if family == "nb":
        r = 1 / alpha_nb
        return float(np.sum(gammaln(y + r) - gammaln(r) - gammaln(y + 1) + r * np.log(r / (r + mu)) + y * np.log(mu / (r + mu))))
    nu = 1 / phi
    return float(np.sum(nu * np.log(nu * y / mu) - nu * y / mu - np.log(y) - gammaln(nu)))


def _fit_glm(X, y, family, link):
    n, p = X.shape
    if family == "nb":
        def nll(la):
            f_ = _irls(X, y, "nb", "log", alpha_nb=np.exp(la))
            return -_loglik(y, f_["mu"], "nb", np.exp(la))
        r = optimize.minimize_scalar(nll, bounds=(-10, 3), method="bounded")
        a = float(np.exp(r.x))
        f = _irls(X, y, "nb", "log", alpha_nb=a)
        f.update(alpha=a, ll=_loglik(y, f["mu"], "nb", a), phi=1.0)
        return f
    f = _irls(X, y, family, link)
    if family == "gamma":
        f["phi"] = float((((y - f["mu"]) / f["mu"]) ** 2).sum() / (n - p))
        f["ll"] = _loglik(y, f["mu"], "gamma", phi=f["phi"])
    else:
        f["phi"] = 1.0
        f["ll"] = _loglik(y, f["mu"], family)
    return f


def classification(y, prob, cutoff=0.5):
    pred = (prob >= cutoff).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    cm = pd.DataFrame([[tn, fp], [fn, tp]], index=["Aktual 0", "Aktual 1"], columns=["Prediksi 0", "Prediksi 1"])
    return {"cm": cm, "acc": (tp + tn) / len(y), "sens": tp / (tp + fn) if tp + fn else np.nan,
            "spec": tn / (tn + fp) if tn + fp else np.nan, "prec": tp / (tp + fp) if tp + fp else np.nan}


def auc_roc(y, prob):
    r = stats.rankdata(prob)
    n1, n0 = int((y == 1).sum()), int((y == 0).sum())
    auc = (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    thr = np.unique(prob)[::-1]
    tpr = [0.0] + [float(((prob >= t) & (y == 1)).sum() / n1) for t in thr] + [1.0]
    fpr = [0.0] + [float(((prob >= t) & (y == 0)).sum() / n0) for t in thr] + [1.0]
    return float(auc), np.array(fpr), np.array(tpr)


def hosmer_lemeshow(y, prob, g=10):
    order = np.argsort(prob)
    chi, rows = 0.0, []
    for gi, idx in enumerate(np.array_split(order, g)):
        n_g, o, e = len(idx), y[idx].sum(), prob[idx].sum()
        pbar = e / n_g
        den = n_g * pbar * (1 - pbar)
        chi += (o - e) ** 2 / den if den > 0 else 0
        rows.append([gi + 1, n_g, o, e])
    dfh = g - 2
    return float(chi), dfh, float(stats.chi2.sf(chi, dfh)), pd.DataFrame(rows, columns=["Kelompok", "n", "Teramati (Y=1)", "Harapan"]).round(3)


GLM_INFO = {
    "logit": ("binomial", "logit", "Regresi Logistik Biner", "Odds Ratio"),
    "probit": ("binomial", "probit", "Regresi Probit", "exp(B)"),
    "poisson": ("poisson", "log", "Regresi Poisson", "IRR"),
    "negbin": ("nb", "log", "Regresi Binomial Negatif", "IRR"),
    "gamma": ("gamma", "log", "Regresi Gamma (link log)", "exp(B)"),
}


def run_glm(df, y, xs_num, xs_cat, kind, alpha=0.05, cutoff=0.5):
    family, link, title, exp_name = GLM_INFO[kind]
    if not xs_num and not xs_cat:
        raise ValueError("Pilih minimal satu variabel independen.")
    d0 = df[[y] + list(xs_num) + list(xs_cat)].copy()
    classes = None
    if family == "binomial":
        d0 = d0.dropna()
        cls = sorted(pd.unique(d0[y].astype(str)))
        if len(cls) != 2:
            raise ValueError(f"Variabel respon harus biner (2 kategori); ditemukan {len(cls)} kategori.")
        yn = pd.to_numeric(d0[y], errors="coerce")
        if yn.notna().all() and set(yn.unique()) <= {0, 1}:
            d0[y] = yn
            classes = ("0", "1")
        else:
            d0[y] = (d0[y].astype(str) == cls[1]).astype(int)
            classes = (cls[0], cls[1])
    d, X, refs = build_X(d0, y, xs_num, xs_cat)
    yv = d[y].values.astype(float)
    n, p = X.shape
    if n < p + 2:
        raise ValueError(f"Data terlalu sedikit: n = {n}, parameter = {p}.")
    if family in ("poisson", "nb") and ((yv < 0).any() or (np.abs(yv - np.round(yv)) > 1e-9).any()):
        raise ValueError("Respon untuk regresi Poisson/Binomial Negatif harus bilangan cacah (≥ 0).")
    if family == "gamma" and (yv <= 0).any():
        raise ValueError("Respon untuk regresi Gamma harus bernilai positif (> 0).")
    f = _fit_glm(X.values.astype(float), yv, family, link)
    beta, mu = f["beta"], f["mu"]
    se = np.sqrt(np.diag(f["cov_u"]) * (f["phi"] if family == "gamma" else 1.0))
    dist = "t" if family == "gamma" else "z"
    names = list(X.columns)
    ci_crit = stats.t.ppf(1 - alpha / 2, n - p) if dist == "t" else stats.norm.ppf(1 - alpha / 2)
    ex = {exp_name: np.exp(beta), f"{exp_name} CI bawah": np.exp(beta - ci_crit * se),
          f"{exp_name} CI atas": np.exp(beta + ci_crit * se)}
    tbl = coef_table(names, beta, se, dist, n - p, alpha, ex)
    pvals = [2 * (stats.t.sf(abs(b / s), n - p) if dist == "t" else stats.norm.sf(abs(b / s))) for b, s in zip(beta, se)]
    f0 = _fit_glm(np.ones((n, 1)), yv, family, link)
    ll, ll0 = f["ll"], f0["ll"]
    dev = _deviance(yv, mu, family, f.get("alpha"))
    dev0 = _deviance(yv, f0["mu"], family, f.get("alpha"))
    k_par = p + (1 if family in ("nb", "gamma") else 0)
    aic, bic = -2 * ll + 2 * k_par, -2 * ll + np.log(n) * k_par
    lr = 2 * (ll - ll0)
    p_lr = float(stats.chi2.sf(max(lr, 0), p - 1))
    mcf = 1 - ll / ll0 if ll0 != 0 else np.nan
    kp = [("n", n), ("Log-likelihood", f"{ll:.3f}"), ("AIC", f"{aic:.2f}"), ("BIC", f"{bic:.2f}"),
          ("LR χ²", f"{lr:.3f}"), ("P-value (LR)", fmt_p(p_lr))]
    if family != "gamma":
        kp.append(("McFadden R²", f"{mcf:.4f}"))
    tables, plots, notes, warn = {}, [], [], []
    fit_tbl = pd.DataFrame({"Ukuran": ["Deviance model", "Deviance model nol", "Log-likelihood", "AIC", "BIC", "Uji rasio likelihood (χ²)",
                                       "db LR", "P-value (LR)", "McFadden R²", "Iterasi IRLS"],
                            "Nilai": [dev, dev0, ll, aic, bic, lr, p - 1, fmt_p(p_lr), mcf, f["iter"]]})
    fit_tbl["Nilai"] = fit_tbl["Nilai"].map(lambda v: f"{v:.4f}" if isinstance(v, (float, np.floating)) else str(v))
    tables["Koefisien"] = tbl
    tables["Ukuran kecocokan model"] = fit_tbl
    if not f["conv"]:
        warn.append("IRLS tidak mencapai konvergensi penuh; hasil perlu diperiksa (kemungkinan separasi sempurna/multikolinearitas).")
    if family == "binomial" and np.abs(beta).max() > 15:
        warn.append("Koefisien sangat besar mengindikasikan separasi (quasi-complete); taksiran tidak stabil.")
    resid_dev = np.sign(yv - mu) * np.sqrt(np.clip(_dev_i(yv, mu, family, f.get("alpha")), 0, None))
    vfun = (mu * (1 - mu) if family == "binomial" else mu if family == "poisson"
            else mu + f.get("alpha", 0) * mu ** 2 if family == "nb" else mu ** 2)
    resid_pear = (yv - mu) / np.sqrt(np.clip(vfun, 1e-10, None))
    extra = {"fitted": mu, "classes": classes, "family": family, "y": yv, "X": X, "beta": beta, "cov": f["cov_u"],
             "resid": resid_dev, "names": names}
    if family == "binomial":
        cl = classification(yv, mu, cutoff)
        auc, fpr, tpr = auc_roc(yv, mu)
        chi, dfh, ph, hl = hosmer_lemeshow(yv, mu)
        tables["Tabel klasifikasi"] = cl["cm"].reset_index().rename(columns={"index": "Aktual"})
        tables["Ukuran klasifikasi"] = pd.DataFrame({
            "Ukuran": ["Akurasi", "Sensitivitas (recall)", "Spesifisitas", "Presisi", "AUC (ROC)", "Hosmer-Lemeshow χ²", "db HL", "P-value HL"],
            "Nilai": [f"{cl['acc']:.4f}", f"{cl['sens']:.4f}", f"{cl['spec']:.4f}", f"{cl['prec']:.4f}", f"{auc:.4f}",
                      f"{chi:.3f}", dfh, fmt_p(ph)]})
        tables["Hosmer-Lemeshow (per kelompok)"] = hl
        kp += [("Akurasi", f"{cl['acc']:.3f}"), ("AUC", f"{auc:.3f}")]
        plots.append(spec_xy("Kurva ROC", "1 − Spesifisitas (FPR)", "Sensitivitas (TPR)",
                             [{"x": fpr, "y": tpr, "mode": "lines", "name": f"ROC (AUC = {auc:.3f})"},
                              {"x": [0, 1], "y": [0, 1], "mode": "lines", "name": "Acak", "dash": "dash"}]))
        plots.append({"kind": "hist2", "title": "Sebaran Peluang Prediksi menurut Kelas Aktual", "xlabel": "Peluang prediksi",
                      "groups": {f"Aktual = {classes[1]}": mu[yv == 1], f"Aktual = {classes[0]}": mu[yv == 0]}})
        if xs_num:
            x0 = xs_num[0]
            order = np.argsort(d[x0].values)
            plots.append(spec_xy(f"Peluang Prediksi vs {x0}", x0, f"P({y} = {classes[1]})",
                                 [{"x": d[x0].values, "y": yv, "mode": "markers", "name": "Data"},
                                  {"x": d[x0].values[order], "y": mu[order], "mode": "lines", "name": "Peluang prediksi"}]))
        notes.append(f"**Uji simultan (LR):** χ² = {lr:.3f}, P = {fmt_p(p_lr)} → model {'signifikan' if p_lr < alpha else 'tidak signifikan'} dibanding model tanpa prediktor.")
        notes.append(f"**Kinerja klasifikasi** (titik potong {cutoff}): akurasi {cl['acc'] * 100:.1f}%, AUC = {auc:.3f} "
                     f"({'sangat baik' if auc >= .9 else 'baik' if auc >= .8 else 'cukup' if auc >= .7 else 'lemah'}).")
        notes.append(f"Kategori peristiwa (Y = 1) adalah **{classes[1]}**" + (f"; pembanding **{classes[0]}**." if classes[0] != "0" else "."))
        notes.append("**Hosmer-Lemeshow:** " + (f"P = {fmt_p(ph)} > α, tidak ada bukti ketidakcocokan model." if ph > alpha
                                                else f"P = {fmt_p(ph)} ≤ α, kecocokan model dipertanyakan."))
        if kind == "logit":
            for nm, b_, pv in zip(names, beta, pvals):
                if nm != "Intersep" and pv < alpha:
                    notes.append(f"**{nm}**: berpengaruh nyata; Odds Ratio = {np.exp(b_):.3f} (odds kejadian "
                                 f"{'naik' if b_ > 0 else 'turun'} {abs(np.exp(b_) - 1) * 100:.1f}% tiap kenaikan 1 satuan).")
    else:
        lo, hi = float(min(mu.min(), yv.min())), float(max(mu.max(), yv.max()))
        plots.append(spec_xy("Aktual vs Prediksi", "Prediksi", "Aktual",
                             [{"x": mu, "y": yv, "mode": "markers", "name": "Data"},
                              {"x": [lo, hi], "y": [lo, hi], "mode": "lines", "name": "y = x", "dash": "dash"}]))
        plots += resid_specs(mu, resid_dev)[:2]
        notes.append(f"**Uji simultan (LR):** χ² = {lr:.3f}, P = {fmt_p(p_lr)} → model {'signifikan' if p_lr < alpha else 'tidak signifikan'}.")
        if family == "poisson":
            od = float((resid_pear ** 2).sum() / (n - p))
            tables["Uji overdispersi"] = pd.DataFrame({"Ukuran": ["Pearson χ²/db", "Kesimpulan"],
                                                         "Nilai": [f"{od:.3f}", "Overdispersi (>1,5): pertimbangkan Binomial Negatif" if od > 1.5 else "Dispersi wajar (≈ 1)"]})
            kp.append(("Pearson χ²/db", f"{od:.2f}"))
            if od > 1.5:
                warn.append(f"Rasio dispersi = {od:.2f} (> 1,5): data overdispersi, galat baku Poisson cenderung terlalu kecil. Gunakan Binomial Negatif.")
        if family == "nb":
            fp = _fit_glm(X.values.astype(float), yv, "poisson", "log")
            lr_a = 2 * (f["ll"] - fp["ll"])
            p_a = 0.5 * float(stats.chi2.sf(max(lr_a, 0), 1))
            tables["Parameter dispersi"] = pd.DataFrame({"Ukuran": ["α (dispersi)", "LR α = 0 (vs Poisson)", "P-value"],
                                                         "Nilai": [f"{f['alpha']:.4f}", f"{lr_a:.3f}", fmt_p(p_a)]})
            kp.append(("α dispersi", f"{f['alpha']:.3f}"))
            notes.append(f"**Dispersi:** α = {f['alpha']:.4f}; uji α = 0: P = {fmt_p(p_a)} → "
                         + ("Binomial Negatif lebih sesuai daripada Poisson." if p_a < alpha else "Poisson sudah memadai."))
        if family == "gamma":
            kp.append(("Dispersi (φ)", f"{f['phi']:.4f}"))
        for nm, b_, pv in zip(names, beta, pvals):
            if nm != "Intersep" and pv < alpha:
                notes.append(f"**{nm}**: berpengaruh nyata; {exp_name} = {np.exp(b_):.3f} (rata-rata Y dikali {np.exp(b_):.3f} tiap kenaikan 1 satuan).")
    if xs_cat:
        notes.append("Kategori referensi: " + "; ".join(f"{c} = {r}" for c, r in refs.items()) + ".")
    tables["Nilai aktual & prediksi"] = pd.DataFrame(
        {"Y aktual": yv, "Prediksi (μ)": mu, "Residual deviance": resid_dev, "Residual Pearson": resid_pear}, index=d.index).round(4)
    return std_result("glm", title, d, kp, tables, plots, notes=notes, warn=warn, extra=extra)


def _num_hessian(f, x, h=1e-4):
    k = len(x)
    H = np.zeros((k, k))
    f0 = f(x)
    for i in range(k):
        for j in range(i, k):
            ei, ej = np.zeros(k), np.zeros(k)
            ei[i], ej[j] = h * max(1, abs(x[i])), h * max(1, abs(x[j]))
            v = (f(x + ei + ej) - f(x + ei - ej) - f(x - ei + ej) + f(x - ei - ej)) / (4 * ei[i] * ej[j])
            H[i, j] = H[j, i] = v
    return H


def _softmax_probs(X, B):
    """B: p x (K-1) untuk kategori 1..K-1 (kategori 0 = referensi)."""
    u = np.column_stack([np.zeros(len(X)), X @ B])
    u -= u.max(axis=1, keepdims=True)
    e = np.exp(u)
    return e / e.sum(axis=1, keepdims=True)


def fit_multinomial(X, y, K):
    n, p = X.shape
    Y = np.eye(K)[y]

    def nll(w):
        P = _softmax_probs(X, w.reshape(p, K - 1))
        return -float(np.log(np.clip(P[np.arange(n), y], 1e-300, None)).sum())

    def grad(w):
        P = _softmax_probs(X, w.reshape(p, K - 1))
        return (-(X.T @ (Y[:, 1:] - P[:, 1:]))).ravel()

    r = optimize.minimize(nll, np.zeros(p * (K - 1)), jac=grad, method="BFGS", options={"gtol": 1e-8, "maxiter": 1000})
    B = r.x.reshape(p, K - 1)
    P = _softmax_probs(X, B)
    info = np.zeros((p * (K - 1), p * (K - 1)))
    for j in range(1, K):
        for k in range(1, K):
            w = P[:, j] * ((j == k) - P[:, k])
            info[(j - 1) * p:j * p, (k - 1) * p:k * p] = (X.T * w) @ X
    # parameter diurutkan per kolom kategori (Fortran) -> sesuaikan urutan blok
    cov = np.linalg.pinv(info)
    se = np.sqrt(np.clip(np.diag(cov), 0, None)).reshape(K - 1, p).T
    return {"B": B, "se": se, "P": P, "ll": -nll(r.x), "conv": bool(r.success or (getattr(r, "jac", None) is not None and float(np.max(np.abs(r.jac))) < 1e-2))}


def run_multinomial(df, y, xs_num, xs_cat, alpha=0.05):
    d0 = df[[y] + list(xs_num) + list(xs_cat)].dropna().copy()
    cats = sorted(pd.unique(d0[y].astype(str)))
    if len(cats) < 3:
        raise ValueError("Regresi logistik multinomial memerlukan respon dengan ≥ 3 kategori (untuk 2 kategori gunakan Logistik Biner).")
    d0["__y"] = pd.Categorical(d0[y].astype(str), categories=cats).codes
    d, X, refs = build_X(d0.drop(columns=[y]).rename(columns={"__y": y}), y, xs_num, xs_cat)
    yv = d[y].values.astype(int)
    K, n = len(cats), len(yv)
    Xm = X.values.astype(float)
    m = fit_multinomial(Xm, yv, K)
    m0 = fit_multinomial(np.ones((n, 1)), yv, K)
    names = list(X.columns)
    rows = []
    for j in range(K - 1):
        for i, nm in enumerate(names):
            b, s = m["B"][i, j], m["se"][i, j]
            pv = 2 * stats.norm.sf(abs(b / s))
            rows.append([f"{cats[j + 1]} vs {cats[0]}", nm, b, s, b / s, fmt_p(pv), sig_mark(pv), np.exp(b)])
    tbl = pd.DataFrame(rows, columns=["Kategori (vs referensi)", "Variabel", "Koefisien (B)", "Std. Error", "z hitung",
                                      "P-value", "Sig.", "exp(B) (RRR)"]).round(4)
    prob = m["P"]
    pred = prob.argmax(axis=1)
    acc = float((pred == yv).mean())
    cm = pd.crosstab(pd.Series([cats[i] for i in yv], name="Aktual"), pd.Series([cats[i] for i in pred], name="Prediksi"))
    ll, ll0 = m["ll"], m0["ll"]
    lr = 2 * (ll - ll0)
    dfm = (Xm.shape[1] - 1) * (K - 1)
    plr = float(stats.chi2.sf(lr, dfm))
    aic = -2 * ll + 2 * Xm.shape[1] * (K - 1)
    kp = [("n", n), ("Kategori", K), ("Log-likelihood", f"{ll:.3f}"), ("LR χ²", f"{lr:.2f}"),
          ("P-value (LR)", fmt_p(plr)), ("McFadden R²", f"{1 - ll / ll0:.4f}"), ("Akurasi", f"{acc:.3f}"), ("AIC", f"{aic:.2f}")]
    notes = [f"**Kategori referensi:** {cats[0]} (koefisien = log-odds kategori lain relatif terhadap referensi).",
             f"**Uji simultan (LR):** χ² = {lr:.2f}, db = {dfm}, P = {fmt_p(plr)} → model {'signifikan' if plr < alpha else 'tidak signifikan'}.",
             f"**Akurasi klasifikasi** = {acc * 100:.1f}%."]
    plots = [spec_heat("Matriks Konfusi (jumlah)", cm.values, list(cm.columns), list(cm.index))]
    if xs_num:
        x0 = xs_num[0]
        order = np.argsort(d[x0].values)
        plots.append(spec_xy(f"Peluang Prediksi tiap Kategori vs {x0}", x0, "Peluang",
                             [{"x": d[x0].values[order], "y": prob[order, j], "mode": "lines", "name": str(cats[j])} for j in range(K)]))
    pr = pd.DataFrame(prob, columns=[f"P({c})" for c in cats], index=d.index)
    pr.insert(0, "Aktual", [cats[i] for i in yv])
    pr.insert(1, "Prediksi", [cats[i] for i in pred])
    warn = [] if m["conv"] else ["Optimasi tidak konvergen penuh; periksa kemungkinan separasi."]
    return std_result("glm", "Regresi Logistik Multinomial", d, kp,
                      {"Koefisien": tbl, "Matriks konfusi": cm.reset_index(), "Peluang prediksi": pr.round(4)}, plots, notes=notes, warn=warn)


def fit_ordinal(X, y, K):
    """Cumulative logit: P(Y<=j) = expit(theta_j - X b). Parameter: b (k), theta1, log-selisih."""
    n, k = X.shape

    def unpack(w):
        b = w[:k]
        th = np.cumsum(np.concatenate([[w[k]], np.exp(w[k + 1:])]))
        return b, th

    def probs(w):
        b, th = unpack(w)
        eta = X @ b if k else np.zeros(n)
        cum = np.column_stack([np.zeros(n)] + [expit(t - eta) for t in th] + [np.ones(n)])
        return np.clip(np.diff(cum, axis=1), 1e-300, None)

    def nll(w):
        return -float(np.log(probs(w)[np.arange(n), y]).sum())

    w0 = np.concatenate([np.zeros(k), [stats.norm.ppf((y <= 0).mean() + 1e-3)], np.zeros(K - 2)])
    w0[k] = np.log(max((y <= 0).mean(), 1e-3) / max(1 - (y <= 0).mean(), 1e-3))
    r = optimize.minimize(nll, w0, method="BFGS", options={"gtol": 1e-7, "maxiter": 2000})
    w = r.x
    H = _num_hessian(nll, w)
    cov = np.linalg.pinv(H)
    b, th = unpack(w)
    # galat baku koefisien b langsung; ambang lewat delta method numerik
    se_b = np.sqrt(np.clip(np.diag(cov)[:k], 0, None))
    J = np.zeros((K - 1, len(w)))
    for i in range(len(w)):
        e = np.zeros(len(w))
        e[i] = 1e-6
        J[:, i] = (unpack(w + e)[1] - unpack(w - e)[1]) / 2e-6
    se_th = np.sqrt(np.clip(np.diag(J @ cov @ J.T), 0, None))
    return {"b": b, "se_b": se_b, "th": th, "se_th": se_th, "P": probs(w), "ll": -nll(w), "conv": bool(r.success or (getattr(r, "jac", None) is not None and float(np.max(np.abs(r.jac))) < 1e-2))}


def run_ordinal(df, y, xs_num, alpha=0.05):
    d = df[[y] + list(xs_num)].dropna().copy()
    for c in xs_num:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna()
    yn = pd.to_numeric(d[y], errors="coerce")
    is_text = yn.isna().any()
    cats = sorted(pd.unique(d[y].astype(str))) if is_text else sorted(pd.unique(yn))
    K = len(cats)
    if K < 3:
        raise ValueError("Regresi logistik ordinal memerlukan respon dengan ≥ 3 kategori berurutan.")
    yc = np.array(pd.Categorical(d[y].astype(str) if is_text else yn, categories=cats, ordered=True).codes)
    X = d[list(xs_num)].values.astype(float)
    n, k = X.shape
    m = fit_ordinal(X, yc, K)
    m0 = fit_ordinal(np.zeros((n, 0)), yc, K)
    b, se = m["b"], m["se_b"]
    tbl = coef_table(list(xs_num), b, se, "z", None, alpha, {"Odds Ratio": np.exp(b)})
    thr_tbl = pd.DataFrame({"Ambang": [f"{cats[i]} | {cats[i + 1]}" for i in range(K - 1)], "Nilai": m["th"],
                            "Std. Error": m["se_th"]}).round(4)
    ll, ll0 = m["ll"], m0["ll"]
    lr = 2 * (ll - ll0)
    plr = float(stats.chi2.sf(lr, k))
    pred = m["P"].argmax(axis=1)
    acc = float((pred == yc).mean())
    cm = pd.crosstab(pd.Series([str(cats[i]) for i in yc], name="Aktual"), pd.Series([str(cats[i]) for i in pred], name="Prediksi"))
    kp = [("n", n), ("Kategori", K), ("Log-likelihood", f"{ll:.3f}"), ("LR χ²", f"{lr:.2f}"),
          ("P-value (LR)", fmt_p(plr)), ("McFadden R²", f"{1 - ll / ll0:.4f}"), ("Akurasi", f"{acc:.3f}"),
          ("AIC", f"{-2 * ll + 2 * (k + K - 1):.2f}")]
    notes = [f"**Model odds proporsional (cumulative logit):** urutan kategori {' < '.join(map(str, cats))}.",
             f"**Uji simultan (LR):** χ² = {lr:.2f}, P = {fmt_p(plr)} → model {'signifikan' if plr < alpha else 'tidak signifikan'}."]
    for nm, b_, s_ in zip(xs_num, b, se):
        if 2 * stats.norm.sf(abs(b_ / s_)) < alpha:
            notes.append(f"**{nm}**: berpengaruh nyata; Odds Ratio = {np.exp(b_):.3f} (peluang berada di kategori lebih tinggi "
                         f"{'meningkat' if b_ > 0 else 'menurun'}).")
    notes.append("Asumsi odds proporsional tidak diuji otomatis; periksa secara substantif.")
    plots = [spec_heat("Matriks Konfusi (jumlah)", cm.values, list(cm.columns), list(cm.index))]
    if k:
        order = np.argsort(X[:, 0])
        plots.append(spec_xy(f"Peluang Prediksi tiap Kategori vs {xs_num[0]}", xs_num[0], "Peluang",
                             [{"x": X[order, 0], "y": m["P"][order, j], "mode": "lines", "name": str(cats[j])} for j in range(K)]))
    return std_result("glm", "Regresi Logistik Ordinal", d, kp,
                      {"Koefisien": tbl, "Ambang (threshold)": thr_tbl, "Matriks konfusi": cm.reset_index()}, plots, notes=notes,
                      warn=[] if m["conv"] else ["Optimasi tidak konvergen penuh."])
