# Ex. 4 — 1,2-Dichloroethane in water

[← Session 07](../) · [Session 03 report](../../03-geometries-and-conformers/report/)

## Task

Recompute the trans–gauche equilibrium of 1,2-dichloroethane with an implicit model of water, and compare it with the gas phase. This is the test that conclusion 4 of the [Session 03 report](../../03-geometries-and-conformers/report/) left open: *"a polar solvent is expected to stabilise gauche and shift the equilibrium"*.

## Prediction, before calculating

1. **Water should stabilise gauche more.** Gauche has a permanent dipole moment (3.14 D at HF/6-31G\*), and trans has none: its centre of inversion cancels the two C–Cl dipoles.
2. **So the gauche population should rise.**
3. **The effect should be smaller than in the SN2 reaction**, because these are dipoles, not ions. The solvation of an ion goes as −q²/r (Born), tens of kcal/mol for F⁻; that of a dipole goes as −μ²/a³ (Onsager), a few kcal/mol. But K depends exponentially on ΔG, so a small change in ΔG can still move the populations a lot.

## Approach

The Session 03 inputs at HF/6-31G\*, with a new route line ([`dce_trans_water.com`](dce_trans_water.com), [`dce_gauche_water.com`](dce_gauche_water.com)):

```
#HF/6-31G* opt=(z-matrix,maxcycles=200) freq scrf=(SMD,solvent=water)
```

- **SMD** (*Solvation Model based on Density*) is a continuum model like PCM, but besides the electrostatic term it includes the non-electrostatic ones: the cost of opening the cavity, dispersion with the solvent and its reorganisation. It is parametrised to give realistic free energies of solvation.
- **`maxcycles=200`** allows more optimisation steps, since in solution the surface is flatter.

Both jobs end with two `Normal termination` lines (`opt`, then `freq`) and have no imaginary frequencies. The values were read from the outputs with `grep` and the equilibrium was worked out in a spreadsheet; they are collected in [`thermo.txt`](thermo.txt), with the gas-phase rows of [Session 03, Ex. 6](../../03-geometries-and-conformers/ex6-conformer-thermochemistry/).

## Results

| Gauche − trans, 298 K | Gas phase | Water (SMD) |
|---|---|---|
| ΔE (kcal/mol) | 1.91 | 0.37 |
| ΔH (kcal/mol) | 1.79 | 0.20 |
| ΔG (kcal/mol) | 1.85 | **0.23** |
| K = 2 exp(−ΔG/RT) | 0.088 | **1.37** |
| Gauche (%) | 8.1 | **57.7** |
| Dipole of gauche (D) | 3.14 | 4.39 |

The population follows from K = [gauche]/[trans] and x(gauche) + x(trans) = 1: x(gauche) = K/(1 + K).

**Water turns the equilibrium around: gauche becomes the majority.** ΔG changes by only 1.6 kcal/mol, but K is exponential, and it goes from 0.088 to 1.37. The dipole of gauche also grows from 3.14 to 4.39 D: the solvent polarises the molecule, which in turn interacts more strongly with the solvent.

## The factor 2

The formula given in class, K = exp(−ΔG/RT), has no factor 2. It has to be there: there are two gauche conformers, mirror images of each other, with the same energy.

| | Gauche with the 2 | Gauche without it | Absolute error |
|---|---|---|---|
| Gas phase | 8.1 % | 4.2 % | −3.9 points |
| Water | 57.7 % | 40.6 % | **−17.1 points** |

- **In K the error is always −50 %**, which says little.
- **In the population it changes the conclusion.** With the 2, gauche is the majority in water (58 %); without it, the minority (41 %).
- **As an energy:** 2 exp(−ΔG/RT) = exp(−(ΔG − RT ln 2)/RT), so the factor 2 is worth RT ln 2 = 0.41 kcal/mol. The effective ΔG is +1.44 kcal/mol in the gas phase (trans dominates) and −0.18 kcal/mol in water (gauche dominates). Physically, it is the entropy of mixing two degenerate states, R ln 2.

## The symmetry number, a second R ln 2

The rotational partition function is divided by the **symmetry number σ**, the number of orientations of the molecule that rotation cannot tell apart. It enters the entropy as −R ln σ, so a σ that is wrong makes G wrong by RT ln σ: 0.41 kcal/mol for σ = 2, 0.65 for σ = 3.

Trans is C₂ₕ and gauche C₂, so both should have σ = 2. Here the Z-matrix gives every H its own variable, the optimised geometry is only *almost* symmetric, and Gaussian takes both as C₁, σ = 1:

```bash
grep "Rotational symmetry number" *.log    # 1. in both
grep "Full point group" *.log | tail -2    # C1 in both
```

**ΔG is still right,** because the same error appears in both conformers and cancels in the difference. The problem appears when Gaussian detects the symmetry in one structure and not in the other, which is exactly what happened to the [SN2 transition state of Session 04](../../04-sn2-reaction/ex4-transition-state/#a-symmetry-number-gaussian-missed).

The two corrections are different things and must not be confused: σ is applied by Gaussian, when it detects the point group; the degeneracy of the two gauche conformers is not, and has to be added by hand.

## How it went

- **Typos in file names** (`dce_trasns`): the Tab key completes names and avoids them.
- **`grep "Normal termination"` on the `.com` files** found nothing, of course: inputs never contain it. It belongs on the `.log` files.

## Files

| File | What it is |
|---|---|
| [`dce_trans_water.com`](dce_trans_water.com), [`dce_gauche_water.com`](dce_gauche_water.com) | `opt freq` of each conformer in water (SMD) |
| [`thermo.txt`](thermo.txt) | Dihedral, E, H, G (hartree), dipole (D) and σ of both conformers, in the gas phase and in water, copied from the outputs |
