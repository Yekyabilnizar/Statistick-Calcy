"""
pages_design.py – halaman Streamlit untuk rancangan percobaan lanjutan dan uji lanjut (BNT, DMRT, Tukey, Scheffé, Dunnett).
"""
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

import design_engine as de
import reg_core as rc
from posthoc_ext import METHODS, posthoc_any
from ui_core import (H, section, form_header, crumb, all_cols, cat_like, draw_spec, draw_specs, num_cols, pick, pick_multi, pick_optional, safe_run)


# ============================================================================
# Formulir per rancangan
# ============================================================================
def _need(df, n_cat=1, n_num=1):
    if len(cat_like(df)) < n_cat or len(num_cols(df)) < n_num:
        H["n_warn"](f"Data memerlukan minimal {n_cat} kolom faktor/kategori dan {n_num} kolom respon numerik.")
        return False
    return True


def _resp(df, k, want, exclude=()):
    num = [c for c in num_cols(df) if c not in exclude]
    return pick("Variabel respon (numerik)", num, f"{k}_resp", want, -1)


def f_latin(df, a, k):
    if not _need(df, 3):
        return None
    cats = cat_like(df)
    c = st.columns(4)
    trt = pick("Perlakuan", cats, f"{k}_t", "Perlakuan", 2)
    row = pick("Baris", [x for x in cats if x != trt], f"{k}_r", "Baris", 0)
    col = pick("Kolom", [x for x in cats if x not in (trt, row)], f"{k}_c", "Kolom", 0)
    resp = _resp(df, k, "Hasil", (trt, row, col))
    return safe_run(de.run_latin, df, resp, trt, row, col)


def f_graeco(df, a, k):
    if not _need(df, 4):
        return None
    cats = cat_like(df)
    trt = pick("Perlakuan (huruf Latin)", cats, f"{k}_t", "Perlakuan", 2)
    gr = pick("Faktor ke-3 (huruf Yunani)", [x for x in cats if x != trt], f"{k}_g", "Greek", 0)
    row = pick("Baris", [x for x in cats if x not in (trt, gr)], f"{k}_r", "Baris", 0)
    col = pick("Kolom", [x for x in cats if x not in (trt, gr, row)], f"{k}_c", "Kolom", 0)
    resp = _resp(df, k, "Hasil", (trt, gr, row, col))
    return safe_run(de.run_graeco, df, resp, trt, gr, row, col)


def f_bib(df, a, k):
    if not _need(df, 2):
        return None
    cats = cat_like(df)
    trt = pick("Perlakuan", cats, f"{k}_t", "Perlakuan", 0)
    blk = pick("Blok", [x for x in cats if x != trt], f"{k}_b", "Blok", 0)
    rep = pick_optional("Ulangan/replikasi (khusus Lattice, opsional)", [x for x in cats if x not in (trt, blk)], f"{k}_rep")
    adj = st.selectbox("Koreksi uji berpasangan", ["LSD", "Bonferroni"], key=f"{k}_adj")
    resp = _resp(df, k, "Hasil", (trt, blk))
    return safe_run(de.run_incomplete, df, resp, trt, blk, rep, a, adj)


def f_factorial(df, a, k):
    if not _need(df, 2):
        return None
    cats = cat_like(df)
    facs = pick_multi("Faktor (2–4)", cats, f"{k}_f", ["Dosis", "Varietas"])
    blk = pick_optional("Kelompok/blok (opsional, jadi RAK faktorial)", [c for c in cats if c not in facs], f"{k}_b", "Kelompok")
    resp = _resp(df, k, "Hasil", tuple(facs) + (blk,))
    if len(facs) < 2:
        H["n_info"]("Pilih 2 sampai 4 faktor.")
        return None
    return safe_run(de.run_factorial, df, resp, facs, blk)


def f_split(df, a, k):
    if not _need(df, 3):
        return None
    cats = cat_like(df)
    blk = pick("Kelompok (ulangan)", cats, f"{k}_b", "Kelompok", 0)
    m = pick("Petak utama (main plot)", [c for c in cats if c != blk], f"{k}_m", "Petak_Utama", 0)
    s = pick("Anak petak (sub plot)", [c for c in cats if c not in (blk, m)], f"{k}_s", "Anak_Petak", 0)
    resp = _resp(df, k, "Hasil", (blk, m, s))
    return safe_run(de.run_split_plot, df, resp, blk, m, s)


def f_splitsplit(df, a, k):
    if not _need(df, 4):
        return None
    cats = cat_like(df)
    blk = pick("Kelompok (ulangan)", cats, f"{k}_b", "Kelompok", 0)
    m = pick("Petak utama", [c for c in cats if c != blk], f"{k}_m", "Petak_Utama", 0)
    s = pick("Anak petak", [c for c in cats if c not in (blk, m)], f"{k}_s", "Anak_Petak", 0)
    ss = pick("Anak-anak petak", [c for c in cats if c not in (blk, m, s)], f"{k}_ss", "Anak_anak_Petak", 0)
    resp = _resp(df, k, "Hasil", (blk, m, s, ss))
    return safe_run(de.run_split_split, df, resp, blk, m, s, ss)


