"""Figuras del informe de la sesion 8: ubiquitina en agua (NAMD, 100 ps, NVT).

Fig. 1: T, E y RMSD frente al tiempo (equilibrado termico frente a estructural).
Fig. 2: factores B de la MD frente a los del cristal 1UBQ, residuo a residuo.

Archivos de entrada (en la misma carpeta):
  ubq_ET.dat        paso, TOTAL (kcal/mol), TEMP (K)        <- log de NAMD
  ubq_rmsd_ini.dat  fotograma, RMSD (A) frente a initial.coor  <- measure rmsd (VMD)
  ubq_rmsf_ca.dat   resid, resname, estructura, RMSF (A)     <- measure rmsf (VMD)
  1ubq_bfac_ca.dat  resid, B (A^2)                           <- PDB 1UBQ, Calfa
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, NullFormatter, ScalarFormatter
from scipy import stats

# ---------------------------------------------------------------- parametros
T_PLATEAU = 32.0                # ps, inicio del plateau del RMSD
DT_FRAME = 0.25                 # ps entre fotogramas (dcdfreq 250 x 1 fs)
C_MD, C_X = "#2a78d6", "#eb6834"  # azul = simulacion, naranja = cristal
GRIS = "#52514e"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10"],          # Computer Modern, como el LaTeX del informe
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "font.size": 8,
    "axes.linewidth": 0.6,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "legend.frameon": False,
    "lines.linewidth": 0.8,
})


def media_acumulada(x):
    """Media de todos los valores vistos hasta cada punto."""
    return np.cumsum(x) / np.arange(1, len(x) + 1)


# ---------------------------------------------------------------- datos
paso, E, T = np.loadtxt("ubq_ET.dat", unpack=True)
t = paso * 1.0e-3                       # pasos (1 fs) -> ps

frame, rmsd = np.genfromtxt("ubq_rmsd_ini.dat", unpack=True)  # salta la linea vacia
t_rmsd = (frame + 1) * DT_FRAME         # el fotograma 0 se escribe en el paso 250

res = np.loadtxt("ubq_rmsf_ca.dat", usecols=0).astype(int)
ss = np.loadtxt("ubq_rmsf_ca.dat", usecols=2, dtype=str)
rmsf = np.loadtxt("ubq_rmsf_ca.dat", usecols=3)
res_x, B_x = np.loadtxt("1ubq_bfac_ca.dat", unpack=True)
assert np.array_equal(res, res_x.astype(int)), "los residuos no coinciden"

B_md = 8 * np.pi**2 / 3 * rmsf**2       # RMSF (A) -> B (A^2), isotropo

# ---------------------------------------------------------------- numeros
plat = t >= T_PLATEAU
print(f"T = {T[plat].mean():.2f} +/- {T[plat].std():.2f} K")
print(f"E = {E[plat].mean():.1f} +/- {E[plat].std():.1f} kcal/mol")
print(f"RMSD plateau = {rmsd[t_rmsd >= T_PLATEAU].mean():.2f} +/- "
      f"{rmsd[t_rmsd >= T_PLATEAU].std():.2f} A")

nucleo = res <= 70
for nombre, m in [("todos", res > 0), ("nucleo 1-70", nucleo)]:
    r = stats.pearsonr(B_md[m], B_x[m])[0]
    rho = stats.spearmanr(B_md[m], B_x[m])[0]
    print(f"{nombre:12s} Pearson r = {r:.2f}  Spearman rho = {rho:.2f}  "
          f"<B_x>/<B_md> = {B_x[m].mean() / B_md[m].mean():.1f}")

# ================================================================ Figura 1
fig, ax = plt.subplots(1, 3, figsize=(7.0, 1.5),
                       gridspec_kw={"wspace": 0.42})

ax[0].plot(t, T, color=C_MD, lw=0.5)
ax[0].plot(t[plat], media_acumulada(T[plat]), color="k", lw=1.0)
ax[0].set_ylabel(r"$T$ / K")

ax[1].plot(t, E / 1e3, color=C_MD, lw=0.5)          # en 10^3 kcal/mol: etiquetas cortas
ax[1].plot(t[plat], media_acumulada(E[plat]) / 1e3, color="k", lw=1.0)
ax[1].set_ylabel(r"$E$ / $10^3$ kcal mol$^{-1}$")

ax[2].plot(t_rmsd, rmsd, color=C_MD, lw=0.8)
ax[2].set_ylabel(r"RMSD / $\AA$")

for a, lab in zip(ax, "abc"):
    a.axvspan(0, T_PLATEAU, color=GRIS, alpha=0.08, lw=0)
    a.text(0.98, 0.08, f"({lab})", transform=a.transAxes, ha="right")
ax[0].annotate(r"211 K", xy=(0.1, 211), xytext=(8, 235),
               arrowprops=dict(arrowstyle="-", lw=0.5, color=GRIS),
               color=GRIS)
for a in ax:
    a.set_xlim(0, 100)
    a.set_xlabel(r"$t$ / ps")

fig.savefig("fig1_ubq_tiempo.pdf", bbox_inches="tight")

# ================================================================ Figura 2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.0),
                             gridspec_kw={"width_ratios": [2.2, 1], "wspace": 0.28})

# --- (a) B frente al residuo, con la estructura secundaria encima
a1.plot(res, B_x, "-o", color=C_X, ms=2.2, label="crystal (1UBQ)")
a1.plot(res, B_md, "-o", color=C_MD, ms=2.2, label="MD (100 ps)")
a1.set_yscale("log")
a1.set_xlim(0.5, 76.5)
a1.set_xlabel("residue")
a1.set_ylabel(r"$B$ / $\AA^2$")
a1.legend(loc="upper left", fontsize=7)

# banda de estructura secundaria (STRIDE, VMD) en coordenadas de eje
ss_color = {"H": "#3a3a38", "G": "#8a8984", "E": "#b5b4ae"}
y0, h = 1.02, 0.06
for r, s in zip(res, ss):
    if s in ss_color:
        a1.add_patch(Rectangle((r - 0.5, y0), 1, h, color=ss_color[s],
                               transform=a1.get_xaxis_transform(),
                               clip_on=False, lw=0))
# una etiqueta por elemento (nomenclatura habitual de la ubiquitina)
for x, txt in [(4, r"$\beta1$"), (14, r"$\beta2$"), (28.5, r"$\alpha1$"), (39, r"$3_{10}$"),
               (43, r"$\beta3$"), (48.5, r"$\beta4$"), (68.5, r"$\beta5$")]:
    a1.text(x, y0 + h + 0.03, txt, transform=a1.get_xaxis_transform(),
            ha="center", va="bottom", fontsize=6.5, color=GRIS)
a1.text(0.40, 0.90, "(a)", transform=a1.transAxes, ha="center")   # zona alta central, sin datos

# --- (b) dispersion MD frente a cristal
lims = [1.5, 70]
a2.plot(lims, lims, color=GRIS, lw=0.6, ls="--")
a2.scatter(B_x[nucleo], B_md[nucleo], s=8, color=C_MD, lw=0, label=r"residues 1$-$70")
a2.scatter(B_x[~nucleo], B_md[~nucleo], s=10, facecolor="white",
           edgecolor=C_MD, lw=0.8, label="C-terminal tail")
a2.set_xscale("log"); a2.set_yscale("log")
a2.set_xlim(lims); a2.set_ylim(lims)
a2.set_xlabel(r"$B_\mathrm{crystal}$ / $\AA^2$")
a2.set_ylabel(r"$B_\mathrm{MD}$ / $\AA^2$")
a2.legend(loc="upper left", fontsize=7, handletextpad=0.2)
a2.text(0.97, 0.04, "(b)", transform=a2.transAxes, ha="right")

# ejes log con numeros normales (2, 5, 10...) en vez de 2x10^0
TICKS = [2, 5, 10, 20, 50]
for eje in (a1.yaxis, a2.xaxis, a2.yaxis):
    eje.set_major_locator(FixedLocator(TICKS))
    eje.set_major_formatter(ScalarFormatter())
    eje.set_minor_formatter(NullFormatter())

fig.savefig("fig2_ubq_bfactors.pdf", bbox_inches="tight")
print("figuras guardadas")
