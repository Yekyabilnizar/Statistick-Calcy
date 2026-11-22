"""render.py – ubah hasil engine menjadi potongan HTML (tabel, KPI, grafik, interpretasi) dan lembar Excel."""
import html as _h
import io
import json
import re

import numpy as np
import pandas as pd
from scipy import stats

from . import core
from .registry import de, rc  # noqa: F401  (impor engine lewat registry agar sys.path terpasang)
from posthoc_ext import METHODS as PH_METHODS, posthoc_any  # noqa: E402
import stats_engine as sc  # noqa: E402
from stats_engine import f4, fmt_p  # noqa: E402,F401


# ----------------------------------------------------------------------------- tabel
def esc(x):
    return _h.escape(str(x))


def rich(text):
    t = esc(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def _fmt_cell(v):
    try:
        if pd.isna(v):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(v, (bool, np.bool_)):
        return "Ya" if v else "Tidak"
    if isinstance(v, (int, np.integer)):
        return f"{int(v):,}".replace(",", " ") if abs(int(v)) >= 100000 else str(int(v))
    if isinstance(v, (float, np.floating)):
        v = float(v)
        if v != v:
            return ""
        if v in (float("inf"), float("-inf")):
            return "∞" if v > 0 else "−∞"
        if v == int(v) and 1000 <= abs(v) < 1e6:
            return f"{int(v)}"
        if abs(v) >= 1e6 or (0 < abs(v) < 1e-4):
            return f"{v:.3e}"
        return f"{v:.4f}"
    return str(v)


def _is_numlike(col):
    if pd.api.types.is_numeric_dtype(col):
        return True
    txt = col.astype(str).str.replace("<", "", regex=False).str.strip()
    txt = txt[(txt != "") & (txt.str.lower() != "nan") & (txt != "None")]
    if txt.empty:
        return False
    return pd.to_numeric(txt, errors="coerce").notna().mean() >= 0.8


def _pill_for(col_name, text):
    t = str(text).strip()
    tl = t.lower()
    if t in ("**", "*", "tn", "ns"):
        return {"**": ("ok", "**"), "*": ("mid", "*"), "tn": ("no", "tn"), "ns": ("no", "tn")}[t]
    cl = col_name.lower()
    if "kesimpulan" in cl or "asumsi" in cl or cl in ("status", "keputusan"):
        if tl.startswith(("tidak terpenuhi", "dipertanyakan", "asumsi ph dipertanyakan")):
            return ("bad", t)
        if tl.startswith(("terpenuhi", "asumsi ph terpenuhi")):
            return ("ok", t)
        if tl.startswith("tidak"):
            return ("no", t)
        if tl.startswith("berbeda nyata") or "nyata" in tl[:12]:
            return ("ok", t)
    return None


def df_html(df, hide_index=True, max_rows=500):
    if df is None or not len(df.columns):
        return ""
    total = len(df)
    d = df.head(max_rows)
    cols = [str(c) for c in d.columns]
    right = [_is_numlike(d.iloc[:, j]) for j in range(d.shape[1])]
    kinds = []
    for c in cols:
        cl = c.lower()
        kinds.append("sig" if cl in ("sig.", "sig") else "p" if cl.startswith(("p-value", "p ", "p-")) or cl in ("p", "p bonferroni") else "")
    head = "".join(f'<th class="{"c" if kinds[j] == "sig" else "r" if right[j] else ""}">{esc(c)}</th>' for j, c in enumerate(cols))
    if not hide_index:
        head = f'<th class="idx">{esc(d.index.name or "")}</th>' + head
    rows = []
    for idx, row in zip(d.index, d.itertuples(index=False, name=None)):
        first = str(row[0]).strip().lower() if len(row) else ""
        cells = []
        for j, v in enumerate(row):
            txt = _fmt_cell(v)
            cls = []
            if right[j]:
                cls.append("r")
            if kinds[j] == "sig":
                cls.append("c")
            if j == 0 and not right[j]:
                cls.append("first")
            if kinds[j] == "p" and txt:
                try:
                    pv = float(txt.replace("<", ""))
                    cls.append("psig" if (txt.startswith("<") or pv < 0.05) else "pns")
                except ValueError:
                    pass
            pill = _pill_for(cols[j], txt) if txt else None
            inner = f'<span class="pill {pill[0]}">{esc(pill[1])}</span>' if pill else esc(txt)
            cells.append(f'<td class="{" ".join(cls)}">{inner}</td>')
        cells = "".join(cells)
        if not hide_index:
            cells = f'<th class="idx">{esc(idx)}</th>' + cells
        rows.append(f'<tr class="{"tot" if first.startswith("total") else ""}">{cells}</tr>')
    out = f'<div class="sc-wrap"><table class="sc-table"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    if total > max_rows:
        out += f'<p class="cap">Menampilkan {max_rows} dari {total} baris.</p>'
    return out


# ----------------------------------------------------------------------------- komponen
def kpis(items):
    cards = "".join(f'<div class="kpi k{i % 6}"><div class="kpi-l">{esc(l)}</div><div class="kpi-v">{esc(v)}</div></div>'
                    for i, (l, v) in enumerate(items))
    return f'<div class="kpi-grid">{cards}</div>'


def notice(msg, kind="info"):
    icon = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "⛔"}[kind]
    return f'<div class="notice {kind}"><span>{icon}</span><div>{rich(msg)}</div></div>'


def section(title):
    return f'<h3 class="sec">{esc(title)}</h3>'


def note_card(title, items):
    lis = "".join(f"<li>{rich(i)}</li>" for i in items)
    return f'<div class="card"><div class="card-title">{esc(title)}</div><ul>{lis}</ul></div>'


def eq_card(label, text):
    return f'<div class="eq"><div class="eq-l">{esc(label)}</div><div class="eq-v">{esc(text)}</div></div>'


