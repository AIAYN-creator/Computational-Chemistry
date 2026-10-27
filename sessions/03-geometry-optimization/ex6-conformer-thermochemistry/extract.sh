#!/bin/bash
# Dihedral, electronic energy, enthalpy and Gibbs free energy of the two
# conformers, at HF and B3LYP, written to thermo.txt.
# Usage: ./extract.sh
#
# The thermochemistry block that "freq" adds at the end of the output
# gives the sums directly, at 298.15 K and 1 atm:
#
#  Sum of electronic and thermal Enthalpies=            -996.962335
#  Sum of electronic and thermal Free Energies=         -996.996809
#
# The value is always the last field of the line, so awk '{print $NF}'
# reads it without counting fields.

echo "conf dihedral E H G" > thermo.txt

# HF conformers (the exercise) and B3LYP ones (the extension in the report)
for c in trans gauche trans_b3lyp gauche_b3lyp; do
	f=dce_${c}.log
	# Optimised Cl-C-C-Cl dihedral. The space after z3 makes sure the
	# pattern does not also match a longer name such as z30.
	z=$(grep "! *z3 " "$f" | tail -1 | awk '{print $3}')
	# Electronic energy at the final geometry
	e=$(grep "SCF Done" "$f" | tail -1 | awk '{print $5}')
	# Electronic energy plus thermal corrections: H and G
	h=$(grep "Sum of electronic and thermal Enthalpies" "$f" | awk '{print $NF}')
	g=$(grep "Sum of electronic and thermal Free Energies" "$f" | awk '{print $NF}')
	echo "$c $z $e $h $g" >> thermo.txt
done
