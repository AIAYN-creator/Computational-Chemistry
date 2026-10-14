"""Builds every figure of Session 02 from the processed data files.

Usage (from this folder):  python plot_figures.py
Requires numpy and matplotlib. Figures are written to figures/.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

HARTREE_TO_EV = 27.211386

# Categorical slots, fixed order: 1 = RHF / first series, 2 = UHF, 3 = third series
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
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
    "xtick.minor.visible": True,
    "ytick.minor.visible": True,
    "legend.frameon": False,
    "lines.linewidth": 1.8,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "savefig.dpi": 200,
})


def load(path, skip=1):
    """Numeric columns of a data file, sorted by the first column (r)."""
    data = np.loadtxt(HERE / path, skiprows=skip, comments="#")
    return data[np.argsort(data[:, 0])]


def coulson_fischer(rhf, uhf, tol=1e-6):
    """First grid point where UHF drops below RHF, and the one before it."""
    split = np.abs(uhf[:, 1] - rhf[:, 1]) > tol
    i = np.argmax(split)
    return rhf[i - 1, 0], rhf[i, 0]


def save(fig, name):
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)
    print("Written", OUT / name)


# --- Figure 1: RHF vs UHF dissociation + spin contamination (ex6) -----------
def fig_rhf_vs_uhf():
    fig, axes = plt.subplots(2, 2, figsize=(9, 5.6), sharex="col",
                             gridspec_kw={"height_ratios": [2.2, 1], "hspace": 0.08,
                                          "wspace": 0.3})
    panels = [("h2", r"H$_2$", r"$2E(\mathrm{H})$"),
              ("lih", "LiH", r"$E(\mathrm{Li}) + E(\mathrm{H})$")]

    for col, (mol, label, ref) in enumerate(panels):
        rhf = load(f"ex6-rhf-vs-uhf/{mol}_rhf.dat")
        uhf = load(f"ex6-rhf-vs-uhf/{mol}_uhfmix.dat")
        r_lo, r_hi = coulson_fischer(rhf, uhf)
        top, bottom = axes[0, col], axes[1, col]

        top.axhline(0, color=INK_2, lw=1, ls=":", label=f"separated atoms, {ref}")
        top.plot(rhf[:, 0], rhf[:, 1], color=BLUE, label="RHF")
        top.plot(uhf[:, 0], uhf[:, 1], color=ORANGE, ls="--", label="UHF, guess=mix")
        top.set_title(f"{label}, HF/3-21G", loc="left")
        top.set_ylabel(r"$\Delta E$ (hartree)")
        top.legend(loc="lower right", fontsize=8.5)

        # Direct label: RHF error at the largest distance
        err = rhf[-1, 1]
        top.text(0.98, 0.62, f"RHF error at {rhf[-1, 0]:g} Å:\n{err * HARTREE_TO_EV:.2f} eV",
                 transform=top.transAxes, ha="right", fontsize=8.5, color=INK)

        bottom.plot(uhf[:, 0], uhf[:, 2], color=ORANGE, ls="--", marker="o", ms=3)
        bottom.set_ylabel(r"$\langle \hat S^2 \rangle$ UHF")
        bottom.set_xlabel(r"$r$ (Å)")
        bottom.set_ylim(-0.1, 1.15)
        bottom.set_yticks([0, 0.5, 1])

        for ax in (top, bottom):
            ax.axvspan(r_lo, r_hi, color=INK_2, alpha=0.12, lw=0)
        bottom.annotate("Coulson–Fischer\npoint", xy=(r_hi, 0.5), xytext=(22, -8),
                        textcoords="offset points", va="center", fontsize=8.5, color=INK)

    save(fig, "rhf_vs_uhf.png")


# --- Figure 2: UHF depends on the initial guess (ex4 + ex5) ----------------
def fig_initial_guess():
    rhf = load("ex4-rhf-dissociation/results.txt", skip=2)
    nomix = load("ex5-uhf-initial-guess/h2_uhf.dat")
    mix = load("ex5-uhf-initial-guess/h2_uhfmix.dat")

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.axhline(0, color=INK_2, lw=1, ls=":", label=r"separated atoms, $2E(\mathrm{H})$")
    ax.plot(rhf[:, 0], rhf[:, 1], color=BLUE, label="RHF")
    ax.plot(nomix[:, 0], nomix[:, 1], color=AQUA, ls="none", marker="o", ms=5,
            mfc="none", mew=1.3, label="UHF, default guess")
    ax.plot(mix[:, 0], mix[:, 1], color=ORANGE, ls="--", label="UHF, guess=mix")
    ax.set_title(r"H$_2$, HF/STO-3G: the UHF result depends on the initial guess",
                 loc="left")
    ax.set_xlabel(r"$r$ (Å)")
    ax.set_ylabel(r"$\Delta E$ (hartree)")
    ax.legend(loc="center right", fontsize=8.5)
    ax.annotate("default-guess UHF falls\nexactly on the RHF curve",
                xy=(6, rhf[np.searchsorted(rhf[:, 0], 6), 1]), xytext=(4.2, 0.2),
                fontsize=8.5, color=INK,
                arrowprops={"arrowstyle": "-", "color": INK_2, "lw": 0.8})
    save(fig, "initial_guess.png")


# --- Figure 3: basis-set convergence (ex2) ---------------------------------
def fig_basis_sets():
    basis = ["sto3g", "321g", "431g", "631gd", "631gdp"]
    names = ["STO-3G", "3-21G", "4-31G", "6-31G(d)", "6-31G(d,p)"]
    mols = [("h2", r"H$_2$"), ("hf", "HF"), ("co", "CO"),
            ("n2", r"N$_2$"), ("ch4", r"CH$_4$"), ("h2o", r"H$_2$O")]

    energies = {}
    for line in (HERE / "ex2-basis-sets/results.txt").read_text().splitlines()[1:]:
        f, e, *_ = line.split()
        mol, b = f.removesuffix(".log").split("_")
        energies[(mol, b)] = float(e)

    fig, axes = plt.subplots(2, 3, figsize=(9, 5), sharex=True)
    x = np.arange(len(basis))
    for ax, (mol, label) in zip(axes.flat, mols):
        e = np.array([energies[(mol, b)] for b in basis])
        de = (e - e[-1]) * 1000  # mhartree above the largest basis
        ax.plot(x, de, color=BLUE, marker="o", ms=5)
        for i in range(1, len(basis)):
            if abs(e[i] - e[i - 1]) < 1e-9:
                ax.annotate("same energy", xy=(i - 0.5, de[i]), xytext=(0, 7),
                            textcoords="offset points", ha="center",
                            fontsize=7.5, color=INK_2)
        ax.set_title(label, loc="left")
        ax.set_xticks(x, names, rotation=40, ha="right", fontsize=8)
        ax.xaxis.set_minor_locator(plt.NullLocator())
        ax.set_ylim(bottom=-0.08 * de.max(), top=1.15 * de.max())
    for ax in axes[:, 0]:
        ax.set_ylabel(r"$E - E_{\mathrm{6\text{-}31G(d,p)}}$ (mhartree)")
    fig.suptitle("HF total energy vs basis set (variational: it can only go down)",
                 x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    save(fig, "basis_sets.png")


# --- Figure 4: equilibrium bond length vs basis set (ex3) -------------------
def fig_bond_scans():
    rows = [l.split() for l in (HERE / "ex3-bond-scans/results.txt").read_text().splitlines()[1:]]
    series = [("sto3g", "STO-3G", AQUA, "o"), ("321g", "3-21G", BLUE, "s"),
              ("631gdp", "6-31G(d,p)", ORANGE, "^")]
    # Experimental r_e: Huber & Herzberg (1979)
    mols = [("h2scan", r"H$_2$", 0.741), ("hfscan", "HF", 0.917)]

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    for ax, (mol, label, r_exp) in zip(axes, mols):
        for b, name, color, marker in series:
            d = np.array([(float(r), float(e)) for f, r, e in rows if f == f"{mol}_{b}.log"])
            d = d[np.argsort(d[:, 0])]
            rel = (d[:, 1] - d[:, 1].min()) * 1000
            i = np.argmin(d[:, 1])  # parabola through the 3 points around the minimum
            a, bb, _ = np.polyfit(d[i - 1:i + 2, 0], d[i - 1:i + 2, 1], 2)
            r_min = -bb / (2 * a)
            ax.plot(d[:, 0], rel, color=color, marker=marker, ms=4.5, lw=1.4,
                    label=f"{name}: $r_e$ ≈ {r_min:.3f} Å")
        ax.axvline(r_exp, color=INK_2, lw=1, ls=":")
        ax.annotate(f"exp. {r_exp} Å", xy=(r_exp, ax.get_ylim()[1]), xytext=(3, -12),
                    textcoords="offset points", fontsize=8.5, color=INK_2)
        ax.set_title(f"{label}, HF bond-length scan", loc="left")
        ax.set_xlabel(r"$r$ (Å)")
        ax.set_ylabel(r"$E - E_{\min}$ (mhartree)")
        ax.legend(fontsize=8.5, loc="upper center")
        ax.set_ylim(top=ax.get_ylim()[1] * 1.45)
    fig.tight_layout()
    save(fig, "bond_scans.png")


if __name__ == "__main__":
    fig_rhf_vs_uhf()
    fig_initial_guess()
    fig_basis_sets()
    fig_bond_scans()
