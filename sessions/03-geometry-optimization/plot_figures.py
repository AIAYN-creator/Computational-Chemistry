"""Builds every figure of Session 03 from the processed data files.

Usage (from this folder):  python plot_figures.py
Requires numpy and matplotlib. Figures are written to figures/.
"""
from pathlib import Path

import matplotlib.patches
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
    "ch4": {"r": 1.087, "angle": 109.47, "mu": 0.0},
    "h2o": {"r": 0.958, "angle": 104.5, "mu": 1.86},
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


# --- Figure 3: normal modes of ammonia (ex3) --------------------------------
NH3_MODES = [
    ("Umbrella", r"A$_1$"), ("Asymmetric bend", "E"), ("Asymmetric bend", "E"),
    ("Symmetric stretch", r"A$_1$"), ("Asymmetric stretch", "E"), ("Asymmetric stretch", "E"),
]


def fig_nh3_modes():
    rows = [l.split() for l in (HERE / "ex3-ammonia-frequencies/normal_modes.txt")
            .read_text().splitlines() if l and not l.startswith("#")]
    xyz = np.array([[float(v) for v in r[1:4]] for r in rows])
    disp = np.array([[float(v) for v in r[4:]] for r in rows]).reshape(len(rows), 6, 3)
    freqs = [float(l.split()[2]) for l in (HERE / "ex3-ammonia-frequencies/frequencies.txt")
             .read_text().splitlines() if l and l[0].isdigit()]

    # Oblique orthographic view: turn about the C3 axis (y), then tilt it
    # towards the viewer so both the umbrella and the in-plane motions show
    yaw, tilt = np.radians(25), np.radians(-30)
    ry = np.array([[np.cos(yaw), 0, np.sin(yaw)], [0, 1, 0], [-np.sin(yaw), 0, np.cos(yaw)]])
    rx = np.array([[1, 0, 0], [0, np.cos(tilt), -np.sin(tilt)], [0, np.sin(tilt), np.cos(tilt)]])
    rot = rx @ ry

    def view(v):
        return (v @ rot.T)[..., :2]

    pos = view(xyz)
    fig, axes = plt.subplots(2, 3, figsize=(10, 6.6))
    for m, ax in enumerate(axes.flat):
        arrows = view(disp[:, m, :]) * 0.9
        for h in range(1, 4):
            ax.plot(*zip(pos[0], pos[h]), color="#8a8986", lw=4, zorder=1, solid_capstyle="round")
        ax.scatter(*pos[0], s=650, color="#3b5bdb", edgecolor=INK, lw=1, zorder=2)
        ax.scatter(pos[1:, 0], pos[1:, 1], s=260, color="#e4e3df", edgecolor=INK, lw=1, zorder=2)
        for a in range(4):
            if np.hypot(*arrows[a]) > 0.03:
                ax.annotate("", xy=pos[a] + arrows[a], xytext=pos[a],
                            arrowprops={"arrowstyle": "-|>", "color": ORANGE, "lw": 2,
                                        "mutation_scale": 14}, zorder=3)
        name, sym = NH3_MODES[m]
        ax.set_title(f"{name} ({sym})\n{freqs[m]:.0f} cm$^{{-1}}$", fontsize=10.5)
        ax.set_aspect("equal")
        ax.set_xlim(-1.75, 1.75)
        ax.set_ylim(-1.45, 1.0)
        ax.axis("off")
    fig.suptitle(r"NH$_3$, HF/6-31G*: normal modes (C$_{3v}$ labels)", x=0.01, ha="left", fontsize=11.5)
    fig.tight_layout()
    save(fig, "nh3_normal_modes.png")

    # Stretch fraction: share of the H motion relative to N that lies along
    # the N-H bonds (0 = pure bend, 1 = pure stretch)
    print("NH3 stretch fraction per mode:")
    for m in range(6):
        along = total = 0.0
        for h in range(1, 4):
            bond = (xyz[h] - xyz[0]) / np.linalg.norm(xyz[h] - xyz[0])
            rel = disp[h, m] - disp[0, m]
            along += np.dot(rel, bond) ** 2
            total += np.dot(rel, rel)
        print(f"  mode {m + 1}: {along / total:.2f}")


