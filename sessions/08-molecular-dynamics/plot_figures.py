"""Builds every figure of Session 08 from the data files of the exercise folders.

Usage (from this folder):  python plot_figures.py
Requires numpy and matplotlib. Figures are written to figures/.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
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
    "axes.facecolor": SURFACE,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "legend.frameon": False,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})

SYSTEMS = (  # folder, label, degrees of freedom (from the NAMD log), colour
    ("ex1-water", "water", 9999, BLUE),
    ("ex2-sodium-in-water", "Na$^+$ in water", 10227, AQUA),
    ("ex3-ubiquitin", "ubiquitin", 21153, ORANGE),
)
EQUILIBRATION = 10.0  # ps left out of every average


def energies(folder):
    return np.loadtxt(HERE / folder / "energies.dat")


def save(fig, name):
    fig.savefig(OUT / name)
    plt.close(fig)
    print("Written", OUT / name)


def fig_temperature():
    """Temperature against time, its distribution, and the canonical prediction for its width."""
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(12, 3.4), gridspec_kw={"width_ratios": [1.5, 1, 1]})
    d = energies("ex1-water")
    t, T = d[:, 0], d[:, 3]
    prod = t > EQUILIBRATION
    a.plot(t, T, color=BLUE, lw=0.7)
    a.axvspan(0, EQUILIBRATION, color=GRID, alpha=0.7, lw=0)
    a.text(EQUILIBRATION / 2, 316, "equil.", ha="center", fontsize=8, color=INK_2)
    a.axhline(300, color=INK_2, lw=0.8, ls=(0, (4, 3)))
    a.set_xlim(0, 100)
    a.set_ylim(282, 320)
    a.set_xlabel("t (ps)")
    a.set_ylabel("T (K)")
    a.set_title("(a) water, Langevin at 300 K", fontsize=10, loc="left")

    mean = T[prod].mean()
    width = mean * np.sqrt(2 / 9999)
    b.hist(T[prod], bins=24, density=True, color=BLUE, alpha=0.35, edgecolor=BLUE, lw=0.6)
    x = np.linspace(282, 318, 200)
    b.plot(x, np.exp(-(x - mean) ** 2 / (2 * width ** 2)) / (width * np.sqrt(2 * np.pi)), color=INK, lw=1.4)
    b.text(0.04, 0.93, "line: canonical width\n" + r"$\langle T\rangle\sqrt{2/N}$, not a fit", transform=b.transAxes,
           fontsize=8, va="top", color=INK)
    b.set_xlabel("T (K)")
    b.set_ylabel("probability density (1/K)")
    b.set_title("(b) 900 samples after 10 ps", fontsize=10, loc="left")

    for i, (folder, label, ndof, colour) in enumerate(SYSTEMS):
        d = energies(folder)
        T = d[d[:, 0] > EQUILIBRATION, 3]
        blocks = [s.std() / s.mean() for s in np.array_split(T, 9)]
        err = np.std(blocks, ddof=1) / 3
        c.errorbar(i, T.std() / T.mean() * 100, yerr=err * 100, fmt="o", color=colour, ms=6, capsize=3)
        c.plot([i - 0.25, i + 0.25], [np.sqrt(2 / ndof) * 100] * 2, color=INK, lw=1.4)
    c.set_xticks(range(3), [s[1] for s in SYSTEMS], fontsize=9)
    c.set_xlim(-0.5, 2.5)
    c.set_ylim(0.8, 1.5)
    c.set_ylabel(r"$\sigma_T/\langle T\rangle$ (%)")
    c.text(0.97, 0.95, r"dots: measured" "\n" r"bars: $\sqrt{2/N}$", transform=c.transAxes, ha="right", va="top", fontsize=8)
    c.set_title("(c) measured against predicted", fontsize=10, loc="left")
    fig.tight_layout()
    save(fig, "temperature_fluctuations.png")


def fig_goo():
    r, g, n = np.loadtxt(HERE / "ex1-water/g_OO.dat", unpack=True)
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.axhline(1, color=INK_2, lw=0.8, ls=(0, (4, 3)))
    ax.plot(r, g, color=BLUE, lw=1.8, label="TIP3P, this run")
    ax.plot(2.80, 2.57, "D", color=ORANGE, ms=6, label="X-ray first maximum (Skinner 2013)")
    i = np.argmax(g)
    j = i + np.argmin(g[i:i + 40])
    ax.annotate(f"{r[i]:.2f} Å, g = {g[i]:.2f}", (r[i], g[i]), (3.4, 2.95), fontsize=8.5,
                arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.7))
    ax.annotate(f"minimum {r[j]:.2f} Å\n" + rf"$n$ = {n[j]:.2f} neighbours", (r[j], g[j]), (3.0, 0.25), fontsize=8.5,
                arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.7))
    tetra = 2.80 * np.sqrt(8 / 3)
    ax.axvline(tetra, color=AQUA, lw=1.0, ls=(0, (2, 2)))
    ax.text(tetra + 0.08, 1.65, f"tetrahedral\nsecond shell\n{tetra:.2f} Å", fontsize=8.5, color=AQUA, va="top")
    ax.set_xlim(2, 10)
    ax.set_ylim(0, 3.3)
    ax.set_xlabel("r (Å)")
    ax.set_ylabel(r"$g_\mathrm{OO}(r)$")
    ax.legend(fontsize=8.5, loc="upper right")
    fig.tight_layout()
    save(fig, "g_OO.png")


def fig_sodium():
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 3.8))
    for name, colour, label in (("NaO", BLUE, "Na–O"), ("NaH", ORANGE, "Na–H")):
        r, g, n = np.loadtxt(HERE / f"ex2-sodium-in-water/g_{name}.dat", unpack=True)
        a.plot(r, g, color=colour, lw=1.6, label=label)
        b.plot(r, n, color=colour, lw=1.6, label=label)
        i = np.argmax(g)
        a.annotate(f"{r[i]:.2f} Å", (r[i], g[i]), (r[i] + 0.3, g[i] + 0.15), fontsize=8.5, color=colour)
        if name == "NaO":
            j = i + np.argmin(g[i:i + 30])
            b.axvline(r[j], color=INK_2, lw=0.8, ls=(0, (4, 3)))
            b.annotate(f"{n[j]:.1f} O within {r[j]:.1f} Å", (r[j], n[j]), (r[j] + 0.3, n[j] - 3), fontsize=8.5,
                       arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.7))
    a.plot(2.384, 7.2, "D", color=INK, ms=5)
    a.text(2.5, 6.9, "X-ray Na–O, 2.384 Å\n(Galib 2017)", fontsize=8, va="top")
    a.set_xlim(1.5, 8)
    a.set_ylim(0, 8.5)
    a.set_xlabel("r (Å)")
    a.set_ylabel("g(r) around Na$^+$")
    a.legend(fontsize=9, loc="upper right")
    b.set_xlim(1.5, 5)
    b.set_ylim(0, 25)
    b.set_xlabel("r (Å)")
    b.set_ylabel("n(r), atoms within r")
    b.legend(fontsize=9, loc="upper left")
    fig.tight_layout()
    save(fig, "g_sodium.png")


def fig_diffusion():
    t, m = np.loadtxt(HERE / "ex1-water/msd_O.dat", unpack=True)
    window = (t >= 5) & (t <= 40)
    slope, icpt = np.polyfit(t[window], m[window], 1)
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(t, m, color=BLUE, lw=1.8, label=rf"this run: $D$ = {slope / 6 * 10:.2f}")
    x = np.linspace(0, 40, 50)
    for D, colour, label in ((2.30, INK, "experiment: 2.30"), (5.06, ORANGE, "TIP3P without friction: 5.06")):
        ax.plot(x, 6 * D / 10 * x, color=colour, lw=1.1, ls=(0, (4, 3)), label=label)
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 160)
    ax.set_xlabel("t (ps)")
    ax.set_ylabel(r"$\langle |\mathbf{r}(t)-\mathbf{r}(0)|^2\rangle$ (Å$^2$)")
    ax.legend(title=r"$D$ in $10^{-5}$ cm$^2$/s", fontsize=8.5, title_fontsize=8.5, loc="upper left")
    fig.tight_layout()
    save(fig, "diffusion.png")


def fig_ubiquitin():
    t, bb, hv = np.loadtxt(HERE / "ex3-ubiquitin/rmsd_time.dat", unpack=True)
    res, per = np.loadtxt(HERE / "ex3-ubiquitin/rmsd_residue.dat", unpack=True)
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw={"width_ratios": [1, 1.3]})
    a.plot(t, hv, color=ORANGE, lw=1.0, label="heavy atoms")
    a.plot(t, bb, color=BLUE, lw=1.0, label="backbone")
    a.set_xlim(0, 100)
    a.set_ylim(0, 1.4)
    a.set_xlabel("t (ps)")
    a.set_ylabel("RMSD from the first frame (Å)")
    a.legend(fontsize=9, loc="lower right")
    colours = [ORANGE if r >= 72 else BLUE for r in res]
    b.bar(res, per, color=colours, width=0.8)
    b.axhline(per.mean(), color=INK_2, lw=0.8, ls=(0, (4, 3)))
    b.text(2, 2.2, f"dashed: mean, {per.mean():.2f} Å", fontsize=8.5, color=INK_2, va="top")
    b.text(71.5, 2.3, "C-terminal\ntail", fontsize=8.5, color=ORANGE, ha="right", va="top")
    b.set_xlim(0, 77)
    b.set_ylim(0, 2.4)
    b.set_xlabel("residue")
    b.set_ylabel("average RMSD, heavy atoms (Å)")
    fig.tight_layout()
    save(fig, "ubiquitin_rmsd.png")


if __name__ == "__main__":
    fig_temperature()
    fig_goo()
    fig_sodium()
    fig_diffusion()
    fig_ubiquitin()
