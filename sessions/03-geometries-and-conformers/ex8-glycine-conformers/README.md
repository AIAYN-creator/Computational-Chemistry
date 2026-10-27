# Ex. 8 — Conformers of glycine

[← Session 03](../) · [Bash guide](../../../docs/bash-for-gaussian.md)

## Task

Optimise the four lowest-energy conformers of neutral glycine (A, B, C and D) at the HF/6-31G\* and B3LYP/6-31G\* levels, confirm that they are true minima, report their dipole moments, and compute their free energies and populations at 298 K.

## Approach

### One Z-matrix, four conformers

The practical session gives only drawings of the four structures, not the inputs, so the Z-matrix had to be built from the drawings (with the help of an AI assistant; building one unaided is on the list for next time). The four conformers share it and differ in three dihedrals:

| Conformer | N–C–C=O (`zncco`) | C–C–O–H (`zccoh`) | H–N–C–C (`zhn`) | Feature |
|---|---|---|---|---|
| A | 0 | 180 | 60 | C=O on the N side, NH₂ hydrogens towards C=O |
| B | 180 | 0 | 120 | OH hydrogen towards N (OH···N hydrogen bond) |
| C | 180 | 180 | 60 | OH on the N side, its H pointing away |
| D | 0 | 180 | 120 | as A, with the NH₂ group rotated |

The first inputs **imposed planar (Cs) symmetry**: the hydroxyl O fixed at 180° in the carboxyl plane, and the CH₂ and NH₂ hydrogens tied in mirror pairs. A minus sign in front of a variable uses it with the opposite sign, so one variable places both hydrogens of a pair ([`gly_A_hf.com`](gly_A_hf.com)):

```
H 2 rch 3 ahcc 1 zh       CH2 hydrogens: +zh and -zh, mirror images
H 2 rch 3 ahcc 1 -zh        through the plane of the heavy atoms
H 1 rnh 2 ahnc 3 zhn      NH2 hydrogens: +zhn and -zhn
H 1 rnh 2 ahnc 3 -zhn
```

Only A was written by hand. B, C and D came from it with `sed`, changing the three dihedrals (`s/^zncco .*/zncco 180./`), and the four B3LYP inputs from the HF ones (`s/#hf/#b3lyp/`). These were one-off commands in the terminal, so there is no script for them. Every job is `opt=z-matrix freq`.

## Planar B and D are saddle points

The frequency check, part of the task, showed that the planar structures are **not all minima**:

| | HF lowest freq. (cm⁻¹) | B3LYP lowest freq. (cm⁻¹) | |
|---|---|---|---|
| A | 83 | 56 | minimum |
| B (planar) | **−112** | **−88** | saddle point |
| C | 18 | 32 | minimum |
| D (planar) | **−278** | **−267** | saddle point |

**Why the optimiser stopped there.** The imposed symmetry only let it explore planar geometries. And even without the constraint, a perfectly symmetric starting point feels symmetric forces, so it never leaves the plane by itself. Imposing symmetry is convenient (fewer variables, faster jobs, and it matches the drawn structures), but it has to be checked with frequencies.

**Reading the imaginary mode.** Before fixing anything, the imaginary mode of planar D (−278 cm⁻¹) showed *what* wants to move:

- The molecule lies in the XY plane: in the third mode, which is in-plane, every atom has Z = 0.
- The reduced mass is 1.05 amu, so almost only hydrogens move.
- The skeleton barely moves (displacements ≤ 0.05), while the two NH₂ hydrogens carry the large ones (0.45).
- Both NH₂ hydrogens have the **same** out-of-plane (Z) component and **opposite** in-plane components: a **rotation of the NH₂ group about the C–N bond**, not an umbrella inversion.

**The fix.** No scan is needed, and nothing has to be forced: the constraint is *released*. The paired hydrogens get independent variables (`zh2`, `zhn2`), and the starting geometry is nudged out of the plane by 15° in `zncco` (and 10° in `zhn2`). Without the nudge, a symmetric geometry would stay planar anyway. The new inputs are the `*_c1.com` files. All four re-optimised structures are true minima, with all frequencies real.

