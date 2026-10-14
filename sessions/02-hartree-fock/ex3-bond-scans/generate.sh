#!/bin/bash
# Builds the 3-21G and 6-31G(d,p) scans from the STO-3G templates
# and runs them all.

for f in *_sto3g.com; do
	mol="${f%_sto3g.com}"
	for b in 3-21G "6-31G(d,p)"; do
		n=$(echo "$b" | tr -d '(),-' | tr 'A-Z' 'a-z')
		sed "s#STO-3G#$b#g" "$f" > "${mol}_${n}.com"
	done
done

../run.sh