# --- Figure 4: HF vs B3LYP against experiment (ex4) ------------------------
# Experimental geometries: (log stem, variable) -> value
# H2O2: semi-experimental equilibrium structure, Herberth, Giesen & Yamada,
# J. Mol. Spectrosc. 2019, 362, 37 (CCCBDB only lists a 1962 fit).
# HCN: NIST CCCBDB.
EXP_EX4 = {
    ("hooh", "roo"): 1.4518, ("hooh", "roh"): 0.962, ("hooh", "a"): 100.0, ("hooh", "z"): 113.7,
    ("hcn", "rcn"): 1.156, ("hcn", "rch"): 1.064,
}
LABELS_EX4 = {
    ("hooh", "roo"): r"O–O (H$_2$O$_2$)", ("hooh", "roh"): r"O–H (H$_2$O$_2$)",
    ("hcn", "rcn"): "C≡N (HCN)", ("hcn", "rch"): "C–H (HCN)",
    ("hooh", "a"): r"∠H–O–O (H$_2$O$_2$)", ("hooh", "z"): r"H–O–O–H dihedral (H$_2$O$_2$)",
}


def load_ex4():
    """{(molecule, method): {variable: value}} from ex4/results.txt."""
    data, key = {}, None
    for line in (HERE / "ex4-hf-vs-b3lyp/results.txt").read_text().splitlines():
        if line.startswith("=="):
            key = tuple(line.split()[1].removesuffix(".log").split("_"))
            data[key] = {}
        else:
            _, name, value, *_ = line.split()
            data[key][name] = float(value)
    return data


def fig_hf_vs_b3lyp():
    data = load_ex4()
    panels = [
        ("Bond lengths", "error against experiment (Å)",
         [("hooh", "roo"), ("hooh", "roh"), ("hcn", "rcn"), ("hcn", "rch")]),
        ("Angles", "error against experiment (°)", [("hooh", "a"), ("hooh", "z")]),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4),
                             gridspec_kw={"width_ratios": [1.25, 1], "wspace": 0.55})
    for ax, (title, xlabel, keys) in zip(axes, panels):
        ax.axvline(0, color=INK_2, lw=1, ls=":")
        for i, key in enumerate(keys):
            mol, var = key
            hf = data[(mol, "hf")][var] - EXP_EX4[key]
            b3 = data[(mol, "b3lyp")][var] - EXP_EX4[key]
            y = len(keys) - 1 - i
            ax.plot([hf, b3], [y, y], color=GRID, lw=3, zorder=1)
            ax.plot(hf, y, "o", color=BLUE, ms=8, zorder=2, label="HF" if i == 0 else None)
            ax.plot(b3, y, "s", color=ORANGE, ms=8, zorder=2, label="B3LYP" if i == 0 else None)
        ax.set_yticks(range(len(keys)), [LABELS_EX4[k] for k in reversed(keys)])
        ax.set_ylim(-0.6, len(keys) - 0.4)
        ax.grid(axis="y", visible=False)
        ax.yaxis.set_minor_locator(plt.NullLocator())
        ax.set_xlabel(xlabel)
        ax.set_title(title, loc="left")
        lim = 1.15 * max(abs(v) for v in ax.get_xlim())
        ax.set_xlim(-lim, lim)
        ax.annotate("experiment", xy=(0, 1), xycoords=("data", "axes fraction"),
                    xytext=(3, -12), textcoords="offset points", fontsize=8, color=INK_2)
    axes[0].legend(loc="lower left", fontsize=8.5)
    fig.suptitle(r"H$_2$O$_2$ (6-31G*) and HCN (6-311G*): HF vs B3LYP optimised geometries",
                 x=0.01, ha="left", fontsize=11.5, y=1.02)
    save(fig, "hf_vs_b3lyp.png")