**Same conformer or a different one?** From a saddle point, the optimiser can slide into *another* conformer (the suspicion was that D would end up as A). Energies and geometries show it did not:

- **D_c1 is not A:** it is 2.2 kcal/mol higher, the skeleton is twisted by 19° (`zncco` ≈ 19), and the NH₂ hydrogens are no longer symmetric (HF: `zhn` ≈ 194, `zhn2` ≈ −46).
- **B_c1 is not C:** it keeps the OH pointing at N (`zccoh` ≈ 1.5°, so the OH···N hydrogen bond survives), and the skeleton twists by only 13–17° (`zncco` ≈ 163–167).

**Two very different saddle points.** Energy of the planar structure above the non-planar minimum:

| | HF | B3LYP | Meaning |
|---|---|---|---|
| B planar → B_c1 | 0.25 kcal/mol | 0.10 kcal/mol | tiny barrier: B is *almost* planar |
| D planar → D_c1 | 3.4 kcal/mol | 3.5 kcal/mol | real barrier: planar D is not a conformer |

Planar B is the transition state between two mirror-image minima, twisted slightly to either side. The barrier is about the size of the zero-point energy of the lowest vibration of B_c1 (91–98 cm⁻¹, so ½hν ≈ 0.13–0.14 kcal/mol): at the B3LYP level it is already below it, and at HF it is about twice as large. So the molecule oscillates between both sides, and its average structure is effectively planar: a small double well, like the umbrella inversion of NH₃ in [Ex. 3](../ex3-ammonia-frequencies/). Planar D, instead, lies clearly above the real minimum: the NH₂ group rotates and the skeleton twists, and the real D is a C1 structure.

## Energies, dipoles and populations (298 K)

![Glycine conformers: free energies, populations and saddle points](../figures/glycine_conformers.png)

Relative to A, using the true minima (B_c1 and D_c1):

| | ΔE HF | ΔG HF | Pop. HF | ΔE B3LYP | ΔG B3LYP | Pop. B3LYP | μ HF / B3LYP (D) |
|---|---|---|---|---|---|---|---|
| **A** | 0.00 | 0.00 | 83 % | 0.00 | 0.00 | 77 % | 1.33 / 1.26 |
| **B** | 2.97 | 3.54 | 0.4 % | 0.71 | 1.49 | 13 % | 5.69 / 5.59 |
| **C** | 1.90 | 1.13 | 12 % | 1.65 | 1.44 | 7 % | 2.04 / 1.92 |
| **D** | 2.20 | 2.13 | 5 % | 2.27 | 2.25 | 3.5 % | 2.34 / 2.05 |

Energies in kcal/mol. Populations from Boltzmann factors exp(−ΔG/RT), with a **degeneracy of 2 for B and D**: being C1, each exists as two mirror-image structures of equal energy (the same factor 2 as the two gauche conformers of 1,2-dichloroethane in [Ex. 6](../ex6-conformer-thermochemistry/)). A and C are planar and count once. Data: [`glycine.txt`](glycine.txt).

## Conclusions

1. **Imposed symmetry hides saddle points.** The planar B and D structures have one imaginary frequency each. Removing the symmetry constraint and nudging the geometry out of the plane leads to true, non-planar (C1) minima that are still B and D, not other conformers.
2. **Not all saddle points are equal.** For B the planar structure lies only 0.1–0.25 kcal/mol above the minimum, so B is effectively planar; for D the gap is 3.4 kcal/mol, so the planar D drawn in the session is not a conformer at these levels.
3. **A dominates** with both methods (about 80 %). The degeneracy factor of 2 for the C1 conformers matters: without it, B at the B3LYP level would drop from 13 % to 7 %.
4. **HF vs B3LYP: the hydrogen bond needs correlation.** Conformer B, the only one with an intramolecular OH···N hydrogen bond, lies 3.0 kcal/mol above A with HF and is almost unpopulated, but only 0.7 kcal/mol above with B3LYP, where it becomes the second most populated. HF, without electron correlation, underestimates this interaction: the same lesson as the gauche effect in 1,2-dichloroethane.
5. **Dipole moments** range from 1.3 D (A) to 5.6 D (B). B is by far the most polar, so a polar solvent would stabilise it further, a point to revisit when solvent models appear in later sessions.
6. **Thermal corrections matter more here than in 1,2-dichloroethane:** for C at the HF level, ΔG (1.13) differs from ΔE (1.90) by almost 0.8 kcal/mol.

