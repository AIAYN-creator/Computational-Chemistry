# Bash for Gaussian: a field guide

Most of the work in a computational chemistry course does not happen inside the quantum chemistry program. It happens around it: writing dozens of nearly identical inputs, launching them, checking they finished, and digging a handful of numbers out of output files thousands of lines long. Doing that by hand is slow and error-prone. Doing it with a few lines of Bash makes it fast and repeatable, and a mistake gets fixed once instead of thirty times.

This guide is built from the scripts in this repository. Each section explains one pattern on the real Gaussian output it reads, and ends with **In the code**: links to the exact lines of every script that uses it. The scripts themselves are commented line by line, so either one can be the entry point.

| Script | Patterns |
|---|---|
| **Session 02** | |
| [`run.sh`](../sessions/02-hartree-fock/run.sh) (same file in every session) | [1](#1-running-every-job-in-a-folder-safely) |
| [`ex2-basis-sets/generate.sh`](../sessions/02-hartree-fock/ex2-basis-sets/generate.sh) | [5](#5-generating-inputs-from-a-template) |
| [`ex2-basis-sets/extract.sh`](../sessions/02-hartree-fock/ex2-basis-sets/extract.sh) | [2](#2-pulling-one-number-out-of-a-log) |
| [`ex3-bond-scans/generate.sh`](../sessions/02-hartree-fock/ex3-bond-scans/generate.sh) | [5](#5-generating-inputs-from-a-template) |
| [`ex3-bond-scans/extract.sh`](../sessions/02-hartree-fock/ex3-bond-scans/extract.sh) | [3](#3-reading-a-table-of-any-length-with-awk) |
| [`ex4-rhf-dissociation/extract.sh`](../sessions/02-hartree-fock/ex4-rhf-dissociation/extract.sh) | [2](#2-pulling-one-number-out-of-a-log), [3](#3-reading-a-table-of-any-length-with-awk), [4](#4-doing-arithmetic-with-shell-values) |
| [`ex5-uhf-initial-guess/extract.sh`](../sessions/02-hartree-fock/ex5-uhf-initial-guess/extract.sh) | [2](#2-pulling-one-number-out-of-a-log), [3](#3-reading-a-table-of-any-length-with-awk), [4](#4-doing-arithmetic-with-shell-values), [6](#6-gluing-columns-together) |
| [`ex6-rhf-vs-uhf/extract.sh`](../sessions/02-hartree-fock/ex6-rhf-vs-uhf/extract.sh) | [2](#2-pulling-one-number-out-of-a-log), [3](#3-reading-a-table-of-any-length-with-awk), [4](#4-doing-arithmetic-with-shell-values), [6](#6-gluing-columns-together), [7](#7-functions-write-it-once) |
| **Session 03** | |
| [`ex1-optimized-geometries/generate.sh`](../sessions/03-geometry-optimization/ex1-optimized-geometries/generate.sh) | [5](#5-generating-inputs-from-a-template), [8](#8-mapping-names-with-case), [9](#9-splitting-file-names-and-default-values) |
| [`ex4-hf-vs-b3lyp/generate.sh`](../sessions/03-geometry-optimization/ex4-hf-vs-b3lyp/generate.sh) | [5](#5-generating-inputs-from-a-template) |
| [`ex4-hf-vs-b3lyp/extract.sh`](../sessions/03-geometry-optimization/ex4-hf-vs-b3lyp/extract.sh) | [2](#2-pulling-one-number-out-of-a-log) |
| [`ex1-optimized-geometries/extract.sh`](../sessions/03-geometry-optimization/ex1-optimized-geometries/extract.sh) | [1](#1-running-every-job-in-a-folder-safely), [2](#2-pulling-one-number-out-of-a-log), [9](#9-splitting-file-names-and-default-values) |

**Patterns**

1. [Running every job in a folder, safely](#1-running-every-job-in-a-folder-safely)
2. [Pulling one number out of a log](#2-pulling-one-number-out-of-a-log)
3. [Reading a table of any length with awk](#3-reading-a-table-of-any-length-with-awk)
4. [Doing arithmetic with shell values](#4-doing-arithmetic-with-shell-values)
5. [Generating inputs from a template](#5-generating-inputs-from-a-template)
6. [Gluing columns together](#6-gluing-columns-together)
7. [Functions: write it once](#7-functions-write-it-once)
8. [Mapping names with case](#8-mapping-names-with-case)
9. [Splitting file names and default values](#9-splitting-file-names-and-default-values)
10. [Bugs worth remembering](#10-bugs-worth-remembering)

---

## 1. Running every job in a folder, safely

```bash
for f in *.com; do
	log="${f%.com}.log"
	if grep -q "Normal termination" "$log" 2>/dev/null; then
		echo "Already done: $log, skipping"
		continue
	fi
	echo "Launching $f"
	g09 < "$f" > "$log"
done
```

| Piece | What it does |
|---|---|
| `for f in *.com` | Loops over every input in the folder. The shell expands `*.com` into the list of file names. |
| `${f%.com}.log` | Parameter expansion: `%` removes the shortest match of `.com` from the end of `$f`, so `h2_rhf.com` → `h2_rhf.log`. |
| `grep -q` | *Quiet*: prints nothing and only reports, through its exit status, whether the text was found. That is all an `if` needs. |
| `2>/dev/null` | Throws away the error message `grep` prints when the `.log` does not exist yet (the first time a job runs). |
| `continue` | Jumps to the next file. |
| `g09 < in > out` | Gaussian reads the input from standard input and writes the output to standard output. |

**Why check for `Normal termination` and not just whether the `.log` exists?** A job that crashes, or that is killed because the session closed, leaves a `.log` behind. If the check is only "does the file exist?", that job is never re-run, and its half-written output quietly ends up in the results. Gaussian writes `Normal termination` only on its very last line, and only on success:

```
 Normal termination of Gaussian 09 at Mon Oct  5 19:52:56 2026.
```

With this check, the script can be launched again after any interruption and it picks up where it stopped.

**In the code:** [`run.sh` L10–L28](../sessions/02-hartree-fock/run.sh#L10-L28), called by [`ex2/generate.sh` L28](../sessions/02-hartree-fock/ex2-basis-sets/generate.sh#L28) and [`ex3/generate.sh` L18](../sessions/02-hartree-fock/ex3-bond-scans/generate.sh#L18), and directly as `../run.sh` in Ex. 4–6. Session 03 has an identical copy, called from [`S03 ex1/generate.sh` L30](../sessions/03-geometry-optimization/ex1-optimized-geometries/generate.sh#L30). The same idea, applied to results instead of jobs, appears in [`S03 ex1/extract.sh` L29–L32](../sessions/03-geometry-optimization/ex1-optimized-geometries/extract.sh#L29-L32): an optimisation that never printed `Stationary point found` is reported as `NOT-CONVERGED` instead of being read as if it had finished.

---

## 2. Pulling one number out of a log

The pattern is always the same: **find a line by text that always comes with it, then take the field by position.**

```bash
grep "some fixed text" file.log | tail -1 | awk '{print $N}'
```

`awk` splits each line into fields separated by whitespace: `$1`, `$2`, …, and `$NF` is the last one (`NF` is the number of fields). `tail -1` keeps the last occurrence, because many blocks repeat during optimisations and scans, and the final one is the converged result.

**Total energy**: field 5 of the `SCF Done` line.

```
 SCF Done:  E(RHF) =  -76.0229850829     A.U. after   10 cycles
  $1    $2    $3   $4       $5           $6  ...
```
```bash
grep "SCF Done" "$f" | tail -1 | awk '{print $5}'
```

**HOMO energy**: the last number of the last line of occupied eigenvalues. Gaussian lists them in ascending order, five per line, so the HOMO is always at the very end.

```
 Alpha  occ. eigenvalues --  -20.56112  -1.33890  -0.70192  -0.56827  -0.49696
```
```bash
grep "occ. eigenvalues" "$f" | tail -1 | awk '{print $NF}'
```

**Dipole moment**: the value is on the line *after* the header, so `grep -A 1` (one line **A**fter) brings it along, `tail -1` keeps just that line, and `Tot` is its last field.

```
 Dipole moment (field-independent basis, Debye):
    X=              0.0000    Y=              0.0000    Z=             -2.1870  Tot=              2.1870
```
```bash
grep -A 1 "Dipole moment" "$f" | tail -1 | awk '{print $NF}'
```

**Mulliken charges**: the charge of atom *n* is *n* + 1 lines below the header (the extra line is a column label), in field 3.

```
 Mulliken charges:
               1
     1  O   -0.674582        ← grep -A 2 | tail -1
     2  H    0.337291        ← grep -A 3 | tail -1
```

**⟨Ŝ²⟩ of a UHF wavefunction**: field 4, with a trailing comma that `tr -d ','` removes. Gaussian prints this line once per converged point, so a scan gives a whole list.

```
 S**2 before annihilation     1.0000,   after     0.0000
```
```bash
grep "S\*\*2 before annihilation" "$f" | awk '{print $4}' | tr -d ','
```

The `*` must be escaped as `\*` because, in a `grep` pattern, `*` means "repeat the previous character".

**Optimised geometry**: at the end of an optimisation Gaussian prints the final value of every Z-matrix variable, each on a line that starts with `!`. The same layout is used for the *initial* parameters, so `tail -1` is what picks the optimised value.

```
 !       r1          1.0025   -DE/DX =    0.0004                        !
 !       a2        112.3568   -DE/DX =    0.0002                        !
```
```bash
grep "! *r1" "$f" | tail -1 | awk '{print $3}'
```

` *` in the pattern means "any number of spaces", so `"! *r1"` matches however much padding Gaussian puts between `!` and the name.

**Counting instead of reading**: `grep -c` prints how many lines match. Every geometry step of an optimisation runs one SCF, so counting `SCF Done` lines gives the number of steps.

```bash
grep -c "SCF Done" "$f"
```

**In the code:**
- Energy, HOMO, dipole and Mulliken charges: [`ex2/extract.sh` L16–L37](../sessions/02-hartree-fock/ex2-basis-sets/extract.sh#L16-L37)
- Atomic reference energies: [`ex4/extract.sh` L10](../sessions/02-hartree-fock/ex4-rhf-dissociation/extract.sh#L10), [`ex5/extract.sh` L10](../sessions/02-hartree-fock/ex5-uhf-initial-guess/extract.sh#L10), [`ex6/extract.sh` L10–L11](../sessions/02-hartree-fock/ex6-rhf-vs-uhf/extract.sh#L10-L11)
- Every optimised variable at once, whatever its name (`grep "! *[a-z]"` keeps the variable rows and drops the headers): [`S03 ex4/extract.sh` L23](../sessions/03-geometry-optimization/ex4-hf-vs-b3lyp/extract.sh#L23)
- Optimised r and angle, dipole, energy and step count: [`S03 ex1/extract.sh` L36–L49](../sessions/03-geometry-optimization/ex1-optimized-geometries/extract.sh#L36-L49)
- ⟨Ŝ²⟩: [`ex5/extract.sh` L34](../sessions/02-hartree-fock/ex5-uhf-initial-guess/extract.sh#L34), [`ex6/extract.sh` L29–L31](../sessions/02-hartree-fock/ex6-rhf-vs-uhf/extract.sh#L29-L31)

---

## 3. Reading a table of any length with awk

At the end of a scan, Gaussian prints a summary table:

```
 Summary of the potential surface scan:
   N      r1          SCF
 ----  ---------  -----------
    1     0.6000     -1.10472
    2     0.6300     -1.11271
  ...
   11     0.9000     -1.10836
 ----  ---------  -----------
```

**First version:** `grep -A 13 "Summary of the potential" | tail -11`. Take 13 lines after the title and keep the last 11. It works, but the numbers 13 and 11 depend on the scan having exactly 11 points, so every scan of a different length needs its own pair of numbers. A wrong one silently cuts the table or lets in a line of dashes.

**Final version:** a small state machine in `awk`, which reads the table whatever its length:

```bash
awk '
	/Summary of the potential surface scan/ { s = 1; next }                 # (1)
	s && /^ *[0-9]+ +[-0-9.]+ +[-0-9.]+ *$/ { print $2, $3; n++; next }   # (2)
	s && n { exit }                                                         # (3)
' file.log
```

An `awk` program is a list of `condition { action }` rules, applied to every line in order.

1. When the line contains the title, raise a flag `s` (for *in summary*) and move on to the next line.
2. If the flag is up and the line looks like a table row (an integer, then two numbers, and nothing else), print *r* and *E*, and count it in `n`.
3. If the flag is up, at least one row has been read, and this line is *not* a row, the table is over: stop reading the file.

The header lines (`N r1 SCF` and the dashes) do not match the row pattern, so they are skipped automatically. The same few lines work for 11, 22 or 39 points.

**In the code:** [`ex3/extract.sh` L31–L35](../sessions/02-hartree-fock/ex3-bond-scans/extract.sh#L31-L35) (the plain version), then reused with a reference energy in [`ex4/extract.sh` L21–L25](../sessions/02-hartree-fock/ex4-rhf-dissociation/extract.sh#L21-L25), [`ex5/extract.sh` L29–L33](../sessions/02-hartree-fock/ex5-uhf-initial-guess/extract.sh#L29-L33) and [`ex6/extract.sh` L18–L24](../sessions/02-hartree-fock/ex6-rhf-vs-uhf/extract.sh#L18-L24).

---

## 4. Doing arithmetic with shell values

Bash arithmetic only handles integers, so `$(( -1.12 - 2 * -0.49 ))` fails. Real-number arithmetic goes to `awk`, and shell values are passed in with `-v`:

```bash
EH=$(grep "SCF Done" h_sto3g.log | awk '{print $5}')          # energy of the H atom

awk -v eh="$EH" '... { print $2, $3 - 2*eh }' h2_rhf_sto3g.log   # ΔE = E(H2) - 2 E(H)
```

Inside `awk`, `eh` is a normal variable. Note the two layers of quoting: the `awk` program goes in single quotes so that Bash leaves `$2` and `$3` alone, and the shell variable crosses over through `-v`.

For a single calculation with no file to read, use a `BEGIN` block:

```bash
REF_LIH=$(awk -v eh="$EH" -v eli="$ELI" 'BEGIN { printf "%.10f", eh + eli }')
```

**In the code:** ΔE at every point in [`ex4/extract.sh` L21–L25](../sessions/02-hartree-fock/ex4-rhf-dissociation/extract.sh#L21-L25) and [`ex5/extract.sh` L29–L33](../sessions/02-hartree-fock/ex5-uhf-initial-guess/extract.sh#L29-L33). The `BEGIN` block, building the references of H₂ and LiH: [`ex6/extract.sh` L35–L36](../sessions/02-hartree-fock/ex6-rhf-vs-uhf/extract.sh#L35-L36).

---

## 5. Generating inputs from a template

When 30 inputs differ only in the basis set, write one and generate the rest:

```bash
for b in 3-21G 4-31G "6-31G(d)" "6-31G(d,p)"; do
	n=$(echo "$b" | tr -d '(),-' | tr 'A-Z' 'a-z')     # "6-31G(d,p)" -> "631gdp"
	sed "s#STO-3G#$b#g" h2o_sto3g.com > "h2o_${n}.com"
done
```

- **`sed "s#old#new#g"`** replaces every (`g`) occurrence of `old` with `new`. The separator does not have to be `/`; any character works, and `#` is a common choice because it never appears in basis-set names or file paths.
- **Double quotes** around the `sed` expression let Bash substitute `$b` before `sed` sees it. With single quotes, `sed` would search for the literal text `$b`.
- **`tr -d '(),-'`** deletes those characters, and **`tr 'A-Z' 'a-z'`** lowercases the rest. Together they turn a basis name into something safe for a file name.
- `"6-31G(d)"` is **quoted in the list** because unquoted parentheses mean something else to Bash.

Besides saving typing, it guarantees that the geometry is *identical* across the series, so any difference in the results comes from the basis alone.

**In the code:** [`ex2/generate.sh` L10–L25](../sessions/02-hartree-fock/ex2-basis-sets/generate.sh#L10-L25) (6 molecules × 4 basis sets) and [`ex3/generate.sh` L6–L15](../sessions/02-hartree-fock/ex3-bond-scans/generate.sh#L6-L15), which also takes the molecule name from the template's file name with `${f%_sto3g.com}`. Session 03 adds a twist: [`S03 ex1/generate.sh` L8–L27](../sessions/03-geometry-optimization/ex1-optimized-geometries/generate.sh#L8-L27) loops over file-name tags and translates them with `case` ([§8](#8-mapping-names-with-case)). [`S03 ex4/generate.sh` L13](../sessions/03-geometry-optimization/ex4-hf-vs-b3lyp/generate.sh#L13) changes the *method* instead of the basis, with two substitutions in one call: `sed "s/#hf/#b3lyp/; s/ HF$/ B3LYP/"`. The `;` separates them, and the `$` anchors the second one to the end of the line, so only the last word of the title changes.

---

## 6. Gluing columns together

In Ex. 5 the energies come from the scan table, and ⟨Ŝ²⟩ comes from lines spread through the log. Both are lists with one entry per point, in the same order. `paste` joins them side by side:

```bash
paste -d ' ' <(command producing "r ΔE") <(command producing "S2") > out.dat
```

- `paste` joins line 1 of each input, then line 2, and so on. `-d ' '` uses a space as separator instead of a tab.
- `<( ... )` is **process substitution**: Bash runs the command and gives `paste` something that behaves like a file containing its output. It avoids writing temporary files.

**In the code:** [`ex5/extract.sh` L28–L35](../sessions/02-hartree-fock/ex5-uhf-initial-guess/extract.sh#L28-L35) (written out in full) and [`ex6/extract.sh` L47–L48](../sessions/02-hartree-fock/ex6-rhf-vs-uhf/extract.sh#L47-L48), where it shrinks to one line thanks to the functions of the next section.

---

## 7. Functions: write it once

When the same pipeline is needed for several molecules, a function keeps it in one place:

```bash
scan() {  # scan <log> <reference energy>
	awk -v ref="$2" '... { print $2, $3 - ref }' "$1"
}

scan h2_rhf_321g.log  "$REF_H2"  > h2_rhf.dat
scan lih_rhf_321g.log "$REF_LIH" > lih_rhf.dat
```

Inside a function, `$1`, `$2`, … are the function's own arguments, not the script's. Careful: inside the single-quoted `awk` program, `$2` and `$3` are `awk` fields and have nothing to do with the function's arguments. That is exactly why the reference is passed in through `-v ref="$2"`.

The loop that uses them only decides which reference goes with which molecule, with a short form of *if/else*: if the test succeeds `&&` runs, otherwise `||` does.

```bash
[ "$mol" = h2 ] && ref=$REF_H2 || ref=$REF_LIH
```

**In the code:** the functions `scan` and `s2` in [`ex6/extract.sh` L18–L31](../sessions/02-hartree-fock/ex6-rhf-vs-uhf/extract.sh#L18-L31), and the loop that uses them in [L38–L51](../sessions/02-hartree-fock/ex6-rhf-vs-uhf/extract.sh#L38-L51).

---

## 8. Mapping names with case

Basis-set names are awkward in file names: `6-31G*` contains a `*`, which the shell treats as a wildcard. [Pattern 5](#5-generating-inputs-from-a-template) cleaned the name with `tr`. The other way round is to loop over clean **file-name tags** and translate each one into the name Gaussian expects:

```bash
for b in 321g 631gs 631gss; do
	case $b in
		321g)   basis="3-21G" ;;
		631gs)  basis="6-31G*" ;;
		631gss) basis="6-31G**" ;;
	esac
	sed "s#sto-3g#$basis#g" "$f" > "${m}_${b}.com"
done
```

- `case $b in … esac` compares `$b` against each pattern in turn and runs the commands of the first one that matches.
- Each branch ends with `;;`.
- Inside a `case`, the patterns are shell patterns, so `6-31G*)` *as a pattern* would match anything starting with `6-31G`. Here the patterns are the plain tags, and the `*` only appears in the values, safely inside quotes.

`tr` derives the tag from the name; `case` derives the name from the tag. The `case` version is longer, but every mapping is written out, and it works for names that no character substitution could produce.

**In the code:** [`S03 ex1/generate.sh` L12–L26](../sessions/03-geometry-optimization/ex1-optimized-geometries/generate.sh#L12-L26).

---

## 9. Splitting file names and default values

When a file name encodes the calculation, as `h2o_631gs.log` does, Bash can take it apart without calling any external program:

```bash
m=${f%.log}       # h2o_631gs.log -> h2o_631gs
mol=${m%_*}       # remove the shortest "_..." from the END:   -> h2o
basis=${m#*_}     # remove the shortest "..._" from the START: -> 631gs
```

| Expansion | Removes | Mnemonic |
|---|---|---|
| `${var%pattern}` | shortest match from the **end** | `%` comes after `$` on the keyboard: the end |
| `${var#pattern}` | shortest match from the **start** | `#` comes before `$`: the start |
| `${var%%pattern}`, `${var##pattern}` | the *longest* match instead | doubled = greedy |

The difference matters when the separator appears twice: for `h2o_rhf_321g`, `${m%_*}` gives `h2o_rhf` but `${m%%_*}` gives `h2o`.

**Default values.** HF is diatomic, so there is no angle to read and `$a` is empty. Printed as is, the row would have one column fewer and every column after it would shift. `${a:--}` prints `$a` if it has a value and `-` otherwise:

```bash
echo "$mol $basis $r ${a:--} $mu"     # hf 631gs 0.911 - 1.9719
```

The general form is `${var:-default}`. Here the default happens to be `-`, hence the odd-looking `:--`.

**In the code:** [`S03 ex1/extract.sh` L23–L25](../sessions/03-geometry-optimization/ex1-optimized-geometries/extract.sh#L23-L25) and [L53](../sessions/03-geometry-optimization/ex1-optimized-geometries/extract.sh#L53).

---

## 10. Bugs worth remembering

Real mistakes found while cleaning up the scripts. Each one *seemed* to work.

| Bug | What happened | Fix |
|---|---|---|
| `grep -1 "Normal termination"` | `-1` is not "quiet": it means "show 1 line of context". The `if` still worked, since `grep` still found the text, but every check printed lines from the log. | `grep -q` |
| `2</dev/null` | Opens `/dev/null` for *reading* on the error channel instead of sending errors there. The messages vanished anyway, since they could not be written, but only by accident. | `2>/dev/null` |
| Skip if the `.log` exists | A crashed job leaves a `.log`, so it was never re-run. | Check for `Normal termination` ([§1](#1-running-every-job-in-a-folder-safely)) |
| `grep -A 41 ... \| tail -39` | Correct only for a 39-point scan. Each new scan needed new numbers. | `awk` table reader ([§3](#3-reading-a-table-of-any-length-with-awk)) |
| Windows line endings | Scripts edited on Windows can be saved with CRLF endings, and on Linux they fail with `$'\r': command not found`. | [`.gitattributes`](../.gitattributes) forces LF on `*.sh` and `*.com` |
