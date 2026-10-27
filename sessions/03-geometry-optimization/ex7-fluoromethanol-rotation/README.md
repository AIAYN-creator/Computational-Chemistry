# Ex. 7 — Internal rotation of fluoromethanol

[← Session 03](../) · [Bash guide](../../../docs/bash-for-gaussian.md)

## Task

Obtain the potential energy curve for the rotation of the hydroxyl hydrogen about the C–O bond of fluoromethanol (FCH₂–OH), and explain it in terms of the interactions that appear along the rotation.

## Approach

A relaxed scan of the H–O–C–F dihedral at B3LYP/6-31G*, from 0° to 180° in steps of 20° (10 points), with `opt=z-matrix`: at each angle, every other coordinate is optimised. The input, [`fluoromethanol_scan.com`](fluoromethanol_scan.com), comes from the practical session:

```
C
O 1 r1
F 1 r2 2 a2
H 2 r3 1 a3 3 z3          the hydroxyl H; z3 = H-O-C-F, the scanned variable
H 1 r4 2 a4 3 z4
H 1 r5 2 a5 3 z5
...
z3 0. S 9 20.0            start at 0, 9 steps of +20: 10 points, 0 -> 180
```

**Half a turn is enough.** The two directions of rotation give mirror-image molecules, so E(φ) = E(−φ), and the scan from 0° to 180° covers the whole curve, as in [Ex. 5](../ex5-dichloroethane-scan/#half-a-turn-is-enough).

**Predict first.** Before looking at the data, the expected answer was the one that works for 1,2-dichloroethane: the minimum at 180° (*anti*, the H as far from F as possible) and the maximum at 0° (eclipsed). It turned out to be wrong, and the reason is the point of the exercise.

## Results

| H–O–C–F (°) | E (hartree) | ΔE (kcal/mol) | |
|---|---|---|---|
| 0   | −214.950576 | 3.01 | local maximum (*syn*) |
| 20  | −214.951662 | 2.32 | |
| 40  | −214.953891 | 0.92 | |
| **60**  | **−214.955365** | **0.00** | **lowest scan point (*gauche*)** |
| 80  | −214.954988 | 0.24 | |
| 100 | −214.952921 | 1.53 | |
| 120 | −214.950279 | 3.19 | |
| 140 | −214.948270 | 4.45 | |
| 160 | −214.947287 | 5.07 | |
| **180** | **−214.947035** | **5.23** | **absolute maximum (*anti*)** |

Data: [`scan.txt`](scan.txt), extracted by [`extract.sh`](extract.sh).

![Rotation of fluoromethanol with Newman projections](../figures/fluoromethanol_rotation.png)

The full rotation has **two equivalent minima at about ±60°**, a small barrier at 0° and the large one at 180°. Since 80° lies lower than 40°, the true minimum is a little past 60°: a cosine-series fit through the points places it at about 66°, 0.07 kcal/mol below the 60° point.

## Interpretation: the anomeric effect

Steric intuition predicts the opposite of what the calculation shows: the *anti* conformer, with the OH hydrogen as far as possible from F, should be the most stable, and it is the **least** stable. The OH hydrogen is too small for sterics to matter. What decides the curve is the orientation of the **oxygen lone pairs** relative to the C–F bond. The Newman projections above, drawn along O → C with the lone pairs, show it:

- **Gauche (≈ 60°), minimum.** One oxygen lone pair is **antiperiplanar** to the C–F bond: in the same plane, on the opposite side. In that position it overlaps with the C–F antibonding orbital, σ\*(C–F), which is low in energy because fluorine is so electronegative, and whose large lobe sits on carbon, on the side away from F. The donation n(O) → σ\*(C–F) stabilises the molecule: this is the **generalised anomeric effect**.
- **Anti (180°), absolute maximum.** No lone pair is near the antiperiplanar position, so there is little n → σ\* stabilisation, and both lone pairs sit on the fluorine side, which adds lone-pair/F repulsion.
- **Syn (0°), lower maximum.** No lone pair is antiperiplanar here either, but the hydroxyl hydrogen (δ+) points at the fluorine (δ−). This weak electrostatic attraction leaves the barrier lower than the *anti* one.

The overlap does not switch on and off: it is largest when the lone pair is exactly antiperiplanar and decreases gradually away from it. In the *anti* conformer it is small, not zero.

**Vocabulary (Klyne–Prelog).** 0 ± 30° synperiplanar (eclipsed), 30–90° synclinal (*gauche*), 90–150° anticlinal, 180 ± 30° antiperiplanar. The minimum is *gauche* in the H–O–C–F dihedral, but what matters is that the **lone pair–O–C–F** dihedral is *anti*.

## Conclusions

1. The minimum lies at about 60° (*gauche*), not at 180° (*anti*), the opposite of what sterics alone would predict.
2. The cause is the anomeric effect: an oxygen lone pair antiperiplanar to the C–F bond donates into σ\*(C–F).
3. The *anti* conformer is the absolute maximum (5.2 kcal/mol): little anomeric stabilisation and lone-pair/F repulsion. The *syn* conformer is a lower maximum (3.0 kcal/mol) thanks to a weak H···F attraction.
4. **General lesson:** lone pairs act like substituents, and hyperconjugation can override steric effects. To spot an anomeric effect, draw the Newman projection with the lone pairs and look for one antiperiplanar to a polar C–X bond.

## How it went

- **The input came from a PDF.** The slides print the charge and multiplicity as `01`, which had to be split into `0 1`. Text pasted from a PDF can also carry non-breaking spaces, which Gaussian does not read as spaces; `grep -c $'\xc2\xa0' file.com` must give 0.
- **The job ran in the background** (`&`), in parallel with the glycine calculations of [Ex. 8](../ex8-glycine-conformers/).
- **Two wrong explanations came before the right one.** The first was the steric prediction above. The second was that the *gauche* minimum comes from a favourable interaction with the hydroxyl H. If an O–H···F attraction were in control, the minimum would be at 0°, where the H points at F, and 0° is 3 kcal/mol higher. The stabilising interaction is between *orbitals*, not atoms: the hydroxyl H is a spectator, and its position only shows where the lone pairs are.
- **Predicting before looking was worth it,** even though the prediction failed: the gap between the prediction and the data is what made the explanation stick.

## Scripts

[`extract.sh`](extract.sh) is the awk one-liner of [Ex. 5](../ex5-dichloroethane-scan/), adapted to a scan that climbs from 0° instead of descending from 180°: it prints before incrementing the counter, so the first point comes out as 0°. Pattern: [remember the last value until a trigger](../../../docs/bash-for-gaussian.md#3-reading-a-table-of-any-length-with-awk).

## Files

| File | What it is |
|---|---|
| [`fluoromethanol_scan.com`](fluoromethanol_scan.com) | Relaxed scan input, B3LYP/6-31G* |
| [`extract.sh`](extract.sh) | Writes the dihedral and energy of each converged point to `scan.txt` |
| [`scan.txt`](scan.txt) | Output of `extract.sh` |

The figure, with the fit and the Newman projections, is built by [`plot_figures.py`](../plot_figures.py).
