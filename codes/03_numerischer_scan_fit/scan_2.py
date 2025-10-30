import math
from statistics import median
#Residuen aus dem Ergebnis von operator_fit.py
RES = [
    ("H_ionization_eV",   11.542064),
    ("H_Ly_alpha_eV",      8.652921),
    ("H_Halpha_eV",        1.602487),
    ("CMB_kBT_eV",         6.527567),
    ("CMB_delta_T_eV",     0.277979),
    ("Deuteron_binding_eV",0.014060),
    ("He4_binding_eV",     0.178843),
    ("Proton_rest_eV",     5.930366),
]
# === 2) 8er-Rundung ===
K_MIN, K_MAX = -20, 20  # erlaubte Potenzen (breit genug)

def nearest_power_of_8(x: float) -> float:
    if x == 0.0:
        return 0.0
    s = 1.0 if x > 0 else -1.0
    ax = abs(x)
    k = round(math.log(ax, 8))
    k = max(K_MIN, min(K_MAX, k))
    return s * (8.0 ** k)

# === 3) Zielfunktion ===
def objective(res_vals, eps):
    if eps <= 0.0:
        return float("inf")
    err2 = 0.0
    for _, r in res_vals:
        m = nearest_power_of_8(r / eps) if eps != 0 else 0.0
        err = r - m * eps
        err2 += err * err
    return err2

# === 4) robuster Startschätzer und Log-Scan ===
def robust_seed(res_vals):
    mags = [abs(r) for _, r in res_vals if r != 0.0]
    if not mags:
        return 1e-12
    m = median(mags)
    k = round(math.log(m, 8)) if m > 0 else 0
    k = max(K_MIN//2, min(K_MAX//2, k))
    base = (8.0 ** k) if k != 0 else 1.0
    return m / base

def search_eps(res_vals, seed=None, widen=6, ngrid=3000):
    if seed is None or seed <= 0.0:
        seed = robust_seed(res_vals)
    best_eps, best_val = None, float("inf")
    for dk in range(-widen, widen+1):
        eps0 = seed * (8.0 ** dk)
        lo, hi = eps0/8.0, eps0*8.0
        if lo <= 0: 
            continue
        # log-uniform scan
        for j in range(ngrid):
            t = j/(ngrid-1)
            eps = lo * ((hi/lo) ** t)
            val = objective(res_vals, eps)
            if val < best_val:
                best_val, best_eps = val, eps
    return best_eps, best_val

# === 5) Lauf & Ausgabe ===
def main():
    eps, val = search_eps(RES)
    print("\nResiduenfit")
    print(f"E_SW = {eps:.12e}  (beste Zielfunktion L2 = {val:.6e})\n")
    print(f"{'id':<18} {'residual':>14} {'m(~8^k)':>14} {'k':>5} {'corr=m x E':>14} {'after':>14}")
    print("-"*80)
    for lab, r in RES:
        m = nearest_power_of_8(r/eps) if eps != 0 else 0.0
        k = None if m == 0 else round(math.log(abs(m), 8)) * (1 if m>0 else -1)
        corr = m * eps
        after = r - corr
        print(f"{lab:<18} {r:>14.6e} {m:>14.6e} {str(k):>5} {corr:>14.6e} {after:>14.6e}")

if __name__ == "__main__":
    main()