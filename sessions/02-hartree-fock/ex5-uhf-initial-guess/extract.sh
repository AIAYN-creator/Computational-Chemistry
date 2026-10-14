#!/bin/bash
# UHF dissociation curves of H2 with and without guess=mix.
# Writes one file per curve: r, DeltaE = E(H2) - 2 E(H), and <S^2>
# before annihilation at each point.

EH=$(grep "SCF Done" h_sto3g.log | awk '{print $5}')

for f in h2_uhf_sto3g.log h2_uhfmix_sto3g.log; do
	out="${f%_sto3g.log}.dat"
	echo "r(A) DeltaE(hartree) S2" > "$out"
	paste -d ' ' \
		<(awk -v eh="$EH" '
			/Summary of the potential surface scan/ { s = 1; next }
			s && /^ *[0-9]+ +[-0-9.]+ +[-0-9.]+ *$/ { print $2, $3 - 2*eh; n++; next }
			s && n { exit }
		' "$f") \
		<(grep "S\*\*2 before annihilation" "$f" | awk '{print $4}' | tr -d ',') \
		>> "$out"
	echo "Written $out"
done
