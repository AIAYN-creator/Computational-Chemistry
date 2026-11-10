%chk=propenal.chk
#hf/3-21g opt geom=connectivity

Propenal opt HF/3-21G

0 1
 C                 -1.17696961   -2.47333370   -1.30644139
 H                 -1.49909951   -2.01950031   -2.22031642
 H                 -1.55284071   -3.43480340   -1.02502189
 C                 -0.29292382   -1.83038992   -0.50540870
 H                  0.02920547   -2.28422297    0.40846672
 C                  0.24804666   -0.44659075   -0.91044054
 H                 -0.07408153    0.00724165   -1.82431667
 O                  1.06894513    0.15042916   -0.16662371

 1 2 1.0 3 1.0 4 2.0
 2
 3
 4 5 1.0 6 1.0
 5
 6 7 1.0 8 2.0
 7
 8

--Link1--
%chk=propenal.chk
#rcis=(nstates=5)/3-21g geom=checkpoint

Propenal CIS 3-21G

0 1

--Link1--
%chk=propenal.chk
#rcis=(nstates=5)/6-31g* geom=checkpoint

Propenal CIS 6-31G*

0 1

--Link1--
%chk=propenal.chk
#rcis=(nstates=5)/6-31+g* geom=checkpoint

Propenal CIS 6-31+G*

0 1

--Link1--
%chk=propenal.chk
#rcis=(nstates=5)/6-311+g* geom=checkpoint

Propenal CIS 6-311+G*

0 1

--Link1--
%chk=propenal.chk
#rcis=(nstates=5)/6-311++g** geom=checkpoint

Propenal CIS 6-311++G**

0 1

--Link1--
%chk=propenal.chk
#rzindo=(nstates=5) geom=checkpoint

Propenal ZINDO

0 1

--Link1--
%chk=propenal.chk
#td=(nstates=5) b3lyp/6-311++g** geom=checkpoint

Propenal TD-B3LYP

0 1


