#!/bin/bash
# Builds the inputs for every basis set from the STO-3G templates
# and runs them all.
#
# Only the six *_sto3g.com files are written by hand. The other 24 are
# copies with the basis name swapped, so the geometry is guaranteed to be
# identical across the series: any change in the results comes from the
# basis alone.

for mol in h2 hf co n2 ch4 h2o; do
	# "6-31G(d)" and "6-31G(d,p)" are quoted: unquoted parentheses mean
	# something else to Bash.
	for b in 3-21G 4-31G "6-31G(d)" "6-31G(d,p)"; do
		# Turn the basis name into something safe for a file name:
		#   tr -d '(),-'     delete ( ) , -      "6-31G(d,p)" -> "631Gdp"
		#   tr 'A-Z' 'a-z'   lowercase           "631Gdp"     -> "631gdp"
		n=$(echo "$b" | tr -d '(),-' | tr 'A-Z' 'a-z')

		# s#old#new#g replaces every "STO-3G" (route line and title) with
		# the new basis. "#" is the separator instead of "/", a habit that
		# avoids clashes with slashes. Double quotes let Bash put the value
		# of $b in before sed runs.
		sed "s#STO-3G#$b#g" "${mol}_sto3g.com" > "${mol}_${n}.com"
	done
done

# Launch all 30 inputs (see ../run.sh).
../run.sh
