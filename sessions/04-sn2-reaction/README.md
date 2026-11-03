# Session 04 — An SN2 Reaction

From structures to reactions: the gas-phase substitution

F⁻ + CH₃Cl → CH₃F + Cl⁻

followed at the HF/6-31+G\* level. The first exercises characterise the stationary points on each side, and the next ones build the energy profile between them. A smaller reaction, HCN → CNH, teaches the search for a transition state on three atoms.

![The double-well profile of the reaction](figures/energy_profile.png)

The transition state lies below the separated reactants: in the gas phase, once F⁻ meets CH₃Cl, nothing stops the reaction.

## Contents

Each exercise folder has its own README with the task and the reasoning behind each step, and its scripts are commented line by line. The Bash patterns are explained in the **[Bash for Gaussian guide](../../docs/bash-for-gaussian.md)**.

| Exercise | Question | Level of theory |
|---|---|---|
| [Ex. 1 — Reactants and products](ex1-reactants-and-products/) | What are E, H and G of the four species, and the energy of the overall reaction? | HF/6-31+G\*, opt + freq |
| [Ex. 2 — Ion-dipole complexes](ex2-ion-dipole-complexes/) | How strongly is each ion bound, and how much does it already weaken the C–X bond? | HF/6-31+G\*, opt + freq |
| [Ex. 3 — The potential energy surface](ex3-potential-energy-surface/) | Where are the valleys, the path between them and the pass? | HF/6-31+G\*, relaxed 2D scan |
| [Ex. 4 — The transition state and the double well](ex4-transition-state/) | Is the pass a true transition state, and how high is it? | HF/6-31+G\*, `opt=ts` + freq |
| [Ex. 8 — HCN to CNH](ex8-hcn-isomerization/) | How is a transition state located and confirmed, on a three-atom reaction? | HF/6-31G\*, opt + freq, `opt=ts` |

Ex. 5 to 7 will be added as their calculations finish. Ex. 8 came before Ex. 3 because it stands alone, and Ex. 3 took long to run.

---

## Ex. 1 — Reactants and products

The two ions and the two halomethanes, each with a frequency calculation so that H and G are available for every species, the single atoms included.

| | F⁻ | Cl⁻ | CH₃Cl | CH₃F |
|---|---|---|---|---|
| E (hartree) | −99.418586 | −459.539661 | −499.094158 | −139.044227 |
| G, 298 K (hartree) | −99.432745 | −459.554684 | −499.076105 | −139.023276 |
| r(C–X) (Å) | – | – | 1.786 | 1.371 |

- **Anions need diffuse functions,** the `+` in 6-31+G\*: the extra electron spreads far from the nucleus, beyond the reach of an ordinary basis set.
- **Atoms need `freq` too:** with no vibrations, their H and G come from translation alone (H − E = 5/2 RT = 1.48 kcal/mol), but the reaction energies need them.
- **The reaction is strongly downhill:** ΔE = −44.6 and ΔG = −43.4 kcal/mol.
- **A Z-matrix with the symmetry built in:** one variable per kind of bond and angle, and the atom on the C₃ axis second, so the three hydrogens are equivalent by construction.

Full table, the first Z-matrix and what was wrong with it, and how the extraction script evolved: [Ex. 1 README](ex1-reactants-and-products/).

---

## Ex. 2 — Ion-dipole complexes

Each ion held behind the C–X bond, on the C₃ axis, where the SN2 attack happens. A dummy atom keeps three collinear atoms out of the Z-matrix. Both complexes are true minima.

| | F⁻···CH₃Cl | FCH₃···Cl⁻ |
|---|---|---|
| Complexation ΔE (kcal/mol) | −14.51 | −8.04 |
| Complexation ΔG, 298 K (kcal/mol) | −8.29 | −2.52 |
| Ion to carbon (Å) | 2.586 | 3.423 |
| C–X bond, free → complex (Å) | 1.786 → 1.864 | 1.371 → 1.399 |
| C–X stretch, free → complex (cm⁻¹) | 779 → 560 | 1155 → 1057 |

- **The ion starts the reaction.** It donates into σ\*(C–X), and the bond weakens without breaking: C–Cl stretches by 0.078 Å and its frequency drops by 28 %.
- **Three measurements, one ratio.** The bond length, the frequency and the charge transferred all change about 3 times more in F⁻···CH₃Cl: F⁻ is the better donor, and C–Cl the better acceptor.
- **ΔG is not ΔE.** Two particles becoming one cost 5 to 6 kcal/mol of translational entropy, so FCH₃···Cl⁻ is barely bound in free energy.

