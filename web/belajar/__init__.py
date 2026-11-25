"""Materi belajar: modul dasar + satu modul ringkas per metode kalkulator."""

TEORI = {}        # slug -> {"notasi","teori","contoh","faq"} (materi mendalam dengan persamaan LaTeX)
MODULES = {}      # slug -> modul
ORDER = []        # urutan jalur belajar


def T(slug, title, ringkas, tujuan, ide, rumus, langkah, baca, jebakan, latihan, pra=(), tahap="", method=None):
    """Satu modul. `method` = slug metode kalkulator untuk latihan (None bila modul dasar)."""
    m = dict(slug=slug, title=title, ringkas=ringkas, tujuan=list(tujuan), ide=list(ide), rumus=[tuple(r) for r in rumus],
             langkah=list(langkah), baca=list(baca), jebakan=list(jebakan), latihan=latihan, pra=list(pra), tahap=tahap, method=method)
    MODULES[slug] = m
    ORDER.append(slug)
    return m


def X(slug, notasi, teori, contoh, faq):
    """Materi mendalam untuk satu modul.
    notasi : [(simbol_latex, arti)]
    teori  : [(judul, [paragraf...], [persamaan_latex...])]   (paragraf boleh memuat \\( ... \\))
    contoh : dict(judul, soal, data=[[...]] atau None, langkah=[(teks, persamaan_latex_atau_None)], simpul)
    faq    : [(pertanyaan, jawaban)]
    """
    TEORI[slug] = dict(notasi=[tuple(n) for n in notasi], teori=[(h, list(p), list(e)) for h, p, e in teori], contoh=contoh, faq=[tuple(f) for f in faq])


def _load():
    from . import dasar, des, reg_a, reg_b  # noqa: F401
    from . import teori_dasar, teori_des, teori_reg_a, teori_reg_b  # noqa: F401


_load()

from .lengkap import LENGKAP, _load as _load_lengkap  # noqa: E402
_load_lengkap()
