# Session 03 — Geometry Optimisation and Frequencies

From fixed geometries to optimised ones: letting Hartree–Fock find the structure of a molecule, seeing how far that structure is from experiment with each basis set, and then probing the curvature of the minimum through its vibrational frequencies.

![Error of HF optimised geometries and dipoles against experiment](figures/error_vs_basis.png)

## Contents

Each exercise folder has its own README with the task and the reasoning behind each step, and its scripts are commented line by line. The Bash patterns are explained in the **[Bash for Gaussian guide](../../docs/bash-for-gaussian.md)**.

| Exercise | Question | Level of theory |
|---|---|---|
| [Ex. 1 — Optimised geometries](ex1-optimized-geometries/) | How close do HF geometries and dipoles get to experiment, and how does the basis set change them? | HF, STO-3G → 6-31G** |
| [Ex. 2 — Vibrational frequencies](ex2-vibrational-frequencies/) | What are the normal modes of water, and how good are harmonic HF frequencies? | HF/6-31G* |
| [Ex. 3 — Ammonia frequencies](ex3-ammonia-frequencies/) | Can the symmetry and the character of each mode be read from the displacement vectors alone? | HF/6-31G* |
| [Ex. 4 — HF vs B3LYP](ex4-hf-vs-b3lyp/) | How much does electron correlation (through B3LYP) improve optimised geometries? | HF, B3LYP / 6-31G*, 6-311G* |
| [Ex. 5 — Dichloroethane conformers](ex5-dichloroethane-scan/) | How does the energy change as one CH₂Cl group rotates about the C–C bond? | HF/6-31G*, relaxed scan |

More exercises will be added as the session goes on.

---

## Ex. 1 — Optimised geometries and the basis set

CH₄, H₂O, HF and NH₃ are optimised with four basis sets, 16 optimisations in all. Each one starts from a Z-matrix whose shared variables keep the molecular symmetry, and some start deliberately far from the answer, such as water at 90°.

| 6-31G** | r (Å) | Exp. | Angle (°) | Exp. | μ (D) | Exp. |
|---|---|---|---|---|---|---|
| CH₄ | 1.0835 | 1.086 | 109.47 | 109.47 | 0 | 0 |
| H₂O | 0.9431 | 0.958 | 105.96 | 104.5 | 2.15 | 1.85 |
| HF  | 0.9006 | 0.917 | – | – | 1.94 | 1.83 |
| NH₃ | 1.0008 | 1.012 | 107.61 | 106.7 | 1.84 | 1.47 |

- **HF bonds are too short** with the larger basis sets, by up to 0.016 Å, the systematic trend of Hartree–Fock without electron correlation.
- **3-21G flattens NH₃** to 112.4°, 5.7° too wide. Adding d functions (6-31G*) fixes it, and polarisation on hydrogen (6-31G**) barely changes the geometry.
- **Dipoles are too large** with the larger basis sets, by 0.1–0.45 D: the HF charge distribution is too ionic.
- **Consistent with Session 02:** the optimised HF bond lengths match the scans of [S02 Ex. 3](../02-hartree-fock/ex3-bond-scans/) to 0.001 Å, and every optimised energy is below the fixed-geometry energy of [S02 Ex. 2](../02-hartree-fock/ex2-basis-sets/) with the same basis set.

Full table, NH₃ symmetry check and conclusions: [Ex. 1 README](ex1-optimized-geometries/).

---

## Ex. 2 — Vibrational frequencies of water

Water is optimised and its harmonic frequencies computed in a single job (`opt freq`) at HF/6-31G*. The optimised geometry is identical to Ex. 1, and three real frequencies confirm it is a true minimum.

![Simulated IR spectrum of water](figures/ir_spectrum.png)

| Mode | Symmetry | Harmonic | Scaled × 0.8953 | Exp. | IR (km/mol) |
|---|---|---|---|---|---|
| Bend | A₁ | 1827 | 1635 | 1595 | 107 |
| Symmetric stretch | A₁ | 4070 | 3644 | 3657 | 18 |
| Antisymmetric stretch | B₂ | 4189 | 3750 | 3756 | 58 |

- **Harmonic HF frequencies are 11–15 % too high:** the harmonic approximation ignores anharmonicity, and HF bonds are too stiff.
- **A single scale factor** (0.8953 for HF/6-31G(d)) brings both stretches within 15 cm⁻¹ of experiment; the bend stays 40 cm⁻¹ high.
- **IR intensity follows the change in dipole, not the stiffness:** the soft bend is the strongest band.

Normal-mode diagrams, GaussView views and conclusions: [Ex. 2 README](ex2-vibrational-frequencies/).

---

## Ex. 3 — Vibrational frequencies of ammonia

