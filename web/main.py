"""main.py – aplikasi web GetComput (Starlette). Jalankan: uvicorn web.main:app --host 0.0.0.0 --port $PORT"""
import asyncio
import json
import logging
import os, re
import sys
import time
import traceback
from collections import defaultdict, deque
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from starlette.applications import Starlette  # noqa: E402
from starlette.concurrency import run_in_threadpool  # noqa: E402
from starlette.middleware import Middleware  # noqa: E402
from starlette.middleware.gzip import GZipMiddleware  # noqa: E402
from starlette.requests import Request  # noqa: E402
from starlette.responses import JSONResponse, PlainTextResponse, RedirectResponse, Response  # noqa: E402
from starlette.routing import Mount, Route  # noqa: E402
from starlette.staticfiles import StaticFiles  # noqa: E402
from starlette.responses import FileResponse  # noqa: E402
from starlette.templating import Jinja2Templates  # noqa: E402

import flows  # noqa: E402
from web import belajar, metode_extra, core, feedback_web, guide_data, i18n, registry, render  # noqa: E402
from web.i18n import lang_of  # noqa: E402
from starlette.responses import HTMLResponse  # noqa: E402

log = logging.getLogger("getcomput")
HERE = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(HERE, "templates"))
templates.env.filters["en"] = i18n.tr

SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")          # mis. https://namadomain.com
PRIMARY_HOST = os.environ.get("PRIMARY_HOST", "").strip().lower()  # bila diisi, host lain dialihkan permanen ke sini
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "").strip()
GOATCOUNTER = os.environ.get("GOATCOUNTER_CODE", "").strip().lower()
if not GOATCOUNTER.replace("-", "").isalnum():
    GOATCOUNTER = ""
GA_ID = os.environ.get("GA_MEASUREMENT_ID", "").strip().upper()  # contoh: G-ABCD123456
if not re.fullmatch(r"G-[A-Z0-9]{6,14}", GA_ID):
    GA_ID = ""
ADSENSE = os.environ.get("ADSENSE_CLIENT", "").strip().lower()  # contoh: ca-pub-1234567890123456
if not re.fullmatch(r"ca-pub-\d{10,20}", ADSENSE):
    ADSENSE = ""
ASSET_V = os.environ.get("ASSET_V") or str(int(max((os.path.getmtime(os.path.join(os.path.dirname(__file__), "static", f)) for f in os.listdir(os.path.join(os.path.dirname(__file__), "static"))), default=1)))
MAX_BODY = 4_500_000
ALPHAS = (0.01, 0.05, 0.10)
NAV = [("/", "🏠 Beranda"), ("/belajar", "🎓 Belajar"), ("/rancangan-percobaan", "🧪 Alat Rancangan"), ("/regresi", "📈 Alat Regresi"),
       ("/panduan", "🧭 Panduan Metode"), ("/alur-metode", "🗺️ Alur Metode"), ("/masukan", "💬 Masukan"), ("/tentang", "ℹ️ Tentang")]
SEM = asyncio.Semaphore(2)
_hits = defaultdict(deque)


# ------------------------------------------------------------------ util
def base_url(request):
    if SITE_URL:
        return SITE_URL
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    return f"{proto}://{request.headers.get('host', request.url.netloc)}"


def search_index(lang="id"):
    en = lang == "en"
    pre = "/en" if en else ""
    items = []
    for m0 in registry.METHODS:
        m = i18n.loc_method(m0, en)
        items.append({"t": m["title"], "u": f"{pre}/metode/{m['slug']}", "d": m["desc"], "k": " ".join(m["tags"]) + f" {m['key']} {m['slug']}",
                      "g": f"{(i18n.FAM_NAME_EN if en else registry.FAM_NAME)[m['family']]} › {m['group']}"})
    for slug in belajar.ORDER:
        mod = belajar.MODULES[slug]
        items.append({"t": ("Learn: " if en else "Belajar: ") + mod["title"], "u": f"{pre}/belajar/{slug}", "d": mod["ringkas"], "k": "materi modul belajar belajar statistika lesson module learn",
                      "g": ("Lessons › " if en else "Materi belajar › ") + mod["tahap"]})
    extra = i18n.SEARCH_EXTRA_EN if en else [("Jalur Belajar Statistika", "/belajar", "belajar materi modul statistika dasar rancangan percobaan regresi latihan"),
                    ("Panduan Memilih Metode", "/panduan", "pilih situasi data kapan dipakai bingung memilih"),
                    ("Alur Metode (flowchart)", "/alur-metode", "flowchart alur langkah analisis tiap metode"),
                    ("Kirim Masukan", "/masukan", "masukan saran bug laporan pertanyaan kesan"),
                    ("Tentang GetComput", "/tentang", "tentang cara membaca hasil catatan metodologi"),
                    ("Kebijakan Privasi & Penafian", "/privasi", "privasi cookie penafian iklan")]
    for t, u, d in extra:
        items.append({"t": t, "u": pre + u, "d": d, "k": "", "g": "Information pages" if en else "Halaman informasi"})
    return json.dumps(items, ensure_ascii=False).replace("<", "\\u003c")


