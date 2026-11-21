"""
reg_models3.py – regresi untuk data terstruktur: Panel (Common/Fixed/Random Effect), Deret waktu (ARIMAX),
Spasial (SAR, SEM, GWR), Mixed Effect, Cox (survival) dan Tobit. Murni numpy + scipy.
"""
import numpy as np
import pandas as pd
from scipy import stats, optimize
from scipy.special import log_ndtr

from stats_engine import f4, fmt_p, sig_mark
from reg_core import (ols, coef_table, numeric_frame, build_X, std_result, spec_xy, spec_bar, spec_heat,
                      resid_specs, _num_hessian)


def spec_map(title, x, y, color, xl="Bujur (Lon)", yl="Lintang (Lat)", clabel=""):
    return {"kind": "map", "title": title, "x": np.asarray(x), "y": np.asarray(y), "color": np.asarray(color),
            "xlabel": xl, "ylabel": yl, "clabel": clabel}


# ============================================================================
# Regresi data panel
# ============================================================================
def run_panel(df, y, xs, entity, time=None, alpha=0.05):
    cols = [y] + list(xs) + [entity] + ([time] if time else [])
    d = df[cols].copy()
    for c in [y] + list(xs):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna()
    d[entity] = d[entity].astype(str)
    if time:
        d = d.sort_values([entity, time])
    d = d.reset_index(drop=True)
    N, n, k = d[entity].nunique(), len(d), len(xs)
    Ti = d.groupby(entity).size()
    if N < 3:
        raise ValueError("Data panel memerlukan minimal 3 unit (entitas).")
    if Ti.max() < 2:
        raise ValueError("Setiap entitas harus memiliki minimal 2 periode untuk data panel.")
    if n - N - k < 1:
        raise ValueError("Data terlalu sedikit untuk model fixed effect.")
    g = d[entity].values
    X = d[list(xs)].values.astype(float)
    yv = d[y].values.astype(float)
    balanced = bool(Ti.nunique() == 1)

    def demean(M, w=None):
        M = np.asarray(M, float)
        out = np.empty_like(M)
        for e in Ti.index:
            m_ = g == e
            mu = M[m_].mean(0)
            out[m_] = M[m_] - ((w[e] if w else 1.0) * mu)
        return out

    # --- Pooled (Common Effect)
    Xc = np.column_stack([np.ones(n), X])
    op = ols(Xc, yv)
    # --- Fixed Effect (within)
    Xw, yw = demean(X), demean(yv.reshape(-1, 1)).ravel()
    of = ols(Xw, yw)
    dfe_fe = n - N - k
    s2e = of["rss"] / dfe_fe
    cov_fe = s2e * np.linalg.pinv(Xw.T @ Xw)
    b_fe = of["beta"]
    se_fe = np.sqrt(np.diag(cov_fe))
    # efek individu (intersep tetap)
    ybar_g = pd.Series(yv).groupby(g).mean()
    xbar_g = pd.DataFrame(X).groupby(g).mean()
    alpha_i = ybar_g.values - xbar_g.values @ b_fe
    fe_tbl = pd.DataFrame({entity: ybar_g.index, "Efek tetap (intersep)": alpha_i, "T": Ti.reindex(ybar_g.index).values}).round(4)
    # --- Random Effect (Swamy-Arora)
    ob = ols(np.column_stack([np.ones(N), xbar_g.values]), ybar_g.values)
    s2b = ob["rss"] / max(N - k - 1, 1)
    Tbar = N / float((1.0 / Ti).sum())
    s2u = max(s2b - s2e / Tbar, 0.0)
    theta = {e: 1 - np.sqrt(s2e / (s2e + Ti[e] * s2u)) for e in Ti.index}
    yr, Xr = demean(yv.reshape(-1, 1), theta).ravel(), demean(X, theta)
    Z1 = np.array([1 - theta[e] for e in g])
    orr = ols(np.column_stack([Z1, Xr]), yr)
    b_re = orr["beta"]
    cov_re = orr["cov"]
    se_re = np.sqrt(np.diag(cov_re))
    names = ["Intersep"] + list(xs)

    def tab(b, se, dfe, dist="t"):
        return coef_table(names if len(b) == k + 1 else list(xs), b, se, dist, dfe, alpha)

    t_pool = tab(op["beta"], op["se"], op["dfe"])
    t_fe = tab(b_fe, se_fe, dfe_fe)
    t_re = tab(b_re, se_re, n - k - 1, "z")
    # --- Uji pemilihan model
    ssr_p, ssr_f = op["rss"], of["rss"]
    F_fe = ((ssr_p - ssr_f) / (N - 1)) / (ssr_f / dfe_fe)
    p_F = float(stats.f.sf(F_fe, N - 1, dfe_fe))
    e = op["res"]
    S = pd.Series(e).groupby(g).sum().values
    s2_ = (e ** 2).sum() / n
    LM = ((S ** 2).sum() - (e ** 2).sum()) ** 2 / (2 * s2_ ** 2 * float((Ti * (Ti - 1)).sum()))
    p_LM = float(stats.chi2.sf(LM, 1))
    db = b_fe - b_re[1:]
    Vd = cov_fe - cov_re[1:, 1:]
    H = float(db @ np.linalg.pinv(Vd) @ db)
    if H < 0 or not np.isfinite(H):
        H = float(abs(H))
    p_H = float(stats.chi2.sf(H, k))
    tests = pd.DataFrame([
        ["Uji F (Chow): Fixed vs Common", f"F = {F_fe:.3f} (db {N - 1}, {dfe_fe})", fmt_p(p_F),
         "Fixed Effect lebih baik daripada Common" if p_F < alpha else "Common Effect memadai"],
        ["Breusch-Pagan LM: Random vs Common", f"χ² = {LM:.3f} (db 1)", fmt_p(p_LM),
         "Random Effect lebih baik daripada Common" if p_LM < alpha else "Common Effect memadai"],
        ["Hausman: Fixed vs Random", f"χ² = {H:.3f} (db {k})", fmt_p(p_H),
         "Fixed Effect dipilih (efek individu berkorelasi dengan X)" if p_H < alpha else "Random Effect dipilih (konsisten & efisien)"]],
        columns=["Uji", "Statistik", "P-value", "Kesimpulan"])
    if p_F >= alpha and p_LM >= alpha:
        best = "Common Effect"
    elif p_H < alpha:
        best = "Fixed Effect"
    else:
        best = "Random Effect" if p_LM < alpha else "Fixed Effect"
    sst_w = float(((yw) ** 2).sum())
    r2_within = 1 - ssr_f / sst_w
    r2_pool = 1 - ssr_p / float(((yv - yv.mean()) ** 2).sum())
    cmp_ = pd.DataFrame({"Variabel": list(xs), "Common Effect": op["beta"][1:], "Fixed Effect": b_fe, "Random Effect": b_re[1:]}).round(4)
    plots = [spec_bar("Perbandingan Koefisien antar Model", "Variabel", "Koefisien", list(xs), list(b_fe)),
             spec_bar("Efek Tetap Individu (Fixed Effect)", entity, "Intersep individu", list(ybar_g.index), alpha_i)]
    fit_fe = np.array([alpha_i[list(ybar_g.index).index(v)] for v in g]) + X @ b_fe
    plots += resid_specs(fit_fe, yv - fit_fe)[:2]
    sig_names = [x for x, pv in zip(xs, 2 * stats.t.sf(np.abs(b_fe / se_fe), dfe_fe)) if pv < alpha]
    notes = [f"**Struktur data:** {N} entitas, {n} pengamatan, " + ("panel seimbang" if balanced else f"panel tidak seimbang (T = {Ti.min()}–{Ti.max()})") + ".",
             f"**Model terbaik menurut rangkaian uji: {best}.**",
             f"**Uji Chow:** P = {fmt_p(p_F)}; **Breusch-Pagan LM:** P = {fmt_p(p_LM)}; **Hausman:** P = {fmt_p(p_H)}.",
             f"**Fixed Effect:** R² within = {r2_within:.4f}; variabel nyata: {', '.join(sig_names) or 'tidak ada'}.",
             f"**Komponen ragam (RE):** σ²ᵤ (antar-entitas) = {s2u:.4f}, σ²ₑ = {s2e:.4f}; ICC = {s2u / (s2u + s2e):.3f}.",
             "Galat baku bersifat klasik (bukan robust/cluster); pada data dengan heteroskedastisitas atau autokorelasi, interpretasikan dengan hati-hati."]
    return std_result("panel", "Regresi Data Panel", d,
                      [("Entitas (N)", N), ("Pengamatan", n), ("R² within (FE)", f"{r2_within:.4f}"), ("R² Common", f"{r2_pool:.4f}"),
                       ("P Hausman", fmt_p(p_H)), ("Model terbaik", best)],
                      {"Uji pemilihan model": tests, "Common Effect": t_pool, "Fixed Effect": t_fe, "Random Effect": t_re,
                       "Perbandingan koefisien": cmp_, "Efek individu (FE)": fe_tbl},
                      plots, notes=notes, extra={"fitted": fit_fe, "resid": yv - fit_fe, "best": best})


