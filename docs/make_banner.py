"""Builds docs/banner.png: water followed through the course, one panel per session.

Usage (from the repository root):  python docs/make_banner.py
Every number comes from the data files of the sessions.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
S01 = ROOT / "sessions/01-linux-and-z-matrices"
S02 = ROOT / "sessions/02-hartree-fock"
S03 = ROOT / "sessions/03-geometries-and-conformers"

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SURFACE = "#fcfcfb"

plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "cm",
    "font.size": 10,
    "axes.edgecolor": INK_2,
    "axes.labelcolor": INK,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "savefig.dpi": 200,
})


def zmatrix_water():
    lines = (S01 / "z-matrices/h2o.zmat").read_text().split()
    v = dict(zip(lines[-4::2], map(float, lines[-3::2])))
    return v["r1"], v["a2"]


def basis_energies():
    names = ["sto3g", "321g", "431g", "631gd", "631gdp"]
    e = {}
    for line in (S02 / "ex2-basis-sets/results.txt").read_text().splitlines()[1:]:
        f, energy, *_ = line.split()
        mol, b = f.removesuffix(".log").split("_")
        if mol == "h2o":
            e[b] = float(energy)
    return names, [e[b] for b in names]


def optimised_angles():
    names = ["sto3g", "321g", "631gs", "631gss"]
    a = {}
    for line in (S03 / "ex1-optimized-geometries/results.txt").read_text().splitlines()[1:]:
        mol, b, r, angle, *_ = line.split()
        if mol == "h2o":
            a[b] = float(angle)
    return names, [a[b] for b in names]


def frequencies():
    rows = [l.split() for l in (S03 / "ex2-vibrational-frequencies/frequencies.txt")
            .read_text().splitlines() if l and l[0].isdigit()]
    return np.array([float(r[2]) for r in rows]), np.array([float(r[3]) for r in rows])


def tag(ax, text):
    ax.text(0.0, 1.17, text, transform=ax.transAxes, fontsize=8.5, color=INK_2,
            fontweight="bold", va="bottom")


def main():
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.3),
                             gridspec_kw={"width_ratios": [0.8, 1, 1, 1.25], "wspace": 0.42})

    # 1. Session 01: the Z-matrix, drawn
    ax = axes[0]
    r, a = zmatrix_water()
    half = np.radians(a / 2)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    # Z-matrix text on top, molecule below, both inside the same axes box
    # as the other panels so the titles line up
    ax.text(0.0, 0.97, f"O\nH 1 r1\nH 1 r1 2 a2\n\nr1 = {r} Å\na2 = {a}°", fontsize=8.5,
            family="monospace", color=INK_2, va="top", transform=ax.transAxes)
    inset = ax.inset_axes([0.05, 0.0, 0.9, 0.5])
    o = np.array([0.0, 0.0])
    h1 = o + r * np.array([-np.sin(half), -np.cos(half)])
    h2 = o + r * np.array([np.sin(half), -np.cos(half)])
    for h in (h1, h2):
        inset.plot(*zip(o, h), color="#8a8986", lw=5, zorder=1, solid_capstyle="round")
    inset.scatter(*o, s=700, color="#e03131", edgecolor=INK, zorder=2)
    inset.scatter(*zip(h1, h2), s=300, color="#e4e3df", edgecolor=INK, zorder=2)
    arc = np.linspace(-half, half, 40) - np.pi / 2
    inset.plot(0.3 * np.cos(arc), 0.3 * np.sin(arc), color=INK_2, lw=1)
    inset.text(0, -0.5, "a2", ha="center", fontsize=9, color=INK, family="monospace")
    inset.text(*(h2 / 2 + [0.12, 0.05]), "r1", fontsize=9, color=INK, family="monospace")
    inset.set_xlim(-1.0, 1.0)
    inset.set_ylim(-0.95, 0.25)
    inset.set_aspect("equal", adjustable="datalim")
    inset.axis("off")
    ax.set_title("Written as a Z-matrix", loc="left", fontsize=10.5, pad=8)
    tag(ax, "SESSION 01")

    # 2. Session 02: energy against basis set
    ax = axes[1]
    names, e = basis_energies()
    x = np.arange(len(e))
    ax.plot(x, (np.array(e) - e[-1]), color=BLUE, marker="o", ms=5)
    ax.set_xticks(x, ["STO-3G", "3-21G", "4-31G", "6-31G*", "6-31G**"], fontsize=8)
    ax.set_ylabel(r"$E - E_{\mathrm{6\text{-}31G^{**}}}$ (hartree)", fontsize=9)
    ax.annotate("variational:\nonly downhill", xy=(1, e[1] - e[-1]), xytext=(1.6, 0.65),
                fontsize=8.5, color=INK, arrowprops={"arrowstyle": "-", "color": INK_2, "lw": 0.8})
    ax.set_title("Energy vs basis set", loc="left", fontsize=10.5, pad=8)
    tag(ax, "SESSION 02")

    # 3. Session 03 Ex. 1: optimised angle
    ax = axes[2]
    names, angles = optimised_angles()
    x = np.arange(len(angles))
    ax.axhline(104.5, color=INK_2, lw=1, ls=":")
    ax.annotate("experiment", xy=(0, 104.5), xytext=(0, 3), textcoords="offset points",
                fontsize=8, color=INK_2)
    ax.plot(x, angles, color=ORANGE, marker="s", ms=5)
    ax.set_xticks(x, ["STO-3G", "3-21G", "6-31G*", "6-31G**"], fontsize=8)
    ax.set_ylabel("optimised ∠HOH (°)", fontsize=9)
    ax.set_title("Optimised geometry", loc="left", fontsize=10.5, pad=8)
    tag(ax, "SESSION 03 · EX. 1")

    # 4. Session 03 Ex. 2: IR spectrum
    ax = axes[3]
    freq, inten = frequencies()
    nu = np.linspace(1300, 4400, 4000)
    hw = 14.0
    spec = sum(i * hw**2 / ((nu - c * 0.8953)**2 + hw**2) for c, i in zip(freq, inten))
    ax.fill_between(nu, spec / spec.max(), color=AQUA, alpha=0.18, lw=0)
    ax.plot(nu, spec / spec.max(), color=AQUA, lw=1.6)
    for k, e_ in enumerate([1595, 3657, 3756]):
        ax.axvline(e_, color=INK_2, lw=1, ls=":", label="experiment" if k == 0 else None)
    ax.set_xlim(4400, 1300)
    ax.set_ylim(0, 1.25)
    ax.set_yticks([])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(r"wavenumber (cm$^{-1}$)", fontsize=9)
    ax.legend(loc="upper left", fontsize=8)
    ax.text(0.97, 0.9, "HF/6-31G*, scaled", transform=ax.transAxes, ha="right",
            fontsize=8.5, color=INK)
    ax.set_title("Vibrations and IR spectrum", loc="left", fontsize=10.5, pad=8)
    tag(ax, "SESSION 03 · EX. 2")

    for ax in axes[1:]:
        ax.tick_params(labelsize=8)

    fig.suptitle(r"One molecule through the course: H$_2$O", x=0.125, ha="left",
                 y=1.13, fontsize=13)
    out = ROOT / "docs/banner.png"
    fig.savefig(out, bbox_inches="tight")
    print("Written", out)


if __name__ == "__main__":
    main()
