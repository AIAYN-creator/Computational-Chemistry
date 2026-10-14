# Ex. 3 — Equilibrium bond lengths

[← Session 02](../) · [Bash guide](../../../docs/bash-for-gaussian.md)

## Task

Scan the bond length of H₂ and HF with three basis sets (STO-3G, 3-21G and 6-31G(d,p)), find the equilibrium distance in each case and compare it with the experimental value.

## Approach

**A scan instead of an optimisation.** An optimisation would only return the minimum. A scan returns the shape of the curve around it, which shows how stiff the bond is and how much each basis moves the minimum. For a diatomic molecule the bond length is the only coordinate, so a one-dimensional scan covers everything.

**Reading Gaussian's scan syntax.** In the Z-matrix the bond length becomes a variable, and the `Scan` keyword reads its line as *start, number of steps, step size*:

```
H
H 1 r1

r1 0.6 10 0.03      ← from 0.6 Å, 10 steps of 0.03 Å: 11 points, up to 0.9 Å
```

The window sits around the experimental distance (0.741 Å for H₂, 0.917 Å for HF), from 0.6 to 0.9 Å for H₂ and from 0.8 to 1.1 Å for HF. The 0.03 Å step is a balance: fine enough to place the minimum within a few thousandths of an ångström once a parabola goes through the lowest points, and coarse enough to stay at 11 points per scan.

**Same template trick as in Ex. 2.** Only the STO-3G scans are written by hand, and [`generate.sh`](generate.sh) builds the other two basis sets with `sed`.

**A better "already done?" check.** In Ex. 2 a job was skipped if its `.log` existed. That fails when a job crashes halfway: the `.log` exists but the job never finished, and it would never be re-run. From this exercise on, a job is skipped only if its output contains `Normal termination`. That check now lives in the shared [`run.sh`](../run.sh).

## Results and reading

| r<sub>e</sub> (Å) | STO-3G | 3-21G | 6-31G(d,p) | Exp. |
|---|---|---|---|---|
| H₂ | 0.713 | 0.735 | 0.733 | 0.741 |
| HF | 0.956 | 0.938 | 0.901 | 0.917 |

r<sub>e</sub> comes from a parabola through the three points around each minimum ([`plot_figures.py`](../plot_figures.py)).

- Beyond the minimal basis, HF bond lengths land within about 0.02 Å of experiment. That is why Hartree–Fock geometries are often good enough as a starting point for more expensive methods.
- STO-3G misses in opposite directions: H₂ comes out too short and HF too long. A minimal basis does not err systematically, it just lacks flexibility.
- With 6-31G(d,p) the HF bond becomes *too short*. Near the basis-set limit, Hartree–Fock tends to give bonds that are too short, and electron correlation lengthens them again.

![Bond-length scans](../figures/bond_scans.png)

## Scripts

### `extract.sh` — reading the scan table

At the end of a scan, Gaussian prints a summary table:

```
 Summary of the potential surface scan:
   N      r1          SCF
 ----  ---------  -----------
    1     0.6000     -1.10472
    2     0.6300     -1.11271
  ...
   11     0.9000     -1.10836
 ----  ---------  -----------
```

The first version used `grep -A 13 ... | tail -11`, which only works if the scan has exactly 11 points. The version here reads the table with a small `awk` state machine: it switches on at the title, prints every row that looks like *integer, number, number*, and stops at the first line that doesn't. The same code works for any scan length, and it is reused in Ex. 4–6. The [Bash guide](../../../docs/bash-for-gaussian.md#3-reading-a-table-of-any-length-with-awk) explains it line by line.

## Files

| File | What it is |
|---|---|
| `h2scan_sto3g.com`, `hfscan_sto3g.com` | Hand-written scan inputs, used as templates |
| [`generate.sh`](generate.sh) | Builds the 3-21G and 6-31G(d,p) scans and runs all six |
| [`extract.sh`](extract.sh) | Prints file, r and E for every scan point |
| [`results.txt`](results.txt) | Output of `extract.sh` |