def f_strip(df, a, k):
    if not _need(df, 3):
        return None
    cats = cat_like(df)
    blk = pick("Kelompok (ulangan)", cats, f"{k}_b", "Kelompok", 0)
    fa = pick("Faktor A (jalur horizontal)", [c for c in cats if c != blk], f"{k}_a", "Faktor_A", 0)
    fb = pick("Faktor B (jalur vertikal)", [c for c in cats if c not in (blk, fa)], f"{k}_bb", "Faktor_B", 0)
    resp = _resp(df, k, "Hasil", (blk, fa, fb))
    return safe_run(de.run_strip_plot, df, resp, blk, fa, fb)


def f_nested(df, a, k):
    if not _need(df, 2):
        return None
    cats = cat_like(df)
    fa = pick("Faktor A (tingkat atas)", cats, f"{k}_a", "Lokasi", 0)
    fb = pick("Faktor B (tersarang dalam A)", [c for c in cats if c != fa], f"{k}_b", "Pohon", 0)
    rnd = st.checkbox("Faktor B bersifat acak (random)", True, key=f"{k}_rnd",
                      help="Acak: A diuji terhadap B(A). Tetap: A diuji terhadap galat.")
    resp = _resp(df, k, "Hasil", (fa, fb))
    return safe_run(de.run_nested, df, resp, fa, fb, rnd)


def f_repeated(df, a, k):
    if not _need(df, 2):
        return None
    cats = cat_like(df)
    sub = pick("Subjek", cats, f"{k}_s", "Subjek", 0)
    wit = pick("Faktor within-subject (waktu/kondisi)", [c for c in cats if c != sub], f"{k}_w", "Waktu", 0)
    resp = _resp(df, k, "Respon", (sub, wit))
    return safe_run(de.run_repeated, df, resp, sub, wit, a)


def f_crossover(df, a, k):
    if not _need(df, 4):
        return None
    cats = cat_like(df)
    seq = pick("Urutan (sequence)", cats, f"{k}_q", "Urutan", 0)
    sub = pick("Subjek", [c for c in cats if c != seq], f"{k}_s", "Subjek", 0)
    per = pick("Periode", [c for c in cats if c not in (seq, sub)], f"{k}_p", "Periode", 0)
    trt = pick("Perlakuan", [c for c in cats if c not in (seq, sub, per)], f"{k}_t", "Perlakuan", 0)
    resp = _resp(df, k, "Respon", (seq, sub, per, trt))
    return safe_run(de.run_crossover, df, resp, seq, sub, per, trt, a)


def f_ancova(df, a, k):
    if not _need(df, 1, 2):
        return None
    cats = cat_like(df)
    grp = pick("Kelompok/perlakuan", cats, f"{k}_g", "Perlakuan", 0)
    num = [c for c in num_cols(df) if c != grp]
    resp = pick("Variabel respon", num, f"{k}_r", "Pertambahan_Bobot", -1)
    cov = pick("Kovariat (numerik)", [c for c in num if c != resp], f"{k}_c", "Bobot_Awal", 0)
    adj = st.selectbox("Koreksi uji berpasangan", ["LSD", "Bonferroni"], key=f"{k}_adj")
    return safe_run(de.run_ancova, df, resp, grp, cov, a, adj)


def f_manova(df, a, k):
    if not _need(df, 1, 2):
        return None
    cats = cat_like(df)
    fac = pick("Faktor/perlakuan", cats, f"{k}_f", "Perlakuan", 0)
    num = [c for c in num_cols(df) if c != fac]
    rs = pick_multi("Variabel respon (≥ 2, numerik)", num, f"{k}_rs", num[:3] if num else [])
    blk = pick_optional("Blok (opsional)", [c for c in cats if c != fac], f"{k}_b")
    if len(rs) < 2:
        H["n_info"]("Pilih minimal 2 variabel respon.")
        return None
    return safe_run(de.run_manova, df, rs, fac, blk)


def f_rsm(df, a, k):
    num = num_cols(df)
    if len(num) < 3:
        H["n_warn"]("RSM memerlukan minimal 2 faktor numerik dan 1 respon.")
        return None
    resp = pick("Variabel respon", num, f"{k}_r", "Rendemen", -1)
    facs = pick_multi("Faktor (2–4, numerik)", [c for c in num if c != resp], f"{k}_f", ["Suhu", "Waktu"])
    order = st.radio("Orde model", [1, 2], index=1, horizontal=True, key=f"{k}_o",
                     format_func=lambda v: "Orde 1 (linear)" if v == 1 else "Orde 2 (kuadratik penuh)")
    with st.expander("🧱 Pembangkit matriks rancangan (CCD / Box-Behnken)"):
        c1, c2, c3 = st.columns(3)
        typ = c1.selectbox("Rancangan", ["CCD", "Box-Behnken"], key=f"{k}_gt")
        kk = c2.slider("Jumlah faktor", 2 if typ == "CCD" else 3, 5, 3, key=f"{k}_gk")
        nc = c3.slider("Titik pusat", 1, 8, 5 if typ == "CCD" else 3, key=f"{k}_gc")
        try:
            D = de.gen_ccd(kk, nc) if typ == "CCD" else de.gen_bbd(kk, nc)
            st.caption(f"{len(D)} unit percobaan, dalam satuan terkode (−1, 0, +1; CCD memuat titik aksial ±α). "
                       "Ubah ke satuan asli: nilai = pusat + kode × setengah rentang.")
            H["show_df"](D, hide_index=True)
        except ValueError as e:
            H["n_err"](str(e))
    if len(facs) < 2:
        H["n_info"]("Pilih 2 sampai 4 faktor.")
        return None
    return safe_run(de.run_rsm, df, resp, facs, order, a)


