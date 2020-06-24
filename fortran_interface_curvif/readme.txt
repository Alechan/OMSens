Steps for now:

1) Compile CURVI files:
    gfortran -fPIC -c Rutf.for Rut.for Curvif.for

2) Using:
   a) Curvi compiled files from prev point(s)
   b) Curvi wrapper f90 file
   c) Curvi wrapper pyf modified by Ale:
        * f2py Curvif_simplified.f90 -m curvif_simplified -h curvif_simplified.pyf --overwrite-signature

3) f2py -c -I. Curvif.o Rutf.o Rut.o -m curvif_simplified curvif_simplified.pyf Curvif_simplified.f90

3) Testing
   a) /home/omsens/anaconda3/bin/python -m unittest -v test_curvi
