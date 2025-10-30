"""
ERT Spiralis-Generator (hierarchisch):
- Proton = erste vollständige 8er-Symmetrie
- H = 8-faches Proton (Ecken eines Würfels)
- O = höhere Ordnung: 8-faches H (H als "Baustein")
- H2 = 1D-Kopplung (zwei H entlang Achse)
- H2O = 2D-Kopplung (O-Brücke + zwei H im Winkel)
- Vacuum = reine Spiralis (Grundschwingung des Feldes)

Ausgabe: .vti (ParaView)
"""

import numpy as np
import vtk

# -------------------- Konstanten --------------------
ALPHA_STAR_DEG = 9.43034098            # exakt, nicht runden
ALPHA_STAR_RAD = ALPHA_STAR_DEG * np.pi / 180.0
BETA3 = ALPHA_STAR_RAD                  # 3D-Phasenlast

# Gitter
N = 192            # 256/512 für Final; 192 ist flott zum Testen
SPACING = (1.0, 1.0, 1.0)
CENTERED = True

# Kopplungs-/Stabilitätshebel
GEOM_POWER_H   = 0.60     # weiche Kopplung in H
GEOM_POWER_O   = 0.50     # noch weicher in O
GEOM_POWER_H2O = 0.55

ENVELOPE_R = 0.75          # radialer Dämpfungsradius (relativ)
ENVELOPE_P = 2.2           # Steilheit


# -------------------- Kern: Spiralis --------------------
def sigma3(x, y, z):
    """Octant-Faltung: |x|+|y|+|z|"""
    return np.abs(x) + np.abs(y) + np.abs(z)

def spiralis3(x, y, z, beta=BETA3):
    """3D-Spiralis: sin(beta * (|x|+|y|+|z|))"""
    return np.sin(beta * sigma3(x, y, z))

def normalize01(vol):
    vmin, vmax = float(vol.min()), float(vol.max())
    if vmax == vmin:
        return np.zeros_like(vol, dtype=np.float32)
    return ((vol - vmin) / (vmax - vmin)).astype(np.float32)

def grid(N=N, centered=True):
    if centered:
        c = (N - 1) / 2.0
        ax = np.arange(N) - c
    else:
        ax = np.arange(N)
    X, Y, Z = np.meshgrid(ax, ax, ax, indexing='ij')
    return X.astype(np.float64), Y.astype(np.float64), Z.astype(np.float64)

def combine_geometric(fields, power=1.0):
    """Weiche Kopplung: geometrisches Mittel mit Power (<=1)"""
    eps = 1e-9
    acc = np.ones_like(fields[0], dtype=np.float64)
    for f in fields:
        acc *= np.clip(f, eps, 1.0)
    k = len(fields)
    return np.power(acc, power / k)

def radial_envelope(X, Y, Z, R=ENVELOPE_R, p=ENVELOPE_P):
    """Sanfte radiale Dämpfung, damit Hierarchie nicht 'explodiert'."""
    N = X.shape[0]
    c = (N - 1) / 2.0
    xn, yn, zn = (X / c), (Y / c), (Z / c)
    r = np.sqrt(xn * xn + yn * yn + zn * zn)
    E = np.exp(- (r / max(R, 1e-6)) ** p)
    return E.astype(np.float64)


# -------------------- Bausteine (Hierarchie) --------------------
def field_vacuum(N=N):
    """Vakuum/Hintergrund: reine Spiralis (Grundschwingung)."""
    X, Y, Z = grid(N, CENTERED)
    F = spiralis3(X, Y, Z)
    return normalize01(F)

def proton(N=N, scale=1.0, use_env=True):
    """Proton = erste vollständige 8er-Symmetrie (zentraler Knoten)."""
    X, Y, Z = grid(N, CENTERED)
    F = spiralis3(X / scale, Y / scale, Z / scale)
    if use_env:
        F = F * radial_envelope(X, Y, Z, R=0.95, p=2.0)
    return normalize01(F)

def H_subfield(X, Y, Z, d=18.0, scale_proton=2.0):
    """Lokales H-Feld (ohne Normierung), aus 8 Proton-Subknoten."""
    fields = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                f = spiralis3((X + sx * d) / scale_proton,
                              (Y + sy * d) / scale_proton,
                              (Z + sz * d) / scale_proton)
                fields.append(normalize01(f))
    return combine_geometric(fields, power=GEOM_POWER_H)

def H_atom(N=N, d=18.0, scale_proton=2.0, use_env=True):
    """H = 8-faches Proton (Ecken eines Würfels, sanft gekoppelt)."""
    X, Y, Z = grid(N, CENTERED)
    F = H_subfield(X, Y, Z, d=d, scale_proton=scale_proton)
    if use_env:
        F *= radial_envelope(X, Y, Z, R=0.85, p=2.1)
    return normalize01(F)