def plots_html(specs):
    out = []
    for s in specs:
        try:
            pj = core.plot_json(s)
        except Exception:
            continue
        txt = json.dumps(pj, ensure_ascii=False).replace("<", "\\u003c")
        out.append(f'<div class="plot-box"><div class="plot"></div><script type="application/json" class="plot-data">{txt}</script></div>')
    if not out:
        return '<p class="cap">Tidak ada grafik untuk analisis ini.</p>'
    return f'<div class="plot-grid">{"".join(out)}</div>'


def tabs(items, uid):
    """items: [(judul, html)] -> blok tab yang dijalankan JavaScript."""
    nav = "".join(f'<button type="button" class="tab-btn{" on" if i == 0 else ""}" data-t="{uid}{i}">{esc(t)}</button>' for i, (t, _) in enumerate(items))
    panels = "".join(f'<div class="tab-panel{" on" if i == 0 else ""}" id="{uid}{i}">{h}</div>' for i, (_, h) in enumerate(items))
    return f'<div class="tabs"><div class="tab-nav">{nav}</div>{panels}</div>'


def _kk_text(v):
    return "sangat baik" if v < 10 else "baik" if v < 20 else "cukup" if v < 30 else "kurang baik (keragaman tinggi)"


def _letters_from_pmap(means, pmap, alpha):
    order = means.sort_values(ascending=False).index.tolist()
    return de._compact_letters(order, lambda a_, b_: pmap[(a_, b_)] >= alpha)


# ----------------------------------------------------------------------------- hasil standar (regresi)
def render_std(R, alpha):
    top = "".join(notice(w, "warning") for w in R.get("warn", []))
    top += kpis(R["kpis"])
    if R.get("eq"):
        top += eq_card("Persamaan model", R["eq"])
    res = "".join(section(n) + df_html(t) for n, t in R["tables"].items())
    sheets = {}
    for name, t in R["tables"].items():
        sheets[name[:28]] = t
    if isinstance(R.get("data"), pd.DataFrame):
        sheets["Data"] = R["data"].reset_index(drop=True)
    html = top + tabs([("📋 Hasil", res), ("📈 Grafik", plots_html(R["plots"] or [])),
                       ("📝 Interpretasi", note_card("Interpretasi otomatis", R["notes"] or ["-"]))], "t")
    return html, sheets


