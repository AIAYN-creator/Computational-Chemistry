#!/bin/bash
# Extracts the energy table of a NAMD log and the averages of the production run.
#
# Usage:  ./extract.sh path/to/namd.log  output_folder
# Writes: output_folder/energies.dat    one row per ENERGY: line (every 100 steps)
#         output_folder/statistics.txt  means and standard deviations after 10 ps
#
# NAMD writes the column names once, in the ETITLE: line, and then one ENERGY:
# line every outputEnergies steps. Counting the word ENERGY: as $1:
#   $2 TS   $11 KINETIC   $12 TOTAL   $13 TEMP   $14 POTENTIAL   $15 TOTAL3

log=$1
out=${2:-.}

# 1. The energy table. The time goes in ps (TS is in steps of 1 fs).
{
    echo "# t_ps KINETIC TOTAL TEMP POTENTIAL TOTAL3   (energies in kcal/mol, T in K)"
    grep "^ENERGY:" "$log" | awk '{print $2/1000, $11, $12, $13, $14, $15}'
} > "$out/energies.dat"

# 2. Degrees of freedom, as NAMD counts them (printed once, in the header)
ndof=$(grep "DEGREES OF FREEDOM" "$log" | awk '{print $2}')

# 3. Averages over the production run: the first 10 ps are equilibration.
#    sd = sqrt(<x^2> - <x>^2), accumulated in a single pass.
grep "^ENERGY:" "$log" | awk -v ndof="$ndof" '
    $2 > 10000 {
        e += $12; ee += $12 * $12
        t += $13; tt += $13 * $13
        n++
    }
    END {
        me = e / n; mt = t / n
        sde = sqrt(ee / n - me * me); sdt = sqrt(tt / n - mt * mt)
        printf "samples (t > 10 ps)    %d\n", n
        printf "TOTAL (kcal/mol)       mean %.2f   sd %.2f\n", me, sde
        printf "TEMP (K)               mean %.2f   sd %.3f\n", mt, sdt
        printf "degrees of freedom     %d\n", ndof
        printf "sd(T)/<T> measured     %.5f\n", sdt / mt
        printf "sqrt(2/N) canonical    %.5f\n", sqrt(2 / ndof)
    }' > "$out/statistics.txt"

cat "$out/statistics.txt"
