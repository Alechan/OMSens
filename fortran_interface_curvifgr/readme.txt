Steps for now:
1) Compile CURVI files:
gfortran -fPIC -c Rutf.for Rut.for Curvif.for Curvifgr.f90 curvifgr_wrap.f90
2) Using:
   a) Curvi compiled files from prev point(s)
   b) Curvi wrapper f90 file
   c) Curvi wrapper pyf modified by Ale
   Run:
f2py -c -I. Curvifgr.o curvifgr_wrap.o Curvif.o Rutf.o Rut.o -m curvifgr_simplified curvifgr_simplified.pyf Curvifgr_simplified.f90

3) Testing
/home/omsens/anaconda3/bin/python -m unittest -v test_curvifgr