# ----------------------------------------------------------------------------- hasil ANOVA rancangan
def render_anova(R, alpha, method, ctrls=None):
    ctrls = ctrls or {}
    d, err = R["data"], R["err"]
    top = kpis([("Pengamatan", R["N"])] + [(f"KK {n}", f"{v:.2f}%") for n, v in R["kk"].items()][:3]
               + [(f"{t['name']}", f"F={t['F']:.2f}, P={de.fmt_p(t['p'])}") for t in R["tests"][:2]])
    eff_tables = {}
    # --- ANOVA
    a = section("Tabel Analisis Ragam") + df_html(R["anova"])
    a += "".join(f'<p class="cap">{esc(en)}: db = {e["df"]}, KT = {e["kt"]:.4f}, KK = {R["kk"][en]:.2f}%</p>' for en, e in err.items())
    meta = R.get("meta") or {}
    if meta.get("carry"):
        a += notice(meta["carry"], "info")
    if meta.get("balanced") is False:
        a += notice("Rancangan tidak seimbang sempurna; perbandingan memakai rata-rata terkoreksi blok.", "warning")
    titles = {"nest_means": "Rata-rata tersarang", "var_comp": "Komponen ragam", "sphericity": "Uji sphericity & koreksi",
              "wide": "Data format lebar", "adj": "Rata-rata terkoreksi kovariat"}
    for name, v in (R.get("extra") or {}).items():
        if isinstance(v, pd.DataFrame):
            a += section(titles.get(name, name)) + df_html(v)
    ex = R.get("extra") or {}
    if "mauchly" in ex:
        m = ex["mauchly"]
        a += f'<p class="cap">Mauchly W = {m["W"]:.4f}, P = {de.fmt_p(m["p"])}; ε Greenhouse-Geisser = {m["gg"]:.4f}; ε Huynh-Feldt = {m["hf"]:.4f}</p>'
    if "homog" in ex:
        h_ = ex["homog"]
        a += (f'<p class="cap">Kehomogenan kemiringan (interaksi perlakuan × kovariat): F = {h_["F"]:.3f}, P = {de.fmt_p(h_["p"])}; '
              f'slope bersama = {ex["slope"]:.4f} ± {ex["slope_se"]:.4f}</p>')
    # --- rata-rata & uji lanjut
    if not R["effects"]:
        b = '<p class="cap">Tidak ada efek yang dibandingkan.</p>'
    else:
        b = f'<p class="cap">Uji lanjut: <b>{esc(method)}</b>. BNT/LSD tidak mengendalikan galat tipe I pada banyak pembandingan; Tukey dan Scheffé lebih konservatif.</p>'
        for eff in R["effects"]:
            b += f'<h4 class="eff">{esc(eff["name"])} · F = {eff["F"]:.3f}, P = {de.fmt_p(eff["p"])} {de.sig_mark(eff["p"])}</h4>'
            means, ns = eff["means"], eff["ns"]
            custom = eff.get("custom")
            if custom:
                b += f'<p class="cap">{esc(custom.get("label", "Rata-rata terkoreksi"))}</p>'
                letters = _letters_from_pmap(means, custom["pmap"], alpha)
                pair = custom["pair_df"]
            else:
                ctrl = None
                if method.startswith("Dunnett"):
                    ctrl = ctrls.get(eff["name"]) if ctrls.get(eff["name"]) in list(means.index) else list(means.index)[0]
                    b += ctrl_select(eff["name"], list(means.index), ctrl)
                letters, pair = posthoc_any(means, ns, eff["ktg"], eff["dbg"], alpha, method, ctrl)
            tbl = pd.DataFrame({"Level": list(means.index), "n": ns.values, "Rata-rata": means.values.round(4),
                                "SD": eff["sd"].values.round(4) if eff.get("sd") is not None else np.nan,
                                "Notasi": [letters.get(l, "") for l in means.index]}).sort_values("Rata-rata", ascending=False)
            b += df_html(tbl)
            eff_tables[eff["name"]] = tbl
            b += f'<details class="more"><summary>Perbandingan berpasangan – {esc(eff["name"])}</summary>{df_html(pair)}</details>'
            eff_tables[f"Uji lanjut {eff['name']}"] = pair
            if not custom and eff["p"] >= alpha and not method.startswith("Dunnett"):
                b += '<p class="cap">Catatan: efek ini tidak nyata pada uji F; uji lanjut ditampilkan sebagai informasi tambahan.</p>'
    # --- asumsi
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
    cols_as = ["Uji", "H0", "Statistik", "P-value", "Kesimpulan"]
    if rows:
        c = df_html(pd.DataFrame(rows, columns=cols_as))
        if any(r[-1] == "Tidak terpenuhi" for r in rows):
            c += notice("Ada asumsi yang tidak terpenuhi. Pertimbangkan transformasi data (log/akar) atau uji nonparametrik.", "warning")
        else:
            c += notice("Asumsi normalitas dan homogenitas ragam galat terpenuhi.", "success")
    else:
        c = '<p class="cap">Data terlalu sedikit untuk uji asumsi.</p>'
    eff_tables["Uji asumsi"] = pd.DataFrame(rows, columns=cols_as) if rows else pd.DataFrame()
    # --- grafik
    specs = []
    for eff in R["effects"][:4]:
        means = eff["means"]
        se_ = np.sqrt(eff["ktg"] / eff["ns"].values.astype(float))
        specs.append({"kind": "bar", "title": f"Rata-rata {eff['name']} (± SE)", "xlabel": eff["name"], "ylabel": R["resp"],
                      "x": list(means.index), "y": list(means.values), "err": list(se_), "horizontal": False})
        if len(eff["factors"]) == 2:
            f1, f2 = eff["factors"]
            g = d.groupby([f1, f2], sort=False)[R["resp"]].mean().unstack(f2)
            specs.append({"kind": "xy", "title": f"Plot interaksi {f1} × {f2}", "xlabel": f1, "ylabel": R["resp"], "hlines": [], "vlines": [],
                          "series": [{"x": [str(v) for v in g.index], "y": g[c_].values, "mode": "lines+markers", "name": str(c_)} for c_ in g.columns]})
    specs += rc.resid_specs(d["Fitted"].values, d["Galat"].values)
    # --- interpretasi
    notes = []
    for t in R["tests"]:
        sg = t["p"] < alpha
        notes.append(f"**{t['name']}**: F = {t['F']:.3f}, P = {de.fmt_p(t['p'])} → " + ("berpengaruh nyata" if sg else "tidak berpengaruh nyata") + f" pada α = {alpha}.")
    for en, v in R["kk"].items():
        notes.append(f"**KK ({en}) = {v:.2f}%** → tingkat ketelitian percobaan {_kk_text(v)}.")
    inter = [t for t in R["tests"] if "×" in t["name"] or "*" in t["name"] or ":" in t["name"]]
    if any(t["p"] < alpha for t in inter):
        notes.append("Interaksi nyata: pengaruh satu faktor bergantung pada level faktor lain; tafsirkan rata-rata kombinasi, bukan efek utama saja.")
    html = top + tabs([("📋 ANOVA", a), ("📊 Rata-rata & Uji Lanjut", b), ("🧪 Asumsi", c), ("📈 Grafik", plots_html(specs)),
                       ("📝 Interpretasi", note_card("Interpretasi otomatis", notes))], "t")
    sheets = {"Data": d.reset_index(drop=True), "ANOVA": R["anova"]}
    for n_, t in eff_tables.items():
        if len(t):
            sheets[n_[:28]] = t
    for name, v in (R.get("extra") or {}).items():
        if isinstance(v, pd.DataFrame):
            sheets[f"x_{name}"[:28]] = v
    return html, sheets


def opt_select(label, name, options, cur, attr="data-opt"):
    ops = "".join(f'<option value="{esc(o)}"{" selected" if str(o) == str(cur) else ""}>{esc(o)}</option>' for o in options)
    return f'<label class="optl">{esc(label)}<select {attr}="{esc(name)}">{ops}</select></label>'


def ctrl_select(eff_name, levels, cur):
    return f'<div class="optbar">{opt_select(f"Kontrol untuk {eff_name}", eff_name, levels, cur, "data-opt-ctrl")}</div>'


def ph_bar(method):
    return ('<div class="optbar">' + opt_select("Uji lanjut", "ph", PH_METHODS, method) +
            '<span class="cap" style="margin:0">BNT/LSD tidak mengendalikan galat tipe I pada banyak pembandingan; Tukey &amp; Scheffé lebih konservatif; '
            'Dunnett membandingkan semua perlakuan terhadap satu kontrol. Mengganti uji lanjut langsung menghitung ulang hasil.</span></div>')


def render(kind, R, alpha, params, opts=None):
    opts = opts or {}
    method = opts.get("ph") if opts.get("ph") in PH_METHODS else PH_METHODS[0]
    ctrls = opts.get("ctrl") if isinstance(opts.get("ctrl"), dict) else {}
    if kind == "anova":
        html, sheets = render_anova(R, alpha, method, ctrls)
        return (ph_bar(method) if R.get("effects") else "") + html, sheets
    if kind == "legacy":
        return render_legacy(R, alpha, method, ctrls, opts.get("err") if opts.get("err") in ("SD", "SE") else "SD")
    fn = {"manova": render_manova, "rsm": render_rsm, "mixture": render_mixture, "taguchi": render_taguchi,
          "fracfact": render_fracfact, "reg0": render_reg0}.get(kind)
    return fn(R, alpha) if fn else render_std(R, alpha)