def f_mixture(df, a, k):
    num = num_cols(df)
    if len(num) < 4:
        H["n_warn"]("Rancangan campuran memerlukan minimal 3 komponen dan 1 respon (semua numerik).")
        return None
    resp = pick("Variabel respon", num, f"{k}_r", "Kekerasan", -1)
    comps = pick_multi("Komponen campuran (≥ 3; proporsi total tetap)", [c for c in num if c != resp], f"{k}_c",
                       ["Tepung", "Air", "Gula"])
    mdl = st.selectbox("Model", ["linear", "quadratic", "special_cubic"], index=1, key=f"{k}_m",
                       format_func=lambda v: {"linear": "Linear (Scheffé)", "quadratic": "Kuadratik (Scheffé)",
                                              "special_cubic": "Special cubic"}[v])
    if len(comps) < 3:
        H["n_info"]("Pilih minimal 3 komponen.")
        return None
    return safe_run(de.run_mixture, df, resp, comps, mdl)


def f_taguchi(df, a, k):
    num = num_cols(df)
    cats = all_cols(df)
    resp = pick_multi("Kolom respon/replikasi (≥ 1)", num, f"{k}_r", [c for c in num if c.startswith("Y")])
    facs = pick_multi("Faktor kontrol (kolom level)", [c for c in cats if c not in resp], f"{k}_f",
                      ["Suhu", "Tekanan", "Waktu", "Kecepatan"])
    kind = st.radio("Karakteristik kualitas", ["larger", "smaller", "nominal"], horizontal=True, key=f"{k}_k",
                    format_func=lambda v: {"larger": "Larger-the-better", "smaller": "Smaller-the-better", "nominal": "Nominal-the-best"}[v])
    if not resp or not facs:
        H["n_info"]("Pilih kolom respon dan faktor kontrol.")
        return None
    return safe_run(de.run_taguchi, df, facs, resp, kind)


def f_fracfact(df, a, k):
    num = num_cols(df)
    if len(num) < 3:
        H["n_warn"]("Faktorial pecahan memerlukan minimal 3 kolom faktor (kode −1/+1) dan 1 respon.")
        return None
    resp = pick("Variabel respon", num, f"{k}_r", "Hasil", -1)
    facs = pick_multi("Faktor (kode −1 / +1)", [c for c in num if c != resp], f"{k}_f", list("ABCDE"))
    mo = st.slider("Orde interaksi maksimum", 1, 3, 2, key=f"{k}_mo")
    with st.expander("🧱 Pembangkit rancangan faktorial pecahan"):
        c1, c2 = st.columns(2)
        base = c1.slider("Jumlah faktor dasar", 3, 6, 4, key=f"{k}_gb")
        gtxt = c2.text_input("Generator (pisahkan koma)", "E=ABCD", key=f"{k}_gg")
        try:
            D, rel, res_, rom, alias = de.gen_fracfact(base, [g.strip() for g in gtxt.split(",") if g.strip()])
            st.caption(f"Relasi pendefinisi: {', '.join(rel)} · Resolusi {rom} · {len(D)} run.")
            H["show_df"](D, hide_index=True)
            H["show_df"](alias, hide_index=True)
        except (ValueError, KeyError) as e:
            H["n_err"](str(e))
    if len(facs) < 3:
        H["n_info"]("Pilih minimal 3 faktor.")
        return None
    return safe_run(de.run_fracfact, df, resp, facs, mo)


# ============================================================================
# Penampil hasil
# ============================================================================
def _kk_text(v):
    return "sangat baik" if v < 10 else "baik" if v < 20 else "cukup" if v < 30 else "kurang baik (keragaman tinggi)"


def _letters_from_pmap(means, pmap, alpha):
    order = means.sort_values(ascending=False).index.tolist()
    return de._compact_letters(order, lambda a_, b_: pmap[(a_, b_)] >= alpha)


