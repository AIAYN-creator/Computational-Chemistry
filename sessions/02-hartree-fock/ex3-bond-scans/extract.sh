#!/bin/bash
# Energy at every point of each bond-length scan.
# Usage: ./extract.sh > results.txt
#
# At the end of a scan Gaussian prints a summary table:
#
#  Summary of the potential surface scan:
#    N      r1          SCF
#  ----  ---------  -----------
#     1     0.6000     -1.10472
#     2     0.6300     -1.11271
#   ...
#    11     0.9000     -1.10836
#  ----  ---------  -----------
#
# The awk program below reads it whatever its length. An awk program is a
# list of "condition { action }" rules applied to every line, in order:
#
#   1. On the title line, raise a flag s ("inside the summary") and move on.
#   2. While s is up, a line that looks like a row (an integer, then two
#      numbers, nothing else) is printed and counted in n. The header and
#      dashed lines don't match, so they are skipped automatically.
#   3. While s is up, the first line that is not a row after at least one
#      row means the table is over: stop reading the file.
#
# (A first version used grep -A 13 ... | tail -11, which only works for
# exactly 11 points.)

echo "file r(A) E(hartree)"
for f in *.log; do
	awk -v name="$f" '
		/Summary of the potential surface scan/ { s = 1; next }
		s && /^ *[0-9]+ +[-0-9.]+ +[-0-9.]+ *$/ { print name, $2, $3; n++; next }
		s && n { exit }
	' "$f"
done
