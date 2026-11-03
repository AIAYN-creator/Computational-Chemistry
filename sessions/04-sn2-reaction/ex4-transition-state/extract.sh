#!/bin/bash
# Energies, geometry, frequencies and transition vector of the SN2
# transition state: the grep commands of the exercise, run on ts_sn2.log.
# Usage: ./extract.sh
#
# Writes results.txt (one row, same columns as Ex. 2 plus the angles),
# frequencies.txt and transition_vector.txt.

m=ts_sn2.log

# One SCF Done per optimisation step: the last one is the final energy
e=$(grep "SCF Done" "$m" | tail -1 | awk '{print $5}')
ez=$(grep "Sum of electronic and zero-point Energies=" "$m" | awk '{print $NF}')
h=$(grep "Sum of electronic and thermal Enthalpies=" "$m" | awk '{print $NF}')
fe=$(grep "Sum of electronic and thermal Free Energies=" "$m" | awk '{print $NF}')
# r5 is C-Cl and r1 is C-F. a2 is one H-C-F angle (the other two are
# equal), and a5 = 90 puts Cl on the F-C axis. The space after the name
# keeps r1 from also matching a longer name.
dccl=$(grep "! *r5 " "$m" | tail -1 | awk '{print $3}')
dcf=$(grep "! *r1 " "$m" | tail -1 | awk '{print $3}')
dch=$(grep "! *r2 " "$m" | tail -1 | awk '{print $3}')
a2=$(grep "! *a2 " "$m" | tail -1 | awk '{print $3}')
a5=$(grep "! *a5 " "$m" | tail -1 | awk '{print $3}')
echo "species E E+ZPE H G r_CCl r_CF r_CH a_HCF a_ClCX" > results.txt
echo "ts_sn2 $e $ez $h $fe $dccl $dcf $dch $a2 $a5" >> results.txt

# Three frequencies per line, from field 3 on. Negative means imaginary.
echo "frequencies_cm-1" > frequencies.txt
grep "Frequencies --" "$m" | awk '{for(i=3;i<=NF;i++) printf "%s ", $i} END {print ""}' >> frequencies.txt

# The imaginary mode next to the geometry it refers to: atomic number and
# x, y, z of each of the 6 real atoms (the dummy atom has no coordinates),
# then its displacement. Only the first "Atom  AN" block holds mode 1.
echo "Z x y z dx dy dz" > transition_vector.txt
paste -d ' ' \
	<(grep -A 10 "Standard orientation" "$m" | tail -6 | awk '{print $2, $4, $5, $6}') \
	<(grep -A 6 "Atom  AN" "$m" | head -7 | tail -6 | awk '{print $3, $4, $5}') \
	>> transition_vector.txt