# --- Figure 5: torsional profile of 1,2-dichloroethane (ex5) ---------------
CL_GREEN, H_GREY = "#2f9e44", "#8a8986"


def load_scan():
    """Dihedral and energy relative to trans (kcal/mol) from ex5/scan.txt."""
    data = np.loadtxt(HERE / "ex5-dichloroethane-scan/scan.txt")
    phi, energy = data[:, 0], data[:, 1]
    return phi, (energy - energy.min()) * 627.5095


def cosine_fit(phi, de, order=6):
    """Least-squares fit E(phi) = sum a_n cos(n phi), symmetric in phi."""
    basis = lambda p: np.column_stack([np.cos(n * np.radians(p)) for n in range(order + 1)])
    coef, *_ = np.linalg.lstsq(basis(phi), de, rcond=None)
    return lambda p: basis(np.atleast_1d(p)) @ coef


def newman(ax, phi, label):
    """Newman projection along C-C: front bonds meet at the centre, back
    bonds start at the circle. Cl on the front carbon points up; the back
    carbon is rotated by the Cl-C-C-Cl dihedral phi. Eclipsed back bonds
    are nudged and their labels pushed out, so both atoms stay readable."""
    r_circle, r_bond = 0.42, 1.0
    ax.add_patch(plt.Circle((0, 0), r_circle, fill=False, color=INK, lw=1.4))
    eclipsed = min(phi % 120, 120 - phi % 120) < 1
    nudge = 14 if eclipsed else 0
    for start, atom in [(0, "Cl"), (120, "H"), (240, "H")]:
        for front in (True, False):
            ang = np.radians(90 - (start + (0 if front else phi + nudge)))
            d = np.array([np.cos(ang), np.sin(ang)])
            p0 = np.zeros(2) if front else d * r_circle
            colour = CL_GREEN if atom == "Cl" else INK_2
            ax.plot(*zip(p0, d * r_bond), color=colour, lw=2.2 if atom == "Cl" else 1.4,
                    zorder=3 if front else 2)
            r_text = r_bond + (0.22 if front or not eclipsed else 0.5)
            ax.text(*(d * r_text), atom, ha="center", va="center",
                    fontsize=8.5 if atom == "Cl" else 7.5,
                    color=CL_GREEN if atom == "Cl" else INK_2,
                    fontweight="bold" if atom == "Cl" else "normal")
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(label, fontsize=9, pad=2)


def fig_dce_scan():
    phi, de = load_scan()
    unique = phi >= 0
    fit = cosine_fit(np.concatenate([phi[unique], -phi[unique]]),
                     np.concatenate([de[unique], de[unique]]), order=5)
    grid = np.linspace(-180, 180, 721)
    curve = fit(grid)
    window = (grid > 30) & (grid < 110)
    phi_g = grid[window][np.argmin(curve[window])]
    e_g = curve[window].min()

    fig = plt.figure(figsize=(10, 6.6))
    ax = fig.add_axes([0.08, 0.08, 0.88, 0.56])
    ax.plot(grid, curve, color=BLUE, lw=1.6, zorder=1, label="cosine-series fit")
    ax.plot(phi, de, "o", color=BLUE, ms=7, zorder=3, label="computed (relaxed scan)")
    mirror = unique & (phi > 0) & (phi < 180)
    ax.plot(np.append(-phi[mirror], -180), np.append(de[mirror], de[phi == 180]),
            "o", mfc=SURFACE, mec=BLUE, mew=1.5, ms=7, zorder=3, label="mirrored, E(φ) = E(−φ)")
    ax.set_xlim(-190, 190)
    ax.set_ylim(-0.8, 11.5)
    ax.set_xticks(range(-180, 181, 60))
    ax.set_xlabel("Cl–C–C–Cl dihedral φ (°)")
    ax.set_ylabel(r"$E - E_{\mathrm{trans}}$ (kcal/mol)")
    ax.legend(loc="upper left", fontsize=8.5)

    # Key conformers: letter on the curve, Newman projection in the row above
    key = [(0, "Cl/Cl eclipsed, 0°"), (phi_g, f"gauche, ≈ {phi_g:.0f}°"),
           (120, "Cl/H eclipsed, 120°"), (180, "trans (anti), 180°")]
    for k, (x, label) in enumerate(key):
        letter = "abcd"[k]
        y = fit(x)[0]
        ax.annotate(f"({letter})", xy=(x, y), xytext=(0, 9 if k != 1 else -16),
                    textcoords="offset points", ha="center", fontsize=9.5,
                    fontweight="bold", color=INK)
        sub = fig.add_axes([0.08 + k * 0.22, 0.69, 0.2, 0.27])
        newman(sub, x, f"({letter}) {label}")
    fig.suptitle("1,2-Dichloroethane, HF/6-31G*: rotation about the C–C bond",
                 x=0.01, ha="left", y=1.045, fontsize=11.5)
    save(fig, "dce_torsion.png")
    print(f"Gauche minimum from the fit: phi = {phi_g:.1f} deg, dE = {e_g:.2f} kcal/mol")


