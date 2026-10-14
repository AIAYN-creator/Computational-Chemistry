# Ex. 2 — How the basis set changes the answer

[← Session 02](../) · [Bash guide](../../../docs/bash-for-gaussian.md)

## Task

Run Hartree–Fock single-point calculations on six small molecules (H₂, HF, CO, N₂, CH₄ and H₂O) with five basis sets of increasing size: STO-3G, 3-21G, 4-31G, 6-31G(d) and 6-31G(d,p). For each one, collect the total energy, the HOMO energy, the dipole moment and the Mulliken charges, and see how each property responds to the basis.

## Approach

**30 calculations that differ in one word.** Six molecules times five basis sets gives 30 inputs, and the only thing that changes between the inputs of one molecule is the basis keyword. Writing them by hand invites typos, and a typo in a geometry would ruin the comparison without anyone noticing. So only the six STO-3G inputs are written by hand. [`generate.sh`](generate.sh) copies each one with `sed`, swapping the basis name, and the geometry is guaranteed identical across the series. If the energy changes, it is because of the basis.

**Fixed geometries, not optimised.** Every molecule sits at a fixed, near-experimental geometry, written as a Z-matrix:

| Molecule | Geometry |
|---|---|
| H₂ | r = 0.74 Å |
| HF | r = 0.92 Å |
| CO | r = 1.128 Å |
| N₂ | r = 1.098 Å |
| CH₄ | r(C–H) = 1.09 Å, tetrahedral (109.47°) |
| H₂O | r(O–H) = 0.96 Å, ∠HOH = 104.5° |

The question is about the basis, not the geometry. Optimising each molecule with each basis would mix two effects in the same number.

**One table, one row per output.** [`extract.sh`](extract.sh) reads every `.log` and prints a single row with the five numbers of interest. The result, [`results.txt`](results.txt), is the whole exercise in one file.

## Results and reading

Energies and the figure are in the [session README](../#ex-2--how-the-basis-set-changes-the-answer). The main points:

- **Variational principle at work.** The energy can only go down as the basis grows, and it does in every molecule. Most of the gain comes from leaving the minimal STO-3G basis.
- **Identical energies are a feature, not a bug.** H₂ gives the same energy with 4-31G and 6-31G(d): hydrogen gets the same 31G functions in both, and `(d)` only polarises heavy atoms. CO and N₂ give the same energy with 6-31G(d) and 6-31G(d,p): the `p` only polarises hydrogen, and they have none. Checking the definition of the basis explains what looks like an error.
- **HOMO energies converge fast.** For H₂O the HOMO goes from −0.391 hartree (STO-3G) to −0.479 (3-21G) and then stays within 0.02 hartree. Through Koopmans' theorem, −ε<sub>HOMO</sub> is an estimate of the ionisation energy, and a minimal basis is not good enough for it.
- **Mulliken charges depend strongly on the basis.** The charge on O in H₂O jumps between −0.36 and −0.87, while the dipole moment, which is a real observable, stays at 2.2 D once polarisation functions are included. Mulliken charges are a partition of the density, and they inherit the arbitrariness of the basis.

## Scripts

Both scripts are commented line by line.

- [`generate.sh`](generate.sh) turns each STO-3G template into the other four basis sets with `sed`, then launches all 30 jobs. Pattern: [generating inputs from a template](../../../docs/bash-for-gaussian.md#5-generating-inputs-from-a-template).
- [`extract.sh`](extract.sh) writes one row per output: energy, HOMO, dipole and two Mulliken charges, each found by a fixed piece of text and picked by its position on the line. Pattern: [pulling one number out of a log](../../../docs/bash-for-gaussian.md#2-pulling-one-number-out-of-a-log), which shows the real Gaussian line behind every command.

## Files

| File | What it is |
|---|---|
| `*_sto3g.com` | The six hand-written inputs, used as templates |
| [`generate.sh`](generate.sh) | Builds the other 24 inputs and runs all 30 |
| [`extract.sh`](extract.sh) | Collects E, HOMO, μ and Mulliken charges of the first two atoms |
| [`results.txt`](results.txt) | Output of `extract.sh` |
