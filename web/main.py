"""main.py – aplikasi web StatCalc (Starlette). Jalankan: uvicorn web.main:app --host 0.0.0.0 --port $PORT"""
import asyncio
import json
import logging
import os
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
from starlette.templating import Jinja2Templates  # noqa: E402

import flows  # noqa: E402
from web import core, feedback_web, guide_data, registry, render  # noqa: E402

log = logging.getLogger("statcalc")
HERE = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(HERE, "templates"))

SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")          # mis. https://namadomain.com
PRIMARY_HOST = os.environ.get("PRIMARY_HOST", "").strip().lower()  # bila diisi, host lain dialihkan permanen ke sini
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "").strip()
ASSET_V = os.environ.get("ASSET_V", "1")
MAX_BODY = 4_500_000
ALPHAS = (0.01, 0.05, 0.10)
NAV = [("/", "🏠 Beranda"), ("/rancangan-percobaan", "🧪 Rancangan"), ("/regresi", "📈 Regresi"),
       ("/panduan", "🧭 Panduan Metode"), ("/alur-metode", "🗺️ Alur Metode"), ("/masukan", "💬 Masukan"), ("/tentang", "ℹ️ Tentang")]
SEM = asyncio.Semaphore(2)
_hits = defaultdict(deque)


# ------------------------------------------------------------------ util
def base_url(request):
    if SITE_URL:
        return SITE_URL
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    return f"{proto}://{request.headers.get('host', request.url.netloc)}"


def search_index():
    items = []
    for m in registry.METHODS:
        items.append({"t": m["title"], "u": f"/metode/{m['slug']}", "d": m["desc"], "k": " ".join(m["tags"]) + f" {m['key']} {m['slug']}",
                      "g": f"{registry.FAM_NAME[m['family']]} › {m['group']}"})
    for t, u, d in [("Panduan Memilih Metode", "/panduan", "pilih situasi data kapan dipakai bingung memilih"),
                    ("Alur Metode (flowchart)", "/alur-metode", "flowchart alur langkah analisis tiap metode"),
                    ("Kirim Masukan", "/masukan", "masukan saran bug laporan pertanyaan kesan"),
                    ("Tentang StatCalc", "/tentang", "tentang cara membaca hasil catatan metodologi"),
                    ("Kebijakan Privasi & Penafian", "/privasi", "privasi cookie penafian iklan")]:
        items.append({"t": t, "u": u, "d": d, "k": "", "g": "Halaman informasi"})
    return json.dumps(items, ensure_ascii=False).replace("<", "\\u003c")


def page(request, name, *, title, description, path, hero_title, hero_lead, hero_tags=None, active=None, status=200, **ctx):
    ctx.update(title=title, description=description, canonical=base_url(request) + path, hero_title=hero_title, hero_lead=hero_lead,
               hero_tags=hero_tags, nav_items=NAV, active=active if active is not None else path, search_index=search_index(),
               asset_v=ASSET_V, jsonld=ctx.get("jsonld"))
    return templates.TemplateResponse(request, name, ctx, status_code=status)


def contact_html():
    if CONTACT_EMAIL:
        return f'Hubungi kami melalui <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.'
    return "Kontak pengembang akan ditambahkan di sini."


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
        return json.loads(body or b"{}")
    except Exception:
        raise core.InputError("Permintaan tidak valid.")


# ------------------------------------------------------------------ halaman
async def home(request):
    g = {f: registry.groups(f) for f in (registry.FAM_DES, registry.FAM_REG)}
    n_des = sum(len(v) for v in g["des"].values())
    n_reg = sum(len(v) for v in g["reg"].values())
    return page(request, "home.html", title="StatCalc – Kalkulator Analisis Statistika Online (ANOVA, Rancangan Percobaan, Regresi)",
                description="Kalkulator analisis statistika berbahasa Indonesia: RAL, RAK, faktorial, split-plot, regresi linear, logistik, dan lainnya. "
                            "Tabel ANOVA, uji lanjut, uji asumsi, grafik, dan interpretasi otomatis.",
                path="/", hero_title="Dari data ke kesimpulan, tanpa menulis kode",
                hero_lead="StatCalc adalah kalkulator analisis statistika untuk penelitian dan percobaan: pilih metode, masukkan data, lalu dapatkan tabel, "
                          "grafik, uji asumsi, dan interpretasi otomatis dalam bahasa Indonesia.",
                hero_tags=["Rancangan percobaan", "Regresi", "Interpretasi otomatis", "Unduh Excel"],
                groups=g, n_des=n_des, n_reg=n_reg, n_all=n_des + n_reg,
                jsonld=json.dumps({"@context": "https://schema.org", "@type": "WebApplication", "name": "StatCalc", "applicationCategory": "EducationalApplication",
                                   "inLanguage": "id", "operatingSystem": "Web", "url": base_url(request) + "/",
                                   "description": "Kalkulator analisis statistika: rancangan percobaan dan regresi."}, ensure_ascii=False))


