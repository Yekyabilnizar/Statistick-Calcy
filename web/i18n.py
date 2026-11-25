"""i18n.py – dukungan dua bahasa (Indonesia = bawaan, Inggris = awalan /en/).

Cara kerja:
- LangMiddleware membuang awalan /en dari path dan menandai request.state.lang = "en"; semua route lama tetap dipakai.
- page() memilih templat templates/en/<nama>.html bila ada, lalu menambahkan awalan /en pada tautan internal.
- Konten yang belum diterjemahkan tetap tampil dalam bahasa Indonesia, diberi catatan, dan ditandai noindex.
- Menandai halaman/metode/modul sebagai siap Inggris: tambahkan ke READY_PATHS, EN_METHODS, atau EN_MODULES (tahap berikutnya).
"""
import re

# halaman statis yang isinya sudah sepenuhnya Inggris (tanpa data dari registry/modul)
READY_PATHS = {"/", "/rancangan-percobaan", "/regresi", "/panduan", "/alur-metode", "/masukan", "/tentang", "/privasi"}
from .i18n_data import METHODS_EN as _ME  # noqa: E402
EN_METHODS = set(_ME)  # slug metode yang sudah punya terjemahan lengkap
EN_MODULES = set()     # diisi otomatis dari i18n_data.mods (lihat bawah berkas)

NAV = {
    "id": [("/", "🏠 Beranda"), ("/belajar", "🎓 Belajar"), ("/rancangan-percobaan", "🧪 Alat Rancangan"), ("/regresi", "📈 Alat Regresi"),
           ("/panduan", "🧭 Panduan Metode"), ("/alur-metode", "🗺️ Alur Metode"), ("/masukan", "💬 Masukan"), ("/tentang", "ℹ️ Tentang")],
    "en": [("/", "🏠 Home"), ("/belajar", "🎓 Learn"), ("/rancangan-percobaan", "🧪 Design Tools"), ("/regresi", "📈 Regression Tools"),
           ("/panduan", "🧭 Method Guide"), ("/alur-metode", "🗺️ Method Flow"), ("/masukan", "💬 Feedback"), ("/tentang", "ℹ️ About")],
}

FAM_NAME_EN = {"des": "Experimental Design", "reg": "Regression"}

