"""Draws every Z-matrix of Session 01 by converting it to Cartesian coordinates.

Usage (from this folder):  python plot_figures.py
Requires numpy and matplotlib. Figures are written to figures/.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

INK, INK_2 = "#0b0b0b", "#52514e"
SURFACE = "#fcfcfb"
ELEMENT = {  # colour, marker size
    "H": ("#e4e3df", 260), "C": ("#5c5f66", 520), "O": ("#e03131", 520),
    "Cl": ("#2f9e44", 700), "X": ("none", 200),
}

plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "cm",
    "font.size": 10,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "savefig.dpi": 200,
})


def read_zmatrix(path):
    """Atom lines and variables of a Z-matrix (bare .zmat or a Gaussian .com)."""
    lines = [l.strip() for l in path.read_text().splitlines()]
    if path.suffix == ".com":  # skip everything up to the charge/multiplicity line
        start = next(i for i, l in enumerate(lines) if l.split() == ["0", "1"]) + 1
        lines = lines[start:]
    while lines and not lines[0]:
        lines.pop(0)
    blank = lines.index("") if "" in lines else len(lines)
    atoms = [l.split() for l in lines[:blank]]
    variables = {}
    for l in lines[blank + 1:]:
        if l:
            name, value = l.split()
            variables[name] = float(value)
    return atoms, variables


def value(token, variables):
    """A Z-matrix entry: a number, a variable, or a negated variable."""
    try:
        return float(token)
    except ValueError:
        sign = -1.0 if token.startswith("-") else 1.0
        return sign * variables[token.lstrip("-")]


def to_cartesian(atoms, variables):
    """Place each atom from its distance, angle and dihedral references."""
    pos = []
    for k, row in enumerate(atoms):
        if k == 0:
            pos.append(np.zeros(3))
            continue
        a = pos[int(row[1]) - 1]
        r = value(row[2], variables)
        if k == 1:
            pos.append(a + np.array([0.0, 0.0, r]))
            continue
        b = pos[int(row[3]) - 1]
        theta = np.radians(value(row[4], variables))
        u = (a - b) / np.linalg.norm(a - b)
        if k == 2:
            perp = np.cross(u, [0, 1, 0]) if abs(u[1]) < 0.9 else np.cross(u, [1, 0, 0])
            perp /= np.linalg.norm(perp)
            pos.append(a + r * (-u * np.cos(theta) + perp * np.sin(theta)))
            continue
        c = pos[int(row[5]) - 1]
        phi = np.radians(value(row[6], variables))
        n = np.cross(b - c, u)
        n /= np.linalg.norm(n)
        m = np.cross(n, u)
        d = np.array([-r * np.cos(theta), r * np.sin(theta) * np.cos(phi),
                      r * np.sin(theta) * np.sin(phi)])
        pos.append(a + d[0] * u + d[1] * m + d[2] * n)
    return np.array(pos)


def project(pos):
    """2D view: principal axes of all atoms (dummies included, so a linear
    molecule still gets a plane), slightly tilted for depth."""
    centre = pos.mean(axis=0)
    _, _, axes = np.linalg.svd(pos - centre)
    p = (pos - centre) @ axes.T
    return np.column_stack([p[:, 0], p[:, 1] + 0.35 * p[:, 2]])


PANELS = [
    ("z-matrices/h2o.zmat", r"H$_2$O"),
    ("z-matrices/h2o2_trans.zmat", r"H$_2$O$_2$, trans (dihedral 180°)"),
    ("z-matrices/h2o2_cis.zmat", r"H$_2$O$_2$, cis (dihedral 0°)"),
    ("z-matrices/ch3cl.zmat", r"CH$_3$Cl"),
    ("z-matrices/hcch.zmat", "HCCH, one dummy atom per carbon"),
    ("single-points/metoh.com", r"CH$_3$OH, staggered"),
]


def fig_zmatrices():
    fig, axes = plt.subplots(2, 3, figsize=(10, 6.2))
    for ax, (file, title) in zip(axes.flat, PANELS):
        atoms, variables = read_zmatrix(HERE / file)
        pos = to_cartesian(atoms, variables)
        symbols = [row[0].capitalize() for row in atoms]
        real = [s != "X" for s in symbols]
        xy = project(pos)

        # Bonds: each atom to its distance reference
        for k, row in enumerate(atoms[1:], start=1):
            j = int(row[1]) - 1
            dummy = not (real[k] and real[j])
            ax.plot(*zip(xy[k], xy[j]), color="#8a8986",
                    lw=1 if dummy else 4, ls="--" if dummy else "-",
                    zorder=1, solid_capstyle="round")
        # Atoms, back to front
        for k in np.argsort(-pos[:, 2]):
            colour, size = ELEMENT[symbols[k]]
            ax.scatter(*xy[k], s=size, color=colour, zorder=2, lw=1,
                       edgecolor=INK_2 if symbols[k] == "X" else INK,
                       linestyle="--" if symbols[k] == "X" else "-")
            if symbols[k] == "X":
                ax.annotate("X", xy[k], ha="center", va="center", fontsize=8, color=INK_2, zorder=3)
        ax.set_title(title, fontsize=10.5)
        ax.set_aspect("equal")
        span = np.ptp(xy, axis=0).max() / 2 + 0.6
        cx, cy = (xy.min(axis=0) + xy.max(axis=0)) / 2
        ax.set_xlim(cx - span, cx + span)
        ax.set_ylim(cy - span, cy + span)
        ax.axis("off")
    fig.suptitle("Session 01 Z-matrices, converted to Cartesian coordinates", x=0.01,
                 ha="left", fontsize=11.5)
    fig.tight_layout()
    fig.savefig(OUT / "z_matrices.png", bbox_inches="tight")
    plt.close(fig)
    print("Written", OUT / "z_matrices.png")

    # Sanity check: the acetylene Z-matrix must give a linear molecule
    atoms, variables = read_zmatrix(HERE / "z-matrices/hcch.zmat")
    pos = to_cartesian(atoms, variables)
    c1, c2, h1, h2 = pos[0], pos[1], pos[4], pos[5]

    def angle(a, b, c):
        u, v = a - b, c - b
        return np.degrees(np.arccos(u @ v / np.linalg.norm(u) / np.linalg.norm(v)))

    print(f"HCCH angles: H-C-C {angle(h1, c1, c2):.1f}, C-C-H {angle(c1, c2, h2):.1f}")


if __name__ == "__main__":
    fig_zmatrices()