# --- Figure 6: gauche/trans thermochemistry (ex6) ---------------------------
HARTREE_TO_KCAL = 627.5095
R_KCAL = 1.987204e-3  # kcal/(mol K)


def load_thermo():
    def table(name):
        lines = [l.split() for l in (HERE / "ex6-conformer-thermochemistry" / name)
                 .read_text().splitlines() if l and not l.startswith("#")]
        head, rows = lines[0], lines[1:]
        return {r[0]: dict(zip(head[1:], map(float, r[1:]))) for r in rows}
    return table("thermo.txt"), table("thermo_extra.txt")


def thermo_summary():
    """Gauche - trans differences (kcal/mol, cal/(mol K)) and K at 298.15 K."""
    main, extra = load_thermo()
    d = lambda t, k: (t["gauche"][k] - t["trans"][k]) * HARTREE_TO_KCAL
    s = {
        "dE": d(main, "E"), "dE0": d(extra, "E+ZPE"), "dH": d(main, "H"), "dG": d(main, "G"),
        "dZPE": d(extra, "ZPE"), "dS": extra["gauche"]["S_total"] - extra["trans"]["S_total"],
    }
    s["K"] = np.exp(-s["dG"] / (R_KCAL * 298.15))
    return s


def fig_thermo():
    s = thermo_summary()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8),
                                   gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.3})

    # (a) From electronic energy to free energy
    steps = [("ΔE\nelectronic", s["dE"]), ("ΔE + ΔZPE", s["dE0"]),
             ("ΔH\n298 K", s["dH"]), ("ΔG\n298 K", s["dG"])]
    x = np.arange(len(steps))
    ax1.bar(x, [v for _, v in steps], width=0.55, color=BLUE, zorder=2)
    for xi, (_, v) in zip(x, steps):
        ax1.text(xi, v + 0.04, f"{v:.2f}", ha="center", va="bottom", fontsize=9, color=INK)
    ax1.set_xticks(x, [n for n, _ in steps], fontsize=8.5)
    ax1.xaxis.set_minor_locator(plt.NullLocator())
    ax1.set_ylim(0, 2.3)
    ax1.set_ylabel("gauche − trans (kcal/mol)")
    ax1.set_title("(a) Gauche − trans, step by step", loc="left")
    ax1.grid(axis="x", visible=False)

    # (b) Gauche population against temperature, with dH and dS fixed at 298 K
    T = np.linspace(100, 1000, 400)
    dG_T = s["dH"] - T * s["dS"] / 1000
    for g, colour, style, label in ((2, BLUE, "-", "g⁺ + g⁻ (degeneracy 2)"),
                                    (1, ORANGE, "--", "one gauche only")):
        K = g * np.exp(-dG_T / (R_KCAL * T))
        ax2.plot(T, 100 * K / (1 + K), color=colour, ls=style, label=label)
    for g, colour in ((2, BLUE), (1, ORANGE)):
        K = g * s["K"]
        ax2.plot(298.15, 100 * K / (1 + K), "o", color=colour, ms=6, zorder=3)
        ax2.annotate(f"{100 * K / (1 + K):.1f} %", (298.15, 100 * K / (1 + K)),
                     xytext=(8, -2 if g == 2 else -12), textcoords="offset points",
                     fontsize=8.5, color=INK)
    ax2.axvline(298.15, color=INK_2, lw=1, ls=":")
    ax2.set_xlabel("T (K)")
    ax2.set_ylabel("gauche population (%)")
    ax2.set_ylim(0, 50)
    ax2.legend(loc="upper left", fontsize=8.5)
    ax2.set_title("(b) Gauche population (ΔH, ΔS fixed)", loc="left")
    fig.suptitle("1,2-Dichloroethane, HF/6-31G*: gauche/trans thermochemistry",
                 x=0.01, ha="left", y=1.03, fontsize=11.5)
    save(fig, "dce_thermo.png")
    print("Gauche - trans: " + ", ".join(f"{k} = {v:.4g}" for k, v in s.items()))


