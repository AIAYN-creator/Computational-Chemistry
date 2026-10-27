#hf/6-31G* opt=z-matrix freq

Glycine B HF

0 1
N
C 1 rcn
C 2 rcc 1 accn
O 3 rco 2 acco 1 zncco
O 3 rcoh 2 accoh 4 180.
H 5 roh 3 acoh 2 zccoh
H 2 rch 3 ahcc 1 zh
H 2 rch 3 ahcc 1 -zh
H 1 rnh 2 ahnc 3 zhn
H 1 rnh 2 ahnc 3 -zhn

rcn 1.45
rcc 1.52
accn 112.
rco 1.20
acco 125.
rcoh 1.35
accoh 112.
roh 0.97
acoh 107.
zncco 180.
zccoh 0.
rch 1.09
ahcc 108.
zh 121.
rnh 1.01
ahnc 110.
zhn 120.


