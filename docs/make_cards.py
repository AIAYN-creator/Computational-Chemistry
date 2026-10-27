"""Builds the "featured findings" cards of the main README (docs/cards/).

Usage (from the repository root):  python docs/make_cards.py
Every number and every curve comes from the data files of the sessions.
"""
import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
S01 = ROOT / "sessions/01-linux-and-z-matrices"
S02 = ROOT / "sessions/02-hartree-fock"
S03 = ROOT / "sessions/03-geometries-and-conformers"
OUT = ROOT / "docs/cards"
OUT.mkdir(exist_ok=True)

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SURFACE, CARD = "#fafaf8", "#ffffff"
HARTREE_TO_EV, HARTREE_TO_KCAL = 27.211386, 627.5095

plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "cm",
    "font.size": 10,
    "axes.edgecolor": INK_2,
    "axes.labelcolor": INK_2,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "savefig.dpi": 200,
})


def card(number, unit, title, caption, tag, draw, name):
    """One card: big number and text on the left, a small plot on the right."""
    fig = plt.figure(figsize=(6.4, 3.0), facecolor=CARD)
    fig.text(0.05, 0.86, tag, fontsize=8, color=INK_2, fontweight="bold")
    big = fig.text(0.05, 0.56, number, fontsize=34, color=BLUE, va="baseline")
    # Place the unit right after the number, measuring its real width
    fig.canvas.draw()
    box = big.get_window_extent().transformed(fig.transFigure.inverted())
    fig.text(box.x1 + 0.012, 0.56, unit, fontsize=13, color=BLUE, va="baseline")
    fig.text(0.05, 0.43, title, fontsize=11.5, color=INK, va="top", wrap=True)
    fig.text(0.05, 0.10, caption, fontsize=8.3, color=INK_2, va="bottom", linespacing=1.4)
    ax = fig.add_axes([0.58, 0.17, 0.38, 0.66])
    ax.set_facecolor(SURFACE)
    draw(ax)
    fig.savefig(OUT / name, facecolor=CARD)
    plt.close(fig)
    print("Written", OUT / name)


# --- 1. RHF cannot break H2 (Session 02, Ex. 6) ------------------------------
def card_rhf():
    rhf = np.loadtxt(S02 / "ex6-rhf-vs-uhf/h2_rhf.dat", skiprows=1)
    uhf = np.loadtxt(S02 / "ex6-rhf-vs-uhf/h2_uhfmix.dat", skiprows=1)
    rhf, uhf = rhf[np.argsort(rhf[:, 0])], uhf[np.argsort(uhf[:, 0])]
    error = rhf[-1, 1] * HARTREE_TO_EV

    def draw(ax):
        ax.axhline(0, color=INK_2, lw=0.8, ls=":")
        ax.plot(rhf[:, 0], rhf[:, 1], color=BLUE, lw=1.8, label="RHF")
        ax.plot(uhf[:, 0], uhf[:, 1], color=ORANGE, lw=1.8, ls="--", label="UHF")
        ax.annotate("", xy=(9.6, rhf[-1, 1]), xytext=(9.6, 0),
                    arrowprops={"arrowstyle": "<->", "color": INK, "lw": 1})
        ax.set_xlabel("H–H distance (Å)", fontsize=8)
        ax.set_ylabel("ΔE (hartree)", fontsize=8)
        ax.legend(fontsize=7.5, loc="center right", frameon=False)

    card(f"{error:.1f}", "eV", "Restricted Hartree–Fock\ncannot break a bond",
         "At 10 Å, RHF keeps H₂ 50 % ionic and\nends far above two H atoms. UHF fixes\nit, at the price of spin contamination.",
         "SESSION 02 · REPORT", draw, "card_rhf.png")


