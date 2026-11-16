"""Trajectory analysis of Session 08: g(r), diffusion and RMSD, written to the exercise folders.

Usage (from this folder):  python analyze.py path/to/course_files
where course_files holds the three folders of the course archives:
    Dinamica_agua/       aguas.prmtop, outputs/aguas_output_.dcd
    Dinamica_sodio/      aguas_sodio.prmtop, outputs/aguas_sodio_output.dcd
    Dinamica_ubiquitin/  ubq_wb.psf, outputs/ubq_output.dcd
The trajectories (16-34 MB each) are not in the repository; the data files this
script writes are. In class the same quantities are computed in VMD (see the
exercise READMEs); this script is an independent check, and it also gives the
diffusion coefficient, which the exercises do not ask for.

Requires only numpy. The DCD reader is in dcd.py.
"""
import sys
from pathlib import Path

import numpy as np

from dcd import read_dcd

HERE = Path(__file__).parent
DT_FRAME = 0.25  # ps between frames: dcdfreq 250 x 1 fs


def box(cell):
    """Edge lengths of an orthorhombic cell from a DCD unit-cell record (A, gamma, B, beta, alpha, C)."""
    return np.array([cell[0], cell[2], cell[5]])


def rdf(frames, cells, ref, sel, rmax=10.0, dr=0.05, same=False):
    """g(r) and running coordination number n(r) of the atoms `sel` around the atoms `ref`.

    Minimum image convention, so rmax must stay below half the box (about 16 A here).
    g(r) = rho(r) / rho_bulk; n(r) = 4 pi rho int_0^r g(r') r'^2 dr', counted directly.
    """
    edges = np.arange(0.0, rmax + dr / 2, dr)
    counts = np.zeros(len(edges) - 1)
    volume = 0.0
    for x, cell in zip(frames, cells):
        L = box(cell)
        volume += L.prod()
        d = x[ref][:, None, :] - x[sel][None, :, :]
        d -= L * np.round(d / L)                      # minimum image
        r = np.sqrt((d * d).sum(-1))
        if same:                                      # O-O: each pair once, counted twice
            r = r[np.triu_indices(len(ref), 1)]
            counts += 2 * np.histogram(r, edges)[0]
        else:
            counts += np.histogram(r.ravel(), edges)[0]
    nframes = len(frames)
    rho = (len(sel) - (1 if same else 0)) / (volume / nframes)
    shell = 4 / 3 * np.pi * (edges[1:] ** 3 - edges[:-1] ** 3)
    r_mid = (edges[1:] + edges[:-1]) / 2
    g = counts / (nframes * len(ref) * rho * shell)
    n = np.cumsum(counts) / (nframes * len(ref))
    return r_mid, g, n, rho


def unwrap(traj, cells):
    """Undo the wrapping into the box (wrapAll/wrapWater) so each molecule moves continuously."""
    L = box(cells[0])
    step = np.diff(traj, axis=0)
    step -= L * np.round(step / L)
    return np.concatenate([traj[:1], traj[:1] + np.cumsum(step, axis=0)])


def msd(traj, max_lag=160):
    """Mean square displacement, averaged over particles and time origins."""
    lags = np.arange(1, max_lag + 1)
    return lags * DT_FRAME, np.array([((traj[k:] - traj[:-k]) ** 2).sum(-1).mean() for k in lags])


def diffusion(t, m, t0=5.0, t1=40.0):
    """Einstein relation, MSD = 6 D t, fitted between t0 and t1 ps. Returns D in 1e-5 cm2/s."""
    window = (t >= t0) & (t <= t1)
    slope = np.polyfit(t[window], m[window], 1)[0]      # A^2/ps
    return slope / 6 * 10                               # 1 A^2/ps = 1e-4 cm2/s


def kabsch(mobile, reference):
    """Rigid-body superposition: returns a function that moves coordinates onto the reference."""
    mc, rc = mobile.mean(0), reference.mean(0)
    u, _, vt = np.linalg.svd((mobile - mc).T @ (reference - rc))
    s = np.sign(np.linalg.det(vt.T @ u.T))
    rot = vt.T @ np.diag([1, 1, s]) @ u.T
    return lambda x: (x - mc) @ rot.T + rc


