#!/bin/bash
# Builds the B3LYP inputs from the HF ones and runs every job.
#
# Each B3LYP input is the HF input with two words changed, so the
# molecule, the basis set and the starting geometry are guaranteed to be
# the same: only the method differs.

for m in hooh hcch hcn; do
	# Two substitutions in one sed call, separated by ";":
	#   s/#hf/#b3lyp/   the method in the route line
	#   s/ HF$/ B3LYP/  the last word of the title; "$" anchors it to the
	#                   end of the line, so nothing else named HF is touched
	sed "s/#hf/#b3lyp/; s/ HF$/ B3LYP/" "${m}_hf.com" > "${m}_b3lyp.com"
done

# Launch all six inputs (see ../run.sh).
../run.sh
