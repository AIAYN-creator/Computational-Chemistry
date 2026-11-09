#!/bin/bash
# Energy, free energy and the three bond lengths of the reactant
# "complex" and the transition state in water, one row per output.
# Usage: ./extract.sh
#
# The variables have different names in each input (rccl, rcf, rch in the
# complex; r5, r1, r2 in the transition state), so one grep -E pattern
# looks for either: (rccl|r5) means "rccl or r5". Requiring -DE/DX after
# the value keeps only the optimised lines, and the / is escaped.

echo "Molecule Energy FEnergy d(ccl) d(cf) d(ch)" > results.txt

for m in *.log; do
	e=$(grep "SCF Done" "$m" | tail -1 | awk '{print $5}')
	fe=$(grep "Sum of electronic and thermal Free Energies" "$m" | awk '{print $NF}')
	dccl=$(grep -E "! *(rccl|r5) .* -DE\/DX" "$m" | tail -1 | awk '{print $3}')
	dcf=$(grep -E "! *(rcf|r1) .* -DE\/DX" "$m" | tail -1 | awk '{print $3}')
	dch=$(grep -E "! *(rch|r2) .* -DE\/DX" "$m" | tail -1 | awk '{print $3}')
	echo "${m%.log} $e $fe ${dccl:--} ${dcf:--}  ${dch:--}" >> results.txt
done
