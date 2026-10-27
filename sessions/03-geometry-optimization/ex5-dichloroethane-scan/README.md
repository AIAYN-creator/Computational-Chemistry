# Ex. 5 — Conformers of 1,2-dichloroethane

[← Session 03](../) · [Bash guide](../../../docs/bash-for-gaussian.md) · **[Case study and report](../report/)**

This exercise and [Ex. 6](../ex6-conformer-thermochemistry/) are written up together in the [Session 03 report](../report/).

## Task

Compute the energy of 1,2-dichloroethane (ClCH₂–CH₂Cl) as a function of the Cl–C–C–Cl dihedral angle at HF/6-31G*, identify its conformers (minima and maxima of the rotation about the C–C bond) and explain the energy differences between them.

## Approach

### A Z-matrix built for the rotation

The whole exercise rests on the Z-matrix: it has to let a *single* variable rotate one CH₂Cl group relative to the other, while every other coordinate stays free to relax. [`dce_scan.com`](dce_scan.com):

```
C                         C1
C  1 r1                   C2, bonded to C1
Cl 1 r2 2 a2              Cl on C1
Cl 2 r3 1 a3 3 z3         Cl on C2; z3 = dihedral Cl-C-C-Cl, the scanned variable
H  1 r4 2 a4 3 z4         H atoms on C1, placed by their dihedral
H  1 r5 2 a5 3 z5           relative to the Cl of their OWN carbon (atom 3)
H  2 r6 1 a6 4 z6         H atoms on C2, placed relative to
H  2 r7 1 a7 4 z7           the Cl of THEIR own carbon (atom 4)

...
z3 180.0 S 10 -20.0       start at 180, 10 steps of -20: 11 points, 180 -> -20
z4 120.0                  the two H atoms of each carbon start at 120 and 240
z5 240.0                    degrees from their Cl around the C-C axis
z6 120.0
z7 240.0
```

The key decision is in the last four lines of the geometry. Each H is placed by a dihedral measured from the Cl **on its own carbon**, not from the other end of the molecule. Each CH₂Cl group is therefore defined relative to its own Cl, so changing `z3` turns the whole group on C2 as a unit, with its hydrogens following its chlorine. If the H atoms on C2 were referenced to the Cl on C1 instead, scanning `z3` would move the Cl alone and leave its hydrogens behind.

The dihedrals are called `z`, not `d`, on purpose: Gaussian reads numbers in Fortran format, where `D` marks an exponent (`1.0D3`), and a variable name starting with `d` can confuse the parser.

The output confirms that this works: along the whole scan, `z4`–`z7` stay between 117° and 122° or between 238° and 243°. The CH₂Cl groups keep their shape while they rotate.

### A relaxed scan

The scan is requested inside the Z-matrix: `S 10 -20.0` after the value of `z3`, together with `opt=z-matrix` in the route line. At each of the 11 values of the dihedral, Gaussian **optimises every other variable** (bond lengths, angles, and the H dihedrals `z4`–`z7`). Each point is a true constrained minimum, and all 11 report "Stationary point found". This is different from the rigid scans of [Session 02, Ex. 3](../../02-hartree-fock/ex3-bond-scans/), where only the scanned distance changed.

The relaxation is not cosmetic. As the two Cl atoms are forced towards each other, the molecule makes room:

| φ | r(C–C) (Å) | ∠C–C–Cl (°) |
|---|---|---|
| 180° (trans) | 1.516 | 109.4 |
| 120° | 1.533 | 112.1 |
| 0° (Cl/Cl eclipsed) | 1.547 | 117.4 |

### Half a turn is enough

The scan runs from 180° to −20°. A rotation and its mirror image have the same energy, E(φ) = E(−φ), so the points from 0° to 180° determine the whole curve. The extra point at −20° checks that symmetry: it matches +20° to 0.0002 kcal/mol.

## Results

