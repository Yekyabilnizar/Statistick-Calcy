"""
design_engine.py
Mesin perhitungan RANCANGAN PERCOBAAN untuk StatCalc (tanpa Streamlit, tanpa statsmodels).

Inti: seq_anova() menghitung jumlah kuadrat sekuensial (Tipe I) dengan numpy sehingga satu mesin
dipakai oleh semua rancangan (RBSL, Graeco-Latin, BIB/Lattice, Faktorial, Split-plot, Split-split-plot,
Strip-plot, Tersarang, Pengukuran Berulang, Cross-over, ANCOVA).
Rancangan khusus (RSM, Campuran, Taguchi, Fractional Factorial, MANOVA) punya fungsi sendiri.
"""
import itertools
import string

import numpy as np
import pandas as pd
from scipy import stats

from stats_engine import f4, fmt_p, sig_mark, _compact_letters, posthoc  # noqa: F401


# ============================================================================
# 1. Inti ANOVA sekuensial
# ============================================================================
def _levels_of(d, fac):
    return list(pd.unique(d[fac]))


def tname(term):
    """Nama tampilan sebuah suku model."""
    if term[0] == "nest":          # ("nest", luar, dalam)  -> dalam(luar)
        return f"{term[2]}({term[1]})"
    if term[0] == "cov":
        return term[1]
    if term[0] == "cxf":           # kovariat x faktor
        return f"{term[1]}×{term[2]}"
    return " × ".join(term)


def _dummies(values, levels, drop_first=True):
    cols = levels[1:] if drop_first else levels
    if not cols:
        return np.zeros((len(values), 0))
    return np.column_stack([(values == c).astype(float) for c in cols])


def _term_matrix(d, term, lv):
    n = len(d)
    if term[0] == "cov":
        return d[term[1]].values.astype(float).reshape(n, 1)
    if term[0] == "cxf":
        D = _dummies(d[term[2]].values, lv[term[2]])
        return D * d[term[1]].values.astype(float).reshape(n, 1)
    if term[0] == "nest":
        lab = (d[term[1]].astype(str) + "|" + d[term[2]].astype(str)).values
        return _dummies(lab, lv[("nest", term[1], term[2])], drop_first=False)
    M = None
    for f in term:
        D = _dummies(d[f].values, lv[f])
        M = D if M is None else np.einsum("ij,ik->ijk", M, D).reshape(n, -1)
    return M


def _levels_dict(d, terms):
    lv = {}
    for t in terms:
        if t[0] == "cov":
            continue
        if t[0] == "cxf":
            lv[t[2]] = _levels_of(d, t[2])
        elif t[0] == "nest":
            lab = (d[t[1]].astype(str) + "|" + d[t[2]].astype(str))
            lv[("nest", t[1], t[2])] = list(pd.unique(lab))
        else:
            for f in t:
                lv[f] = _levels_of(d, f)
    return lv


def design_matrix(d, terms, lv=None, upto=None):
    lv = lv or _levels_dict(d, terms)
    X = np.ones((len(d), 1))
    for t in (terms if upto is None else terms[:upto]):
        X = np.hstack([X, _term_matrix(d, t, lv)])
    return X, lv


def seq_anova(d, resp, terms):
    """Jumlah kuadrat sekuensial. Mengembalikan (daftar komponen, JK sisa, db sisa, X, lv)."""
    y = d[resp].values.astype(float)
    lv = _levels_dict(d, terms)
    X = np.ones((len(y), 1))
    rank = 1
    rss_prev = float(((y - y.mean()) ** 2).sum())
    comps = []
    for t in terms:
        M = _term_matrix(d, t, lv)
        Xn = np.hstack([X, M])
        beta = np.linalg.lstsq(Xn, y, rcond=None)[0]
        rss = float(((y - Xn @ beta) ** 2).sum())
        r = int(np.linalg.matrix_rank(Xn))
        comps.append({"term": t, "name": tname(t), "ss": max(rss_prev - rss, 0.0), "df": r - rank})
        X, rank, rss_prev = Xn, r, rss
    return comps, max(rss_prev, 0.0), len(y) - rank, X, lv


def fit_terms(d, resp, terms):
    """Nilai prediksi dan galat dari model yang hanya memuat 'terms'."""
    y = d[resp].values.astype(float)
    X, _ = design_matrix(d, terms)
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    fitted = X @ beta
    return fitted, y - fitted


def ls_means(d, resp, terms, factor):
    """Rata-rata kuadrat terkecil (disesuaikan) untuk 'factor' beserta matriks kovarians."""
    y = d[resp].values.astype(float)
    X, lv = design_matrix(d, terms)
    XtXi = np.linalg.pinv(X.T @ X)
    beta = XtXi @ X.T @ y
    res = y - X @ beta
    dfe = len(y) - np.linalg.matrix_rank(X)
    s2 = float(res @ res) / dfe
    C = s2 * XtXi
    levels, rows = lv[factor], []
    for l in levels:
        d2 = d.copy()
        d2[factor] = l
        X2, _ = design_matrix(d2, terms, lv)
        rows.append(X2.mean(axis=0))
    L = np.array(rows)
    means = pd.Series(L @ beta, index=levels)
    cov = L @ C @ L.T
    return means, cov, dfe, s2


def pairwise_from_cov(means, cov, dfe, alpha, adjust="LSD"):
    """Perbandingan berpasangan dari rata-rata terkoreksi: selisih, SE, t, p (LSD atau Bonferroni)."""
    lv = list(means.index)
    m = len(lv)
    rows, pmap = [], {}
    npair = m * (m - 1) // 2
    for i in range(m):
        for j in range(i + 1, m):
            diff = means.iloc[i] - means.iloc[j]
            se = np.sqrt(max(cov[i, i] + cov[j, j] - 2 * cov[i, j], 1e-300))
            t = diff / se
            p = 2 * stats.t.sf(abs(t), dfe)
            if adjust.startswith("Bonf"):
                p = min(1.0, p * npair)
            pmap[(lv[i], lv[j])] = pmap[(lv[j], lv[i])] = p
            rows.append([f"{lv[i]} vs {lv[j]}", round(diff, 4), round(se, 4), round(t, 4), fmt_p(p),
                         "Berbeda nyata" if p < alpha else "Tidak berbeda nyata"])
    tbl = pd.DataFrame(rows, columns=["Perbandingan", "Selisih", "SE", "t hitung", "P-value", "Kesimpulan"])
    return tbl, pmap


# ----------------------------------------------------------------------------
# Pembangun tabel ANOVA umum
# ----------------------------------------------------------------------------
def make_anova(d, resp, terms, errors, tests, layout, model_terms=None, comparable=None, meta=None):
    """
    terms  : daftar suku model (urutan sekuensial)
    errors : {nama galat: [nama suku/'residual' yang dijumlahkan]}
    tests  : {nama suku: nama galat pembanding}
    layout : urutan baris yang ditampilkan (nama suku atau nama galat)
    comparable : daftar nama suku (efek utama / interaksi) yang dibandingkan rata-ratanya
    """
    comps, rss, dfres, _, _ = seq_anova(d, resp, terms)
    comp = {c["name"]: c for c in comps}
    comp["residual"] = {"name": "residual", "ss": rss, "df": dfres}
    err = {}
    for en, parts in errors.items():
        ss = sum(comp[p]["ss"] for p in parts)
        df = sum(comp[p]["df"] for p in parts)
        if df <= 0:
            raise ValueError(f"Derajat bebas {en} = 0, sehingga uji F tidak dapat dihitung. "
                             "Periksa apakah data memiliki ulangan/kelompok yang cukup.")
        err[en] = {"ss": ss, "df": df, "kt": ss / df}
    for nm, c in comp.items():
        if nm != "residual" and c["df"] <= 0 and nm in tests:
            raise ValueError(f"Suku '{nm}' tidak memiliki derajat bebas (data tidak lengkap atau tidak seimbang).")

    y = d[resp].values.astype(float)
    N = len(y)
    sst = float(((y - y.mean()) ** 2).sum())
    recs, tlist = [], []
    for item in layout:
        if item in tests:
            c, e = comp[item], err[tests[item]]
            kt = c["ss"] / c["df"]
            F = kt / e["kt"]
            p = float(stats.f.sf(F, c["df"], e["df"]))
            recs.append([item, c["df"], f4(c["ss"]), f4(kt), f4(F), fmt_p(p), sig_mark(p)])
            tlist.append({"name": item, "F": F, "p": p, "kt": kt, "db": c["df"], "err": tests[item],
                          "dbe": e["df"], "ss": c["ss"]})
        elif item in err:
            e = err[item]
            recs.append([item, e["df"], f4(e["ss"]), f4(e["kt"]), "", "", ""])
        else:  # suku tanpa uji
            c = comp[item]
            recs.append([item, c["df"], f4(c["ss"]), f4(c["ss"] / c["df"]) if c["df"] else "", "", "", ""])
    recs.append(["Total", N - 1, f4(sst), "", "", "", ""])
    anova = pd.DataFrame(recs, columns=["Sumber Keragaman", "db", "JK", "KT", "F hitung", "P-value", "Sig."])

    err_parts = {p for parts in errors.values() for p in parts}
    mt = model_terms if model_terms is not None else [t for t in terms if tname(t) not in err_parts]
    fitted, resid = fit_terms(d, resp, mt) if mt else (np.full(N, y.mean()), y - y.mean())
    dd = d.copy()
    dd["Fitted"], dd["Galat"] = fitted, resid
    grand = float(y.mean())

    effects = []
    tmap = {t["name"]: t for t in tlist}
    for nm in (comparable or []):
        term = [c["term"] for c in comps if c["name"] == nm][0]
        facs = list(term)
        key = dd[facs[0]] if len(facs) == 1 else dd[facs].astype(str).agg(" | ".join, axis=1)
        order = list(pd.unique(key))
        g = dd.groupby(key.values, sort=False)[resp]
        eff = {"name": nm, "factors": facs, "levels": order,
               "means": g.mean().reindex(order), "ns": g.count().reindex(order),
               "sd": g.std().reindex(order), "err": tmap[nm]["err"],
               "ktg": err[tmap[nm]["err"]]["kt"], "dbg": err[tmap[nm]["err"]]["df"],
               "F": tmap[nm]["F"], "p": tmap[nm]["p"]}
        effects.append(eff)

    kk = {en: (np.sqrt(e["kt"]) / grand * 100 if grand else np.nan) for en, e in err.items()}
    return {"data": dd, "resp": resp, "anova": anova, "tests": tlist, "err": err, "effects": effects,
            "grand": grand, "kk": kk, "N": N, "meta": meta or {}, "extra": {}}