The same `opt freq` job for NH₃. This time the six normal modes are worked out from the output alone: the displacement vectors give the C₃ axis, the position of each H and, through their projection on the N–H bonds, whether each mode is a bend or a stretch.

![Normal modes of ammonia](figures/nh3_normal_modes.png)

| Mode | C₃ᵥ | Harmonic (cm⁻¹) | Exp. (cm⁻¹) | IR (km/mol) | Raman (Å⁴/amu) |
|---|---|---|---|---|---|
| Umbrella | A₁ | 1210 | 950 | 218 | 8.8 |
| Asymmetric bend | E | 1850 | 1627 | 21 | 10.6 |
| Symmetric stretch | A₁ | 3688 | 3337 | 0.3 | 116 |
| Asymmetric stretch | E | 3821 | 3444 | 0.5 | 59 |

- **Bends and stretches separate cleanly:** the share of each mode's H motion along the N–H bonds is 0.00 for the three bends and 0.99–1.00 for the three stretches.
- **The umbrella has the largest error, 27 %**, against 11–14 % for the other modes: inversion makes its potential a strongly anharmonic double well.
- **IR and Raman are complementary:** the umbrella dominates the IR spectrum, while the stretches are almost IR-silent but dominate the Raman one.
- **Gaussian found Cs, not C₃ᵥ:** the Z-matrix leaves the symmetry free, and a 10⁻⁴ Å asymmetry was enough to lose the C₃ axis. It splits the E pairs by 0.05 cm⁻¹ and gives the wrong rotational symmetry number in the thermochemistry.

Full analysis, GaussView views and conclusions: [Ex. 3 README](ex3-ammonia-frequencies/).

---

## Ex. 4 — HF vs B3LYP geometries

H₂O₂ (6-31G*), HCN (6-311G*) and HCCH (6-31G*) are optimised with Hartree–Fock and with the B3LYP functional, from identical inputs that differ only in the method.

![HF vs B3LYP: error against experiment](figures/hf_vs_b3lyp.png)

- **HF shortens bonds between heavy atoms**, most where there are lone pairs or multiple bonds: O–O by 0.056 Å, C≡N by 0.026 Å.
- **B3LYP brings both within 0.005 Å of experiment**, and the H–O–O angle from +2.1° to −0.3°.
- **The H–O–O–H dihedral defeats both methods** (+4.5° and +7.0°): the torsional surface is very flat, and the experimental value is a vibrational average.
- **Acetylene came out bent.** The Z-matrix defines the second H relative to a dummy atom that sits on the first carbon, so the C–C–H angle stayed at about 130°. The diagnosis, the corrected Z-matrix and the lesson are in the exercise README; the corrected run is pending.

Full table and conclusions: [Ex. 4 README](ex4-hf-vs-b3lyp/).

---

## Ex. 5 — Conformers of 1,2-dichloroethane

A relaxed scan of the Cl–C–C–Cl dihedral from 180° to −20°: at each angle every other coordinate is optimised. The Z-matrix places each H relative to the Cl of its own carbon, so a single variable rotates a whole CH₂Cl group.

![Torsional profile of 1,2-dichloroethane](figures/dce_torsion.png)

- **Trans is the global minimum, gauche a local one** near 70°, about 2 kcal/mol higher.
- **Two kinds of barrier:** 5.1 kcal/mol with Cl eclipsing H (120°), 10.0 kcal/mol with the two Cl atoms eclipsed (0°).
- **The molecule makes room as the Cl atoms approach:** the C–C bond stretches from 1.516 to 1.547 Å and the C–C–Cl angle opens from 109° to 117°.
- **Half a turn is enough:** E(φ) = E(−φ), and the extra point at −20° matches +20° to 0.0002 kcal/mol.

Z-matrix design, full table and conclusions: [Ex. 5 README](ex5-dichloroethane-scan/).

---

## Reproducing everything

On a machine with Gaussian 09 (`g09` in the `PATH`):

```bash
cd ex1-optimized-geometries && ./generate.sh && ./extract.sh > results.txt && cd ..
cd ex2-vibrational-frequencies && ../run.sh && cd ..   # frequencies read by hand into frequencies.txt
cd ex3-ammonia-frequencies && ../run.sh && cd ..       # modes read by hand into frequencies.txt, normal_modes.txt
cd ex4-hf-vs-b3lyp && ./generate.sh && ./extract.sh > results.txt && cd ..
cd ex5-dichloroethane-scan && ../run.sh && cd ..        # scan points read from the output into scan.txt
python plot_figures.py   # numpy + matplotlib
```

[`run.sh`](run.sh) is the same launcher as in Session 02: it runs every input in a folder and skips the jobs that already finished normally.

Gaussian output files (`.log`, `.chk`) are not stored. Everything the analysis needs is in the extracted data files.
