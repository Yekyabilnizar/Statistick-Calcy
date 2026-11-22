"""Materi belajar: modul dasar + satu modul ringkas per metode kalkulator."""

MODULES = {}      # slug -> modul
ORDER = []        # urutan jalur belajar


def T(slug, title, ringkas, tujuan, ide, rumus, langkah, baca, jebakan, latihan, pra=(), tahap="", method=None):
    """Satu modul. `method` = slug metode kalkulator untuk latihan (None bila modul dasar)."""
    m = dict(slug=slug, title=title, ringkas=ringkas, tujuan=list(tujuan), ide=list(ide), rumus=[tuple(r) for r in rumus],
             langkah=list(langkah), baca=list(baca), jebakan=list(jebakan), latihan=latihan, pra=list(pra), tahap=tahap, method=method)
    MODULES[slug] = m
    ORDER.append(slug)
    return m


def _load():
    from . import dasar, des, reg_a, reg_b  # noqa: F401


_load()