async def search_index_json(request):
    lang = "en" if request.path_params.get("lang") == "en" else "id"
    return Response(search_index(lang), media_type="application/json")


def page(request, name, *, title="", description="", path, hero_title="", hero_lead="", hero_tags=None, active=None, status=200,
         key=None, meta_vars=None, ready=None, **ctx):
    lang = lang_of(request)
    en = lang == "en"
    if en and key in i18n.META_EN:           # metadata berbahasa Inggris menggantikan teks Indonesia
        me = i18n.META_EN[key]
        mv = meta_vars or {}
        title = me.get("title", title).format(**mv) if mv else me.get("title", title)
        description = me.get("description", description).format(**mv) if mv else me.get("description", description)
        hero_title = me.get("hero_title", hero_title).format(**mv) if mv and "hero_title" in me else me.get("hero_title", hero_title)
        hero_lead = me.get("hero_lead", hero_lead).format(**mv) if mv and "hero_lead" in me else me.get("hero_lead", hero_lead)
        hero_tags = me.get("hero_tags", hero_tags)
    if ready is None:
        ready = path in i18n.READY_PATHS
    b = base_url(request)
    p_en = "/en" + ("" if path != "/" else "/") + (path if path != "/" else "")
    act = active if active is not None else path
    pk = ("hero" if path == "/" else "group" if path == "/belajar" else "books" if path.startswith("/belajar/") else
          "field" if act == "/rancangan-percobaan" else "charts" if act == "/regresi" else "notes" if act in ("/panduan", "/alur-metode") else "books")
    ctx.setdefault("hero_photo", HOME_PHOTOS[pk][0])
    ctx.update(site_base=b, title=title, description=description, canonical=b + (p_en if en else path), hero_title=hero_title, hero_lead=hero_lead,
               hero_tags=hero_tags, nav_items=i18n.NAV[lang], active=active if active is not None else path,
               asset_v=ASSET_V, goatcounter=GOATCOUNTER, adsense=ADSENSE, ga_id=GA_ID, jsonld=ctx.get("jsonld"), request=request,
               lang=lang, ready_en=ready, noindex=(en and not ready), alt_id=b + path,
               alt_en=b + ("/en/" if path == "/" else "/en" + path), qs=("?" + request.url.query) if request.url.query else "")
    tpl = f"en/{name}" if en and os.path.exists(os.path.join(HERE, "templates", "en", name)) else name
    html = templates.env.get_template(tpl).render(**ctx)
    if en:
        html = i18n.localize_links(html)
    return HTMLResponse(html, status_code=status)


def contact_html(en=False):
    if CONTACT_EMAIL:
        pre = "Contact us at" if en else "Hubungi kami melalui"
        return f'{pre} <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.'
    return ('You can also reach the developer through the <a href="/masukan">feedback form</a>; include your email if you would like a reply.' if en
            else 'Anda juga dapat menghubungi pengembang melalui <a href="/masukan">formulir masukan</a>; sertakan email Anda bila ingin dibalas.')


def client_ip(request):
    fwd = request.headers.get("x-forwarded-for")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "?")


RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "60"))   # perhitungan per IP per menit


def too_many(request, limit=None, window=60, bucket=""):
    limit = limit or RATE_LIMIT
    ip, now = client_ip(request) + bucket, time.time()
    q = _hits[ip]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= limit:
        return True
    q.append(now)
    if len(_hits) > 5000:
        for k in [k for k, v in _hits.items() if not v or now - v[-1] > window]:
            _hits.pop(k, None)
    return False


async def read_json(request):
    cl = request.headers.get("content-length")
    if cl and cl.isdigit() and int(cl) > MAX_BODY:
        raise core.InputError("Data terlalu besar (maksimal sekitar 4 MB).")
    body = await request.body()
    if len(body) > MAX_BODY:
        raise core.InputError("Data terlalu besar (maksimal sekitar 4 MB).")
    try:
        data = json.loads(body or b"{}")
    except Exception:
        raise core.InputError("Permintaan tidak valid.")
    if isinstance(data, dict) and data.get("lang") == "en":
        REQ_LANG.set("en")
    return data