def to_xlsx(sheets):
    from openpyxl import Workbook
    wb = Workbook()
    wb.remove(wb.active)
    used = set()
    for name, df in sheets.items():
        nm = re.sub(r"[\\/*?:\[\]]", "_", str(name))[:31] or "Sheet"
        base, i = nm, 2
        while nm in used:
            nm = f"{base[:28]}_{i}"
            i += 1
        used.add(nm)
        ws = wb.create_sheet(nm)
        ws.append([str(c) for c in df.columns])
        for row in df.itertuples(index=False, name=None):
            ws.append([None if (isinstance(v, float) and not np.isfinite(v)) else (v.item() if hasattr(v, "item") else v) for v in row])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ============================================================================ RAL / RAK (halaman dasar)
def _sidx(df):
    d = df.copy()
    d.index = d.index.astype(str)
    return d


def render_legacy(R, alpha, method, ctrls, err_type):
    kind, resp, trt, blk = R["kind"], R["resp"], R["trt"], R.get("blk")
    d, levels = R["data"], R["levels"]
    nm = "RAL" if kind == "ral" else "RAK"
    ctrl = None
    if method.startswith("Dunnett"):
        ctrl = ctrls.get(trt) if ctrls.get(trt) in levels else levels[0]
    letters, pair_df = posthoc_any(R["means"], R["ns"], R["ktg"], R["dbg"], alpha, method, ctrl)
    short = method.split(" ")[0]
    assump = sc.anova_assumptions(R, alpha)
    desc = pd.DataFrame({trt: levels, "n": R["ns"].values, "Rata-rata": R["means"].values.round(4), "SD": R["sd"].values.round(4),
                         "SE": (R["sd"] / np.sqrt(R["ns"])).values.round(4), "Min": R["min"].values, "Maks": R["max"].values,
                         f"Notasi {short}": [letters.get(l, "") for l in levels]})
    cols = [c for c in [trt, blk, resp] if c]
    # --- Data
    a = ""
    if R.get("dropped"):
        a += notice(f"{R['dropped']} baris dengan nilai kosong/non-angka dikeluarkan dari analisis.", "warning")
    a += section("Data yang dianalisis") + df_html(d[cols].reset_index(drop=True))
    if kind == "rak":
        tbl = R["matrix"].copy()
        tbl["Total kelompok"] = tbl.sum(axis=1)
        tot = tbl.sum(axis=0).to_frame("Total perlakuan").T
        two = pd.concat([tbl, tot]).round(4)
        two.index.name = "Kelompok"
        a += section("Tabel dua arah (Kelompok × Perlakuan)") + df_html(two.reset_index())
    # --- Ringkasan
    t0 = R["tests"][0]
    b = kpis([("Jumlah perlakuan", R["t"]), ("Ulangan (r)", f"{R['r']:.0f}" if float(R["r"]).is_integer() else f"{R['r']:.2f}"),
              ("F hitung (perlakuan)", f"{t0['F']:.3f}"), ("P-value", fmt_p(t0["p"])), ("KK (%)", f"{R['kk']:.2f}"), ("Rata-rata umum", f"{R['grand']:.3f}")])
    items = []
    for t in R["tests"]:
        ok = t["p"] < alpha
        subj = "perlakuan" if t["name"] == "Perlakuan" else "pengelompokan"
        kal = (f"H₀ ditolak. Terdapat pengaruh **nyata** {subj} terhadap {resp}." if ok
               else f"H₀ gagal ditolak. Tidak terdapat pengaruh nyata {subj} terhadap {resp}.")
        items.append(f"**{t['name']}:** F = {t['F']:.3f}, P-value = {fmt_p(t['p'])} {'<' if ok else '≥'} α ({alpha}). {kal}")
    items.append(f"**Koefisien keragaman (KK)** = {R['kk']:.2f}%.")
    if kind == "rak":
        er = R["extra"]["ER"]
        items.append(f"**Efisiensi relatif RAK terhadap RAL** = {er:.2f}. " + ("RAK lebih efisien daripada RAL (pengelompokan efektif)." if er > 1 else "Pengelompokan tidak meningkatkan efisiensi."))
    b += note_card("📝 Interpretasi", items)
    if t0["p"] < alpha:
        best = max(levels, key=lambda l: R["means"][l])
        b += notice(f"Uji lanjut {method} pada taraf {alpha}: rata-rata tertinggi pada **{best}** ({R['means'][best]:.3f}, notasi '{letters.get(best, '')}').", "success")
    else:
        b += notice("Perlakuan tidak berpengaruh nyata, sehingga uji lanjut sebenarnya tidak diperlukan (hasilnya ditampilkan hanya sebagai informasi).", "info")
    if ctrl is not None:
        b += ctrl_select(trt, levels, ctrl)
    b += '<p class="mini"><b>Rata-rata perlakuan:</b></p>' + df_html(desc)
    b += f'<p class="cap">Rata-rata yang diikuti huruf yang sama tidak berbeda nyata pada taraf {alpha} menurut uji {esc(method)}.</p>'
    # --- Tabel
    pred = d[cols + ["Fitted", "Galat"]].round(4).reset_index(drop=True)
    c = section(f"Tabel Sidik Ragam (ANOVA) – {nm}") + df_html(R["anova"]) + '<p class="cap">Sig.: ** sangat nyata (P&lt;0,01), * nyata (P&lt;0,05), tn tidak nyata.</p>'
    c += section("Statistik Deskriptif & Notasi Uji Lanjut") + df_html(desc)
    c += section(f"Perbandingan Berpasangan – {method}") + df_html(pair_df) + section("Nilai Prediksi dan Galat") + df_html(pred)
    # --- Visualisasi
    err = desc["SD" if err_type == "SD" else "SE"].fillna(0).values
    top = float((R["means"].values + err).max())
    specs = [{"kind": "box", "title": f"Boxplot {resp} per {trt}", "xlabel": trt, "ylabel": resp,
              "groups": {lv: d.loc[d[trt] == lv, resp].values for lv in levels}},
             {"kind": "bar", "title": f"Rata-rata ± {err_type} dengan notasi {short}", "xlabel": trt, "ylabel": resp, "x": levels,
              "y": list(R["means"].values), "err": list(err), "horizontal": False, "text": [letters.get(l, "") for l in levels], "ylim": [0, top * 1.12]}]
    if kind == "rak":
        M_ = R["matrix"]
        specs.append({"kind": "xy", "title": "Plot Interaksi (garis per kelompok)", "xlabel": trt, "ylabel": resp, "hlines": [], "vlines": [],
                      "series": [{"x": levels, "y": M_.loc[bk].values, "mode": "lines+markers", "name": str(bk)} for bk in M_.index]})
        specs.append({"kind": "heat", "title": "Heatmap Kelompok × Perlakuan", "z": M_.values, "x": list(M_.columns), "y": list(M_.index), "zmid": None})
    specs += rc.resid_specs(d["Fitted"].values, d["Galat"].values)
    v = ('<div class="optbar">' + opt_select("Batang galat (error bar)", "err", ["SD", "SE"], err_type) + "</div>") + plots_html(specs)
    # --- asumsi
    e = df_html(assump) + f'<p class="cap">Pada taraf α = {alpha}: P-value &gt; α berarti asumsi terpenuhi. Lihat juga Q-Q plot dan plot galat pada tab Grafik.</p>'
    if (assump["Kesimpulan"] == "Tidak terpenuhi").any():
        e += notice("Ada asumsi yang tidak terpenuhi. Pertimbangkan transformasi data (log/akar) atau uji nonparametrik (Kruskal-Wallis untuk RAL, Friedman untuk RAK).", "warning")
    html = ph_bar(method) + tabs([("📋 Data", a), ("📊 Ringkasan", b), ("📑 Tabel", c), ("📈 Grafik", v), ("✅ Uji Asumsi", e)], "t")
    sheets = {"Data": d[cols].reset_index(drop=True), "ANOVA": R["anova"], "Rata-rata & Notasi": desc, "Uji Lanjut": pair_df,
              "Uji Asumsi": assump, "Prediksi & Galat": pred}
    return html, sheets


