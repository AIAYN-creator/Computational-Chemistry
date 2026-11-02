"""Builds every figure of Session 04 from the processed data files.

Usage (from this folder):  python plot_figures.py
Requires numpy and matplotlib. Figures are written to figures/.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse

HERE = Path(__file__).parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SURFACE = "#fcfcfb"
HARTREE_TO_KCAL = 627.5095

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
    "ytick.direction": "in",
    "legend.frameon": False,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "savefig.dpi": 200,
})


def read_results(path):
    """{species: {column: value}} from a results.txt with a header row."""
    lines = (HERE / path).read_text().splitlines()
    names = lines[0].split()[1:]
    return {l.split()[0]: dict(zip(names, l.split()[1:])) for l in lines[1:]}


def profile():
    """Energy of each stationary point relative to the reactants (kcal/mol)."""
    ions = read_results("ex1-reactants-and-products/results.txt")
    complexes = read_results("ex2-ion-dipole-complexes/results.txt")
    out = {}
    for column in ("E", "G"):
        v = lambda table, key: float(table[key][column])
        reactants = v(ions, "f_anion") + v(ions, "ch3cl")
        products = v(ions, "cl_anion") + v(ions, "ch3f")
        out[column] = [(x - reactants) * HARTREE_TO_KCAL for x in (
            reactants, v(complexes, "f_ch3cl"), v(complexes, "ch3f_cl"), products)]
    return out


# --- Figure 1: the energy profile so far (ex1 + ex2) -------------------------
def fig_profile():
    levels = profile()
    x = [0, 1, 3, 4]
    names = [r"F$^-$ + CH$_3$Cl", r"F$^-\cdots$CH$_3$Cl", r"FCH$_3\cdots$Cl$^-$", r"CH$_3$F + Cl$^-$"]
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    # G lies above E at the complexes: its label goes above, the one of E below
    for column, colour, label, shift in (("E", BLUE, "ΔE", -2.6), ("G", ORANGE, "ΔG (298 K)", 2.6)):
        y = levels[column]
        for k, (xi, yi) in enumerate(zip(x, y)):
            ax.plot([xi - 0.3, xi + 0.3], [yi, yi], color=colour, lw=3, solid_capstyle="butt",
                    label=label if k == 0 else None, zorder=3)
            if k == 0 and column == "E":   # both are 0 at the reactants: one label
                continue
            text = "0" if k == 0 else f"{yi:.1f}".replace("-", "−")
            ax.text(xi, yi + shift, text, ha="center", va="center",
                    fontsize=9, color=INK_2 if k == 0 else colour)
        ax.plot([x[0] + 0.3, x[1] - 0.3], y[:2], color=colour, lw=0.9, ls=":", zorder=2)
        ax.plot([x[2] + 0.3, x[3] - 0.3], y[2:], color=colour, lw=0.9, ls=":", zorder=2)
    ax.text(2, -22, "transition state:\nnext exercises", ha="center", va="center",
            fontsize=9, color=INK_2, style="italic")
    ax.set_xticks(x, names)
    ax.set_xlim(-0.6, 4.6)
    ax.set_ylim(-60, 10)
    ax.set_ylabel("energy relative to reactants (kcal/mol)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title(r"F$^-$ + CH$_3$Cl $\to$ CH$_3$F + Cl$^-$, HF/6-31+G*: the profile so far",
                 loc="left", fontsize=11.5)
    fig.savefig(OUT / "energy_profile.png", bbox_inches="tight")
    plt.close(fig)
    print("Written", OUT / "energy_profile.png")
    for column, y in levels.items():
        print(column, [round(v, 2) for v in y])


# --- Figure 2: the n -> sigma*(C-X) donation, a scheme (ex2) -------------------
def level(ax, x, y, width=0.7, electrons=0, **style):
    """One orbital: a horizontal line, with up to two electrons as arrows."""
    style = {"color": INK, "lw": 2.2, **style}
    ax.plot([x - width / 2, x + width / 2], [y, y], solid_capstyle="butt", **style)
    offsets = {1: [0], 2: [-0.07, 0.07]}.get(electrons, [])
    for k, dx in enumerate(offsets):
        tail, head = (y - 0.26, y + 0.26) if k == 0 else (y + 0.26, y - 0.26)
        ax.annotate("", xy=(x + dx, head), xytext=(x + dx, tail),
                    arrowprops={"arrowstyle": "-|>", "color": INK, "lw": 1, "mutation_scale": 8,
                                "shrinkA": 0, "shrinkB": 0})


def fig_orbitals():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.5),
                                   gridspec_kw={"width_ratios": [1, 1.15], "wspace": 0.05,
                                                "left": 0.02, "right": 0.99})
    # (a) Levels: C and Cl make sigma and sigma*, and F- donates into sigma*
    c, cl, sigma, star, star_f = (0, 0), (2.4, -0.9), (1.2, -2), (1.2, 1.3), (1.2, 2.5)
    n_f = (4.0, 0.1)
    for start in (c, cl):
        for end in (sigma, star):
            sx = 0.35 if start is c else -0.35
            ex = -0.35 if start is c else 0.35
            ax1.plot([start[0] + sx, end[0] + ex], [start[1], end[1]], color=INK_2, lw=0.8, ls=":")
    level(ax1, *c, electrons=1)
    level(ax1, *cl, electrons=1)
    level(ax1, *sigma, electrons=2, color=BLUE)
    level(ax1, *star, color=ORANGE)
    level(ax1, *star_f, color=INK_2, ls=(0, (3, 2)), lw=1.6)
    level(ax1, *n_f, electrons=2, color=AQUA)
    ax1.annotate("", xy=(star[0] + 0.4, star[1]), xytext=(n_f[0] - 0.4, n_f[1] + 0.05),
                 arrowprops={"arrowstyle": "-|>", "color": AQUA, "lw": 2, "mutation_scale": 14,
                             "connectionstyle": "arc3,rad=0.2"})
    for x, y, text, colour, ha in (
            (-0.45, 0, "C", INK, "right"), (2.85, -0.9, "Cl", INK, "left"),
            (1.65, -2, "σ(C–Cl), bonding: full", BLUE, "left"),
            (0.75, 1.3, "σ*(C–Cl)\nantibonding: empty", ORANGE, "right"),
            (0.75, 2.5, "σ*(C–F): higher,\na worse acceptor", INK_2, "right")):
        ax1.text(x, y, text, ha=ha, va="center", fontsize=9, color=colour)
    ax1.text(4.0, -0.45, "n(F$^-$)\nlone pair", ha="center", va="top", fontsize=9, color=AQUA)
    ax1.text(3.05, 1.5, "partial donation:\nthe bond order drops", ha="center", va="bottom",
             fontsize=9, color=INK)
    ax1.annotate("", xy=(-1.95, 3.0), xytext=(-1.95, -2.5),
                 arrowprops={"arrowstyle": "-|>", "color": INK_2, "lw": 1, "shrinkA": 0, "shrinkB": 0})
    ax1.text(-2.08, 0.25, "energy", rotation=90, ha="right", va="center", fontsize=9, color=INK_2)
    ax1.set_xlim(-2.4, 4.9)
    ax1.set_ylim(-2.8, 3.2)
    ax1.axis("off")
    ax1.set_title("(a) The energy levels", loc="left", fontsize=10.5)

    # (b) Shape: the large lobe of sigma* sits behind C, facing the incoming ion
    lobes = [(-0.85, 1.7, 1.15, BLUE), (0.33, 0.66, 0.55, ORANGE),
             (1.6, 0.7, 0.6, BLUE), (2.6, 0.9, 0.8, ORANGE)]
    for x, width, height, colour in lobes:
        ax2.add_patch(Ellipse((x, 0), width, height, fc=colour, ec=colour, alpha=0.45, lw=1, zorder=1))
    ax2.add_patch(Ellipse((-2.25, 0), 1.5, 0.72, fc=AQUA, ec=AQUA, alpha=0.55, lw=1, zorder=1))
    ax2.plot([0.9, 0.9], [-0.75, 0.75], color=INK_2, lw=1, ls=(0, (3, 2)), zorder=2)
    # The H atoms lean away from Cl, at the H-C-Cl angle of the molecule
    for sign in (1, -1):
        hx, hy = 1.0 * np.cos(np.radians(108)), sign * 1.0 * np.sin(np.radians(108))
        ax2.plot([0, hx], [0, hy], color=INK_2, lw=1.4, zorder=2)
        ax2.text(hx * 1.2, hy * 1.2, "H", ha="center", va="center", fontsize=9, color=INK_2)
    ax2.plot([0, 2.1], [0, 0], color=INK_2, lw=1.4, zorder=2)
    for x, name in ((-3.15, "F$^-$"), (0, "C"), (2.1, "Cl")):
        ax2.add_patch(plt.Circle((x, 0), 0.2, fc=SURFACE, ec=INK, lw=1.2, zorder=3))
        ax2.text(x, 0, name, ha="center", va="center", fontsize=8.5, color=INK, zorder=4)
    ax2.text(-2.25, -0.62, "n(F$^-$)", ha="center", va="top", fontsize=9, color=AQUA)
    ax2.annotate("large lobe of σ*, behind C:\nthe ion arrives right here", xy=(-1.1, 0.5),
                 xytext=(-1.75, 1.6), ha="center", va="center", fontsize=9, color=INK,
                 arrowprops={"arrowstyle": "-", "color": INK_2, "lw": 0.8})
    ax2.annotate("node between C and Cl:\nelectrons here weaken the bond", xy=(0.9, 0.75),
                 xytext=(1.9, 1.6), ha="center", va="center", fontsize=9, color=INK,
                 arrowprops={"arrowstyle": "-", "color": INK_2, "lw": 0.8})
    ax2.text(0, -1.75, "blue and orange: the two signs of the orbital", ha="center", va="center",
             fontsize=8.5, color=INK_2)
    ax2.set_xlim(-3.7, 3.4)
    ax2.set_ylim(-2.1, 2.1)
    ax2.set_aspect("equal")
    ax2.set_anchor("N")   # top edge level with panel (a), so the titles line up
    ax2.axis("off")
    ax2.set_title("(b) The shape of σ*(C–Cl), along the attack axis", loc="left", fontsize=10.5)
    fig.suptitle(r"Why the ion weakens the bond: n(F$^-$) $\to$ σ*(C–Cl). A scheme, not to scale",
                 x=0.01, ha="left", y=1.02, fontsize=11.5)
    fig.savefig(OUT / "orbital_scheme.png", bbox_inches="tight")
    plt.close(fig)
    print("Written", OUT / "orbital_scheme.png")


if __name__ == "__main__":
    fig_profile()
    fig_orbitals()
