# Ex. 4 — What happens to RHF when a bond breaks

[← Session 02](../) · [Bash guide](../../../docs/bash-for-gaussian.md)

## Task

Compute the RHF/STO-3G potential energy curve of H₂ from 10 Å down to 0.5 Å, and compare its long-distance limit with the energy of two isolated hydrogen atoms.

## Approach

**A long scan, run backwards.** The scan line `r1 10.0 38 -0.25` starts at 10 Å and takes 38 steps of −0.25 Å, so 39 points down to 0.5 Å. Starting from the separated atoms means each point begins from the converged wavefunction of the previous, slightly longer one.

**A reference that makes the error visible.** The raw total energy of H₂ at 10 Å means little on its own. What matters is how it compares with two isolated atoms. So the H atom is computed separately, and every point is reported as

  ΔE(r) = E(H₂, r) − 2 E(H)

A correct curve must go to ΔE = 0 at long distance, and any leftover is the error of the method.

**Why the H atom is UHF.** A hydrogen atom has a single electron, so it is a doublet (`0 2` in the input), and RHF, which pairs electrons in the same spatial orbital, cannot describe it. With one electron there is nothing for UHF to unbalance, and it gives the exact Hartree–Fock answer for the atom.

## Results and reading

At 10 Å, RHF lies **0.361 hartree (9.8 eV)** above two H atoms. That is almost twice the bond energy at this level, and the curve is still creeping upwards rather than levelling off at zero.

The reason is the closed-shell determinant |σ<sub>g</sub>α σ<sub>g</sub>β|. Written in terms of atomic orbitals, it holds the covalent H·  ·H configuration and the ionic H⁺H⁻ configuration with equal weight at *every* distance. At 10 Å the true answer is 100 % covalent, but RHF is forced to keep a 50 % ionic contribution, and H⁺ + H⁻ is very high in energy.

The curve is plotted together with Ex. 5 in the [session README](../#ex-4-and-5--rhf-dissociation-and-the-uhf-initial-guess).

## Scripts

[`extract.sh`](extract.sh), commented line by line, reads the energy of the H atom once, then runs the scan-table reader from Ex. 3, subtracting 2 E(H) at every point. Bash only handles integers, so the subtraction happens in `awk`, with the shell value passed in through `-v`. E(H) is kept as a `#` comment at the top of the output. Patterns: [reading a table](../../../docs/bash-for-gaussian.md#3-reading-a-table-of-any-length-with-awk), [arithmetic with shell values](../../../docs/bash-for-gaussian.md#4-doing-arithmetic-with-shell-values).

## Files

| File | What it is |
|---|---|
| [`h2_rhf_sto3g.com`](h2_rhf_sto3g.com) | RHF scan of H₂, 10 → 0.5 Å |
| [`h_sto3g.com`](h_sto3g.com) | UHF H atom (doublet), the reference |
| [`extract.sh`](extract.sh) | ΔE(r) relative to 2 E(H) |
| [`results.txt`](results.txt) | Output of `extract.sh` |

Run with `../run.sh && ./extract.sh > results.txt`.
