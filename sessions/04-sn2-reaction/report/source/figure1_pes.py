"""Figure 1: (a) gas-phase PES, (b) water PES (PCM), (c) free-energy profiles.
Usage: python3 fig2.py sep.dat [sep_pcm.dat] figure1.pdf"""
import sys, os
CMAP = os.environ.get("CMAP", "viridis")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.interpolate import RectBivariateSpline

plt.rcParams.update({
    "font.family": "serif", "mathtext.fontset": "cm", "font.size": 8,
    "axes.linewidth": 0.6, "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "legend.frameon": False,
})

def load(path):
    d = {}
    for line in open(path):
        p = line.split()
        if len(p) == 3 and float(p[0]) > 1.7:          # mismo rango en los dos mapas
            d[(float(p[0]), float(p[1]))] = float(p[2])
    xs = np.array(sorted({k[0] for k in d})); ys = np.array(sorted({k[1] for k in d}))
    Z = np.array([[d[(x, y)] for y in ys] for x in xs])
    Z = Z - Z.min()                                   # relativa al punto más bajo
    S = RectBivariateSpline(xs, ys, Z)
    gx = np.linspace(xs[0], xs[-1], 300); gy = np.linspace(ys[0], ys[-1], 300)
    return gx, gy, S(gx, gy).T

def pes(ax, path, labels, tag):
    gx, gy, Z = load(path)
    cf = ax.contourf(gx, gy, Z, levels=np.arange(-4, 92, 2), cmap=CMAP, extend="max")
    ax.contour(gx, gy, Z, levels=np.arange(2, 90, 2), colors="k", linewidths=0.2, alpha=0.45)
    cs = ax.contour(gx, gy, Z, levels=np.arange(10, 90, 10), colors="k", linewidths=0.6)
    ax.clabel(cs, fmt="%d", fontsize=5.5, inline_spacing=2)
    for text, (x, y, dx, dy) in labels.items():
        if not text.startswith("_"):
            ax.plot(x, y, "o", ms=2.2, color="white", mec="k", mew=0.4)
        text = text.lstrip("_")
        ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=7.5,
                    color="white", fontweight="bold", ha="center", va="center")
    ax.set_xlabel(r"$d$(C–Cl) (Å)"); ax.set_ylabel(r"$d$(C–F) (Å)")
    ax.text(-0.22, 1.0, tag, transform=ax.transAxes, va="bottom", fontweight="bold")
    return cf

args = sys.argv[1:]
gas_dat, out = args[0], args[-1]
water_dat = args[1] if len(args) == 3 else None

fig, (a, b, c) = plt.subplots(1, 3, figsize=(7.1, 2.1),
                              gridspec_kw={"width_ratios": [1, 1, 1.15]})
# Geometrías optimizadas [d(C-Cl), d(C-F)] (ej. 2, ej. 4 y PCM)
pes(a, gas_dat, {"RC": (1.861, 2.586, 11, 5), r"TS$^\ddagger$": (2.133, 2.125, 12, 3),
                 "PC": (3.423, 1.399, -10, 7)}, "(a)")
if water_dat:
    pes(b, water_dat, {r"TS$^\ddagger$": (2.231, 2.071, 12, 3),
                       "_R": (1.95, 2.78, 0, 0), "_P": (3.48, 1.4, 0, 0)}, "(b)")
else:
    b.text(0.5, 0.5, "water PES\n(pending)", ha="center", va="center", transform=b.transAxes)
    b.text(0.04, 0.95, "(b)", transform=b.transAxes, va="top", fontweight="bold")

# (c) perfiles de energía libre (kcal/mol, respecto a F- + CH3Cl)
xl = ["R", "RC", r"TS$^\ddagger$", "PC", "P"]
gas = [0, -8.29, -5.22, -45.89, -43.37]
wat = {0: 0.0, 2: 20.86, 4: -27.88}
def levels(xs, ys, color, ls, label):
    for x, y in zip(xs, ys):
        c.plot([x - .28, x + .28], [y, y], color=color, lw=1.6, solid_capstyle="butt")
    for (x1, y1), (x2, y2) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        c.plot([x1 + .28, x2 - .28], [y1, y2], color=color, lw=0.6, ls=ls)
    c.plot([], [], color=color, lw=1.6, label=label)
levels(range(5), gas, "k", "--", "gas phase")
levels(list(wat), list(wat.values()), "0.55", ":", "water (PCM)")
for x, y in zip(range(5), gas):
    c.text(x, y - 5, f"{y:.1f}", ha="center", fontsize=6)
for x, y in wat.items():
    if x:
        c.text(x, y + 2, f"{y:.1f}", ha="center", fontsize=6, color="0.4")
c.set_xticks(range(5)); c.set_xticklabels(xl)
c.tick_params(axis="x", top=False)
c.set_xlabel("reaction coordinate (schematic)"); c.set_ylabel(r"$\Delta G$ (kcal/mol)")
c.set_xlim(-0.5, 4.5); c.set_ylim(-56, 28)
c.legend(loc="lower left", fontsize=6.5, handlelength=1.5)
c.text(-0.22, 1.0, "(c)", transform=c.transAxes, va="bottom", fontweight="bold")

plt.tight_layout(pad=0.3, w_pad=0.8)
plt.savefig(out)
