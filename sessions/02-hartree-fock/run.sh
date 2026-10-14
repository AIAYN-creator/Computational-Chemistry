#!/bin/bash
# Runs every .com in the current folder through Gaussian 09,
# skipping jobs that already terminated normally.
# Usage (from an exercise folder): ../run.sh

for f in *.com; do
	log="${f%.com}.log"
	if grep -q "Normal termination" "$log" 2>/dev/null; then
		echo "Already done: $log, skipping"
		continue
	fi
	echo "Launching $f"
	g09 < "$f" > "$log"
done
