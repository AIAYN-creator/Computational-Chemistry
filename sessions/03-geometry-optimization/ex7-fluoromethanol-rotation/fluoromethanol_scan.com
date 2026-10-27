#b3lyp/6-31G* opt=z-matrix

Scan for fluoromethanol internal rotation

0 1
C
O 1 r1
F 1 r2 2 a2
H 2 r3 1 a3 3 z3
H 1 r4 2 a4 3 z4
H 1 r5 2 a5 3 z5

r1 1.4
r2 1.5
r3 0.95
r4 1.09
r5 1.1
a2 110.
a3 105.
a4 109.
a5 109.
z3 0. S 9 20.0
z4 120.
z5 -120.


