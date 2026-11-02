#!/bin/bash
# Energy, thermochemistry and bond lengths of the two ion-dipole
# complexes, one row per output, written to results.txt.
# Usage: ./extract.sh
#
# The optimised variables are read from the table that ends each
# optimisation, in lines that start with "!":
#
#  !      rccl         1.8635   -DE/DX =   -0.0003                        !
#
# The value is field 3; field 6 is the gradient, about 0 at a minimum.
# The final summary of the log (the "archive") also contains rccl, so a
# plain grep "rccl" | tail -1 lands there. The "!" avoids it, and " *"
# (a regular expression: any number of spaces) matches the alignment.

echo "species E E+ZPE H G r_CCl r_CF r_CH" > results.txt

for m in *.log; do
	# One SCF Done per optimisation step: the last one is the final energy
	e=$(grep "SCF Done" "$m" | tail -1 | awk '{print $5}')
	# Each of these appears once. $NF is the last field, however many
	# words the label has.
	ez=$(grep "Sum of electronic and zero-point Energies=" "$m" | awk '{print $NF}')
	h=$(grep "Sum of electronic and thermal Enthalpies=" "$m" | awk '{print $NF}')
	fe=$(grep "Sum of electronic and thermal Free Energies=" "$m" | awk '{print $NF}')
	dccl=$(grep "! *rccl" "$m" | tail -1 | awk '{print $3}')
	dcf=$(grep "! *rcf" "$m" | tail -1 | awk '{print $3}')
	dch=$(grep "! *rch" "$m" | tail -1 | awk '{print $3}')
	echo "${m%.log} $e $ez $h $fe $dccl $dcf $dch" >> results.txt
done