# ============================================================================
# 2. Pembersihan & validasi
# ============================================================================
def _clean(df, resp, facs):
    cols = [c for c in facs if c] + [resp]
    d = df[cols].copy()
    d[resp] = pd.to_numeric(d[resp], errors="coerce")
    d = d.dropna()
    for c in facs:
        if c:
            d[c] = d[c].astype(str).str.strip()
    return d.reset_index(drop=True)


def _need_complete(d, facs, label="rancangan ini"):
    """Setiap kombinasi seluruh faktor harus tepat satu pengamatan."""
    cnt = d.groupby(facs).size()
    full = int(np.prod([d[f].nunique() for f in facs]))
    if len(cnt) != full or (cnt != 1).any():
        raise ValueError(f"{label} memerlukan data lengkap: setiap kombinasi {' × '.join(facs)} harus "
                         f"memiliki tepat 1 pengamatan (ditemukan {len(cnt)} dari {full} kombinasi, "
                         f"atau ada kombinasi ganda).")


def _distinct(cols):
    if len([c for c in cols if c]) != len(set(c for c in cols if c)):
        raise ValueError("Kolom yang dipilih harus berbeda satu sama lain.")


# ============================================================================
# 3. Rancangan lingkungan
# ============================================================================
def run_latin(df, resp, trt, row, col):
    _distinct([trt, row, col])
    d = _clean(df, resp, [trt, row, col])
    t = d[trt].nunique()
    if d[row].nunique() != t or d[col].nunique() != t or len(d) != t * t:
        raise ValueError("Bujur sangkar Latin memerlukan jumlah baris = jumlah kolom = jumlah perlakuan "
                         f"dan {t}×{t} = {t * t} pengamatan (ditemukan {d[row].nunique()} baris, "
                         f"{d[col].nunique()} kolom, {t} perlakuan, {len(d)} pengamatan).")
    _need_complete(d, [row, col], "Bujur sangkar Latin")
    for g in (row, col):
        if d.groupby([g, trt]).ngroups != t * t:
            raise ValueError(f"Setiap perlakuan harus muncul tepat sekali pada setiap {g}.")
    terms = [(row,), (col,), (trt,)]
    R = make_anova(d, resp, terms, {"Galat": ["residual"]},
                   {row: "Galat", col: "Galat", trt: "Galat"}, [row, col, trt, "Galat"], comparable=[trt])
    R.update(kind="rbsl", trt=trt, factors=[trt], meta={"t": t, "blocks": [row, col]})
    return R


def run_graeco(df, resp, trt, greek, row, col):
    _distinct([trt, greek, row, col])
    d = _clean(df, resp, [trt, greek, row, col])
    t = d[trt].nunique()
    if not (d[greek].nunique() == d[row].nunique() == d[col].nunique() == t) or len(d) != t * t:
        raise ValueError("Bujur sangkar Graeco-Latin memerlukan jumlah level yang sama pada keempat faktor "
                         "(t) dan t² pengamatan.")
    _need_complete(d, [row, col], "Bujur sangkar Graeco-Latin")
    if t < 3:
        raise ValueError("Minimal t = 3 (t = 6 tidak memiliki bujur sangkar Graeco-Latin).")
    terms = [(row,), (col,), (greek,), (trt,)]
    R = make_anova(d, resp, terms, {"Galat": ["residual"]},
                   {row: "Galat", col: "Galat", greek: "Galat", trt: "Galat"},
                   [row, col, greek, trt, "Galat"], comparable=[trt])
    R.update(kind="graeco", trt=trt, factors=[trt], meta={"t": t})
    return R


def run_incomplete(df, resp, trt, blk, rep=None, alpha=0.05, adjust="LSD"):
    """BIB / Lattice: perlakuan disesuaikan terhadap blok (JK sekuensial: blok dahulu, lalu perlakuan)."""
    _distinct([trt, blk, rep])
    d = _clean(df, resp, [trt, blk, rep])
    if rep:
        blk_term = ("nest", rep, blk)
        terms = [(rep,), blk_term, (trt,)]
        layout = [rep, tname(blk_term), trt, "Galat"]
    else:
        terms = [(blk,), (trt,)]
        layout = [blk, trt, "Galat"]
    if d[trt].nunique() < 2 or d[blk].nunique() < 2:
        raise ValueError("Minimal 2 perlakuan dan 2 blok.")
    R = make_anova(d, resp, terms, {"Galat": ["residual"]}, {trt: "Galat"}, layout, model_terms=terms)
    means, cov, dfe, s2 = ls_means(d, resp, terms, trt)
    pair_tbl, pmap = pairwise_from_cov(means, cov, dfe, alpha, adjust)
    raw = d.groupby(trt, sort=False)[resp].mean().reindex(means.index)
    cnt = d.groupby(trt, sort=False)[resp].count().reindex(means.index)
    R["effects"] = [{"name": trt, "factors": [trt], "levels": list(means.index), "means": means, "ns": cnt,
                     "sd": d.groupby(trt, sort=False)[resp].std().reindex(means.index), "err": "Galat",
                     "ktg": R["err"]["Galat"]["kt"], "dbg": R["err"]["Galat"]["df"],
                     "F": R["tests"][0]["F"], "p": R["tests"][0]["p"],
                     "custom": {"pair_df": pair_tbl, "pmap": pmap, "raw": raw,
                                "se": pd.Series(np.sqrt(np.diag(cov)), index=means.index),
                                "label": f"Rata-rata terkoreksi blok ({adjust})"}}]
    inc = pd.crosstab(d[blk] if not rep else d[rep] + "|" + d[blk], d[trt]).clip(upper=1)
    r_, k_ = inc.sum(axis=0), inc.sum(axis=1)
    lam = None
    if r_.nunique() == 1 and k_.nunique() == 1:
        M = inc.values.T @ inc.values
        off = M[~np.eye(M.shape[0], dtype=bool)]
        if len(set(off)) == 1:
            lam = int(off[0])
    R.update(kind="bib", trt=trt, factors=[trt],
             meta={"t": len(means), "b": inc.shape[0], "r": float(r_.mean()), "k": float(k_.mean()), "lambda": lam,
                   "balanced": lam is not None})
    return R


# ============================================================================
# 4. Rancangan perlakuan
# ============================================================================
def _all_interactions(factors):
    terms = []
    for r in range(1, len(factors) + 1):
        terms += [tuple(c) for c in itertools.combinations(factors, r)]
    return terms


def run_factorial(df, resp, factors, blk=None):
    if not 2 <= len(factors) <= 4:
        raise ValueError("Percobaan faktorial mendukung 2 sampai 4 faktor.")
    _distinct(list(factors) + [blk])
    d = _clean(df, resp, list(factors) + [blk])
    cell = d.groupby(list(factors)).size()
    full = int(np.prod([d[f].nunique() for f in factors]))
    if len(cell) != full:
        raise ValueError(f"Ada kombinasi perlakuan yang tidak memiliki data ({len(cell)} dari {full} kombinasi).")
    if cell.nunique() != 1:
        raise ValueError("Jumlah ulangan antar kombinasi tidak sama (data tidak seimbang). "
                         "ANOVA faktorial pada aplikasi ini memerlukan data seimbang.")
    inter = _all_interactions(list(factors))
    terms = ([(blk,)] if blk else []) + inter
    names = [tname(t) for t in inter]
    layout = ([blk] if blk else []) + names + ["Galat"]
    tests = {n: "Galat" for n in names}
    if blk:
        tests[blk] = "Galat"
    R = make_anova(d, resp, terms, {"Galat": ["residual"]}, tests, layout, model_terms=terms, comparable=names)
    R.update(kind="factorial", factors=list(factors), blk=blk,
             meta={"design": "RAKL" if blk else "RAL", "r": int(cell.iloc[0]),
                   "levels": {f: d[f].nunique() for f in factors}})
    return R