def render_anova_design(R, prefix, alpha, fname):
    d = R["data"]
    err = R["err"]
    H["kpis"]([("Pengamatan", R["N"])] + [(f"KK {n}", f"{v:.2f}%") for n, v in R["kk"].items()][:3]
              + [(f"{t['name']}", f"F={t['F']:.2f}, P={de.fmt_p(t['p'])}") for t in R["tests"][:2]])
    tabs = st.tabs(["📋 ANOVA", "📊 Rata-rata & Uji Lanjut", "🧪 Asumsi", "📈 Grafik", "📝 Interpretasi", "⬇️ Unduh"])
    eff_tables = {}
    with tabs[0]:
        section("Tabel Analisis Ragam")
        H["show_df"](R["anova"], hide_index=True)
        for en, e in err.items():
            st.caption(f"{en}: db = {e['df']}, KT = {e['kt']:.4f}, KK = {R['kk'][en]:.2f}%")
        meta = R.get("meta") or {}
        if meta.get("carry"):
            H["n_info"](meta["carry"])
        if meta.get("balanced") is False:
            H["n_warn"]("Rancangan tidak seimbang sempurna; perbandingan memakai rata-rata terkoreksi blok.")
        for name, v in (R.get("extra") or {}).items():
            if isinstance(v, pd.DataFrame):
                section({"nest_means": "Rata-rata tersarang", "var_comp": "Komponen ragam", "sphericity": "Uji sphericity & koreksi",
                              "wide": "Data format lebar", "adj": "Rata-rata terkoreksi kovariat"}.get(name, name))
                H["show_df"](v, hide_index=name != "wide" and True)
        ex = R.get("extra") or {}
        if "mauchly" in ex:
            m = ex["mauchly"]
            st.caption(f"Mauchly W = {m['W']:.4f}, P = {de.fmt_p(m['p'])}; ε Greenhouse-Geisser = {m['gg']:.4f}; ε Huynh-Feldt = {m['hf']:.4f}")
        if "homog" in ex:
            h_ = ex["homog"]
            st.caption(f"Kehomogenan kemiringan (interaksi perlakuan × kovariat): F = {h_['F']:.3f}, P = {de.fmt_p(h_['p'])}; slope bersama = {ex['slope']:.4f} ± {ex['slope_se']:.4f}")
    with tabs[1]:
        if not R["effects"]:
            st.info("Tidak ada efek yang dibandingkan.")
        else:
            c1, c2 = st.columns([2, 1])
            method = c1.selectbox("Uji lanjut", METHODS, index=0, key=f"{prefix}_ph")
            st.caption("BNT/LSD tidak mengendalikan galat tipe I untuk banyak pembandingan; Tukey & Scheffé lebih konservatif; "
                       "Dunnett membandingkan semua perlakuan terhadap satu kontrol.")
            for i, eff in enumerate(R["effects"]):
                st.markdown(f"##### {eff['name']}  ·  F = {eff['F']:.3f}, P = {de.fmt_p(eff['p'])} {de.sig_mark(eff['p'])}")
                means, ns = eff["means"], eff["ns"]
                custom = eff.get("custom")
                if custom:
                    st.caption(custom.get("label", "Rata-rata terkoreksi"))
                    letters = _letters_from_pmap(means, custom["pmap"], alpha)
                    pair = custom["pair_df"]
                else:
                    ctrl = None
                    if method.startswith("Dunnett"):
                        ctrl = c2.selectbox(f"Kontrol untuk {eff['name']}", list(means.index), key=f"{prefix}_ctl{i}")
                    letters, pair = posthoc_any(means, ns, eff["ktg"], eff["dbg"], alpha, method, ctrl)
                tbl = pd.DataFrame({"Level": list(means.index), "n": ns.values, "Rata-rata": means.values.round(4),
                                    "SD": eff["sd"].values.round(4) if eff.get("sd") is not None else np.nan,
                                    "Notasi": [letters.get(l, "") for l in means.index]}).sort_values("Rata-rata", ascending=False)
                H["show_df"](tbl, hide_index=True)
                eff_tables[eff["name"]] = tbl
                with st.expander(f"Perbandingan berpasangan – {eff['name']}"):
                    H["show_df"](pair, hide_index=True)
                eff_tables[f"Uji lanjut {eff['name']}"] = pair
                if not custom and eff["p"] >= alpha and not method.startswith("Dunnett"):
                    st.caption("Catatan: efek ini tidak nyata pada uji F; uji lanjut ditampilkan sebagai informasi tambahan.")
    with tabs[2]:
        resid = d["Galat"].values
        rows = []
        if 3 <= len(resid) <= 5000:
            w, p = stats.shapiro(resid)
            rows.append(["Shapiro-Wilk", "Galat menyebar normal", f"{w:.4f}", de.fmt_p(p), "Terpenuhi" if p > alpha else "Tidak terpenuhi"])
        if R["effects"]:
            f0 = R["effects"][0]["factors"]
            key = d[f0[0]] if len(f0) == 1 else d[f0].astype(str).agg("|".join, axis=1)
            groups = [resid[(key == g).values] for g in pd.unique(key)]
            groups = [g for g in groups if len(g) >= 2]
            if len(groups) >= 2:
                w, p = stats.levene(*groups, center="median")
                rows.append([f"Levene (Brown-Forsythe) menurut {R['effects'][0]['name']}", "Ragam galat homogen", f"{w:.4f}", de.fmt_p(p),
                             "Terpenuhi" if p > alpha else "Tidak terpenuhi"])
        if rows:
            H["show_df"](pd.DataFrame(rows, columns=["Uji", "H0", "Statistik", "P-value", "Kesimpulan"]), hide_index=True)
            if any(r[-1] == "Tidak terpenuhi" for r in rows):
                H["n_warn"]("Ada asumsi yang tidak terpenuhi. Pertimbangkan transformasi data (log/akar) atau uji nonparametrik.")
            else:
                H["n_ok"]("Asumsi normalitas dan homogenitas ragam galat terpenuhi.")
        else:
            st.info("Data terlalu sedikit untuk uji asumsi.")
        eff_tables["Uji asumsi"] = pd.DataFrame(rows, columns=["Uji", "H0", "Statistik", "P-value", "Kesimpulan"]) if rows else pd.DataFrame()
    with tabs[3]:
        specs = []
        for eff in R["effects"][:4]:
            means = eff["means"]
            se = np.sqrt(eff["ktg"] / eff["ns"].values.astype(float))
            specs.append({"kind": "bar", "title": f"Rata-rata {eff['name']} (± SE)", "xlabel": eff["name"], "ylabel": R["resp"],
                          "x": list(means.index), "y": list(means.values), "err": list(se), "horizontal": False})
            if len(eff["factors"]) == 2:
                f1, f2 = eff["factors"]
                g = d.groupby([f1, f2], sort=False)[R["resp"]].mean().unstack(f2)
                specs.append({"kind": "xy", "title": f"Plot interaksi {f1} × {f2}", "xlabel": f1, "ylabel": R["resp"], "hlines": [], "vlines": [],
                              "series": [{"x": [str(v) for v in g.index], "y": g[c].values, "mode": "lines+markers", "name": str(c)} for c in g.columns]})
        specs += rc.resid_specs(d["Fitted"].values, d["Galat"].values)
        draw_specs(specs, prefix)
    with tabs[4]:
        notes = []
        for t in R["tests"]:
            sg = t["p"] < alpha
            notes.append(f"**{t['name']}**: F = {t['F']:.3f}, P = {de.fmt_p(t['p'])} → " + ("berpengaruh nyata" if sg else "tidak berpengaruh nyata") + f" pada α = {alpha}.")
        for en, v in R["kk"].items():
            notes.append(f"**KK ({en}) = {v:.2f}%** → tingkat ketelitian percobaan {_kk_text(v)}.")
        inter = [t for t in R["tests"] if "×" in t["name"] or "*" in t["name"] or ":" in t["name"]]
        if any(t["p"] < alpha for t in inter):
            notes.append("Interaksi nyata: pengaruh satu faktor bergantung pada level faktor lain; tafsirkan rata-rata kombinasi, bukan efek utama saja.")
        meta = R.get("meta") or {}
        if meta.get("var_comp") is not None:
            pass
        H["note_card"]("Interpretasi otomatis", notes)
    with tabs[5]:
        sheets = {"Data": d.reset_index(drop=True), "ANOVA": R["anova"]}
        for n_, t in eff_tables.items():
            if len(t):
                sheets[n_[:28]] = t
        for name, v in (R.get("extra") or {}).items():
            if isinstance(v, pd.DataFrame):
                sheets[f"x_{name}"[:28]] = v
        H["download_excel"](sheets, fname, f"dl_{prefix}")


