# Ex. 5 — Does UHF fix it on its own?

[← Session 02](../) · [Bash guide](../../../docs/bash-for-gaussian.md)

## Task

Repeat the H₂ dissociation curve of Ex. 4 with UHF/STO-3G, once with the default initial guess and once with `guess=mix`, and compare both with RHF.

## Approach

**The hypothesis.** RHF fails because α and β electrons are forced into the same spatial orbital. UHF lifts that constraint, so it should be able to put one electron on each atom and dissociate correctly.

**The test, and the surprise.** The first UHF scan uses the same input as Ex. 4 with `RHF` changed to `UHF`. Its curve comes out **identical to RHF, point by point**, and ⟨Ŝ²⟩ = 0 everywhere. UHF *allows* different α and β orbitals, but nothing pushes it to use them. For a closed-shell singlet the default guess has identical α and β orbitals, so the α and β Fock matrices are identical too, and every SCF iteration keeps them that way. The restricted solution is a stationary point of the UHF equations, and the SCF never leaves it.

**Breaking the symmetry on purpose.** `guess=mix` mixes the HOMO and LUMO in the initial guess, so the α and β orbitals start out different. Once the symmetry is broken, the SCF can relax to the lower, unrestricted solution wherever one exists.

**Checking with ⟨Ŝ²⟩.** The energy alone shows that something changed. ⟨Ŝ²⟩ shows what. It is 0 for a pure singlet, and it becomes non-zero as soon as the α and β orbitals differ, so [`extract.sh`](extract.sh) stores it next to ΔE at every point.

## Results and reading

| | Default guess | `guess=mix` |
|---|---|---|
| ΔE at 10 Å | 0.361 hartree (same as RHF) | 4 × 10⁻⁶ hartree (≈ 0) |
| ⟨Ŝ²⟩ at 10 Å | 0.000 | 1.000 |
| Below RHF | never | from 1.75 Å outwards (see below) |

- At long distance `guess=mix` reaches the correct limit, and ⟨Ŝ²⟩ rises to 1: the broken-symmetry solution is an equal mix of singlet and triplet. That is the price of the correct energy.
- Near equilibrium both UHF runs coincide with RHF: there the restricted solution really is the lowest one.
- **A suspicious point.** Between 1.75 Å and 1.5 Å the `guess=mix` curve jumps 0.1 hartree back onto RHF. A real Coulson–Fischer point is a smooth, tangential split, as Ex. 6 shows with 3-21G. A jump this size suggests that at 1.5 Å the SCF fell back into the restricted solution, even though a lower unrestricted one probably still existed. The true Coulson–Fischer point at this level is likely below 1.5 Å. A finer scan, or a stability check (`stable=opt`) at those points, would settle it.
- **Lesson:** a UHF result depends on where the SCF starts, even point to point within the same scan, and the input does not show which solution came out. The output does, through ⟨Ŝ²⟩ and the energy.

![RHF vs UHF with and without guess=mix](../figures/initial_guess.png)

## Scripts

### `extract.sh` — energy and ⟨Ŝ²⟩ side by side

```bash
paste -d ' ' \
	<(awk ...scan table reader... "$f") \
	<(grep "S\*\*2 before annihilation" "$f" | awk '{print $4}' | tr -d ',') \
	>> "$out"
```

The energies come from the scan summary table, and ⟨Ŝ²⟩ comes from a line that Gaussian prints once per converged point:

```
 S**2 before annihilation     1.0000,   after     0.0000
```

Both lists have one entry per point in the same order, so `paste` glues them into columns. `<( ... )` lets `paste` read each command's output as if it were a file. `tr -d ','` removes the comma Gaussian puts after the number. The value *before* annihilation is the true ⟨Ŝ²⟩ of the UHF determinant.

## Files

| File | What it is |
|---|---|
| [`h2_uhf_sto3g.com`](h2_uhf_sto3g.com) | UHF scan, default guess |
| [`h2_uhfmix_sto3g.com`](h2_uhfmix_sto3g.com) | UHF scan, `guess=mix` |
| [`h_sto3g.com`](h_sto3g.com) | H atom reference (same as Ex. 4) |
| [`extract.sh`](extract.sh) | Writes r, ΔE and ⟨Ŝ²⟩ for each curve |
| [`h2_uhf.dat`](h2_uhf.dat), [`h2_uhfmix.dat`](h2_uhfmix.dat) | Output of `extract.sh` |