def run_split_plot(df, resp, blk, main, sub):
    _distinct([blk, main, sub])
    d = _clean(df, resp, [blk, main, sub])
    _need_complete(d, [blk, main, sub], "Petak terbagi")
    terms = [(blk,), (main,), (blk, main), (sub,), (main, sub)]
    names = [tname(t) for t in terms]
    ea, eb = "Galat (a)", "Galat (b)"
    errors = {ea: [names[2]], eb: ["residual"]}
    tests = {blk: ea, main: ea, sub: eb, names[4]: eb}
    layout = [blk, main, ea, sub, names[4], eb]
    R = make_anova(d, resp, terms, errors, tests, layout, model_terms=terms,
                   comparable=[main, sub, names[4]])
    R.update(kind="split", factors=[main, sub], blk=blk,
             meta={"main": main, "sub": sub, "b": d[blk].nunique(), "a": d[main].nunique(), "c": d[sub].nunique()})
    return R


def run_split_split(df, resp, blk, a, b, c):
    _distinct([blk, a, b, c])
    d = _clean(df, resp, [blk, a, b, c])
    _need_complete(d, [blk, a, b, c], "Petak terbagi-terbagi")
    T = lambda *x: tuple(x)
    terms = [T(blk), T(a), T(blk, a), T(b), T(a, b), T(blk, b), T(blk, a, b),
             T(c), T(a, c), T(b, c), T(a, b, c), T(blk, c), T(blk, a, c), T(blk, b, c), T(blk, a, b, c)]
    nm = {t: tname(t) for t in terms}
    ea, eb, ec = "Galat (a)", "Galat (b)", "Galat (c)"
    errors = {ea: [nm[T(blk, a)]], eb: [nm[T(blk, b)], nm[T(blk, a, b)]],
              ec: [nm[T(blk, c)], nm[T(blk, a, c)], nm[T(blk, b, c)], nm[T(blk, a, b, c)]]}
    tests = {nm[T(blk)]: ea, nm[T(a)]: ea, nm[T(b)]: eb, nm[T(a, b)]: eb,
             nm[T(c)]: ec, nm[T(a, c)]: ec, nm[T(b, c)]: ec, nm[T(a, b, c)]: ec}
    layout = [nm[T(blk)], nm[T(a)], ea, nm[T(b)], nm[T(a, b)], eb,
              nm[T(c)], nm[T(a, c)], nm[T(b, c)], nm[T(a, b, c)], ec]
    comp = [nm[T(a)], nm[T(b)], nm[T(c)], nm[T(a, b)], nm[T(a, c)], nm[T(b, c)], nm[T(a, b, c)]]
    R = make_anova(d, resp, terms, errors, tests, layout, model_terms=terms, comparable=comp)
    R.update(kind="splitsplit", factors=[a, b, c], blk=blk, meta={"main": a, "sub": b, "subsub": c})
    return R


def run_strip_plot(df, resp, blk, a, b):
    _distinct([blk, a, b])
    d = _clean(df, resp, [blk, a, b])
    _need_complete(d, [blk, a, b], "Petak berjalur")
    T = lambda *x: tuple(x)
    terms = [T(blk), T(a), T(blk, a), T(b), T(blk, b), T(a, b)]
    nm = {t: tname(t) for t in terms}
    ea, eb, ec = "Galat (a)", "Galat (b)", "Galat (c)"
    errors = {ea: [nm[T(blk, a)]], eb: [nm[T(blk, b)]], ec: ["residual"]}
    tests = {blk: ea, a: ea, b: eb, nm[T(a, b)]: ec}
    layout = [blk, a, ea, b, eb, nm[T(a, b)], ec]
    R = make_anova(d, resp, terms, errors, tests, layout, model_terms=terms, comparable=[a, b, nm[T(a, b)]])
    R.update(kind="strip", factors=[a, b], blk=blk, meta={"a": a, "b": b})
    return R


def run_nested(df, resp, a, b, b_random=True):
    """B tersarang dalam A (B(A)). b_random=True: A diuji terhadap KT B(A) (model campuran/acak)."""
    _distinct([a, b])
    d = _clean(df, resp, [a, b])
    nest = ("nest", a, b)
    nb = tname(nest)
    terms = [(a,), nest]
    ncell = d.groupby([a, b]).size()
    if ncell.min() < 2:
        raise ValueError("Rancangan tersarang memerlukan ulangan (minimal 2 pengamatan) pada setiap B dalam A.")
    errors = {"Galat": ["residual"], "Galat A": [nb]}
    tests = {nb: "Galat", a: "Galat A" if b_random else "Galat"}
    R = make_anova(d, resp, terms, errors, tests, [a, nb, "Galat"], model_terms=terms, comparable=[a])
    g = R["data"].groupby([a, b], sort=False)[resp]
    nb_means = g.mean()
    R["extra"]["nest_means"] = pd.DataFrame({
        a: [i[0] for i in nb_means.index], b: [i[1] for i in nb_means.index],
        "n": g.count().values, "Rata-rata": nb_means.values.round(4), "SD": g.std().values.round(4)})
    n0 = float(ncell.mean())
    kt_e = R["err"]["Galat"]["kt"]
    kt_b = [t for t in R["tests"] if t["name"] == nb][0]["kt"]
    R["extra"]["var_comp"] = pd.DataFrame(
        [[f"σ² {nb}", max((kt_b - kt_e) / n0, 0.0)], ["σ² Galat", kt_e]], columns=["Komponen ragam", "Taksiran"]).round(4)
    R.update(kind="nested", factors=[a], meta={"a": a, "b": b, "b_random": b_random})
    return R


def mauchly_and_eps(Y):
    """Y: matriks subjek × kondisi. Mauchly W, epsilon GG & HF."""
    n, k = Y.shape
    S = np.cov(Y, rowvar=False)
    H = np.linalg.qr(np.vstack([np.ones(k), np.eye(k)[1:]]).T)[0][:, 1:]
    Sc = H.T @ S @ H
    p = k - 1
    tr = np.trace(Sc)
    eps_gg = tr ** 2 / (p * np.trace(Sc @ Sc))
    eps_hf = min(1.0, (n * p * eps_gg - 2) / (p * (n - 1 - p * eps_gg)))
    W = np.linalg.det(Sc) / (tr / p) ** p if p > 1 else 1.0
    if p > 1 and n > 1:
        dfm = n - 1
        f = 1 - (2 * p * p + p + 2) / (6 * p * dfm)
        chi = -f * dfm * np.log(max(W, 1e-300))
        ddf = p * (p + 1) / 2 - 1
        pm = float(stats.chi2.sf(chi, ddf))
    else:
        pm = np.nan
    return W, pm, eps_gg, eps_hf


def run_repeated(df, resp, subj, within, alpha=0.05):
    _distinct([subj, within])
    d = _clean(df, resp, [subj, within])
    _need_complete(d, [subj, within], "Pengukuran berulang")
    k = d[within].nunique()
    if k < 2:
        raise ValueError("Minimal 2 kondisi/waktu pengukuran.")
    terms = [(subj,), (within,)]
    R = make_anova(d, resp, terms, {"Galat": ["residual"]}, {within: "Galat"},
                   [subj, within, "Galat"], model_terms=terms, comparable=[])
    wide = d.pivot(index=subj, columns=within, values=resp)[list(pd.unique(d[within]))]
    n = len(wide)
    t = R["tests"][0]
    ex = {}
    if k >= 3:
        W, pm, ggeps, hfeps = mauchly_and_eps(wide.values)
        rows = []
        for nm_, e in (("Tanpa koreksi (asumsi sphericity)", 1.0), ("Greenhouse-Geisser", ggeps), ("Huynh-Feldt", hfeps)):
            p_ = float(stats.f.sf(t["F"], t["db"] * e, t["dbe"] * e))
            rows.append([nm_, round(e, 4), round(t["db"] * e, 3), round(t["dbe"] * e, 3), fmt_p(p_), sig_mark(p_)])
        ex["sphericity"] = pd.DataFrame(rows, columns=["Koreksi", "Epsilon", "db1", "db2", "P-value", "Sig."])
        ex["mauchly"] = {"W": float(W), "p": pm, "gg": float(ggeps), "hf": float(hfeps)}
    lv = list(wide.columns)
    rows, pmap = [], {}
    npair = k * (k - 1) // 2
    for i in range(k):
        for j in range(i + 1, k):
            diff = wide.iloc[:, i] - wide.iloc[:, j]
            tt, pp = stats.ttest_rel(wide.iloc[:, i], wide.iloc[:, j])
            pb = min(1.0, pp * npair)
            pmap[(lv[i], lv[j])] = pmap[(lv[j], lv[i])] = pb
            rows.append([f"{lv[i]} vs {lv[j]}", round(diff.mean(), 4), round(tt, 4), fmt_p(pp), fmt_p(pb),
                         "Berbeda nyata" if pb < alpha else "Tidak berbeda nyata"])
    pair = pd.DataFrame(rows, columns=["Perbandingan", "Selisih rata-rata", "t", "P-value", "P Bonferroni", "Kesimpulan"])
    g = d.groupby(within, sort=False)[resp]
    means = g.mean().reindex(lv)
    R["effects"] = [{"name": within, "factors": [within], "levels": lv, "means": means, "ns": g.count().reindex(lv),
                     "sd": g.std().reindex(lv), "err": "Galat", "ktg": R["err"]["Galat"]["kt"],
                     "dbg": R["err"]["Galat"]["df"], "F": t["F"], "p": t["p"],
                     "custom": {"pair_df": pair, "pmap": pmap, "label": "Uji t berpasangan (Bonferroni)"}}]
    R["extra"].update(ex)
    R["extra"]["wide"] = wide
    R.update(kind="repeated", factors=[within], meta={"n": n, "k": k, "subj": subj})
    return R