def oxygen_atom(N=N, D=34.0, d_H=12.0, scale_H=2.6, use_env=True):
    """
    O = höhere Ordnung: 8-faches H.
    D  : äußeres Würfel-Offset (Position der H-Zentren)
    d_H: internes H-Offset (Eckenabstand in H_subfield)
    """
    X, Y, Z = grid(N, CENTERED)
    fields = []
    for SX in (-1, 1):
        for SY in (-1, 1):
            for SZ in (-1, 1):
                Fx = X + SX * D
                Fy = Y + SY * D
                Fz = Z + SZ * D
                h_loc = H_subfield(Fx, Fy, Fz, d=d_H, scale_proton=scale_H)
                fields.append(h_loc)
    O = combine_geometric(fields, power=GEOM_POWER_O)
    if use_env:
        O *= radial_envelope(X, Y, Z, R=0.80, p=2.3)
    return normalize01(O)

def H2_molecule(N=N, sep=56.0, axis='x', h_kwargs=None, use_env=True):
    """H2 = 1D-Kopplung zweier H entlang einer Achse."""
    if h_kwargs is None:
        h_kwargs = dict(d=18.0, scale_proton=2.0)
    X, Y, Z = grid(N, CENTERED)
    half = sep / 2.0
    if axis == 'x':
        H1 = H_subfield(X - half, Y, Z, **h_kwargs)
        H2 = H_subfield(X + half, Y, Z, **h_kwargs)
    elif axis == 'y':
        H1 = H_subfield(X, Y - half, Z, **h_kwargs)
        H2 = H_subfield(X, Y + half, Z, **h_kwargs)
    else:
        H1 = H_subfield(X, Y, Z - half, **h_kwargs)
        H2 = H_subfield(X, Y, Z + half, **h_kwargs)
    F = combine_geometric([H1, H2], power=0.7)
    if use_env:
        F *= radial_envelope(X, Y, Z, R=0.9, p=2.0)
    return normalize01(F)

def H2O_molecule(N=N, sep_H=38.0, bend_deg=104.5,
                 O_kwargs=None, H_kwargs=None, use_env=True):
    """
    H^2O = 2D-Kopplung (O-Brücke + zwei H in x–z-Ebene).
    """
    if O_kwargs is None:
        O_kwargs = dict(D=34.0, d_H=12.0, scale_H=2.6)
    if H_kwargs is None:
        H_kwargs = dict(d=18.0, scale_proton=2.0)

    X, Y, Z = grid(N, CENTERED)

    # O zentriert (höhere Ordnung)
    O = oxygen_atom(N=N, **O_kwargs, use_env=False)

    # zwei H in V-Geometrie (x–z Ebene)
    theta = np.deg2rad(bend_deg / 2.0)
    hx = np.sin(theta) * sep_H
    hz = np.cos(theta) * sep_H
    H1 = H_subfield(X - hx, Y, Z - hz, **H_kwargs)
    H2 = H_subfield(X + hx, Y, Z - hz, **H_kwargs)

    # sanfte Kopplung aller drei Felder
    F = combine_geometric([O, H1, H2], power=GEOM_POWER_H2O)
    if use_env:
        F *= radial_envelope(X, Y, Z, R=0.85, p=2.2)
    return normalize01(F)


# -------------------- VTI Writer --------------------
def write_vti(array01, filename, spacing=SPACING):
    arr = np.ascontiguousarray(array01.transpose(2, 1, 0))  # (Z,Y,X)->(X,Y,Z)
    nx, ny, nz = arr.shape
    image = vtk.vtkImageData()
    image.SetDimensions(nx, ny, nz)
    image.SetSpacing(spacing)
    image.AllocateScalars(vtk.VTK_FLOAT, 1)
    scal = vtk.vtkFloatArray.SafeDownCast(image.GetPointData().GetScalars())
    scal.SetName("spiralis")
    scal.SetNumberOfValues(nx * ny * nz)
    scal.SetArray(arr.ravel(order='C'), nx * ny * nz, 1)
    w = vtk.vtkXMLImageDataWriter()
    w.SetFileName(filename)
    w.SetInputData(image)
    w.Write()


# -------------------- Ausführung --------------------
if __name__ == "__main__":
    # 0) Vacuum (Grundschwingung)
    write_vti(field_vacuum(N), "vacuum.vti")

    # 1) Proton (Grundzustand, sichtbar via Opacity in ParaView)
    write_vti(proton(N, scale=1.0), "proton.vti")

    # 2) H (8 x Proton)
    write_vti(H_atom(N, d=18.0, scale_proton=2.0), "H.vti")

    # 3) O (8 x H) – explizit gewünscht
    write_vti(oxygen_atom(N, D=34.0, d_H=12.0, scale_H=2.6), "oxygen.vti")

    # 4) H2 (1D-Kopplung)
    write_vti(H2_molecule(N, sep=56.0, axis='x'), "H2.vti")

    # 5) H^2O (2D-Kopplung)
    write_vti(H2O_molecule(N, sep_H=38.0, bend_deg=104.5), "H2O.vti")
