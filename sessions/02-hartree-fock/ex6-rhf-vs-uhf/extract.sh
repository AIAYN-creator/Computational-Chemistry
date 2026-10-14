#!/bin/bash
# RHF and UHF (guess=mix) dissociation curves of H2 and LiH at HF/3-21G.
# Writes one file per curve: r, DeltaE relative to the separated atoms,
# and <S^2> before annihilation (UHF only).
#
# H2 and LiH need the same operations, so they are written once as
# functions and the loop only picks the right reference energy.

# Atomic references (field 5 of the "SCF Done" line)
EH=$(grep "SCF Done" h_321g.log | awk '{print $5}')
ELI=$(grep "SCF Done" li_321g.log | awk '{print $5}')

# scan <log> <reference energy>
# Prints "r DeltaE" for every point of the scan summary table (same awk
# reader as ex3-bond-scans/extract.sh). Inside a function, $1 and $2 are
# its own arguments. Inside the single-quoted awk program, $2 and $3 are
# awk fields instead, which is why the reference goes in through -v.
scan() {
	awk -v ref="$2" '
		/Summary of the potential surface scan/ { s = 1; next }
		s && /^ *[0-9]+ +[-0-9.]+ +[-0-9.]+ *$/ { print $2, $3 - ref; n++; next }
		s && n { exit }
	' "$1"
}

# s2 <log>
# Prints <S^2> before annihilation, one line per converged point:
#   S**2 before annihilation     1.0000,   after     0.0000
s2() {
	grep "S\*\*2 before annihilation" "$1" | awk '{print $4}' | tr -d ','
}

# Bash arithmetic is integer-only, so the sums go through awk. With no
# file to read, the work happens in a BEGIN block.
REF_H2=$(awk -v eh="$EH" 'BEGIN { printf "%.10f", 2*eh }')
REF_LIH=$(awk -v eh="$EH" -v eli="$ELI" 'BEGIN { printf "%.10f", eh + eli }')

for mol in h2 lih; do
	# Short if/else: if the test succeeds run the && part, otherwise the || part
	[ "$mol" = h2 ] && ref=$REF_H2 || ref=$REF_LIH

	echo "r(A) DeltaE(hartree)" > "${mol}_rhf.dat"
	scan "${mol}_rhf_321g.log" "$ref" >> "${mol}_rhf.dat"

	# Energies and <S^2> side by side (see ex5-uhf-initial-guess/extract.sh)
	echo "r(A) DeltaE(hartree) S2" > "${mol}_uhfmix.dat"
	paste -d ' ' <(scan "${mol}_uhfmix_321g.log" "$ref") <(s2 "${mol}_uhfmix_321g.log") \
		>> "${mol}_uhfmix.dat"

	echo "Written ${mol}_rhf.dat ${mol}_uhfmix.dat"
done
