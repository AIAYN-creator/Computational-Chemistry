# Ex. 1 — Optimised geometries and the basis set

[← Session 03](../) · [Bash guide](../../../docs/bash-for-gaussian.md)

## Task

Optimise the geometry of CH₄, H₂O, HF and NH₃ at the Hartree–Fock level with four basis sets: STO-3G, 3-21G, 6-31G* and 6-31G**. For each one, report the bond length, the bond angle and the dipole moment, and compare them with experiment.

## Approach

**Let the symmetry do part of the work.** Each molecule is written as a Z-matrix in which equivalent bonds and angles share one variable: the four C–H bonds of methane are all `r1`, the two O–H bonds of water are both `r1`, and so on. With `opt=z-matrix`, Gaussian optimises those variables directly. The molecule keeps its symmetry, and the optimiser has only one to three numbers to find instead of 3N − 6 coordinates.

| Molecule | Variables | Starting values |
|---|---|---|
| CH₄ | r1, a2, z3 | 1.30 Å, 109.5°, 120° |
| H₂O | r1, a2 | 0.96 Å, **90°** |
| HF | r1 | 0.984 Å |
| NH₃ | r1, a2, z3 | 1.07 Å, 107°, 100° |

**Start away from the answer.** Some starting points are deliberately off: water starts at 90°, 15° away from its real angle, and methane at 1.30 Å, 0.2 Å too long. A good optimiser should not care. Every job converged in two to six geometry steps, the 90° water included.

**One more check for NH₃.** Its Z-matrix fixes two H–N–H angles to `a2`, but the third one depends on the dihedral `z3`, so C₃ᵥ symmetry is not built in. The third angle can be computed from a2 and z3, and it matches a2 to within 0.05° in every basis set: the optimiser found the symmetric pyramid on its own.

| NH₃ | STO-3G | 3-21G | 6-31G* | 6-31G** |
|---|---|---|---|---|
| ∠H₂NH₃ = a2 | 104.19° | 112.36° | 107.17° | 107.61° |
| ∠H₃NH₄ from a2 and z3 | 104.18° | 112.40° | 107.17° | 107.62° |

**Same template trick as Session 02.** Only the STO-3G inputs are written by hand, and [`generate.sh`](generate.sh) builds the other twelve. This time the loop runs over short file-name tags (`631gs`), and a `case` statement maps each one to the name Gaussian expects (`6-31G*`), because `*` is awkward in a file name.

## Results

| | Basis | r (Å) | Angle (°) | μ (D) | E (hartree) | Steps |
|---|---|---|---|---|---|---|
| **CH₄** | STO-3G | 1.0830 | 109.47 | 0 | −39.72686 | 4 |
| | 3-21G | 1.0829 | 109.47 | 0 | −39.97688 | 4 |
| | 6-31G* | 1.0837 | 109.47 | 0 | −40.19517 | 4 |
| | 6-31G** | 1.0835 | 109.47 | 0 | −40.20170 | 4 |
| | *Exp.* | *1.087* | *109.47* | *0* | | |
| **H₂O** | STO-3G | 0.9894 | 100.03 | 1.71 | −74.96590 | 5 |
| | 3-21G | 0.9667 | 107.65 | 2.39 | −75.58596 | 4 |
| | 6-31G* | 0.9473 | 105.50 | 2.20 | −76.01075 | 4 |
| | 6-31G** | 0.9431 | 105.96 | 2.15 | −76.02362 | 4 |
| | *Exp.* | *0.958* | *104.5* | *1.86* | | |
| **HF** | STO-3G | 0.9555 | – | 1.25 | −98.57285 | 3 |
| | 3-21G | 0.9372 | – | 2.17 | −99.46022 | 2 |
| | 6-31G* | 0.9110 | – | 1.97 | −100.00291 | 3 |
| | 6-31G** | 0.9006 | – | 1.94 | −100.01169 | 3 |
| | *Exp.* | *0.917* | – | *1.83* | | |
| **NH₃** | STO-3G | 1.0324 | 104.19 | 1.88 | −55.45542 | 6 |
| | 3-21G | 1.0025 | 112.36 | 1.75 | −55.87220 | 6 |
| | 6-31G* | 1.0026 | 107.17 | 1.92 | −56.18436 | 5 |
| | 6-31G** | 1.0008 | 107.61 | 1.84 | −56.19554 | 6 |
| | *Exp.* | *1.012* | *106.7* | *1.47* | | |