def run_crossover(df, resp, seq, subj, period, trt, alpha=0.05):
    _distinct([seq, subj, period, trt])
    d = _clean(df, resp, [seq, subj, period, trt])
    if (d.groupby([seq, subj]).size() != d[period].nunique()).any():
        raise ValueError("Setiap subjek harus memiliki satu pengamatan pada setiap periode.")
    nest = ("nest", seq, subj)
    ns_ = tname(nest)
    terms = [(seq,), nest, (period,), (trt,)]
    errors = {"Galat": ["residual"], "Galat antar-subjek": [ns_]}
    tests = {seq: "Galat antar-subjek", ns_: "Galat", period: "Galat", trt: "Galat"}
    R = make_anova(d, resp, terms, errors, tests, [seq, ns_, period, trt, "Galat"],
                   model_terms=terms, comparable=[trt])
    means, cov, dfe, s2 = ls_means(R["data"], resp, terms, trt)
    pair_tbl, pmap = pairwise_from_cov(means, cov, dfe, alpha, "LSD")
    R["effects"][0]["custom"] = {"pair_df": pair_tbl, "pmap": pmap, "label": "Selisih perlakuan terkoreksi periode & subjek"}
    R["effects"][0]["means"] = means
    R.update(kind="crossover", factors=[trt], meta={"seq": seq, "n_seq": d[seq].nunique(),
                                                    "n_subj": d.groupby([seq, subj]).ngroups,
                                                    "carry": "Efek carry-over tercampur dengan efek Urutan "
                                                             "pada rancangan 2×2 dan tidak dapat diuji terpisah."})
    return R


# ============================================================================
# 5. ANCOVA
# ============================================================================
def run_ancova(df, resp, group, cov, alpha=0.05, adjust="LSD"):
    _distinct([group, cov, resp])
    d = df[[group, cov, resp]].copy()
    d[resp] = pd.to_numeric(d[resp], errors="coerce")
    d[cov] = pd.to_numeric(d[cov], errors="coerce")
    d = d.dropna().reset_index(drop=True)
    d[group] = d[group].astype(str).str.strip()
    g_n = d[group].nunique()
    if g_n < 2:
        raise ValueError("ANCOVA memerlukan minimal 2 kelompok.")
    if len(d) - 2 * g_n < 1:
        raise ValueError("Data terlalu sedikit untuk ANCOVA.")
    homo_terms = [("cov", cov), (group,), ("cxf", cov, group)]
    comps, rss, dfr, _, _ = seq_anova(d, resp, homo_terms)
    c3 = comps[2]
    F_h = (c3["ss"] / c3["df"]) / (rss / dfr)
    p_h = float(stats.f.sf(F_h, c3["df"], dfr))
    terms = [("cov", cov), (group,)]
    R = make_anova(d, resp, terms, {"Galat": ["residual"]}, {cov: "Galat", group: "Galat"}, [cov, group, "Galat"],
                   model_terms=terms, comparable=[])
    means, C, dfe, s2 = ls_means(d, resp, terms, group)
    pair_tbl, pmap = pairwise_from_cov(means, C, dfe, alpha, adjust)
    raw = d.groupby(group, sort=False)[resp].agg(["count", "mean"]).reindex(means.index)
    cm = d.groupby(group, sort=False)[cov].mean().reindex(means.index)
    X, _ = design_matrix(d, terms)
    beta = np.linalg.lstsq(X, d[resp].values.astype(float), rcond=None)[0]
    slope = float(beta[1])
    se_slope = float(np.sqrt(s2 * np.linalg.pinv(X.T @ X)[1, 1]))
    tg = [t for t in R["tests"] if t["name"] == group][0]
    R["effects"] = [{"name": group, "factors": [group], "levels": list(means.index), "means": means,
                     "ns": raw["count"], "sd": d.groupby(group, sort=False)[resp].std().reindex(means.index),
                     "err": "Galat", "ktg": s2, "dbg": dfe, "F": tg["F"], "p": tg["p"],
                     "custom": {"pair_df": pair_tbl, "pmap": pmap, "raw": raw["mean"],
                                "label": f"Rata-rata terkoreksi kovariat ({adjust})"}}]
    R["extra"].update({"homog": {"F": F_h, "p": p_h, "df1": c3["df"], "df2": dfr},
                       "slope": slope, "slope_se": se_slope, "cov_means": cm, "cov_grand": float(d[cov].mean()),
                       "adj": pd.DataFrame({group: means.index, "n": raw["count"].values,
                                            "Rata-rata awal": raw["mean"].values.round(4),
                                            f"Rata-rata {cov}": cm.values.round(4),
                                            "Rata-rata terkoreksi": means.values.round(4),
                                            "SE": np.sqrt(np.diag(C)).round(4)})})
    R.update(kind="ancova", factors=[group], cov=cov, meta={"group": group, "cov": cov})
    return R


# ============================================================================
# 6. MANOVA satu faktor (opsional + blok)
# ============================================================================
def _sscp(Y, X):
    B = np.linalg.lstsq(X, Y, rcond=None)[0]
    Rm = Y - X @ B
    return Rm.T @ Rm, int(np.linalg.matrix_rank(X))


def run_manova(df, resps, factor, block=None):
    if len(resps) < 2:
        raise ValueError("MANOVA memerlukan minimal 2 variabel respon.")
    cols = list(resps) + [factor] + ([block] if block else [])
    d = df[cols].copy()
    for r in resps:
        d[r] = pd.to_numeric(d[r], errors="coerce")
    d = d.dropna().reset_index(drop=True)
    d[factor] = d[factor].astype(str)
    if block:
        d[block] = d[block].astype(str)
    Y = d[list(resps)].values.astype(float)
    n, p = Y.shape
    terms_full = ([(block,)] if block else []) + [(factor,)]
    X_full, _ = design_matrix(d, terms_full)
    X_red, _ = design_matrix(d, terms_full[:-1]) if len(terms_full) > 1 else (np.ones((n, 1)), None)
    E, r_full = _sscp(Y, X_full)
    Rred, r_red = _sscp(Y, X_red)
    H = Rred - E
    q, v = r_full - r_red, n - r_full
    if v < p:
        raise ValueError(f"Derajat bebas galat ({v}) lebih kecil dari jumlah variabel respon ({p}); tambah ulangan.")
    ev = np.sort(np.real(np.linalg.eigvals(np.linalg.solve(E, H))))[::-1]
    ev = np.clip(ev, 0, None)
    s = min(p, q)
    m = (abs(p - q) - 1) / 2
    nn = (v - p - 1) / 2
    rows = []
    V = float((ev / (1 + ev)).sum())
    df1, df2 = s * (2 * m + s + 1), s * (2 * nn + s + 1)
    F = (2 * nn + s + 1) / (2 * m + s + 1) * V / (s - V) if s - V > 0 else np.inf
    rows.append(["Pillai's Trace", V, F, df1, df2, float(stats.f.sf(F, df1, df2))])
    lam = float(np.prod(1 / (1 + ev)))
    tmp = p * p + q * q - 5
    sw = np.sqrt((p * p * q * q - 4) / tmp) if tmp > 0 else 1.0
    df1w = p * q
    df2w = sw * (v - (p - q + 1) / 2) - (p * q - 2) / 2
    lw = lam ** (1 / sw)
    Fw = (1 - lw) / lw * df2w / df1w
    rows.append(["Wilks' Lambda", lam, Fw, df1w, df2w, float(stats.f.sf(Fw, df1w, df2w))])
    U = float(ev.sum())
    df1h, df2h = s * (2 * m + s + 1), 2 * (s * nn + 1)
    Fh = 2 * (s * nn + 1) * U / (s * s * (2 * m + s + 1))
    rows.append(["Hotelling-Lawley Trace", U, Fh, df1h, df2h, float(stats.f.sf(Fh, df1h, df2h))])
    df1r = max(p, q)
    df2r = v - df1r + q
    Fr = ev[0] * df2r / df1r
    rows.append(["Roy's Largest Root", float(ev[0]), Fr, df1r, df2r, float(stats.f.sf(Fr, df1r, df2r))])
    tbl = pd.DataFrame(rows, columns=["Statistik uji", "Nilai", "F (aproksimasi)", "db1", "db2", "P-value"])
    tbl["Sig."] = [sig_mark(x) for x in tbl["P-value"]]
    uni = []
    for r in resps:
        comps, rss, dfe, _, _ = seq_anova(d, r, terms_full)
        c = comps[-1]
        Fu = (c["ss"] / c["df"]) / (rss / dfe)
        pu = float(stats.f.sf(Fu, c["df"], dfe))
        uni.append([r, c["df"], f4(c["ss"]), f4(rss), f4(Fu), fmt_p(pu), sig_mark(pu),
                    f"{pu * len(resps):.4f}" if pu * len(resps) < 1 else "1.0000"])
    uni = pd.DataFrame(uni, columns=["Respon", "db", "JK faktor", "JK galat", "F", "P-value", "Sig.", "P Bonferroni"])
    means = d.groupby(factor, sort=False)[list(resps)].mean()
    groups = [g[list(resps)].values for _, g in d.groupby(factor, sort=False)]
    box = None
    if all(len(g) > p for g in groups) and block is None:
        k = len(groups)
        ns_ = np.array([len(g) for g in groups])
        Sg = [np.cov(g, rowvar=False) for g in groups]
        Sp = sum((ns_[i] - 1) * Sg[i] for i in range(k)) / (ns_.sum() - k)
        M = (ns_.sum() - k) * np.log(np.linalg.det(Sp)) - sum((ns_[i] - 1) * np.log(np.linalg.det(Sg[i])) for i in range(k))
        c1 = (sum(1 / (ns_ - 1)) - 1 / (ns_.sum() - k)) * (2 * p * p + 3 * p - 1) / (6 * (p + 1) * (k - 1))
        chi = M * (1 - c1)
        dfb = p * (p + 1) * (k - 1) / 2
        box = {"M": float(M), "chi2": float(chi), "df": dfb, "p": float(stats.chi2.sf(chi, dfb))}
    return {"kind": "manova", "data": d, "resps": list(resps), "factor": factor, "block": block, "multi": tbl, "uni": uni,
            "means": means, "corr": d[list(resps)].corr(), "box": box, "eig": ev, "n": n, "p": p, "q": q, "v": v,
            "levels": list(pd.unique(d[factor]))}


