#!/bin/bash
# Energy at every point of each bond-length scan.
# Usage: ./extract.sh > results.txt

echo "file r(A) E(hartree)"
for f in *.log; do
	awk -v name="$f" '
		/Summary of the potential surface scan/ { s = 1; next }
		s && /^ *[0-9]+ +[-0-9.]+ +[-0-9.]+ *$/ { print name, $2, $3; n++; next }
		s && n { exit }
	' "$f"
done
