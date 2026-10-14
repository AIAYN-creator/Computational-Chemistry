#!/bin/bash
# Total energy, HOMO energy, dipole moment and Mulliken charges
# of the first two atoms for every output.
# Usage: ./extract.sh > results.txt
#
# Every value follows the same recipe:
#   grep  find a line by a piece of text that always comes with it
#   tail  keep the last occurrence (the converged result)
#   awk   take the field by position: $1, $2, ... and $NF = last field

echo "file E(hartree) HOMO(hartree) mu(D) q1 q2"
for f in *.log; do
	# Total energy, field 5:
	#  SCF Done:  E(RHF) =  -76.0229850829     A.U. after   10 cycles
	#   $1    $2    $3  $4        $5
	E=$(grep "SCF Done" "$f" | tail -1 | awk '{print $5}')

	# HOMO: occupied orbital energies are printed in ascending order, five
	# per line, so the HOMO is the last field of the last line:
	#  Alpha  occ. eigenvalues --  -20.56112  -1.33890  ...  -0.49696
	homo=$(grep "occ. eigenvalues" "$f" | tail -1 | awk '{print $NF}')

	# Dipole moment: the numbers are on the line AFTER the header,
	# so grep -A 1 brings it along and tail -1 keeps only that line.
	# Tot is its last field:
	#  Dipole moment (field-independent basis, Debye):
	#     X=   0.0000    Y=   0.0000    Z=  -2.1870  Tot=   2.1870
	mu=$(grep -A 1 "Dipole moment" "$f" | tail -1 | awk '{print $NF}')

	# Mulliken charges: after the header comes a column label line, then
	# one line per atom, with the charge in field 3:
	#  Mulliken charges:
	#                1
	#      1  O   -0.674582     <- 2 lines below the header (atom 1)
	#      2  H    0.337291     <- 3 lines below the header (atom 2)
	q1=$(grep -A 2 "Mulliken charges:" "$f" | tail -1 | awk '{print $3}')
	q2=$(grep -A 3 "Mulliken charges:" "$f" | tail -1 | awk '{print $3}')

	echo "$f $E $homo $mu $q1 $q2"
done