# --- Figure 7: the report, closing the gap to experiment ---------------------
# Wiberg & Murcko, J. Phys. Chem. 1987, 91, 3616: best computed value
# (MP3/6-31++G**, enthalpy at 298 K) and the gas-phase experiment
LIT_MP3_DH = 1.39
EXP_DH, EXP_DH_ERR = 1.1, 0.1


def report_differences():
    """Gauche - trans dE, dH, dG (kcal/mol), K (with the factor 2) and % gauche."""
    thermo, _ = load_thermo()  # ex6/thermo.txt: trans, gauche, trans_b3lyp, gauche_b3lyp
    out = {}
    for level, suffix in (("HF", ""), ("B3LYP", "_b3lyp")):
        d = {k: (thermo["gauche" + suffix][k] - thermo["trans" + suffix][k]) * HARTREE_TO_KCAL
             for k in ("E", "H", "G")}
        K = 2 * np.exp(-d["G"] / (R_KCAL * 298.15))
        out[level] = {**d, "K": K, "pop": 100 * K / (1 + K)}
    return out


def fig_report_gap():
    res = report_differences()
    K_exp = 2 * np.exp(-EXP_DH / (R_KCAL * 298.15))
    pop_exp = 100 * K_exp / (1 + K_exp)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6),
                                   gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.5})
    # (a) dH, from HF to experiment
    labels = ["HF/6-31G*", "B3LYP/6-31G*", "MP3/6-31++G**\n(Wiberg & Murcko)", "Experiment"]
    values = [res["HF"]["H"], res["B3LYP"]["H"], LIT_MP3_DH, EXP_DH]
    colours = [BLUE, ORANGE, AQUA, INK_2]
    y = np.arange(len(labels))[::-1]
    ax1.axvspan(EXP_DH - EXP_DH_ERR, EXP_DH + EXP_DH_ERR, color=GRID, zorder=0)
    ax1.barh(y, values, height=0.55, color=colours, zorder=2)
    ax1.errorbar(EXP_DH, y[-1], xerr=EXP_DH_ERR, color=INK, capsize=4, lw=1.2, zorder=3)
    for k, (yi, v) in enumerate(zip(y, values)):
        pad = EXP_DH_ERR + 0.05 if k == len(values) - 1 else 0.04
        label = f"{v:.1f} ± {EXP_DH_ERR}" if k == len(values) - 1 else f"{v:.2f}"
        ax1.text(v + pad, yi, label, va="center", fontsize=9, color=INK)
    ax1.set_yticks(y, labels, fontsize=8.5)
    ax1.set_xlim(0, 2.15)
    ax1.set_xlabel("ΔH gauche − trans, 298 K (kcal/mol)")
    ax1.set_title("(a) The gap to experiment", loc="left")
    ax1.grid(axis="y", visible=False)
    ax1.yaxis.set_minor_locator(plt.NullLocator())

    # (b) gauche population at 298 K
    pops = [res["HF"]["pop"], res["B3LYP"]["pop"], pop_exp]
    names = ["HF", "B3LYP", "Exp.\n(estimate)"]
    x = np.arange(3)
    bars = ax2.bar(x, pops, width=0.55, color=[BLUE, ORANGE, SURFACE],
                   edgecolor=[BLUE, ORANGE, INK_2], linewidth=1.5, zorder=2)
    bars[2].set_hatch("///")
    for xi, p in zip(x, pops):
        ax2.text(xi, p + 0.6, f"{p:.0f} %", ha="center", fontsize=9, color=INK)
    ax2.set_xticks(x, names, fontsize=8.5)
    ax2.xaxis.set_minor_locator(plt.NullLocator())
    ax2.set_ylim(0, 30)
    ax2.set_ylabel("gauche population, 298 K (%)")
    ax2.set_title("(b) Gauche population", loc="left")
    ax2.grid(axis="x", visible=False)
    fig.suptitle("1,2-Dichloroethane: HF, B3LYP and experiment", x=0.01, ha="left",
                 y=1.03, fontsize=11.5)
    save(fig, "report_gap.png")
    for level, d in res.items():
        print(level, ", ".join(f"{k} = {v:.3g}" for k, v in d.items()))


