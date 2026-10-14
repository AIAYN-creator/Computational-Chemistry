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

### `generate.sh` — build the inputs and run them

```bash
for mol in h2 hf co n2 ch4 h2o; do
	for b in 3-21G 4-31G "6-31G(d)" "6-31G(d,p)"; do
		n=$(echo "$b" | tr -d '(),-' | tr 'A-Z' 'a-z')    # "6-31G(d,p)" -> "631gdp"
		sed "s#STO-3G#$b#g" "${mol}_sto3g.com" > "${mol}_${n}.com"
	done
done

../run.sh    # launch every .com, skipping finished jobs
```

The basis name has to become part of a file name, so `tr` removes the characters that would cause trouble (`(`, `)`, `,`, `-`) and lowercases the rest. The `sed` replacement also changes the title line, so every output says which basis it used.

### `extract.sh` — one row per output

```bash
E=$(grep "SCF Done" "$f" | tail -1 | awk '{print $5}')
homo=$(grep "occ. eigenvalues" "$f" | tail -1 | awk '{print $NF}')
mu=$(grep -A 1 "Dipole moment" "$f" | tail -1 | awk '{print $NF}')
q1=$(grep -A 2 "Mulliken charges:" "$f" | tail -1 | awk '{print $3}')
```

Each property is found by a line of text that always comes with it, and then picked by its position on that line. The HOMO is the **last number of the last line** of occupied eigenvalues, because Gaussian prints them in ascending order. The [Bash guide](../../../docs/bash-for-gaussian.md#2-pulling-one-number-out-of-a-log) shows the real output lines each command reads.

## Files

| File | What it is |
|---|---|
| `*_sto3g.com` | The six hand-written inputs, used as templates |
| [`generate.sh`](generate.sh) | Builds the other 24 inputs and runs all 30 |
| [`extract.sh`](extract.sh) | Collects E, HOMO, μ and Mulliken charges of the first two atoms |
| [`results.txt`](results.txt) | Output of `extract.sh` |