# ============================================================================ Regresi linear (halaman dasar)
def render_reg0(R, alpha):
    d, xs, y, k, n, names = R["data"], R["xs"], R["y"], R["k"], R["n"], R["names"]
    intercept = R["intercept"]
    # --- Data
    a = ""
    if R["n_dropped"]:
        a += notice(f"{R['n_dropped']} baris dengan nilai kosong/non-angka dikeluarkan dari analisis.", "warning")
    a += section("Data yang dianalisis") + df_html(d.reset_index(drop=True)) + f'<p class="cap">n = {n} pengamatan lengkap</p>'
    desc = d.describe().T.round(4)
    desc.insert(0, "Variabel", desc.index)
    a += section("Statistik deskriptif") + df_html(desc.reset_index(drop=True))
    # --- Ringkasan
    sig_model = R["pF"] < alpha
    b = section("Ringkasan Model Regresi") + eq_card("Persamaan regresi", R["equation"])
    b += kpis([("n", n), ("R²", f"{R['r2']:.4f}"), ("R² Adjusted", f"{R['r2a']:.4f}"), ("F hitung", f"{R['F']:.3f}"),
               ("P-value (F)", fmt_p(R["pF"])), ("RMSE", f"{R['rmse']:.4f}")])
    items = [f"**Uji simultan (Uji F):** F = {R['F']:.3f}, P-value = {fmt_p(R['pF'])} {'<' if sig_model else '≥'} α ({alpha}). Model regresi "
             f"**{'signifikan' if sig_model else 'tidak signifikan'}**, artinya "
             + (f"minimal satu variabel X berpengaruh nyata terhadap {y}." if sig_model else f"belum ada bukti bahwa variabel X berpengaruh terhadap {y}."),
             f"**Koefisien determinasi:** R² = {R['r2']:.4f}, sehingga {R['r2'] * 100:.2f}% keragaman {y} dapat dijelaskan oleh {', '.join(xs)}."]
    off = 1 if intercept else 0
    for i, nm_ in enumerate(xs):
        b_, p_ = R["beta"][i + off], R["pvals"][i + off]
        arah = "naik" if b_ > 0 else "turun"
        items.append(f"**{nm_}**: berpengaruh nyata (P = {fmt_p(p_)}). Setiap kenaikan 1 satuan {nm_} membuat {y} {arah} sebesar {abs(b_):.4f} satuan (variabel lain tetap)."
                     if p_ < alpha else f"**{nm_}**: tidak berpengaruh nyata (P = {fmt_p(p_)}).")
    b += note_card("📝 Interpretasi", items)
    if not intercept:
        b += notice("Model tanpa intersep: R² dihitung terhadap total JK tak terpusat sehingga tidak sebanding dengan model berintersep.", "info")
    lines = [f"Variabel dependen : {y}", f"n                 : {n}", f"R-squared         : {R['r2']:.4f}   Adj. R-squared: {R['r2a']:.4f}",
             f"F-statistic       : {R['F']:.3f}   Prob (F): {fmt_p(R['pF'])}", "", "{:<22}{:>12}{:>12}{:>10}{:>10}".format("Variabel", "Koef.", "Std.Err", "t", "P")]
    for i, nm_ in enumerate(names):
        c = R["coef"].iloc[i]
        lines.append("{:<22}{:>12.4f}{:>12.4f}{:>10.3f}{:>10}".format(str(nm_)[:21], c["Koefisien (B)"], c["Std. Error"], c["t hitung"], c["P-value"]))
    b += f'<details class="more"><summary>Tampilkan ringkasan lengkap (teks)</summary><pre class="sc-pre">{esc(chr(10).join(lines))}</pre></details>'
    # --- Tabel
    c = section("Tabel Koefisien Regresi") + df_html(R["coef"]) + '<p class="cap">Sig.: ** sangat nyata (P&lt;0,01), * nyata (P&lt;0,05), tn tidak nyata.</p>'
    c += section("Tabel ANOVA Regresi") + df_html(R["anova"])
    corr = d.corr().round(4)
    corr.insert(0, "Variabel", corr.index)
    c += section("Matriks Korelasi (Pearson)") + df_html(corr.reset_index(drop=True))
    c += section("Nilai Aktual, Prediksi, dan Galat") + df_html(R["pred_table"].reset_index(drop=True))
    # --- Grafik
    specs = []
    if k == 1:
        x = xs[0]
        xr = np.linspace(d[x].min(), d[x].max(), 100)
        Xn = np.column_stack([np.ones(100), xr]) if intercept else xr[:, None]
        pm = Xn @ R["beta"]
        sem = np.sqrt(np.clip(np.einsum("ij,jk,ik->i", Xn, R["s2"] * R["XtXi"], Xn), 0, None))
        cl = int((1 - alpha) * 100)
        specs.append({"kind": "xy", "title": f"Diagram Pencar & Garis Regresi ({y} ~ {x})", "xlabel": x, "ylabel": y, "hlines": [], "vlines": [],
                      "band": {"x": xr, "lo": pm - R["tcrit"] * sem, "hi": pm + R["tcrit"] * sem, "name": f"CI {cl}%"},
                      "series": [{"x": d[x].values, "y": d[y].values, "mode": "markers", "name": "Data"},
                                 {"x": xr, "y": pm, "mode": "lines", "name": "Garis regresi"}]})
    else:
        mn, mx = float(min(d[y].min(), R["fitted"].min())), float(max(d[y].max(), R["fitted"].max()))
        specs.append({"kind": "xy", "title": "Nilai Aktual vs Prediksi", "xlabel": "Prediksi", "ylabel": "Aktual", "hlines": [], "vlines": [],
                      "series": [{"x": R["fitted"], "y": d[y].values, "mode": "markers", "name": "Data"},
                                 {"x": [mn, mx], "y": [mn, mx], "mode": "lines", "name": "y = x", "dash": "dash"}]})
    specs += rc.resid_specs(R["fitted"], R["resid"])
    specs.append({"kind": "bar", "title": "Jarak Cook (Pengamatan Berpengaruh)", "xlabel": "Pengamatan", "ylabel": "Cook's D",
                  "x": [str(i) for i in d.index], "y": list(R["cooks"]), "err": None, "horizontal": False, "hlines": [4 / n]})
    specs.append({"kind": "heat", "title": "Heatmap Korelasi", "z": d.corr().values, "x": list(d.columns), "y": list(d.columns), "zmid": 0})
    if k >= 2 and k + 1 <= 6:
        specs.append({"kind": "splom", "title": "Matriks Diagram Pencar", "dims": {c_: d[c_].values for c_ in d.columns}})
    # --- Asumsi
    e = section("Uji Asumsi Klasik") + df_html(R["assump"]) + f'<p class="cap">Pada taraf α = {alpha}: P-value &gt; α berarti asumsi terpenuhi.</p>'
    if R["vif"] is not None:
        e += section("Uji Multikolinearitas (VIF)") + df_html(R["vif"])
    # --- Prediksi
    cfg = {"y": y, "xs": xs, "intercept": intercept, "beta": [float(v) for v in R["beta"]], "cov": [[float(v) for v in r] for r in (R["s2"] * R["XtXi"])],
           "s2": float(R["s2"]), "tcrit": R["tcrit"], "alpha": alpha,
           "mean": [round(float(d[x].mean()), 4) for x in xs], "min": [float(d[x].min()) for x in xs], "max": [float(d[x].max()) for x in xs]}
    pj = json.dumps(cfg, ensure_ascii=False).replace("<", "\\u003c")
    f = (section("Kalkulator Prediksi") + '<p class="cap">Masukkan nilai variabel X untuk memprediksi Y.</p>'
         f'<div class="predictor" data-cfg="{esc(pj)}"></div>')
    html = tabs([("📋 Data", a), ("📊 Ringkasan", b), ("📑 Tabel", c), ("📈 Grafik", plots_html(specs)), ("✅ Uji Asumsi", e), ("🔮 Prediksi", f)], "t")
    sheets = {"Data": d.reset_index(drop=True), "Koefisien": R["coef"], "ANOVA": R["anova"], "Uji Asumsi": R["assump"],
              "Prediksi & Galat": R["pred_table"].reset_index(drop=True)}
    if R["vif"] is not None:
        sheets["VIF"] = R["vif"]
    return html, sheets


