"""
StatCalc – Dashboard Kalkulator Analisis Statistika
Analisis: Regresi Linear | RAL (Rancangan Acak Lengkap) | RAK (Rancangan Acak Kelompok)

Jalankan lokal :  streamlit run app.py
"""
import io

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

import stats_engine as sc

st.set_page_config(page_title="StatCalc – Analisis Statistika", page_icon="📊", layout="wide")
TPL = "plotly_white"

COLORS = ["#0F766E", "#4F46E5", "#F59E0B", "#EF4444", "#06B6D4", "#8B5CF6", "#16A34A", "#EC4899"]

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700;800&display=swap');
html, body, .stApp, [data-testid="stSidebar"] {font-family:'Source Sans 3','Source Sans Pro',sans-serif;}
.stApp {background:linear-gradient(160deg,#E6F0FF 0%,#D8E8FD 55%,#E8F2FF 100%); background-attachment:fixed;}
header[data-testid="stHeader"] {background:transparent;}
header[data-testid="stHeader"] *, [data-testid="stToolbar"] * {color:#475569 !important;}
.block-container {padding-top:2rem; padding-bottom:3rem; max-width:1400px;}
section[data-testid="stSidebar"] {background:linear-gradient(180deg,#F5F9FF 0%,#E6F0FC 100%); border-right:1px solid #CFE0F3;}
section[data-testid="stSidebar"] .block-container {padding-top:1.2rem;}
/* ---------- teks dasar ---------- */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp li, .stApp label,
.stApp [data-testid="stWidgetLabel"] p, .stApp [data-testid="stCaptionContainer"] p,
.stApp [data-testid="stRadio"] label p, .stApp [data-testid="stCheckbox"] label p {color:#0F2A43 !important;}
.stApp [data-testid="stCaptionContainer"] p {color:#52667D !important;}
.stApp h3 {font-weight:800; font-size:1.3rem; border-left:5px solid #2563EB; padding-left:12px; line-height:1.3; margin-top:10px;}
.stApp [data-testid="stRadio"] label:has(input:checked) > div:first-child {background-color:#1D4ED8 !important; border-color:#1D4ED8 !important;}
.stApp [data-testid="stCheckbox"] label:has(input:checked) > span:first-child {background-color:#1D4ED8 !important; border-color:#1D4ED8 !important;}
/* ---------- sidebar ---------- */
.stApp .brand {font-size:1.55rem; font-weight:800; color:#0F2A43 !important; margin-top:4px;}
.stApp .brand-sub {color:#52667D !important; font-size:.95rem; margin:2px 0 6px;}
.stApp .badge {display:inline-block; background:#CFE6FF; color:#1D4ED8 !important; font-weight:800; font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; padding:7px 14px; border-radius:10px; margin:16px 0 8px;}
/* ---------- hero ---------- */
.stApp .hero {position:relative; overflow:hidden; border-radius:28px; padding:36px 44px 28px; margin-bottom:22px; background:radial-gradient(circle at 88% 18%,rgba(45,212,191,.50),transparent 45%),linear-gradient(120deg,#16306B 0%,#1E40AF 50%,#0F8A8A 100%); box-shadow:0 18px 40px rgba(30,64,175,.22);}
.stApp .hero .hero-chip {display:inline-block; border:1px solid rgba(94,234,212,.65); color:#5EEAD4 !important; background:rgba(255,255,255,.08); font-weight:800; font-size:.72rem; letter-spacing:.2em; padding:7px 16px; border-radius:999px;}
.stApp .hero h1 {color:#fff !important; font-size:2.4rem; font-weight:800; margin:16px 0 10px; padding:0; line-height:1.15; border:none;}
.stApp .hero p {color:#DCE8FF !important; font-size:1.05rem; line-height:1.65; max-width:920px; margin:0 0 16px;}
.stApp .hero .hero-tags span {display:inline-block; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.35); color:#fff !important; font-weight:700; font-size:.82rem; padding:7px 16px; border-radius:999px; margin:0 8px 8px 0;}
/* ---------- kartu KPI ---------- */
.kpi-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(165px,1fr)); gap:14px; margin:6px 0 18px;}
.kpi {background:#fff; border:1px solid #D5E3F3; border-top:4px solid #2563EB; border-radius:16px; padding:14px 18px; box-shadow:0 6px 18px rgba(30,64,120,.08);}
.kpi.k1 {border-top-color:#0F766E;} .kpi.k2 {border-top-color:#7C3AED;} .kpi.k3 {border-top-color:#F59E0B;} .kpi.k4 {border-top-color:#EC4899;} .kpi.k5 {border-top-color:#06B6D4;}
.stApp .kpi-l {text-transform:uppercase; letter-spacing:.08em; font-size:.72rem; font-weight:800; color:#1D4ED8 !important;}
.stApp .kpi-v {color:#0B2545 !important; font-size:1.65rem; font-weight:800; margin-top:4px; line-height:1.2;}
/* ---------- kartu interpretasi, persamaan, notifikasi ---------- */
.card {background:#fff; border:1px solid #D5E3F3; border-radius:18px; padding:18px 26px; box-shadow:0 6px 18px rgba(30,64,120,.07); margin:8px 0 16px;}
.stApp .card-title {font-size:1.12rem; font-weight:800; color:#0F2A43 !important; margin-bottom:8px;}
.card ul {margin:0; padding-left:20px;}
.stApp .card li {color:#1E3A52 !important; line-height:1.7; margin:5px 0;}
.stApp .card li b {color:#0B2545 !important;}
.eq {background:linear-gradient(120deg,#EAF2FF,#F5F9FF); border:1px solid #C9DCF3; border-left:5px solid #2563EB; border-radius:14px; padding:14px 22px; margin:6px 0 16px;}
.stApp .eq-l {text-transform:uppercase; letter-spacing:.1em; font-size:.72rem; font-weight:800; color:#1D4ED8 !important;}
.stApp .eq-v {font-family:ui-monospace,Menlo,Consolas,monospace; color:#0B2545 !important; font-size:1.05rem; font-weight:600; margin-top:4px; word-break:break-word;}
.notice {display:flex; gap:12px; align-items:flex-start; border-radius:14px; padding:13px 18px; margin:8px 0 14px; border:1px solid; font-size:.98rem; line-height:1.55;}
.stApp .notice.info, .stApp .notice.info * {color:#16325C !important;}
.stApp .notice.success, .stApp .notice.success * {color:#14452B !important;}
.stApp .notice.warning, .stApp .notice.warning * {color:#5B4200 !important;}
.stApp .notice.error, .stApp .notice.error * {color:#6B1D1D !important;}
.notice.info {background:#E6F0FF; border-color:#BCD3F2;} .notice.success {background:#E3F6EC; border-color:#B7E4CB;}
.notice.warning {background:#FFF4DA; border-color:#F2D98F;} .notice.error {background:#FFE7E7; border-color:#F2B8B8;}
.stApp .sc-pre {background:#F3F8FF; border:1px solid #D5E3F3; border-radius:12px; padding:14px 16px; overflow:auto; color:#0F2A43 !important; font-size:.82rem; line-height:1.45; max-height:520px;}
/* ---------- tab ---------- */
.stTabs [data-baseweb="tab-list"], .stApp [role="tablist"] {gap:8px; border-bottom:none !important; box-shadow:none !important; flex-wrap:wrap;}
.stApp .stTabs [data-baseweb="tab"] {background:rgba(255,255,255,.85); border:1px solid #CFE0F3; border-radius:999px; padding:8px 18px; height:auto; font-weight:700;}
.stApp .stTabs [data-baseweb="tab"] p {color:#334E68 !important; font-weight:700;}
.stApp .stTabs [aria-selected="true"] {background:linear-gradient(120deg,#1D4ED8,#0E7FA8); border-color:transparent; box-shadow:none !important;}
.stApp .stTabs [aria-selected="true"] p {color:#fff !important;}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {display:none !important; height:0 !important; background:transparent !important;}
/* ---------- grafik, expander ---------- */
div[data-testid="stPlotlyChart"] {background:#fff; border:1px solid #D5E3F3; border-radius:18px; padding:12px 10px 4px; box-shadow:0 6px 20px rgba(30,64,120,.08);}
.stDownloadButton button {background:linear-gradient(120deg,#1D4ED8,#0E7FA8); border:none; border-radius:12px; padding:.6rem 1.3rem;}
.stApp .stDownloadButton button p {color:#fff !important; font-weight:700;}
.stDownloadButton button:hover {filter:brightness(1.08);}
/* ---------- tabel HTML ---------- */
.sc-wrap {background:#fff; border:1px solid #D5E3F3; border-radius:14px; overflow:auto; max-height:460px; box-shadow:0 6px 20px rgba(30,64,120,.08); margin:4px 0 14px;}
.sc-table {border-collapse:separate; border-spacing:0; width:100%; font-size:.92rem; font-variant-numeric:tabular-nums;}
.sc-table th {position:sticky; top:0; z-index:2; background:linear-gradient(180deg,#16325C,#10264A); color:#fff !important; font-weight:700; font-size:.76rem; letter-spacing:.06em; text-transform:uppercase; padding:11px 14px; text-align:left; white-space:nowrap; border-bottom:2px solid #2563EB;}
.sc-table td {color:#0F2A43 !important; padding:9px 14px; border-bottom:1px solid #E8EFF8; white-space:nowrap; text-align:left;}
.sc-table td.first {font-weight:700; color:#0B2545 !important;}
.sc-table td.wrap {white-space:normal; min-width:220px; max-width:520px;}
.sc-table tbody tr:nth-child(even) td, .sc-table tbody tr:nth-child(even) th.idx {background:#F5F9FF;}
.sc-table tbody tr:hover td, .sc-table tbody tr:hover th.idx {background:#E3EEFF;}
.sc-table tbody tr.tot td {background:#E8F0FC !important; font-weight:800; border-top:2px solid #BCD0EA;}
.sc-table th.r, .sc-table td.r {text-align:right;}
.sc-table th.c, .sc-table td.c {text-align:center;}
.sc-table th.idx {position:sticky; left:0; background:#10264A; color:#9FB4CC !important; font-weight:600; text-align:right; border-bottom:1px solid #E8EFF8;}
.sc-table tbody th.idx {background:#F0F5FC; color:#64748B !important; position:static;}
.sc-table td.psig {font-weight:800; color:#1D4ED8 !important;}
.sc-table td.pns {color:#64748B !important;}
.pill {display:inline-block; border-radius:999px; padding:2px 11px; font-size:.78rem; font-weight:800; letter-spacing:.02em; line-height:1.5;}
.pill.ok {background:#D1FAE5; color:#065F46 !important;} .pill.mid {background:#FEF3C7; color:#92400E !important;}
.pill.no {background:#E2E8F0; color:#475569 !important;} .pill.bad {background:#FEE2E2; color:#991B1B !important;}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

# Komponen bawaan Streamlit (input, dropdown, tabel editor) mengikuti tema aplikasi. Bila tema gelap aktif,
# warna komponen itu dibalik (invert) agar menjadi terang dan serasi dengan latar biru soft.
DARK_FIX = """
[data-testid="stSelectbox"], [data-testid="stMultiSelect"], [data-testid="stTextInput"],
[data-testid="stNumberInput"], [data-testid="stTextArea"], [data-testid="stFileUploader"],
[data-testid="stDataFrame"], [data-testid="stDataEditor"],
[data-testid="stRadio"] label > div:first-child, [data-testid="stCheckbox"] label > span:first-child
{filter:invert(1) hue-rotate(180deg) brightness(1.06);}
[data-testid="stSelectbox"] [data-testid="stWidgetLabel"], [data-testid="stMultiSelect"] [data-testid="stWidgetLabel"],
[data-testid="stTextInput"] [data-testid="stWidgetLabel"], [data-testid="stNumberInput"] [data-testid="stWidgetLabel"],
[data-testid="stTextArea"] [data-testid="stWidgetLabel"], [data-testid="stFileUploader"] [data-testid="stWidgetLabel"]
{filter:invert(1) hue-rotate(180deg);}
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {border-radius:14px; overflow:hidden; border:1px solid #C5D7EC;}
"""


def _theme_type():
    try:
        return st.context.theme.type
    except Exception:
        return None


_mode = _theme_type()
if _mode == "dark":
    st.markdown(f"<style>{DARK_FIX}</style>", unsafe_allow_html=True)
elif _mode is None:
    st.markdown(f"<style>@media (prefers-color-scheme: dark){{{DARK_FIX}}}</style>", unsafe_allow_html=True)



def badge(text):
    st.sidebar.markdown(f'<div class="badge">{text}</div>', unsafe_allow_html=True)


def hero(title, desc, tags):
    chips = "".join(f"<span>{t}</span>" for t in tags)
    st.markdown(
        f'<div class="hero"><span class="hero-chip">KALKULATOR STATISTIKA</span>'
        f"<h1>{title}</h1><p>{desc}</p><div class=\"hero-tags\">{chips}</div></div>",
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Helper tampilan
# ----------------------------------------------------------------------------
def _rich(text):
    import html as _h
    import re as _re
    t = _h.escape(str(text)).replace("$", "&#36;")
    return _re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def _notice(msg, kind):
    icon = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "⛔"}[kind]
    st.markdown(f'<div class="notice {kind}"><span>{icon}</span><div>{_rich(msg)}</div></div>', unsafe_allow_html=True)


def n_info(msg):
    _notice(msg, "info")


def n_ok(msg):
    _notice(msg, "success")


def n_warn(msg):
    _notice(msg, "warning")


def n_err(msg):
    _notice(msg, "error")


def kpis(items):
    import html as _h
    cards = "".join(
        f'<div class="kpi k{i % 6}"><div class="kpi-l">{_h.escape(str(l))}</div>'
        f'<div class="kpi-v">{_h.escape(str(v))}</div></div>' for i, (l, v) in enumerate(items))
    st.markdown(f'<div class="kpi-grid">{cards}</div>', unsafe_allow_html=True)


def note_card(title, items):
    lis = "".join(f"<li>{_rich(i)}</li>" for i in items)
    st.markdown(f'<div class="card"><div class="card-title">{title}</div><ul>{lis}</ul></div>', unsafe_allow_html=True)


def eq_card(label, text):
    import html as _h
    st.markdown(f'<div class="eq"><div class="eq-l">{_h.escape(label)}</div>'
                f'<div class="eq-v">{_h.escape(text)}</div></div>', unsafe_allow_html=True)


def pre_block(text):
    import html as _h
    body = "\n".join(l if l.strip() else "\u200b" for l in str(text).splitlines())
    st.markdown(f'<pre class="sc-pre">{_h.escape(body)}</pre>', unsafe_allow_html=True)


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


_POS = ("terpenuhi", "berbeda nyata", "nyata", "signifikan", "ya", "baik", "stasioner", "cocok", "dipilih")
_NEG = ("tidak terpenuhi", "tidak", "buruk", "ditolak", "dipertanyakan")


def _pill_for(col_name, text):
    t = str(text).strip()
    tl = t.lower()
    if t in ("**", "*", "tn", "ns"):
        return {"**": ("ok", "**"), "*": ("mid", "*"), "tn": ("no", "tn"), "ns": ("no", "tn")}[t]
    if "kesimpulan" in col_name.lower() or "asumsi" in col_name.lower() or col_name.lower() in ("status", "keputusan"):
        if tl.startswith("tidak terpenuhi") or tl.startswith("dipertanyakan") or tl.startswith("asumsi ph dipertanyakan"):
            return ("bad", t)
        if tl.startswith("terpenuhi") or tl.startswith("asumsi ph terpenuhi"):
            return ("ok", t)
        if tl.startswith("tidak"):
            return ("no", t)
        if tl.startswith("berbeda nyata") or "nyata" in tl[:12]:
            return ("ok", t)
    return None


def show_df(df, hide_index=False, max_rows=1000, **kw):
    """Tabel HTML bergaya kartu (tidak bergantung pada tema gelap/terang Streamlit)."""
    import html as _html

    def esc(x):
        return _html.escape(str(x)).replace("$", "&#36;")

    total = len(df)
    d = df.head(max_rows)
    cols = [str(c) for c in d.columns]
    right = [_is_numlike(d.iloc[:, j]) for j in range(d.shape[1])]
    kinds = []
    for j, c in enumerate(cols):
        cl = c.lower()
        kinds.append("sig" if cl in ("sig.", "sig") else "p" if cl.startswith("p-value") or cl.startswith("p ") or cl in ("p", "p bonferroni") or cl.startswith("p-") else "")
    long_txt = []
    for j in range(d.shape[1]):
        col = d.iloc[:, j]
        long_txt.append((not right[j]) and col.astype(str).str.len().max() > 38 if len(col) else False)
    head = "".join(
        f'<th class="{"c" if kinds[j] == "sig" else "r" if right[j] else ""}">{esc(c)}</th>' for j, c in enumerate(cols))
    if not hide_index:
        head = f'<th class="idx">{esc(d.index.name or "")}</th>' + head
    rows = []
    for idx, row in zip(d.index, d.itertuples(index=False, name=None)):
        first = str(row[0]).strip().lower() if len(row) else ""
        tot = first == "total" or first.startswith("total")
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
            if long_txt[j]:
                cls.append("wrap")
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
        rows.append(f'<tr class="{"tot" if tot else ""}">{cells}</tr>')
    html = (f'<div class="sc-wrap"><table class="sc-table"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')
    st.markdown(html, unsafe_allow_html=True)
    if total > max_rows:
        st.caption(f"Menampilkan {max_rows} dari {total} baris.")


PALETTE = ["#2563EB", "#0D9488", "#F59E0B", "#E11D48", "#7C3AED", "#0891B2", "#65A30D", "#DB2777"]


def style_fig(fig):
    """Tema grafik profesional: bersih, kontras jelas, legenda di bawah."""
    ax = dict(showgrid=True, gridcolor="#E9EFF7", gridwidth=1, zeroline=False, showline=True, linecolor="#B6C6DA",
              linewidth=1, ticks="outside", tickcolor="#B6C6DA", ticklen=4, tickfont=dict(size=12, color="#41566F"),
              title_font=dict(size=12.5, color="#52667D"), automargin=True, title_standoff=10)
    fig.update_layout(
        template="plotly_white", colorway=PALETTE, height=420,
        margin=dict(l=56, r=26, t=62, b=56),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Source Sans 3, sans-serif", color="#0F2A43", size=13),
        title=dict(font=dict(size=16, color="#0F2A43", family="Source Sans 3, sans-serif"), x=0.015, xanchor="left", y=0.96),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="left", x=0, font=dict(size=12, color="#334E68"),
                    bgcolor="rgba(0,0,0,0)", itemsizing="constant"),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#B6C6DA", font=dict(size=12.5, color="#0F2A43")),
        hovermode="closest", bargap=0.3,
    )
    fig.update_xaxes(**ax)
    fig.update_yaxes(**ax)
    return fig


def show_plot(fig, key):
    style_fig(fig)
    cfg = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"], "toImageButtonOptions": {"scale": 2}}
    try:
        st.plotly_chart(fig, width="stretch", key=key, theme=None, config=cfg)
    except Exception:
        st.plotly_chart(fig, use_container_width=True, key=key, theme=None, config=cfg)


def to_excel_bytes(sheets):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for name, frame in sheets.items():
            frame.to_excel(w, sheet_name=name[:31], index=False)
    return buf.getvalue()


def download_excel(sheets, filename, key):
    st.download_button(
        "⬇️ Unduh semua hasil (Excel)",
        data=to_excel_bytes(sheets),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=key,
    )


# ----------------------------------------------------------------------------
# Grafik residual (dipakai regresi, RAL, dan RAK)
# ----------------------------------------------------------------------------
def fig_resid_fitted(fitted, resid):
    fig = go.Figure(go.Scatter(x=np.asarray(fitted), y=np.asarray(resid), mode="markers", name="Galat"))
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    fig.update_layout(title="Galat vs Nilai Prediksi", xaxis_title="Nilai prediksi", yaxis_title="Galat")
    return fig


def fig_qq(resid):
    (osm, osr), (slope, intercept, _) = stats.probplot(np.asarray(resid), dist="norm")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=osm, y=osr, mode="markers", name="Galat"))
    fig.add_trace(go.Scatter(x=osm, y=slope * osm + intercept, mode="lines", name="Garis normal"))
    fig.update_layout(title="Normal Q-Q Plot Galat", xaxis_title="Kuantil teoretis", yaxis_title="Kuantil sampel")
    return fig


def fig_hist(resid):
    n = len(resid)
    fig = px.histogram(x=np.asarray(resid), nbins=max(5, min(20, int(np.sqrt(n)) + 2)),
                       labels={"x": "Galat"}, title="Histogram Galat")
    fig.update_layout(yaxis_title="Frekuensi", bargap=0.05)
    return fig


def residual_plots(fitted, resid, prefix):
    c1, c2 = st.columns(2)
    with c1:
        show_plot(fig_resid_fitted(fitted, resid), f"{prefix}_rf")
    with c2:
        show_plot(fig_qq(resid), f"{prefix}_qq")
    c3, _ = st.columns(2)
    with c3:
        show_plot(fig_hist(resid), f"{prefix}_hist")


# ----------------------------------------------------------------------------
# Input data
# ----------------------------------------------------------------------------
def load_data(key):
    badge("2 · Data")
    src = st.sidebar.radio("Sumber data", ["Data contoh", "Unggah file (CSV/Excel)", "Input manual"], key="src")
    if src == "Data contoh":
        return sc.sample_data(key), "contoh"

    if src.startswith("Unggah"):
        f = st.sidebar.file_uploader("Pilih file", type=["csv", "xlsx", "xls"], key=f"up_{key}")
        if f is None:
            n_info("⬅️ Unggah file CSV atau Excel pada sidebar. Baris pertama harus berisi nama kolom.")
            return None, "unggah"
        try:
            if f.name.lower().endswith(".csv"):
                df = pd.read_csv(f, sep=None, engine="python")
            else:
                df = pd.read_excel(f)
        except Exception as e:
            n_err(f"Gagal membaca file: {e}")
            return None, "unggah"
        return df, "unggah"

    # ---------------- Input manual ----------------
    st.subheader("✍️ Input data manual")
    if key == "reg":
        c1, c2 = st.columns([3, 1])
        txt = c1.text_input("Nama kolom (pisahkan dengan koma, kolom terakhir = Y)", "X1, X2, Y", key="cols_reg")
        nrow = int(c2.number_input("Jumlah baris", min_value=5, max_value=500, value=12, step=1, key="rows_reg"))
        cols = [c.strip() for c in txt.split(",") if c.strip()]
        if len(set(cols)) != len(cols) or len(cols) < 2:
            n_warn("Nama kolom harus unik dan minimal 2 kolom.")
            return None, "manual"
        base = pd.DataFrame({c: [np.nan] * nrow for c in cols})
        check_col, sig = cols[-1], f"reg|{'|'.join(cols)}|{nrow}"
    else:
        c1, c2, c3 = st.columns(3)
        t_in = int(c1.number_input("Jumlah perlakuan", min_value=2, max_value=30, value=4, step=1, key=f"t_{key}"))
        r = int(c2.number_input("Jumlah ulangan" if key == "ral" else "Jumlah kelompok",
                                min_value=2, max_value=30, value=4, step=1, key=f"r_{key}"))
        resp_col = c3.text_input("Nama kolom respon", "Hasil", key=f"resp_{key}").strip() or "Hasil"
        names_txt = st.text_input("Nama perlakuan (opsional, pisahkan dengan koma)", "",
                                  placeholder="contoh: P0, P1, P2, P3  (kosongkan untuk P1, P2, ...)", key=f"names_{key}")
        levels = [x.strip() for x in names_txt.split(",") if x.strip()] or [f"P{i}" for i in range(1, t_in + 1)]
        if len(set(levels)) != len(levels):
            n_warn("Nama perlakuan harus unik.")
            return None, "manual"
        if resp_col in ("Perlakuan", "Ulangan", "Kelompok"):
            n_warn("Nama kolom respon tidak boleh sama dengan kolom perlakuan/ulangan/kelompok; dipakai 'Hasil'.")
            resp_col = "Hasil"
        t = len(levels)
        if key == "ral":
            base = pd.DataFrame({"Perlakuan": np.repeat(levels, r), "Ulangan": np.tile(np.arange(1, r + 1), t),
                                 resp_col: np.nan})
        else:
            blocks = [f"K{i}" for i in range(1, r + 1)]
            base = pd.DataFrame({"Perlakuan": np.tile(levels, r), "Kelompok": np.repeat(blocks, t), resp_col: np.nan})
        check_col, sig = resp_col, f"{key}|{'|'.join(levels)}|{r}|{resp_col}"
    st.caption("Tabel sudah disusun otomatis. Cukup isi kolom nilai pengamatan (angka, titik sebagai desimal), "
               "atau salin-tempel dari Excel. Mengubah jumlah perlakuan/ulangan akan mereset tabel.")
    try:
        edited = st.data_editor(base, num_rows="dynamic", hide_index=True, key=f"ed_{sig}")
    except TypeError:
        edited = st.data_editor(base, num_rows="dynamic", key=f"ed_{sig}")
    edited = edited.dropna(how="all")
    if pd.to_numeric(edited[check_col], errors="coerce").notna().sum() == 0:
        n_info(f"Isi kolom **{check_col}** pada tabel di atas untuk memulai analisis.")
        return None, "manual"
    return edited.reset_index(drop=True), "manual"


def page_regression(df, alpha):
    num = sc.numeric_cols(df)
    sig = str(abs(hash(tuple(map(str, df.columns)))))
    if len(num) < 2:
        n_err("Dibutuhkan minimal 2 kolom numerik untuk regresi.")
        return

    badge("3 · Variabel")
    y = st.sidebar.selectbox("Variabel dependen (Y)", num, index=len(num) - 1, key=f"reg_y_{sig}")
    x_opts = [c for c in num if c != y]
    xs = st.sidebar.multiselect("Variabel independen (X)", x_opts, default=x_opts, key=f"reg_x_{y}_{sig}")
    intercept = st.sidebar.checkbox("Sertakan intersep (konstanta)", value=True, key="reg_int")
    if not xs:
        n_info("Pilih minimal satu variabel independen (X) pada sidebar.")
        return

    try:
        R = sc.run_regression(df, y, xs, intercept, alpha)
    except ValueError as e:
        n_err(str(e))
        return
    except Exception as e:
        n_err(f"Terjadi kesalahan saat menghitung regresi: {e}")
        return

    model, d, k, n = R["model"], R["data"], R["k"], R["n"]
    if R["n_dropped"]:
        n_warn(f"{R['n_dropped']} baris dengan nilai kosong/non-angka dikeluarkan dari analisis.")

    tabs = st.tabs(["📋 Data", "📊 Ringkasan", "📑 Tabel", "📈 Visualisasi", "✅ Uji Asumsi", "🔮 Prediksi", "💾 Unduh"])

    # --- Data
    with tabs[0]:
        st.subheader("Data yang dianalisis")
        show_df(d.reset_index(drop=True))
        st.caption(f"n = {n} pengamatan lengkap")
        st.subheader("Statistik deskriptif")
        show_df(d.describe().T.round(4))

    # --- Ringkasan
    with tabs[1]:
        st.subheader("Ringkasan Model Regresi")
        eq_card("Persamaan regresi", R["equation"])
        kpis([("n", n), ("R²", f"{model.rsquared:.4f}"), ("R² Adjusted", f"{model.rsquared_adj:.4f}"),
              ("F hitung", f"{model.fvalue:.3f}"), ("P-value (F)", sc.fmt_p(model.f_pvalue)),
              ("RMSE", f"{R['rmse']:.4f}")])

        sig_model = model.f_pvalue < alpha
        items = [
            f"**Uji simultan (Uji F):** F = {model.fvalue:.3f}, P-value = {sc.fmt_p(model.f_pvalue)} "
            f"{'<' if sig_model else '≥'} α ({alpha}). Model regresi "
            f"**{'signifikan' if sig_model else 'tidak signifikan'}**, artinya "
            f"{'minimal satu variabel X berpengaruh nyata terhadap ' + y if sig_model else 'belum ada bukti bahwa variabel X berpengaruh terhadap ' + y}.",
            f"**Koefisien determinasi:** R² = {model.rsquared:.4f}, sehingga {model.rsquared * 100:.2f}% "
            f"keragaman {y} dapat dijelaskan oleh {', '.join(xs)}.",
        ]
        for nm in xs:
            b_, p_ = model.params[nm], model.pvalues[nm]
            arah = "naik" if b_ > 0 else "turun"
            if p_ < alpha:
                items.append(f"**{nm}**: berpengaruh nyata (P = {sc.fmt_p(p_)}). Setiap kenaikan 1 satuan {nm} "
                             f"membuat {y} {arah} sebesar {abs(b_):.4f} satuan (variabel lain tetap).")
            else:
                items.append(f"**{nm}**: tidak berpengaruh nyata (P = {sc.fmt_p(p_)}).")
        note_card("📝 Interpretasi", items)
        if not intercept:
            n_info("Model tanpa intersep: R² dihitung terhadap total JK tak terpusat sehingga tidak sebanding dengan model berintersep.")

        if st.checkbox("Tampilkan ringkasan lengkap (format statsmodels)", key="reg_full"):
            pre_block(str(model.summary()))

    # --- Tabel
    with tabs[2]:
        st.subheader("Tabel Koefisien Regresi")
        show_df(R["coef"], hide_index=True)
        st.caption("Sig.: ** sangat nyata (P<0,01), * nyata (P<0,05), tn tidak nyata.")
        st.subheader("Tabel ANOVA Regresi")
        show_df(R["anova"], hide_index=True)
        if k >= 1:
            st.subheader("Matriks Korelasi (Pearson)")
            show_df(d.corr().round(4))
        st.subheader("Nilai Aktual, Prediksi, dan Galat")
        show_df(R["pred_table"])

    # --- Visualisasi
    with tabs[3]:
        st.subheader("Visualisasi")
        c1, c2 = st.columns(2)
        with c1:
            if k == 1:
                x = xs[0]
                xr = np.linspace(d[x].min(), d[x].max(), 100)
                Xn = pd.DataFrame({x: xr})
                if intercept:
                    Xn.insert(0, "const", 1.0)
                sf = model.get_prediction(Xn).summary_frame(alpha=alpha)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(xr) + list(xr[::-1]),
                                         y=list(sf["mean_ci_upper"]) + list(sf["mean_ci_lower"][::-1]),
                                         fill="toself", fillcolor="rgba(99,110,250,0.15)",
                                         line=dict(width=0), name=f"CI {int((1 - alpha) * 100)}%", hoverinfo="skip"))
                fig.add_trace(go.Scatter(x=d[x], y=d[y], mode="markers", name="Data"))
                fig.add_trace(go.Scatter(x=xr, y=sf["mean"], mode="lines", name="Garis regresi",
                                         line=dict(color="red")))
                fig.update_layout(title=f"Diagram Pencar & Garis Regresi ({y} ~ {x})", xaxis_title=x, yaxis_title=y)
            else:
                mn, mx = float(min(d[y].min(), model.fittedvalues.min())), float(max(d[y].max(), model.fittedvalues.max()))
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=model.fittedvalues, y=d[y], mode="markers", name="Data"))
                fig.add_trace(go.Scatter(x=[mn, mx], y=[mn, mx], mode="lines", name="y = x",
                                         line=dict(color="red", dash="dash")))
                fig.update_layout(title="Nilai Aktual vs Prediksi", xaxis_title="Prediksi", yaxis_title="Aktual")
            show_plot(fig, "reg_main")
        with c2:
            show_plot(fig_resid_fitted(model.fittedvalues, model.resid), "reg_rf")
        c3, c4 = st.columns(2)
        with c3:
            show_plot(fig_qq(model.resid), "reg_qq")
        with c4:
            show_plot(fig_hist(model.resid), "reg_hist")
        c5, c6 = st.columns(2)
        with c5:
            cook = R["cooks"]
            fcook = go.Figure(go.Bar(x=[str(i) for i in d.index], y=cook, name="Cook's D"))
            fcook.add_hline(y=4 / n, line_dash="dash", line_color="red",
                            annotation_text="4/n", annotation_position="top right")
            fcook.update_layout(title="Jarak Cook (Pengamatan Berpengaruh)", xaxis_title="Pengamatan", yaxis_title="Cook's D")
            show_plot(fcook, "reg_cook")
        with c6:
            fh = px.imshow(d.corr().round(3), text_auto=True, color_continuous_scale="RdBu_r",
                           zmin=-1, zmax=1, title="Heatmap Korelasi")
            show_plot(fh, "reg_heat")
        if k >= 2 and k + 1 <= 6:
            fm = px.scatter_matrix(d, title="Matriks Diagram Pencar")
            fm.update_traces(diagonal_visible=False, marker=dict(size=4))
            fm.update_layout(height=650)
            show_plot(fm, "reg_matrix")

    # --- Asumsi
    with tabs[4]:
        st.subheader("Uji Asumsi Klasik")
        show_df(R["assump"], hide_index=True)
        st.caption(f"Pada taraf α = {alpha}: P-value > α berarti asumsi terpenuhi.")
        if R["vif"] is not None:
            st.subheader("Uji Multikolinearitas (VIF)")
            show_df(R["vif"], hide_index=True)

    # --- Prediksi
    with tabs[5]:
        st.subheader("Kalkulator Prediksi")
        st.caption("Masukkan nilai variabel X untuk memprediksi Y.")
        cols = st.columns(min(len(xs), 4))
        vals = {}
        for i, x in enumerate(xs):
            with cols[i % len(cols)]:
                vals[x] = st.number_input(x, value=float(round(d[x].mean(), 4)), key=f"pred_{x}", format="%.4f")
        Xn = pd.DataFrame([vals])
        if intercept:
            Xn.insert(0, "const", 1.0)
        sf = model.get_prediction(Xn).summary_frame(alpha=alpha)
        cl = int((1 - alpha) * 100)
        kpis([(f"Prediksi {y}", f"{sf['mean'].iloc[0]:.4f}")])
        out = pd.DataFrame({
            "Prediksi": [sf["mean"].iloc[0]],
            f"CI {cl}% (rata-rata) bawah": [sf["mean_ci_lower"].iloc[0]],
            f"CI {cl}% (rata-rata) atas": [sf["mean_ci_upper"].iloc[0]],
            f"PI {cl}% (individu) bawah": [sf["obs_ci_lower"].iloc[0]],
            f"PI {cl}% (individu) atas": [sf["obs_ci_upper"].iloc[0]],
        }).round(4)
        show_df(out, hide_index=True)
        outside = [x for x in xs if not (d[x].min() <= vals[x] <= d[x].max())]
        if outside:
            n_warn(f"Nilai {', '.join(outside)} berada di luar rentang data (ekstrapolasi) sehingga prediksi kurang andal.")

    # --- Unduh
    with tabs[6]:
        st.subheader("Unduh Hasil")
        sheets = {
            "Data": d.reset_index(drop=True),
            "Koefisien": R["coef"],
            "ANOVA": R["anova"],
            "Uji Asumsi": R["assump"],
            "Prediksi & Galat": R["pred_table"].reset_index(drop=True),
        }
        if R["vif"] is not None:
            sheets["VIF"] = R["vif"]
        download_excel(sheets, "hasil_regresi.xlsx", "dl_reg")
        st.caption("Grafik dapat diunduh sebagai PNG melalui ikon kamera di pojok kanan atas tiap grafik.")


# ----------------------------------------------------------------------------
# Halaman: RAL & RAK
# ----------------------------------------------------------------------------
def page_anova(df, alpha, kind):
    num = sc.numeric_cols(df)
    cols = list(df.columns)
    sig = str(abs(hash(tuple(map(str, df.columns)))))
    badge("3 · Variabel")
    blk = None
    if kind == "ral":
        trt = st.sidebar.selectbox("Kolom perlakuan", cols, index=0, key=f"ral_trt_{sig}")
        r_opts = [c for c in num if c != trt]
        if not r_opts:
            n_err("Tidak ada kolom numerik untuk variabel respon.")
            return
        resp = st.sidebar.selectbox("Kolom respon (numerik)", r_opts, index=len(r_opts) - 1, key=f"ral_resp_{trt}_{sig}")
    else:
        trt = st.sidebar.selectbox("Kolom perlakuan", cols, index=0, key=f"rak_trt_{sig}")
        b_opts = [c for c in cols if c != trt]
        blk = st.sidebar.selectbox("Kolom kelompok (blok)", b_opts, index=0, key=f"rak_blk_{trt}_{sig}")
        r_opts = [c for c in num if c not in (trt, blk)]
        if not r_opts:
            n_err("Tidak ada kolom numerik untuk variabel respon.")
            return
        resp = st.sidebar.selectbox("Kolom respon (numerik)", r_opts, index=len(r_opts) - 1, key=f"rak_resp_{trt}_{blk}_{sig}")

    method = st.sidebar.selectbox("Uji lanjut", sc.POSTHOC_METHODS, key=f"{kind}_ph")

    try:
        R = sc.run_ral(df, resp, trt) if kind == "ral" else sc.run_rak(df, resp, trt, blk)
    except ValueError as e:
        n_err(str(e))
        return
    except Exception as e:
        n_err(f"Terjadi kesalahan saat menghitung: {e}")
        return

    d, levels = R["data"], R["levels"]
    letters, pair_df = sc.posthoc(R["means"], R["ns"], R["ktg"], R["dbg"], alpha, method)
    short = method.split(" ")[0]
    assump = sc.anova_assumptions(R, alpha)
    nm_design = "RAL" if kind == "ral" else "RAK"

    desc = pd.DataFrame({
        trt: levels,
        "n": R["ns"].values,
        "Rata-rata": R["means"].values.round(4),
        "SD": R["sd"].values.round(4),
        "SE": (R["sd"] / np.sqrt(R["ns"])).values.round(4),
        "Min": R["min"].values,
        "Maks": R["max"].values,
        f"Notasi {short}": [letters[l] for l in levels],
    })
    dropped = len(df) - len(d)

    tabs = st.tabs(["📋 Data", "📊 Ringkasan", "📑 Tabel", "📈 Visualisasi", "✅ Uji Asumsi", "💾 Unduh"])

    # --- Data
    with tabs[0]:
        st.subheader("Data yang dianalisis")
        if dropped:
            n_warn(f"{dropped} baris dengan nilai kosong/non-angka dikeluarkan dari analisis.")
        show_df(d[[c for c in [trt, blk, resp] if c]].reset_index(drop=True))
        if kind == "rak":
            st.subheader("Tabel dua arah (Kelompok × Perlakuan)")
            tbl = R["matrix"].copy()
            tbl["Total kelompok"] = tbl.sum(axis=1)
            tot = tbl.sum(axis=0).to_frame("Total perlakuan").T
            show_df(pd.concat([tbl, tot]).round(4))

    # --- Ringkasan
    with tabs[1]:
        st.subheader(f"Ringkasan Analisis {nm_design}")
        t0 = R["tests"][0]
        kpis([("Jumlah perlakuan", R["t"]),
              ("Ulangan (r)", f"{R['r']:.0f}" if float(R["r"]).is_integer() else f"{R['r']:.2f}"),
              ("F hitung (perlakuan)", f"{t0['F']:.3f}"), ("P-value", sc.fmt_p(t0["p"])),
              ("KK (%)", f"{R['kk']:.2f}"), ("Rata-rata umum", f"{R['grand']:.3f}")])

        items = []
        for t in R["tests"]:
            nm = t["name"]
            ok = t["p"] < alpha
            subj = "perlakuan" if nm == "Perlakuan" else "pengelompokan"
            if ok:
                kal = f"H₀ ditolak. Terdapat pengaruh **nyata** {subj} terhadap {resp}."
            else:
                kal = f"H₀ gagal ditolak. Tidak terdapat pengaruh nyata {subj} terhadap {resp}."
            items.append(f"**{nm}:** F = {t['F']:.3f}, P-value = {sc.fmt_p(t['p'])} {'<' if ok else '≥'} α ({alpha}). {kal}")
        items.append(f"**Koefisien keragaman (KK)** = {R['kk']:.2f}%.")
        if kind == "rak":
            er = R["extra"]["ER"]
            items.append(
                f"**Efisiensi relatif RAK terhadap RAL** = {er:.2f}. "
                + ("RAK lebih efisien daripada RAL (pengelompokan efektif)." if er > 1
                   else "Pengelompokan tidak meningkatkan efisiensi.")
            )
        note_card("📝 Interpretasi", items)
        if t0["p"] < alpha:
            best = max(levels, key=lambda l: R["means"][l])
            n_ok(f"Uji lanjut {method} pada taraf {alpha}: rata-rata tertinggi pada **{best}** "
                       f"({R['means'][best]:.3f}, notasi '{letters[best]}').")
        else:
            n_info("Perlakuan tidak berpengaruh nyata, sehingga uji lanjut sebenarnya tidak diperlukan "
                    "(hasilnya ditampilkan hanya sebagai informasi).")
        st.markdown("**Rata-rata perlakuan:**")
        show_df(desc, hide_index=True)
        st.caption("Rata-rata yang diikuti huruf yang sama tidak berbeda nyata pada taraf "
                   f"{alpha} menurut uji {method}.")

    # --- Tabel
    with tabs[2]:
        st.subheader(f"Tabel Sidik Ragam (ANOVA) – {nm_design}")
        show_df(R["anova"], hide_index=True)
        st.caption("Sig.: ** sangat nyata (P<0,01), * nyata (P<0,05), tn tidak nyata.")
        st.subheader("Statistik Deskriptif & Notasi Uji Lanjut")
        show_df(desc, hide_index=True)
        st.subheader(f"Perbandingan Berpasangan – {method}")
        show_df(pair_df, hide_index=True)
        st.subheader("Nilai Prediksi dan Galat")
        show_df(d[[c for c in [trt, blk, resp, "Fitted", "Galat"] if c]].round(4).reset_index(drop=True))

    # --- Visualisasi
    with tabs[3]:
        st.subheader("Visualisasi")
        c1, c2 = st.columns(2)
        with c1:
            fb = px.box(d, x=trt, y=resp, points="all", category_orders={trt: levels},
                        title=f"Boxplot {resp} per {trt}")
            show_plot(fb, f"{kind}_box")
        with c2:
            err_type = st.radio("Batang galat (error bar)", ["SD", "SE"], horizontal=True, key=f"{kind}_err")
            err = desc["SD" if err_type == "SD" else "SE"].fillna(0).values
            fbar = go.Figure(go.Bar(x=levels, y=R["means"].values, error_y=dict(type="data", array=err),
                                    name="Rata-rata"))
            top = float((R["means"].values + err).max())
            for lv, m, e in zip(levels, R["means"].values, err):
                fbar.add_annotation(x=lv, y=m + e, text=f"<b>{letters[lv]}</b>", showarrow=False, yshift=12)
            fbar.update_layout(title=f"Rata-rata ± {err_type} dengan notasi {short}",
                               xaxis_title=trt, yaxis_title=resp, yaxis_range=[0, top * 1.12])
            show_plot(fbar, f"{kind}_bar")

        if kind == "rak":
            c3, c4 = st.columns(2)
            with c3:
                fi = px.line(d, x=trt, y=resp, color=blk, markers=True, category_orders={trt: levels},
                             title="Plot Interaksi (garis per kelompok)")
                show_plot(fi, "rak_inter")
            with c4:
                fh = px.imshow(R["matrix"].round(3), text_auto=True, aspect="auto",
                               color_continuous_scale="Tealgrn",
                               labels=dict(x=trt, y=blk, color=resp), title="Heatmap Kelompok × Perlakuan")
                show_plot(fh, "rak_heat")
        residual_plots(d["Fitted"], d["Galat"], kind)

    # --- Asumsi
    with tabs[4]:
        st.subheader("Uji Asumsi ANOVA")
        show_df(assump, hide_index=True)
        st.caption(f"Pada taraf α = {alpha}: P-value > α berarti asumsi terpenuhi. "
                   "Lihat juga Q-Q plot dan plot galat pada tab Visualisasi.")
        if (assump["Kesimpulan"] == "Tidak terpenuhi").any():
            n_warn("Ada asumsi yang tidak terpenuhi. Pertimbangkan transformasi data (log/akar) "
                       "atau uji nonparametrik (Kruskal-Wallis untuk RAL, Friedman untuk RAK).")

    # --- Unduh
    with tabs[5]:
        st.subheader("Unduh Hasil")
        sheets = {
            "Data": d[[c for c in [trt, blk, resp] if c]].reset_index(drop=True),
            "ANOVA": R["anova"],
            "Rata-rata & Notasi": desc,
            "Uji Lanjut": pair_df,
            "Uji Asumsi": assump,
            "Prediksi & Galat": d[[c for c in [trt, blk, resp, "Fitted", "Galat"] if c]].round(4).reset_index(drop=True),
        }
        download_excel(sheets, f"hasil_{kind}.xlsx", f"dl_{kind}")
        st.caption("Grafik dapat diunduh sebagai PNG melalui ikon kamera di pojok kanan atas tiap grafik.")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def _bind_ui():
    import ui_core
    ui_core.bind(dict(show_df=show_df, show_plot=show_plot, kpis=kpis, note_card=note_card, eq_card=eq_card,
                      n_info=n_info, n_ok=n_ok, n_warn=n_warn, n_err=n_err, badge=badge, hero=hero,
                      download_excel=download_excel))


def main():
    st.sidebar.markdown('<div class="brand">📊 StatCalc</div><div class="brand-sub">Kalkulator analisis statistika</div>',
                        unsafe_allow_html=True)
    _bind_ui()
    import pages_design
    import pages_reg
    badge("1 · Analisis")
    CATS = ["Dasar: Regresi Linear · RAL · RAK", "Rancangan Percobaan Lanjutan", "Regresi Lanjutan"]
    cat = st.sidebar.radio("Kategori", CATS, key="category")
    alpha_box = None

    if cat == CATS[0]:
        choice = st.sidebar.radio(
            "Jenis analisis",
            ["Regresi Linear", "Rancangan Acak Lengkap (RAL)", "Rancangan Acak Kelompok (RAK)"],
            key="analysis",
        )
        mode, mkey = "legacy", {"Regresi Linear": "reg", "Rancangan Acak Lengkap (RAL)": "ral",
                                "Rancangan Acak Kelompok (RAK)": "rak"}[choice]
    elif cat == CATS[1]:
        groups = pages_design.DESIGN_GROUPS
        grp = st.sidebar.selectbox("Kelompok rancangan", list(groups.keys()), key="dgroup")
        labels = {m["label"]: m["key"] for m in groups[grp]}
        lab = st.sidebar.selectbox("Metode", list(labels.keys()), key=f"dmethod_{grp}")
        mode, mkey = "design", labels[lab]
    else:
        groups = pages_reg.REG_GROUPS
        grp = st.sidebar.selectbox("Kelompok regresi", list(groups.keys()), key="rgroup")
        labels = {m["label"]: m["key"] for m in groups[grp]}
        lab = st.sidebar.selectbox("Metode", list(labels.keys()), key=f"rmethod_{grp}")
        mode, mkey = "reg", labels[lab]

    alpha = st.sidebar.selectbox("Taraf nyata (α)", [0.01, 0.05, 0.10], index=1,
                                 format_func=lambda a: f"α = {a:.2f}", key="alpha")

    if mode == "design":
        pages_design.run_design_page(mkey, alpha)
        return
    if mode == "reg":
        pages_reg.run_reg_page(mkey, alpha)
        return

    key = mkey

    heroes = {
        "reg": ("Analisis Regresi Linear",
                "Ukur hubungan antara variabel independen (X) dan variabel dependen (Y): persamaan regresi, uji F dan uji t, "
                "R², uji asumsi klasik, hingga kalkulator prediksi. Hasil langsung berubah saat Anda mengubah data atau variabel di panel kiri.",
                ["OLS", "Sederhana & berganda", "Uji asumsi klasik"]),
        "ral": ("Rancangan Acak Lengkap (RAL)",
                "Analisis ragam satu faktor untuk percobaan dengan satuan percobaan yang homogen: tabel ANOVA, koefisien keragaman, "
                "uji lanjut bernotasi huruf, dan uji asumsi. Hasil langsung berubah saat Anda mengubah data di panel kiri.",
                ["ANOVA satu arah", "DMRT · BNJ · BNT", "Uji asumsi"]),
        "rak": ("Rancangan Acak Kelompok (RAK)",
                "Analisis ragam dengan pengelompokan untuk mengendalikan keragaman lingkungan: ANOVA perlakuan dan kelompok, "
                "efisiensi relatif terhadap RAL, serta uji lanjut bernotasi huruf. Hasil langsung berubah saat Anda mengubah data di panel kiri.",
                ["ANOVA dua arah tanpa interaksi", "DMRT · BNJ · BNT", "Efisiensi relatif"]),
    }
    h = heroes[key]
    hero(h[0], h[1], h[2] + [f"Taraf nyata α = {alpha}"])

    df, src = load_data(key)
    if df is None:
        return
    if src == "contoh":
        n_info("Menggunakan **data contoh**. Pilih 'Unggah file' atau 'Input manual' pada sidebar untuk data Anda sendiri.")

    if key == "reg":
        page_regression(df, alpha)
    else:
        page_anova(df, alpha, key)


main()
