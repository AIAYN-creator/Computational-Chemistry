 set terminal pngcairo size 1200,900
 set output 'sep.png'
 set noztics
 set parametric
 set view 0, 0, 1, 1
 set contour base
 set cntrparam bspline
 set cntrparam points 30
 set cntrparam order 10
 set cntrparam levels incremen 0.0,2,42
 set pm3d interpolate 8,10  
 set pm3d map 
 set xlabel "d(C-Cl) A"
 set ylabel "d(C-F) A"
 set key lmargin title 'Energia kcal/mol'
 set xrange [1.6:3.6]
 set yrange [1.3:2.9]
 set xtics 1.6,0.2 font "Helvetica, 10" 
 set ytics 1.3,0.2 font "Helvetica, 10" 
 set contour base
 set title " Superficie de energia potencial " font "Helvetica, 16"
 splot 'sep.dat' u 1:2:3

