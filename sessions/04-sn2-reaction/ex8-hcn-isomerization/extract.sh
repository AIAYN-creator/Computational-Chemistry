#!/bin/bash
# Energies and geometry of HCN, CNH and the transition state, one row per
# output, written to results.txt, their frequencies to frequencies.txt,
# and the transition vector to transition_vector.txt.
# Usage: ./extract.sh
#
# The variables have different names in each input, so a column can come
# from more than one name: with grep -E, (rcn|rnc) means "rcn or rnc".
# The space after the name keeps "rch" from matching a longer name.

echo "species E E+ZPE H G r_CN r_CH r_NH angle" > results.txt
echo "species frequencies_cm-1" > frequencies.txt

for m in *.log; do
	# One SCF Done per optimisation step: the last one is the final energy
	e=$(grep "SCF Done" "$m" | tail -1 | awk '{print $5}')
	# Each of these appears once, and $NF is the last field
	ez=$(grep "Sum of electronic and zero-point Energies=" "$m" | awk '{print $NF}')
	h=$(grep "Sum of electronic and thermal Enthalpies=" "$m" | awk '{print $NF}')
	fe=$(grep "Sum of electronic and thermal Free Energies=" "$m" | awk '{print $NF}')
	dcn=$(grep -E "! *(rcn|rnc) " "$m" | tail -1 | awk '{print $3}')
	dch=$(grep "! *rch " "$m" | tail -1 | awk '{print $3}')
	dnh=$(grep "! *rnh " "$m" | tail -1 | awk '{print $3}')
	a=$(grep "! *a1 " "$m" | tail -1 | awk '{print $3}')
	# Not every species has every variable: "-" keeps the columns aligned
	echo "${m%.log} $e $ez $h $fe $dcn ${dch:--} ${dnh:--} ${a:--}" >> results.txt
	# Three frequencies per line, from field 3 on. Negative means imaginary.
	fr=$(grep "Frequencies --" "$m" | awk '{for(i=3;i<=NF;i++) printf "%s ", $i}')
	echo "${m%.log} $fr" >> frequencies.txt
done

# The first mode of the transition state, next to the geometry it refers
# to: atomic number, x and y of each atom, then its displacement in x and y.
# Both tables list C, H, N in the same order, and z is 0 (the molecule is
# in the xy plane). Only the first "Atom  AN" block holds the first mode.
echo "Z x y dx dy" > transition_vector.txt
paste -d ' ' \
	<(grep -A 7 "Standard orientation" ts_hcn.log | tail -3 | awk '{print $2, $4, $5}') \
	<(grep -A 3 "Atom  AN" ts_hcn.log | head -4 | tail -3 | awk '{print $3, $4}') \
	>> transition_vector.txt