Experimental equilibrium values: NIST CCCBDB. "Steps" is the number of geometries the optimiser visited.

![Error against experiment vs basis set](../figures/error_vs_basis.png)

## Conclusions

### 1. Bond lengths: the basis set converges to the HF limit, not to experiment

- **STO-3G lengthens every polar bond**, by 0.02–0.04 Å.
- **Larger basis sets shorten the bonds until they fall below experiment.** With 6-31G**, the polar bonds are about 0.01–0.02 Å too short.
- **Interpretation:** a better basis set only removes the *basis* error. What remains is the error of the method: Hartree–Fock has no electron correlation, and without it bonds come out too short. When 3-21G looks right in some cases, it is because the two errors cancel, not because the basis is good.
- **CH₄ barely changes** because a nonpolar C–H bond is only weakly sensitive to the basis.

### 2. Bond angles: polarisation functions are the key

- **3-21G overestimates the angles considerably**, and ammonia becomes much flatter (112.4° against 106.7°).
- **The d functions of 6-31G\* bring the angles to within 1° of experiment.** They give the central atom the angular flexibility it needs to describe its lone pairs.
- **Adding p functions on hydrogen (6-31G\*\*) does not improve the angles**, and can even make them slightly worse.
- **CH₄ is not a real test here:** its Z-matrix keeps the four C–H bonds equivalent, and the optimiser only has to settle on the tetrahedral angle (109.47°), starting from 109.5°.

### 3. Dipole moments: HF overestimates them even with polarised basis sets

- **STO-3G gives erratic results:** it underestimates the dipoles of HF and H₂O and overestimates that of NH₃.
- **3-21G overestimates them strongly**, by up to +0.53 D.
- **6-31G\* and 6-31G\*\* still overestimate them.** Doing better would need a larger basis set with diffuse functions, and even then an error would remain, because Hartree–Fock overweights the ionic contribution to the bonds.
- **NH₃ shows that the dipole depends on the geometry:** at 3-21G the molecule is flatter, and its dipole is lower.

### Overall

For simple molecules like these, **6-31G\* is a good compromise between cost and accuracy.** The errors that remain come from Hartree–Fock itself, which is what motivates correlated methods.

## Cross-checks with Session 02

**Two methods, one minimum.** In [Session 02, Ex. 3](../../02-hartree-fock/ex3-bond-scans/), the HF bond length came from a parabola fitted to a scan. Here it comes from an optimiser. They agree to 0.001 Å:

| HF bond, r<sub>e</sub> (Å) | STO-3G | 3-21G | 6-31G** |
|---|---|---|---|
| Scan + parabola (S02 Ex. 3) | 0.956 | 0.938 | 0.901 |
| Optimisation (this exercise) | 0.9555 | 0.9372 | 0.9006 |

**Optimising can only lower the energy.** [Session 02, Ex. 2](../../02-hartree-fock/ex2-basis-sets/) computed the same molecules at fixed, near-experimental geometries. With the same basis set, the optimised energy is lower in every case, from 0.1 to 2.6 mhartree. The largest gains are with STO-3G, whose minimum lies furthest from the experimental geometry (6-31G* and 6-31G** are Gaussian's names for 6-31G(d) and 6-31G(d,p)).

## Scripts

Both scripts are commented line by line.

- [`generate.sh`](generate.sh) builds the twelve non-STO-3G inputs from the templates, using `case` to map file-name tags to basis names, and runs them with the session's [`run.sh`](../run.sh). Patterns: [generating inputs from a template](../../../docs/bash-for-gaussian.md#5-generating-inputs-from-a-template), [mapping names with case](../../../docs/bash-for-gaussian.md#8-mapping-names-with-case).
- [`extract.sh`](extract.sh) reads the final values of the Z-matrix variables from Gaussian's *Optimized Parameters* table, plus dipole, energy and number of steps, and refuses to report a geometry that did not converge. Patterns: [pulling one number out of a log](../../../docs/bash-for-gaussian.md#2-pulling-one-number-out-of-a-log), [splitting names and default values](../../../docs/bash-for-gaussian.md#9-splitting-file-names-and-default-values).

## Files

| File | What it is |
|---|---|
| `*_sto3g.com` | The four hand-written Z-matrix inputs, used as templates |
| [`generate.sh`](generate.sh) | Builds the other twelve inputs and runs all sixteen |
| [`extract.sh`](extract.sh) | One row per output: r, angle, μ, E and steps |
| [`results.txt`](results.txt) | Output of `extract.sh` |