# ============================================================================ rancangan lanjutan
def render_manova(R, alpha):
    top = kpis([("Pengamatan", R["n"]), ("Variabel respon", R["p"]), ("Level faktor", R["q"]), ("db galat", R["v"])])
    a = section("Uji multivariat (Pillai, Wilks, Hotelling-Lawley, Roy)") + df_html(R["multi"])
    bx = R["box"]
    if bx:
        ok = bx["p"] > 0.001
        a += notice(f"Uji Box's M: χ² = {bx['chi2']:.3f}, db = {bx['df']}, P = {de.fmt_p(bx['p'])} → "
                    + ("matriks kovarians homogen." if ok else "matriks kovarians tidak homogen; Pillai's trace lebih tahan terhadap pelanggaran ini."), "success" if ok else "warning")
    pm = R["multi"]
    sig = (pm["P-value"].astype(str).str.replace("<", "").astype(float) < alpha).any() if "P-value" in pm else False
    a += note_card("Interpretasi", [f"Faktor **{R['factor']}** " + ("berpengaruh nyata secara multivariat (vektor rata-rata respon berbeda antar level)." if sig else "tidak berpengaruh nyata secara multivariat."),
                                    "Uji univariat (tab berikutnya) menunjukkan respon mana yang berbeda; gunakan P Bonferroni untuk mengendalikan galat tipe I."])
    b = (section("ANOVA univariat per respon") + df_html(R["uni"]) + section("Rata-rata per level") + df_html(R["means"].reset_index())
         + section("Korelasi antar respon (galat)") + df_html(R["corr"].reset_index()))
    m = R["means"]
    specs = [{"kind": "bar", "title": f"Rata-rata {c_}", "xlabel": R["factor"], "ylabel": c_, "x": list(m.index), "y": list(m[c_].values), "err": None, "horizontal": False} for c_ in m.columns]
    cr = R["corr"]
    specs.append({"kind": "heat", "title": "Korelasi antar respon", "z": cr.values, "x": list(cr.columns), "y": list(cr.index), "zmid": 0})
    sheets = {"Multivariat": R["multi"], "Univariat": R["uni"], "Rata-rata": R["means"].reset_index(), "Korelasi": R["corr"].reset_index(), "Data": R["data"]}
    return top + tabs([("📋 Uji Multivariat", a), ("📊 Univariat & Rata-rata", b), ("📈 Grafik", plots_html(specs))], "t"), sheets