# Metadata halaman berbahasa Inggris (kunci = nama halaman). {x} diisi dari argumen meta_vars.
META_EN = {
    "home": dict(
        title="GetComput – Learn Statistics Online with Built-in Calculators (ANOVA, Experimental Design, Regression)",
        description="Learn statistics step by step: 62 modules with equations, worked examples, and practice, from the basics through experimental design to advanced regression. "
                    "Includes calculators for ANOVA, post-hoc tests, and regression.",
        hero_title="Learn statistics, then practise it",
        hero_lead="GetComput is a statistics learning site: 62 modules with concepts, equations, worked examples, and exercises. "
                  "The built-in calculators let you practise every topic with your own data.",
        hero_tags=["62 learning modules", "Equations & worked examples", "Calculators for practice", "Free"]),
    "family_des": dict(
        title="Experimental Design Calculators – GetComput",
        description="Analysis of variance for controlled experiments: from CRD and RCBD to advanced designs.",
        hero_title="Experimental Design",
        hero_lead="Analysis of variance for controlled experiments: from CRD and RCBD to advanced designs."),
    "family_reg": dict(
        title="Regression Calculators – GetComput",
        description="From multiple linear regression to models for binary, count, and positive responses.",
        hero_title="Regression",
        hero_lead="From multiple linear regression to models for binary, count, and positive responses."),
    "method": dict(
        title="{t} – Online Calculator | GetComput",
        description="{d} Calculate online: result tables, assumption tests, charts, and automatic interpretation."),
    "guide": dict(
        title="How to Choose a Statistical Method – GetComput",
        description="Not sure which method to use? See when each experimental design and regression method applies.",
        hero_title="Method Guide",
        hero_lead="Pick the situation that matches your data or experiment; we show the right method and open it for you.",
        hero_tags=["Experimental design", "Regression"]),
    "learn": dict(
        title="Learn Statistics: Learning Path and Exercises – GetComput",
        description="A step-by-step statistics learning path from the basics to experimental design and regression, with hands-on practice in the calculators.",
        hero_title="Learn Statistics",
        hero_lead="Learn the concept first, then practise it right in the calculator. Follow the ordered path from the basics to advanced methods.",
        hero_tags=["Short lessons", "Ordered path", "Practice in the calculator"]),
    "module": dict(
        title="Lesson: {t} – Learn Statistics | GetComput", description="{d}"),
    "flow": dict(
        title="Analysis Flow for Each Method (Flowchart) – GetComput",
        description="See the order of steps for each statistical method: data input, assumption checks, decisions, and results.",
        hero_title="Analysis Flow for Each Method",
        hero_lead="See the sequence from data input and assumption checks to results. Choose a method below.",
        hero_tags=["Flowchart", "Assumptions & decisions", "Results"]),
    "feedback": dict(
        title="Send Feedback – GetComput",
        description="Send feature suggestions, problem reports, or questions to the GetComput developer.",
        hero_title="Send Feedback",
        hero_lead="Found a flaw, need a new method, or have a question? Write it here; the developer reads every message.",
        hero_tags=["Feature ideas", "Problem reports", "Questions"]),
    "about": dict(
        title="About GetComput", description="About GetComput: a statistics learning site with built-in calculators.",
        hero_title="About GetComput", hero_lead="How to read the results, calculation assumptions, and limitations to be aware of.",
        hero_tags=["Guide to reading results"]),
    "privacy": dict(
        title="Privacy Policy & Disclaimer – GetComput", description="GetComput privacy policy and disclaimer.",
        hero_title="Privacy Policy & Disclaimer", hero_lead="How your data is handled and the limits of the service's liability."),
    "notfound": dict(
        title="Page not found – GetComput", description="Page not found.",
        hero_title="Page not found", hero_lead="The address you opened is not available."),
}

SEARCH_EXTRA_EN = [
    ("Statistics Learning Path", "/belajar", "learn lessons modules statistics basics experimental design regression exercises"),
    ("How to Choose a Method", "/panduan", "choose situation data when to use confused which method"),
    ("Method Flow (flowchart)", "/alur-metode", "flowchart analysis steps for each method"),
    ("Send Feedback", "/masukan", "feedback suggestion bug report question"),
    ("About GetComput", "/tentang", "about how to read results methodology notes"),
    ("Privacy Policy & Disclaimer", "/privasi", "privacy cookies disclaimer ads"),
]


def lang_of(request):
    return getattr(request.state, "lang", "id")


def is_en(request):
    return lang_of(request) == "en"


class LangMiddleware:
    """/en/... -> path tanpa awalan, request.state.lang = 'en'."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            p = scope["path"]
            st = dict(scope.get("state") or {})
            if p == "/en" or p.startswith("/en/"):
                rest = p[3:] or "/"
                scope = dict(scope)
                scope["path"] = rest
                scope["raw_path"] = rest.encode()
                st["lang"] = "en"
            else:
                st["lang"] = "id"
            scope["state"] = st
        await self.app(scope, receive, send)


_SKIP = ("/static/", "/api/", "/favicon", "/robots.txt", "/sitemap.xml", "/ads.txt", "/healthz", "/en/", "//")


def localize_links(html):
    """Tambahkan awalan /en pada tautan internal href=\"/...\" (kecuali aset, API, dan berkas khusus)."""
    def fix(m):
        p = m.group(1)
        if p == "/":
            return 'href="/en/"'
        if p.startswith(_SKIP) or p == "/en":
            return m.group(0)
        return f'href="/en{p}"'
    return re.sub(r'href="(/[^"]*)"', fix, html)