# ------------------------------------------------------------------ halaman
# Foto halaman depan: Unsplash (lisensi Unsplash, bebas dipakai). (id foto, fotografer, halaman sumber)
HOME_PHOTOS = {
    "hero": ("photo-1758270705290-62b6294dd044", "Vitaly Gariev", "https://unsplash.com/photos/kp7qkHTgSKc"),
    "group": ("photo-1762512346988-045f4d5ad2b3", "Jaykumar Bherwani", "https://unsplash.com/photos/Dg8WzlOE1as"),
    "books": ("photo-1499447155021-4907f71b9ef5", "CHUTTERSNAP", "https://unsplash.com/photos/984e1Fk4E04"),
    "notes": ("photo-1654022963276-ef761eac346e", "Benoît Deschasaux", "https://unsplash.com/photos/O04ybN0h1C8"),
    "field": ("photo-1788122290883-6587385ffb8c", "Bernd Dittrich", "https://unsplash.com/photos/f8Yj2_dxZJk"),
    "charts": ("photo-1763568258367-1c52beb60be7", "Daniil Komov", "https://unsplash.com/photos/GQOylIn892U"),
}


def _home_stages():
    out = []
    for slug in belajar.ORDER:
        t = belajar.MODULES[slug]["tahap"]
        if not out or out[-1]["tahap"] != t:
            out.append({"tahap": t, "n": 0, "first": slug})
        out[-1]["n"] += 1
    return out


async def home(request):
    g = {f: i18n.loc_groups(registry.groups(f), lang_of(request) == "en") for f in (registry.FAM_DES, registry.FAM_REG)}
    n_des = sum(len(v) for v in g["des"].values())
    n_reg = sum(len(v) for v in g["reg"].values())
    return page(request, "home.html", key="home", title="GetComput – Belajar Statistika Online dengan Alat Hitung (ANOVA, Rancangan Percobaan, Regresi)",
                description="Belajar statistika berbahasa Indonesia: 62 modul dengan persamaan, contoh hitung, dan latihan, dari dasar, rancangan percobaan, sampai regresi lanjutan. "
                            "Dilengkapi alat hitung ANOVA, uji lanjut, dan regresi untuk berlatih.",
                path="/", hero_title="Belajar statistika, lalu praktikkan",
                hero_lead="GetComput adalah web pembelajaran statistika berbahasa Indonesia: 62 modul dengan konsep, persamaan, contoh hitung, dan latihan. "
                          "Alat hitung di dalamnya membantu Anda mempraktikkan setiap materi dengan data sendiri.",
                hero_tags=["62 modul belajar", "Persamaan & contoh hitung", "Alat hitung untuk latihan", "Gratis"],
                groups=g, n_des=n_des, n_reg=n_reg, n_all=n_des + n_reg, photos=HOME_PHOTOS, stages=_home_stages(), n_mod=len(belajar.ORDER),
                jsonld=json.dumps({"@context": "https://schema.org", "@type": "WebApplication", "name": "GetComput", "applicationCategory": "EducationalApplication",
                                   "inLanguage": lang_of(request), "operatingSystem": "Web", "url": base_url(request) + "/",
                                   "description": "Web pembelajaran statistika dengan alat hitung untuk berlatih."}, ensure_ascii=False))


async def family_page(request):
    path = request.url.path.rstrip("/")
    fam = registry.FAM_DES if path == "/rancangan-percobaan" else registry.FAM_REG
    name = (i18n.FAM_NAME_EN if lang_of(request) == "en" else registry.FAM_NAME)[fam]
    lead = ("Analisis ragam untuk percobaan terkontrol: dari RAL dan RAK sampai rancangan lanjutan." if fam == registry.FAM_DES
            else "Dari regresi linear berganda sampai model untuk data biner, cacahan, dan respon positif.")
    return page(request, "catalog.html", key=f"family_{fam}", title=f"{name} – GetComput", description=lead, path=path, hero_title=name, hero_lead=lead,
                groups=i18n.loc_groups(registry.groups(fam), lang_of(request) == "en"), fam_name=name)


async def method_page(request):
    m = registry.BY_SLUG.get(request.path_params["slug"])
    if not m:
        return await not_found(request, None)
    en = lang_of(request) == "en"
    path = f"/metode/{m['slug']}"
    related = [i18n.loc_method(x, en) for x in registry.METHODS if x["family"] == m["family"] and x["slug"] != m["slug"] and x["group"] == m["group"]][:3]
    mod_ = belajar.MODULES.get(m["slug"])
    m = i18n.loc_method(m, en)
    fields = [{k: v for k, v in f.items()} for f in m["fields"]]
    spec = json.dumps({"slug": m["slug"], "fields": fields, "key": m["key"], "family": m["family"], "gen": m.get("gen")}, ensure_ascii=False).replace("<", "\\u003c")
    flow = flows.flow_html(flows.nodes_for(m["key"], m["family"], lang_of(request)), lang_of(request))
    ld = json.dumps({"@context": "https://schema.org", "@type": "WebApplication", "name": m["title"], "applicationCategory": "EducationalApplication",
                     "inLanguage": lang_of(request), "url": base_url(request) + path, "description": m["desc"]}, ensure_ascii=False)
    gen = json.dumps(m["gen"], ensure_ascii=False).replace("<", "\\u003c") if m.get("gen") else "null"
    return page(request, "method.html", key="method", meta_vars={"t": m["title"], "d": m["desc"]}, ready=m["slug"] in i18n.EN_METHODS, title=f"{m['title']} – Kalkulator Online | GetComput",
                description=f"{m['desc']} Hitung online: tabel hasil, uji asumsi, grafik, dan interpretasi otomatis.", path=path, active="/" + registry.FAM_PATH[m["family"]],
                hero_title=m["title"], hero_lead=m["desc"], hero_tags=m["tags"], m=m, fam_name=(i18n.FAM_NAME_EN if lang_of(request) == "en" else registry.FAM_NAME)[m["family"]],
                fam_path=registry.FAM_PATH[m["family"]], related=related, spec=spec, flow=flow, jsonld=ld, module=mod_,
                ext=i18n.loc_extra(m["slug"], en))


