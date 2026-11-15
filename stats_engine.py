"""
stats_engine.py
Mesin perhitungan statistika untuk dashboard StatCalc.
Berisi: Regresi Linear (sederhana & berganda), RAL, RAK, uji lanjut, uji asumsi.
Tidak bergantung pada Streamlit sehingga mudah diuji.
"""
import string

import numpy as np
import pandas as pd
from scipy import stats


# ----------------------------------------------------------------------------
# Utilitas format
# ----------------------------------------------------------------------------
def fmt_p(p):
    if p is None or pd.isna(p):
        return "-"
    return "<0.0001" if p < 0.0001 else f"{p:.4f}"


def sig_mark(p):
    """Notasi kebermaknaan khas Indonesia: ** sangat nyata, * nyata, tn tidak nyata."""
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "tn"


def f4(v):
    return f"{float(v):.4f}"


def numeric_cols(df):
    """Kolom yang (hampir seluruhnya) bisa dibaca sebagai angka."""
    out = []
    for c in df.columns:
        s = df[c].dropna()
        if len(s) and pd.to_numeric(s, errors="coerce").notna().mean() >= 0.9:
            out.append(c)
    return out


# ----------------------------------------------------------------------------
# Data contoh
# ----------------------------------------------------------------------------
def sample_data(kind):
    rng = np.random.default_rng(42)
    if kind == "reg":
        n = 40
        luas = rng.uniform(1, 5, n).round(2)
        pupuk = rng.uniform(50, 200, n).round(1)
        hujan = rng.uniform(100, 300, n).round(1)
        hasil = (2 + 1.8 * luas + 0.03 * pupuk + 0.01 * hujan + rng.normal(0, 0.8, n)).round(2)
        return pd.DataFrame({
            "Luas_Lahan_ha": luas,
            "Pupuk_kg": pupuk,
            "Curah_Hujan_mm": hujan,
            "Hasil_Panen_ton": hasil,
        })
    if kind == "ral":
        eff = {"P0": 20, "P1": 24, "P2": 29, "P3": 26}
        rows = []
        for lv, mu in eff.items():
            for u in range(1, 6):
                rows.append([lv, u, round(mu + rng.normal(0, 1.8), 1)])
        return pd.DataFrame(rows, columns=["Perlakuan", "Ulangan", "Hasil"])
    # RAK
    teff = {"V1": 0, "V2": 3, "V3": 6, "V4": 4}
    beff = {"K1": 0, "K2": 1.5, "K3": -1, "K4": 2}
    rows = []
    for b, be in beff.items():
        for t, te in teff.items():
            rows.append([t, b, round(40 + te + be + rng.normal(0, 1), 1)])
    return pd.DataFrame(rows, columns=["Perlakuan", "Kelompok", "Hasil"])


# ----------------------------------------------------------------------------
# Tabel ANOVA
# ----------------------------------------------------------------------------
def build_anova(factors, jkg, dbg, jkt, dbt):
    """factors: list of (nama, jk, db). Mengembalikan (DataFrame tampilan, list hasil uji F)."""
    ktg = jkg / dbg
    recs, tests = [], []
    for name, jk, db in factors:
        kt = jk / db
        F = kt / ktg
        p = stats.f.sf(F, db, dbg)
        recs.append([name, db, f4(jk), f4(kt), f4(F), fmt_p(p), sig_mark(p)])
        tests.append({"name": name, "F": F, "p": p, "kt": kt, "db": db})
    recs.append(["Galat", dbg, f4(jkg), f4(ktg), "", "", ""])
    recs.append(["Total", dbt, f4(jkt), "", "", "", ""])
    df = pd.DataFrame(recs, columns=["Sumber Keragaman", "db", "JK", "KT", "F hitung", "P-value", "Sig."])
    return df, tests


def _clean(df, cols, resp, factor_cols):
    d = df[cols].copy()
    d[resp] = pd.to_numeric(d[resp], errors="coerce")
    d = d.dropna()
    for c in factor_cols:
        d[c] = d[c].astype(str).str.strip()
    return d


