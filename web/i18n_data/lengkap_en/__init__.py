"""Terjemahan Inggris untuk materi lengkap. Persamaan blok diambil dari versi Indonesia (lewat tr_eq)."""
import importlib

LENGKAP_EN = {}


def LE(slug, teori, soal, contoh2=None):
    """teori: [(judul, [paragraf...])], soal: [(q, a)], contoh2: dict(judul, soal, data, langkah=[teks], simpul)."""
    LENGKAP_EN[slug] = dict(teori=[(h, list(p)) for h, p in teori], soal=[tuple(s) for s in soal], contoh2=contoh2)


def LD(slug, teori=(), soal=()):
    t = LENGKAP_EN[slug]
    t["teori"] += [(h, list(p)) for h, p in teori]
    t["soal"] += [tuple(x) for x in soal]


for _n in ("dasar", "dasar2", "des", "des2", "reg", "reg2"):
    try:
        importlib.import_module(f"{__name__}.{_n}")
    except ModuleNotFoundError as _e:
        if _n not in str(_e):
            raise
