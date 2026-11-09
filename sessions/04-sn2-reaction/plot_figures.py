"""Builds every figure of Session 04 from the processed data files.

Usage (from this folder):  python plot_figures.py
Requires numpy, scipy and matplotlib. Figures are written to figures/.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse
from scipy.interpolate import RectBivariateSpline
from scipy.optimize import root

HERE = Path(__file__).parent
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
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


def reactants(column="E"):
    """E or G of F- + CH3Cl, the zero of every energy in this session (hartree)."""
    ions = read_results("ex1-reactants-and-products/results.txt")
    return float(ions["f_anion"][column]) + float(ions["ch3cl"][column])


def profile():
    """Energy of each stationary point relative to the reactants (kcal/mol)."""
    ions = read_results("ex1-reactants-and-products/results.txt")
    complexes = read_results("ex2-ion-dipole-complexes/results.txt")
    ts = read_results("ex4-transition-state/results.txt")
    out = {}
    for column in ("E", "G"):
        v = lambda table, key: float(table[key][column])
        products = v(ions, "cl_anion") + v(ions, "ch3f")
        out[column] = [(x - reactants(column)) * HARTREE_TO_KCAL for x in (
            reactants(column), v(complexes, "f_ch3cl"), v(ts, "ts_sn2"), v(complexes, "ch3f_cl"),
            products)]
    return out


# --- Figure 1: the double-well profile (ex1 + ex2 + ex4) -----------------------
def fig_profile():
    levels = profile()
    x = [0, 1, 2, 3, 4]
    names = [r"F$^-$ + CH$_3$Cl", r"F$^-\cdots$CH$_3$Cl", "transition\nstate",
             r"FCH$_3\cdots$Cl$^-$", r"CH$_3$F + Cl$^-$"]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.axhline(0, color=INK_2, lw=0.8, ls=(0, (4, 3)), zorder=1)
    ax.text(4.55, 1.4, "separated reactants", ha="right", va="bottom", fontsize=8.5, color=INK_2)
    # G lies above E everywhere: its label goes above, the one of E below
    for column, colour, label, shift in (("E", BLUE, "ΔE", -2.7), ("G", ORANGE, "ΔG (298 K)", 2.7)):
        y = levels[column]
        for k, (xi, yi) in enumerate(zip(x, y)):
            ax.plot([xi - 0.28, xi + 0.28], [yi, yi], color=colour, lw=3, solid_capstyle="butt",
                    label=label if k == 0 else None, zorder=3)
            if k == 0:   # both are 0 at the reactants: no label needed
                continue
            ax.text(xi, yi + shift, f"{yi:.1f}".replace("-", "−"), ha="center", va="center",
                    fontsize=9, color=colour)
        for k in range(4):
            ax.plot([x[k] + 0.28, x[k + 1] - 0.28], y[k:k + 2], color=colour, lw=0.9, ls=":", zorder=2)
    e = levels["E"]
    # The two wells, and the barrier between them
    ax.annotate("", xy=(2.42, e[2]), xytext=(2.42, e[1]),
                arrowprops={"arrowstyle": "<->", "color": INK, "lw": 0.9, "shrinkA": 0, "shrinkB": 0})
    ax.text(2.5, (e[1] + e[2]) / 2 - 1, f"barrier from the complex: {e[2] - e[1]:.1f}",
            ha="left", va="center", fontsize=9, color=INK)
    ax.annotate("", xy=(1.62, e[2]), xytext=(1.62, 0),
                arrowprops={"arrowstyle": "<->", "color": INK, "lw": 0.9, "shrinkA": 0, "shrinkB": 0})
    ax.text(1.56, -3, f"{-e[2]:.1f}", ha="right", va="center", fontsize=9, color=INK)
    ax.text(2.55, -27, f"the transition state lies {-e[2]:.1f} kcal/mol\nbelow the separated reactants:\n"
            "no net barrier from them", ha="left", va="center", fontsize=9, color=INK)
    for xi, text in ((1, "well 1"), (3, "well 2")):
        ax.text(xi, e[xi] - 7, text, ha="center", va="center", fontsize=9, color=INK_2, style="italic")
    ax.set_xticks(x, names)
    ax.set_xlim(-0.6, 4.6)
    ax.set_ylim(-63, 10)
    ax.set_ylabel("energy relative to reactants (kcal/mol)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title(r"F$^-$ + CH$_3$Cl $\to$ CH$_3$F + Cl$^-$, HF/6-31+G*: the double-well profile",
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


# --- Figure 3: HCN to CNH, levels and geometries to scale (ex8) ------------------
def molecule(ax, atoms, bonds, title):
    """Atoms {name: (x, y)} and bonds [(a, b, label, dx, dy, dashed)], in angstrom."""
    for a, b, label, dx, dy, dashed in bonds:
        (x1, y1), (x2, y2) = atoms[a], atoms[b]
        ax.plot([x1, x2], [y1, y2], color=INK_2, lw=1.4, zorder=1, ls=(0, (3, 2)) if dashed else "-")
        ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, label, ha="center", va="center",
                fontsize=8.5, color=INK_2)
    for name, (x, y) in atoms.items():
        ax.add_patch(plt.Circle((x, y), 0.17, fc=SURFACE, ec=INK, lw=1.2, zorder=2))
        ax.text(x, y, name, ha="center", va="center", fontsize=8.5, color=INK, zorder=3)
    ax.text(0.5, 0.02, title, transform=ax.transAxes, ha="center", va="bottom", fontsize=9.5, color=INK)
    xs = [x for x, _ in atoms.values()]
    centre = (min(xs) + max(xs)) / 2   # each molecule right below its level
    ax.set_xlim(centre - 2.15, centre + 2.15)
    ax.set_ylim(-0.95, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")


def fig_isomerization():
    table = read_results("ex8-hcn-isomerization/results.txt")
    keys = ("hcn", "ts_hcn", "cnh")
    fig = plt.figure(figsize=(8.6, 6.0))
    grid = fig.add_gridspec(2, 3, height_ratios=[1.5, 1], hspace=0.02, wspace=0)
    ax = fig.add_subplot(grid[0, :])
    # E lies above G at the TS and at CNH: its label goes above, the one of G below
    for column, colour, label, shift in (("E", BLUE, "ΔE", 3.4), ("G", ORANGE, "ΔG (298 K)", -3.4)):
        y = [(float(table[k][column]) - float(table["hcn"][column])) * HARTREE_TO_KCAL for k in keys]
        for k, yi in enumerate(y):
            ax.plot([k - 0.26, k + 0.26], [yi, yi], color=colour, lw=3, solid_capstyle="butt",
                    label=label if k == 0 else None, zorder=3)
            if k == 0:   # both are 0 at HCN: one label
                if column == "E":
                    ax.text(k, yi + shift, "0", ha="center", va="center", fontsize=9, color=INK_2)
                continue
            ax.text(k, yi + shift, f"{yi:.1f}", ha="center", va="center", fontsize=9, color=colour)
        ax.plot([0.26, 0.74], y[:2], color=colour, lw=0.9, ls=":", zorder=2)
        ax.plot([1.26, 1.74], y[1:], color=colour, lw=0.9, ls=":", zorder=2)
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-6, 62)
    ax.set_xticks([])
    ax.set_ylabel("energy relative to HCN (kcal/mol)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title(r"H–C≡N $\to$ C≡N–H, HF/6-31G*: energy levels, and geometries to scale", loc="left", fontsize=11.5)

    # C at the origin and N along +x, the same frame for all three
    rcn = {k: float(table[k]["r_CN"]) for k in keys}
    rch, rnh = float(table["hcn"]["r_CH"]), float(table["cnh"]["r_NH"])
    molecule(fig.add_subplot(grid[1, 0]), {"H": (-rch, 0), "C": (0, 0), "N": (rcn["hcn"], 0)},
             [("H", "C", f"{rch:.3f}", 0, 0.32, False), ("C", "N", f"{rcn['hcn']:.3f}", 0, 0.32, False)],
             "HCN: minimum")

    # The TS is printed with C-N along y: rotate it into the same frame
    rows = [l.split() for l in (HERE / "ex8-hcn-isomerization/transition_vector.txt").read_text().splitlines()[1:]]
    c, h, n = (np.array(r[1:3], float) for r in rows)
    move = np.array(rows[1][3:5], float)
    u = (n - c) / np.linalg.norm(n - c)
    v = (h - c) - (h - c) @ u * u
    v /= np.linalg.norm(v)
    frame = lambda p: (p @ u, p @ v)
    hx, hy = frame(h - c)
    ts = fig.add_subplot(grid[1, 1])
    molecule(ts, {"C": (0, 0), "N": (rcn["ts_hcn"], 0), "H": (hx, hy)},
             [("C", "N", f"{rcn['ts_hcn']:.3f}", 0, -0.27, False),
              ("C", "H", f"{float(table['ts_hcn']['r_CH']):.3f}", -0.42, 0, False),
              ("H", "N", f"{np.linalg.norm(h - n):.3f}", 0.5, 0.08, True)],
             "transition state: 1227i cm$^{-1}$")
    dx, dy = frame(move)
    ts.annotate("", xy=(hx + 0.75 * dx, hy + 0.75 * dy), xytext=(hx + 0.17, hy),
                arrowprops={"arrowstyle": "-|>", "color": AQUA, "lw": 2, "mutation_scale": 13,
                            "shrinkA": 0, "shrinkB": 0})

    molecule(fig.add_subplot(grid[1, 2]), {"C": (0, 0), "N": (rcn["cnh"], 0), "H": (rcn["cnh"] + rnh, 0)},
             [("C", "N", f"{rcn['cnh']:.3f}", 0, 0.32, False), ("N", "H", f"{rnh:.3f}", 0, 0.32, False)],
             "CNH: minimum")
    fig.savefig(OUT / "hcn_isomerization.png", bbox_inches="tight")
    plt.close(fig)
    print("Written", OUT / "hcn_isomerization.png")


# --- Figure 4: the potential energy surface and its minimum energy path (ex3) ---
def surface(path="ex3-potential-energy-surface/scan_raw.txt", zero=None):
    """The 9 x 11 scan as a grid in kcal/mol above F- + CH3Cl, and a bicubic spline of it."""
    zero = reactants() if zero is None else zero
    rows = np.loadtxt(HERE / path)
    ccl, cf = np.unique(rows[:, 0]), np.unique(rows[:, 1])
    grid = np.empty((len(ccl), len(cf)))
    for a, b, e in rows:
        grid[np.searchsorted(ccl, a), np.searchsorted(cf, b)] = (e - zero) * HARTREE_TO_KCAL
    return ccl, cf, grid, RectBivariateSpline(ccl, cf, grid)


def minimum_energy_path(spline, guess):
    """Saddle point of the spline near guess, and the path down both sides, short C-Cl first."""
    grad = lambda p: [spline(*p, dx=1)[0, 0], spline(*p, dy=1)[0, 0]]
    saddle = root(grad, guess).x
    hess = np.array([[spline(*saddle, dx=2)[0, 0], spline(*saddle, dx=1, dy=1)[0, 0]],
                     [spline(*saddle, dx=1, dy=1)[0, 0], spline(*saddle, dy=2)[0, 0]]])
    values, vectors = np.linalg.eigh(hess)
    down = vectors[:, np.argmin(values)]   # the direction of negative curvature
    side_a, side_b = (steepest_descent(spline, saddle, s * down) for s in (1, -1))
    if side_a[-1, 0] > side_b[-1, 0]:
        side_a, side_b = side_b, side_a
    return saddle, np.vstack([side_a[::-1], side_b[1:]])


def steepest_descent(spline, start, direction, step=0.002, limits=((1.6, 3.6), (1.3, 2.9))):
    """Walk downhill from the saddle point until the energy stops falling."""
    energy = lambda p: spline(*p)[0, 0]
    path = [start]
    p = start + step * direction
    while True:
        g = np.array([spline(*p, dx=1)[0, 0], spline(*p, dy=1)[0, 0]])
        nxt = p - step * g / np.linalg.norm(g)
        inside = all(lo <= v <= hi for v, (lo, hi) in zip(nxt, limits))
        if not inside or energy(nxt) >= energy(p):
            return np.array(path + [p])
        path.append(p)
        p = nxt


def fig_pes():
    ccl, cf, grid, spline = surface()
    ts = read_results("ex4-transition-state/results.txt")["ts_sn2"]
    complexes = read_results("ex2-ion-dipole-complexes/results.txt")
    opt = {k: ((float(v["E"]) - reactants()) * HARTREE_TO_KCAL, float(v["r_CCl"]), float(v["r_CF"]))
           for k, v in complexes.items()}
    opt["ts"] = ((float(ts["E"]) - reactants()) * HARTREE_TO_KCAL, float(ts["r_CCl"]), float(ts["r_CF"]))

    # The saddle point of the spline, close to the optimised one, and the path
    # from the reactant valley (short C-Cl) to the product valley
    saddle, path = minimum_energy_path(spline, [opt["ts"][1], opt["ts"][2]])
    along = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    energy = spline(path[:, 0], path[:, 1], grid=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.0),
                                   gridspec_kw={"width_ratios": [1.12, 1], "wspace": 0.42})
    # (a) The map
    fx, fy = np.linspace(1.6, 3.6, 300), np.linspace(1.3, 2.9, 300)
    fine = spline(fx, fy).T
    levels = np.arange(-55, 41, 5)
    filled = ax1.contourf(fx, fy, fine, levels=levels, cmap="magma", extend="max")
    ax1.contour(fx, fy, fine, levels=levels, colors="white", linewidths=0.45, alpha=0.35)
    gx, gy = np.meshgrid(ccl, cf)
    ax1.plot(gx.ravel(), gy.ravel(), ".", color="white", ms=2.2, alpha=0.55)
    ax1.plot(path[:, 0], path[:, 1], color=AQUA, lw=2.6, solid_capstyle="round")
    for key in ("f_ch3cl", "ch3f_cl"):
        ax1.plot(opt[key][1], opt[key][2], "o", ms=8, mfc="white", mec=INK, mew=1.2, zorder=5)
    ax1.plot(opt["ts"][1], opt["ts"][2], "*", ms=17, mfc=YELLOW, mec=INK, mew=1, zorder=5)
    for x, y, text, ha, colour in (
            (1.98, 2.66, r"F$^-\cdots$CH$_3$Cl" + "\nreactant complex", "left", "white"),
            (3.25, 1.56, r"FCH$_3\cdots$Cl$^-$" + "\nproduct complex", "center", "white"),
            (2.24, 2.2, "transition state\n(2.133, 2.125)", "left", "white"),
            (1.64, 1.42, "highest region:\nF and Cl crowd C,\nnever visited", "left", INK)):
        ax1.text(x, y, text, ha=ha, va="center", fontsize=8.5, color=colour)
    ax1.set_xlabel("d(C–Cl) (Å)")
    ax1.set_ylabel("d(C–F) (Å)")
    ax1.set_aspect("equal")
    ax1.grid(False)
    bar = fig.colorbar(filled, ax=ax1, fraction=0.045, pad=0.03)
    bar.set_label("kcal/mol, relative to F$^-$ + CH$_3$Cl")
    ax1.set_anchor("N")   # top edge level with panel (b), so the titles line up
    ax1.set_title("(a) The surface: 99 points, interpolated", loc="left", fontsize=10.5)

    # (b) The same path, stretched out
    ax2.axhline(0, color=INK_2, lw=0.8, ls=(0, (4, 3)))
    ax2.text(along[-1], 1.2, "separated reactants", ha="right", va="bottom", fontsize=8.5, color=INK_2)
    ax2.plot(along, energy, color=AQUA, lw=2.4, label="along the path of the scan")
    nearest = lambda key: along[np.argmin(np.hypot(path[:, 0] - opt[key][1], path[:, 1] - opt[key][2]))]
    for key, marker, size, colour in (("f_ch3cl", "o", 8, "white"), ("ts", "*", 16, YELLOW),
                                      ("ch3f_cl", "o", 8, "white")):
        ax2.plot(nearest(key), opt[key][0], marker, ms=size, mfc=colour, mec=INK, mew=1.1, zorder=5,
                 label="optimised (Ex. 2 and 4)" if key == "ts" else None)
        last = key == "ch3f_cl"   # at the right edge: label on its left
        ax2.text(nearest(key) + (-0.06 if last else 0.06), opt[key][0] + (2.4 if key == "ts" else -2.6),
                 f"{opt[key][0]:.1f}".replace("-", "−"), ha="right" if last else "left",
                 va="center", fontsize=9, color=INK)
    ax2.set_xlabel("distance along the path (Å)")
    ax2.set_ylabel("energy relative to F$^-$ + CH$_3$Cl (kcal/mol)")
    ax2.set_ylim(-60, 8)
    ax2.legend(loc="lower left", fontsize=9)
    ax2.set_title("(b) The minimum energy path, stretched out", loc="left", fontsize=10.5)
    fig.suptitle(r"F$^-$ + CH$_3$Cl, HF/6-31+G*: relaxed scan of d(C–Cl) and d(C–F)",
                 x=0.07, ha="left", y=0.99, fontsize=11.5)
    fig.savefig(OUT / "potential_energy_surface.png", bbox_inches="tight")
    plt.close(fig)
    print("Written", OUT / "potential_energy_surface.png")
    print("saddle of the spline", saddle.round(3), "E", round(spline(*saddle)[0, 0], 2))
    print("path ends", path[0].round(3), round(energy[0], 2), path[-1].round(3), round(energy[-1], 2))


# --- Figure 5: the transition vector of the SN2 (ex4) ----------------------------
def fig_sn2_vector():
    rows = np.loadtxt(HERE / "ex4-transition-state/transition_vector.txt", skiprows=1)
    z, xyz, move = rows[:, 0].astype(int), rows[:, 1:4], rows[:, 4:7]
    c, f = xyz[z == 6][0], xyz[z == 9][0]
    hydrogens = np.where(z == 1)[0]
    # The F-C-Cl axis across, and the first H up: the plane of the drawing
    u = (f - c) / np.linalg.norm(f - c)
    v = (xyz[hydrogens[0]] - c) - (xyz[hydrogens[0]] - c) @ u * u
    v /= np.linalg.norm(v)
    flat = lambda p: np.array([p @ u, p @ v])
    pos = {k: flat(xyz[k] - c) for k in range(len(z))}
    names = {6: "C", 9: "F", 17: "Cl", 1: "H"}
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    for k in hydrogens:
        behind = k != hydrogens[0]   # the other two H are out of the plane
        ax.plot(*zip(pos[np.where(z == 6)[0][0]], pos[k]), color=INK_2, lw=1.3, alpha=0.5 if behind else 1)
    for name, ls in ((9, (0, (3, 2))), (17, (0, (3, 2)))):
        k = np.where(z == name)[0][0]
        ax.plot(*zip(pos[np.where(z == 6)[0][0]], pos[k]), color=INK_2, lw=1.3, ls=ls)
    scale = 1.0   # displacements have no unit: 1 is drawn as 1 Å
    for k in range(len(z)):
        behind = z[k] == 1 and k != hydrogens[0]
        radius = 0.24 if z[k] != 1 else 0.17
        ax.add_patch(plt.Circle(pos[k], radius, fc=SURFACE, ec=INK, lw=1.2, zorder=3, alpha=0.6 if behind else 1))
        ax.text(*pos[k], names[z[k]], ha="center", va="center", fontsize=8.5, color=INK, zorder=4,
                alpha=0.6 if behind else 1)
        d = flat(move[k]) * scale
        if np.linalg.norm(d) > 0.05:
            # The short arrows of the H atoms start at the edge of the circle, so they stay visible
            edge = pos[k] + (radius * d / np.linalg.norm(d) if z[k] == 1 else 0)
            ax.annotate("", xy=edge + d, xytext=edge, zorder=5,
                        arrowprops={"arrowstyle": "-|>", "color": AQUA, "lw": 2, "mutation_scale": 12,
                                    "shrinkA": 0, "shrinkB": 0})
    ts = read_results("ex4-transition-state/results.txt")["ts_sn2"]
    ax.text(pos[np.where(z == 9)[0][0]][0] / 2, -0.32, f"{float(ts['r_CF']):.3f} Å", ha="center",
            fontsize=8.5, color=INK_2)
    ax.text(pos[np.where(z == 17)[0][0]][0] / 2, -0.32, f"{float(ts['r_CCl']):.3f} Å", ha="center",
            fontsize=8.5, color=INK_2)
    ax.text(0.05, -1.3, "The carbon moves most, towards F and away from Cl, through the plane of the H atoms.\n"
            "The two pale H atoms lie out of the plane, one behind the other.", ha="center", va="center", fontsize=8.5, color=INK_2)
    ax.set_xlim(-2.75, 2.75)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("The SN2 transition state and its imaginary mode, 442i cm$^{-1}$ (arrows: the transition vector)",
                 loc="left", fontsize=10.5)
    fig.savefig(OUT / "sn2_transition_vector.png", bbox_inches="tight")
    plt.close(fig)
    print("Written", OUT / "sn2_transition_vector.png")


# --- Figure 6: gas phase against water, PCM (extra) ------------------------------
def fig_water():
    water = read_results("extra-water-pcm/results.txt")
    w = lambda key, column: float(water[key][column])
    zero_w = {c: w("f_anion", c) + w("ch3cl", c) for c in ("E", "G")}
    gas_ts = read_results("ex4-transition-state/results.txt")["ts_sn2"]
    maps = (("(a) Gas phase", "ex3-potential-energy-surface/scan_raw.txt", None,
             (float(gas_ts["r_CCl"]), float(gas_ts["r_CF"]))),
            ("(b) Water (PCM)", "extra-water-pcm/sep_pcm_raw.txt", zero_w["E"], (2.2306, 2.0714)))
    stopped = np.loadtxt(HERE / "extra-water-pcm/scan_stopped.txt")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), gridspec_kw={"width_ratios": [1, 1, 1.05], "wspace": 0.32})
    levels = np.arange(-55, 41, 5)   # the same scale for both maps
    fx, fy = np.linspace(1.6, 3.6, 300), np.linspace(1.3, 2.9, 300)
    for ax, (title, path, zero, ts) in zip(axes[:2], maps):
        ccl, cf, grid, spline = surface(path, zero)
        filled = ax.contourf(fx, fy, spline(fx, fy).T, levels=levels, cmap="magma", extend="both")
        ax.contour(fx, fy, spline(fx, fy).T, levels=levels, colors="white", linewidths=0.45, alpha=0.35)
        saddle, mep = minimum_energy_path(spline, ts)
        ax.plot(mep[:, 0], mep[:, 1], color=AQUA, lw=2.4, solid_capstyle="round")
        ax.plot(*ts, "*", ms=15, mfc=YELLOW, mec=INK, mew=1, zorder=5)
        e_ts = spline(*ts)[0, 0]
        ax.text(ts[0] + 0.12, ts[1] + 0.12, f"transition state\n{e_ts:+.1f} kcal/mol".replace("-", "−"),
                ha="left", va="bottom", fontsize=8.5, color="white")
        ax.set_xlabel("d(C–Cl) (Å)")
        ax.set_ylabel("d(C–F) (Å)")
        ax.set_aspect("equal")
        ax.set_anchor("N")
        ax.grid(False)
        ax.set_title(title, loc="left", fontsize=10.5)
        print(title, "saddle of the spline", saddle.round(3), "path ends", mep[0].round(2), mep[-1].round(2))
    ax = axes[1]
    ax.plot(stopped[:, 0], stopped[:, 1], "x", color="white", ms=5, mew=1.2)
    ax.text(1.65, 2.84, r"F$^-$ drifts away", ha="left", va="top", fontsize=8.5, color="white")
    ax.text(3.55, 1.62, r"Cl$^-$ drifts away", ha="right", va="bottom", fontsize=8.5, color="white")
    ax.text(3.55, 2.84, "×: scan point not converged", ha="right", va="top", fontsize=8, color=INK)
    axes[0].text(1.95, 2.72, "well 1", ha="left", va="top", fontsize=8.5, color="white")
    axes[0].text(3.4, 1.6, "well 2", ha="center", va="bottom", fontsize=8.5, color="white")
    bar = fig.colorbar(filled, ax=axes[:2], orientation="horizontal", fraction=0.05, pad=0.16, aspect=40)
    bar.set_label("kcal/mol, relative to F$^-$ + CH$_3$Cl in each medium")

    # (c) Free energy: the double well against the single barrier
    ax = axes[2]
    gas = profile()["G"]
    wat = {0: 0.0, 2: (w("ts_sn2", "G") - zero_w["G"]) * HARTREE_TO_KCAL,
           4: (w("ch3f", "G") + w("cl_anion", "G") - zero_w["G"]) * HARTREE_TO_KCAL}
    ax.axhline(0, color=INK_2, lw=0.8, ls=(0, (4, 3)))
    for xs, ys, colour, label, shift in ((range(5), gas, BLUE, "gas phase", -2.8),
                                         (list(wat), list(wat.values()), ORANGE, "water (PCM)", 2.8)):
        xs, ys = list(xs), list(ys)
        for k, (x, y) in enumerate(zip(xs, ys)):
            ax.plot([x - 0.28, x + 0.28], [y, y], color=colour, lw=3, solid_capstyle="butt",
                    label=label if k == 0 else None, zorder=3)
            if x:
                ax.text(x, y + shift, f"{y:.1f}".replace("-", "−"), ha="center", va="center", fontsize=9,
                        color=colour)
        for (x1, y1), (x2, y2) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
            ax.plot([x1 + 0.28, x2 - 0.28], [y1, y2], color=colour, lw=0.9, ls=":")
    ax.set_xticks(range(5), ["R", "RC", "TS", "PC", "P"])
    ax.set_xlim(-0.5, 4.5)
    ax.set_ylim(-55, 30)
    ax.set_ylabel("ΔG, 298 K (kcal/mol)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title("(c) Free energy: double well or single barrier", loc="left", fontsize=10.5)
    fig.suptitle(r"F$^-$ + CH$_3$Cl, HF/6-31+G*: the same reaction in the gas phase and in water",
                 x=0.07, ha="left", y=1.0, fontsize=11.5)
    fig.savefig(OUT / "gas_vs_water.png", bbox_inches="tight")
    plt.close(fig)
    print("Written", OUT / "gas_vs_water.png", {k: round(v, 2) for k, v in wat.items()})


if __name__ == "__main__":
    fig_water()
    fig_profile()
    fig_orbitals()
    fig_isomerization()
    fig_pes()
    fig_sn2_vector()
