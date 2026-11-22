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
EN_METHODS = set()     # slug metode yang sudah punya terjemahan lengkap
EN_MODULES = set()     # slug modul belajar yang sudah punya terjemahan lengkap

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
