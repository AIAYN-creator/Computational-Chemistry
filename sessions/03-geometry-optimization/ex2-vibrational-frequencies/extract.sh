#!/bin/bash
# Harmonic frequencies, symmetry labels and IR intensities of every
# normal mode, plus the zero-point energy.
# Usage: ./extract.sh h2o_freq.log > frequencies.txt
#
# Gaussian prints the normal modes in blocks of up to three columns:
#
#                       1                      2                      3
#                      A1                     A1                     B2
#  Frequencies --   1826.6059              4070.3974              4188.6160
#  Red. masses --      1.0823                 1.0455                 1.0828
#  Frc consts  --      2.1276                10.2061                11.1933
#  IR Inten    --    107.2633                18.2076                58.0946
#
# Each quantity is a row and each mode a column, so the script turns every
# row into a list with one value per line and pastes the lists side by
# side. That works for any number of blocks, so for any molecule.

f=${1:-h2o_freq.log}

# Row -> one value per line. Labels have one or two words ("Frequencies",
# "IR Inten"), so the values cannot be found by a fixed field number.
# What every row has in common is the "--" right before the values:
# awk prints everything after the field that equals "--".
row() {
	grep "$1" "$f" | awk '{ v = 0; for (i = 1; i <= NF; i++) { if (v) print $i; if ($i == "--") v = 1 } }'
}

# The symmetry labels sit on the line just above "Frequencies".
# grep -B 1 brings that line along; the second grep drops the
# "Frequencies" lines themselves and the "--" separators grep -B adds
# between blocks.
labels() {
	grep -B 1 "Frequencies --" "$f" | grep -v -e "Frequencies" -e "^--$" \
		| awk '{ for (i = 1; i <= NF; i++) print $i }'
}

# Zero-point energy, field 3 of:
#  Zero-point correction=                           0.022977 (Hartree/Particle)
zpe=$(grep "Zero-point correction" "$f" | awk '{print $3}')
echo "# ZPE = $zpe hartree"

echo "mode symmetry freq(cm-1) IR(km/mol) force_const(mDyne/A)"
# seq numbers the modes; paste glues the five lists into columns.
n=$(row "Frequencies --" | wc -l)
paste -d ' ' <(seq 1 "$n") <(labels) <(row "Frequencies --") \
	<(row "IR Inten") <(row "Frc consts")
