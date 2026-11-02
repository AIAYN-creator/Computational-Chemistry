#HF/6-31+G* opt=z-matrix freq

Cl- CH3F complex

-1 1
C
X 1 1.
F 1 rcf 2 90.
Cl 1 rccl 2 90. 3 180.
H 1 rch 3 a 2 0.
H 1 rch 3 a 5 120.
H 1 rch 3 a 5 -120.

rcf 1.40
rccl 3.20
rch 1.08
a 109.


