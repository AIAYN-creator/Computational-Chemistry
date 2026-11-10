#!/bin/bash
# For each .log and each chained job (--Link1--), keeps the excited state
# with the LARGEST oscillator strength f: the allowed pi -> pi* transition.
# Output: molecule  method/basis  lambda(nm)  E(eV)  f
# Usage: ./extract.sh
#
# Each job of the chain prints its route line, starting with " #". awk
# notes it in r (first word, without the "#" and the "geom=..." part), so
# every excited state that follows is filed under its own method. The
# arrays best, nm and ev, indexed by r, keep the brightest state of each.
#
#  Excited State   2:      Singlet-A      7.2386 eV  171.28 nm  f=0.7550  <S**2>=0.000
#     $1     $2    $3         $4            $5   $6    $7   $8     $9
echo "Molecule Method lambda_nm E_eV f" > uv.dat
for m in *.log; do
    awk -v mol="${m%.log}" '
        /^ #/ { r = $1; sub(/^#/, "", r); sub(/geom=.*/, "", r) }   # route of each job
        /Excited State/ {
            f = substr($9, 3)                                       # "f=0.4880" -> 0.4880
            if (f + 0 > best[r] + 0) { best[r] = f; nm[r] = $7; ev[r] = $5 }
        }
        END { for (r in nm) print mol, r, nm[r], ev[r], best[r] }
    ' "$m" >> uv.dat
done
column -t uv.dat
