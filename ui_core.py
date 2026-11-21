"""
ui_core.py – komponen tampilan bersama untuk halaman metode baru (regresi & rancangan percobaan).
Helper dari app.py (show_df, kpis, dst.) disuntikkan lewat bind() agar tidak terjadi import melingkar.
"""
import traceback

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

import stats_engine as sc

_H = {}  # diisi oleh bind()


class _Proxy:
    def __getitem__(self, k):
        return _H[k]


H = _Proxy()


CSS_EXTRA = """<style>
.stApp .sec {display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; margin:22px 0 8px;}
.stApp .sec-t {font-size:1.12rem; font-weight:800; color:#0F2A43 !important; padding-left:12px; border-left:5px solid #2563EB; line-height:1.25;}
.stApp .sec-c {font-size:.9rem; color:#52667D !important;}
.stApp .crumb {display:flex; gap:8px; align-items:center; margin:-6px 0 14px; flex-wrap:wrap;}
.stApp .crumb span {background:rgba(255,255,255,.85); border:1px solid #CFE0F3; color:#334E68 !important; border-radius:999px; padding:3px 12px; font-size:.82rem; font-weight:700;}
.stApp .crumb span.cur {background:#1D4ED8; border-color:#1D4ED8; color:#fff !important;}
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div[data-testid="stVerticalBlock"] .form-marker) {background:#fff; border:1px solid #D5E3F3 !important; border-radius:18px; padding:8px 12px 4px; box-shadow:0 6px 18px rgba(30,64,120,.07);}
.stApp .form-marker {display:flex; align-items:center; gap:10px; font-weight:800; font-size:1.05rem; color:#0F2A43 !important; margin-bottom:4px;}
.stApp .form-marker i {font-style:normal; background:#E1EDFB; border-radius:10px; padding:4px 9px;}
.stApp .stTabs {margin-top:6px;}
.stApp details {background:rgba(255,255,255,.7); border:1px solid #D5E3F3 !important; border-radius:14px !important;}
.stApp [data-testid="stExpander"] summary p {color:#0F2A43 !important; font-weight:700;}
.stApp .stSelectbox > div > div, .stApp .stMultiSelect > div > div {border-radius:10px;}
.stApp .stButton button {border-radius:12px;}
</style>"""


def bind(helpers):
    _H.clear()
    _H.update(helpers)
    st.markdown(CSS_EXTRA, unsafe_allow_html=True)


def section(title, caption=None):
    import html as _h
    cap = f'<span class="sec-c">{_h.escape(str(caption))}</span>' if caption else ""
    st.markdown(f'<div class="sec"><span class="sec-t">{_h.escape(str(title))}</span>{cap}</div>', unsafe_allow_html=True)


def form_header(title):
    import html as _h
    st.markdown(f'<div class="form-marker"><i>⚙️</i>{_h.escape(title)}</div>', unsafe_allow_html=True)


