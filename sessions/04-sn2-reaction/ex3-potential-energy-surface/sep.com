#HF/6-31+G* opt=z-matrix

SEP

-1 1
C
F 1 r1 
H 1 r2 2 a2
H 1 r3 2 a3 3 z3
H 1 r4 2 a4 3 z4
X 1 1.0 2 90. 3 0.
Cl 1 r5 6 a5 2 z5

r1 1.3 S 8 0.2
r2 1.09
r3 1.08
r4 1.1
r5 3.6 S 10 -0.2
a2 110.
a3 110.
a4 110.
a5 90.
z3 120.
z4 240.
z5 180.