async def guide(request):
    return page(request, "guide.html", key="guide", title="Panduan Memilih Metode Analisis Statistika – GetComput",
                description="Bingung memilih metode? Lihat kapan tiap rancangan percobaan dan metode regresi dipakai.", path="/panduan",
                hero_title="Panduan Memilih Metode", hero_lead="Pilih situasi data atau percobaan Anda; kami tunjukkan metode yang cocok dan membukanya langsung.",
                hero_tags=["Rancangan percobaan", "Regresi"], rows=guide_data.rows(lang_of(request)),
                groups={f: i18n.loc_groups(registry.groups(f), lang_of(request) == "en") for f in (registry.FAM_DES, registry.FAM_REG)})


def _learn_stages(en=False):
    """Kelompokkan modul menurut tahap, lalu menurut kelompok metode (bila ada)."""
    out = []
    for slug in belajar.ORDER:
        mod = belajar.MODULES[slug]
        meth = registry.BY_SLUG.get(slug)
        grp = meth["group"] if meth else "Dasar statistika"
        if not out or out[-1]["tahap"] != mod["tahap"]:
            out.append({"tahap": mod["tahap"], "groups": []})
        gs = out[-1]["groups"]
        if not gs or gs[-1]["name"] != grp:
            gs.append({"name": grp, "mods": []})
        gs[-1]["mods"].append(i18n.loc_module_brief(mod, en))
    return out


async def learn_index(request):
    return page(request, "belajar.html", key="learn", title="Belajar Statistika: Jalur Materi dan Latihan – GetComput",
                description="Jalur belajar statistika berbahasa Indonesia dari dasar sampai rancangan percobaan dan regresi, dengan latihan langsung di kalkulator.",
                path="/belajar", hero_title="Belajar Statistika",
                hero_lead="Pelajari konsepnya dulu, lalu praktikkan langsung di kalkulator. Ikuti jalur berurutan dari dasar sampai metode lanjutan.",
                hero_tags=["Materi ringkas", "Jalur berurutan", "Latihan di kalkulator"], stages=_learn_stages(lang_of(request) == "en"), total=len(belajar.ORDER),
                order=json.dumps(belajar.ORDER))


async def learn_module(request):
    mod0 = belajar.MODULES.get(request.path_params["slug"])
    if not mod0:
        return await not_found(request, None)
    en = lang_of(request) == "en"
    mod, ext = i18n.loc_module(mod0, belajar.TEORI.get(mod0["slug"]), en)
    i = belajar.ORDER.index(mod["slug"])
    prev = i18n.loc_module_brief(belajar.MODULES[belajar.ORDER[i - 1]], en) if i > 0 else None
    nxt = i18n.loc_module_brief(belajar.MODULES[belajar.ORDER[i + 1]], en) if i + 1 < len(belajar.ORDER) else None
    own = i18n.loc_method(registry.BY_SLUG.get(mod["slug"]), en) if registry.BY_SLUG.get(mod["slug"]) else None
    prac = i18n.loc_method(registry.BY_SLUG.get(mod["method"]), en) if mod["method"] else None
    ld = json.dumps({"@context": "https://schema.org", "@type": "LearningResource", "name": mod["title"], "inLanguage": lang_of(request), "description": mod["ringkas"],
                     "learningResourceType": "Learning material" if en else "Materi belajar", "educationalLevel": mod["tahap"]}, ensure_ascii=False)
    return page(request, "modul.html", key="module", meta_vars={"t": mod["title"], "d": mod["ringkas"]}, ready=mod["slug"] in i18n.EN_MODULES, title=f"Materi: {mod['title']} – Belajar Statistika | GetComput", description=mod["ringkas"],
                path=f"/belajar/{mod['slug']}", active="/belajar", hero_title=mod["title"], hero_lead=mod["ringkas"], hero_tags=[mod["tahap"]],
                mod=mod, idx=i + 1, total=len(belajar.ORDER), prev=prev, nxt=nxt, own=own, prac=prac, lk=i18n.loc_lengkap(mod0["slug"], en),
                pras=[i18n.loc_module_brief(belajar.MODULES[p], en) for p in mod["pra"]], ext=ext, jsonld=ld)