def render_rsm(R, alpha):
    top = kpis([("R²", f"{R['r2']:.4f}"), ("R² adj", f"{R['r2a']:.4f}"), ("R² prediksi", f"{R['r2p']:.4f}"), ("P model", de.fmt_p(R["pm"])),
                ("P lack-of-fit", de.fmt_p(R["lof"]["p"]) if R.get("lof") else "-"), ("PRESS", f"{R['press']:.3f}")])
    a = section("Koefisien (satuan terkode)") + df_html(R["coef"]) + section("ANOVA model") + df_html(R["anova"])
    notes = [f"Model {'kuadratik' if R['order'] == 2 else 'linear'} " + ("signifikan" if R["pm"] < alpha else "tidak signifikan") + f" (P = {de.fmt_p(R['pm'])}).",
             f"R² = {R['r2']:.3f}, R² prediksi = {R['r2p']:.3f}" + (" (selisih dengan R² adj > 0.2 menandakan overfitting)." if R["r2a"] - R["r2p"] > 0.2 else ".")]
    if R.get("lof"):
        notes.append("Lack-of-fit " + ("nyata → model kurang tepat; coba orde lebih tinggi." if R["lof"]["p"] < alpha else "tidak nyata → model cukup tepat."))
    a += note_card("Interpretasi", notes)
    b = ""
    st_ = R.get("stat")
    if st_:
        inside = st_.get("inside", True)
        row = {**{f_: round(float(v), 4) for f_, v in st_["actual"].items()}, "Respon prediksi": round(float(st_["y"]), 4), "Jenis": st_.get("kind", ""),
               "Dalam daerah percobaan": "Ya" if inside else "Tidak"}
        b += section("Titik stasioner") + df_html(pd.DataFrame([row]))
        if not inside:
            b += notice("Titik stasioner berada di luar daerah percobaan; ekstrapolasi tidak andal. Gunakan optimum terbatas di bawah.", "warning")
    o = R["opt"]
    b += section("Optimum dalam daerah percobaan") + df_html(pd.DataFrame([{"Tujuan": "Maksimum", **{k_: round(v, 4) for k_, v in o["max"].items()}},
                                                                            {"Tujuan": "Minimum", **{k_: round(v, 4) for k_, v in o["min"].items()}}]))
    specs = [{"kind": "contour", "title": f"Kontur respon: {f1} × {f2}", "xlabel": f1, "ylabel": f2, "x": g["x"], "y": g["y"], "z": g["z"], "px": g.get("px"), "py": g.get("py")}
             for (f1, f2), g in R["grids"].items()]
    specs += rc.resid_specs(R["fitted"], R["resid"])
    sheets = {"Koefisien": R["coef"], "ANOVA": R["anova"], "Data": R["data"]}
    return top + tabs([("📋 Model", a), ("🎯 Optimum", b), ("📈 Kontur & Grafik", plots_html(specs))], "t"), sheets