# ============================================================================
# 7. Rancangan respons: RSM
# ============================================================================
def code_factors(df, facs):
    """Kodekan faktor ke -1/+1. Kembalikan (kode, pusat, setengah-rentang)."""
    centers, halves, Z = {}, {}, {}
    for f in facs:
        x = pd.to_numeric(df[f], errors="coerce").astype(float)
        lv = np.sort(x.dropna().unique())
        # CCD (>= 5 level berbeda): titik faktorial (level ke-2 dan ke-2 dari atas) menjadi -1/+1.
        lo, hi = (lv[1], lv[-2]) if len(lv) >= 5 else (lv[0], lv[-1])
        centers[f], halves[f] = (hi + lo) / 2, (hi - lo) / 2 or 1.0
        Z[f] = (x - centers[f]) / halves[f]
    return pd.DataFrame(Z), centers, halves


def quad_terms(k):
    lin = [(i,) for i in range(k)]
    sq = [(i, i) for i in range(k)]
    inter = [(i, j) for i in range(k) for j in range(i + 1, k)]
    return lin, inter, sq


def run_rsm(df, resp, facs, order=2, alpha=0.05):
    k = len(facs)
    if not 2 <= k <= 4:
        raise ValueError("RSM mendukung 2 sampai 4 faktor.")
    d = df[list(facs) + [resp]].apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    Z, centers, halves = code_factors(d, facs)
    y = d[resp].values.astype(float)
    n = len(y)
    lin, inter, sq = quad_terms(k)
    spec = lin + (inter + sq if order == 2 else (inter if order == 1.5 else []))
    labels = []
    cols = [np.ones(n)]
    for t in spec:
        cols.append(np.prod([Z.iloc[:, i].values for i in t], axis=0))
        if len(t) == 1:
            labels.append(f"{facs[t[0]]}")
        elif t[0] == t[1]:
            labels.append(f"{facs[t[0]]}²")
        else:
            labels.append(f"{facs[t[0]]}×{facs[t[1]]}")
    X = np.column_stack(cols)
    p = X.shape[1]
    if n <= p:
        raise ValueError(f"Jumlah titik rancangan (n = {n}) harus lebih besar dari jumlah parameter model ({p}).")
    XtXi = np.linalg.pinv(X.T @ X)
    beta = XtXi @ X.T @ y
    fit = X @ beta
    res = y - fit
    sse = float(res @ res)
    dfe = n - np.linalg.matrix_rank(X)
    mse = sse / dfe
    se = np.sqrt(np.diag(XtXi) * mse)
    tv = beta / se
    pv = 2 * stats.t.sf(np.abs(tv), dfe)
    names = ["Intersep"] + labels
    coef = pd.DataFrame({"Suku (kode)": names, "Koefisien": beta.round(4), "SE": se.round(4), "t": tv.round(4),
                         "P-value": [fmt_p(x) for x in pv], "Sig.": [sig_mark(x) for x in pv]})
    sst = float(((y - y.mean()) ** 2).sum())
    ssm = sst - sse
    dfm = p - 1
    Fm = (ssm / dfm) / mse
    pm = float(stats.f.sf(Fm, dfm, dfe))
    rows = [["Model", dfm, f4(ssm), f4(ssm / dfm), f4(Fm), fmt_p(pm), sig_mark(pm)]]
    key = pd.Series([tuple(np.round(r, 8)) for r in Z.values])
    grp = pd.DataFrame({"k": key, "y": y}).groupby("k")["y"]
    sspe = float(sum(((g - g.mean()) ** 2).sum() for _, g in grp))
    dfpe = int(sum(len(g) - 1 for _, g in grp))
    lof = None
    if dfpe > 0 and dfe - dfpe > 0:
        sslof, dflof = sse - sspe, dfe - dfpe
        Fl = (sslof / dflof) / (sspe / dfpe)
        pl = float(stats.f.sf(Fl, dflof, dfpe))
        lof = {"F": Fl, "p": pl}
        rows += [["Galat (sisa)", dfe, f4(sse), f4(mse), "", "", ""],
                 ["  Kurang cocok (lack of fit)", dflof, f4(sslof), f4(sslof / dflof), f4(Fl), fmt_p(pl), sig_mark(pl)],
                 ["  Galat murni", dfpe, f4(sspe), f4(sspe / dfpe), "", "", ""]]
    else:
        rows += [["Galat (sisa)", dfe, f4(sse), f4(mse), "", "", ""]]
    rows.append(["Total", n - 1, f4(sst), "", "", "", ""])
    anova = pd.DataFrame(rows, columns=["Sumber Keragaman", "db", "JK", "KT", "F hitung", "P-value", "Sig."])
    r2 = 1 - sse / sst
    r2a = 1 - (sse / dfe) / (sst / (n - 1))
    h = np.einsum("ij,jk,ik->i", X, XtXi, X)
    press = float(((res / (1 - h)) ** 2).sum())
    r2p = 1 - press / sst
    stat = None
    if order == 2:
        b = beta[1:1 + k]
        B = np.zeros((k, k))
        idx = 1 + k
        for i in range(k):
            for j in range(i + 1, k):
                B[i, j] = B[j, i] = beta[idx] / 2
                idx += 1
        for i in range(k):
            B[i, i] = beta[idx]
            idx += 1
        try:
            zs = -0.5 * np.linalg.solve(B, b)
            ys = float(beta[0] + 0.5 * b @ zs)
            ev = np.linalg.eigvalsh(B)
            kind = "maksimum" if (ev < 0).all() else "minimum" if (ev > 0).all() else "titik pelana (saddle)"
            stat = {"coded": zs, "actual": {f: centers[f] + halves[f] * zs[i] for i, f in enumerate(facs)},
                    "y": ys, "eig": ev, "kind": kind,
                    "inside": bool((np.abs(zs) <= np.sqrt(k) * 1.0001).all()), "B": B, "b": b}
        except np.linalg.LinAlgError:
            stat = None

    def predict_coded(zmat):
        zmat = np.atleast_2d(zmat)
        cols_ = [np.ones(len(zmat))]
        for t in spec:
            cols_.append(np.prod([zmat[:, i] for i in t], axis=0))
        return np.column_stack(cols_) @ beta

    grids = {}
    base = stat["coded"] if stat is not None else np.zeros(k)
    base = np.clip(base, -1.6, 1.6)
    gx = np.linspace(Z.values.min(), Z.values.max(), 41)
    for i in range(k):
        for j in range(i + 1, k):
            G1, G2 = np.meshgrid(gx, gx)
            pts = np.tile(base, (G1.size, 1))
            pts[:, i], pts[:, j] = G1.ravel(), G2.ravel()
            zz = predict_coded(pts).reshape(G1.shape)
            grids[(facs[i], facs[j])] = {
                "x": centers[facs[i]] + halves[facs[i]] * gx, "y": centers[facs[j]] + halves[facs[j]] * gx, "z": zz,
                "px": d[facs[i]].values, "py": d[facs[j]].values}
    gz = np.array(list(itertools.product(np.linspace(-1, 1, 21), repeat=k)))
    pr = predict_coded(gz)
    imax, imin = int(np.argmax(pr)), int(np.argmin(pr))
    opt = {"max": {"y": float(pr[imax]), **{f: centers[f] + halves[f] * gz[imax, i] for i, f in enumerate(facs)}},
           "min": {"y": float(pr[imin]), **{f: centers[f] + halves[f] * gz[imin, i] for i, f in enumerate(facs)}}}
    return {"kind": "rsm", "data": d, "resp": resp, "facs": list(facs), "coef": coef, "anova": anova, "r2": r2, "r2a": r2a,
            "r2p": r2p, "press": press, "n": n, "p": p, "dfe": dfe, "mse": mse, "lof": lof, "stat": stat,
            "grids": grids, "opt": opt, "centers": centers, "halves": halves, "fitted": fit, "resid": res,
            "Fm": Fm, "pm": pm, "order": order, "Z": Z, "beta": beta, "labels": names}


