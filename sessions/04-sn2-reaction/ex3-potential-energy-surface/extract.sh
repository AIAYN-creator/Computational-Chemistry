#!/bin/bash
# The 99 points of the relaxed scan: d(C-Cl), d(C-F) and energy, first in
# hartree (scan_raw.txt), then in kcal/mol above the lowest point and laid
# out as a grid for gnuplot (sep.dat).
# Usage: ./extract.sh
#
# The summary table at the end of the log is not used: its energies are
# glued together (-598.58982-598.59118...) and its points come in zigzag.
#
# awk reads the log line by line and its variables keep their value from
# one line to the next, like a notebook:
#   - every SCF Done overwrites e, so e always holds the latest energy;
#   - the optimised r1 is noted when its line appears;
#   - r5 is printed last in each point, so by then e and r1 are its own.
# Only the "Optimized Parameters" lines carry -DE/DX: the initial table
# ("! r1 1.3 Scan !") does not, so it is left out. Between r1 and -DE/DX
# there is a number, hence ".*" (anything), and the / of DE/DX is escaped
# because awk patterns are written between slashes.
awk '/SCF Done/ {e=$5} /! *r1 .* -DE\/DX/ {r1=$3} /! *r5 .* -DE\/DX/ {print $3, r1, e}' sep.log > scan_raw.txt

# The lowest energy of the grid: sort -n sorts as numbers, -k3 by column 3
emin=$(sort -n -k3 scan_raw.txt | head -1 | awk '{print $3}')

# Relative energy in kcal/mol. emin is negative, so E - emin is a sum.
# Then sort by C-Cl and, within each C-Cl, by C-F (this undoes the
# zigzag), and leave a blank line each time C-Cl changes: that is how
# gnuplot knows that a row of the grid has ended. prev is noted last,
# so the comparison is with the previous line, not with this one.
awk -v emin="$emin" '{print $1, $2, ($3 - emin) * 627.5}' scan_raw.txt |
	sort -k1,1n -k2,2n |
	awk '{ if (NR > 1 && $1 != prev) print ""; print; prev = $1 }' > sep.dat
