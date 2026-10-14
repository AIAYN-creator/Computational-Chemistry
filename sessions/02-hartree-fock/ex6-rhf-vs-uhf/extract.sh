#!/bin/bash
# RHF and UHF (guess=mix) dissociation curves of H2 and LiH at HF/3-21G.
# Writes one file per curve: r, DeltaE relative to the separated atoms,
# and <S^2> before annihilation (UHF only).

# Atomic references
EH=$(grep "SCF Done" h_321g.log | awk '{print $5}')
ELI=$(grep "SCF Done" li_321g.log | awk '{print $5}')

scan() {  # scan <log> <reference energy>
	awk -v ref="$2" '
		/Summary of the potential surface scan/ { s = 1; next }
		s && /^ *[0-9]+ +[-0-9.]+ +[-0-9.]+ *$/ { print $2, $3 - ref; n++; next }
		s && n { exit }
	' "$1"
}

s2() {  # s2 <log>
	grep "S\*\*2 before annihilation" "$1" | awk '{print $4}' | tr -d ','
}

REF_H2=$(awk -v eh="$EH" 'BEGIN { printf "%.10f", 2*eh }')
REF_LIH=$(awk -v eh="$EH" -v eli="$ELI" 'BEGIN { printf "%.10f", eh + eli }')

for mol in h2 lih; do
	[ "$mol" = h2 ] && ref=$REF_H2 || ref=$REF_LIH

	echo "r(A) DeltaE(hartree)" > "${mol}_rhf.dat"
	scan "${mol}_rhf_321g.log" "$ref" >> "${mol}_rhf.dat"

	echo "r(A) DeltaE(hartree) S2" > "${mol}_uhfmix.dat"
	paste -d ' ' <(scan "${mol}_uhfmix_321g.log" "$ref") <(s2 "${mol}_uhfmix_321g.log") \
		>> "${mol}_uhfmix.dat"

	echo "Written ${mol}_rhf.dat ${mol}_uhfmix.dat"
done