# --- Figure 8: internal rotation of fluoromethanol (ex7) ---------------------
F_GREEN, LP_FILL = "#2f9e44", "#f2d48a"


def lobe(ax, angle, length, width, **style):
    """A lone-pair or orbital lobe: an ellipse starting at the centre and
    pointing along angle (degrees, counterclockwise from +x)."""
    d = np.array([np.cos(np.radians(angle)), np.sin(np.radians(angle))])
    centre = d * length / 2
    ax.add_patch(matplotlib.patches.Ellipse(centre, length, width, angle=angle, **style))


def newman_lone_pairs(ax, phi, label):
    """Newman projection of FCH2-OH along O -> C. Front (centre): O, its H
    and its two lone pairs. Back (circle): C with F up and two H.
    phi is the H-O-C-F dihedral, so the front H sits at 90 + phi degrees
    and the lone pairs 120 degrees on either side. A lone pair within 30
    degrees of 270, opposite F, is antiperiplanar to C-F (Klyne-Prelog) and
    is drawn highlighted, next to the back lobe of sigma*(C-F)."""
    r_circle, r_bond = 0.42, 1.0
    eclipsed = abs((phi + 180) % 360 - 180) < 1   # front H on top of F
    nudge = 14 if eclipsed else 0
    ax.add_patch(plt.Circle((0, 0), r_circle, fill=True, fc=SURFACE, ec=INK, lw=1.4, zorder=1))
    # Back carbon: F up, two H
    for start, atom in [(90, "F"), (210, "H"), (330, "H")]:
        ang = np.radians(start - nudge)
        d = np.array([np.cos(ang), np.sin(ang)])
        colour = F_GREEN if atom == "F" else INK_2
        ax.plot(*zip(d * r_circle, d * r_bond), color=colour, lw=2.2 if atom == "F" else 1.4,
                zorder=2)
        ax.text(*(d * (r_bond + 0.2)), atom, ha="center", va="center", color=colour,
                fontsize=8.5 if atom == "F" else 7.5, fontweight="bold" if atom == "F" else "normal")
    # sigma*(C-F): its large lobe sits on C, on the side away from F
    lobe(ax, 270, 0.95, 0.42, fill=False, ec=F_GREEN, lw=1.2, ls=(0, (3, 2)), zorder=2)
    ax.text(0.33, -0.98, "σ*(C–F)", color=F_GREEN, fontsize=7.5, ha="left", va="center")
    # Front oxygen: H and two lone pairs
    h_ang = 90 + phi
    for lp in (h_ang + 120, h_ang - 120):
        anti = abs((lp - 270 + 180) % 360 - 180) < 30
        lobe(ax, lp, 0.62, 0.3, fc=ORANGE if anti else LP_FILL, ec=INK_2, lw=0.8,
             alpha=0.9 if anti else 0.85, zorder=3)
    d = np.array([np.cos(np.radians(h_ang)), np.sin(np.radians(h_ang))])
    ax.plot(*zip((0, 0), d * r_bond), color=INK, lw=1.6, zorder=4)
    ax.text(*(d * (r_bond + 0.2)), "H", ha="center", va="center", fontsize=7.5, color=INK)
    ax.add_patch(plt.Circle((0, 0), 0.07, color=INK, zorder=5))
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(label, fontsize=9, pad=2)


