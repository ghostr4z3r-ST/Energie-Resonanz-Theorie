# ert_dataset.py
# Alle Energieskalen in eV (MeV => *1e6). Wellenzahlen/Temperatur konvertiert.

DATA = {
    "atomic": {
        "H_ionization_eV": 13.605693,
        "H_Ly_alpha_eV": 10.200,      # 121.567 nm
        "H_Halpha_eV":   1.889,       # 656.28 nm
        "Rydberg_m_inv": 10973731.568160,
        "alpha_atomic_eV": 13.605693/8.0,  # = 1.7007116 eV
    },
    "nuclear": {
        "Deuteron_binding_eV": 2.224566e6,   # MeV -> eV
        "He4_binding_eV":      28.295674e6,  # MeV -> eV
        "Proton_rest_eV":      938.272081e6,
        "Proton_radius_fm":    0.8409,
        # Platzhalter für spätere Skalenwahl:
        "alpha_nuclear_eV": None
    },
    "cosmo": {
        "CMB_T_K":         2.725,
        "CMB_kBT_eV":      2.725 * 8.617333262e-5,  # ~2.352e-4 eV
        "CMB_l1_peak":     220,
        "CMB_delta_T":     1e-5,
        "alpha_cosmo_eV":  None
    },
    "material_diamond": {
        "Raman_1332cm1_eV": 0.1653,   # 1332 cm^-1 ~ 0.165 eV
        "Bandgap_eV":       5.47,
        "Density_g_cm3":    3.51
    }
}

def multiples_of_alpha(value_eV, alpha_eV):
    if alpha_eV is None or alpha_eV == 0:
        return None
    return value_eV / alpha_eV

if __name__ == "__main__":
    a = DATA["atomic"]["alpha_atomic_eV"]
    print(f"alpha_atomic = {a:.9f} eV")
    for k in ("H_ionization_eV","H_Ly_alpha_eV","H_Halpha_eV"):
        v = DATA["atomic"][k]
        m = multiples_of_alpha(v, a)
        print(f"{k:>18}: {v:>10.6f} eV  ->  {m:>8.3f} x alpha")