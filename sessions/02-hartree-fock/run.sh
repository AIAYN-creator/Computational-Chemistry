#!/bin/bash
# Runs every .com in the current folder through Gaussian 09,
# skipping jobs that already terminated normally.
# Usage (from an exercise folder): ../run.sh
#
# Safe to re-run after an interruption: finished jobs are skipped and
# crashed or half-written ones are launched again.

# The shell expands *.com into the list of every input in the folder.
for f in *.com; do
	# ${f%.com} strips ".com" from the end of the name:
	# h2_rhf_321g.com -> h2_rhf_321g.log
	log="${f%.com}.log"

	# Gaussian writes "Normal termination" only on the last line of a job
	# that succeeded. Checking for it (instead of "does the .log exist?")
	# means a job that crashed halfway is not mistaken for a finished one.
	#   -q          quiet: print nothing, only report found / not found
	#   2>/dev/null hide the error grep gives when the .log does not exist yet
	if grep -q "Normal termination" "$log" 2>/dev/null; then
		echo "Already done: $log, skipping"
		continue    # go straight to the next input
	fi

	echo "Launching $f"
	# Gaussian reads the input from stdin and writes the output to stdout.
	g09 < "$f" > "$log"
done
