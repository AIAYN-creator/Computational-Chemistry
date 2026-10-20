"""Builds every figure of Session 03 from the processed data files.

Usage (from this folder):  python plot_figures.py
Requires numpy and matplotlib. Figures are written to figures/.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

# Categorical slots in fixed order; each molecule keeps its colour in every panel
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SURFACE = "#fcfcfb"

plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "cm",
    "font.size": 10,
    "axes.edgecolor": INK_2,
    "axes.labelcolor": INK,
    "axes.titlesize": 11,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "ytick.minor.visible": True,
    "legend.frameon": False,
    "lines.linewidth": 1.8,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "savefig.dpi": 200,
})

BASES = ["sto3g", "321g", "631gs", "631gss"]
BASIS_NAMES = ["STO-3G", "3-21G", "6-31G*", "6-31G**"]

# molecule: (label, colour, marker)
MOLS = {
    "ch4": (r"CH$_4$", BLUE, "o"),
    "h2o": (r"H$_2$O", ORANGE, "s"),
    "hf": ("HF", AQUA, "^"),
    "nh3": (r"NH$_3$", YELLOW, "D"),
}

# Experimental equilibrium values (NIST CCCBDB): r (Å), angle (deg), dipole (D)
EXP = {
    "ch4": {"r": 1.086, "angle": 109.47, "mu": 0.0},
    "h2o": {"r": 0.958, "angle": 104.5, "mu": 1.85},
    "hf": {"r": 0.917, "angle": None, "mu": 1.83},
    "nh3": {"r": 1.012, "angle": 106.7, "mu": 1.47},
}


def save(fig, name):
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)
    print("Written", OUT / name)


def load_results():
    """{(mol, basis): {"r", "angle", "mu", "E", "steps"}} from ex1/results.txt."""
    rows = (HERE / "ex1-optimized-geometries/results.txt").read_text().splitlines()[1:]
    data = {}
    for line in rows:
        mol, basis, r, angle, mu, e, steps = line.split()
        data[(mol, basis)] = {
            "r": float(r),
            "angle": None if angle == "-" else float(angle),
            "mu": float(mu),
            "E": float(e),
            "steps": int(steps),
        }
    return data


# --- Figure 1: error against experiment vs basis set ------------------------
def fig_errors():
    data = load_results()
    x = np.arange(len(BASES))
    panels = [
        ("r", r"$r_{\mathrm{calc}} - r_{\mathrm{exp}}$ (Å)", "Bond length", ["ch4", "h2o", "hf", "nh3"]),
        ("angle", r"$\theta_{\mathrm{calc}} - \theta_{\mathrm{exp}}$ (°)", "Bond angle", ["h2o", "nh3"]),
        ("mu", r"$\mu_{\mathrm{calc}} - \mu_{\mathrm{exp}}$ (D)", "Dipole moment", ["h2o", "hf", "nh3"]),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.9))
    for ax, (key, ylabel, title, mols) in zip(axes, panels):
        ax.axhline(0, color=INK_2, lw=1, ls=":")
        ends = []
        for mol in mols:
            label, color, marker = MOLS[mol]
            err = [data[(mol, b)][key] - EXP[mol][key] for b in BASES]
            ax.plot(x, err, color=color, marker=marker, ms=6, label=label)
            ends.append([err[-1], label])
        ax.set_title(title, loc="left")
        ax.set_ylabel(ylabel)
        ax.set_xticks(x, BASIS_NAMES)
        ax.set_xlim(-0.3, len(BASES) - 0.4)
        ax.annotate("experiment", xy=(0.02, 0), xycoords=ax.get_yaxis_transform(),
                    xytext=(0, 3), textcoords="offset points", fontsize=8, color=INK_2)

        # Direct labels at the line ends (relief for the low-contrast hues),
        # pushed apart vertically so they never overlap
        lo, hi = ax.get_ylim()
        gap = 0.065 * (hi - lo)
        ends.sort()
        for i in range(1, len(ends)):
            ends[i][0] = max(ends[i][0], ends[i - 1][0] + gap)
        for y, label in ends:
            ax.annotate(label, xy=(x[-1], y), xytext=(9, 0), textcoords="offset points",
                        va="center", fontsize=9, color=INK)
    axes[0].legend(loc="upper right", fontsize=8.5, ncol=2)
    fig.suptitle("HF optimised geometries and dipoles: error against experiment",
                 x=0.01, ha="left", fontsize=11.5)
    fig.tight_layout()
    save(fig, "error_vs_basis.png")


# --- Figure 2: simulated IR spectrum of water (ex2) -------------------------
# Experimental fundamentals of H2O (NIST CCCBDB), cm-1, in mode order
# (bend, symmetric stretch, antisymmetric stretch)
EXP_FUND = [1595, 3657, 3756]
# Scale factor for HF/6-31G(d) harmonic frequencies (Scott & Radom, 1996)
SCALE = 0.8953
MODE_NAMES = ["bend", "sym. stretch", "asym. stretch"]


def fig_ir_spectrum():
    rows = [l.split() for l in (HERE / "ex2-vibrational-frequencies/frequencies.txt")
            .read_text().splitlines() if l and l[0].isdigit()]
    freq = np.array([float(r[2]) for r in rows])
    inten = np.array([float(r[3]) for r in rows])

    nu = np.linspace(1400, 4400, 6000)
    hwhm = 12.0

    def spectrum(centres):
        # Sum of Lorentzians with the computed IR intensities as weights
        return sum(i * hwhm**2 / ((nu - c)**2 + hwhm**2) for c, i in zip(centres, inten))

    raw, scaled = spectrum(freq), spectrum(freq * SCALE)
    top = raw.max()

    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(nu, raw / top, color=BLUE, lw=1.6, label="HF/6-31G*, harmonic")
    ax.plot(nu, scaled / top, color=ORANGE, lw=1.6, ls="--",
            label=f"HF/6-31G*, scaled × {SCALE}")
    for k, e in enumerate(EXP_FUND):
        ax.axvline(e, color=INK_2, lw=1, ls=":", label="experiment (fundamentals)" if k == 0 else None)

    for c, i, name in zip(freq, inten, MODE_NAMES):
        ax.annotate(f"{name}\n{c:.0f}", xy=(c, i / top), xytext=(0, 6), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.5, color=INK)

    ax.set_xlim(4400, 1400)  # IR convention: wavenumber decreases to the right
    ax.set_ylim(0, 1.3)
    ax.set_yticks([])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(r"Wavenumber (cm$^{-1}$)")
    ax.set_ylabel("IR intensity (arb. units)")
    ax.set_title(r"H$_2$O: simulated IR spectrum (Lorentzian, HWHM 12 cm$^{-1}$)", loc="left")
    ax.legend(loc="upper center", fontsize=8.5, ncol=3)
    save(fig, "ir_spectrum.png")


if __name__ == "__main__":
    fig_errors()
    fig_ir_spectrum()