# ----------------------------------------------------------------------------
# RAL
# ----------------------------------------------------------------------------
def run_ral(df, resp, trt):
    d = _clean(df, [resp, trt], resp, [trt])
    levels = list(pd.unique(d[trt]))
    t, N = len(levels), len(d)
    if t < 2:
        raise ValueError("RAL membutuhkan minimal 2 perlakuan.")
    if N - t < 1:
        raise ValueError("RAL membutuhkan ulangan (minimal satu perlakuan memiliki lebih dari 1 pengamatan).")

    g = d.groupby(trt, sort=False)[resp]
    means = g.mean().reindex(levels)
    ns = g.count().reindex(levels)
    sums = g.sum().reindex(levels)
    y = d[resp].values.astype(float)

    fk = y.sum() ** 2 / N
    jkt = (y ** 2).sum() - fk
    jkp = (sums ** 2 / ns).sum() - fk
    jkg = max(jkt - jkp, 0.0)
    dbp, dbg, dbt = t - 1, N - t, N - 1
    if jkg <= 0:
        raise ValueError("Jumlah kuadrat galat = 0 (data identik dalam tiap perlakuan); ANOVA tidak dapat dihitung.")

    anova, tests = build_anova([("Perlakuan", jkp, dbp)], jkg, dbg, jkt, dbt)
    ktg = jkg / dbg
    grand = y.mean()
    d = d.copy()
    d["Fitted"] = d[trt].map(means)
    d["Galat"] = d[resp] - d["Fitted"]

    return {
        "kind": "ral", "resp": resp, "trt": trt, "blk": None, "data": d,
        "levels": levels, "means": means, "ns": ns, "sd": g.std().reindex(levels),
        "min": g.min().reindex(levels), "max": g.max().reindex(levels),
        "anova": anova, "tests": tests, "ktg": ktg, "dbg": dbg,
        "grand": grand, "kk": np.sqrt(ktg) / grand * 100 if grand else np.nan,
        "t": t, "N": N, "r": N / t, "extra": {},
    }


# ----------------------------------------------------------------------------
# RAK
# ----------------------------------------------------------------------------
def run_rak(df, resp, trt, blk):
    d = _clean(df, [resp, trt, blk], resp, [trt, blk])
    levels = list(pd.unique(d[trt]))
    blocks = list(pd.unique(d[blk]))
    t, b, N = len(levels), len(blocks), len(d)
    if t < 2 or b < 2:
        raise ValueError("RAK membutuhkan minimal 2 perlakuan dan 2 kelompok.")

    cnt = d.pivot_table(index=blk, columns=trt, values=resp, aggfunc="count").reindex(index=blocks, columns=levels)
    if cnt.isna().any().any() or (cnt != 1).any().any():
        raise ValueError(
            "RAK standar memerlukan data lengkap: setiap kombinasi Perlakuan × Kelompok harus memiliki "
            "tepat 1 pengamatan. Periksa data yang kosong atau ganda."
        )
    Y = d.pivot_table(index=blk, columns=trt, values=resp, aggfunc="sum").reindex(index=blocks, columns=levels)

    G = Y.values.sum()
    fk = G ** 2 / N
    jkt = (Y.values ** 2).sum() - fk
    Ti, Bj = Y.sum(axis=0), Y.sum(axis=1)
    jkp = (Ti ** 2).sum() / b - fk
    jkk = (Bj ** 2).sum() / t - fk
    jkg = max(jkt - jkp - jkk, 0.0)
    dbp, dbk, dbg, dbt = t - 1, b - 1, (t - 1) * (b - 1), N - 1
    if jkg <= 0:
        raise ValueError("Jumlah kuadrat galat = 0; ANOVA tidak dapat dihitung.")

    anova, tests = build_anova([("Perlakuan", jkp, dbp), ("Kelompok", jkk, dbk)], jkg, dbg, jkt, dbt)
    ktg = jkg / dbg
    ktk = jkk / dbk
    grand = G / N

    means = (Ti / b).reindex(levels)
    bmeans = (Bj / t).reindex(blocks)
    d = d.copy()
    d["Fitted"] = d[trt].map(means) + d[blk].map(bmeans) - grand
    d["Galat"] = d[resp] - d["Fitted"]

    g = d.groupby(trt, sort=False)[resp]
    er = ((b - 1) * ktk + b * (t - 1) * ktg) / ((t * b - 1) * ktg)

    return {
        "kind": "rak", "resp": resp, "trt": trt, "blk": blk, "data": d,
        "levels": levels, "blocks": blocks, "means": means,
        "ns": pd.Series(b, index=levels), "sd": g.std().reindex(levels),
        "min": g.min().reindex(levels), "max": g.max().reindex(levels),
        "anova": anova, "tests": tests, "ktg": ktg, "dbg": dbg,
        "grand": grand, "kk": np.sqrt(ktg) / grand * 100 if grand else np.nan,
        "t": t, "N": N, "r": b, "b": b, "matrix": Y, "extra": {"ER": er},
    }