async def flow_page(request):
    fam = request.query_params.get("fam", "des")
    fam = fam if fam in ("des", "reg") else "des"
    cur = registry.BY_SLUG.get(request.query_params.get("m", ""))
    if cur and cur["family"] != fam:
        fam = cur["family"]
    ms = [m for m in registry.METHODS if m["family"] == fam]
    cur = cur if cur and cur["family"] == fam else ms[0]
    flow = flows.flow_html(flows.nodes_for(cur["key"], cur["family"], lang_of(request)), lang_of(request))
    en = lang_of(request) == "en"
    cur = i18n.loc_method(cur, en)
    return page(request, "flow.html", key="flow", title="Alur Analisis Setiap Metode (Flowchart) – GetComput",
                description="Lihat urutan langkah analisis tiap metode statistika: data masuk, pemeriksaan asumsi, keputusan, sampai hasil.",
                path="/alur-metode", hero_title="Alur Analisis Setiap Metode",
                hero_lead="Lihat urutan langkah dari data masuk, pemeriksaan asumsi, sampai hasil. Pilih metodenya di bawah.",
                hero_tags=["Flowchart", "Asumsi & keputusan", "Hasil"], fam=fam, cur=cur, flow=flow, groups=registry.groups(fam),
                all_methods=json.dumps([{"s": m["slug"], "t": m_["title"], "g": m_["group"], "f": m["family"]} for m in registry.METHODS for m_ in [i18n.loc_method(m, en)]], ensure_ascii=False).replace("<", "\\u003c"))


async def feedback_page(request):
    ok = feedback_web.get_config() is not None
    return page(request, "feedback.html", key="feedback", title="Kirim Masukan – GetComput", description="Kirim saran fitur, laporan masalah, atau pertanyaan untuk pengembang GetComput.",
                path="/masukan", hero_title="Kirim Masukan",
                hero_lead="Temukan kekurangan, butuh metode baru, atau punya pertanyaan? Tulis di sini; masukan Anda dibaca langsung oleh pengembang.",
                hero_tags=["Saran fitur", "Laporan masalah", "Pertanyaan"], enabled=ok, categories=feedback_web.CATEGORIES, cat_en=i18n.FEEDBACK_CAT_EN,
                methods=[m["title"] for m in registry.METHODS], max_msg=feedback_web.MAX_MSG, max_contact=feedback_web.MAX_CONTACT)


async def api_feedback(request):
    try:
        if too_many(request, limit=5, window=300, bucket="|fb"):
            return err("Mohon tunggu sebentar sebelum mengirim lagi.", 429)
        cfg = feedback_web.get_config()
        if cfg is None:
            return err("Fitur masukan belum diaktifkan oleh pengelola situs. Silakan coba lagi nanti.", 503)
        b = await read_json(request)
        if str(b.get("website") or "").strip():          # jebakan anti-spam: pengguna asli tidak melihat kolom ini
            return JSONResponse({"ok": True})
        pesan = str(b.get("pesan") or "")
        if len(pesan.strip()) < 10:
            return err("Pesan terlalu pendek (minimal 10 karakter).")
        if not b.get("setuju"):
            return err("Centang persetujuan penyimpanan masukan terlebih dahulu.")
        kat = b.get("kategori") if b.get("kategori") in feedback_web.CATEGORIES else feedback_web.CATEGORIES[-1]
        met = str(b.get("metode") or "")
        met = met if met in {m["title"] for m in registry.METHODS} else ""
        try:
            nilai = int(b.get("nilai") or 0)
        except (TypeError, ValueError):
            nilai = 0
        nilai = nilai if 1 <= nilai <= 5 else ""
        row = feedback_web.make_row(kat, met, nilai, pesan, b.get("kontak"))
        await run_in_threadpool(feedback_web.append_row, cfg, row)
        return JSONResponse({"ok": True})
    except core.InputError as e:
        return err(str(e))
    except Exception as e:  # noqa: BLE001
        log.error("[feedback] gagal mengirim: %s: %s", type(e).__name__, e)
        kode = str(e)[:40] if str(e).startswith("GitHub") else type(e).__name__
        return err(f"Maaf, masukan belum berhasil terkirim. Silakan coba lagi beberapa saat lagi. (kode: {kode})", 502)