# ============================================================================
# Deret waktu: regresi dengan galat ARMA (ARIMAX)
# ============================================================================
def _diff(a, d):
    for _ in range(d):
        a = np.diff(a, axis=0)
    return a


def _arma_resid(e, phi, theta):
    n = len(e)
    p, q = len(phi), len(theta)
    a = np.zeros(n)
    m = max(p, q)
    for t in range(m, n):
        ar = sum(phi[i] * e[t - 1 - i] for i in range(p))
        ma = sum(theta[j] * a[t - 1 - j] for j in range(q))
        a[t] = e[t] - ar - ma
    return a[m:]


def acf(x, nlag):
    x = np.asarray(x) - np.mean(x)
    den = (x ** 2).sum()
    return np.array([(x[k:] * x[:len(x) - k]).sum() / den for k in range(nlag + 1)])


def ljung_box(r, lags, ddof=0):
    n = len(r)
    ac = acf(r, lags)
    Q = n * (n + 2) * sum(ac[k] ** 2 / (n - k) for k in range(1, lags + 1))
    return float(Q), float(stats.chi2.sf(Q, max(lags - ddof, 1)))


def run_arimax(df, y, xs, p=1, d=0, q=0, time=None, alpha=0.05):
    cols = [y] + list(xs) + ([time] if time else [])
    dd = df[cols].copy()
    for c in [y] + list(xs):
        dd[c] = pd.to_numeric(dd[c], errors="coerce")
    dd = dd.dropna()
    if time:
        dd = dd.sort_values(time)
    dd = dd.reset_index(drop=True)
    n0 = len(dd)
    if n0 < 25:
        raise ValueError("Model deret waktu memerlukan minimal 25 pengamatan berurutan.")
    if p + q > 4 or d > 2:
        raise ValueError("Batas: p + q ≤ 4 dan d ≤ 2.")
    yv = dd[y].values.astype(float)
    Xv = dd[list(xs)].values.astype(float) if xs else np.zeros((n0, 0))
    w = _diff(yv, d)
    Xw = _diff(Xv, d) if len(xs) else np.zeros((len(w), 0))
    const = d == 0
    Xd = np.column_stack([np.ones(len(w)), Xw]) if const else Xw
    kb = Xd.shape[1]
    names = (["Intersep"] if const else []) + list(xs)
    ob = ols(Xd, w) if kb else None
    b0 = ob["beta"] if kb else np.zeros(0)

    def css(par):
        b, phi, th = par[:kb], par[kb:kb + p], par[kb + p:kb + p + q]
        a = _arma_resid(w - (Xd @ b if kb else 0.0), phi, th)
        return float((a ** 2).sum())

    x0 = np.concatenate([b0, np.zeros(p), np.zeros(q)])
    r = optimize.minimize(css, x0, method="BFGS", options={"gtol": 1e-8, "maxiter": 1000})
    par = r.x
    nobs = len(w) - max(p, q)
    s2 = r.fun / nobs
    H = _num_hessian(css, par) / (2 * s2)
    cov = np.linalg.pinv(H)
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    pn = names + [f"AR({i + 1})" for i in range(p)] + [f"MA({j + 1})" for j in range(q)]
    tbl = coef_table(pn, par, se, "z", None, alpha)
    phi, th = par[kb:kb + p], par[kb + p:]
    stat_ok = (not p) or bool(np.all(np.abs(np.roots(np.concatenate([-phi[::-1], [1.0]]))) > 1))
    inv_ok = (not q) or bool(np.all(np.abs(np.roots(np.concatenate([th[::-1], [1.0]]))) > 1))
    a = _arma_resid(w - (Xd @ par[:kb] if kb else 0.0), phi, th)
    kpar = kb + p + q + 1
    aic = nobs * np.log(r.fun / nobs) + 2 * kpar
    bic = nobs * np.log(r.fun / nobs) + np.log(nobs) * kpar
    lb_lags = min(10, nobs // 4)
    Q, pQ = ljung_box(a, lb_lags, ddof=p + q)
    dwv = float((np.diff(a) ** 2).sum() / (a ** 2).sum())
    fitted_w = (Xd @ par[:kb] if kb else np.zeros(len(w)))
    # perbandingan dengan OLS
    cmp_rows = []
    if kb:
        e_ols = w - Xd @ b0
        Qo, pQo = ljung_box(e_ols, lb_lags)
        dwo = float((np.diff(e_ols) ** 2).sum() / (e_ols ** 2).sum())
        cmp_rows = [["OLS (abaikan autokorelasi)", len(w) * np.log((e_ols ** 2).mean()) + 2 * (kb + 1), dwo, fmt_p(pQo)],
                    [f"ARIMAX({p},{d},{q})", aic, dwv, fmt_p(pQ)]]
    cmp_ = pd.DataFrame(cmp_rows, columns=["Model", "AIC", "Durbin-Watson", "P Ljung-Box"]).round(4) if cmp_rows else None
    lagn = min(20, len(a) // 3)
    ac_a = acf(a, lagn)
    bound = 1.96 / np.sqrt(len(a))
    t_axis = np.arange(len(a))
    plots = [spec_xy("Galat Model (a_t) menurut Waktu", "Waktu", "Galat", [{"x": t_axis, "y": a, "mode": "lines+markers", "name": "a_t"}], hlines=[0.0]),
             spec_bar("ACF Galat Model", "Lag", "Autokorelasi", list(range(1, lagn + 1)), ac_a[1:])]
    plots[1]["hlines"] = [bound, -bound]
    if d == 0 or kb == 0:
        fit_series = (fitted_w if kb else np.zeros(len(w)))
        # prediksi satu langkah ke depan: x_b + AR(e_{t-1}) + MA(a_{t-1})
        e_full = w - fitted_w
        m_ = max(p, q)
        one = np.full(len(w), np.nan)
        for t in range(m_, len(w)):
            one[t] = fitted_w[t] + sum(phi[i] * e_full[t - 1 - i] for i in range(p)) + sum(th[j] * (a[t - 1 - j - m_] if t - 1 - j - m_ >= 0 else 0.0) for j in range(q))
        plots.insert(0, spec_xy("Aktual vs Prediksi Satu Langkah", "Waktu", y,
                                [{"x": np.arange(len(w)), "y": w, "mode": "lines", "name": "Aktual"},
                                 {"x": np.arange(len(w)), "y": one, "mode": "lines", "name": "Prediksi 1 langkah", "dash": "dash"}]))
    notes = [f"**Model:** regresi dengan galat ARIMA({p},{d},{q}); parameter diduga dengan conditional sum of squares ({nobs} pengamatan efektif).",
             f"**Diagnostik galat:** Ljung-Box (lag {lb_lags}) P = {fmt_p(pQ)} → " + ("tidak ada autokorelasi tersisa (model memadai)." if pQ > alpha else "masih ada autokorelasi; naikkan orde p/q."),
             f"**Stasioneritas AR:** {'terpenuhi' if stat_ok else 'TIDAK terpenuhi (akar di dalam lingkaran satuan)'}; **invertibilitas MA:** {'terpenuhi' if inv_ok else 'tidak terpenuhi'}.",
             f"**AIC = {aic:.2f}, BIC = {bic:.2f}**; σ² galat = {s2:.4f}."]
    if d > 0:
        notes.append(f"Data didiferensiasi {d} kali (koefisien X menggambarkan hubungan antar-perubahan, tanpa intersep).")
    if cmp_ is not None and p + q > 0 and dwo < 1.5:
        notes.append(f"OLS biasa menunjukkan autokorelasi (DW = {dwo:.2f}) sehingga uji-t OLS tidak andal; model ARIMAX memperbaikinya (DW = {dwv:.2f}).")
    tables = {"Koefisien": tbl}
    if cmp_ is not None:
        tables["Perbandingan dengan OLS"] = cmp_
    tables["Autokorelasi galat"] = pd.DataFrame({"Lag": range(1, lagn + 1), "ACF": ac_a[1:], "Batas ±95%": bound}).round(4)
    warn = []
    if not stat_ok:
        warn.append("Akar AR berada di dalam lingkaran satuan: proses tidak stasioner. Pertimbangkan d = 1.")
    return std_result("ts", f"Regresi Deret Waktu – ARIMAX({p},{d},{q})", dd,
                      [("n", n0), ("Pengamatan efektif", nobs), ("AIC", f"{aic:.2f}"), ("BIC", f"{bic:.2f}"),
                       ("Durbin-Watson", f"{dwv:.3f}"), ("P Ljung-Box", fmt_p(pQ))],
                      tables, plots, notes=notes, warn=warn, extra={"resid": a})


# ============================================================================
# Regresi spasial
# ============================================================================
def spatial_weights(coords, k=5, kind="knn"):
    n = len(coords)
    D = np.sqrt(((coords[:, None, :] - coords[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(D, np.inf)
    W = np.zeros((n, n))
    if kind == "knn":
        k = min(k, n - 1)
        nn = np.argsort(D, axis=1)[:, :k]
        for i in range(n):
            W[i, nn[i]] = 1.0
    else:
        W = 1.0 / np.where(np.isfinite(D), D, np.inf) ** 2
        W[~np.isfinite(W)] = 0
    rs = W.sum(1, keepdims=True)
    rs[rs == 0] = 1
    return W / rs, D


def moran_i(e, W, n_perm=999, seed=0):
    z = e - e.mean()
    s0 = W.sum()
    I = len(z) / s0 * (z @ W @ z) / (z @ z)
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(n_perm):
        zp = rng.permutation(z)
        Ip = len(z) / s0 * (zp @ W @ zp) / (zp @ zp)
        if abs(Ip) >= abs(I):
            cnt += 1
    return float(I), (cnt + 1) / (n_perm + 1)


def _spatial_ll_sar(par, X, y, W, eig):
    p = X.shape[1]
    b, rho, ls2 = par[:p], par[p], par[p + 1]
    s2 = np.exp(ls2)
    n = len(y)
    r = y - rho * (W @ y) - X @ b
    ld = float(np.log(np.clip(1 - rho * eig, 1e-12, None)).sum())
    return -n / 2 * np.log(2 * np.pi * s2) - (r @ r) / (2 * s2) + ld


def _spatial_ll_sem(par, X, y, W, eig):
    p = X.shape[1]
    b, lam, ls2 = par[:p], par[p], par[p + 1]
    s2 = np.exp(ls2)
    n = len(y)
    r = (y - X @ b) - lam * (W @ (y - X @ b))
    ld = float(np.log(np.clip(1 - lam * eig, 1e-12, None)).sum())
    return -n / 2 * np.log(2 * np.pi * s2) - (r @ r) / (2 * s2) + ld


def _fit_spatial(X, y, W, kind):
    eig = np.real(np.linalg.eigvals(W))
    lo, hi = 1 / eig.min() + 1e-4, 1 / eig.max() - 1e-4
    n, p = X.shape

    def conc(rho):
        if kind == "sar":
            ys, Xs = y - rho * (W @ y), X
        else:
            ys, Xs = y - rho * (W @ y), X - rho * (W @ X)
        o = ols(Xs, ys)
        s2 = o["rss"] / n
        return -(-n / 2 * np.log(2 * np.pi * s2) - n / 2 + float(np.log(np.clip(1 - rho * eig, 1e-12, None)).sum())), o

    grid = np.linspace(lo, hi, 61)
    vals = [conc(g_)[0] for g_ in grid]
    i0 = int(np.argmin(vals))
    r_ = optimize.minimize_scalar(lambda t: conc(t)[0], bounds=(grid[max(i0 - 1, 0)], grid[min(i0 + 1, 60)]), method="bounded")
    rho = float(r_.x)
    _, o = conc(rho)
    b = o["beta"]
    s2 = o["rss"] / n
    par = np.concatenate([b, [rho, np.log(s2)]])
    f = _spatial_ll_sar if kind == "sar" else _spatial_ll_sem
    H = _num_hessian(lambda t: -f(t, X, y, W, eig), par, h=1e-4)
    cov = np.linalg.pinv(H)
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    return {"b": b, "rho": rho, "s2": s2, "se_b": se[:p], "se_rho": se[p], "ll": float(f(par, X, y, W, eig)), "eig": eig}


def run_spatial(df, y, xs, lon, lat, kind="sar", k_nn=5, wkind="knn", alpha=0.05):
    d = numeric_frame(df, [y] + list(xs) + [lon, lat])
    n, k = len(d), len(xs)
    if n < 25:
        raise ValueError("Regresi spasial memerlukan minimal 25 lokasi.")
    coords = d[[lon, lat]].values.astype(float)
    if len(np.unique(coords, axis=0)) < n:
        raise ValueError("Terdapat koordinat ganda; setiap lokasi harus memiliki koordinat unik.")
    W, D = spatial_weights(coords, k_nn, wkind)
    X = np.column_stack([np.ones(n), d[list(xs)].values.astype(float)])
    yv = d[y].values.astype(float)
    names = ["Intersep"] + list(xs)
    o = ols(X, yv)
    e = o["res"]
    s2 = o["rss"] / n
    I, pI = moran_i(e, W)
    Tr = float(np.trace(W.T @ W + W @ W))
    lm_err = float((e @ W @ e / s2) ** 2 / Tr)
    WXb = W @ (X @ o["beta"])
    M = np.eye(n) - X @ o["XtXi"] @ X.T
    J = (float(WXb @ M @ WXb) + Tr * s2) / (n * s2)
    lm_lag = float((e @ W @ yv / s2) ** 2 / (n * J))
    tests = pd.DataFrame([["Moran's I (galat OLS)", f"{I:.4f}", fmt_p(pI), "Ada autokorelasi spasial" if pI < alpha else "Tidak ada autokorelasi spasial"],
                          ["LM-Lag (SAR)", f"{lm_lag:.3f}", fmt_p(stats.chi2.sf(lm_lag, 1)), "Efek lag spasial nyata" if stats.chi2.sf(lm_lag, 1) < alpha else "Tidak nyata"],
                          ["LM-Error (SEM)", f"{lm_err:.3f}", fmt_p(stats.chi2.sf(lm_err, 1)), "Galat spasial nyata" if stats.chi2.sf(lm_err, 1) < alpha else "Tidak nyata"]],
                         columns=["Uji (pada model OLS)", "Statistik", "P-value", "Kesimpulan"])
    m = _fit_spatial(X, yv, W, kind)
    lab = "SAR (Spatial Autoregressive / Lag)" if kind == "sar" else "SEM (Spatial Error Model)"
    rname = "ρ (lag spasial)" if kind == "sar" else "λ (galat spasial)"
    par_names = names + [rname]
    beta = np.concatenate([m["b"], [m["rho"]]])
    se = np.concatenate([m["se_b"], [m["se_rho"]]])
    tbl = coef_table(par_names, beta, se, "z", None, alpha)
    ll_ols = -n / 2 * np.log(2 * np.pi * s2) - n / 2
    lr = 2 * (m["ll"] - ll_ols)
    aic_s, aic_o = -2 * m["ll"] + 2 * (k + 3), -2 * ll_ols + 2 * (k + 2)
    if kind == "sar":
        Ainv = np.linalg.inv(np.eye(n) - m["rho"] * W)
        imp = []
        for j in range(1, k + 1):
            S = Ainv * m["b"][j]
            tot = S.sum(1).mean()
            dr = float(np.mean(np.diag(S)))
            imp.append([names[j], dr, tot - dr, tot])
        imp_t = pd.DataFrame(imp, columns=["Variabel", "Efek langsung", "Efek tidak langsung (spillover)", "Efek total"]).round(4)
        fit = Ainv @ (X @ m["b"])
        resid = yv - fit
    else:
        imp_t = None
        fit = X @ m["b"]
        resid = (yv - fit) - m["rho"] * (W @ (yv - fit))
        resid = yv - fit
    I2, pI2 = moran_i(resid if kind == "sar" else (yv - fit) - m["rho"] * (W @ (yv - fit)), W, 499)
    notes = [f"**Matriks bobot:** {'k tetangga terdekat (k = ' + str(k_nn) + ')' if wkind == 'knn' else 'inverse jarak kuadrat'}, distandarkan per baris.",
             f"**Moran's I galat OLS** = {I:.4f} (P = {fmt_p(pI)}) → " + ("autokorelasi spasial nyata; OLS biasa tidak memadai." if pI < alpha else "tidak ada bukti autokorelasi spasial; OLS cukup."),
             f"**{rname.split(' ')[0]} = {m['rho']:.4f}** (P = {fmt_p(2 * stats.norm.sf(abs(m['rho'] / m['se_rho'])))}); LR vs OLS: χ² = {lr:.3f}, P = {fmt_p(stats.chi2.sf(max(lr, 0), 1))}.",
             f"**AIC:** {lab.split(' ')[0]} = {aic_s:.2f} vs OLS = {aic_o:.2f} → " + ("model spasial lebih baik." if aic_s < aic_o else "OLS tidak kalah."),
             f"**Moran's I galat model spasial** = {I2:.4f} (P = {fmt_p(pI2)}) → " + ("autokorelasi spasial sudah teratasi." if pI2 > alpha else "masih ada sisa autokorelasi spasial.")]
    if kind == "sar":
        notes.append("Pada model lag, koefisien β bukan efek marjinal langsung; gunakan tabel efek langsung/tidak langsung/total.")
    tables = {"Uji autokorelasi spasial": tests, f"Koefisien {lab.split(' ')[0]}": tbl}
    if imp_t is not None:
        tables["Efek langsung, tidak langsung, total"] = imp_t
    tables["Koefisien OLS (pembanding)"] = coef_table(names, o["beta"], o["se"], "t", o["dfe"], alpha)
    plots = [spec_map("Sebaran Y (observasi)", coords[:, 0], coords[:, 1], yv, lon, lat, y),
             spec_map("Galat OLS (peta)", coords[:, 0], coords[:, 1], e, lon, lat, "Galat OLS"),
             spec_xy("Diagram Moran: Galat OLS vs Lag Spasialnya", "Galat OLS", "W × Galat OLS",
                     [{"x": e, "y": W @ e, "mode": "markers", "name": "Lokasi"}], hlines=[0.0], vlines=[0.0])]
    return std_result("spatial", f"Regresi Spasial – {lab}", d,
                      [("n", n), ("Moran's I (OLS)", f"{I:.3f}"), (rname.split(" ")[0], f"{m['rho']:.3f}"), ("Log-likelihood", f"{m['ll']:.2f}"),
                       ("AIC model", f"{aic_s:.2f}"), ("AIC OLS", f"{aic_o:.2f}")],
                      tables, plots, notes=notes, extra={"resid": resid, "fitted": fit})


def run_gwr(df, y, xs, lon, lat, bw_nn=None, alpha=0.05):
    d = numeric_frame(df, [y] + list(xs) + [lon, lat])
    n, k = len(d), len(xs)
    if n < 30:
        raise ValueError("GWR memerlukan minimal 30 lokasi.")
    coords = d[[lon, lat]].values.astype(float)
    X = np.column_stack([np.ones(n), d[list(xs)].values.astype(float)])
    yv = d[y].values.astype(float)
    names = ["Intersep"] + list(xs)
    D = np.sqrt(((coords[:, None, :] - coords[None, :, :]) ** 2).sum(-1))
    p = k + 1

    def fit_gwr(q, loo=False):
        B = np.zeros((n, p))
        S = np.zeros((n, n))
        for i in range(n):
            h = np.sort(D[i])[min(q, n) - 1]
            w = np.where(D[i] < h, (1 - (D[i] / h) ** 2) ** 2, 0.0)
            if loo:
                w[i] = 0.0
            A = X.T @ (w[:, None] * X) + 1e-10 * np.eye(p)
            C = np.linalg.solve(A, (X * w[:, None]).T)
            B[i] = C @ yv
            S[i] = X[i] @ C
        return B, S

    qs = sorted({int(v) for v in np.linspace(max(p + 4, int(0.1 * n)), n, 14)})
    cv, aicc = [], []
    for q in qs:
        B, _ = fit_gwr(q, loo=True)
        cv.append(float(((yv - (B * X).sum(1)) ** 2).sum()))
    q_opt = qs[int(np.argmin(cv))]
    q = bw_nn or q_opt
    B, S = fit_gwr(q)
    fit = (B * X).sum(1)
    res = yv - fit
    rss = float(res @ res)
    tr = float(np.trace(S))
    s2 = rss / (n - tr)
    sigma = np.sqrt(rss / n)
    aicc_g = 2 * n * np.log(sigma) + n * np.log(2 * np.pi) + n * (n + tr) / (n - 2 - tr)
    o = ols(X, yv)
    aicc_o = 2 * n * np.log(np.sqrt(o["rss"] / n)) + n * np.log(2 * np.pi) + n * (n + p) / (n - 2 - p)
    # galat baku lokal
    se = np.zeros((n, p))
    for i in range(n):
        h = np.sort(D[i])[min(q, n) - 1]
        w = np.where(D[i] < h, (1 - (D[i] / h) ** 2) ** 2, 0.0)
        Ci = np.linalg.solve(X.T @ (w[:, None] * X) + 1e-10 * np.eye(p), (X * w[:, None]).T)
        se[i] = np.sqrt(s2 * (Ci ** 2).sum(1))
    sst = float(((yv - yv.mean()) ** 2).sum())
    r2 = 1 - rss / sst
    # R² lokal
    r2l = np.zeros(n)
    for i in range(n):
        h = np.sort(D[i])[min(q, n) - 1]
        w = np.where(D[i] < h, (1 - (D[i] / h) ** 2) ** 2, 0.0)
        ym = (w * yv).sum() / w.sum()
        r2l[i] = 1 - (w * (yv - fit) ** 2).sum() / max((w * (yv - ym) ** 2).sum(), 1e-12)
    summ = pd.DataFrame({"Variabel": names, "Koefisien global (OLS)": o["beta"], "Min": B.min(0), "Q1": np.quantile(B, .25, axis=0),
                         "Median": np.median(B, axis=0), "Q3": np.quantile(B, .75, axis=0), "Maks": B.max(0),
                         "Rentang antar-kuartil": np.quantile(B, .75, axis=0) - np.quantile(B, .25, axis=0)}).round(4)
    tsig = np.abs(B / np.where(se == 0, np.nan, se))
    pct = np.nanmean(tsig > stats.norm.ppf(1 - alpha / 2), axis=0) * 100
    summ["% lokasi nyata"] = np.round(pct, 1)
    cmp_ = pd.DataFrame([["OLS (global)", p, 1 - o["rss"] / sst, aicc_o], ["GWR (lokal)", tr, r2, aicc_g]],
                        columns=["Model", "df efektif", "R²", "AICc"]).round(4)
    loc = pd.DataFrame({lon: coords[:, 0], lat: coords[:, 1], **{f"b[{nm}]": B[:, j] for j, nm in enumerate(names)}, "R² lokal": r2l}).round(4)
    plots = [spec_map(f"Peta Koefisien Lokal: {nm}", coords[:, 0], coords[:, 1], B[:, j + 1], lon, lat, f"β {nm}") for j, nm in enumerate(xs)]
    plots.append(spec_map("Peta R² Lokal", coords[:, 0], coords[:, 1], r2l, lon, lat, "R² lokal"))
    plots.append(spec_xy("Bandwidth GWR (CV)", "Jumlah tetangga (adaptif)", "JKG CV", [{"x": qs, "y": cv, "mode": "lines+markers", "name": "CV"}], vlines=[float(q_opt)]))
    var_tbl = summ[summ["Variabel"] != "Intersep"]
    big = var_tbl.loc[var_tbl["Rentang antar-kuartil"].abs().idxmax()] if len(var_tbl) else None
    notes = [f"**Bandwidth adaptif optimal** (CV): {q_opt} tetangga terdekat" + (f"; dipakai {q}." if bw_nn else ".") + " Kernel bisquare adaptif.",
             f"**GWR vs OLS:** AICc {aicc_g:.2f} vs {aicc_o:.2f} (selisih {aicc_o - aicc_g:.2f}) → " + ("GWR jauh lebih baik: hubungan berubah menurut lokasi (nonstasioner spasial)." if aicc_o - aicc_g > 3 else "tidak ada bukti kuat nonstasioneritas; model global memadai."),
             f"**R²** GWR = {r2:.4f} vs OLS = {1 - o['rss'] / sst:.4f}; df efektif = {tr:.2f}."]
    if big is not None:
        notes.append(f"**Variasi spasial terbesar:** {big['Variabel']} (koefisien berkisar {big['Min']:.3f} hingga {big['Maks']:.3f}; OLS global {big['Koefisien global (OLS)']:.3f}).")
    notes.append("Uji signifikansi lokal bersifat eksploratif (banyak uji sekaligus); interpretasikan pola peta, bukan satu lokasi saja.")
    return std_result("spatial", "Geographically Weighted Regression (GWR)", d,
                      [("n", n), ("Bandwidth (tetangga)", q), ("df efektif", f"{tr:.2f}"), ("R² GWR", f"{r2:.4f}"), ("AICc GWR", f"{aicc_g:.1f}"), ("AICc OLS", f"{aicc_o:.1f}")],
                      {"Ringkasan koefisien lokal": summ, "GWR vs OLS": cmp_, "Koefisien tiap lokasi": loc}, plots, notes=notes,
                      extra={"fitted": fit, "resid": res})


# ============================================================================
# Mixed effect (random intercept [+ random slope]), REML
# ============================================================================
def run_mixed(df, y, xs, group, slope=None, alpha=0.05):
    cols = [y] + list(xs) + [group]
    d = df[cols].copy()
    for c in [y] + list(xs):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna()
    d[group] = d[group].astype(str)
    d = d.reset_index(drop=True)
    n, G = len(d), d[group].nunique()
    if slope is not None and slope not in xs:
        raise ValueError("Variabel slope acak harus salah satu variabel X.")
    if G < 5:
        raise ValueError("Mixed model memerlukan minimal 5 kelompok.")
    if n - G < 5:
        raise ValueError("Jumlah pengamatan per kelompok terlalu sedikit.")
    X = np.column_stack([np.ones(n), d[list(xs)].values.astype(float)])
    yv = d[y].values.astype(float)
    p = X.shape[1]
    names = ["Intersep"] + list(xs)
    ids = list(pd.unique(d[group]))
    idx = {g: np.where(d[group].values == g)[0] for g in ids}
    sl_col = None if slope is None else d[slope].values.astype(float)
    q = 1 if slope is None else 2
    xm = 0.0 if sl_col is None else float(sl_col.mean())

    def Zg(ii):
        return np.ones((len(ii), 1)) if sl_col is None else np.column_stack([np.ones(len(ii)), sl_col[ii] - xm])

    def Gmat(th):
        if q == 1:
            return np.array([[np.exp(2 * th[0])]])
        s0, s1, r = np.exp(th[0]), np.exp(th[1]), np.tanh(th[2])
        return np.array([[s0 ** 2, r * s0 * s1], [r * s0 * s1, s1 ** 2]])

    def pieces(th):
        Gm, se2 = Gmat(th), np.exp(2 * th[-1])
        XtVX, XtVy, ld, parts = np.zeros((p, p)), np.zeros(p), 0.0, []
        for g in ids:
            ii = idx[g]
            Z = Zg(ii)
            V = Z @ Gm @ Z.T + se2 * np.eye(len(ii))
            L = np.linalg.cholesky(V)
            Vi = np.linalg.inv(V)
            XtVX += X[ii].T @ Vi @ X[ii]
            XtVy += X[ii].T @ Vi @ yv[ii]
            ld += 2 * np.log(np.diag(L)).sum()
            parts.append((ii, Z, Vi))
        return XtVX, XtVy, ld, parts, Gm, se2

    def reml(th):
        try:
            XtVX, XtVy, ld, parts, _, _ = pieces(th)
            b = np.linalg.solve(XtVX, XtVy)
            quad = sum(float((yv[ii] - X[ii] @ b) @ Vi @ (yv[ii] - X[ii] @ b)) for ii, Z, Vi in parts)
            return 0.5 * (ld + np.linalg.slogdet(XtVX)[1] + quad)
        except np.linalg.LinAlgError:
            return 1e12

    o = ols(X, yv)
    s0 = np.log(np.sqrt(max(o["s2"], 1e-6)))
    th0 = np.array([s0 - 0.5] + ([s0 - 1.0, 0.0] if q == 2 else []) + [s0 - 0.5])
    r = optimize.minimize(reml, th0, method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-9, "maxiter": 6000, "maxfev": 6000})
    r = optimize.minimize(reml, r.x, method="BFGS")
    th = r.x
    XtVX, XtVy, ld, parts, Gm, se2 = pieces(th)
    cov = np.linalg.inv(XtVX)
    b = cov @ XtVy
    se = np.sqrt(np.diag(cov))
    dfe = max(G - 1, 1) if p == 2 and False else n - p - G
    tbl = coef_table(names, b, se, "t", max(n - p - (G if slope is None else 2 * G) // 2, 1), alpha)
    # BLUP
    blup = {}
    for (ii, Z, Vi), g in zip(parts, ids):
        blup[g] = (Gm @ Z.T @ Vi @ (yv[ii] - X[ii] @ b))
    bl = pd.DataFrame({group: ids})
    bl["Intersep acak (BLUP)"] = [blup[g][0] for g in ids]
    if q == 2:
        bl[f"Slope acak {slope} (BLUP)"] = [blup[g][1] for g in ids]
    fixed = X @ b
    cond = fixed.copy()
    for g in ids:
        ii = idx[g]
        cond[ii] = fixed[ii] + Zg(ii) @ blup[g]
    res = yv - cond
    s2u = float(Gm[0, 0])
    icc = s2u / (s2u + se2) if q == 1 else np.nan
    vf = float(np.var(fixed))
    vr = float(np.mean([np.trace(Zg(idx[g]) @ Gm @ Zg(idx[g]).T) / len(idx[g]) for g in ids]))
    r2m, r2c = vf / (vf + vr + se2), (vf + vr) / (vf + vr + se2)
    # LRT efek acak vs OLS (REML, fixed effects sama)
    reml_ols = 0.5 * (n * np.log(o["s2"] * (n - p) / n) + np.linalg.slogdet(X.T @ X)[1] - p * np.log(o["s2"] * (n - p) / n) + n)
    lr = 2 * (reml_ols - r.fun)
    p_lr = 0.5 * float(stats.chi2.sf(max(lr, 0), 1)) if q == 1 else 0.5 * float(stats.chi2.sf(max(lr, 0), 2)) + 0.5 * float(stats.chi2.sf(max(lr, 0), 1))
    vc = [["σ² intersep acak (antar-kelompok)", s2u]]
    if q == 2:
        vc += [[f"σ² slope acak ({slope})", float(Gm[1, 1])], ["Korelasi intersep–slope", float(Gm[0, 1] / np.sqrt(Gm[0, 0] * Gm[1, 1]))]]
    vc += [["σ² galat (dalam kelompok)", se2]]
    vc_t = pd.DataFrame(vc, columns=["Komponen", "Taksiran"]).round(4)
    cmp_ = pd.DataFrame({"Variabel": names, "OLS (abaikan kelompok)": o["beta"], "SE OLS": o["se"], "Mixed (REML)": b, "SE Mixed": se}).round(4)
    plots = []
    if len(xs) >= 1:
        xv = xs[0] if slope is None else slope
        xcol = d[xv].values.astype(float)
        ser = [{"x": xcol[idx[g]], "y": yv[idx[g]], "mode": "markers", "name": str(g), "nolegend": True} for g in ids[:12]]
        order_idx = {g: np.argsort(xcol[idx[g]]) for g in ids}
        for g in ids[:12]:
            ii = idx[g][order_idx[g]]
            ser.append({"x": xcol[ii], "y": cond[ii], "mode": "lines", "name": f"{g}", "nolegend": True})
        plots.append(spec_xy(f"Data dan Garis Prediksi per Kelompok (maks. 12 kelompok)", xv, y, ser))
    srt = bl.sort_values("Intersep acak (BLUP)")
    plots.append(spec_bar("Intersep Acak per Kelompok (BLUP)", group, "BLUP", list(srt[group]), list(srt["Intersep acak (BLUP)"])))
    plots += resid_specs(cond, res)[:2]
    notes = [f"**Model:** efek tetap {', '.join(xs)}; efek acak: intersep" + (f" dan slope {slope}" if q == 2 else "") + f" per {group} ({G} kelompok), penaksiran REML.",
             f"**LRT efek acak vs OLS:** χ̄² = {lr:.2f}, P = {fmt_p(p_lr)} → " + ("efek acak diperlukan (ada keragaman antar-kelompok)." if p_lr < alpha else "tidak ada bukti keragaman antar-kelompok."),
             (f"**ICC** = {icc:.3f}: {icc * 100:.1f}% keragaman Y berasal dari perbedaan antar-kelompok." if q == 1 else "ICC tergantung nilai X pada model slope acak."),
             f"**R² marginal** (efek tetap) = {r2m:.3f}; **R² kondisional** (tetap + acak) = {r2c:.3f}.",
             "Uji-t efek tetap memakai derajat bebas aproksimasi; untuk jumlah kelompok kecil (< 30) interpretasikan sebagai pendekatan."]
    return std_result("mixed", "Mixed Effect Model (REML)", d,
                      [("n", n), ("Kelompok", G), ("ICC", f"{icc:.3f}" if q == 1 else "-"), ("R² marginal", f"{r2m:.3f}"), ("R² kondisional", f"{r2c:.3f}"),
                       ("P LRT efek acak", fmt_p(p_lr))],
                      {"Efek tetap": tbl, "Komponen ragam": vc_t, "Perbandingan dengan OLS": cmp_, "BLUP per kelompok": bl.round(4)},
                      plots, notes=notes, extra={"fitted": cond, "resid": res})


# ============================================================================
# Cox proportional hazards (Breslow)
# ============================================================================
def _cox_fit(X, t, e, maxit=50, tol=1e-10):
    n, p = X.shape
    order = np.argsort(-t, kind="stable")
    Xo, to, eo = X[order], t[order], e[order]
    # indeks terakhir tiap kelompok waktu sama (pada urutan menurun)
    last = np.zeros(n, dtype=int)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and to[j + 1] == to[i]:
            j += 1
        last[i:j + 1] = j
        i = j + 1
    b = np.zeros(p)
    ll_old = -np.inf
    for it in range(maxit):
        eta = Xo @ b
        eta -= eta.max()
        w = np.exp(eta)
        S0 = np.cumsum(w)[last]
        S1 = np.cumsum(w[:, None] * Xo, axis=0)[last]
        S2 = np.cumsum(w[:, None, None] * (Xo[:, :, None] * Xo[:, None, :]), axis=0)[last]
        ll = float((eo * (eta - np.log(S0))).sum())
        ev = eo.astype(bool)
        m1 = S1[ev] / S0[ev, None]
        grad = (Xo[ev] - m1).sum(0)
        info = (S2[ev] / S0[ev, None, None] - m1[:, :, None] * m1[:, None, :]).sum(0)
        step = np.linalg.solve(info + 1e-10 * np.eye(p), grad)
        # perbaikan langkah (step-halving)
        s = 1.0
        while s > 1e-4:
            bn = b + s * step
            etan = Xo @ bn
            etan -= etan.max()
            wn = np.exp(etan)
            lln = float((eo * (etan - np.log(np.cumsum(wn)[last]))).sum())
            if lln >= ll - 1e-12:
                break
            s /= 2
        b = b + s * step
        if abs(lln - ll_old) < tol:
            ll = lln
            break
        ll_old = lln
    # info & ll di titik akhir
    eta = Xo @ b
    shift = eta.max()
    w = np.exp(eta - shift)
    S0 = np.cumsum(w)[last]
    S1 = np.cumsum(w[:, None] * Xo, axis=0)[last]
    S2 = np.cumsum(w[:, None, None] * (Xo[:, :, None] * Xo[:, None, :]), axis=0)[last]
    ev = eo.astype(bool)
    ll = float((eo * ((eta - shift) - np.log(S0))).sum())
    m1 = S1[ev] / S0[ev, None]
    info = (S2[ev] / S0[ev, None, None] - m1[:, :, None] * m1[:, None, :]).sum(0)
    return b, np.linalg.pinv(info), ll, info, it + 1


def _cox_ll0(t, e):
    order = np.argsort(-t, kind="stable")
    to, eo = t[order], e[order]
    n = len(t)
    last = np.zeros(n, dtype=int)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and to[j + 1] == to[i]:
            j += 1
        last[i:j + 1] = j
        i = j + 1
    S0 = (np.arange(n) + 1)[last]
    return float((eo * (-np.log(S0))).sum())


def concordance(t, e, risk):
    n = len(t)
    conc = disc = tie = 0
    for i in range(n):
        if not e[i]:
            continue
        m = t > t[i]
        conc += (risk[i] > risk[m]).sum()
        disc += (risk[i] < risk[m]).sum()
        tie += (risk[i] == risk[m]).sum()
    tot = conc + disc + tie
    return float((conc + 0.5 * tie) / tot) if tot else np.nan


def km_curve(t, e):
    ut = np.unique(t[e == 1])
    s, out_t, out_s = 1.0, [0.0], [1.0]
    for u in ut:
        d_ = ((t == u) & (e == 1)).sum()
        r_ = (t >= u).sum()
        s *= 1 - d_ / r_
        out_t.append(float(u))
        out_s.append(s)
    return np.array(out_t), np.array(out_s)


def run_cox(df, time, event, xs_num, xs_cat=(), alpha=0.05):
    cols = [time, event] + list(xs_num) + list(xs_cat)
    d0 = df[cols].copy()
    d0[time] = pd.to_numeric(d0[time], errors="coerce")
    d0[event] = pd.to_numeric(d0[event], errors="coerce")
    d0 = d0.dropna()
    if not set(d0[event].unique()) <= {0, 1}:
        raise ValueError("Kolom status/kejadian harus berisi 0 (tersensor) dan 1 (kejadian).")
    if (d0[time] <= 0).any():
        raise ValueError("Waktu harus bernilai positif.")
    if d0[event].sum() < 5:
        raise ValueError("Diperlukan minimal 5 kejadian (event = 1).")
    d, Xdf, refs = build_X(d0, time, xs_num, xs_cat)
    Xdf = Xdf.drop(columns="Intersep")
    d = d0.loc[d.index]
    names = list(Xdf.columns)
    if not names:
        raise ValueError("Pilih minimal satu kovariat.")
    X = Xdf.values.astype(float)
    t, e = d[time].values.astype(float), d[event].values.astype(int)
    n, p = X.shape
    if e.sum() < 2 * p:
        raise ValueError(f"Jumlah kejadian ({int(e.sum())}) terlalu sedikit untuk {p} kovariat (minimal ≈ 2×).")
    b, cov, ll, info, it = _cox_fit(X, t, e)
    se = np.sqrt(np.diag(cov))
    z = b / se
    pv = 2 * stats.norm.sf(np.abs(z))
    zc = stats.norm.ppf(1 - alpha / 2)
    cl = int(round((1 - alpha) * 100))
    tbl = pd.DataFrame({"Variabel": names, "Koefisien (B)": b, "Std. Error": se, "z": z, "P-value": [fmt_p(x) for x in pv],
                        "Sig.": [sig_mark(x) for x in pv], "Hazard Ratio exp(B)": np.exp(b),
                        f"HR CI {cl}% bawah": np.exp(b - zc * se), f"HR CI {cl}% atas": np.exp(b + zc * se)}).round(4)
    ll0 = _cox_ll0(t, e)
    lr = 2 * (ll - ll0)
    p_lr = float(stats.chi2.sf(lr, p))
    wald = float(b @ info @ b)
    # skor di b=0
    b_0, _, _, info0, _ = _cox_fit(X * 0 + X, t, e, maxit=0) if False else (None, None, None, None, None)
    cidx = concordance(t, e, X @ b)
    aic = -2 * ll + 2 * p
    # baseline hazard Breslow
    eta = X @ b
    r_exp = np.exp(eta - eta.mean())
    ut = np.unique(t[e == 1])
    H0, h = [], 0.0
    for u in ut:
        d_ = ((t == u) & (e == 1)).sum()
        h += d_ / r_exp[t >= u].sum()
        H0.append(h)
    H0 = np.array(H0)
    # uji PH (Grambsch-Therneau, g(t) = peringkat waktu) dengan residual Schoenfeld terskala
    eta_all = X @ b
    R_, T_ = [], []
    for u in ut:
        risk = t >= u
        w = np.exp(eta_all[risk] - eta_all.max())
        xbar = (w[:, None] * X[risk]).sum(0) / w.sum()
        for i in np.where((t == u) & (e == 1))[0]:
            R_.append(X[i] - xbar)
            T_.append(u)
    R_, T_ = np.array(R_), np.array(T_)
    D_ = len(T_)
    g_ = stats.rankdata(T_)
    g_ = g_ - g_.mean()
    Sst = D_ * (R_ @ cov.T)  # baris k = D * V r_k
    ph_rows = []
    for j in range(p):
        num = float((g_ * Sst[:, j]).sum()) ** 2
        den = D_ * cov[j, j] * float((g_ ** 2).sum())
        T = num / den if den > 0 else np.nan
        pr = float(stats.chi2.sf(T, 1)) if np.isfinite(T) else np.nan
        rho = float(np.corrcoef(g_, Sst[:, j])[0, 1]) if np.std(Sst[:, j]) > 0 else np.nan
        ph_rows.append([names[j], rho, fmt_p(pr), "Asumsi PH terpenuhi" if (np.isnan(pr) or pr > alpha) else "Asumsi PH dipertanyakan"])
    ph = pd.DataFrame(ph_rows, columns=["Variabel", "Korelasi dgn waktu", "P-value", "Kesimpulan"]).round(4)
    # kurva
    kt, ks = km_curve(t, e)
    plots = [{"kind": "step", "title": "Kurva Kaplan-Meier (seluruh sampel)", "xlabel": "Waktu", "ylabel": "Peluang bertahan S(t)", "series": [{"x": kt, "y": ks, "name": "KM"}]}]
    # survival model untuk profil rata-rata & tiap kovariat (±1 SD / kategori)
    prof = [{"x": np.concatenate([[0], ut]), "y": np.concatenate([[1], np.exp(-H0 * np.exp(0))]), "name": "Profil rata-rata"}]
    for j, nm in enumerate(names):
        vals = np.unique(X[:, j])
        if len(vals) == 2:
            lo, hi = vals[0], vals[1]
            lab = (f"{nm} = {lo:g}", f"{nm} = {hi:g}")
        else:
            lo, hi = X[:, j].mean() - X[:, j].std(), X[:, j].mean() + X[:, j].std()
            lab = (f"{nm} = −1 SD", f"{nm} = +1 SD")
        for val, lb in ((lo, lab[0]), (hi, lab[1])):
            dx = val - X[:, j].mean()
            prof.append({"x": np.concatenate([[0], ut]), "y": np.concatenate([[1], np.exp(-H0 * np.exp(b[j] * dx))]), "name": lb})
        break  # satu kovariat pertama agar grafik tidak padat
    plots.append({"kind": "step", "title": f"Kurva Survival Model Cox (variasi {names[0]})", "xlabel": "Waktu", "ylabel": "S(t)", "series": prof})
    plots.append(spec_bar("Hazard Ratio (skala log)", "Variabel", "log(HR)", names, list(b), err=list(zc * se)))
    plots.append({"kind": "step", "title": "Hazard Kumulatif Dasar H₀(t)", "xlabel": "Waktu", "ylabel": "H₀(t)", "series": [{"x": np.concatenate([[0], ut]), "y": np.concatenate([[0], H0]), "name": "H₀(t)"}]})
    notes = [f"**Model Cox** (Breslow untuk tie): {int(e.sum())} kejadian dari {n} subjek ({(1 - e.mean()) * 100:.0f}% tersensor).",
             f"**Uji simultan:** LR χ² = {lr:.2f} (db {p}), P = {fmt_p(p_lr)}; Wald χ² = {wald:.2f}. **Concordance (C-index)** = {cidx:.3f} " +
             f"({'baik' if cidx >= 0.7 else 'sedang' if cidx >= 0.6 else 'lemah'})."]
    for nm, b_, p_, se_ in zip(names, b, pv, se):
        if p_ < alpha:
            hr = np.exp(b_)
            notes.append(f"**{nm}**: berpengaruh nyata; HR = {hr:.3f} → risiko kejadian {'naik' if hr > 1 else 'turun'} {abs(hr - 1) * 100:.1f}% tiap kenaikan 1 satuan (HR > 1 = risiko lebih tinggi).")
    bad = [r[0] for r in ph_rows if not np.isnan(r[2] if isinstance(r[2], float) else np.nan) and False]
    bad = [r["Variabel"] for _, r in ph.iterrows() if r["Kesimpulan"].endswith("dipertanyakan")]
    notes.append("**Asumsi proportional hazards:** " + ("tidak ada pelanggaran terdeteksi (uji Grambsch-Therneau pada residual Schoenfeld terskala)." if not bad else "dipertanyakan untuk " + ", ".join(bad) + "; pertimbangkan stratifikasi atau interaksi dengan waktu."))
    if xs_cat:
        notes.append("Kategori referensi: " + "; ".join(f"{c} = {r}" for c, r in refs.items()) + ".")
    return std_result("cox", "Regresi Cox (Survival)", d,
                      [("n", n), ("Kejadian", int(e.sum())), ("Log-likelihood", f"{ll:.2f}"), ("LR χ²", f"{lr:.2f}"), ("P-value (LR)", fmt_p(p_lr)),
                       ("C-index", f"{cidx:.3f}"), ("AIC", f"{aic:.2f}")],
                      {"Koefisien & Hazard Ratio": tbl, "Uji proportional hazards": ph,
                       "Hazard kumulatif dasar": pd.DataFrame({"Waktu": ut, "H0(t)": H0, "S0(t)": np.exp(-H0)}).round(5)},
                      plots, notes=notes, extra={"b": b, "names": names, "cov": cov})


# ============================================================================
# Tobit (regresi tersensor)
# ============================================================================
def run_tobit(df, y, xs, lower=0.0, upper=None, alpha=0.05):
    d = numeric_frame(df, [y] + list(xs))
    n, k = len(d), len(xs)
    if n < 20:
        raise ValueError("Regresi Tobit memerlukan minimal 20 pengamatan.")
    X = np.column_stack([np.ones(n), d[list(xs)].values.astype(float)])
    yv = d[y].values.astype(float)
    names = ["Intersep"] + list(xs)
    cl = (yv <= lower) if lower is not None else np.zeros(n, bool)
    cr = (yv >= upper) if upper is not None else np.zeros(n, bool)
    un = ~(cl | cr)
    if un.sum() < k + 3:
        raise ValueError("Terlalu banyak pengamatan tersensor; pengamatan tak tersensor terlalu sedikit.")
    if cl.sum() + cr.sum() == 0:
        raise ValueError("Tidak ada pengamatan tersensor pada batas yang ditentukan; gunakan regresi linear biasa.")
    p = X.shape[1]

    def nll(par):
        b, ls = par[:p], par[p]
        s = np.exp(ls)
        mu = X @ b
        ll = 0.0
        if un.any():
            ll += (stats.norm.logpdf((yv[un] - mu[un]) / s) - ls).sum()
        if cl.any():
            ll += log_ndtr((lower - mu[cl]) / s).sum()
        if cr.any():
            ll += log_ndtr((mu[cr] - upper) / s).sum()
        return -float(ll)

    o = ols(X, yv)
    r = optimize.minimize(nll, np.concatenate([o["beta"], [np.log(np.sqrt(o["s2"]))]]), method="BFGS", options={"gtol": 1e-7, "maxiter": 2000})
    par = r.x
    H = _num_hessian(nll, par)
    cov = np.linalg.pinv(H)
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    b, s = par[:p], float(np.exp(par[p]))
    se_s = s * se[p]
    tbl = coef_table(names + ["σ (simpangan baku galat)"], np.concatenate([b, [s]]), np.concatenate([se[:p], [se_s]]), "z", None, alpha)
    mu = X @ b
    # efek marjinal pada E[y] teramati
    if lower is not None and upper is None:
        scale = stats.norm.cdf((mu - lower) / s)
    elif upper is not None and lower is None:
        scale = stats.norm.cdf((upper - mu) / s)
    else:
        scale = stats.norm.cdf((upper - mu) / s) - stats.norm.cdf((lower - mu) / s)
    me = scale.mean() * b[1:]
    me_t = pd.DataFrame({"Variabel": xs, "Koefisien laten (β)": b[1:], "Efek marjinal pada E[Y teramati]": me,
                         "Efek marjinal pada Y tak tersensor (β)": b[1:]}).round(4)
    ll = -r.fun
    nllnull = None
    r0 = optimize.minimize(lambda t: nll(np.concatenate([[t[0]], np.zeros(k), [t[1]]])), [float(np.mean(yv)), np.log(np.std(yv))], method="Nelder-Mead")
    lr = 2 * (ll + r0.fun)
    p_lr = float(stats.chi2.sf(max(lr, 0), k))
    cmp_ = pd.DataFrame({"Variabel": names, "OLS (abaikan sensor)": o["beta"], "Tobit": b, "Selisih": b - o["beta"]}).round(4)
    ystar = mu
    plots = []
    if k >= 1:
        x0 = d[xs[0]].values.astype(float)
        order = np.argsort(x0)
        g = x0[order]
        plots.append(spec_xy(f"Tobit vs OLS ({y} ~ {xs[0]})", xs[0], y,
                             [{"x": x0[un], "y": yv[un], "mode": "markers", "name": "Tak tersensor"},
                              {"x": x0[~un], "y": yv[~un], "mode": "markers", "name": "Tersensor"},
                              {"x": g, "y": mu[order], "mode": "lines", "name": "Tobit (laten)"},
                              {"x": g, "y": (X @ o["beta"])[order], "mode": "lines", "name": "OLS", "dash": "dash"}]))
    ey = np.where(un, 0, 0)  # placeholder
    res = yv - mu
    notes = [f"**Penyensoran:** {int(cl.sum())} tersensor kiri (≤ {lower}), {int(cr.sum())} tersensor kanan, {int(un.sum())} teramati penuh ({(1 - un.mean()) * 100:.0f}% tersensor).",
             f"**Uji simultan (LR):** χ² = {lr:.2f}, db = {k}, P = {fmt_p(p_lr)} → model {'signifikan' if p_lr < alpha else 'tidak signifikan'}.",
             "**Koefisien Tobit (β)** adalah efek pada Y laten (tanpa sensor); efek marjinal pada rata-rata Y teramati lebih kecil karena dikalikan peluang tak tersensor.",
             f"**Bias OLS:** koefisien OLS menyusut ke arah nol dibanding Tobit (mis. {names[1]}: OLS {o['beta'][1]:.3f} vs Tobit {b[1]:.3f})."]
    return std_result("tobit", "Regresi Tobit", d,
                      [("n", n), ("Tersensor", int(cl.sum() + cr.sum())), ("Log-likelihood", f"{ll:.2f}"), ("LR χ²", f"{lr:.2f}"),
                       ("P-value (LR)", fmt_p(p_lr)), ("σ", f"{s:.4f}")],
                      {"Koefisien Tobit": tbl, "Efek marjinal": me_t, "Perbandingan dengan OLS": cmp_},
                      plots, notes=notes, extra={"fitted": mu, "resid": res})