![Torsional profile of 1,2-dichloroethane with Newman projections of the key conformers](../figures/dce_torsion.png)

| φ | ΔE (kcal/mol) | Conformer |
|---|---|---|
| 180° | 0.00 | **trans** (anti), global minimum |
| 160° | 1.23 | |
| 140° | 3.74 | |
| 120° | 5.05 | Cl/H eclipsed, maximum |
| 100° | 4.00 | |
| 80° | 2.22 | near the gauche minimum |
| 60° | 2.32 | near the gauche minimum |
| 40° | 5.06 | |
| 20° | 8.46 | |
| 0° | 9.98 | **Cl/Cl eclipsed**, global maximum |
| −20° | 8.46 | symmetry check |

The gauche minimum falls between two scan points. A cosine-series fit through the computed points (the smooth curve, 0.003 kcal/mol from every point) places it at **φ ≈ 70°, ΔE ≈ 1.9 kcal/mol**. Other fits, and parabolas through the three lowest points, all give 69–71° and 1.9–2.0 kcal/mol. It is an interpolated estimate, and [Ex. 6](../ex6-conformer-thermochemistry/) confirms it: the unconstrained optimisation lands at 70.5° and 1.912 kcal/mol.

**Validation.** The scan energies match the reference table of the practical session to the fifth decimal. They also coincide, to within 10⁻⁵ hartree, with the HF/6-31G* values published by Wiberg and Murcko (*J. Phys. Chem.* **1987**, 91, 3616): −997.03094, −997.02288 and −997.01503 hartree at 180°, 120° and 0°, and −997.02789 hartree for the optimised gauche minimum.

## Conclusions

1. **Two minima.** The potential energy curve for rotation about the C–C bond has a global minimum at 180° (the **trans** conformer) and a local minimum between 60° and 80° (the **gauche** conformer), about 2.2 kcal/mol higher in energy at the scan points.

2. **Two types of maxima.** The maximum at 120° (5.1 kcal/mol) is an eclipsed conformation in which each Cl eclipses an H. The absolute maximum at 0° (10.0 kcal/mol) is the **eclipsed** conformation with the two Cl atoms facing each other.

3. **Origin of the energy differences.** The trans conformer is the most stable because the two bulky, electronegative Cl atoms are as far apart as possible, which minimises both the steric and the dipole–dipole repulsion between the C–Cl bonds. In the gauche conformer the Cl atoms are closer, which raises the energy. The Cl/Cl eclipsed conformation maximises this repulsion.

4. **Symmetry check.** The energies at −20° and +20° are identical, as expected from the symmetry of the rotation, and the computed curve reproduces the reference values (see *Validation* above).

## Data

The scan summary table that Gaussian prints at the end gives the energies with only five decimals, and runs the columns together. [`extract.sh`](extract.sh) takes them from somewhere else, with a one-line `awk` program: it keeps overwriting a variable with every `SCF Done` energy, and prints the one it holds each time a point converges (`Stationary point found`). The dihedral of the n-th converged point is 200 − 20n.

```bash
awk '/SCF Done/ {e=$5} /Stationary point found/ {n++; print 200-20*n, e}' dce_scan.log > scan.txt
```

Pattern: [remembering the last value until a trigger](../../../docs/bash-for-gaussian.md#3-reading-a-table-of-any-length-with-awk).

## Files

| File | What it is |
|---|---|
| [`dce_scan.com`](dce_scan.com) | Relaxed scan of the Cl–C–C–Cl dihedral, HF/6-31G* |
| [`extract.sh`](extract.sh) | Writes dihedral and energy of every converged point to `scan.txt` |
| [`scan.txt`](scan.txt) | Output of `extract.sh` |
| [`scan_geometry.txt`](scan_geometry.txt) | Optimised C–C distance, C–C–Cl angle and H dihedrals at each point, copied from the output |

The figure, the cosine-series fit and the Newman projections are drawn by [`plot_figures.py`](../plot_figures.py).
