#!/bin/bash
# Energy of every point of the relaxed scan, written to scan.txt as
# "dihedral energy".
# Usage: ./extract.sh
#
# The same awk as in Ex. 5: each point of a relaxed scan is a full
# optimisation, and its energy is the last "SCF Done" line before
# "Stationary point found". awk keeps overwriting e with every SCF energy
# and prints the one it holds when the trigger line arrives.
#
# The difference is the direction. This scan climbs from 0 in steps of
# +20 ("z3 0. S 9 20.0" in the input), so the n-th converged point has
# dihedral 20 n, counting from n = 0. Printing BEFORE n++ makes the first
# point come out as 0.

awk '/SCF Done/ {e=$5} /Stationary point found/ {print 20*n, e; n++}' fluoromethanol_scan.log > scan.txt
