#!/bin/bash
# Energy, thermochemistry and the C-X bond length of the four species of
# the reaction, one row per output, written to results.txt.
# Usage: ./extract.sh
#
# Every job has "freq", so every output ends with the thermochemistry
# block at 298.15 K, where each value is the last field of its line:
#
#  Sum of electronic and zero-point Energies=           -499.053510
#  Sum of electronic and thermal Enthalpies=            -499.049596
#  Sum of electronic and thermal Free Energies=         -499.076105
#
# The ions are single atoms: no "opt", and no bond length to read.

echo "species E E+ZPE H G r_CCl r_CF" > results.txt

for m in *.log; do
	# Inside the loop, every command reads "$m", the file of this turn.
	# The last SCF Done is the energy at the final geometry.
	e=$(grep "SCF Done" "$m" | tail -1 | awk '{print $5}')
	ezpe=$(grep "Sum of electronic and zero-point Energies=" "$m" | awk '{print $NF}')
	h=$(grep "Sum of electronic and thermal Enthalpies=" "$m" | awk '{print $NF}')
	g=$(grep "Sum of electronic and thermal Free Energies=" "$m" | awk '{print $NF}')
	# Optimised bond lengths. Each exists in one molecule only, so the
	# variable stays empty in the other three outputs.
	dccl=$(grep "! *rccl " "$m" | tail -1 | awk '{print $3}')
	dcf=$(grep "! *rcf " "$m" | tail -1 | awk '{print $3}')
	# ${var:--} writes "-" for an empty value, so the columns stay aligned
	echo "${m%.log} $e $ezpe $h $g ${dccl:--} ${dcf:--}" >> results.txt
done
