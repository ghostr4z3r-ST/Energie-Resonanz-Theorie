"""
ERT Operator Scan – Auto-Referenz-Finder (8er-Raster)
"""

from math import isfinite
import importlib

def load_dataset():
    ds = importlib.import_module("ert_dataset")
    return ds.DATA

def best_fraction_on_8_lattice(r: float,
                               n_max: int = 64,
                               denom_set=(1, 2, 4, 8, 16, 32, 64)):
    if not (isinstance(r, (int, float)) and isfinite(r)):
        return (0, 1, 0.0, float("inf"))
    best = None
    for d in denom_set:
        n_guess = round(r * d)
        for n in (n_guess - 1, n_guess, n_guess + 1):
            if 1 <= n <= n_max:
                approx = n / d
                rel = abs(r - approx) / max(abs(r), 1e-15)
                cand = (n, d, approx, rel)
                if (best is None) or (rel < best[3]):
                    best = cand
    if best is None:
        return (0, 1, 0.0, float("inf"))
    return best

REF_PREFS = {
    "atomic":  ["H_ionization_eV", "H_Ly_alpha_eV"],
    "nuclear": ["Deuteron_binding_eV", "He4_binding_eV", "Proton_rest_eV"],
    "cosmo":   ["CMB_kBT_eV"],
}

SKIP_KEYS = {"CMB_T_K", "Rydberg_m_inv", "Proton_radius_fm"}

def is_energy_value(x):
    return isinstance(x, (int, float)) and isfinite(x) and x != 0.0

def evaluate_scale_with_alpha(scale_dict: dict, alpha: float):
    rows = []
    total_rel = 0.0
    count = 0
    for key, val in scale_dict.items():
        if key in SKIP_KEYS:
            continue
        if not is_energy_value(val):
            continue
        r = val / alpha
        n, d, approx, rel = best_fraction_on_8_lattice(r)
        rows.append((key, val, r, n, d, approx, rel))
        total_rel += rel
        count += 1
    score = total_rel / max(count, 1)
    return score, rows

def choose_best_alpha(scale_name: str, scale_dict: dict):
    candidates = []
    explicit_alpha_key = f"alpha_{scale_name}_eV"
    if explicit_alpha_key in scale_dict and is_energy_value(scale_dict[explicit_alpha_key]):
        candidates.append(("EXPLIZIT", explicit_alpha_key, scale_dict[explicit_alpha_key]))

    for k in REF_PREFS.get(scale_name, []):
        if k in scale_dict and is_energy_value(scale_dict[k]):
            candidates.append((k, k, scale_dict[k] / 8.0))

    if not candidates:
        return (float("inf"), "NONE", "-", float("nan"), [])

    best = None
    for tag, key, a in candidates:
        score, rows = evaluate_scale_with_alpha(scale_dict, a)
        item = (score, tag, key, a, rows)
        if (best is None) or (score < best[0]):
            best = item
    return best

def print_scale_report(scale_name: str, best_tuple):
    score, tag, key, alpha, rows = best_tuple
    print(f"\n=== Skala: {scale_name} ===")
    if tag == "NONE":
        print("Keine gültige Referenz gefunden – Skala übersprungen.")
        return
    print(f"ausgewählte Referenz: {tag} -> {key}")
    print(f"alpha = {alpha:.9g} eV   | mittlere rel. Abw. = {100*score:.3f}%")
    rows_sorted = sorted(rows, key=lambda r: r[6])
    for k, val, r, n, d, approx, rel in rows_sorted:
        print(f"- {k:>24}: {val:>12.6g} eV  |  r={r:>10.6f}  "
              f"~ {n}/{d} = {approx:>8.5f}   (rel. Abw. {100*rel:>6.3f}%)")

def main():
    print("ERT Auto-Referenz-Scan (8er-Raster)")
    DATA = load_dataset()
    for scale_name, scale_dict in DATA.items():
        best = choose_best_alpha(scale_name, scale_dict)
        print_scale_report(scale_name, best)

if __name__ == "__main__":
    main()