#!/bin/bash
# RHF dissociation curve of H2 relative to two isolated H atoms:
# DeltaE(r) = E(H2, r) - 2 E(H)
# Usage: ./extract.sh > results.txt

EH=$(grep "SCF Done" h_sto3g.log | awk '{print $5}')

echo "# E(H) = $EH hartree"
echo "r(A) DeltaE(hartree)"
awk -v eh="$EH" '
	/Summary of the potential surface scan/ { s = 1; next }
	s && /^ *[0-9]+ +[-0-9.]+ +[-0-9.]+ *$/ { print $2, $3 - 2*eh; n++; next }
	s && n { exit }
' h2_rhf_sto3g.log
