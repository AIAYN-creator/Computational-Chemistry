#!/bin/bash
# RHF dissociation curve of H2 relative to two isolated H atoms:
# DeltaE(r) = E(H2, r) - 2 E(H)
# Usage: ./extract.sh > results.txt
#
# A correct curve must reach DeltaE = 0 at long distance, so any leftover
# there is the error of the method.

# Energy of the isolated H atom (field 5 of the "SCF Done" line).
EH=$(grep "SCF Done" h_sto3g.log | awk '{print $5}')

# Keep E(H) on record as a comment, so the data stays two clean columns.
echo "# E(H) = $EH hartree"
echo "r(A) DeltaE(hartree)"

# Same scan-table reader as ex3-bond-scans/extract.sh.
# Bash only does integer arithmetic, so the subtraction happens in awk.
# -v eh="$EH" hands the shell value to awk as the variable eh. The awk
# program is in single quotes so that Bash leaves $2 and $3 alone: those
# are awk fields (r and E), not shell variables.
awk -v eh="$EH" '
	/Summary of the potential surface scan/ { s = 1; next }
	s && /^ *[0-9]+ +[-0-9.]+ +[-0-9.]+ *$/ { print $2, $3 - 2*eh; n++; next }
	s && n { exit }
' h2_rhf_sto3g.log
