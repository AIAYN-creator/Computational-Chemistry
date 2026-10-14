# Bash for Gaussian: a field guide

Most of the work in a computational chemistry course does not happen inside the quantum chemistry program. It happens around it: writing dozens of nearly identical inputs, launching them, checking they finished, and digging a handful of numbers out of output files thousands of lines long. Doing that by hand is slow and error-prone. Doing it with a few lines of Bash makes it fast and repeatable, and a mistake gets fixed once instead of thirty times.

This guide collects the patterns used across the repository, each one with the real Gaussian output it works on. Examples come from [Session 02](../sessions/02-hartree-fock/).

**Contents**

1. [Running every job in a folder, safely](#1-running-every-job-in-a-folder-safely)
2. [Pulling one number out of a log](#2-pulling-one-number-out-of-a-log)
3. [Reading a table of any length with awk](#3-reading-a-table-of-any-length-with-awk)
4. [Doing arithmetic with shell values](#4-doing-arithmetic-with-shell-values)
5. [Generating inputs from a template](#5-generating-inputs-from-a-template)
6. [Gluing columns together](#6-gluing-columns-together)
7. [Functions: write it once](#7-functions-write-it-once)
8. [Bugs worth remembering](#8-bugs-worth-remembering)

---

## 1. Running every job in a folder, safely

[`run.sh`](../sessions/02-hartree-fock/run.sh):

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

---

## 2. Pulling one number out of a log

The pattern is always the same: **find a line by text that always comes with it, then take the field by position.**

```bash
grep "some fixed text" file.log | tail -1 | awk '{print $N}'
```

`awk` splits each line into fields separated by whitespace: `$1`, `$2`, …, and `$NF` is the last one (`NF` is the number of fields). `tail -1` keeps the last occurrence, because many blocks repeat during optimisations and scans, and the final one is the converged result.

Real examples from [Ex. 2](../sessions/02-hartree-fock/ex2-basis-sets/):

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

**⟨Ŝ²⟩ of a UHF wavefunction**: field 4, with a trailing comma that `tr -d ','` removes.

```
 S**2 before annihilation     1.0000,   after     0.0000
```
```bash
grep "S\*\*2 before annihilation" "$f" | awk '{print $4}' | tr -d ','
```

The `*` must be escaped as `\*` because, in a `grep` pattern, `*` means "repeat the previous character".

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
	/Summary of the potential surface scan/ { s = 1; next }        # (1)
	s && /^ *[0-9]+ +[-0-9.]+ +[-0-9.]+ *$/ { print $2, $3; n++; next }   # (2)
	s && n { exit }                                                # (3)
' file.log
```

An `awk` program is a list of `condition { action }` rules, applied to every line in order.

1. When the line contains the title, raise a flag `s` (for *in summary*) and move on to the next line.
2. If the flag is up and the line looks like a table row (an integer, then two numbers, and nothing else), print *r* and *E*, and count it in `n`.
3. If the flag is up, at least one row has been read, and this line is *not* a row, the table is over: stop reading the file.

The header lines (`N r1 SCF` and the dashes) do not match the row pattern, so they are skipped automatically. The same few lines work for 11, 22 or 39 points.

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
REF=$(awk -v eh="$EH" -v eli="$ELI" 'BEGIN { printf "%.10f", eh + eli }')
```

---

## 5. Generating inputs from a template

When 30 inputs differ only in the basis set, write one and generate the rest ([Ex. 2](../sessions/02-hartree-fock/ex2-basis-sets/generate.sh)):

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

---

## 6. Gluing columns together

In [Ex. 5](../sessions/02-hartree-fock/ex5-uhf-initial-guess/extract.sh) the energies come from the scan table, and ⟨Ŝ²⟩ comes from lines spread through the log. Both are lists with one entry per point, in the same order. `paste` joins them side by side:

```bash
paste -d ' ' <(command producing "r ΔE") <(command producing "S2") > out.dat
```

- `paste` joins line 1 of each input, then line 2, and so on. `-d ' '` uses a space as separator instead of a tab.
- `<( ... )` is **process substitution**: Bash runs the command and gives `paste` something that behaves like a file containing its output. It avoids writing temporary files.

---

## 7. Functions: write it once

When the same pipeline is needed for several molecules, a function keeps it in one place ([Ex. 6](../sessions/02-hartree-fock/ex6-rhf-vs-uhf/extract.sh)):

```bash
scan() {  # scan <log> <reference energy>
	awk -v ref="$2" '... { print $2, $3 - ref }' "$1"
}

scan h2_rhf_321g.log  "$REF_H2"  > h2_rhf.dat
scan lih_rhf_321g.log "$REF_LIH" > lih_rhf.dat
```

Inside a function, `$1`, `$2`, … are the function's own arguments, not the script's. Careful: inside the single-quoted `awk` program, `$2` and `$3` are `awk` fields and have nothing to do with the function's arguments. That is exactly why the reference is passed in through `-v ref="$2"`.

---

## 8. Bugs worth remembering

Real mistakes found while cleaning up the scripts. Each one *seemed* to work.

| Bug | What happened | Fix |
|---|---|---|
| `grep -1 "Normal termination"` | `-1` is not "quiet": it means "show 1 line of context". The `if` still worked, since `grep` still found the text, but every check printed lines from the log. | `grep -q` |
| `2</dev/null` | Opens `/dev/null` for *reading* on the error channel instead of sending errors there. The messages vanished anyway, since they could not be written, but only by accident. | `2>/dev/null` |
| Skip if the `.log` exists | A crashed job leaves a `.log`, so it was never re-run. | Check for `Normal termination` ([§1](#1-running-every-job-in-a-folder-safely)) |
| `grep -A 41 ... \| tail -39` | Correct only for a 39-point scan. Each new scan needed new numbers. | `awk` table reader ([§3](#3-reading-a-table-of-any-length-with-awk)) |
| Windows line endings | Scripts edited on Windows can be saved with CRLF endings, and on Linux they fail with `$'\r': command not found`. | `.gitattributes` forces LF on `*.sh` and `*.com` |