def render_manova(R, prefix, alpha, fname):
    H["kpis"]([("Pengamatan", R["n"]), ("Variabel respon", R["p"]), ("Level faktor", R["q"]), ("db galat", R["v"])])
    tabs = st.tabs(["📋 Uji Multivariat", "📊 Univariat & Rata-rata", "📈 Grafik", "⬇️ Unduh"])
    with tabs[0]:
        section("Uji multivariat (Pillai, Wilks, Hotelling-Lawley, Roy)")
        H["show_df"](R["multi"], hide_index=True)
        b = R["box"]
        if b:
            ok = b["p"] > 0.001
            (H["n_ok"] if ok else H["n_warn"])(f"Uji Box's M: χ² = {b['chi2']:.3f}, db = {b['df']}, P = {de.fmt_p(b['p'])} → "
                                               + ("matriks kovarians homogen." if ok else "matriks kovarians tidak homogen; Pillai's trace lebih tahan terhadap pelanggaran ini."))
        pm = R["multi"]
        sig = (pm["P-value"].astype(str).str.replace("<", "").astype(float) < alpha).any() if "P-value" in pm else False
        H["note_card"]("Interpretasi", [f"Faktor **{R['factor']}** " + ("berpengaruh nyata secara multivariat (vektor rata-rata respon berbeda antar level)."
                                                                      if sig else "tidak berpengaruh nyata secara multivariat."),
                                         "Uji univariat (tab berikutnya) menunjukkan respon mana yang berbeda; gunakan P Bonferroni untuk mengendalikan galat tipe I."])
    with tabs[1]:
        section("ANOVA univariat per respon")
        H["show_df"](R["uni"], hide_index=True)
        section("Rata-rata per level")
        H["show_df"](R["means"].reset_index(), hide_index=True)
        section("Korelasi antar respon (galat)")
        H["show_df"](R["corr"].reset_index(), hide_index=True)
    with tabs[2]:
        m = R["means"]
        specs = []
        for c in m.columns:
            specs.append({"kind": "bar", "title": f"Rata-rata {c}", "xlabel": R["factor"], "ylabel": c, "x": list(m.index), "y": list(m[c].values),
                          "err": None, "horizontal": False})
        cr = R["corr"]
        specs.append({"kind": "heat", "title": "Korelasi antar respon", "z": cr.values, "x": list(cr.columns), "y": list(cr.index), "zmid": 0})
        draw_specs(specs, prefix)
    with tabs[3]:
        H["download_excel"]({"Multivariat": R["multi"], "Univariat": R["uni"], "Rata-rata": R["means"].reset_index(),
                             "Korelasi": R["corr"].reset_index(), "Data": R["data"]}, fname, f"dl_{prefix}")


