#!/bin/bash
# Optimised geometry, dipole moment, energy and number of optimisation
# steps for every output.
# Usage: ./extract.sh > results.txt
#
# At the end of an optimisation Gaussian prints the final values of the
# Z-matrix variables:
#
#                        !   Optimized Parameters   !
#  ...
#  !       r1          1.0025   -DE/DX =    0.0004                        !
#  !       a2        112.3568   -DE/DX =    0.0002                        !
#  !       z3        127.9308   -DE/DX =    0.0                           !
#
# The same "! name value" layout is also used for the initial parameters,
# so tail -1 keeps the last occurrence: the optimised one.

echo "mol basis r(A) angle(deg) mu(D) E(hartree) steps"
for f in *.log; do
	# Split the file name into molecule and basis tag:
	#   ${m%_*}  removes the shortest "_..." from the end:   h2o_631gs -> h2o
	#   ${m#*_}  removes the shortest "..._" from the start: h2o_631gs -> 631gs
	m=${f%.log}
	mol=${m%_*}
	basis=${m#*_}

	# A geometry that did not converge is not a result. Gaussian prints
	# "Stationary point found" only when every convergence criterion is met.
	if ! grep -q "Stationary point found" "$f"; then
		echo "$mol $basis NOT-CONVERGED"
		continue
	fi

	# Bond length r1 and angle a2, field 3 of their "!" lines.
	# "! *r1" matches "!", any number of spaces, then "r1".
	r=$(grep "! *r1" "$f" | tail -1 | awk '{print $3}')
	a=$(grep "! *a2" "$f" | tail -1 | awk '{print $3}')

	# Dipole moment: Tot, last field of the line after the header
	#  Dipole moment (field-independent basis, Debye):
	#     X=   0.0000    Y=   0.0000    Z=  -2.1477  Tot=   2.1477
	mu=$(grep -A 1 "Dipole moment" "$f" | tail -1 | awk '{print $NF}')

	# Energy at the final geometry, field 5 of the last "SCF Done" line.
	E=$(grep "SCF Done" "$f" | tail -1 | awk '{print $5}')

	# Every geometry step runs one SCF, so counting "SCF Done" lines gives
	# the number of geometries the optimiser visited. grep -c counts lines.
	steps=$(grep -c "SCF Done" "$f")

	# HF is diatomic and has no angle, so $a is empty. ${a:--} prints the
	# value of a, or "-" if it is empty, which keeps the columns aligned.
	echo "$mol $basis $r ${a:--} $mu $E $steps"
done
