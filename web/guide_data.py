"""guide_data.py – tabel 'situasi data → metode yang disarankan' (sama dengan Panduan Metode pada versi Streamlit)."""
from . import registry


def rows(lang="id"):
    by_label = {m["title"]: m for m in registry.METHODS}
    out = {}
    for fam, g, t in ((registry.FAM_DES, "GUIDE_DES", "TARGET_DES"), (registry.FAM_REG, "GUIDE_REG", "TARGET_REG")):
        lst = []
        for (sit, rec, grp), label in zip(registry.META[g], registry.META[t]):
            m = by_label.get(label)
            if lang == "en":
                from .i18n_data.guide import GUIDE_EN
                sit, rec = GUIDE_EN.get(sit, sit), GUIDE_EN.get(rec, rec)
            lst.append({"sit": sit, "rec": rec, "grp": grp, "slug": m["slug"] if m else None})
        out[fam] = lst
    return out
