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


def bind(helpers):
    _H.clear()
    _H.update(helpers)


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
    st.subheader("✍️ Input data manual")
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
                                     fillcolor="rgba(79,70,229,0.15)", name=b.get("name", "Pita kepercayaan"), hoverinfo="skip"))
        for s in spec["series"]:
            mode = s.get("mode", "lines")
            line = dict(dash=s["dash"]) if s.get("dash") else {}
            if k == "step":
                line["shape"] = "hv"
            fig.add_trace(go.Scatter(x=_arr(s["x"]), y=_arr(s["y"]), mode=mode, name=str(s.get("name", "")), line=line,
                                     showlegend=not s.get("nolegend", False)))
        if spec.get("xlog"):
            fig.update_xaxes(type="log")
    elif k == "bar":
        x, y = list(spec["x"]), _arr(spec["y"])
        err = dict(type="data", array=_arr(spec["err"])) if spec.get("err") is not None else None
        if spec.get("horizontal"):
            fig.add_trace(go.Bar(x=y, y=x, orientation="h", error_x=err, showlegend=False))
        else:
            txt = spec.get("text")
            fig.add_trace(go.Bar(x=[str(v) for v in x], y=y, error_y=err, showlegend=False,
                                 text=txt, textposition="outside" if txt else None))
    elif k == "heat":
        z = _arr(spec["z"]).astype(float)
        kw = {"zmid": spec["zmid"]} if spec.get("zmid") is not None else {}
        fig.add_trace(go.Heatmap(z=z, x=[str(v) for v in spec["x"]], y=[str(v) for v in spec["y"]], colorscale="RdBu_r",
                                 text=np.round(z, 2), texttemplate="%{text}", **kw))
    elif k == "contour":
        fig.add_trace(go.Contour(x=_arr(spec["x"]), y=_arr(spec["y"]), z=_arr(spec["z"]), colorscale="Blues",
                                 contours=dict(showlabels=True), colorbar=dict(title="Respon")))
        if spec.get("px") is not None:
            fig.add_trace(go.Scatter(x=_arr(spec["px"]), y=_arr(spec["py"]), mode="markers", name="Titik percobaan",
                                     marker=dict(color="#EF4444", size=8)))
    elif k == "hist":
        v = _arr(spec["values"]).astype(float)
        fig.add_trace(go.Histogram(x=v, nbinsx=max(5, min(20, int(np.sqrt(len(v))) + 2)), showlegend=False))
        fig.update_layout(bargap=0.05)
    elif k == "hist2":
        for name, v in spec["groups"].items():
            fig.add_trace(go.Histogram(x=_arr(v).astype(float), name=name, opacity=0.65, nbinsx=15))
        fig.update_layout(barmode="overlay")
    elif k == "qq":
        (osm, osr), (slope, intercept, _) = stats.probplot(_arr(spec["values"]).astype(float), dist="norm")
        fig.add_trace(go.Scatter(x=osm, y=osr, mode="markers", name="Data"))
        fig.add_trace(go.Scatter(x=osm, y=slope * osm + intercept, mode="lines", name="Garis normal"))
        spec = {**spec, "xlabel": spec.get("xlabel", "Kuantil teoretis"), "ylabel": spec.get("ylabel", "Kuantil sampel")}
    elif k == "map":
        fig.add_trace(go.Scatter(x=_arr(spec["x"]), y=_arr(spec["y"]), mode="markers",
                                 marker=dict(size=11, color=_arr(spec["color"]), colorscale="Viridis", showscale=True,
                                             colorbar=dict(title=spec.get("clabel", "")), line=dict(width=0.5, color="#FFFFFF")),
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
        fig.add_hline(y=h, line_dash="dash", line_color="#EF4444")
    for v in spec.get("vlines", []) or []:
        fig.add_vline(x=v, line_dash="dash", line_color="#EF4444")
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
            st.subheader(name)
            H["show_df"](t, hide_index=True)
    with tabs[1]:
        if R["plots"]:
            draw_specs(R["plots"], prefix)
        else:
            st.info("Tidak ada grafik untuk analisis ini.")
    with tabs[2]:
        H["note_card"]("Interpretasi otomatis", R["notes"] or ["-"])
    with tabs[3]:
        st.subheader("Unduh Hasil")
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