## How it went

The most instructive part of the exercise was the chain of errors before the first good calculation. Each one had a different symptom and a different way to diagnose it:

| # | Symptom | Cause | How it was found | Lesson |
|---|---|---|---|---|
| 1 | 8 × `: No such file or directory` | The loop defined `d` (`for d in ...`) but used `$f` | The file name appeared **empty** before the colon | The loop variable and the one in the body must match |
| 2 | 8 × `segmentation violation`, instantly | A missing atom, the second NH₂ hydrogen: with 39 electrons (odd), a singlet `0 1` is impossible | `cat -A` of the input: the Z-matrix ended at the first NH₂ hydrogen | Count the atoms before launching; an instant segfault usually means an invalid input |
| 3 | The prompt turns into `>` and nothing happens | An unclosed quote in `"${f%.com}.log ]` | `>` is Bash's **continuation** prompt: it is waiting for the rest of the command | Ctrl+C to get out; check quotes and brackets |
| 4 | Segfault again, only for B, C and D | A typo in the `sed`: `znncco` instead of `zncco` | Running **one job in the foreground** and reading its `.log`: `Symbol "znncco" not found in Z-matrix` | When a batch fails, isolate one case and read its `.log` |
| 5 | (no symptom) D with `zncco 180` | A typo while generating D | Checking the values with `grep -H` against the table of dihedrals | Check generated inputs before launching them, not after |
| 6 | Only 16 of the 24 expected lines | A typo in the checking `grep`: `zcooh` instead of `zccoh` | Counting the output lines | The check can have typos too |
| 7 | `No such file` when looking for the `_c1.log` | Launched with `> "${f%.com}"`, without `.log`: outputs with no extension | `ls gly_*_c1*` | Check the output redirection; rename with `mv` instead of recalculating |

The missing atom only gave a segfault in the background loop: once fixed, A run **alone, in the foreground**, ended with `Normal termination` in 7 seconds. From then on the rule was: **test one job in the foreground before launching the batch.**

The first version of the extraction script also had four typos, each of which would have broken something different: a stray `_` in the glob (no files found), `awll` for `awk` (empty dipole column), `znnco` for `zncco` (empty dihedral column), and a forgotten `$g` in the `echo` (every column shifted, no G). `bash -n` catches syntax errors but not typos inside patterns; for those, the best check is the resulting table: look for empty or shifted columns. The debugging habits are collected in the [Bash guide](../../../docs/bash-for-gaussian.md#11-when-a-batch-fails).

## Scripts

[`extract.sh`](extract.sh) reads E, G, the dipole and the key dihedrals of the twelve outputs into `glycine.txt`. The planar jobs have no `zhn2`, so `${z4:--}` writes a `-` to keep the columns aligned. Patterns: [pulling one number out of a log](../../../docs/bash-for-gaussian.md#2-pulling-one-number-out-of-a-log), [default values](../../../docs/bash-for-gaussian.md#9-splitting-file-names-and-default-values).

## Files

| File | What it is |
|---|---|
| [`gly_A_hf.com`](gly_A_hf.com), `gly_[BCD]_hf.com`, `gly_[ABCD]_b3lyp.com` | Planar (Cs) inputs, `opt freq`; only `gly_A_hf.com` was written by hand |
| `gly_[BD]_hf_c1.com`, `gly_[BD]_b3lyp_c1.com` | Re-optimisations of B and D without symmetry, nudged out of the plane |
| [`extract.sh`](extract.sh) | Writes E, G, μ and the key dihedrals of all twelve calculations to `glycine.txt` |
| [`glycine.txt`](glycine.txt) | Output of `extract.sh` |

The relative energies, populations and the figure are computed by [`plot_figures.py`](../plot_figures.py).
