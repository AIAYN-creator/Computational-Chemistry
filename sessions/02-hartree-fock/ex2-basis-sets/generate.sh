#!/bin/bash
# Builds the inputs for every basis set from the STO-3G templates
# and runs them all.

for mol in h2 hf co n2 ch4 h2o; do
	for b in 3-21G 4-31G "6-31G(d)" "6-31G(d,p)"; do
		n=$(echo "$b" | tr -d '(),-' | tr 'A-Z' 'a-z')
		sed "s#STO-3G#$b#g" "${mol}_sto3g.com" > "${mol}_${n}.com"
	done
done

../run.sh