def gen_ccd(k, n_center=5, alpha="rotatable"):
    if k < 2 or k > 5:
        raise ValueError("CCD: k = 2 sampai 5.")
    F = np.array(list(itertools.product([-1.0, 1.0], repeat=k)))
    if k == 5:
        F = F[np.prod(F, axis=1) > 0]
    a = len(F) ** 0.25 if alpha == "rotatable" else (np.sqrt(k) if alpha == "spherical" else 1.0)
    ax = []
    for i in range(k):
        for s in (-a, a):
            r = np.zeros(k)
            r[i] = s
            ax.append(r)
    D = np.vstack([F, np.array(ax), np.zeros((n_center, k))])
    return pd.DataFrame(D, columns=[f"X{i + 1}" for i in range(k)]).round(4)


def gen_bbd(k, n_center=3):
    if k < 3 or k > 5:
        raise ValueError("Box-Behnken: k = 3 sampai 5.")
    rows = []
    for i, j in itertools.combinations(range(k), 2):
        for a, b in itertools.product([-1.0, 1.0], repeat=2):
            r = np.zeros(k)
            r[i], r[j] = a, b
            rows.append(r)
    D = np.vstack([np.array(rows), np.zeros((n_center, k))])
    return pd.DataFrame(D, columns=[f"X{i + 1}" for i in range(k)])


# ============================================================================
# 8. Rancangan campuran (Scheffé)
# ============================================================================
def run_mixture(df, resp, comps, model="linear"):
    k = len(comps)
    if k < 3:
        raise ValueError("Rancangan campuran memerlukan minimal 3 komponen.")
    d = df[list(comps) + [resp]].apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    P = d[list(comps)].values.astype(float)
    tot = P.sum(axis=1)
    scale = 1.0
    if np.nanmedian(tot) > 1.5:
        P, scale = P / 100.0, 100.0
        tot = tot / 100.0
    if (np.abs(tot - 1) > 0.02).any():
        raise ValueError("Jumlah proporsi komponen harus 1 (atau 100%) pada setiap baris campuran. "
                         f"Ditemukan jumlah antara {tot.min():.3f} dan {tot.max():.3f}.")
    P = P / tot[:, None]
    y = d[resp].values.astype(float)
    n = len(y)
    cols, labels = [P[:, i] for i in range(k)], list(comps)
    pairs = list(itertools.combinations(range(k), 2))
    if model in ("quadratic", "special_cubic"):
        for i, j in pairs:
            cols.append(P[:, i] * P[:, j])
            labels.append(f"{comps[i]}·{comps[j]}")
    if model == "special_cubic" and k >= 3:
        for i, j, l in itertools.combinations(range(k), 3):
            cols.append(P[:, i] * P[:, j] * P[:, l])
            labels.append(f"{comps[i]}·{comps[j]}·{comps[l]}")
    X = np.column_stack(cols)
    p = X.shape[1]
    if n <= p:
        raise ValueError(f"Jumlah campuran (n = {n}) harus lebih besar dari jumlah parameter model ({p}).")
    XtXi = np.linalg.pinv(X.T @ X)
    beta = XtXi @ X.T @ y
    fit = X @ beta
    res = y - fit
    sse = float(res @ res)
    dfe = n - p
    mse = sse / dfe
    se = np.sqrt(np.diag(XtXi) * mse)
    tv = beta / se
    pv = 2 * stats.t.sf(np.abs(tv), dfe)
    coef = pd.DataFrame({"Suku": labels, "Koefisien": beta.round(4), "SE": se.round(4), "t": tv.round(4),
                         "P-value": [fmt_p(x) for x in pv], "Sig.": [sig_mark(x) for x in pv]})
    sst = float(((y - y.mean()) ** 2).sum())
    ssm = sst - sse
    dfm = p - 1
    Fm = (ssm / dfm) / mse
    pm = float(stats.f.sf(Fm, dfm, dfe))
    anova = pd.DataFrame([["Model", dfm, f4(ssm), f4(ssm / dfm), f4(Fm), fmt_p(pm), sig_mark(pm)],
                          ["Galat", dfe, f4(sse), f4(mse), "", "", ""],
                          ["Total", n - 1, f4(sst), "", "", "", ""]],
                         columns=["Sumber Keragaman", "db", "JK", "KT", "F hitung", "P-value", "Sig."])
    r2 = ssm / sst
    r2a = 1 - (sse / dfe) / (sst / (n - 1))

    def pred(Pm):
        cc = [Pm[:, i] for i in range(k)]
        if model in ("quadratic", "special_cubic"):
            cc += [Pm[:, i] * Pm[:, j] for i, j in pairs]
        if model == "special_cubic":
            cc += [Pm[:, i] * Pm[:, j] * Pm[:, l] for i, j, l in itertools.combinations(range(k), 3)]
        return np.column_stack(cc) @ beta

    step = 25 if k == 3 else 10 if k == 4 else 6
    g = [c for c in itertools.product(range(step + 1), repeat=k - 1) if sum(c) <= step]
    G = np.array([list(c) + [step - sum(c)] for c in g], dtype=float) / step
    pr = pred(G)
    imax, imin = int(np.argmax(pr)), int(np.argmin(pr))
    opt = {"max": (dict(zip(comps, (G[imax] * scale).round(3))), float(pr[imax])),
           "min": (dict(zip(comps, (G[imin] * scale).round(3))), float(pr[imin]))}
    return {"kind": "mixture", "data": d, "resp": resp, "comps": list(comps), "coef": coef, "anova": anova, "r2": r2,
            "r2a": r2a, "n": n, "p": p, "dfe": dfe, "fitted": fit, "resid": res, "opt": opt, "grid": G, "grid_pred": pr,
            "P": P, "y": y, "model": model, "Fm": Fm, "pm": pm, "scale": scale, "mse": mse}


# ============================================================================
# 9. Taguchi
# ============================================================================
def sn_ratio(vals, kind):
    v = np.asarray(vals, dtype=float)
    n = len(v)
    if kind == "larger":
        return -10 * np.log10(np.mean(1 / np.clip(v, 1e-12, None) ** 2))
    if kind == "smaller":
        return -10 * np.log10(np.mean(v ** 2))
    m, s2 = v.mean(), v.var(ddof=1) if n > 1 else np.nan
    return 10 * np.log10(m ** 2 / s2) if s2 and s2 > 0 else np.nan


def _l_2k(k):
    """Susunan ortogonal 2-level L(2^k) dengan 2^k - 1 kolom."""
    n = 2 ** k
    base = np.array([[(i >> (k - 1 - b)) & 1 for b in range(k)] for i in range(n)])
    cols = []
    for c in range(1, n):
        mask = np.array([(c >> (k - 1 - b)) & 1 for b in range(k)])
        cols.append((base @ mask) % 2)
    return np.column_stack(cols) + 1


OA = {
    "L4 (2³)": {"levels": 2, "array": np.array([[1, 1, 1], [1, 2, 2], [2, 1, 2], [2, 2, 1]])},
    "L8 (2⁷)": {"levels": 2, "array": _l_2k(3)},
    "L9 (3⁴)": {"levels": 3, "array": np.array([[1, 1, 1, 1], [1, 2, 2, 2], [1, 3, 3, 3], [2, 1, 2, 3], [2, 2, 3, 1],
                                                 [2, 3, 1, 2], [3, 1, 3, 2], [3, 2, 1, 3], [3, 3, 2, 1]])},
    "L16 (2¹⁵)": {"levels": 2, "array": _l_2k(4)},
}