def render_mixture(R, alpha):
    top = kpis([("R²", f"{R['r2']:.4f}"), ("R² adj", f"{R['r2a']:.4f}"), ("P model", de.fmt_p(R["pm"])), ("Pengamatan", R["n"]), ("Model", R["model"])])
    a = section("Koefisien model Scheffé") + df_html(R["coef"]) + section("ANOVA") + df_html(R["anova"])
    a += note_card("Interpretasi", ["Model campuran tidak memiliki intersep; koefisien linear = respon prediksi komponen murni.",
                                    "Koefisien interaksi positif menunjukkan sinergi antar komponen, negatif menunjukkan antagonisme.",
                                    f"Model {'signifikan' if R['pm'] < alpha else 'tidak signifikan'} (P = {de.fmt_p(R['pm'])})."])
    rows = []
    for lab, key in (("Maksimum", "max"), ("Minimum", "min")):
        comp, val = R["opt"][key]
        rows.append({"Tujuan": lab, **{k_: float(v) for k_, v in comp.items()}, "Respon prediksi": round(val, 4)})
    b = df_html(pd.DataFrame(rows))
    comps, G, P = R["comps"], R["grid"], R["P"]
    specs = []
    if len(comps) == 3:
        specs.append({"kind": "tern", "title": "Permukaan respon prediksi (diagram segitiga)", "names": comps, "a": G[:, 0], "b": G[:, 1], "c": G[:, 2],
                      "z": R["grid_pred"], "pa": P[:, 0], "pb": P[:, 1], "pc": P[:, 2]})
    else:
        specs.append({"kind": "bar", "title": "Komposisi optimum (maksimum)", "xlabel": "Komponen", "ylabel": "Proporsi", "x": comps,
                      "y": [float(R["opt"]["max"][0][c_]) for c_ in comps], "err": None, "horizontal": False})
    lo_, hi_ = float(np.min(R["y"])), float(np.max(R["y"]))
    specs.append({"kind": "xy", "title": "Aktual vs Prediksi", "xlabel": "Prediksi", "ylabel": "Aktual", "hlines": [], "vlines": [],
                  "series": [{"x": R["fitted"], "y": R["y"], "mode": "markers", "name": "Data"}, {"x": [lo_, hi_], "y": [lo_, hi_], "mode": "lines", "name": "y = x", "dash": "dash"}]})
    specs += rc.resid_specs(R["fitted"], R["resid"])
    sheets = {"Koefisien": R["coef"], "ANOVA": R["anova"], "Data": R["data"]}
    return top + tabs([("📋 Model", a), ("🎯 Optimum", b), ("📈 Grafik", plots_html(specs))], "t"), sheets


def render_taguchi(R, alpha):
    top = kpis([("Run", len(R["data"])), ("Faktor", len(R["factors"])), ("Replikasi", len(R["resps"])), ("S/N rata-rata", f"{R['grand_sn']:.3f} dB"),
                ("S/N prediksi (optimum)", f"{R['pred_sn']:.3f} dB")])
    a = (section("Rata-rata S/N dan respon per level") + df_html(R["table"]) + section("Peringkat pengaruh faktor (delta)") + df_html(R["rank"])
         + section("ANOVA terhadap S/N") + df_html(R["anova"]))
    if R.get("pooled"):
        a += f'<p class="cap">{esc(R["pooled"])}</p>'
    tp = R["rank"].sort_values("Peringkat").iloc[0]["Faktor"]
    b = df_html(pd.DataFrame([R["best"]])) + note_card("Interpretasi", [
        "Level terbaik tiap faktor dipilih dari S/N tertinggi (semakin besar semakin kokoh).", f"Faktor paling berpengaruh: **{tp}**.",
        f"S/N prediksi pada kombinasi optimum = {R['pred_sn']:.3f} dB (rata-rata keseluruhan {R['grand_sn']:.3f} dB). Lakukan percobaan konfirmasi pada kombinasi optimum untuk memverifikasi prediksi."])
    specs = []
    for f_ in R["factors"]:
        sub = R["table"][R["table"]["Faktor"] == f_]
        specs.append({"kind": "xy", "title": f"Efek utama {f_} terhadap S/N", "xlabel": f_, "ylabel": "Rata-rata S/N (dB)", "hlines": [float(R["grand_sn"])], "vlines": [],
                      "series": [{"x": [str(v) for v in sub["Level"]], "y": sub["Rata-rata S/N"].values, "mode": "lines+markers", "name": "S/N"}]})
    sheets = {"Tabel S-N": R["table"], "Peringkat": R["rank"], "ANOVA": R["anova"], "Data": R["data"]}
    return top + tabs([("📋 Respon S/N", a), ("🎯 Kombinasi Optimum", b), ("📈 Grafik", plots_html(specs))], "t"), sheets


def render_fracfact(R, alpha):
    ex = R["extra"]
    top = kpis([("Run", R["n"]), ("Faktor", R["k"]), ("Fraksi", f"{R['fraction']:.3g} dari 2^{R['k']}"), ("Efek diduga", len(R["table"])),
                ("Mode uji", "ANOVA galat" if ex.get("mode") == "anova" else "Lenth (tanpa galat)")])
    a = df_html(R["table"])
    notes = []
    if R["dropped_alias"]:
        notes.append(f"{R['dropped_alias']} efek tidak dapat dipisahkan karena beralias; efek ditulis dengan alias-nya, mis. 'A (= BCD)'.")
    if ex.get("mode") == "lenth":
        notes.append("Tidak ada derajat bebas galat; signifikansi memakai metode Lenth (PSE). Hasil bersifat eksploratif.")
    sigrows = R["table"][R["table"]["Sig."].isin(["*", "**"])]["Efek"].tolist() if "Sig." in R["table"] else []
    notes.append("Efek nyata: " + (", ".join(sigrows) if sigrows else "tidak ada") + ".")
    a += note_card("Interpretasi", notes)
    eff = R["table"].copy()
    srt = eff.reindex(eff["Nilai efek"].abs().sort_values(ascending=False).index)
    v = np.sort(eff["Nilai efek"].values)
    q = stats.norm.ppf((np.arange(1, len(v) + 1) - 0.5) / len(v))
    specs = [{"kind": "bar", "title": "Diagram Pareto efek (|efek|)", "xlabel": "Efek", "ylabel": "|Efek|", "x": list(srt["Efek"]), "y": list(srt["Nilai efek"].abs()), "err": None, "horizontal": False},
             {"kind": "xy", "title": "Plot peluang normal efek", "xlabel": "Kuantil normal", "ylabel": "Efek", "hlines": [], "vlines": [],
              "series": [{"x": q, "y": v, "mode": "markers", "name": "Efek"}]}]
    g = plots_html(specs) + '<p class="cap">Efek yang menjauh dari garis lurus pada plot peluang normal adalah efek yang nyata.</p>'
    return top + tabs([("📋 Efek", a), ("📈 Grafik", g)], "t"), {"Efek": R["table"], "Data": R["data"]}