def render_rsm(R, prefix, alpha, fname):
    H["kpis"]([("R²", f"{R['r2']:.4f}"), ("R² adj", f"{R['r2a']:.4f}"), ("R² prediksi", f"{R['r2p']:.4f}"),
               ("P model", de.fmt_p(R["pm"])), ("P lack-of-fit", de.fmt_p(R["lof"]["p"]) if R.get("lof") else "-"),
               ("PRESS", f"{R['press']:.3f}")])
    tabs = st.tabs(["📋 Model", "🎯 Optimum", "📈 Kontur & Grafik", "⬇️ Unduh"])
    with tabs[0]:
        section("Koefisien (satuan terkode)")
        H["show_df"](R["coef"], hide_index=True)
        section("ANOVA model")
        H["show_df"](R["anova"], hide_index=True)
        notes = [f"Model {'kuadratik' if R['order'] == 2 else 'linear'} " + ("signifikan" if R["pm"] < alpha else "tidak signifikan") + f" (P = {de.fmt_p(R['pm'])}).",
                 f"R² = {R['r2']:.3f}, R² prediksi = {R['r2p']:.3f}" + (" (selisih dengan R² adj > 0.2 menandakan overfitting)." if R["r2a"] - R["r2p"] > 0.2 else ".")]
        if R.get("lof"):
            notes.append("Lack-of-fit " + ("nyata → model kurang tepat; coba orde lebih tinggi." if R["lof"]["p"] < alpha else "tidak nyata → model cukup tepat."))
        H["note_card"]("Interpretasi", notes)
    with tabs[1]:
        st_ = R.get("stat")
        if st_:
            kind = st_.get("kind", "")
            inside = st_.get("inside", True)
            section("Titik stasioner")
            row = {**{f: round(float(v), 4) for f, v in st_["actual"].items()}, "Respon prediksi": round(float(st_["y"]), 4), "Jenis": kind,
                   "Dalam daerah percobaan": "Ya" if inside else "Tidak"}
            H["show_df"](pd.DataFrame([row]), hide_index=True)
            if not inside:
                H["n_warn"]("Titik stasioner berada di luar daerah percobaan; ekstrapolasi tidak andal. Gunakan optimum terbatas di bawah.")
        section("Optimum dalam daerah percobaan")
        o = R["opt"]
        H["show_df"](pd.DataFrame([{"Tujuan": "Maksimum", **{k_: round(v, 4) for k_, v in o["max"].items()}},
                                   {"Tujuan": "Minimum", **{k_: round(v, 4) for k_, v in o["min"].items()}}]), hide_index=True)
    with tabs[2]:
        specs = []
        for (f1, f2), g in R["grids"].items():
            specs.append({"kind": "contour", "title": f"Kontur respon: {f1} × {f2}", "xlabel": f1, "ylabel": f2, "x": g["x"], "y": g["y"], "z": g["z"],
                          "px": g.get("px"), "py": g.get("py")})
        specs += rc.resid_specs(R["fitted"], R["resid"])
        draw_specs(specs, prefix)
    with tabs[3]:
        H["download_excel"]({"Koefisien": R["coef"], "ANOVA": R["anova"], "Data": R["data"]}, fname, f"dl_{prefix}")


def render_mixture(R, prefix, alpha, fname):
    H["kpis"]([("R²", f"{R['r2']:.4f}"), ("R² adj", f"{R['r2a']:.4f}"), ("P model", de.fmt_p(R["pm"])), ("Pengamatan", R["n"]), ("Model", R["model"])])
    tabs = st.tabs(["📋 Model", "🎯 Optimum", "📈 Grafik", "⬇️ Unduh"])
    with tabs[0]:
        section("Koefisien model Scheffé")
        H["show_df"](R["coef"], hide_index=True)
        section("ANOVA")
        H["show_df"](R["anova"], hide_index=True)
        H["note_card"]("Interpretasi", ["Model campuran tidak memiliki intersep; koefisien linear = respon prediksi komponen murni.",
                                         "Koefisien interaksi positif menunjukkan sinergi antar komponen, negatif menunjukkan antagonisme.",
                                         f"Model {'signifikan' if R['pm'] < alpha else 'tidak signifikan'} (P = {de.fmt_p(R['pm'])})."])
    with tabs[1]:
        rows = []
        for lab, key in (("Maksimum", "max"), ("Minimum", "min")):
            comp, val = R["opt"][key]
            rows.append({"Tujuan": lab, **{k_: float(v) for k_, v in comp.items()}, "Respon prediksi": round(val, 4)})
        H["show_df"](pd.DataFrame(rows), hide_index=True)
    with tabs[2]:
        specs = []
        comps, G, P = R["comps"], R["grid"], R["P"]
        if len(comps) == 3:
            specs.append({"kind": "tern", "title": "Permukaan respon prediksi (diagram segitiga)", "names": comps,
                          "a": G[:, 0], "b": G[:, 1], "c": G[:, 2], "z": R["grid_pred"],
                          "pa": P[:, 0], "pb": P[:, 1], "pc": P[:, 2]})
        else:
            specs.append({"kind": "bar", "title": "Komposisi optimum (maksimum)", "xlabel": "Komponen", "ylabel": "Proporsi",
                          "x": comps, "y": [float(R["opt"]["max"][0][c]) for c in comps], "err": None, "horizontal": False})
        specs.append({"kind": "xy", "title": "Aktual vs Prediksi", "xlabel": "Prediksi", "ylabel": "Aktual", "hlines": [], "vlines": [],
                      "series": [{"x": R["fitted"], "y": R["y"], "mode": "markers", "name": "Data"},
                                 {"x": [float(np.min(R["y"])), float(np.max(R["y"]))], "y": [float(np.min(R["y"])), float(np.max(R["y"]))],
                                  "mode": "lines", "name": "y = x", "dash": "dash"}]})
        specs += rc.resid_specs(R["fitted"], R["resid"])
        draw_specs(specs, prefix)
    with tabs[3]:
        H["download_excel"]({"Koefisien": R["coef"], "ANOVA": R["anova"], "Data": R["data"]}, fname, f"dl_{prefix}")