# --- 2. The acetylene that came out bent (Session 03, Ex. 4) -----------------
def card_acetylene():
    spec = importlib.util.spec_from_file_location("s01", S01 / "plot_figures.py")
    s01 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s01)

    lines = (S03 / "ex4-hf-vs-b3lyp/results.txt").read_text().splitlines()
    i = lines.index("== hcch_hf.log")
    variables = {l.split()[1]: float(l.split()[2]) for l in lines[i + 1:i + 3]}
    bent_atoms, _ = s01.read_zmatrix(S03 / "ex4-hf-vs-b3lyp/hcch_hf.com")
    good_atoms, good_vars = s01.read_zmatrix(S01 / "z-matrices/hcch.zmat")
    good_vars.update({"r1": variables["rcc"], "r2": variables["rch"]})
    bent = s01.to_cartesian(bent_atoms, variables)
    good = s01.to_cartesian(good_atoms, good_vars)

    def angle(a, b, c):
        u, v = a - b, c - b
        return np.degrees(np.arccos(u @ v / np.linalg.norm(u) / np.linalg.norm(v)))

    theta = angle(bent[0], bent[1], bent[4])

    def draw(ax):
        for pos, idx, y0, colour, label in ((good, [5, 0, 1, 4], 0.9, AQUA, "intended: linear"),
                                            (bent, [3, 0, 1, 4], -0.5, ORANGE, "optimised: bent")):
            # project onto the plane of the molecule: C-C along x
            c1, c2 = pos[0], pos[1]
            ex = (c2 - c1) / np.linalg.norm(c2 - c1)
            other = pos[idx[-1]] - c1
            ey = other - (other @ ex) * ex
            ey = ey / np.linalg.norm(ey) if np.linalg.norm(ey) > 1e-6 else np.array([0, 1, 0])
            xy = np.array([[(pos[k] - c1) @ ex, (pos[k] - c1) @ ey + y0] for k in idx])
            ax.plot(xy[:, 0], xy[:, 1], color="#8a8986", lw=3, zorder=1)
            ax.scatter(xy[1:3, 0], xy[1:3, 1], s=120, color="#5c5f66", edgecolor=INK, zorder=2)
            ax.scatter(xy[[0, 3], 0], xy[[0, 3], 1], s=60, color="#e4e3df", edgecolor=INK, zorder=2)
            ax.text(-1.15, y0 + 0.32, label, fontsize=7.5, color=colour, fontweight="bold")
        ax.set_xlim(-1.3, 2.6)
        ax.set_ylim(-1.35, 1.5)
        ax.set_aspect("equal")
        ax.axis("off")

    card(f"{theta:.0f}", "°", "“Stationary point found”\ndoes not mean right",
         "One dummy atom for two carbons left the\nsecond H off the axis. The optimiser\nconverged, to the wrong molecule.",
         "SESSION 03 · EX. 4", draw, "card_acetylene.png")


# --- 3. The gauche population of 1,2-dichloroethane (Session 03 report) ------
def card_gauche():
    rows = [l.split() for l in (S03 / "ex6-conformer-thermochemistry/thermo.txt")
            .read_text().splitlines()[1:]]
    data = {r[0]: float(r[4]) for r in rows}
    R, T = 1.987204e-3, 298.15
    pops = {}
    for level, suffix in (("HF", ""), ("B3LYP", "_b3lyp")):
        dG = (data["gauche" + suffix] - data["trans" + suffix]) * HARTREE_TO_KCAL
        K = 2 * np.exp(-dG / (R * T))
        pops[level] = 100 * K / (1 + K)
    K_exp = 2 * np.exp(-1.1 / (R * T))
    pops["Exp."] = 100 * K_exp / (1 + K_exp)

    def draw(ax):
        x = np.arange(3)
        bars = ax.bar(x, list(pops.values()), width=0.6, color=[BLUE, ORANGE, SURFACE],
                      edgecolor=[BLUE, ORANGE, INK_2], lw=1.3, zorder=2)
        bars[2].set_hatch("///")
        for xi, p in zip(x, pops.values()):
            ax.text(xi, p + 0.8, f"{p:.0f} %", ha="center", fontsize=8, color=INK)
        ax.set_xticks(x, list(pops.keys()), fontsize=8)
        ax.set_ylim(0, 30)
        ax.set_ylabel("gauche at 298 K (%)", fontsize=8)
        ax.grid(axis="x", visible=False)

    card(f"{pops['HF']:.0f}", "%", "Gauche 1,2-dichloroethane:\na third of the real amount",
         "HF misses ΔH by 0.7 kcal/mol, and K is\nexponential. B3LYP closes only a third\nof the gap: correlation is not enough.",
         "SESSION 03 · REPORT", draw, "card_gauche.png")


# --- 4. A scan and an optimiser agree (Sessions 02 and 03) -------------------
def card_agreement():
    rows = [l.split() for l in (S02 / "ex3-bond-scans/results.txt").read_text().splitlines()[1:]]
    pts = np.array([(float(r), float(e)) for f, r, e in rows if f == "hfscan_631gdp.log"])
    pts = pts[np.argsort(pts[:, 0])]
    i = np.argmin(pts[:, 1])
    a, b, _ = np.polyfit(pts[i - 1:i + 2, 0], pts[i - 1:i + 2, 1], 2)
    r_scan = -b / (2 * a)
    r_opt = next(float(l.split()[2]) for l in (S03 / "ex1-optimized-geometries/results.txt")
                 .read_text().splitlines() if l.startswith("hf 631gss"))

    def draw(ax):
        rel = (pts[:, 1] - pts[:, 1].min()) * 1000
        ax.plot(pts[:, 0], rel, "o", color=BLUE, ms=4.5, label="S02: scan points")
        grid = np.linspace(pts[0, 0], pts[-1, 0], 200)
        fit = np.polyval(np.polyfit(pts[:, 0], pts[:, 1], 4), grid)
        ax.plot(grid, (fit - pts[:, 1].min()) * 1000, color=BLUE, lw=1, alpha=0.6)
        ax.axvline(r_opt, color=ORANGE, lw=1.8, label="S03: optimiser")
        ax.set_xlabel("H–F distance (Å)", fontsize=8)
        ax.set_ylabel("E − E$_{min}$ (mhartree)", fontsize=8)
        ax.legend(fontsize=7.5, frameon=False, loc="upper center")
        ax.set_ylim(top=ax.get_ylim()[1] * 1.5)

    card(f"{abs(r_scan - r_opt):.3f}", "Å", "Two methods, two sessions,\none bond length",
         f"Bond length of HF at HF/6-31G**:\n{r_scan:.4f} Å from a scan (Session 02),\n{r_opt:.4f} Å from an optimiser (Session 03).",
         "SESSIONS 02 + 03", draw, "card_agreement.png")


