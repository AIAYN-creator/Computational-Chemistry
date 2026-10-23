#!/bin/bash
# Prints the optimised Z-matrix variables of every output.
# Usage: ./extract.sh > results.txt
#
# The variables have different names in each molecule (roo, roh, a, z for
# HOOH; rcc, rch for HCCH; rcn, rch for HCN), so instead of asking for
# them by name the script prints every line of the final table:
#
#                        !   Optimized Parameters   !
#                        ! (Angstroms and Degrees)  !
#  ----------------------                            ----------------------
#  !      Name          Value   Derivative information (Atomic Units)     !
#  ------------------------------------------------------------------------
#  !       roo         1.3964   -DE/DX =    0.0001                        !
#  !       roh         0.9492   -DE/DX =    0.0                           !

for f in *.log; do
	echo "== $f"
	# grep -A 12 takes the title and the 12 lines after it, enough for
	# the four variables of HOOH. The second grep keeps only the rows of
	# variables: "!", spaces, then a lowercase letter. The headers start
	# "! (" or "!      Name", so they do not match.
	grep -A 12 "Optimized Parameters" "$f" | grep "! *[a-z]"
done