def fig_fluoromethanol():
    data = np.loadtxt(HERE / "ex7-fluoromethanol-rotation/scan.txt")
    phi, de = data[:, 0], (data[:, 1] - data[:, 1].min()) * HARTREE_TO_KCAL
    fit = cosine_fit(np.concatenate([phi, -phi]), np.concatenate([de, de]), order=5)
    grid = np.linspace(-180, 180, 721)
    curve = fit(grid)
    window = (grid > 20) & (grid < 120)
    phi_min = grid[window][np.argmin(curve[window])]

    fig = plt.figure(figsize=(10, 6.9))
    ax = fig.add_axes([0.08, 0.08, 0.88, 0.5])
    ax.plot(grid, curve, color=BLUE, lw=1.6, zorder=1, label="cosine-series fit")
    ax.plot(phi, de, "o", color=BLUE, ms=7, zorder=3, label="computed (relaxed scan)")
    mirror = (phi > 0) & (phi < 180)
    ax.plot(np.append(-phi[mirror], -180), np.append(de[mirror], de[phi == 180]), "o",
            mfc=SURFACE, mec=BLUE, mew=1.5, ms=7, zorder=3, label="mirrored, E(φ) = E(−φ)")
    ax.set_xlim(-190, 190)
    ax.set_ylim(-0.9, 6.4)
    ax.set_xticks(range(-180, 181, 60))
    ax.set_xlabel("H–O–C–F dihedral φ (°)")
    ax.set_ylabel(r"$E - E_{\mathrm{min}}$ (kcal/mol)")
    ax.legend(loc="upper center", fontsize=8.5)

    key = [(0, "syn, 0°", "no lone pair anti to C–F;\nweak O–H···F attraction"),
           (phi_min, f"gauche, ≈ {phi_min:.0f}°", "one lone pair anti to C–F:\nn(O) → σ*(C–F)"),
           (180, "anti, 180°", "no lone pair anti to C–F;\nboth point towards F")]
    for k, (x, label, note) in enumerate(key):
        letter = "abc"[k]
        ax.annotate(f"({letter})", xy=(x, fit(x)[0]), xytext=(0, 9 if k != 1 else -16),
                    textcoords="offset points", ha="center", fontsize=9.5,
                    fontweight="bold", color=INK)
        sub = fig.add_axes([0.1 + k * 0.3, 0.68, 0.24, 0.27])
        newman_lone_pairs(sub, x, f"({letter}) {label}")
        sub.text(0.5, -0.06, note, transform=sub.transAxes, ha="center", va="top",
                 fontsize=7.8, color=INK_2, linespacing=1.3)
    fig.suptitle("Fluoromethanol, B3LYP/6-31G*: rotation of the OH group, seen along O → C",
                 x=0.01, ha="left", y=1.045, fontsize=11.5)
    save(fig, "fluoromethanol_rotation.png")
    print(f"Fluoromethanol minimum from the fit: phi = {phi_min:.1f} deg, "
          f"dE(0) = {de[phi == 0][0]:.2f}, dE(180) = {de[phi == 180][0]:.2f} kcal/mol")


if __name__ == "__main__":
    fig_errors()
    fig_ir_spectrum()
    fig_nh3_modes()
    fig_hf_vs_b3lyp()
    fig_dce_scan()
    fig_thermo()
    fig_report_gap()
    fig_fluoromethanol()