# Nama kelompok/tahap untuk antarmuka Inggris (filter Jinja `en`; teks lain dikembalikan apa adanya)
TR_EN = {
    "Dasar": "Basics", "Data Terstruktur": "Structured Data", "GLM": "GLM", "Nonlinear": "Nonlinear",
    "Optimasi Proses": "Process Optimisation", "Pengukuran Berulang": "Repeated Measures",
    "Peubah Pendamping & Multivariat": "Covariates & Multivariate", "Rancangan Dasar": "Basic Designs",
    "Rancangan Lingkungan": "Environmental Designs", "Rancangan Perlakuan": "Treatment Designs",
    "Robust & Nonparametrik": "Robust & Nonparametric", "Seleksi & Regularisasi": "Selection & Regularisation",
    "Dasar statistika": "Statistics basics",
    "Tahap 1 · Dasar statistika": "Stage 1 · Statistics basics", "Tahap 2 · Rancangan percobaan": "Stage 2 · Experimental design",
    "Tahap 3 · Regresi": "Stage 3 · Regression",
}


def tr(s):
    return TR_EN.get(s, s)

FEEDBACK_CAT_EN = ["💡 Feature / new method suggestion", "🐞 Problem report (bug)", "❓ Question", "👍 Impressions & comments", "📝 Other"]


def loc_method(m, en=True):
    """Salinan metode dengan teks Inggris (judul, deskripsi, tag, dll.) bila tersedia."""
    if not en:
        return m
    from .i18n_data import METHODS_EN
    from .i18n_data.fields import FIELDS_EN, HELP_EN
    t = METHODS_EN.get(m["slug"])
    o = dict(m)
    o["group"] = tr(m["group"])
    if t:
        o.update(title=t[0], desc=t[1], tags=list(t[2]), when=t[3], assume=t[4], read=t[5])
        o["label"] = t[0]
    o["fields"] = [dict(f, label=FIELDS_EN.get(f["label"], f["label"]), **({"help": HELP_EN.get(f["help"], f["help"])} if f.get("help") else {})) for f in m["fields"]]
    return o


def loc_groups(groups, en=True):
    if not en:
        return groups
    return {tr(g): [loc_method(m) for m in items] for g, items in groups.items()}


# ---- penerjemah hasil perhitungan (HTML) untuk mode Inggris ----
_NUM = r"(-?\d+(?:[.,]\d+)?(?:e[+-]?\d+)?)"
_RES = None


def _load_res():
    global _RES
    if _RES is not None:
        return _RES
    from .i18n_data import res1, res2, res3, res4, res5
    exact, frag = {}, []
    for m in (res1, res2, res3, res4, res5):
        exact.update(getattr(m, "EXACT", {}))
        frag += getattr(m, "FRAG", [])
    comp = []
    for ind, eng in sorted(frag, key=lambda p: -len(p[0])):
        pat = re.escape(ind).replace(r"\#", _NUM).replace(r"\{\}", r"(.+?)")
        if re.match(r"\w", ind):
            pat = r"(?<![\w])" + pat
        if re.search(r"\w$", ind):
            pat += r"(?![\w])"
        parts = re.split(r"(#|\{\})", eng)
        n = 0
        out = []
        for p in parts:
            if p in ("#", "{}"):
                n += 1
                out.append(("g", n))
            elif p:
                out.append(("t", p))
        comp.append((re.compile(pat), out))
    _RES = (exact, comp)
    return _RES


def _norm(t):
    return re.sub(r"-?\d+(?:[.,]\d+)?(?:e[+-]?\d+)?", "#", t)


