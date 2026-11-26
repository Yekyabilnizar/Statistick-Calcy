"""core.py – utilitas data: baca tabel dari teks/berkas, inspeksi kolom, konversi grafik ke Plotly JSON."""
import io
import math

import numpy as np
import pandas as pd
from scipy import stats

MAX_CHARS = 3_000_000
MAX_ROWS = 50_000
MAX_COLS = 80


class InputError(ValueError):
    """Kesalahan input pengguna (pesan aman ditampilkan)."""


def _to_numeric_if_possible(s):
    if pd.api.types.is_numeric_dtype(s):
        return s
    t = s.astype(str).str.strip()
    t = t.replace({"": np.nan, "nan": np.nan, "NaN": np.nan, "NA": np.nan, "na": np.nan, "NULL": np.nan, "-": np.nan})
    nn = t.dropna()
    if nn.empty:
        return s
    conv = pd.to_numeric(nn, errors="coerce")
    if conv.notna().all():
        return pd.to_numeric(t, errors="coerce")
    nn2 = nn.str.replace(",", ".", regex=False)          # desimal koma (1,5)
    conv2 = pd.to_numeric(nn2, errors="coerce")
    if conv2.notna().all() and not nn.str.contains(r"\.").any():
        return pd.to_numeric(t.str.replace(",", ".", regex=False), errors="coerce")
    return s


def parse_table(text):
    """Baca data dari teks hasil tempel Excel (tab), CSV (koma/titik koma), atau spasi."""
    if text is None or not str(text).strip():
        raise InputError("Data kosong. Tempel data, unggah berkas, atau pakai data contoh.")
    text = str(text)
    if len(text) > MAX_CHARS:
        raise InputError("Data terlalu besar (maksimal sekitar 3 MB).")
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    first = text.split("\n", 1)[0]
    for sep in ("\t", ";", ","):
        if sep in first:
            break
    else:
        sep = r"\s+"
    try:
        df = pd.read_csv(io.StringIO(text), sep=sep, engine="python", skipinitialspace=True, dtype=str,
                         keep_default_na=False)
    except Exception:
        raise InputError("Format data tidak terbaca. Pastikan baris pertama berisi nama kolom dan kolom dipisah tab, koma, atau titik koma.")
    df.columns = [str(c).strip() or f"Kolom{i+1}" for i, c in enumerate(df.columns)]
    if len(set(df.columns)) != len(df.columns):
        raise InputError("Nama kolom ada yang kembar. Beri nama berbeda pada tiap kolom.")
    df = df.dropna(how="all")
    df = df.loc[:, [c for c in df.columns if not (df[c].astype(str).str.strip() == "").all()]]
    if df.shape[1] < 2:
        raise InputError("Data minimal memiliki 2 kolom. Periksa pemisah kolom (tab, koma, atau titik koma).")
    if df.shape[0] < 3:
        raise InputError("Data minimal memiliki 3 baris pengamatan.")
    if df.shape[0] > MAX_ROWS or df.shape[1] > MAX_COLS:
        raise InputError(f"Data terlalu besar (maksimal {MAX_ROWS:,} baris dan {MAX_COLS} kolom).")
    for c in df.columns:
        df[c] = _to_numeric_if_possible(df[c])
        if pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].replace([np.inf, -np.inf], np.nan)
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip().replace({"": np.nan})
    return df.reset_index(drop=True)


def parse_file(filename, content):
    """Baca berkas unggahan (CSV/TSV/TXT/XLSX) menjadi teks tabel (TSV)."""
    name = (filename or "").lower()
    if name.endswith((".xlsx", ".xlsm")):
        try:
            df = pd.read_excel(io.BytesIO(content), sheet_name=0, dtype=str)
        except Exception:
            raise InputError("Berkas Excel tidak terbaca. Simpan ulang sebagai .xlsx atau CSV.")
        return df.to_csv(sep="\t", index=False)
    if name.endswith(".xls"):
        raise InputError("Format .xls lama tidak didukung. Simpan sebagai .xlsx atau CSV.")
    for enc in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            return content.decode(enc)
        except Exception:
            continue
    raise InputError("Berkas teks tidak terbaca (encoding tidak dikenali).")


def is_cat_like(s, max_unique=15):
    s = s.dropna()
    return (not pd.api.types.is_numeric_dtype(s)) or s.nunique() <= max_unique


def inspect(df):
    cols = []
    for c in df.columns:
        s = df[c]
        num = bool(pd.api.types.is_numeric_dtype(s))
        cols.append({"name": str(c), "numeric": num, "cat": bool(is_cat_like(s)), "nuniq": int(s.nunique()),
                     "missing": int(s.isna().sum())})
    head = df.head(8).copy()
    return {"rows": int(len(df)), "columns": cols,
            "preview": {"header": [str(c) for c in head.columns],
                        "rows": [[("" if pd.isna(v) else (round(float(v), 4) if isinstance(v, (float, np.floating)) else str(v)))
                                  for v in r] for r in head.itertuples(index=False)]}}


