# operator_fit.py  –  baut die 8er-Leiter (alpha*) und bewertet alle Skalen

import math

alpha_scan = {
    "atomic": 1.70071163,      # eV (aus deiner Ausgabe)
    "nuclear": 1.17284010e8,   # eV (Proton_rest_eV/8)
    "cosmo": 2.93527914e-5,    # eV (CMB_kBT_eV/8)
    # "material_diamond": ...   # wenn vorhanden
}

def fit_alpha_star(alpha_by_scale):
    """
    Finde alpha* und ganzzahlige k_scale, so dass
    alpha_scale ~ alpha* * 8^k mit minimalem Fehler im log8-Raum.
    """
    # starte mit alpha* als geometrisches Mittel (robust)
    logs = [math.log(a, 8) for a in alpha_by_scale.values()]
    alpha_star = 8 ** (sum(logs)/len(logs))

    # iteratives Runden auf ganze k und Refit von alpha*
    for _ in range(8):
        k = {s: round(math.log(a/alpha_star, 8)) for s, a in alpha_by_scale.items()}
        # Refit alpha* = mean( a / 8^k )
        alpha_star = sum(a / (8**k[s]) for s, a in alpha_by_scale.items()) / len(alpha_by_scale)
    return alpha_star, k

def best_dyadic(r, n_max=256, max_m=12):
    """Finde n/2^m am nächsten zu r."""
    best = None
    for m in range(max_m+1):
        d = 2**m
        n = round(r*d)
        if 1 <= n <= n_max:
            approx = n/d
            rel = abs(r-approx)/max(abs(r), 1e-15)
            if (best is None) or (rel < best[2]):
                best = (n, m, rel, approx)
    return best

# 2) Leiter fitten
alpha_star, k = fit_alpha_star(alpha_scan)
alpha_ladder = {s: alpha_star * (8**k_s) for s, k_s in k.items()}

print("== Gefundener Operator (Leiter) ==")
print(f"alpha* = {alpha_star:.9g} eV")
for s in alpha_scan:
    print(f"- {s:8s}: k={k[s]:+d}, alpha_scale={alpha_ladder[s]:.9g} eV  "
          f"(scan={alpha_scan[s]:.9g} eV)")

# 3) Beispiel-Bewertung einiger Energien (trage hier deine E pro Skala ein)
E_values = {
    "atomic": {
        "H_ionization_eV": 13.6057,
        "H_Ly_alpha_eV": 10.2,
        "H_Halpha_eV": 1.889,
    },
    "cosmo": {
        "CMB_kBT_eV": 0.000234822,
        "CMB_delta_T_eV": 1.0e-5,
    },
    "nuclear": {
        "Deuteron_binding_eV": 2.22457e6,
        "He4_binding_eV": 2.82957e7,
        "Proton_rest_eV": 9.38272e8,
    },
}

print("\n== Bewertung im 8er-Raster ==")
for s, vals in E_values.items():
    a = alpha_ladder[s]
    print(f"\n[ {s} ]   alpha_scale = {a:.9g} eV")
    for name, E in vals.items():
        r = E / a
        n, m, rel, approx = best_dyadic(r)
        print(f"  - {name:>20s}: r={r:>12.6f} ~ {n}/{2**m}={approx:.6f}  "
              f"(rel.Abw={100*rel:5.3f}%)")