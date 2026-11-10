%chk=pentadienal.chk
# hf/3-21g geom=connectivity

Title Card Required

0 1
 C                 -0.83427167    1.03531619    1.33222117
 H                 -0.98767124    0.20554289    0.67431174
 H                 -1.67367055    1.58074679    1.71012985
 C                  0.42314933    1.39544801    1.68685415
 H                  1.26254825    0.85001780    1.30894497
 C                  0.64393014    2.58970256    2.63375008
 H                 -0.19546877    3.13513283    3.01165917
 C                  1.90135121    2.94983530    2.98838186
 H                  2.74074991    2.40440223    2.61047633
 C                  2.12213203    4.14408985    3.93527779
 H                  1.28273323    4.68952145    4.31318520
 O                  3.28973711    4.47849605    4.26458226

 1 2 1.0 3 1.0 4 2.0
 2
 3
 4 5 1.0 6 1.0
 5
 6 7 1.0 8 2.0
 7
 8 9 1.0 10 1.0
 9
 10 11 1.0 12 2.0
 11
 12

--Link1--
%chk=pentadienal.chk
#rcis=(nstates=5)/3-21g geom=checkpoint

Pentadienal CIS 3-21G

0 1

--Link1--
%chk=pentadienal.chk
#rcis=(nstates=5)/6-31g* geom=checkpoint

Pentadienal CIS 6-31G*

0 1

--Link1--
%chk=pentadienal.chk
#rcis=(nstates=5)/6-31+g* geom=checkpoint

Pentadienal CIS 6-31+G*

0 1

--Link1--
%chk=pentadienal.chk
#rcis=(nstates=5)/6-311+g* geom=checkpoint

Pentadienal CIS 6-311+G*

0 1

--Link1--
%chk=pentadienal.chk
#rcis=(nstates=5)/6-311++g** geom=checkpoint

Pentadienal CIS 6-311++G**

0 1

--Link1--
%chk=pentadienal.chk
#rzindo=(nstates=5) geom=checkpoint

Pentadienal ZINDO

0 1

--Link1--
%chk=pentadienal.chk
#td=(nstates=5) b3lyp/6-311++g** geom=checkpoint

Pentadienal TD-B3LYP

0 1


