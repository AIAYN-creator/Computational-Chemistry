# Computational Chemistry

Coursework portfolio for a university course in computational chemistry. Each session is a short, self-contained study: a chemical question, the calculations used to answer it, the scripts that automate them, and a written report with the results and conclusions.

The aim is to show the whole workflow, not only the final numbers: how each calculation is set up, how the output is processed, and how the results are read against theory and experiment.

## Sessions

| # | Topic | Methods | Highlights |
|---|-------|---------|------------|
| 02 | [The dissociation problem in Hartree–Fock theory](sessions/02-hf-dissociation/) | RHF / UHF, 3-21G, Gaussian 09 | Potential energy curves of H₂ and LiH; failure of RHF at dissociation, Coulson–Fischer point, spin contamination in UHF |

More sessions will be added as the course goes on.

## Repository layout

```
sessions/
└── NN-topic/
    ├── README.md   # Summary: question, method, key results, conclusions
    ├── report/     # Full written report (PDF)
    ├── inputs/     # Input files for the quantum chemistry software
    ├── scripts/    # Bash/Python scripts that run the jobs and post-process the output
    └── data/       # Processed data (energies, scan tables) used for the figures
```

Large raw outputs (checkpoint files, full logs) are not tracked; only the inputs, the scripts and the processed data needed to rebuild the figures are kept.

## Tools

- **Electronic structure:** Gaussian 09
- **Automation:** Bash on Linux (job launching, output parsing with `grep`/`awk`)
- **Figures and reports:** LaTeX, PGFPlots/TikZ

## Author

Martín Llorens Giménez

---

© 2026 Martín Llorens Giménez. All rights reserved.
