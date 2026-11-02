"""Builds every figure of Session 04 from the processed data files.

Usage (from this folder):  python plot_figures.py
Requires matplotlib. Figures are written to figures/.
"""
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

BLUE, ORANGE = "#2a78d6", "#eb6834"
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


if __name__ == "__main__":
    fig_profile()
