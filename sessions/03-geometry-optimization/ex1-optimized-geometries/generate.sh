#!/bin/bash
# Builds the 3-21G, 6-31G* and 6-31G** optimisations from the STO-3G
# templates and runs them all.
#
# Only the four *_sto3g.com files are written by hand: the starting
# geometry is then identical for every basis set.

for f in *_sto3g.com; do
	# Strip the suffix to get the molecule: h2o_sto3g.com -> h2o
	m=${f%_sto3g.com}

	for b in 321g 631gs 631gss; do
		# Here the loop runs over the short file-name tags, and case maps
		# each one to the basis name Gaussian expects. "*" cannot go in a
		# file name comfortably, so 6-31G* becomes "gs" (G-star) and
		# 6-31G** becomes "gss".
		case $b in
			321g)   basis="3-21G" ;;
			631gs)  basis="6-31G*" ;;
			631gss) basis="6-31G**" ;;
		esac

		# Swap the basis in the route line and the title. "#" is used as
		# separator, as in every other generate.sh of the repository.
		sed "s#sto-3g#$basis#g" "$f" > "${m}_${b}.com"
	done
done

# Launch all 16 inputs (see ../run.sh).
../run.sh
