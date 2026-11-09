# Ex. 6 — The SN2 reaction in water

[← Session 07](../) · [Session 04 extension in water](../../04-sn2-reaction/extra-water-pcm/)

## Task

Compute the barrier of F⁻ + CH₃Cl → CH₃F + Cl⁻ in water (PCM) from the reactant complex to the transition state, and compare it with the gas phase. The reaction was already studied in water as an [extension of Session 04](../../04-sn2-reaction/extra-water-pcm/), against the separated reactants; this exercise repeats it with the keywords given in class, from the complex.

## Approach

```
#HF/6-31+G* opt=(z-matrix,calcfc,maxcycles=100) freq scrf=(pcm,solvent=water)
#HF/6-31+G* opt=(z-matrix,calcfc,maxcycles=100,ts,noeigentest) freq scrf=(pcm,solvent=water)
```

The first route line is for the complex ([`rc_pcm.com`](rc_pcm.com)), a minimum; the second, with `ts`, for the transition state ([`ts_pcm.com`](ts_pcm.com)). Both start from the initial values of Session 04, Ex. 2 and Ex. 4, not from the geometries optimised in the gas phase, which was what the class recommended.

[`extract.sh`](extract.sh) was written in class and worked the first time. The bond lengths have different names in each input, so one `grep -E` pattern looks for either: `(rccl|r5)`, `(rcf|r1)`, `(rch|r2)`.

## Results

| | E (hartree) | G (hartree) | d(C–Cl) (Å) | d(C–F) (Å) | d(C–H) (Å) |
|---|---|---|---|---|---|
| Gas: complex | −598.535868 | −598.522055 | 1.864 | 2.586 | 1.070 |
| Gas: transition state | −598.531104 | −598.517174 | 2.133 | 2.125 | 1.062 |
| Water: "complex" | −598.654276 | −598.644709 | 1.800 | **4.629** | 1.077 |
| Water: transition state | −598.631792 | −598.618125 | 2.231 | 2.071 | 1.062 |

Data: [`results.txt`](results.txt) for water; the gas rows come from [Session 04](../../04-sn2-reaction/).

| Barrier, transition state − complex | ΔE‡ (kcal/mol) | ΔG‡ (kcal/mol) | k (n = 1), 298 K |
|---|---|---|---|
| Gas phase | 2.99 | 3.06 | 3.5 × 10¹⁰ s⁻¹ |
| Water | 14.11 | 16.68 | ≈ 3.6 s⁻¹ |

- **The "complex" in water is not a complex.** F⁻ ends 4.63 Å from the carbon, against 2.59 Å in the gas phase: the dielectric screens the ion-dipole attraction. Its lowest frequency is a tiny imaginary one (14i cm⁻¹), the sign of a flat region, not of a minimum. ΔE‡ from it, 14.11 kcal/mol, is almost the same as from the separated reactants (14.03): there is no well.
- **The barrier rises by about 13.6 kcal/mol and k falls by ten orders of magnitude.** Water stabilises F⁻, whose charge is concentrated, much more than the transition state, where it is shared.
- **ΔG‡ from the "complex" (16.7) and from the separated reactants (20.9)** differ by about 4 kcal/mol, almost all of it translational entropy: one particle against two.
- **The transition state is later in water,** with a shorter C–F and a longer C–Cl: Hammond's postulate.

## Why the results differ between students

The class reference gave 18.6 kcal/mol without symmetry and 19.3 with it. Two things move these numbers:

1. **The symmetry number.** 19.3 − 18.6 = 0.7 ≈ RT ln 3. The collinear transition state is C₃ᵥ (σ = 3), but unless the Z-matrix imposes the symmetry, Gaussian takes it as C₁ (σ = 1), and G comes out 0.65 kcal/mol too low. Here the "complex" was detected as C₃ᵥ (σ = 3) and the transition state as C₁ (σ = 1), so 16.68 is too low by that amount: about 17.3 kcal/mol with σ = 3 for both. The same mismatch explains the [gas-phase barrier of Session 04](../../04-sn2-reaction/ex4-transition-state/#a-symmetry-number-gaussian-missed), 3.06 here against 3.7 in the class reference.
2. **The flat region.** Around the "complex" the energy barely changes with the distance, and the gradient is so small that the optimiser stops before the real minimum: some students at 4.7 Å, others at 5.1 Å. A flat region also has very low frequencies, which in the harmonic model contribute a lot of entropy, so G depends strongly on where the optimiser stopped. ΔE is much more stable than ΔG. `opt=tight`, with stricter convergence criteria, should bring everyone's results closer together.

**The lesson:** in flat regions the harmonic free energy is unreliable. Check σ, the point group and the lowest frequencies every time.

## Two Bash traps

- **`grep "SCF Done" *.log | tail -1` gives a single line,** the last one of the last file: `grep` writes everything in one stream, and `tail` does not know there were two files. For the last line of each file, a loop: `for m in *.log; do echo "$m"; grep "SCF Done" "$m" | tail -1; done`.
- **`grep "-DE\/DX"` fails with `unknown devices method`:** a pattern that starts with `-` is read as an option. `grep -e "-DE/DX" file` marks it explicitly as the pattern.

## Pending

- The complex again with `opt=tight`: where does it stop, and how does ΔG‡ move?

## Files

| File | What it is |
|---|---|
| [`rc_pcm.com`](rc_pcm.com), [`ts_pcm.com`](ts_pcm.com) | The complex and the transition state in water (PCM) |
| [`extract.sh`](extract.sh) | Writes `results.txt` (written in class) |
| [`results.txt`](results.txt) | E, G and the three bond lengths of both structures |