# ----------------------------------------------------------------------------
# Uji lanjut: BNT (LSD), BNJ (Tukey), DMRT (Duncan)
# ----------------------------------------------------------------------------
POSTHOC_METHODS = ["DMRT (Duncan)", "BNJ (Tukey HSD)", "BNT (LSD)"]


def _compact_letters(order, ns_fn):
    m = len(order)
    groups = []
    for i in range(m):
        e = i
        while e + 1 < m and all(ns_fn(order[k], order[e + 1]) for k in range(i, e + 1)):
            e += 1
        groups.append((i, e))
    uniq = []
    for g in groups:
        contained = any(h != g and h[0] <= g[0] and g[1] <= h[1] for h in groups)
        if not contained and g not in uniq:
            uniq.append(g)
    alphabet = string.ascii_lowercase
    letters = {o: "" for o in order}
    for idx, (s, e) in enumerate(uniq):
        ch = alphabet[idx % 26] * (idx // 26 + 1)
        for k in range(s, e + 1):
            letters[order[k]] += ch
    return letters


def posthoc(means, ns, ktg, dbg, alpha, method):
    order = means.sort_values(ascending=False).index.tolist()
    rank = {lv: i for i, lv in enumerate(order)}
    k = len(order)

    def crit(a, b):
        ni, nj = ns[a], ns[b]
        if method.startswith("BNT"):
            return stats.t.ppf(1 - alpha / 2, dbg) * np.sqrt(ktg * (1 / ni + 1 / nj))
        se = np.sqrt(ktg / 2 * (1 / ni + 1 / nj))
        if method.startswith("BNJ"):
            q = stats.studentized_range.ppf(1 - alpha, k, dbg)
        else:  # Duncan
            p_ = abs(rank[a] - rank[b]) + 1
            q = stats.studentized_range.ppf((1 - alpha) ** (p_ - 1), p_, dbg)
        return q * se

    rows, nonsig = [], {}
    for i in range(k):
        for j in range(i + 1, k):
            a, b = order[i], order[j]
            diff = means[a] - means[b]
            cr = crit(a, b)
            sig = diff > cr
            nonsig[(a, b)] = nonsig[(b, a)] = not sig
            rows.append([f"{a} vs {b}", round(diff, 4), round(cr, 4), "Berbeda nyata" if sig else "Tidak berbeda nyata"])
    pair_df = pd.DataFrame(rows, columns=["Perbandingan", "Selisih rata-rata", "Nilai kritis", "Kesimpulan"])
    letters = _compact_letters(order, lambda a, b: nonsig[(a, b)])
    return letters, pair_df


# ----------------------------------------------------------------------------
# Uji asumsi
# ----------------------------------------------------------------------------
def anova_assumptions(res, alpha):
    d, resp, trt = res["data"], res["resp"], res["trt"]
    resid = d["Galat"].values
    rows = []
    if 3 <= len(resid) <= 5000:
        w, p = stats.shapiro(resid)
        rows.append(["Shapiro-Wilk", "Galat menyebar normal", f4(w), fmt_p(p),
                     "Terpenuhi" if p > alpha else "Tidak terpenuhi"])
    groups = [g[resp].values for _, g in d.groupby(trt, sort=False)]
    try:
        s, p = stats.levene(*groups, center="median")
        rows.append(["Levene (Brown-Forsythe)", "Ragam antar perlakuan homogen", f4(s), fmt_p(p),
                     "Terpenuhi" if p > alpha else "Tidak terpenuhi"])
    except Exception:
        pass
    try:
        if all(len(g) >= 2 for g in groups):
            s, p = stats.bartlett(*groups)
            rows.append(["Bartlett", "Ragam antar perlakuan homogen", f4(s), fmt_p(p),
                         "Terpenuhi" if p > alpha else "Tidak terpenuhi"])
    except Exception:
        pass
    return pd.DataFrame(rows, columns=["Uji", "H0", "Statistik", "P-value", "Kesimpulan"])


# ----------------------------------------------------------------------------
# Regresi linear (OLS) – statsmodels dipanggil di sini
# ----------------------------------------------------------------------------
def run_regression(df, y, xs, intercept=True, alpha=0.05):
    import statsmodels.api as sm
    from statsmodels.stats.diagnostic import het_breuschpagan
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from statsmodels.stats.stattools import durbin_watson

    d0 = df[[y] + xs].apply(pd.to_numeric, errors="coerce")
    d = d0.dropna()
    n, k = len(d), len(xs)
    if n < k + 2:
        raise ValueError(f"Data terlalu sedikit: n = {n}, dibutuhkan minimal {k + 2} pengamatan lengkap.")

    X = sm.add_constant(d[xs], has_constant="add") if intercept else d[xs]
    model = sm.OLS(d[y], X).fit()
    resid, fitted = model.resid, model.fittedvalues

    # --- koefisien
    ci = model.conf_int(alpha=alpha)
    names = list(model.params.index)
    beta_std = [np.nan if nm == "const" else model.params[nm] * d[nm].std() / d[y].std() for nm in names]
    cl = int(round((1 - alpha) * 100))
    coef = pd.DataFrame({
        "Variabel": ["Intersep" if nm == "const" else nm for nm in names],
        "Koefisien (B)": model.params.values.round(4),
        "Std. Error": model.bse.values.round(4),
        "t hitung": model.tvalues.values.round(4),
        "P-value": [fmt_p(p) for p in model.pvalues.values],
        "Sig.": [sig_mark(p) for p in model.pvalues.values],
        f"Batas bawah CI {cl}%": ci[0].values.round(4),
        f"Batas atas CI {cl}%": ci[1].values.round(4),
        "Beta terstandar": np.round(beta_std, 4),
    })

    # --- ANOVA regresi
    ssr, sse = model.ess, model.ssr
    dfr, dfe = model.df_model, model.df_resid
    anova = pd.DataFrame([
        ["Regresi", int(dfr), f4(ssr), f4(ssr / dfr), f4(model.fvalue), fmt_p(model.f_pvalue), sig_mark(model.f_pvalue)],
        ["Sisa (Galat)", int(dfe), f4(sse), f4(sse / dfe), "", "", ""],
        ["Total", int(dfr + dfe), f4(ssr + sse), "", "", "", ""],
    ], columns=["Sumber Keragaman", "db", "JK", "KT", "F hitung", "P-value", "Sig."])

    # --- persamaan
    eq = "Ŷ = "
    parts = []
    for nm in names:
        b = model.params[nm]
        if nm == "const":
            parts.append(f"{b:.4f}")
        else:
            parts.append(f"{'+' if b >= 0 else '−'} {abs(b):.4f}·{nm}" if parts else f"{b:.4f}·{nm}")
    eq += " ".join(parts)

    # --- uji asumsi
    rows = []
    if 3 <= n <= 5000:
        w, p = stats.shapiro(resid)
        rows.append(["Shapiro-Wilk", "Galat menyebar normal", f4(w), fmt_p(p),
                     "Terpenuhi" if p > alpha else "Tidak terpenuhi"])
    try:
        exog_bp = model.model.exog if intercept else sm.add_constant(d[xs], has_constant="add").values
        lm, lm_p, _, _ = het_breuschpagan(resid, exog_bp)
        rows.append(["Breusch-Pagan", "Ragam galat homogen (homoskedastis)", f4(lm), fmt_p(lm_p),
                     "Terpenuhi" if lm_p > alpha else "Tidak terpenuhi"])
    except Exception:
        pass
    dw = durbin_watson(resid)
    rows.append(["Durbin-Watson", "Tidak ada autokorelasi galat", f4(dw), "-",
                 "Terpenuhi (1,5–2,5)" if 1.5 <= dw <= 2.5 else "Perlu diperiksa (di luar 1,5–2,5)"])
    assump = pd.DataFrame(rows, columns=["Uji", "H0 / Asumsi", "Statistik", "P-value", "Kesimpulan"])

    vif = None
    if k >= 2:
        Xv = sm.add_constant(d[xs], has_constant="add")
        vals = []
        for i, nm in enumerate(xs, start=1):
            try:
                vals.append(variance_inflation_factor(Xv.values, i))
            except Exception:
                vals.append(np.nan)
        vif = pd.DataFrame({
            "Variabel": xs,
            "VIF": np.round(vals, 3),
            "Keterangan": ["Multikolinearitas tinggi (>10)" if v > 10 else
                           "Perlu diperhatikan (5–10)" if v > 5 else "Aman (<5)" for v in vals],
        })

    cooks = model.get_influence().cooks_distance[0]
    pred_tbl = pd.DataFrame({
        "Y aktual": d[y].values, "Y prediksi": fitted.values, "Galat (residual)": resid.values,
        "Galat terstandar": (resid / np.sqrt(model.mse_resid)).values, "Cook's D": cooks,
    }, index=d.index).round(4)

    return {
        "model": model, "data": d, "y": y, "xs": xs, "intercept": intercept, "n": n, "k": k,
        "n_dropped": len(d0) - n, "coef": coef, "anova": anova, "equation": eq,
        "assump": assump, "vif": vif, "pred_table": pred_tbl, "cooks": cooks,
        "rmse": float(np.sqrt(model.mse_resid)),
    }
