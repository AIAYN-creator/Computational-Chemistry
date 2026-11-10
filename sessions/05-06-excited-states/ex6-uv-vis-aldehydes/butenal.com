%chk=butenal.chk
#hf/3-21g opt geom=connectivity

Title Card Required

0 1
 C                 -0.32211183   -2.13080422    1.07147621
 H                 -0.54647333   -3.11099948    1.43723456
 H                  0.57324562   -1.77322975    1.53556191
 H                 -0.18357788   -2.16882374    0.01116358
 C                 -1.48722961   -1.17997613    1.40317865
 H                 -2.48581520   -1.55911552    1.46626699
 C                 -1.24778260    0.13694857    1.61517276
 H                 -0.24919698    0.51608792    1.55208460
 C                 -2.41290037    1.08777667    1.94687520
 H                 -3.41148582    0.70863708    2.00996465
 O                 -2.19055676    2.31063538    2.14372653

 1 2 1.0 3 1.0 4 1.0 5 1.0
 2
 3
 4
 5 6 1.0 7 2.0
 6
 7 8 1.0 9 1.0
 8
 9 10 1.0 11 2.0
 10
 11

--Link1--
%chk=butenal.chk
#rcis=(nstates=5)/3-21g geom=checkpoint

Butenal CIS 3-21G

0 1

--Link1--
%chk=butenal.chk
#rcis=(nstates=5)/6-31g* geom=checkpoint

Butenal CIS 6-31G*

0 1

--Link1--
%chk=butenal.chk
#rcis=(nstates=5)/6-31+g* geom=checkpoint

Butenal CIS 6-31+G*

0 1

--Link1--
%chk=butenal.chk
#rcis=(nstates=5)/6-311+g* geom=checkpoint

Butenal CIS 6-311+G*

0 1

--Link1--
%chk=butenal.chk
#rcis=(nstates=5)/6-311++g** geom=checkpoint

Butenal CIS 6-311++G**

0 1

--Link1--
%chk=butenal.chk
#rzindo=(nstates=5) geom=checkpoint

Butenal ZINDO

0 1

--Link1--
%chk=butenal.chk
#td=(nstates=5) b3lyp/6-311++g** geom=checkpoint

Butenal TD-B3LYP

0 1


