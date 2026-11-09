#HF/6-31+G* opt=z-matrix freq scrf=(pcm,solvent=water)

F-CH3Cl complex

-1 1
C
X 1 1.
Cl 1 rccl 2 90.
F 1 rcf 2 90. 3 180.
H 1 rch 3 a 2 0.
H 1 rch 3 a 5 120.
H 1 rch 3 a 5 -120.

rccl 1.80
rcf 2.60
rch 1.08
a 108.