# ----------------------------------------------------------------------------
# Grafik: spesifikasi sederhana -> JSON Plotly (digambar di browser)
# ----------------------------------------------------------------------------
def _arr(v):
    a = np.asarray(v)
    if a.dtype.kind in "fc":
        a = a.astype(float)
        return [None if not math.isfinite(x) else round(float(x), 6) for x in a.ravel()] if a.ndim == 1 else \
            [[None if not math.isfinite(x) else round(float(x), 6) for x in row] for row in a]
    if a.dtype.kind in "iu":
        return a.tolist()
    return [str(x) for x in a.ravel()]


def plot_json(spec):
    """Ubah spesifikasi grafik engine menjadi {'data': [...], 'layout': {...}} untuk Plotly.js."""
    k = spec["kind"]
    data, layout = [], {"title": {"text": spec.get("title", "")}, "xaxis": {"title": {"text": spec.get("xlabel", "")}},
                        "yaxis": {"title": {"text": spec.get("ylabel", "")}}}
    shapes = []
    if k in ("xy", "step"):
        if spec.get("band"):
            b = spec["band"]
            data.append({"type": "scatter", "mode": "lines", "x": _arr(b["x"]), "y": _arr(b["hi"]), "line": {"width": 0},
                         "showlegend": False, "hoverinfo": "skip"})
            data.append({"type": "scatter", "mode": "lines", "x": _arr(b["x"]), "y": _arr(b["lo"]), "line": {"width": 0}, "fill": "tonexty",
                         "fillcolor": "rgba(30,58,138,0.12)", "name": b.get("name", "Pita kepercayaan"), "hoverinfo": "skip"})
        for s in spec["series"]:
            mode = s.get("mode", "lines")
            line = {"width": 2.4}
            if s.get("dash"):
                line["dash"] = s["dash"]
            if k == "step":
                line["shape"] = "hv"
            t = {"type": "scatter", "mode": mode, "x": _arr(s["x"]), "y": _arr(s["y"]), "name": str(s.get("name", "")), "line": line,
                 "showlegend": not s.get("nolegend", False)}
            if "markers" in mode:
                t["marker"] = {"size": 7.5, "opacity": 0.85, "line": {"width": 0.8, "color": "#fff"}}
            data.append(t)
        if spec.get("xlog"):
            layout["xaxis"]["type"] = "log"
    elif k == "bar":
        x, y = list(spec["x"]), _arr(spec["y"])
        err = {"type": "data", "array": _arr(spec["err"])} if spec.get("err") is not None else None
        if spec.get("horizontal"):
            t = {"type": "bar", "orientation": "h", "x": y, "y": [str(v) for v in x], "showlegend": False, "marker": {"color": "#1E3A8A"}}
            if err:
                t["error_x"] = err
        else:
            t = {"type": "bar", "x": [str(v) for v in x], "y": y, "showlegend": False, "marker": {"color": "#1E3A8A"}}
            if err:
                t["error_y"] = err
            if spec.get("text"):
                t["text"] = [str(v) for v in spec["text"]]
                t["textposition"] = "outside"
        data.append(t)
    elif k == "box":
        for name, v in spec["groups"].items():
            data.append({"type": "box", "y": _arr(np.asarray(v, float)), "name": str(name), "boxpoints": "all", "jitter": 0.4, "pointpos": 0,
                         "showlegend": False, "marker": {"size": 6, "opacity": 0.8}})
    elif k == "splom":
        def _lab(n):
            n = str(n).replace("_", " ")
            return n if len(n) <= 16 else n[:15] + "…"
        dims = [{"label": _lab(n), "values": _arr(np.asarray(v, float))} for n, v in spec["dims"].items()]
        data.append({"type": "splom", "dimensions": dims, "diagonal": {"visible": False}, "showupperhalf": False,
                     "marker": {"size": 4, "color": "#1E3A8A", "opacity": 0.8}, "showlegend": False})
        layout["height"] = 650
        layout.pop("xaxis"), layout.pop("yaxis")
        layout["margin"] = {"l": 80, "r": 20, "t": 60, "b": 80}
        for i in range(1, len(dims) + 1):
            sfx = "" if i == 1 else str(i)
            ax = {"title": {"font": {"size": 11}}, "tickfont": {"size": 10}, "automargin": False}
            layout["xaxis" + sfx] = dict(ax)
            layout["yaxis" + sfx] = dict(ax)
    elif k == "heat":
        z = _arr(np.asarray(spec["z"], float))
        t = {"type": "heatmap", "z": z, "x": [str(v) for v in spec["x"]], "y": [str(v) for v in spec["y"]], "xgap": 2, "ygap": 2,
             "colorscale": [[0, "#B91C1C"], [0.25, "#F4A58A"], [0.5, "#F8FAFC"], [0.75, "#8DB5EA"], [1, "#1E3A8A"]],
             "texttemplate": "%{z:.2f}", "colorbar": {"thickness": 12, "outlinewidth": 0}}
        if spec.get("zmid") is not None:
            t["zmid"] = spec["zmid"]
        data.append(t)
    elif k == "contour":
        data.append({"type": "contour", "x": _arr(spec["x"]), "y": _arr(spec["y"]), "z": _arr(np.asarray(spec["z"], float)),
                     "colorscale": [[0, "#EFF6FF"], [0.35, "#93C5FD"], [0.7, "#1E3A8A"], [1, "#1E3A8A"]],
                     "contours": {"showlabels": True}, "colorbar": {"title": {"text": "Respon"}, "thickness": 12}})
        if spec.get("px") is not None:
            data.append({"type": "scatter", "mode": "markers", "x": _arr(spec["px"]), "y": _arr(spec["py"]), "name": "Titik percobaan",
                         "marker": {"color": "#DC4C64", "size": 9, "line": {"width": 1, "color": "#fff"}}})
    elif k == "hist":
        v = np.asarray(spec["values"], float)
        data.append({"type": "histogram", "x": _arr(v), "nbinsx": max(5, min(20, int(np.sqrt(len(v))) + 2)), "showlegend": False,
                     "marker": {"color": "#1E3A8A", "line": {"color": "#fff", "width": 1}}})
        layout["bargap"] = 0.05
    elif k == "hist2":
        for name, v in spec["groups"].items():
            data.append({"type": "histogram", "x": _arr(np.asarray(v, float)), "name": str(name), "opacity": 0.7, "nbinsx": 15})
        layout["barmode"] = "overlay"
    elif k == "qq":
        (osm, osr), (slope, intercept, _) = stats.probplot(np.asarray(spec["values"], float), dist="norm")
        data.append({"type": "scatter", "mode": "markers", "x": _arr(osm), "y": _arr(osr), "name": "Data",
                     "marker": {"size": 7.5, "opacity": 0.85, "line": {"width": 0.8, "color": "#fff"}}})
        data.append({"type": "scatter", "mode": "lines", "x": _arr(osm), "y": _arr(slope * osm + intercept), "name": "Garis normal",
                     "line": {"color": "#DC4C64", "dash": "dash", "width": 2}})
        layout["xaxis"]["title"] = {"text": spec.get("xlabel", "Kuantil teoretis")}
        layout["yaxis"]["title"] = {"text": spec.get("ylabel", "Kuantil sampel")}
    elif k == "map":
        data.append({"type": "scatter", "mode": "markers", "x": _arr(spec["x"]), "y": _arr(spec["y"]), "showlegend": False,
                     "marker": {"size": 12, "color": _arr(np.asarray(spec["color"], float)), "colorscale": "Viridis", "showscale": True,
                                "colorbar": {"title": {"text": spec.get("clabel", "")}, "thickness": 12},
                                "line": {"width": 0.8, "color": "#fff"}}})
    elif k == "tern":
        data.append({"type": "scatterternary", "mode": "markers", "a": _arr(spec["a"]), "b": _arr(spec["b"]), "c": _arr(spec["c"]),
                     "marker": {"size": 7, "color": _arr(np.asarray(spec["z"], float)), "colorscale": "Viridis", "showscale": True,
                                "colorbar": {"title": {"text": "Respon prediksi"}}}, "showlegend": False})
        if spec.get("pa") is not None:
            data.append({"type": "scatterternary", "mode": "markers", "a": _arr(spec["pa"]), "b": _arr(spec["pb"]), "c": _arr(spec["pc"]),
                         "marker": {"size": 10, "color": "#DC4C64", "symbol": "diamond"}, "name": "Titik percobaan"})
        n = spec["names"]
        layout["ternary"] = {"aaxis": {"title": {"text": n[0]}}, "baxis": {"title": {"text": n[1]}}, "caxis": {"title": {"text": n[2]}}}
        layout.pop("xaxis"), layout.pop("yaxis")
    if spec.get("ylim") and "yaxis" in layout:
        layout["yaxis"]["range"] = [float(spec["ylim"][0]), float(spec["ylim"][1])]
    for h in spec.get("hlines", []) or []:
        shapes.append({"type": "line", "xref": "paper", "x0": 0, "x1": 1, "y0": h, "y1": h, "line": {"color": "#DC4C64", "dash": "dash", "width": 1.5}})
    for v in spec.get("vlines", []) or []:
        shapes.append({"type": "line", "yref": "paper", "y0": 0, "y1": 1, "x0": v, "x1": v, "line": {"color": "#DC4C64", "dash": "dash", "width": 1.5}})
    if shapes:
        layout["shapes"] = shapes
    return {"data": data, "layout": layout}
