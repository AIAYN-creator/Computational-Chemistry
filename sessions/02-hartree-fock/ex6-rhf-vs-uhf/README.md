# Ex. 6 — RHF vs UHF for H₂ and LiH

[← Session 02](../) · [Bash guide](../../../docs/bash-for-gaussian.md) · **[📄 Report (PDF)](../report/report.pdf)**

## Task

Compute the RHF and UHF (`guess=mix`) dissociation curves of H₂ and LiH at HF/3-21G, reference them to the separated atoms, and write up the results as a short report.

## Approach

**What Ex. 4 and 5 already established.** RHF cannot dissociate H₂, and UHF can only if the initial guess breaks the symmetry. This exercise checks whether the picture holds with a better basis (3-21G instead of STO-3G) and for a heteronuclear bond.

**Why LiH.** Like H₂, it is a two-electron bond, but between two different atoms, and much longer and weaker. It has two consequences:

- The reference becomes E(Li) + E(H). Both atoms are doublets, computed with UHF.
- The scan range moves out: `r1 7.5 21 -0.3` covers 7.5 → 1.2 Å in 22 points, around an equilibrium distance of about 1.6 Å.

**Six jobs, one launcher.** Four scans (2 molecules × 2 methods) and two atoms go into one folder, and [`run.sh`](../run.sh) launches them all, skipping any that already finished.

**One data file per curve.** [`extract.sh`](extract.sh) writes four files (`h2_rhf.dat`, `h2_uhfmix.dat`, `lih_rhf.dat`, `lih_uhfmix.dat`) that can be plotted directly. The report's figures were drawn from them with PGFPlots. In this repository, ⟨Ŝ²⟩ was added to the UHF files, and the figures were redrawn with [`plot_figures.py`](../plot_figures.py).

## Results and reading

The full discussion is in the **[report](../report/report.pdf)**, and the summary table and conclusions are in the [session README](../).

![RHF vs UHF dissociation curves of H2 and LiH](../figures/rhf_vs_uhf.png)

- Near equilibrium RHF and UHF are the same calculation. HF/3-21G gives r<sub>e</sub> within 0.05 Å, but underestimates D<sub>e</sub> by 25 % (H₂) and 44 % (LiH), because Hartree–Fock has no electron correlation.
- RHF ends 7.6 eV (H₂) and 4.1 eV (LiH) above the separated atoms, errors larger than the bonds themselves.
- UHF leaves RHF at the Coulson–Fischer point, ≈ 1.2 Å for H₂ and ≈ 2.2 Å for LiH, and reaches the correct limit. Below the curves, ⟨Ŝ²⟩ shows the cost: it rises from 0 to 1 right where the curves split.
- Here the UHF curves split from RHF smoothly. In Ex. 5, at STO-3G, the split was an abrupt jump, most likely the SCF falling back into the restricted solution. A smooth onset of ⟨Ŝ²⟩ is a good sign that the scan followed one solution all the way.

## Scripts

### `extract.sh` — functions instead of copy-paste

H₂ and LiH need the same two operations, reading a scan relative to a reference and reading ⟨Ŝ²⟩, so they are written once as Bash functions:

```bash
scan() {  # scan <log> <reference energy>
	awk -v ref="$2" '...scan table reader... { print $2, $3 - ref }' "$1"
}

s2() {    # s2 <log>
	grep "S\*\*2 before annihilation" "$1" | awk '{print $4}' | tr -d ','
}
```

The loop then only decides which reference goes with which molecule:

```bash
for mol in h2 lih; do
	[ "$mol" = h2 ] && ref=$REF_H2 || ref=$REF_LIH
	scan "${mol}_rhf_321g.log" "$ref" >> "${mol}_rhf.dat"
	paste -d ' ' <(scan "${mol}_uhfmix_321g.log" "$ref") <(s2 "${mol}_uhfmix_321g.log") >> "${mol}_uhfmix.dat"
done
```

The first version of this script repeated the extraction for each molecule, with the number of scan points fixed by hand (39 for H₂, 22 for LiH). With functions, adding a third molecule only takes another reference energy.

## Files

| File | What it is |
|---|---|
| `h2_rhf_321g.com`, `h2_uhfmix_321g.com` | H₂ scans, 10 → 0.5 Å |
| `lih_rhf_321g.com`, `lih_uhfmix_321g.com` | LiH scans, 7.5 → 1.2 Å |
| `h_321g.com`, `li_321g.com` | Atomic references (UHF doublets) |
| [`extract.sh`](extract.sh) | Writes the four `.dat` files |
| `*.dat` | r, ΔE (and ⟨Ŝ²⟩ for UHF), one file per curve |
