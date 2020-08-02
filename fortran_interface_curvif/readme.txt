Steps for now:

1) Compile CURVI files:
    gfortran -fPIC -c Rutf.for Rut.for Curvif.for

2) Make python library:
  f2py -c -I. Curvif.o Rutf.o Rut.o -m curvif_simplified curvif_simplified.pyf Curvif_simplified.f90

3) Testing
  /home/omsens/anaconda3/bin/python -m unittest -v test_curvi
