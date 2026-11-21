"""posthoc_ext.py – uji lanjut tambahan: Scheffé dan Dunnett (pembanding terhadap kontrol),
dengan antarmuka sama seperti stats_engine.posthoc. Semua metode: BNT, DMRT, Tukey (BNJ), Scheffé, Dunnett."""
import numpy as np
import pandas as pd
from scipy import stats

from stats_engine import posthoc, _compact_letters

METHODS = ["BNT (LSD)", "DMRT (Duncan)", "Tukey (BNJ)", "Scheffé", "Dunnett (vs kontrol)"]


def _dunnett_crit(ns_t, n0, dbg, alpha, nsim=200000, seed=1):
    """Nilai kritis Dunnett dua arah lewat simulasi t multivariat (korelasi sesuai ukuran sampel)."""
    ns_t = np.asarray(ns_t, float)
    m = len(ns_t)
    r = np.sqrt(np.outer(ns_t, ns_t) / np.outer(ns_t + n0, ns_t + n0))
    np.fill_diagonal(r, 1.0)
    rng = np.random.default_rng(seed)
    z = rng.multivariate_normal(np.zeros(m), r, size=nsim)
    s = np.sqrt(rng.chisquare(dbg, size=nsim) / dbg)
    mx = np.abs(z / s[:, None]).max(1)
    return float(np.quantile(mx, 1 - alpha))


def posthoc_any(means, ns, ktg, dbg, alpha, method, control=None):
    """Mengembalikan (huruf, tabel pasangan). Untuk Dunnett huruf = '*' bila berbeda dari kontrol."""
    if method.startswith("BNT"):
        return posthoc(means, ns, ktg, dbg, alpha, "BNT")
    if method.startswith("DMRT"):
        return posthoc(means, ns, ktg, dbg, alpha, "DMRT")
    if method.startswith("Tukey") or method.startswith("BNJ"):
        return posthoc(means, ns, ktg, dbg, alpha, "BNJ")
    order = means.sort_values(ascending=False).index.tolist()
    k = len(order)
    if method.startswith("Sche"):
        fcrit = stats.f.ppf(1 - alpha, k - 1, dbg)
        rows, nonsig = [], {}
        for i in range(k):
            for j in range(i + 1, k):
                a, b = order[i], order[j]
                cr = np.sqrt((k - 1) * fcrit * ktg * (1 / ns[a] + 1 / ns[b]))
                diff = means[a] - means[b]
                nonsig[(a, b)] = nonsig[(b, a)] = not diff > cr
                rows.append([f"{a} vs {b}", round(diff, 4), round(cr, 4), "Berbeda nyata" if diff > cr else "Tidak berbeda nyata"])
        pair = pd.DataFrame(rows, columns=["Perbandingan", "Selisih rata-rata", "Nilai kritis", "Kesimpulan"])
        return _compact_letters(order, lambda a, b: nonsig[(a, b)]), pair
    # Dunnett
    ctrl = control if control in means.index else order[-1]
    others = [l for l in order if l != ctrl]
    crit = _dunnett_crit([ns[l] for l in others], ns[ctrl], dbg, alpha)
    rows, letters = [], {ctrl: "kontrol"}
    for l in others:
        se = np.sqrt(ktg * (1 / ns[l] + 1 / ns[ctrl]))
        diff = means[l] - means[ctrl]
        t = diff / se
        sig = abs(t) > crit
        letters[l] = "*" if sig else "tn"
        rows.append([f"{l} vs {ctrl} (kontrol)", round(diff, 4), round(t, 4), round(crit, 4), "Berbeda nyata dari kontrol" if sig else "Tidak berbeda nyata"])
    pair = pd.DataFrame(rows, columns=["Perbandingan", "Selisih rata-rata", "t hitung", "Nilai kritis Dunnett", "Kesimpulan"])
    return letters, pair
