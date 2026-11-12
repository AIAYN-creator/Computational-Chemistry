# Input templates — the Menshutkin reaction

The `.com` files themselves are not stored; these templates are what is reusable, and they rebuild every job.

## The Z-matrix of the complex and the transition state

The dummy atom `X` makes N–C–Cl collinear without writing an angle of 180°, which would break the Z-matrix. With `a5 = 90.` and `z5 = 180.`, N, C and Cl lie on one line.

```
C
N   1 r1
H   1 r2 2 a2
H   1 r3 2 a3 3 z3
H   1 r4 2 a4 3 z4
X   1 1.0 2 90. 3 0.
Cl  1 r5 6 a5 2 z5
H   2 r6 1 a6 6 z6
H   2 r7 1 a7 6 z7
H   2 r8 1 a8 6 z8
```

| Variable | Complex | Transition state | What it is |
|---|---|---|---|
| `r1` | 3.7 | 2.2 | d(N–C), from the handout |
| `r5` | 1.8 | 2.3 | d(C–Cl), from the handout |
| `a2`–`a4` | 72. | 90. | H–C–N, the CH₃ umbrella. In the complex CH₃Cl is almost intact (H–C–Cl ≈ 108°); in the transition state it is planar, halfway through the Walden inversion |
| `a5` | 90. | 90. | Collinearity |
| `a6`–`a8` | 110. | 110. | H–N–C, tetrahedral nitrogen |
| `z3`, `z4` | 120., 240. | same | H of CH₃ |
| `z5` | 180. | same | Collinearity |
| `z6`–`z8` | 60., 180., 300. | same | H of NH₃, **staggered** with respect to those of CH₃, as in ethane |
| `r2`–`r4` | 1.08 | same | C–H |
| `r6`–`r8` | 1.01 | same | N–H |

Charge and multiplicity: **`0 1`**. The reactants are neutral, and the system stays neutral at the transition state even though charge separates inside it.

## Route lines

```
# complex
#HF/6-31+G* opt=(z-matrix,calcfc,maxcycles=100) freq scrf=(pcm,solvent=XXX) pop=chelpg

# transition state
#HF/6-31+G* opt=(ts,z-matrix,calcfc,noeigentest,maxcycles=100) freq scrf=(pcm,solvent=XXX) pop=chelpg

# separate molecules (NH3, CH3Cl, CH3NH3+)
#HF/6-31+G* opt=(calcfc,maxcycles=200) freq scrf=(pcm,solvent=XXX) pop=chelpg

# separate ion (Cl-): one atom, no geometry to optimise
#HF/6-31+G* freq scrf=(pcm,solvent=XXX)
```

For the gas phase, `scrf=(...)` is removed. In the chained jobs, `geom=checkpoint` replaces the coordinates.

## The order of the chains

> Start where the starting geometry is most reliable and end where convergence is least certain.

- **Transition state:** water, acetonitrile, chloroform, benzene, heptane, gas. The handout geometries are those of a very polar medium, and the gas-phase transition state is the furthest from them (a very endothermic reaction, so a very late transition state).
- **Everything else:** gas, heptane, benzene, chloroform, acetonitrile, water. Here the doubtful end is the polar one, where the complex stops existing.

## Launching and checking

```bash
(for m in nh3 ch3cl rc ts ch3nh3 cl; do g09 < "$m.com" > "$m.log"; done) &

grep -c "Normal termination" *.log   # 2 per job with opt + freq, 1 with freq only
grep -c "Error termination" *.log    # 0
grep "imaginary frequencies" ts.log  # 6 lines, all of them saying 1
```

`opt freq` prints two `Normal termination` lines per job, one when the optimisation ends and one when the frequencies do: six chained jobs give 12.
