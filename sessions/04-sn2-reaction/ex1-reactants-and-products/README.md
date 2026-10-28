# Ex. 1 — Reactants and products

[← Session 04](../) · [Bash guide](../../../docs/bash-for-gaussian.md)

## Task

Compute the energy, enthalpy and free energy of the reactants and products of the SN2 reaction

F⁻ + CH₃Cl → CH₃F + Cl⁻

at the HF/6-31+G\* level, together with the C–Cl and C–F bond lengths. The table is the reference for the energy profile of the reaction in the next exercises.

## Approach

### Three questions before writing any input

**What does the `+` in 6-31+G\* add?** **Diffuse functions** on the heavy atoms: very spread-out basis functions that describe the electron density far from the nucleus. An anion has an extra electron that the nucleus holds only weakly, so its electron cloud is much more extended than that of a neutral molecule. Without diffuse functions the basis does not reach where that electron is, and the energy of the anion comes out badly. Everything in Session 03 was neutral, so they were not needed; here there are F⁻ and Cl⁻, so they are.

**Do the ions need `opt` and `freq`?** Not `opt`: a single atom has no geometry to optimise. But `freq`, yes: Gaussian only prints H and G after a frequency calculation, and the reaction energies need them for every species. For an atom they come from translation alone, with no vibrations.

**Charge and multiplicity.** The charge does not go in the route line but in the charge and multiplicity line: `-1 1` for F⁻ and Cl⁻ (with the extra electron both are closed-shell, like a noble gas), `0 1` for CH₃Cl and CH₃F.

### A Z-matrix with the symmetry built in

The first CH₃Cl Z-matrix put a hydrogen second and gave the chlorine the same bond variable as the hydrogens:

```
C
H 1 r1
CL 1 r1 2 a2        C-Cl forced equal to C-H (1.78 against 1.09 Å)
H 1 r1 2 a2 3 z3    every angle measured from the first H, so
H 1 r1 2 a2 3 -z3     H-C-H and H-C-Cl forced equal (about 110.5° and 108.4°)
```

The `z3`/`-z3` pair was a good idea, but the optimiser would have searched for an absurd compromise. The fix has two rules: **one variable per kind of bond and angle**, with a name that says what it is, and **the atom on the symmetry axis goes second**, so the equivalent atoms are all defined in the same way from it ([`ch3cl.com`](ch3cl.com)):

```
C
Cl 1 rccl
H 1 rch 2 a         the three H share the distance and the angle to Cl,
H 1 rch 2 a 3 z       so they are equivalent by construction (C3v)
H 1 rch 2 a 3 -z
```

CH₃F is identical, with F in place of Cl. Both optimisations end in point group C3v with all frequencies real.

## Results

| | F⁻ | Cl⁻ | CH₃Cl | CH₃F |
|---|---|---|---|---|
| E (hartree) | −99.418586 | −459.539661 | −499.094158 | −139.044227 |
| E + ZPE (hartree) | −99.418586 | −459.539661 | −499.053510 | −139.001888 |
| H, 298 K (hartree) | −99.416226 | −459.537300 | −499.049596 | −138.998061 |
| G, 298 K (hartree) | −99.432745 | −459.554684 | −499.076105 | −139.023276 |
| r(C–Cl) (Å) | – | – | 1.786 | – |
| r(C–F) (Å) | – | – | – | 1.371 |

Data: [`results.txt`](results.txt), written by [`extract.sh`](extract.sh).

**Two consistency checks on the ions.**

- **E + ZPE = E:** an atom does not vibrate, so it has no zero-point energy.
- **H − E = 0.00236 hartree** for both: the translational energy plus the PV term, 5/2 RT = 1.48 kcal/mol. It is all the thermochemistry gives an atom, and the reason the `freq` was needed.

**Against experiment** (NIST CCCBDB): r(C–Cl) = 1.786 Å against 1.785 Å, and r(C–F) = 1.371 Å against 1.383 Å, the usual Hartree–Fock shortening of a bond to an electronegative atom.

**Looking ahead.** Combined, the table gives the energy of the overall reaction at this level: ΔE = −44.6, ΔH = −43.6 and ΔG = −43.4 kcal/mol (products minus reactants). The reaction is strongly downhill; the next exercises add what lies between the two sides.

## How it went

- **The answers came first.** Two of the three questions above had a first answer that was wrong or half right: the `+` was first taken to have "something to do with the reaction", and the `freq` was first thought unnecessary for single atoms.
- **The first Z-matrix,** written unaided, had the problems shown above, plus a missing title and charge/multiplicity line (the same slip as with NH₃ in Session 03).
- **The launch loop** was written from scratch, more general than the one proposed (`*.com` instead of a list of names), with a one-character slip: `${%m.com}` for `${m%.com}`. In `${var%pattern}` the variable name comes first, then the `%` and what to cut from the end.
- **Finding a value in the log** does not mean memorising where it is: `grep -n "Free" file.log` gives the line number, `sed -n '440,470p' file.log` shows the context, `less file.log` (then `/Free`, `n`, `q`) browses it, and `awk '{for(i=1;i<=NF;i++) print i, $i}'` numbers the fields of a line instead of counting them by eye.
- **The extraction script** took three versions. The four search patterns were right from the start; the structure was not. Inside the loop every command must read `"$m"`, the file of that turn, never `*.log`: with several files, `grep` also puts the file name in front of each match, which shifts the `awk` fields. An optimisation prints one `SCF Done` per step, so it needs `tail -1`. And a header with two-word names (`energia (E)`) breaks the alignment of `column -t`: one word per column, as many as in the rows.

## Files

| File | What it is |
|---|---|
| [`f_anion.com`](f_anion.com), [`cl_anion.com`](cl_anion.com) | `freq` of each ion, charge −1, singlet |
| [`ch3cl.com`](ch3cl.com), [`ch3f.com`](ch3f.com) | `opt freq` of each molecule, Z-matrix with C3v symmetry built in |
| [`extract.sh`](extract.sh) | Writes E, E + ZPE, H, G and the C–X bond length of the four species to `results.txt` |
| [`results.txt`](results.txt) | Output of `extract.sh` |