# --- 5. The anomeric effect in fluoromethanol (Session 03, Ex. 7) ------------
def card_anomeric():
    data = np.loadtxt(S03 / "ex7-fluoromethanol-rotation/scan.txt")
    phi, de = data[:, 0], (data[:, 1] - data[:, 1].min()) * HARTREE_TO_KCAL
    # Mirror the half turn, E(phi) = E(-phi), and smooth it with a cosine series
    both_phi, both_de = np.concatenate([phi, -phi]), np.concatenate([de, de])
    basis = lambda p: np.column_stack([np.cos(n * np.radians(p)) for n in range(6)])
    coef, *_ = np.linalg.lstsq(basis(both_phi), both_de, rcond=None)
    grid = np.linspace(-180, 180, 361)

    def draw(ax):
        ax.plot(grid, basis(grid) @ coef, color=BLUE, lw=1.8)
        ax.plot(both_phi, both_de, "o", color=BLUE, ms=3.5)
        ax.annotate("gauche", xy=(60, 0), xytext=(60, 1.6), ha="center", fontsize=7.5,
                    color=INK, arrowprops={"arrowstyle": "-", "color": INK_2, "lw": 0.8})
        ax.annotate("anti", xy=(180, de[-1]), xytext=(118, de[-1] + 0.7), ha="center",
                    fontsize=7.5, color=ORANGE,
                    arrowprops={"arrowstyle": "-", "color": INK_2, "lw": 0.8})
        ax.set_xlim(-190, 190)
        ax.set_ylim(-0.4, 6.6)
        ax.set_xticks([-180, 0, 180])
        ax.set_xlabel("H–O–C–F dihedral (°)", fontsize=8)
        ax.set_ylabel("ΔE (kcal/mol)", fontsize=8)

    card(f"{de[-1]:.1f}", "kcal/mol", "Anti is the worst\nconformer of fluoromethanol",
         "Sterics predict the opposite. At gauche,\nan O lone pair sits anti to C–F and\ndonates into σ*(C–F): the anomeric effect.",
         "SESSION 03 · EX. 7", draw, "card_anomeric.png")


# --- 6. The saddle point hidden by symmetry (Session 03, Ex. 8) --------------
def card_saddle():
    rows = [l.split() for l in (S03 / "ex8-glycine-conformers/glycine.txt")
            .read_text().splitlines()[1:]]
    e = {r[0]: float(r[1]) for r in rows}
    gap = {(c, m): (e[f"gly_{c}_{m}"] - e[f"gly_{c}_{m}_c1"]) * HARTREE_TO_KCAL
           for c in "BD" for m in ("hf", "b3lyp")}

    def draw(ax):
        x = np.arange(2)
        for k, (m, name, colour) in enumerate((("hf", "HF", BLUE), ("b3lyp", "B3LYP", ORANGE))):
            vals = [gap[(c, m)] for c in "BD"]
            ax.bar(x + (k - 0.5) * 0.36, vals, width=0.36, color=colour, label=name, zorder=2)
        ax.set_xticks(x, ["B: almost planar", "D: not planar"], fontsize=7.5)
        ax.set_ylim(0, 4.6)
        ax.set_ylabel("E(planar) − E(real min.)\n(kcal/mol)", fontsize=8)
        ax.legend(fontsize=7.5, frameon=False, loc="upper left")
        ax.grid(axis="x", visible=False)

    card(f"{gap[('D', 'hf')]:.1f}", "kcal/mol", "Imposed symmetry hid\na saddle point",
         "Planar glycine D had an imaginary mode,\nthe NH₂ group turning. Freed from the\nplane, it fell to the real, twisted minimum.",
         "SESSION 03 · EX. 8", draw, "card_saddle.png")


if __name__ == "__main__":
    card_rhf()
    card_acetylene()
    card_gauche()
    card_agreement()
    card_anomeric()
    card_saddle()
