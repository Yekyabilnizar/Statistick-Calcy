"""English: extra explanations on calculator pages. Same structure as web/metode_extra.py."""
EXTRA_EN = {}


def XE(slug, kasus, data, baca, salah, lapor, faq):
    EXTRA_EN[slug] = dict(kasus=kasus, data=list(data), baca=list(baca), salah=list(salah), lapor=lapor, faq=list(faq))


for _n in ("des", "reg1", "reg2", "reg3"):
    try:
        __import__(f"{__name__.rsplit('.', 1)[0]}.metode_extra_en_{_n}")
    except ModuleNotFoundError as e:
        if f"metode_extra_en_{_n}" not in str(e):
            raise