def run_taguchi(df, factors, resp_cols, kind="larger"):
    if not factors or not resp_cols:
        raise ValueError("Pilih minimal 1 faktor dan 1 kolom respon.")
    d = df[list(factors) + list(resp_cols)].copy()
    for r in resp_cols:
        d[r] = pd.to_numeric(d[r], errors="coerce")
    d = d.dropna().reset_index(drop=True)
    for f in factors:
        d[f] = d[f].astype(str)
    Yv = d[list(resp_cols)].values
    d["Rata-rata"] = Yv.mean(axis=1)
    d["S/N"] = [sn_ratio(r, kind) for r in Yv]
    if kind == "nominal" and d["S/N"].isna().any():
        raise ValueError("S/N nominal-terbaik memerlukan minimal 2 replikasi dengan ragam > 0 pada setiap run.")
    rows = []
    for f in factors:
        lv = sorted(pd.unique(d[f]), key=lambda s: (len(s), s))
        sn = d.groupby(f)["S/N"].mean().reindex(lv)
        mn = d.groupby(f)["Rata-rata"].mean().reindex(lv)
        for l in lv:
            rows.append([f, l, sn[l], mn[l]])
    table = pd.DataFrame(rows, columns=["Faktor", "Level", "Rata-rata S/N", "Rata-rata respon"])
    rank = []
    for f in factors:
        sub = table[table["Faktor"] == f]
        rank.append([f, sub["Rata-rata S/N"].max() - sub["Rata-rata S/N"].min(),
                     sub["Rata-rata respon"].max() - sub["Rata-rata respon"].min()])
    rk = pd.DataFrame(rank, columns=["Faktor", "Delta S/N", "Delta respon"])
    rk["Peringkat"] = rk["Delta S/N"].rank(ascending=False, method="min").astype(int)
    best = {f: table[table["Faktor"] == f].sort_values("Rata-rata S/N", ascending=False)["Level"].iloc[0] for f in factors}
    comps, rss, dfe, _, _ = seq_anova(d, "S/N", [(f,) for f in factors])
    sst = float(((d["S/N"] - d["S/N"].mean()) ** 2).sum())
    comps = [dict(c) for c in comps]
    pooled_note = None
    err_ss, err_df = rss, dfe
    if err_df <= 0 and len(comps) > 1:
        small = min(comps, key=lambda c: c["ss"])
        err_ss, err_df = small["ss"] + rss, small["df"] + dfe
        comps = [c for c in comps if c is not small]
        pooled_note = small["name"]
    arows = []
    for c in comps:
        kt = c["ss"] / c["df"] if c["df"] else np.nan
        if err_df > 0 and c["df"]:
            Fv = kt / (err_ss / err_df)
            pv = fmt_p(stats.f.sf(Fv, c["df"], err_df))
        else:
            Fv, pv = np.nan, "-"
        arows.append([c["name"], c["df"], c["ss"], kt, c["ss"] / sst * 100, Fv, pv])
    arows.append(["Galat" + (f" (gabungan {pooled_note})" if pooled_note else ""), err_df, err_ss,
                  err_ss / err_df if err_df > 0 else np.nan, err_ss / sst * 100, np.nan, ""])
    anova = pd.DataFrame(arows, columns=["Faktor", "db", "JK", "KT", "Kontribusi (%)", "F hitung", "P-value"])
    gm = d["S/N"].mean()
    pred = gm + sum(table[(table["Faktor"] == f) & (table["Level"] == best[f])]["Rata-rata S/N"].iloc[0] - gm
                    for f in factors)
    return {"kind": "taguchi", "data": d, "factors": list(factors), "resps": list(resp_cols), "sn_type": kind,
            "table": table, "rank": rk, "best": best, "anova": anova, "dfe": err_df, "pooled": pooled_note,
            "grand_sn": gm, "pred_sn": float(pred)}


# ============================================================================
# 10. Fractional factorial (analisis + pembangkit)
# ============================================================================
def lenth_pse(effects):
    e = np.abs(np.asarray(effects, dtype=float))
    s0 = 1.5 * np.median(e)
    return float(1.5 * np.median(e[e < 2.5 * s0]) if (e < 2.5 * s0).any() else s0)


def run_fracfact(df, resp, facs, max_order=2):
    k = len(facs)
    d = df[list(facs) + [resp]].apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    for f in facs:
        if set(np.unique(d[f])) - {-1.0, 1.0}:
            if d[f].nunique() != 2:
                raise ValueError(f"Faktor '{f}' harus 2 level (kode -1/+1 atau dua nilai berbeda).")
            Z, _, _ = code_factors(d, [f])
            d[f] = Z[f].values
    n = len(d)
    y = d[resp].values.astype(float)
    cols, labels = [], []
    for r in range(1, max_order + 1):
        for c in itertools.combinations(range(k), r):
            cols.append(np.prod([d[facs[i]].values for i in c], axis=0))
            labels.append("".join(facs[i] for i in c) if all(len(f) == 1 for f in facs)
                          else " × ".join(facs[i] for i in c))
    X = np.column_stack(cols)
    keep, alias_of = [], {}
    for j in range(X.shape[1]):
        dup = None
        for i in keep:
            if np.allclose(X[:, i], X[:, j]) or np.allclose(X[:, i], -X[:, j]):
                dup = i
                break
        if dup is None:
            keep.append(j)
        else:
            alias_of.setdefault(dup, []).append(j)
    if len(keep) > n - 1:
        keep = keep[: n - 1]
    Xk = X[:, keep]
    effects = 2 * (Xk.T @ y) / n
    lab = [labels[j] + ((" (= " + ", ".join(labels[a] for a in alias_of[j]) + ")") if j in alias_of else "")
           for j in keep]
    Xf = np.column_stack([np.ones(n), Xk])
    dfe = n - Xf.shape[1]
    ex = {"effects": effects}
    tbl = pd.DataFrame({"Efek": lab, "Nilai efek": effects, "Koefisien (efek/2)": effects / 2,
                        "Kontribusi (%)": effects ** 2 / (effects ** 2).sum() * 100})
    if dfe > 0:
        res = y - Xf @ np.linalg.lstsq(Xf, y, rcond=None)[0]
        mse = float(res @ res) / dfe
        se_eff = 2 * np.sqrt(mse / n)
        t = effects / se_eff
        p = 2 * stats.t.sf(np.abs(t), dfe)
        tbl["SE efek"], tbl["t"], tbl["P-value"] = se_eff, t, [fmt_p(x) for x in p]
        tbl["Sig."] = [sig_mark(x) for x in p]
        ex.update(mode="anova", dfe=dfe, mse=mse)
    else:
        pse = lenth_pse(effects)
        dfl = len(effects) / 3
        t = effects / pse
        p = 2 * stats.t.sf(np.abs(t), dfl)
        tbl["PSE Lenth"], tbl["t (Lenth)"], tbl["P-value (Lenth)"] = pse, t, [fmt_p(x) for x in p]
        tbl["Sig."] = [sig_mark(x) for x in p]
        ex.update(mode="lenth", pse=pse, dfl=dfl)
    tbl = tbl.sort_values("Nilai efek", key=np.abs, ascending=False).reset_index(drop=True)
    return {"kind": "fracfact", "data": d, "resp": resp, "facs": list(facs), "table": tbl,
            "eff": [(lab[i], effects[i]) for i in range(len(lab))], "extra": ex,
            "n": n, "k": k, "runs_full": 2 ** k, "fraction": n / 2 ** k, "dropped_alias": len(labels) - len(keep)}


def gen_fracfact(base, gens):
    """base: jumlah faktor dasar (A..); gens: daftar 'E=ABCD'. Mengembalikan (desain, relasi, resolusi, romawi, alias)."""
    letters = string.ascii_uppercase
    bf = list(letters[:base])
    runs = np.array(list(itertools.product([-1, 1], repeat=base)))
    D = {f: runs[:, i].astype(float) for i, f in enumerate(bf)}
    words = []
    for g in gens:
        if "=" not in g:
            raise ValueError(f"Generator '{g}' tidak valid. Gunakan bentuk seperti E=ABCD.")
        new, rhs = [s.strip().upper() for s in g.split("=")]
        sign = 1
        if rhs.startswith("-"):
            sign, rhs = -1, rhs[1:]
        if len(new) != 1 or not rhs or not all(c in D for c in rhs):
            raise ValueError(f"Generator '{g}' memakai faktor yang belum terdefinisi.")
        D[new] = sign * np.prod([D[c] for c in rhs], axis=0)
        words.append(new + rhs)
    names = list(D.keys())

    def mul(a, b):
        return "".join(sorted(set(a) ^ set(b)))

    group = set()
    for r in range(1, len(words) + 1):
        for c in itertools.combinations(words, r):
            w = ""
            for x in c:
                w = mul(w, x)
            group.add(w)
    group = sorted(group, key=lambda w: (len(w), w))
    resol = min(len(w) for w in group)
    roman = {3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}.get(resol, str(resol))
    alias = []
    for r in (1, 2):
        for c in itertools.combinations(names, r):
            e = "".join(c)
            al = sorted({mul(e, w) for w in group if mul(e, w) != e and len(mul(e, w)) <= 3})
            alias.append([e, ", ".join(al) if al else "-"])
    design = pd.DataFrame({f: D[f].astype(int) for f in names})
    return design, ["I = " + w for w in group], resol, roman, pd.DataFrame(alias, columns=["Efek", "Beralias dengan"])