def render_taguchi(R, prefix, alpha, fname):
    H["kpis"]([("Run", len(R["data"])), ("Faktor", len(R["factors"])), ("Replikasi", len(R["resps"])),
               ("S/N rata-rata", f"{R['grand_sn']:.3f} dB"), ("S/N prediksi (optimum)", f"{R['pred_sn']:.3f} dB")])
    tabs = st.tabs(["📋 Respon S/N", "🎯 Kombinasi Optimum", "📈 Grafik", "⬇️ Unduh"])
    with tabs[0]:
        section("Rata-rata S/N dan respon per level")
        H["show_df"](R["table"], hide_index=True)
        section("Peringkat pengaruh faktor (delta)")
        H["show_df"](R["rank"], hide_index=True)
        section("ANOVA terhadap S/N")
        H["show_df"](R["anova"], hide_index=True)
        if R.get("pooled"):
            st.caption(R["pooled"])
    with tabs[1]:
        H["show_df"](pd.DataFrame([R["best"]]), hide_index=True)
        top = R["rank"].sort_values("Peringkat").iloc[0]["Faktor"]
        H["note_card"]("Interpretasi", [f"Level terbaik tiap faktor dipilih dari S/N tertinggi (semakin besar semakin kokoh).",
                                         f"Faktor paling berpengaruh: **{top}**.",
                                         f"S/N prediksi pada kombinasi optimum = {R['pred_sn']:.3f} dB (rata-rata keseluruhan {R['grand_sn']:.3f} dB). "
                                         "Lakukan percobaan konfirmasi pada kombinasi optimum untuk memverifikasi prediksi."])
    with tabs[2]:
        specs = []
        for f in R["factors"]:
            sub = R["table"][R["table"]["Faktor"] == f]
            specs.append({"kind": "xy", "title": f"Efek utama {f} terhadap S/N", "xlabel": f, "ylabel": "Rata-rata S/N (dB)", "hlines": [float(R["grand_sn"])], "vlines": [],
                          "series": [{"x": [str(v) for v in sub["Level"]], "y": sub["Rata-rata S/N"].values, "mode": "lines+markers", "name": "S/N"}]})
        draw_specs(specs, prefix)
    with tabs[3]:
        H["download_excel"]({"Tabel S-N": R["table"], "Peringkat": R["rank"], "ANOVA": R["anova"], "Data": R["data"]}, fname, f"dl_{prefix}")


def render_fracfact(R, prefix, alpha, fname):
    ex = R["extra"]
    H["kpis"]([("Run", R["n"]), ("Faktor", R["k"]), ("Fraksi", f"{R['fraction']:.3g} dari 2^{R['k']}"), ("Efek diduga", len(R["table"])),
               ("Mode uji", "ANOVA galat" if ex.get("mode") == "anova" else "Lenth (tanpa galat)")])
    tabs = st.tabs(["📋 Efek", "📈 Grafik", "⬇️ Unduh"])
    with tabs[0]:
        H["show_df"](R["table"], hide_index=True)
        notes = []
        if R["dropped_alias"]:
            notes.append(f"{R['dropped_alias']} efek tidak dapat dipisahkan karena beralias; efek ditulis dengan alias-nya, mis. 'A (= BCD)'.")
        if ex.get("mode") == "lenth":
            notes.append("Tidak ada derajat bebas galat; signifikansi memakai metode Lenth (PSE). Hasil bersifat eksploratif.")
        sigrows = R["table"][R["table"]["Sig."].isin(["*", "**"])]["Efek"].tolist() if "Sig." in R["table"] else []
        notes.append("Efek nyata: " + (", ".join(sigrows) if sigrows else "tidak ada") + ".")
        H["note_card"]("Interpretasi", notes)
    with tabs[1]:
        eff = R["table"].copy()
        srt = eff.reindex(eff["Nilai efek"].abs().sort_values(ascending=False).index)
        pareto = {"kind": "bar", "title": "Diagram Pareto efek (|efek|)", "xlabel": "Efek", "ylabel": "|Efek|", "x": list(srt["Efek"]),
                  "y": list(srt["Nilai efek"].abs()), "err": None, "horizontal": False}
        v = np.sort(eff["Nilai efek"].values)
        n = len(v)
        q = stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n)
        npp = {"kind": "xy", "title": "Plot peluang normal efek", "xlabel": "Kuantil normal", "ylabel": "Efek", "hlines": [], "vlines": [],
               "series": [{"x": q, "y": v, "mode": "markers", "name": "Efek"}]}
        draw_specs([pareto, npp], prefix)
        st.caption("Efek yang menjauh dari garis lurus pada plot peluang normal adalah efek yang nyata.")
    with tabs[2]:
        H["download_excel"]({"Efek": R["table"], "Data": R["data"]}, fname, f"dl_{prefix}")


def render_design(R, prefix, alpha, fname):
    k = R.get("kind")
    if k == "manova":
        render_manova(R, prefix, alpha, fname)
    elif k == "rsm":
        render_rsm(R, prefix, alpha, fname)
    elif k == "mixture":
        render_mixture(R, prefix, alpha, fname)
    elif k == "taguchi":
        render_taguchi(R, prefix, alpha, fname)
    elif k == "fracfact":
        render_fracfact(R, prefix, alpha, fname)
    else:
        render_anova_design(R, prefix, alpha, fname)


# ============================================================================
# Registri
# ============================================================================
def M(key, label, sample, form, desc, tags):
    return dict(key=key, label=label, sample=sample, form=form, desc=desc, tags=tags)