async def family_page(request):
    path = request.url.path.rstrip("/")
    fam = registry.FAM_DES if path == "/rancangan-percobaan" else registry.FAM_REG
    name = registry.FAM_NAME[fam]
    lead = ("Analisis ragam untuk percobaan terkontrol: dari RAL dan RAK sampai rancangan lanjutan." if fam == registry.FAM_DES
            else "Dari regresi linear berganda sampai model untuk data biner, cacahan, dan respon positif.")
    return page(request, "catalog.html", title=f"{name} – StatCalc", description=lead, path=path, hero_title=name, hero_lead=lead,
                groups=registry.groups(fam), fam_name=name)


async def method_page(request):
    m = registry.BY_SLUG.get(request.path_params["slug"])
    if not m:
        return await not_found(request, None)
    path = f"/metode/{m['slug']}"
    related = [x for x in registry.METHODS if x["family"] == m["family"] and x["slug"] != m["slug"] and x["group"] == m["group"]][:3]
    fields = [{k: v for k, v in f.items()} for f in m["fields"]]
    spec = json.dumps({"slug": m["slug"], "fields": fields, "key": m["key"], "family": m["family"], "gen": m.get("gen")}, ensure_ascii=False).replace("<", "\\u003c")
    flow = flows.flow_html(flows.nodes_for(m["key"], m["family"]))
    ld = json.dumps({"@context": "https://schema.org", "@type": "WebApplication", "name": m["title"], "applicationCategory": "EducationalApplication",
                     "inLanguage": "id", "url": base_url(request) + path, "description": m["desc"]}, ensure_ascii=False)
    gen = json.dumps(m["gen"], ensure_ascii=False).replace("<", "\\u003c") if m.get("gen") else "null"
    return page(request, "method.html", title=f"{m['title']} – Kalkulator Online | StatCalc",
                description=f"{m['desc']} Hitung online: tabel hasil, uji asumsi, grafik, dan interpretasi otomatis.", path=path, active="/" + registry.FAM_PATH[m["family"]],
                hero_title=m["title"], hero_lead=m["desc"], hero_tags=m["tags"], m=m, fam_name=registry.FAM_NAME[m["family"]],
                fam_path=registry.FAM_PATH[m["family"]], related=related, spec=spec, flow=flow, jsonld=ld)


async def guide(request):
    return page(request, "guide.html", title="Panduan Memilih Metode Analisis Statistika – StatCalc",
                description="Bingung memilih metode? Lihat kapan tiap rancangan percobaan dan metode regresi dipakai.", path="/panduan",
                hero_title="Panduan Memilih Metode", hero_lead="Pilih situasi data atau percobaan Anda; kami tunjukkan metode yang cocok dan membukanya langsung.",
                hero_tags=["Rancangan percobaan", "Regresi"], rows=guide_data.rows(),
                groups={f: registry.groups(f) for f in (registry.FAM_DES, registry.FAM_REG)})


async def flow_page(request):
    fam = request.query_params.get("fam", "des")
    fam = fam if fam in ("des", "reg") else "des"
    cur = registry.BY_SLUG.get(request.query_params.get("m", ""))
    if cur and cur["family"] != fam:
        fam = cur["family"]
    ms = [m for m in registry.METHODS if m["family"] == fam]
    cur = cur if cur and cur["family"] == fam else ms[0]
    flow = flows.flow_html(flows.nodes_for(cur["key"], cur["family"]))
    return page(request, "flow.html", title="Alur Analisis Setiap Metode (Flowchart) – StatCalc",
                description="Lihat urutan langkah analisis tiap metode statistika: data masuk, pemeriksaan asumsi, keputusan, sampai hasil.",
                path="/alur-metode", hero_title="Alur Analisis Setiap Metode",
                hero_lead="Lihat urutan langkah dari data masuk, pemeriksaan asumsi, sampai hasil. Pilih metodenya di bawah.",
                hero_tags=["Flowchart", "Asumsi & keputusan", "Hasil"], fam=fam, cur=cur, flow=flow, groups=registry.groups(fam),
                all_methods=json.dumps([{"s": m["slug"], "t": m["title"], "g": m["group"], "f": m["family"]} for m in registry.METHODS], ensure_ascii=False).replace("<", "\\u003c"))