def tr_text(t):
    """Terjemahkan satu potongan teks hasil (Indonesia -> Inggris)."""
    exact, comp = _load_res()
    s = t.strip()
    if not s or not re.search(r"[A-Za-z]{2,}", s):
        return t
    lead, trail = t[:len(t) - len(t.lstrip())], t[len(t.rstrip()):]
    if s in exact:
        return lead + exact[s] + trail
    out = s
    for rx, parts in comp:
        def sub(m, parts=parts):
            return "".join(p if k == "t" else m.group(p) for k, p in parts)
        out = rx.sub(sub, out)
    out = re.sub(r"(?<=\d),(?=\d)", ".", out) if out != s else out
    return lead + out + trail


def tr_html(html):
    """Terjemahkan simpul teks HTML hasil; tag, angka, dan nama data tidak diubah. Juga string di JSON grafik."""
    import html as _h
    import json as _j

    def node(m):
        raw = m.group(1)
        t = _h.unescape(raw)
        o = tr_text(t)
        return ">" + (raw if o == t else _h.escape(o, quote=False)) + "<"

    def plot(m):
        try:
            d = _j.loads(_h.unescape(m.group(2)) if "&quot;" in m.group(2) else m.group(2))
        except Exception:  # noqa: BLE001
            return m.group(0)

        def walk(x, key=""):
            if isinstance(x, str):
                return tr_text(x) if key in ("text", "title", "name", "label", "ticktext", "hovertemplate") or True else x
            if isinstance(x, list):
                return [walk(i, key) for i in x]
            if isinstance(x, dict):
                return {k: (v if k in ("x", "y", "z", "lat", "lon") and not isinstance(v, str) else walk(v, k)) for k, v in x.items()}
            return x
        return m.group(1) + _j.dumps(walk(d), ensure_ascii=False).replace("<", "\\u003c") + m.group(3)

    html = re.sub(r"(<script[^>]*type=\"application/json\"[^>]*>)(.*?)(</script>)", plot, html, flags=re.S)
    return re.sub(r">([^<>]+)<", node, html)


_ERR = None


def tr_err(msg):
    global _ERR
    if _ERR is None:
        from .i18n_data.errors import FRAG
        comp = []
        for ind, eng in sorted(FRAG, key=lambda p: -len(p[0])):
            pat = re.escape(ind).replace(r"\#", _NUM).replace(r"\{\}", r"(.+?)")
            parts, n, out = re.split(r"(#|\{\})", eng), 0, []
            for p in parts:
                if p in ("#", "{}"):
                    n += 1
                    out.append(("g", n))
                elif p:
                    out.append(("t", p))
            comp.append((re.compile(pat), out))
        _ERR = comp
    out = msg
    for rx, parts in _ERR:
        out = rx.sub(lambda m, parts=parts: "".join(p if k == "t" else m.group(p) for k, p in parts), out)
    from .i18n_data.fields import FIELDS_EN
    return re.sub(r"“([^”]+)”", lambda m: "“" + FIELDS_EN.get(m.group(1), m.group(1)) + "”", out)


def tr_sheets(sheets):
    """Terjemahkan nama lembar, judul kolom, dan sel teks umum pada ekspor Excel."""
    import pandas as pd
    out = {}
    for name, df in sheets.items():
        try:
            d = df.copy()
            d.columns = [tr_text(str(c)) for c in d.columns]
            for c in d.columns:
                if d[c].dtype == object:
                    d[c] = d[c].map(lambda v: tr_text(v) if isinstance(v, str) else v)
            if not isinstance(d.index, pd.RangeIndex) and d.index.dtype == object:
                d.index = [tr_text(str(i)) for i in d.index]
            out[tr_text(str(name))[:31]] = d
        except Exception:  # noqa: BLE001
            out[name] = df
    return out


# ---- modul belajar ----
_MATH = re.compile(r"\\\(.*?\\\)", re.S)


def _mn(x):
    return [_ABBR_RE.sub(lambda k: _ABBR[k.group(1)], m.replace("{,}", ".")) for m in _MATH.findall(x)]


def mod_en():
    from .i18n_data.mods import MOD_EN
    return MOD_EN


