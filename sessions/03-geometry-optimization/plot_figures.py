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


if __name__ == "__main__":
    fig_errors()
