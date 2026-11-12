#!/bin/bash
# One record per converged job, from every Gaussian .log in the folder.
# Usage: ./extract.sh
#
# Each log holds six jobs chained with --Link1-- (one per medium). awk
# keeps the latest value of everything it needs and prints a record when
# the job reaches its thermochemistry, then resets for the next job.
#   - The solvent and its dielectric constant are read from the "Solvent"
#     banner, not from the route line: the value used is the one the
#     program actually applied.
#   - "^ ESP charges:$" is anchored at both ends because three blocks of
#     the output contain that string, and only one is the ChelpG table.
#   - The record is printed on the free-energy line, not on "Normal
#     termination": a job that failed never reaches it, so failed jobs are
#     simply absent instead of appearing with half-read values.
echo "species solvent eps E_au G_au r_NC r_CCl q_Cl mu_D nu_imag" > jobs.dat

for f in *.log; do
    awk -v species="${f%.log}" '
        # --- solvent and the dielectric constant Gaussian used ---
        /^ Solvent  / {
            sol = $3; sub(/,$/, "", sol)
            split($0, p, "Eps="); eps = p[2] + 0
        }
        # --- electronic energy: always keep the latest ---
        /^ SCF Done:/ { e = $5 }
        # --- distances from the table of optimised parameters ---
        $1 == "!" && $2 == "r1" { rnc  = $3 }
        $1 == "!" && $2 == "r5" { rccl = $3 }
        # --- ChelpG charge on chlorine ---
        /^ ESP charges:$/ { inesp = 1; next }
        inesp && $2 == "Cl" { q = $3; inesp = 0 }
        inesp && /Sum of ESP/ { inesp = 0 }
        # --- dipole moment: on the line after its label ---
        /Dipole moment \(field-independent/ { getline; mu = $NF }
        # --- first frequency of the job (the imaginary one, if any) ---
        /^ Frequencies --/ { if (nu == "") nu = $3 }
        # --- end of a job: print the record and reset ---
        /Sum of electronic and thermal Free Energies=/ {
            printf "%s %s %s %s %s %s %s %s %s %s\n", \
                species, \
                (sol  == "" ? "gas" : sol), \
                (eps  == 0  ? "1.0" : eps), \
                e, $NF, \
                (rnc  == "" ? "-" : rnc), \
                (rccl == "" ? "-" : rccl), \
                (q    == "" ? "-" : q), \
                mu, \
                (nu + 0 < 0 ? nu : "-")
            sol = ""; eps = 0; rnc = ""; rccl = ""; q = ""; nu = ""
        }
    ' "$f" >> jobs.dat
done

column -t jobs.dat