# ============================================================================
# 11. Data contoh
# ============================================================================
def sample_design(kind):
    rng = np.random.default_rng(7)
    r1 = lambda x: round(float(x), 2)
    if kind == "rbsl":
        t = 4
        trt = np.array(list("ABCD"))
        eff = {"A": 0, "B": 2.5, "C": 5, "D": 3.2}
        re_, ce = [0, 1, -1, 0.5], [0.3, -0.4, 0.8, 0]
        rows = []
        for i in range(t):
            for j in range(t):
                tt = trt[(i + j) % t]
                rows.append([f"B{i + 1}", f"K{j + 1}", tt, r1(30 + eff[tt] + re_[i] + ce[j] + rng.normal(0, .6))])
        return pd.DataFrame(rows, columns=["Baris", "Kolom", "Perlakuan", "Hasil"])
    if kind == "graeco":
        t = 5
        eff = np.array([0, 2, 4, 3, 1.0])
        rows = []
        for i in range(t):
            for j in range(t):
                a, g = (i + j) % t, (i + 2 * j) % t
                rows.append([f"B{i + 1}", f"K{j + 1}", f"P{a + 1}", f"G{g + 1}",
                             r1(50 + eff[a] + 0.8 * (g - 2) * 0.3 + rng.normal(0, .7))])
        return pd.DataFrame(rows, columns=["Baris", "Kolom", "Perlakuan", "Greek", "Hasil"])
    if kind == "bib":
        eff = {"V1": 0, "V2": 3, "V3": 5, "V4": 2}
        rows = []
        for b in range(4):
            for tn in eff:
                if tn != f"V{b + 1}":
                    rows.append([f"Blok{b + 1}", tn, r1(20 + eff[tn] + (b - 1.5) * 0.9 + rng.normal(0, .5))])
        return pd.DataFrame(rows, columns=["Blok", "Perlakuan", "Hasil"])
    if kind == "factorial":
        a_eff, b_eff = {"D0": 0, "D1": 3, "D2": 5}, {"V1": 0, "V2": 2}
        rows = []
        for r in range(1, 4):
            for a in a_eff:
                for b in b_eff:
                    inter = 1.5 if (a == "D2" and b == "V2") else 0
                    rows.append([a, b, f"K{r}", r1(40 + a_eff[a] + b_eff[b] + inter + (r - 2) * 0.8 + rng.normal(0, .8))])
        return pd.DataFrame(rows, columns=["Dosis", "Varietas", "Kelompok", "Hasil"])
    if kind == "split":
        a_eff, b_eff = {"I1": 0, "I2": 3, "I3": 5}, {"V1": 0, "V2": 2, "V3": 4}
        rows = []
        for b in range(1, 5):
            be = rng.normal(0, 1)
            for a in a_eff:
                ae = rng.normal(0, 1.2)
                for s in b_eff:
                    rows.append([f"K{b}", a, s, r1(35 + a_eff[a] + b_eff[s] + 0.3 * a_eff[a] * (s == "V3") + be + ae + rng.normal(0, .6))])
        return pd.DataFrame(rows, columns=["Kelompok", "Petak_Utama", "Anak_Petak", "Hasil"])
    if kind == "splitsplit":
        ae, be, ce = {"A1": 0, "A2": 3}, {"B1": 0, "B2": 2}, {"C1": 0, "C2": 1.5, "C3": 4}
        rows = []
        for b in range(1, 4):
            bk = rng.normal(0, 1)
            for a in ae:
                e1 = rng.normal(0, 1)
                for bb in be:
                    e2 = rng.normal(0, .8)
                    for c in ce:
                        rows.append([f"K{b}", a, bb, c, r1(30 + ae[a] + be[bb] + ce[c] + bk + e1 + e2 + rng.normal(0, .5))])
        return pd.DataFrame(rows, columns=["Kelompok", "Petak_Utama", "Anak_Petak", "Anak_anak_Petak", "Hasil"])
    if kind == "strip":
        ae, be = {"J1": 0, "J2": 2, "J3": 4}, {"P1": 0, "P2": 3, "P3": 5}
        rows = []
        for b in range(1, 4):
            bk = rng.normal(0, 1)
            ea = {a: rng.normal(0, 1) for a in ae}
            eb = {s: rng.normal(0, 1) for s in be}
            for a in ae:
                for s in be:
                    rows.append([f"K{b}", a, s, r1(25 + ae[a] + be[s] + bk + ea[a] + eb[s] + rng.normal(0, .6))])
        return pd.DataFrame(rows, columns=["Kelompok", "Faktor_A", "Faktor_B", "Hasil"])
    if kind == "nested":
        rows = []
        a_eff = {"L1": 0, "L2": 4, "L3": 2}
        for a in a_eff:
            for b in ("B1", "B2", "B3"):
                be = rng.normal(0, 1.5)
                for _ in range(4):
                    rows.append([a, b, r1(30 + a_eff[a] + be + rng.normal(0, .8))])
        return pd.DataFrame(rows, columns=["Lokasi", "Pohon", "Hasil"])
    if kind == "repeated":
        tp = {"T0": 0, "T1": 2.5, "T2": 4, "T3": 4.5}
        rows = []
        for s in range(1, 9):
            se = rng.normal(0, 3)
            for t in tp:
                rows.append([f"S{s}", t, r1(60 + tp[t] + se + rng.normal(0, 1.2))])
        return pd.DataFrame(rows, columns=["Subjek", "Waktu", "Respon"])
    if kind == "crossover":
        rows = []
        for s in range(1, 13):
            seq = "AB" if s <= 6 else "BA"
            se = rng.normal(0, 2)
            for per, trt in enumerate(seq, start=1):
                y = 50 + se + (4 if trt == "B" else 0) + (1 if per == 2 else 0) + rng.normal(0, 1)
                rows.append([seq, f"S{s}", f"P{per}", trt, r1(y)])
        return pd.DataFrame(rows, columns=["Urutan", "Subjek", "Periode", "Perlakuan", "Respon"])
    if kind == "ancova":
        rows = []
        for g, e in (("Kontrol", 0), ("Pakan1", 3), ("Pakan2", 5)):
            for _ in range(8):
                x = rng.normal(20, 2.5)
                rows.append([g, r1(x), r1(10 + 0.9 * (x - 20) + e + rng.normal(0, 1))])
        return pd.DataFrame(rows, columns=["Perlakuan", "Bobot_Awal", "Pertambahan_Bobot"])
    if kind == "manova":
        rows = []
        mu = {"G1": (10, 20, 5), "G2": (12, 22, 5.5), "G3": (14, 21, 8)}
        for g, m in mu.items():
            for _ in range(10):
                z = rng.normal(0, 1)
                rows.append([g] + [r1(m[0] + z + rng.normal(0, 1)), r1(m[1] + 0.5 * z + rng.normal(0, 1.2)),
                                   r1(m[2] + rng.normal(0, 0.8))])
        return pd.DataFrame(rows, columns=["Perlakuan", "Tinggi", "Bobot", "Kadar"])
    if kind == "rsm":
        D = gen_ccd(2, 5)
        suhu, waktu = 80 + 10 * D["X1"], 60 + 15 * D["X2"]
        y = 75 + 4 * D["X1"] + 3 * D["X2"] - 3.5 * D["X1"] ** 2 - 2.5 * D["X2"] ** 2 + 1.2 * D["X1"] * D["X2"] + rng.normal(0, .6, len(D))
        return pd.DataFrame({"Suhu": suhu.round(2), "Waktu": waktu.round(2), "Rendemen": y.round(2)})
    if kind == "mixture":
        pts = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (.5, .5, 0), (.5, 0, .5), (0, .5, .5), (1 / 3, 1 / 3, 1 / 3),
               (2 / 3, 1 / 6, 1 / 6), (1 / 6, 2 / 3, 1 / 6), (1 / 6, 1 / 6, 2 / 3), (1, 0, 0), (0, 1, 0)]
        rows = []
        for a, b, c in pts:
            y = 20 * a + 30 * b + 15 * c + 40 * a * b + 25 * b * c - 10 * a * c + rng.normal(0, .8)
            rows.append([round(a, 4), round(b, 4), round(c, 4), r1(y)])
        return pd.DataFrame(rows, columns=["Tepung", "Air", "Gula", "Kekerasan"])
    if kind == "taguchi":
        A = OA["L9 (3⁴)"]["array"]
        eff = [{1: 0, 2: 2, 3: 4}, {1: 3, 2: 0, 3: 1}, {1: 0, 2: 1, 3: 0.5}, {1: 1, 2: 0, 3: 2}]
        rows = []
        for r in A:
            base = 50 + sum(eff[j][r[j]] for j in range(4))
            rows.append([f"L{r[0]}", f"L{r[1]}", f"L{r[2]}", f"L{r[3]}"] + [r1(base + rng.normal(0, 1.2)) for _ in range(3)])
        return pd.DataFrame(rows, columns=["Suhu", "Tekanan", "Waktu", "Kecepatan", "Y1", "Y2", "Y3"])
    if kind == "fracfact":
        D, _, _, _, _ = gen_fracfact(4, ["E=ABCD"])
        y = 60 + 5 * D["A"] + 3 * D["B"] - 4 * D["E"] + 2.5 * D["A"] * D["B"] + rng.normal(0, 1, len(D))
        D = D.copy()
        D["Hasil"] = y.round(2)
        return D
    raise KeyError(kind)