Dummy atoms, the `rch 108.` that broke the first run, reading the frequencies, and conclusions: [Ex. 2 README](ex2-ion-dipole-complexes/).

---

## Ex. 3 — The potential energy surface

A relaxed scan of the two bonds that change, 9 × 11 = 99 optimisations, with everything else free.

![The potential energy surface and the minimum energy path](figures/potential_energy_surface.png)

- **Two valleys, one path, one pass.** The valleys are the complexes of Ex. 2, and the pass between them is at about (2.13, 2.13) Å.
- **The highest point of the map is not the transition state.** It is F and Cl crowding the carbon at once, 160 kcal/mol up, where the reaction never goes. The transition state is the highest point of the *path*.
- **A scan gives the shape, an optimisation gives the numbers.** The lowest grid point is 3 kcal/mol above the true product complex, but an interpolation of the grid puts the pass within 0.004 Å of the optimised transition state.
- **The log, not the summary table.** Its energies are glued together and its points come in zigzag, so one `awk` reads them from the log like a notebook.

The scan, the traps of the summary table, the extraction step by step and the conclusions: [Ex. 3 README](ex3-potential-energy-surface/).

---

## Ex. 4 — The transition state and the double well

The pass of the map, optimised as a transition state.

| | Transition state |
|---|---|
| Imaginary frequency | 442i cm⁻¹ (one) |
| d(C–F), d(C–Cl) (Å) | 2.125, 2.133 |
| H–C–F (°) | 82.7 |
| Barrier from F⁻···CH₃Cl, ΔE‡ / ΔG‡ (kcal/mol) | 2.99 / 3.06 |
| Relative to F⁻ + CH₃Cl, ΔE / ΔG (kcal/mol) | **−11.52 / −5.22** |

- **A double well.** Two ion-dipole complexes, separated by a barrier of only 3 kcal/mol, which does not reach the level of the separated reactants.
- **A negative barrier is not an error.** A transition state only has to lie above the two wells it connects. From F⁻ + CH₃Cl there is no net barrier, and in the gas phase the reaction is almost as fast as the collisions.
- **Reactant-like, as Hammond predicts** for a strongly exothermic reaction: the umbrella is at 82.7°, short of planar, and most of the charge is still on F.
- **The carbon does the moving.** In the transition vector it shuttles from Cl towards F through the plane of the H atoms: that is the Walden inversion.

Building the input from the scan, the transition vector, the entropy toll of −TΔS = +6.8 kcal/mol, and the mathematics behind saddle points: [Ex. 4 README](ex4-transition-state/).

---

## Ex. 8 — HCN to CNH

A separate reaction, the H atom jumping from C to N, and the first transition state of the session: a first-order saddle point, with exactly one imaginary frequency.

![Energy levels of HCN, the transition state and CNH, with their geometries to scale](figures/hcn_isomerization.png)

| kcal/mol | ΔE | ΔG, 298 K |
|---|---|---|
| Reaction, CNH − HCN | +12.47 | +11.81 |
| Barrier from HCN | 52.24 | 47.19 |
| Barrier from CNH | 39.77 | 35.38 |

- **One imaginary frequency, 1227i cm⁻¹,** whose mode is the H moving from C to N, nearly alone: its reduced mass is 1.17 amu.
- **Two separate answers.** The barrier says the reaction is slow, and ΔG says it is unfavourable.
- **ZPE lowers the barrier by 4 kcal/mol,** because the two bends of HCN are gone at the transition state.
- **The search climbs.** The energy ends higher than it started, the opposite of a search for a minimum.

The route line, what each option does, the transition vector, and the comparison with experiment and high-level theory: [Ex. 8 README](ex8-hcn-isomerization/).

---

## Reproducing everything

On a machine with Gaussian 09 (`g09` in the `PATH`):

```bash
cd ex1-reactants-and-products && ../run.sh && ./extract.sh && cd ..
cd ex2-ion-dipole-complexes && ../run.sh && ./extract.sh && cd ..
cd ex3-potential-energy-surface && ../run.sh && ./extract.sh && cd ..
cd ex4-transition-state && ../run.sh && ./extract.sh && cd ..
cd ex8-hcn-isomerization && ../run.sh && ./extract.sh && cd ..
python plot_figures.py   # numpy, scipy, matplotlib
```

[`run.sh`](run.sh) is the same launcher as in the previous sessions: it runs every input in a folder and skips the jobs that already finished normally.

Gaussian output files (`.log`, `.chk`) are not stored. Everything the analysis needs is in the extracted data files.
