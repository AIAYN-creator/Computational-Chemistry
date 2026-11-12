#!/usr/bin/env python3
"""Analysis of Session 07, Ex. 8: the Menshutkin reaction in six media.

Reads jobs.dat (written by extract.sh), computes barriers and reaction free
energies, fits against eps and against f(eps), leave-one-out validation and
the comparison with experiment. Prints everything and writes results.dat.

Usage (from this folder):  python analyze.py
"""
import numpy as np

HARTREE = 627.5095          # kcal/mol
RT      = 0.0019872 * 298.15

ORDER = ['gas', 'Heptane', 'Benzene', 'Chloroform', 'Acetonitrile', 'Water']
NAME  = {'gas': 'Gas'}

def f(eps):
    """Kirkwood-Onsager function: what actually appears in the energy."""
    return (eps - 1.0) / (2.0 * eps + 1.0)

def eps_from_f(x):
    """Inverse: which dielectric constant gives a certain f."""
    return (1.0 + x) / (1.0 - 2.0 * x)

def read(path='jobs.dat'):
    G, E, eps, geo = {}, {}, {}, {}
    for line in open(path).read().splitlines()[1:]:
        p = line.split()
        sp, sol = p[0], p[1]
        if sp == 'ch3nh3b':          # the cation, relaunched with opt=calcfc
            sp = 'ch3nh3'
        eps[sol] = float(p[2])
        E.setdefault(sp, {})[sol] = float(p[3])
        G.setdefault(sp, {})[sol] = float(p[4])
        if sp == 'ts':
            geo[sol] = dict(rnc=float(p[5]), rccl=float(p[6]),
                            q=float(p[7]), mu=float(p[8]), nu=float(p[9]))
    return E, G, eps, geo

def fit(x, y):
    """Least-squares straight line and its coefficient of determination."""
    m, b = np.polyfit(x, y, 1)
    r2 = 1.0 - ((y - (m * x + b))**2).sum() / ((y - y.mean())**2).sum()
    return m, b, r2

def main():
    E, G, eps, geo = read()

    e  = np.array([eps[s] for s in ORDER])
    fe = f(e)

    dG2 = np.array([(G['ts'][s] - G['nh3'][s] - G['ch3cl'][s]) * HARTREE for s in ORDER])
    dGr = np.array([(G['ch3nh3'][s] + G['cl'][s]
                     - G['nh3'][s] - G['ch3cl'][s]) * HARTREE for s in ORDER])
    rnc  = np.array([geo[s]['rnc']  for s in ORDER])
    rccl = np.array([geo[s]['rccl'] for s in ORDER])
    q    = np.array([geo[s]['q']    for s in ORDER])
    mu   = np.array([geo[s]['mu']   for s in ORDER])

    print('=== Main table ===')
    print(f"{'Medium':13s}{'eps':>9s}{'f(eps)':>8s}{'d(N-C)':>9s}{'d(C-Cl)':>9s}"
          f"{'q(Cl)':>8s}{'mu/D':>8s}{'nu_i':>9s}{'dG2':>9s}{'dGr':>9s}")
    for i, s in enumerate(ORDER):
        print(f"{NAME.get(s, s):13s}{e[i]:9.4f}{fe[i]:8.4f}{rnc[i]:9.3f}{rccl[i]:9.3f}"
              f"{q[i]:8.3f}{mu[i]:8.2f}{geo[s]['nu']:9.1f}{dG2[i]:9.2f}{dGr[i]:9.2f}")

    print('\n=== R2 of the linear fits ===')
    print(f"{'quantity':14s}{'vs eps':>9s}{'vs f(eps)':>11s}{'vs f, no gas':>14s}")
    for name, y in [('d(N-C)', rnc), ('d(C-Cl)', rccl), ('q(Cl)', q),
                    ('mu', mu), ('dG2', dG2), ('dG_r', dGr)]:
        print(f"{name:14s}{fit(e, y)[2]:9.4f}{fit(fe, y)[2]:11.4f}"
              f"{fit(fe[1:], y[1:])[2]:14.4f}")

    print('\n=== Predictive model of the barrier ===')
    m6, b6, r6 = fit(fe, dG2)
    m5, b5, r5 = fit(fe[1:], dG2[1:])
    print(f"all six points : dG2 = {m6:7.2f} f + {b6:6.2f}   R2 = {r6:.4f}")
    print(f"solvents only  : dG2 = {m5:7.2f} f + {b5:6.2f}   R2 = {r5:.4f}")
    print('\nleave-one-out validation:')
    for i, s in enumerate(ORDER):
        k = [j for j in range(len(ORDER)) if j != i]
        mm, bb, _ = fit(fe[k], dG2[k])
        pred = mm * fe[i] + bb
        print(f"  {NAME.get(s, s):13s} pred {pred:6.2f}  calc {dG2[i]:6.2f}  error {pred-dG2[i]:+6.2f}")

    print('\n=== Where the reaction turns exergonic ===')
    mr, br, _ = fit(fe, dGr)
    f0 = -br / mr
    print(f"dG_r = {mr:.1f} f + {br:.1f}  ->  zero at f = {f0:.4f}, eps = {eps_from_f(f0):.2f}")

    print('\n=== Complexation energy (the complex only exists at low eps) ===')
    for s in ['gas', 'Heptane', 'Benzene']:
        dE = (E['rc'][s] - E['nh3'][s] - E['ch3cl'][s]) * HARTREE
        dG = (G['rc'][s] - G['nh3'][s] - G['ch3cl'][s]) * HARTREE
        print(f"  {NAME.get(s, s):12s} dE = {dE:6.2f}   dG = {dG:6.2f} kcal/mol")

    print('\n=== Free-energy relationships (Hammond and Leffler) ===')
    _, _, r_h = fit(dGr, rnc)
    al, _, r_l = fit(dGr, dG2)
    print(f"d(N-C) vs dG_r : R2 = {r_h:.4f}")
    print(f"dG2    vs dG_r : R2 = {r_l:.4f}   alpha (Leffler) = {al:.3f}")

    print('\n=== Comparison with experiment ===')
    exp = [('CCl4', 31), ('chlorobenzene', 1200), ('acetonitrile', 12000), ('DMSO', 50000)]
    print(f"computed, heptane to acetonitrile: {dG2[1]-dG2[4]:.2f} kcal/mol")
    for name, krel in exp:
        print(f"  exp, hexane to {name:13s} k_rel = {krel:6d}  ->  ddG = {RT*np.log(krel):.2f} kcal/mol")

    np.savetxt('results.dat',
               np.column_stack([e, fe, rnc, rccl, q, mu, dG2, dGr]),
               header='eps f(eps) d_NC d_CCl q_Cl mu dG2 dG_r', fmt='%10.4f')
    print('\nWritten results.dat')

if __name__ == '__main__':
    main()
