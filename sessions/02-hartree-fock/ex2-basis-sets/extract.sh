#!/bin/bash
# Total energy, HOMO energy, dipole moment and Mulliken charges
# of the first two atoms for every output.
# Usage: ./extract.sh > results.txt

echo "file E(hartree) HOMO(hartree) mu(D) q1 q2"
for f in *.log; do
	E=$(grep "SCF Done" "$f" | tail -1 | awk '{print $5}')
	homo=$(grep "occ. eigenvalues" "$f" | tail -1 | awk '{print $NF}')
	mu=$(grep -A 1 "Dipole moment" "$f" | tail -1 | awk '{print $NF}')
	q1=$(grep -A 2 "Mulliken charges:" "$f" | tail -1 | awk '{print $3}')
	q2=$(grep -A 3 "Mulliken charges:" "$f" | tail -1 | awk '{print $3}')
	echo "$f $E $homo $mu $q1 $q2"
done