async def api_gen(request):
    """Pembangkit matriks rancangan (CCD/Box-Behnken, faktorial pecahan)."""
    try:
        m = registry.BY_SLUG.get(request.path_params["slug"])
        if not m or not m.get("gen"):
            return err("Pembangkit tidak tersedia.", 404)
        b = await read_json(request)
        kind = m["gen"]["kind"]
        if kind == "rsm":
            typ = b.get("typ") if b.get("typ") in ("CCD", "Box-Behnken") else "CCD"
            k = min(max(int(b.get("k") or 3), 2 if typ == "CCD" else 3), 5)
            nc = min(max(int(b.get("nc") or 3), 1), 8)
            D = registry.de.gen_ccd(k, nc) if typ == "CCD" else registry.de.gen_bbd(k, nc)
            html = (f'<p class="cap">{len(D)} unit percobaan, dalam satuan terkode (−1, 0, +1; CCD memuat titik aksial ±α). '
                    'Ubah ke satuan asli: nilai = pusat + kode × setengah rentang.</p>' + render.df_html(D))
        else:
            base = min(max(int(b.get("base") or 4), 3), 6)
            gens = [g.strip() for g in str(b.get("gens") or "")[:200].split(",") if g.strip()]
            D, rel, _res, rom, alias = registry.de.gen_fracfact(base, gens)
            html = (f'<p class="cap">Relasi pendefinisi: {render.esc(", ".join(rel))} · Resolusi {render.esc(rom)} · {len(D)} run.</p>'
                    + render.df_html(D) + render.df_html(alias))
        return JSONResponse({"ok": True, "html": html})
    except (ValueError, KeyError, TypeError) as e:
        return err(str(e) or "Pengaturan pembangkit tidak valid.")
    except Exception:
        log.error("gen gagal:\n%s", traceback.format_exc())
        return err("Pembangkit rancangan gagal. Periksa pengaturan Anda.", 500)


async def about(request):
    return page(request, "about.html", key="about", title="Tentang GetComput", description="Tentang GetComput: kalkulator analisis statistika berbahasa Indonesia.",
                path="/tentang", hero_title="Tentang GetComput", hero_lead="Cara membaca hasil, asumsi perhitungan, dan batasan yang perlu diketahui.",
                hero_tags=["Panduan membaca hasil"], contact=contact_html(lang_of(request) == "en"))


async def privacy(request):
    return page(request, "privacy.html", key="privacy", title="Kebijakan Privasi & Penafian – GetComput", description="Kebijakan privasi dan penafian GetComput.",
                path="/privasi", hero_title="Kebijakan Privasi & Penafian", hero_lead="Bagaimana data Anda diperlakukan dan batas tanggung jawab layanan.",
                contact=contact_html(lang_of(request) == "en"), updated=date.today().strftime("%d-%m-%Y"))


async def not_found(request, exc):
    return page(request, "notfound.html", key="notfound", ready=False, no_note=True, title="Halaman tidak ditemukan – GetComput", description="Halaman tidak ditemukan.", path=request.url.path,
                hero_title="Halaman tidak ditemukan", hero_lead="Alamat yang Anda buka tidak tersedia.", active="", status=404)


async def ads_txt(request):
    if not ADSENSE:
        return PlainTextResponse("", status_code=404)
    pub = ADSENSE.replace("ca-", "", 1)
    return PlainTextResponse(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")


async def robots(request):
    return PlainTextResponse(f"User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {base_url(request)}/sitemap.xml\n")


async def sitemap(request):
    b = base_url(request)
    urls = (["/", "/belajar", "/rancangan-percobaan", "/regresi", "/panduan", "/alur-metode", "/masukan", "/tentang", "/privasi"]
            + [f"/metode/{m['slug']}" for m in registry.METHODS] + [f"/belajar/{s}" for s in belajar.ORDER])

    def en_ready(u):
        if u.startswith("/metode/"):
            return u.split("/")[-1] in i18n.EN_METHODS
        if u.startswith("/belajar/"):
            return u.split("/")[-1] in i18n.EN_MODULES
        return u in i18n.READY_PATHS

    out = []
    for u in urls:
        if en_ready(u):
            ue = "/en/" if u == "/" else "/en" + u
            alt = (f'<xhtml:link rel="alternate" hreflang="id" href="{b}{u}"/><xhtml:link rel="alternate" hreflang="en" href="{b}{ue}"/>'
                   f'<xhtml:link rel="alternate" hreflang="x-default" href="{b}{u}"/>')
            out.append(f"<url><loc>{b}{u}</loc>{alt}</url>")
            out.append(f"<url><loc>{b}{ue}</loc>{alt}</url>")
        else:
            out.append(f"<url><loc>{b}{u}</loc></url>")
    body = ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + "".join(out) + "</urlset>")
    return Response(body, media_type="application/xml")


async def healthz(request):
    return PlainTextResponse("ok")


# ------------------------------------------------------------------ API
import contextvars  # noqa: E402
REQ_LANG = contextvars.ContextVar("req_lang", default="id")


def err(msg, status=422):
    if REQ_LANG.get() == "en":
        msg = i18n.tr_err(msg)
    return JSONResponse({"ok": False, "error": msg}, status_code=status)


