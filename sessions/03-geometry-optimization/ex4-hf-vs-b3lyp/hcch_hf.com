#hf/6-31G* opt=z-matrix

HCCH optimization HF

0 1
C
C 1 rcc
X 1 1.0 2 90.0
H 1 rch 3 90.0 2 180.0
h 2 rch 3 90.0 1 180.0

rcc 1.20
rch 1.06


