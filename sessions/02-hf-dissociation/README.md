# Session 02 — The Dissociation Problem in Hartree–Fock Theory

**Restricted vs. unrestricted potential energy curves of H₂ and LiH**

📄 [Full report (PDF)](report/report.pdf)

## Question

Restricted Hartree–Fock (RHF) describes closed-shell molecules well near equilibrium, but its closed-shell determinant keeps a fixed 50 % ionic contribution at every bond length, so it cannot dissociate a bond into neutral atoms. Unrestricted HF (UHF) lets α and β electrons occupy different spatial orbitals and can fix this, but only beyond the Coulson–Fischer point and with a symmetry-broken initial guess.

This session quantifies both behaviours for H₂ and LiH.

## Method

- **Level of theory:** HF/3-21G, Gaussian 09 (Rev. D.01)
- **Scans:** Z-matrix with the bond length *r* as the only variable, `Scan` keyword
  - H₂: 10.0 → 0.5 Å, step 0.25 Å (39 points)
  - LiH: 7.5 → 1.2 Å, step 0.3 Å (22 points)
  - Scans run from long to short distance so that each point starts from the converged wavefunction of the previous one.
- **Methods:** RHF, and UHF with `guess=mix` (mixes HOMO and LUMO to break α/β spatial symmetry; without it UHF collapses onto RHF).
- **Reference:** separated-atom energies from UHF/3-21G on the doublet ground states, with curves reported as

  ΔE(r) = E<sub>AB</sub>(r) − E(A) − E(B), so a correct curve tends to 0 as r → ∞.
- **Automation:** Bash scripts run every input through Gaussian (skipping jobs that already terminated normally), pull the atomic energies and scan tables from the outputs with `grep`, compute ΔE and write one data file per curve. Figures are drawn straight from those files with PGFPlots.

## Key results

| | r<sub>e</sub> HF (Å) | r<sub>e</sub> exp. (Å) | D<sub>e</sub> HF (eV) | D<sub>e</sub> exp. (eV) | r<sub>CF</sub> (Å) | RHF error at r<sub>max</sub> (eV) |
|---|---|---|---|---|---|---|
| H₂  | 0.735 | 0.741 | 3.55 | 4.75 | ≈ 1.2 | 7.62 |
| LiH | 1.64  | 1.596 | 1.42 | 2.52 | ≈ 2.2 | 4.13 |

Experimental values: Huber & Herzberg (1979).

## Conclusions

- **Near equilibrium** RHF and UHF coincide and give bond lengths within 0.05 Å, but underestimate D<sub>e</sub> (−25 % for H₂, −44 % for LiH) because HF lacks electron correlation.
- **RHF cannot dissociate the bond:** at the largest distance it lies 0.280 Eₕ (H₂) and 0.152 Eₕ (LiH) above the separated atoms, an error larger than the bond energy itself.
- **UHF with `guess=mix`** splits from RHF at the Coulson–Fischer point and goes smoothly to the correct limit, at the cost of spin contamination: ⟨Ŝ²⟩ → 1, an equal singlet/triplet mixture.
- The UHF result depends on the initial guess. A balanced description of the whole curve needs multi-determinant methods such as configuration interaction.

## Files

| Folder | Contents |
|---|---|
| [`report/`](report/) | Final report (PDF) |
| `inputs/` | Gaussian input files *(to be added)* |
| `scripts/` | Bash scripts for running jobs and extracting data *(to be added)* |
| `data/` | ΔE(r) tables for each curve *(to be added)* |