async def api_parse(request):
    try:
        form = await request.form()
        f = form.get("file")
        if f is None or not hasattr(f, "read"):
            return err("Berkas tidak ditemukan.")
        content = await f.read()
        if len(content) > MAX_BODY:
            return err("Berkas terlalu besar (maksimal 4 MB).")
        text = await run_in_threadpool(core.parse_file, getattr(f, "filename", ""), content)
        return JSONResponse({"ok": True, "csv": text})
    except core.InputError as e:
        return err(str(e))
    except Exception:
        log.error("parse gagal:\n%s", traceback.format_exc())
        return err("Berkas tidak dapat dibaca. Coba simpan ulang sebagai CSV atau .xlsx.")


async def api_inspect(request):
    try:
        body = await read_json(request)
        df = await run_in_threadpool(core.parse_table, body.get("csv"))
        return JSONResponse({"ok": True, "info": core.inspect(df)})
    except core.InputError as e:
        return err(str(e))
    except Exception:
        log.error("inspect gagal:\n%s", traceback.format_exc())
        return err("Data tidak dapat dibaca. Periksa format data Anda.")


async def api_sample(request):
    m = registry.BY_SLUG.get(request.path_params["slug"])
    if not m:
        return err("Metode tidak ditemukan.", 404)
    df = registry.sample_df(m)
    return JSONResponse({"ok": True, "csv": df.to_csv(sep="\t", index=False)})


def clean_params(m, df, raw):
    """Validasi isian dari browser terhadap definisi isian metode (tidak pernah percaya input mentah)."""
    cols = [str(c) for c in df.columns]
    out, chosen = {}, []
    raw = raw if isinstance(raw, dict) else {}
    for f in m["fields"]:
        n, t, v = f["name"], f["type"], raw.get(f["name"])
        if t == "text":
            out[n] = str(v if v is not None else f.get("default", ""))[:200]
        elif t == "float_opt":
            try:
                out[n] = float(v) if v not in (None, "") else None
            except (TypeError, ValueError):
                out[n] = None
            if out[n] is not None and not (abs(out[n]) < 1e15):
                out[n] = None
        elif t == "select_multi":
            vs = {str(x) for x in v} if isinstance(v, list) else set()
            out[n] = [x for x in f["options"] if str(x) in vs]
        elif t in ("num", "cat", "any", "cat_opt", "any_opt"):
            if v in (None, ""):
                if t in ("cat_opt", "any_opt"):
                    out[n] = None
                    continue
                raise core.InputError(f"Pilih kolom untuk “{f['label']}”.")
            if not isinstance(v, str) or v not in cols:
                raise core.InputError(f"Kolom untuk “{f['label']}” tidak ada pada data.")
            if t == "num" and not core.pd.api.types.is_numeric_dtype(df[v]):
                raise core.InputError(f"Kolom “{v}” berisi teks, sedangkan “{f['label']}” harus numerik.")
            if f.get("reuse"):
                out[n] = v
                continue
            if v in chosen:
                raise core.InputError(f"Kolom “{v}” dipakai lebih dari sekali. Pilih kolom berbeda untuk tiap peran.")
            out[n] = v
            chosen.append(v)
        elif t in ("num_multi", "cat_multi", "any_multi"):
            vs = v if isinstance(v, list) else []
            if not all(isinstance(x, str) and x in cols for x in vs):
                raise core.InputError(f"Kolom untuk “{f['label']}” tidak ada pada data.")
            if t == "num_multi" and any(not core.pd.api.types.is_numeric_dtype(df[x]) for x in vs):
                raise core.InputError(f"Semua kolom pada “{f['label']}” harus numerik.")
            if any(x in chosen for x in vs) or len(set(vs)) != len(vs):
                raise core.InputError(f"Kolom pada “{f['label']}” tumpang tindih dengan pilihan lain.")
            lo, hi = f.get("min", 0), f.get("max", 99)
            if len(vs) < lo:
                raise core.InputError(f"Pilih minimal {lo} kolom pada “{f['label']}”." if lo else "")
            if len(vs) > hi:
                raise core.InputError(f"Pilih maksimal {hi} kolom pada “{f['label']}”.")
            out[n] = vs
            chosen += vs
        elif t in ("int", "float"):
            try:
                x = float(v)
            except (TypeError, ValueError):
                x = float(f["default"])
            x = min(max(x, f["min"]), f["max"])
            out[n] = int(round(x)) if t == "int" else x
        elif t == "bool":
            out[n] = bool(v) if v is not None else bool(f["default"])
        elif t == "select":
            out[n] = v if v in f["options"] else f["default"]
    # beberapa metode (GLM, dummy) memerlukan sedikitnya satu prediktor
    if "xn" in out and "xc" in out and not out["xn"] and not out["xc"]:
        raise core.InputError("Pilih minimal satu variabel independen (numerik atau kategorik).")
    return out