def crumb(*parts):
    import html as _h
    spans = "".join(f'<span class="{"cur" if i == len(parts) - 1 else ""}">{_h.escape(str(p))}</span>' for i, p in enumerate(parts))
    st.markdown(f'<div class="crumb">{spans}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Pemilih kolom
# ----------------------------------------------------------------------------
def num_cols(df):
    return sc.numeric_cols(df)


def all_cols(df):
    return list(map(str, df.columns))


def cat_like(df, max_unique=15):
    """Kolom yang layak menjadi faktor/kategori: non-numerik atau numerik dengan sedikit nilai unik."""
    out = []
    for c in df.columns:
        s = df[c].dropna()
        if not pd.api.types.is_numeric_dtype(s) or s.nunique() <= max_unique:
            out.append(str(c))
    return out


def _default(options, want, fallback_idx=0):
    if want in options:
        return options.index(want)
    return min(max(fallback_idx, -len(options)), len(options) - 1) % max(len(options), 1)


def pick(label, options, key, want=None, idx=0, help=None):
    if not options:
        return None
    return st.selectbox(label, options, index=_default(options, want, idx), key=key, help=help)


def pick_multi(label, options, key, want=None, help=None):
    want = [w for w in (want or []) if w in options]
    return st.multiselect(label, options, default=want, key=key, help=help)


def pick_optional(label, options, key, want=None, help=None):
    opts = ["(tidak ada)"] + list(options)
    v = st.selectbox(label, opts, index=opts.index(want) if want in opts else 0, key=key, help=help)
    return None if v == "(tidak ada)" else v


# ----------------------------------------------------------------------------
# Data: contoh / unggah / tabel manual
# ----------------------------------------------------------------------------
def load_data_generic(sample_fn, kind, label):
    H["badge"]("2 · Data")
    src = st.sidebar.radio("Sumber data", ["Data contoh", "Unggah file (CSV/Excel)", "Input manual"], key="src")
    if src == "Data contoh":
        return sample_fn(kind), "contoh"
    if src.startswith("Unggah"):
        f = st.sidebar.file_uploader("Pilih file", type=["csv", "xlsx", "xls"], key=f"up_{label}")
        if f is None:
            H["n_info"]("⬅️ Unggah file CSV atau Excel pada sidebar. Baris pertama harus berisi nama kolom.")
            return None, "unggah"
        try:
            df = pd.read_csv(f, sep=None, engine="python") if f.name.lower().endswith(".csv") else pd.read_excel(f)
        except Exception as e:  # noqa: BLE001
            H["n_err"](f"Gagal membaca file: {e}")
            return None, "unggah"
        return df, "unggah"
    section("✍️ Input data manual")
    st.caption("Tabel di bawah dimulai dari data contoh sebagai kerangka format kolom. Ganti isinya dengan data Anda "
               "(boleh menambah/menghapus baris, atau salin-tempel dari Excel). Nama kolom dapat diganti dengan mengunggah file.")
    base = sample_fn(kind).copy()
    try:
        edited = st.data_editor(base, num_rows="dynamic", hide_index=True, key=f"ed_{label}")
    except TypeError:
        edited = st.data_editor(base, num_rows="dynamic", key=f"ed_{label}")
    edited = edited.dropna(how="all").reset_index(drop=True)
    if len(edited) == 0:
        H["n_info"]("Isi tabel di atas untuk memulai analisis.")
        return None, "manual"
    return edited, "manual"


def safe_run(fn, *a, **kw):
    """Jalankan mesin analisis; tampilkan pesan galat yang ramah. Mengembalikan None jika gagal."""
    try:
        with st.spinner("Menghitung…"):
            return fn(*a, **kw)
    except ValueError as e:
        H["n_err"](str(e))
    except np.linalg.LinAlgError:
        H["n_err"]("Perhitungan gagal karena matriks singular (ada variabel yang saling bergantung penuh atau konstan). "
                   "Periksa variabel yang dipilih.")
    except Exception as e:  # noqa: BLE001
        H["n_err"](f"Terjadi kesalahan tak terduga saat menghitung: {type(e).__name__}: {e}")
        with st.expander("Rincian teknis"):
            st.code(traceback.format_exc())
    return None


# ----------------------------------------------------------------------------
# Penggambar spesifikasi grafik
# ----------------------------------------------------------------------------
def _arr(a):
    return np.asarray(a)


def build_fig(spec):
    k = spec["kind"]
    fig = go.Figure()
    title = spec.get("title", "")
    if k in ("xy", "step"):
        if spec.get("band"):
            b = spec["band"]
            fig.add_trace(go.Scatter(x=_arr(b["x"]), y=_arr(b["hi"]), mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=_arr(b["x"]), y=_arr(b["lo"]), mode="lines", line=dict(width=0), fill="tonexty",
                                     fillcolor="rgba(37,99,235,0.14)", name=b.get("name", "Pita kepercayaan"), hoverinfo="skip"))
        for s in spec["series"]:
            mode = s.get("mode", "lines")
            line = dict(dash=s["dash"]) if s.get("dash") else {}
            if k == "step":
                line["shape"] = "hv"
            line.setdefault("width", 2.4)
            kw = {}
            if "markers" in mode:
                kw["marker"] = dict(size=7.5, opacity=0.85, line=dict(width=0.8, color="#FFFFFF"))
            fig.add_trace(go.Scatter(x=_arr(s["x"]), y=_arr(s["y"]), mode=mode, name=str(s.get("name", "")), line=line,
                                     showlegend=not s.get("nolegend", False), **kw))
        if spec.get("xlog"):
            fig.update_xaxes(type="log")
    elif k == "bar":
        x, y = list(spec["x"]), _arr(spec["y"])
        err = dict(type="data", array=_arr(spec["err"])) if spec.get("err") is not None else None
        if spec.get("horizontal"):
            fig.add_trace(go.Bar(x=y, y=x, orientation="h", error_x=err, showlegend=False,
                                 marker=dict(color="#2563EB", opacity=0.92)))
        else:
            txt = spec.get("text")
            fig.add_trace(go.Bar(x=[str(v) for v in x], y=y, error_y=err, showlegend=False,
                                 marker=dict(color="#2563EB", opacity=0.92, line=dict(width=0)),
                                 text=txt, textposition="outside" if txt else None))
    elif k == "heat":
        z = _arr(spec["z"]).astype(float)
        kw = {"zmid": spec["zmid"]} if spec.get("zmid") is not None else {}
        fig.add_trace(go.Heatmap(z=z, x=[str(v) for v in spec["x"]], y=[str(v) for v in spec["y"]], colorscale=[[0, "#B91C1C"], [0.25, "#F4A58A"], [0.5, "#F8FAFC"], [0.75, "#8DB5EA"], [1, "#1D4ED8"]],
                                 text=np.round(z, 2), texttemplate="%{text}", textfont=dict(size=12),
                                 colorbar=dict(thickness=12, outlinewidth=0), xgap=2, ygap=2, **kw))
    elif k == "contour":
        fig.add_trace(go.Contour(x=_arr(spec["x"]), y=_arr(spec["y"]), z=_arr(spec["z"]), colorscale=[[0, "#EFF6FF"], [0.35, "#93C5FD"], [0.7, "#2563EB"], [1, "#1E3A8A"]],
                                 contours=dict(showlabels=True, labelfont=dict(size=11, color="#0F2A43")),
                                 line=dict(width=0.8, color="rgba(255,255,255,.7)"),
                                 colorbar=dict(title="Respon", thickness=12, outlinewidth=0)))
        if spec.get("px") is not None:
            fig.add_trace(go.Scatter(x=_arr(spec["px"]), y=_arr(spec["py"]), mode="markers", name="Titik percobaan",
                                     marker=dict(color="#E11D48", size=9, line=dict(width=1, color="#FFFFFF"))))
    elif k == "hist":
        v = _arr(spec["values"]).astype(float)
        fig.add_trace(go.Histogram(x=v, nbinsx=max(5, min(20, int(np.sqrt(len(v))) + 2)), showlegend=False,
                                   marker=dict(color="#2563EB", opacity=0.9, line=dict(color="#FFFFFF", width=1))))
        fig.update_layout(bargap=0.05)
    elif k == "hist2":
        for name, v in spec["groups"].items():
            fig.add_trace(go.Histogram(x=_arr(v).astype(float), name=name, opacity=0.7, nbinsx=15,
                                       marker=dict(line=dict(color="#FFFFFF", width=0.8))))
        fig.update_layout(barmode="overlay")
    elif k == "qq":
        (osm, osr), (slope, intercept, _) = stats.probplot(_arr(spec["values"]).astype(float), dist="norm")
        fig.add_trace(go.Scatter(x=osm, y=osr, mode="markers", name="Data",
                                 marker=dict(size=7.5, opacity=0.85, line=dict(width=0.8, color="#FFFFFF"))))
        fig.add_trace(go.Scatter(x=osm, y=slope * osm + intercept, mode="lines", name="Garis normal",
                                 line=dict(color="#E11D48", dash="dash", width=2)))
        spec = {**spec, "xlabel": spec.get("xlabel", "Kuantil teoretis"), "ylabel": spec.get("ylabel", "Kuantil sampel")}
    elif k == "map":
        fig.add_trace(go.Scatter(x=_arr(spec["x"]), y=_arr(spec["y"]), mode="markers",
                                 marker=dict(size=12, color=_arr(spec["color"]), colorscale="Viridis", showscale=True,
                                             colorbar=dict(title=spec.get("clabel", ""), thickness=12, outlinewidth=0),
                                             line=dict(width=0.8, color="#FFFFFF")),
                                 showlegend=False))
    elif k == "tern":
        fig.add_trace(go.Scatterternary(a=_arr(spec["a"]), b=_arr(spec["b"]), c=_arr(spec["c"]), mode="markers",
                                        marker=dict(size=7, color=_arr(spec["z"]), colorscale="Viridis", showscale=True,
                                                    colorbar=dict(title="Respon prediksi")), name="Prediksi", showlegend=False))
        if spec.get("pa") is not None:
            fig.add_trace(go.Scatterternary(a=_arr(spec["pa"]), b=_arr(spec["pb"]), c=_arr(spec["pc"]), mode="markers",
                                            marker=dict(size=10, color="#EF4444", symbol="diamond"), name="Titik percobaan"))
        fig.update_layout(ternary=dict(aaxis=dict(title=spec["names"][0]), baxis=dict(title=spec["names"][1]),
                                       caxis=dict(title=spec["names"][2])))
    fig.update_layout(title=title)
    if k not in ("tern",):
        fig.update_xaxes(title=spec.get("xlabel", ""))
        fig.update_yaxes(title=spec.get("ylabel", ""))
    for h in spec.get("hlines", []) or []:
        fig.add_hline(y=h, line_dash="dash", line_color="#E11D48", line_width=1.5)
    for v in spec.get("vlines", []) or []:
        fig.add_vline(x=v, line_dash="dash", line_color="#E11D48", line_width=1.5)
    return fig


def draw_spec(spec, key):
    H["show_plot"](build_fig(spec), key)


def draw_specs(specs, prefix):
    """Tampilkan daftar grafik dalam dua kolom."""
    for i in range(0, len(specs), 2):
        cols = st.columns(2)
        for j, c in enumerate(cols):
            if i + j < len(specs):
                with c:
                    draw_spec(specs[i + j], f"{prefix}_{i + j}")


# ----------------------------------------------------------------------------
# Penampil hasil standar (regresi)
# ----------------------------------------------------------------------------
def render_result(R, prefix, filename="hasil.xlsx"):
    for w in R.get("warn", []):
        H["n_warn"](w)
    H["kpis"](R["kpis"])
    if R.get("eq"):
        H["eq_card"]("Persamaan model", R["eq"])
    tabs = st.tabs(["📋 Hasil", "📈 Grafik", "📝 Interpretasi", "⬇️ Unduh"])
    with tabs[0]:
        for name, t in R["tables"].items():
            section(name)
            H["show_df"](t, hide_index=True)
    with tabs[1]:
        if R["plots"]:
            draw_specs(R["plots"], prefix)
        else:
            st.info("Tidak ada grafik untuk analisis ini.")
    with tabs[2]:
        H["note_card"]("Interpretasi otomatis", R["notes"] or ["-"])
    with tabs[3]:
        section("Unduh Hasil")
        sheets = {}
        for name, t in R["tables"].items():
            sheets[name[:28]] = t
        data = R.get("data")
        if isinstance(data, pd.DataFrame):
            sheets["Data"] = data.reset_index(drop=True)
        H["download_excel"](sheets, filename, f"dl_{prefix}")
        st.caption("Grafik dapat diunduh sebagai PNG melalui ikon kamera di pojok kanan atas tiap grafik.")


def hero_for(title, desc, tags, alpha):
    H["hero"](title, desc, list(tags) + [f"Taraf nyata α = {alpha}"])
