# Session 01 — Linux and Z-matrices

The starting point of the course: getting comfortable with the Linux command line, and learning to describe a molecule the way Gaussian reads it, as a Z-matrix. The session ends with the first two calculations, single-point energies of water and methanol.

![The Session 01 Z-matrices, converted to Cartesian coordinates](figures/z_matrices.png)

## Linux

Most of the session was spent on the shell itself: navigating the file system, editing files with Vim, and setting up the shell environment. The configuration files written for that are personal and are not included here. What the session started is visible in every later one: from Session 02 on, all jobs are launched and analysed with Bash scripts, collected in the [Bash for Gaussian guide](../../docs/bash-for-gaussian.md).

## Z-matrices

A Z-matrix places each atom relative to atoms already placed: a distance to one, an angle with a second and a dihedral with a third. Values can be numbers or named variables, defined below a blank line. Atoms that share a variable are equivalent by construction.

| File | Molecule | What it shows |
|---|---|---|
| [`h2o.zmat`](z-matrices/h2o.zmat) | H₂O | The minimal case: one shared bond length `r1` and one angle `a2` |
| [`h2o2_trans.zmat`](z-matrices/h2o2_trans.zmat) | H₂O₂, trans | The dihedral `d2` sets the conformation: 180° puts the two H atoms on opposite sides |
| [`h2o2_cis.zmat`](z-matrices/h2o2_cis.zmat) | H₂O₂, cis | The same Z-matrix with `d2` = 0°: both H atoms on the same side |
| [`ch3cl.zmat`](z-matrices/ch3cl.zmat) | CH₃Cl | Three equivalent H atoms from one bond, one angle and the dihedrals `z2` and `-z2`: a variable can be used with a minus sign |
| [`hcch.zmat`](z-matrices/hcch.zmat) | HCCH | A linear molecule needs dummy atoms (`X`), one per carbon |
| [`metoh.com`](single-points/metoh.com) | CH₃OH | A staggered methyl group, with dihedrals 180°, 60° and −60° |

**Dummy atoms.** An atom cannot be defined at 180° from the previous two: the dihedral that should place the next atom becomes undefined. In acetylene each carbon gets a dummy atom `X`, 1 Å away at 90° from the C–C axis. Each H is then placed at 90° from *its own carbon's* dummy with a dihedral of 180°, which puts it on the axis. Converting the Z-matrix to Cartesian coordinates gives exactly 180° for both C–C–H angles ([`plot_figures.py`](plot_figures.py) checks it). This detail came back later: in [Session 03, Ex. 4](../03-geometry-optimization/ex4-hf-vs-b3lyp/#acetylene-came-out-bent), an acetylene input with a single dummy atom optimised to a bent molecule.

**Neither cis nor trans.** The two H₂O₂ Z-matrices are the planar extremes. The real molecule is skewed, with a dihedral of about 111°, and finding it takes an optimisation: [Session 03, Ex. 4](../03-geometry-optimization/ex4-hf-vs-b3lyp/) gets 116° with HF and 118° with B3LYP.

## First calculations

Two single-point energies at HF/3-21G, at fixed geometries given by the Z-matrices:

| Input | Molecule | E (hartree) | μ (D) | Point group |
|---|---|---|---|---|
| [`h2oi.com`](single-points/h2oi.com) | H₂O (r = 0.958 Å, 104.5°) | −75.58542 | 2.44 | C₂ᵥ |
| [`metoh.com`](single-points/metoh.com) | CH₃OH (staggered) | −114.39589 | 2.21 | Cs |

Values read from the outputs into [`results.txt`](single-points/results.txt).

**Following water through the course.** The same molecule and basis set appear again in later sessions at different geometries, and the energies fall in the order they should:

| Geometry, HF/3-21G | r (Å) | ∠HOH | E (hartree) |
|---|---|---|---|
| Session 01: experimental geometry | 0.958 | 104.5° | −75.58542 |
| [Session 02, Ex. 2](../02-hartree-fock/ex2-basis-sets/): rounded geometry | 0.96 | 104.5° | −75.58550 |
| [Session 03, Ex. 1](../03-geometry-optimization/ex1-optimized-geometries/): optimised | 0.9667 | 107.65° | −75.58596 |

The closer the geometry is to the 3-21G minimum, the lower the energy, and the optimised one is lowest of all. Both dipoles are also well above experiment (1.85 D for water, 1.70 D for methanol), the same Hartree–Fock overestimation that Session 03 measures in detail.

## Files

| Folder | Contents |
|---|---|
| [`z-matrices/`](z-matrices/) | The practice Z-matrices (geometry block only, no route line) |
| [`single-points/`](single-points/) | The two Gaussian inputs and their [results](single-points/results.txt) |
| [`plot_figures.py`](plot_figures.py) | Converts every Z-matrix to Cartesian coordinates and draws it |

Gaussian outputs (`.log`, `.chk`) are not stored.