def rmsd(a, b):
    return np.sqrt(((a - b) ** 2).sum(-1).mean())


def write(path, columns, header, fmt="%.4f"):
    np.savetxt(path, np.column_stack(columns), fmt=fmt, header=header)
    print("Written", path)


def water(root):
    _, *_, frames, cells = read_dcd(root / "Dinamica_agua/outputs/aguas_output_.dcd")
    oxygens = np.arange(0, frames.shape[1], 3)          # atom order O H1 H2, from aguas.prmtop
    r, g, n, rho = rdf(frames, cells, oxygens, oxygens, same=True)
    write(HERE / "ex1-water/g_OO.dat", (r, g, n), "r_A g_OO(r) n_O(r)   oxygen-oxygen, 400 frames")
    t, m = msd(unwrap(frames[:, oxygens], cells))
    write(HERE / "ex1-water/msd_O.dat", (t, m), f"t_ps msd_A2   oxygen; D = {diffusion(t, m):.2f}e-5 cm2/s (fit 5-40 ps)")
    print(f"  water: rho = {rho:.5f} molecules/A3, D = {diffusion(t, m):.2f}e-5 cm2/s")


def sodium(root):
    _, *_, frames, cells = read_dcd(root / "Dinamica_sodio/outputs/aguas_sodio_output.dcd")
    na = np.array([0])                                  # Na+ is atom 1 in aguas_sodio.prmtop
    oxygens = np.arange(1, frames.shape[1], 3)
    hydrogens = np.setdiff1d(np.arange(1, frames.shape[1]), oxygens)
    for name, sel in (("NaO", oxygens), ("NaH", hydrogens)):
        r, g, n, _ = rdf(frames, cells, na, sel)
        write(HERE / f"ex2-sodium-in-water/g_{name}.dat", (r, g, n),
              f"r_A g_{name}(r) n(r)   one ion, 400 frames: noisier than O-O")


def ubiquitin(root):
    psf = (root / "Dinamica_ubiquitin/ubq_wb.psf").read_text().splitlines()
    start = next(i for i, line in enumerate(psf) if "!NATOM" in line)
    atoms = [line.split() for line in psf[start + 1:start + 1 + int(psf[start].split()[0])]]
    protein = np.array([a[1] == "U" for a in atoms])   # segment U = ubiquitin, WT1 = water
    resid = np.array([int(a[2]) for a in atoms])
    name = np.array([a[4] for a in atoms])
    heavy = protein & ~np.char.startswith(name, "H")
    backbone = protein & np.isin(name, ["N", "CA", "C", "O"])

    _, *_, frames, _ = read_dcd(root / "Dinamica_ubiquitin/outputs/ubq_output.dcd")
    ref = frames[0]                                     # first frame, as in residue_rmsd.tcl
    residues = np.arange(1, resid[protein].max() + 1)
    t, bb, hv, per_residue = [], [], [], np.zeros(len(residues))
    for k, x in enumerate(frames):
        # Backbone RMSD after fitting the backbone: the usual measure of the fold
        bb.append(rmsd(kabsch(x[backbone], ref[backbone])(x[backbone]), ref[backbone]))
        # Fit on the whole protein, then heavy atoms of each residue, as residue_rmsd.tcl does
        y = kabsch(x[protein], ref[protein])(x)
        hv.append(rmsd(y[heavy], ref[heavy]))
        for i, res in enumerate(residues):
            sel = heavy & (resid == res)
            per_residue[i] += rmsd(y[sel], ref[sel])
        t.append(DT_FRAME * (k + 1))
    write(HERE / "ex3-ubiquitin/rmsd_time.dat", (t, bb, hv),
          "t_ps rmsd_backbone_A rmsd_heavy_A   reference: first frame (t = 0.25 ps)")
    write(HERE / "ex3-ubiquitin/rmsd_residue.dat", (residues, per_residue / len(frames)),
          "resid rmsd_A   heavy atoms, averaged over the 400 frames", fmt=["%d", "%.4f"])


if __name__ == "__main__":
    root = Path(sys.argv[1])
    water(root)
    sodium(root)
    ubiquitin(root)
