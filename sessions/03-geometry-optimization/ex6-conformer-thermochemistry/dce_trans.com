#hf/6-31G* opt=z-matrix freq

SEP DCE

0 1
C
C 1 r1
Cl 1 r2 2 a2
Cl 2 r3 1 a3 3 z3
H 1 r4 2 a4 3 z4
H 1 r5 2 a5 3 z5
H 2 r6 1 a6 4 z6
H 2 r7 1 a7  4 z7

r1 1.5
r2 1.8
r3 1.76
r4 1.1
r5 1.1
r6 1.1
r7 1.1
a2 109.0
a3 110.0
a4 109.0
a5 110.0
a6 109.0
a7 110.0
z3 180.
z4 120.0
z5 240.0
z6 120.0
z7 240.0