async def feedback_page(request):
    ok = feedback_web.get_config() is not None
    return page(request, "feedback.html", title="Kirim Masukan – StatCalc", description="Kirim saran fitur, laporan masalah, atau pertanyaan untuk pengembang StatCalc.",
                path="/masukan", hero_title="Kirim Masukan",
                hero_lead="Temukan kekurangan, butuh metode baru, atau punya pertanyaan? Tulis di sini; masukan Anda dibaca langsung oleh pengembang.",
                hero_tags=["Saran fitur", "Laporan masalah", "Pertanyaan"], enabled=ok, categories=feedback_web.CATEGORIES,
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
    return page(request, "about.html", title="Tentang StatCalc", description="Tentang StatCalc: kalkulator analisis statistika berbahasa Indonesia.",
                path="/tentang", hero_title="Tentang StatCalc", hero_lead="Cara membaca hasil, asumsi perhitungan, dan batasan yang perlu diketahui.",
                hero_tags=["Panduan membaca hasil"], contact=contact_html())


async def privacy(request):
    return page(request, "privacy.html", title="Kebijakan Privasi & Penafian – StatCalc", description="Kebijakan privasi dan penafian StatCalc.",
                path="/privasi", hero_title="Kebijakan Privasi & Penafian", hero_lead="Bagaimana data Anda diperlakukan dan batas tanggung jawab layanan.",
                contact=contact_html(), updated=date.today().strftime("%d-%m-%Y"))


async def not_found(request, exc):
    return page(request, "notfound.html", title="Halaman tidak ditemukan – StatCalc", description="Halaman tidak ditemukan.", path=request.url.path,
                hero_title="Halaman tidak ditemukan", hero_lead="Alamat yang Anda buka tidak tersedia.", active="", status=404)


async def robots(request):
    return PlainTextResponse(f"User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {base_url(request)}/sitemap.xml\n")


async def sitemap(request):
    b = base_url(request)
    urls = ["/", "/rancangan-percobaan", "/regresi", "/panduan", "/alur-metode", "/masukan", "/tentang", "/privasi"] + [f"/metode/{m['slug']}" for m in registry.METHODS]
    body = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + \
           "".join(f"<url><loc>{b}{u}</loc></url>" for u in urls) + "</urlset>"
    return Response(body, media_type="application/xml")


async def healthz(request):
    return PlainTextResponse("ok")


# ------------------------------------------------------------------ API
def err(msg, status=422):
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
            vs = v if isinstance(v, list) else []
            out[n] = [x for x in f["options"] if x in vs]
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
            return render.render(kind, R, alpha, params, opts)

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
                msg["headers"] = h
            await send(msg)
        return await self.app(scope, receive, send2)


routes = [
    Route("/", home), Route("/rancangan-percobaan", family_page), Route("/regresi", family_page),
    Route("/metode/{slug}", method_page), Route("/panduan", guide), Route("/alur-metode", flow_page), Route("/masukan", feedback_page),
    Route("/api/feedback", api_feedback, methods=["POST"]), Route("/api/{slug}/gen", api_gen, methods=["POST"]), Route("/tentang", about), Route("/privasi", privacy),
    Route("/robots.txt", robots), Route("/sitemap.xml", sitemap), Route("/healthz", healthz),
    Route("/api/parse", api_parse, methods=["POST"]), Route("/api/inspect", api_inspect, methods=["POST"]),
    Route("/api/{slug}/sample", api_sample), Route("/api/{slug}/run", api_run, methods=["POST"]),
    Route("/api/{slug}/xlsx", api_xlsx, methods=["POST"]),
    Mount("/static", StaticFiles(directory=os.path.join(HERE, "static")), name="static"),
]
app = Starlette(routes=routes, middleware=[Middleware(Guard), Middleware(GZipMiddleware, minimum_size=1000)],
                exception_handlers={404: not_found})
