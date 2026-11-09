#!/bin/bash
# The SN2 in water (PCM): energies of every species, and the relaxed scan.
# Usage: ./extract.sh
#
# Writes results.txt (E, H, G and the lowest frequency of each species),
# sep_pcm_raw.txt and sep_pcm.dat (the scan, as in Ex. 3) and
# scan_stopped.txt (the scan points whose optimisation did not converge).

echo "species E H G lowest_freq" > results.txt

for m in f_anion ch3cl f_ch3cl ts_sn2 ch3f_cl ch3f cl_anion; do
	e=$(grep "SCF Done" "$m.log" | tail -1 | awk '{print $5}')
	h=$(grep "Sum of electronic and thermal Enthalpies=" "$m.log" | awk '{print $NF}')
	g=$(grep "Sum of electronic and thermal Free Energies=" "$m.log" | awk '{print $NF}')
	# The first frequency is the lowest: negative means imaginary
	nu=$(grep "Frequencies --" "$m.log" | head -1 | awk '{print $3}')
	# f_ch3cl never finished (the ion drifts away), so it has no H, G or
	# frequencies; a single atom has no frequencies at all
	echo "$m $e ${h:--} ${g:--} ${nu:--}" >> results.txt
done

# The scan, with the same notebook awk as Ex. 3
awk '/SCF Done/ {e=$5} /! *r1 .* -DE\/DX/ {r1=$3} /! *r5 .* -DE\/DX/ {print $3, r1, e}' sep_pcm.log > sep_pcm_raw.txt
emin=$(sort -n -k3 sep_pcm_raw.txt | head -1 | awk '{print $3}')
awk -v emin="$emin" '{print $1, $2, ($3 - emin) * 627.5}' sep_pcm_raw.txt |
	sort -k1,1n -k2,2n |
	awk '{ if (NR > 1 && $1 != prev) print ""; print; prev = $1 }' > sep_pcm.dat

# A point that runs out of steps prints "Optimization stopped" instead of
# "Stationary point found", and its parameters are still printed: flag it
# and report its r5 and r1 when they come.
awk '/Optimization stopped/ {bad=1} /! *r1 .* -DE\/DX/ {r1=$3}
	/! *r5 .* -DE\/DX/ {if (bad) print $3, r1; bad=0}' sep_pcm.log > scan_stopped.txt