_ABBR = {"FK": "CF", "db": "df", "JKT": "SSTO", "JKP": "SSTR", "JKG": "SSE", "KTP": "MSTR", "KTG": "MSE", "JK": "SS", "KT": "MS", "KK": "CV", "BNT": "LSD", "BNJ": "HSD", "JKR": "SSR", "JKS": "SSL", "JKK": "SSB", "KTK": "MSB"}
_ABBR_RE = re.compile(r"(?<![A-Za-z\\])(" + "|".join(sorted(_ABBR, key=len, reverse=True)) + r")(?![A-Za-z])")


def _eqt(t):
    from .i18n_data.eqtext import EQTEXT
    if t in EQTEXT:
        return EQTEXT[t]
    core = t.strip()
    for k in (core, core + " ", " " + core):
        if k in EQTEXT:
            return t[:len(t) - len(t.lstrip())] + EQTEXT[k].strip() + t[len(t.rstrip()):]
    return t


def tr_eq(e):
    """Persamaan LaTeX untuk mode Inggris: koma desimal {,} -> titik dan kata Indonesia di \\text{} diterjemahkan."""
    from .i18n_data.eqtext import EQTEXT
    e = e.replace("{,}", ".")
    e = _ABBR_RE.sub(lambda m: _ABBR[m.group(1)], e)
    e = re.sub(r"(?<![A-Za-z\\])(JK|KT)([A-Z]{1,2})(?![A-Za-z])", lambda m: ("SS" if m.group(1) == "JK" else "MS") + m.group(2), e)
    return re.sub(r"(\\(?:text|mathrm|mathit|operatorname)\{)([^}]*)(\})", lambda m: m.group(1) + _eqt(m.group(2)) + m.group(3), e)


def loc_module(mod, ext, en=True):
    """Kembalikan (mod, ext) berbahasa Inggris bila terjemahannya ada; persamaan LaTeX diambil dari aslinya."""
    t = mod_en().get(mod["slug"]) if en else None
    if not t:
        return mod, ext
    m = dict(mod)
    m["tahap"] = tr(mod["tahap"])
    for k in ("title", "ringkas", "tujuan", "ide", "langkah", "baca", "jebakan", "latihan"):
        m[k] = t[k]
    m["rumus"] = [tuple(r) for r in t["rumus"]]
    e = ext
    if ext and "teori" in t:
        e = dict(ext)
        e["notasi"] = [(tr_eq(sym), a) for (sym, _), a in zip(ext["notasi"], t["notasi"])]
        e["teori"] = [(h, list(p), [tr_eq(x) for x in eq]) for (_, _, eq), (h, p) in zip(ext["teori"], t["teori"])]
        c, tc = ext["contoh"], t["contoh"]
        e["contoh"] = dict(judul=tc["judul"], soal=tc["soal"], data=tc.get("data"),
                           langkah=[(txt, tr_eq(eq) if eq else eq) for (_, eq), txt in zip(c["langkah"], tc["langkah"])], simpul=tc["simpul"])
        e["faq"] = [tuple(f) for f in t["faq"]]
    return m, e


def loc_module_brief(mod, en=True):
    t = mod_en().get(mod["slug"]) if en else None
    if not t:
        return mod
    m = dict(mod)
    m["title"], m["ringkas"] = t["title"], t["ringkas"]
    return m


