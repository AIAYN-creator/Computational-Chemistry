#!/bin/bash
# Energy of every point of the relaxed scan, written to scan.txt as
# "dihedral energy".
# Usage: ./extract.sh
#
# Each point of a relaxed scan is a full optimisation. Its energy is the
# last "SCF Done" line before Gaussian declares the optimisation
# converged with "Stationary point found":
#
#  SCF Done:  E(RHF) =  -997.030936218     A.U. after    8 cycles
#  ...
#     -- Stationary point found.
#
# awk keeps overwriting e with every SCF energy it reads, and prints the
# one it holds when the trigger line arrives. The n-th converged point
# has dihedral 200 - 20 n: 180, 160, ..., 0, -20, as set by
# "z3 180.0 S 10 -20.0" in the input.

awk '/SCF Done/ {e=$5} /Stationary point found/ {n++; print 200-20*n, e}' dce_scan.log > scan.txt