async def _compute(request, slug):
    if too_many(request):
        raise core.InputError("Terlalu banyak permintaan. Tunggu sebentar lalu coba lagi.")
    m = registry.BY_SLUG.get(slug)
    if not m:
        raise core.InputError("Metode tidak ditemukan.")
    body = await read_json(request)
    alpha = body.get("alpha", 0.05)
    alpha = alpha if alpha in ALPHAS else 0.05
    df = await run_in_threadpool(core.parse_table, body.get("csv"))
    params = clean_params(m, df, body.get("params"))
    opts = body.get("opts") if isinstance(body.get("opts"), dict) else {}

    def job():
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kind, R = m["run"](df, params, alpha)
            out = render.render(kind, R, alpha, params, opts)
            if body.get("lang") == "en":
                out = (i18n.tr_html(out[0]), i18n.tr_sheets(out[1]) if isinstance(out[1], dict) else out[1])
            return out

    async with SEM:
        return await asyncio.wait_for(run_in_threadpool(job), timeout=120)


def _fail(exc, where):
    if isinstance(exc, (core.InputError, ValueError)):
        return err(str(exc))
    if isinstance(exc, asyncio.TimeoutError):
        return err("Perhitungan terlalu lama. Kurangi ukuran data atau jumlah variabel.", 504)
    log.error("%s gagal:\n%s", where, "".join(traceback.format_exception(exc)))
    return err("Perhitungan tidak dapat diselesaikan dengan data dan pilihan ini. Periksa kolom yang dipilih dan kelengkapan data, "
               "atau coba metode lain.", 500)


async def api_run(request):
    try:
        html, _ = await _compute(request, request.path_params["slug"])
        return JSONResponse({"ok": True, "html": html})
    except Exception as e:
        return _fail(e, "run")


async def api_xlsx(request):
    try:
        _, sheets = await _compute(request, request.path_params["slug"])
        data = await run_in_threadpool(render.to_xlsx, sheets)
        return Response(data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": f'attachment; filename="hasil_{request.path_params["slug"]}.xlsx"'})
    except Exception as e:
        return _fail(e, "xlsx")


# ------------------------------------------------------------------ middleware
class Guard:
    """Alihkan ke host utama (bila diatur) dan pasang header keamanan dasar."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict((k.decode().lower(), v.decode()) for k, v in scope["headers"])
        host = headers.get("host", "").split(":")[0].lower()
        if PRIMARY_HOST and host and host != PRIMARY_HOST and scope["path"] != "/healthz" and not host.startswith(("localhost", "127.")):
            q = scope.get("query_string", b"").decode()
            resp = RedirectResponse(f"https://{PRIMARY_HOST}{scope['path']}" + (f"?{q}" if q else ""), status_code=301)
            return await resp(scope, receive, send)

        async def send2(msg):
            if msg["type"] == "http.response.start":
                h = list(msg.get("headers", []))
                h += [(b"x-content-type-options", b"nosniff"), (b"referrer-policy", b"strict-origin-when-cross-origin"),
                      (b"x-frame-options", b"SAMEORIGIN")]
                path = scope["path"]
                if msg.get("status") == 200 and (path.startswith("/static/") or path.startswith("/search-index")):
                    versioned = b"v=" in scope.get("query_string", b"")
                    h = [x for x in h if x[0].lower() != b"cache-control"]
                    h.append((b"cache-control", b"public, max-age=31536000, immutable" if versioned else b"public, max-age=86400"))
                msg["headers"] = h
            await send(msg)
        return await self.app(scope, receive, send2)


routes = [
    Route("/", home), Route("/rancangan-percobaan", family_page), Route("/regresi", family_page),
    Route("/metode/{slug}", method_page), Route("/belajar", learn_index), Route("/belajar/{slug}", learn_module), Route("/panduan", guide), Route("/alur-metode", flow_page), Route("/masukan", feedback_page),
    Route("/api/feedback", api_feedback, methods=["POST"]), Route("/api/{slug}/gen", api_gen, methods=["POST"]), Route("/tentang", about), Route("/privasi", privacy),
    Route("/search-index-{lang}.json", search_index_json), Route("/robots.txt", robots), Route("/ads.txt", ads_txt), Route("/sitemap.xml", sitemap), Route("/healthz", healthz),
    Route("/api/parse", api_parse, methods=["POST"]), Route("/api/inspect", api_inspect, methods=["POST"]),
    Route("/api/{slug}/sample", api_sample), Route("/api/{slug}/run", api_run, methods=["POST"]),
    Route("/api/{slug}/xlsx", api_xlsx, methods=["POST"]),
    Route("/favicon.ico", lambda r: FileResponse(os.path.join(HERE, "static", "favicon-48.png"), media_type="image/png")),
    Mount("/static", StaticFiles(directory=os.path.join(HERE, "static")), name="static"),
]
app = Starlette(routes=routes, middleware=[Middleware(Guard), Middleware(i18n.LangMiddleware), Middleware(GZipMiddleware, minimum_size=1000)],
                exception_handlers={404: not_found})