def check_module(slug):
    """Periksa terjemahan: panjang daftar sama dan segmen \\( ... \\) identik. Kembalikan daftar masalah."""
    from . import belajar
    mod, ext = belajar.MODULES[slug], belajar.TEORI.get(slug)
    t = mod_en().get(slug)
    bad = []
    if not t:
        return ["tidak ada"]

    def same(a, b, where):
        if len(a) != len(b):
            bad.append(f"{where}: panjang {len(a)} != {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            if isinstance(x, (list, tuple)):
                same(x, y, f"{where}[{i}]")
            elif isinstance(x, str) and _mn(x) != _mn(y):
                bad.append(f"{where}[{i}]: math berbeda")
    for k in ("tujuan", "ide", "langkah", "baca", "jebakan"):
        same(mod[k], t[k], k)
    same([list(r) for r in mod["rumus"]], [list(r) for r in t["rumus"]], "rumus")
    if ext:
        same([a for _, a in ext["notasi"]], t.get("notasi", []), "notasi")
        same([[h, p] for h, p, _ in ext["teori"]], [list(x) for x in t.get("teori", [])], "teori")
        c = ext["contoh"]
        if "contoh" not in t:
            bad.append("contoh hilang")
        else:
            tc = t["contoh"]
            same([x[0] for x in c["langkah"]], tc["langkah"], "contoh.langkah")
            if c.get("data"):
                same(c["data"], tc.get("data") or [], "contoh.data")
            same([c["soal"], c["simpul"]], [tc["soal"], tc["simpul"]], "contoh.teks")
        same([list(f) for f in ext["faq"]], [list(f) for f in t.get("faq", [])], "faq")
    return bad


def _fill_en_modules():
    EN_MODULES.update(mod_en().keys())
    from . import belajar
    if set(belajar.ORDER) <= EN_MODULES:  # seluruh modul sudah diterjemahkan -> indeks belajar siap
        READY_PATHS.add("/belajar")


_fill_en_modules()


# ------------------------------------------------------------------ materi lengkap (pendalaman)
def loc_lengkap(slug, en=False):
    """Materi lengkap untuk satu modul. Versi Inggris hanya bila terjemahannya ada (jika tidak, None)."""
    from . import belajar
    lk = belajar.LENGKAP.get(slug)
    if not lk or not en:
        return lk
    from .i18n_data.lengkap_en import LENGKAP_EN
    t = LENGKAP_EN.get(slug)
    if not t:
        return None
    out = dict(ref=lk["ref"], soal=t["soal"],
               teori=[(h, list(p), [tr_eq(x) for x in eq]) for (_, _, eq), (h, p) in zip(lk["teori"], t["teori"])], contoh2=None)
    c, tc = lk.get("contoh2"), t.get("contoh2")
    if c and tc:
        out["contoh2"] = dict(judul=tc["judul"], soal=tc["soal"], data=tc.get("data"),
                              langkah=[(txt, tr_eq(eq) if eq else eq) for (_, eq), txt in zip(c["langkah"], tc["langkah"])], simpul=tc["simpul"])
    return out


def check_lengkap(slug):
    """Periksa terjemahan materi lengkap: panjang daftar sama dan segmen \\( ... \\) identik."""
    from . import belajar
    from .i18n_data.lengkap_en import LENGKAP_EN
    lk, t = belajar.LENGKAP.get(slug), LENGKAP_EN.get(slug)
    if not lk:
        return ["tidak ada (ID)"]
    if not t:
        return ["tidak ada (EN)"]
    bad = []

    def same(a, b, where):
        if len(a) != len(b):
            bad.append(f"{where}: panjang {len(a)} != {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            if isinstance(x, (list, tuple)):
                same(x, y, f"{where}[{i}]")
            elif isinstance(x, str) and _mn(x) != _mn(y):
                bad.append(f"{where}[{i}]: math berbeda")
    same([[h, p] for h, p, _ in lk["teori"]], [list(x) for x in t["teori"]], "teori")
    same([list(s) for s in lk["soal"]], [list(s) for s in t["soal"]], "soal")
    c, tc = lk.get("contoh2"), t.get("contoh2")
    if c:
        if not tc:
            bad.append("contoh2 hilang")
        else:
            same([x[0] for x in c["langkah"]], tc["langkah"], "contoh2.langkah")
            if c.get("data"):
                same(c["data"], tc.get("data") or [], "contoh2.data")
            same([c["soal"], c["simpul"]], [tc["soal"], tc["simpul"]], "contoh2.teks")
    return bad