DESIGN_GROUPS = {
    "Rancangan Lingkungan": [
        M("rbsl", "Rancangan Bujur Sangkar Latin (RBSL)", "rbsl", f_latin,
          "Pengendalian dua sumber keragaman sekaligus (baris dan kolom) dengan perlakuan muncul sekali pada tiap baris dan kolom.", ["Dua arah pengelompokan", "ANOVA Latin"]),
        M("graeco", "Rancangan Graeco-Latin", "graeco", f_graeco,
          "Perluasan RBSL dengan tiga sumber pengelompokan (baris, kolom, huruf Yunani) untuk perlakuan.", ["Tiga pengelompokan"]),
        M("bib", "Blok Tidak Lengkap (BIB / Lattice)", "bib", f_bib,
          "Balanced Incomplete Block dan Lattice: rata-rata perlakuan terkoreksi blok dan uji berpasangan.", ["BIB", "Lattice", "Terkoreksi blok"]),
    ],
    "Rancangan Perlakuan": [
        M("factorial", "Percobaan Faktorial", "factorial", f_factorial,
          "Dua hingga empat faktor dengan interaksi (RAL atau RAK faktorial), plot interaksi, dan uji lanjut.", ["2–4 faktor", "Interaksi"]),
        M("fracfact", "Faktorial Pecahan (Fractional Factorial)", "fracfact", f_fracfact,
          "Faktorial 2^(k−p) dengan struktur alias, resolusi, efek utama/interaksi, dan metode Lenth.", ["2^(k−p)", "Alias", "Lenth"]),
        M("split", "Petak Terbagi (Split-Plot)", "split", f_split,
          "Dua faktor dengan ukuran satuan percobaan berbeda; galat (a) untuk petak utama dan galat (b) untuk anak petak.", ["Galat a & b"]),
        M("splitsplit", "Petak-Petak Terbagi (Split-Split-Plot)", "splitsplit", f_splitsplit,
          "Tiga faktor bertingkat dengan tiga galat percobaan.", ["Galat a, b, c"]),
        M("strip", "Petak Berjalur (Strip-Plot)", "strip", f_strip,
          "Dua faktor ditempatkan pada jalur horizontal dan vertikal yang bersilangan.", ["Galat a, b, c"]),
        M("nested", "Rancangan Tersarang (Nested)", "nested", f_nested,
          "Faktor B tersarang dalam A (mis. pohon dalam lokasi) dengan komponen ragam.", ["Komponen ragam", "Acak / tetap"]),
    ],
    "Pengukuran Berulang": [
        M("repeated", "Pengukuran Berulang (Repeated Measures)", "repeated", f_repeated,
          "ANOVA within-subject dengan uji Mauchly dan koreksi Greenhouse-Geisser / Huynh-Feldt.", ["Mauchly", "GG · HF"]),
        M("crossover", "Rancangan Cross-Over", "crossover", f_crossover,
          "Dua perlakuan bergantian antar periode pada subjek yang sama: efek perlakuan, periode, dan urutan.", ["2×2", "Periode · Urutan"]),
    ],
    "Peubah Pendamping & Multivariat": [
        M("ancova", "ANCOVA (Analisis Kovarians)", "ancova", f_ancova,
          "Membandingkan kelompok setelah mengendalikan kovariat numerik, dengan uji kehomogenan kemiringan.", ["Kovariat", "Rata-rata terkoreksi"]),
        M("manova", "MANOVA", "manova", f_manova,
          "Beberapa respon sekaligus: Pillai, Wilks, Hotelling-Lawley, Roy, uji Box's M, dan ANOVA univariat.", ["Pillai · Wilks", "Box's M"]),
    ],
    "Optimasi Proses": [
        M("rsm", "Response Surface Methodology (RSM)", "rsm", f_rsm,
          "Model kuadratik (CCD atau Box-Behnken), titik stasioner, kontur permukaan respon, dan optimum.", ["CCD · Box-Behnken", "Kontur", "Optimasi"]),
        M("mixture", "Rancangan Campuran (Mixture)", "mixture", f_mixture,
          "Komponen dengan total proporsi tetap: model Scheffé, diagram segitiga, dan komposisi optimum.", ["Scheffé", "Diagram segitiga"]),
        M("taguchi", "Metode Taguchi", "taguchi", f_taguchi,
          "Array ortogonal dengan rasio S/N, peringkat faktor, ANOVA S/N, dan kombinasi optimum.", ["S/N ratio", "Array ortogonal"]),
    ],
}
DESIGN_FLAT = {m["key"]: m for g in DESIGN_GROUPS.values() for m in g}


def run_design_page(mkey, alpha):
    from ui_core import hero_for, load_data_generic
    m = DESIGN_FLAT[mkey]
    hero_for(m["label"], m["desc"], m["tags"], alpha)
    crumb("Rancangan Percobaan", _group_of(mkey), m["label"])
    df, src = load_data_generic(de.sample_design, m["sample"], f"des_{mkey}")
    if df is None:
        return
    if src == "contoh":
        H["n_info"]("Menggunakan **data contoh**. Pilih 'Unggah file' atau 'Input manual' pada sidebar untuk data Anda sendiri.")
    with st.expander("👁️ Pratinjau data", expanded=False):
        H["show_df"](df.head(200), hide_index=True)
    with st.container(border=True):
        form_header("Pengaturan analisis")
        R = m["form"](df, alpha, f"d_{mkey}")
    if R is None:
        return
    render_design(R, f"d_{mkey}", alpha, f"hasil_{mkey}.xlsx")


def _group_of(mkey):
    for g, items in DESIGN_GROUPS.items():
        if any(i["key"] == mkey for i in items):
            return g
    return ""
