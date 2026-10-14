#!/bin/bash
# Builds the 3-21G and 6-31G(d,p) scans from the STO-3G templates
# and runs them all.
# Same template trick as ex2-basis-sets/generate.sh.

for f in *_sto3g.com; do
	# Strip the suffix to get the molecule: h2scan_sto3g.com -> h2scan
	mol="${f%_sto3g.com}"
	for b in 3-21G "6-31G(d,p)"; do
		# "6-31G(d,p)" -> "631gdp", safe for a file name
		n=$(echo "$b" | tr -d '(),-' | tr 'A-Z' 'a-z')
		# Swap the basis name everywhere in the template
		sed "s#STO-3G#$b#g" "$f" > "${mol}_${n}.com"
	done
done

# Launch all six scans (see ../run.sh).
../run.sh
