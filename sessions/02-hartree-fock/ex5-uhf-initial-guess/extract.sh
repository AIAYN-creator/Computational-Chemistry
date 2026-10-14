#!/bin/bash
# UHF dissociation curves of H2 with and without guess=mix.
# Writes one file per curve: r, DeltaE = E(H2) - 2 E(H), and <S^2>
# before annihilation at each point.
#
# <S^2> tells which solution the SCF actually found: 0 for the restricted
# (closed-shell) one, close to 1 for the broken-symmetry one at long r.

# Energy of the isolated H atom (field 5 of the "SCF Done" line).
EH=$(grep "SCF Done" h_sto3g.log | awk '{print $5}')

for f in h2_uhf_sto3g.log h2_uhfmix_sto3g.log; do
	# h2_uhfmix_sto3g.log -> h2_uhfmix.dat
	out="${f%_sto3g.log}.dat"
	echo "r(A) DeltaE(hartree) S2" > "$out"

	# Two lists with one entry per scan point, in the same order, glued
	# side by side with paste (-d ' ' uses a space instead of a tab).
	# <( ... ) is process substitution: paste reads each command's output
	# as if it were a file, with no temporary files needed.
	#
	#   1st column block: r and DeltaE from the scan summary table
	#                     (same awk reader as ex3-bond-scans/extract.sh)
	#   2nd column block: <S^2>, printed by Gaussian once per converged point:
	#     S**2 before annihilation     1.0000,   after     0.0000
	#     field 4 is the value; tr -d ',' removes the trailing comma.
	#     \*\* escapes the asterisks, which grep would read as "repeat".
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
