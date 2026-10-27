#!/bin/bash
# Energy, free energy, dipole and the key dihedrals of the twelve glycine
# calculations, written to glycine.txt.
# Usage: ./extract.sh
#
# Every job is "opt=z-matrix freq", so each output has:
#  - the final SCF energy (last "SCF Done" line),
#  - the free energy at 298.15 K from the thermochemistry block,
#  - the dipole moment, whose total is the last field of the line
#    after "Dipole moment":
#      Dipole moment (field-independent basis, Debye):
#        X=   -0.8502   Y=    1.0247   Z=    0.0000   Tot=    1.3315
#  - the optimised Z-matrix variables, in lines that start with "!":
#      !      zncco        0.0      -DE/DX =    0.0   !

echo "calc E G mu zncco zccoh zhn zhn2" > glycine.txt

# gly_A_hf, gly_B_b3lyp_c1, ...: four conformers, two methods, and the
# re-optimisations without symmetry (_c1) of B and D
for f in gly_*.log; do
	c=${f%.log}
	e=$(grep "SCF Done" "$f" | tail -1 | awk '{print $5}')
	g=$(grep "Sum of electronic and thermal Free Energies" "$f" | awk '{print $NF}')
	mu=$(grep -A 1 "Dipole moment" "$f" | tail -1 | awk '{print $NF}')
	# The three dihedrals that tell the conformers apart, plus zhn2, the
	# second N-H dihedral, which only exists once the symmetry is removed.
	# The space after each name keeps zhn from also matching zhn2.
	z1=$(grep "! *zncco " "$f" | tail -1 | awk '{print $3}')
	z2=$(grep "! *zccoh " "$f" | tail -1 | awk '{print $3}')
	z3=$(grep "! *zhn " "$f" | tail -1 | awk '{print $3}')
	z4=$(grep "! *zhn2 " "$f" | tail -1 | awk '{print $3}')
	# Planar jobs have no zhn2: ${z4:--} writes "-" so the columns stay aligned
	echo "$c $e $g $mu $z1 $z2 $z3 ${z4:--}" >> glycine.txt
done
