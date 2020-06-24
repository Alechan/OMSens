      subroutine curvifgr_wrap(fu,n,x,fopt,eps,ibound,&
      jbound,bl,bu,waNotUsed,nfu,nit,idiff,kmax,ier)

!     ===== Rutina para calcular minimos globales ====
!           Hugo D.Scolnik y Santiago Laplagne - Febrero 2019 

!     fu debe ser llamada como call fu(n,x,f)

!        Ver ejemplo

!     n es el numero de variables

!     x vector inicial (tambien output con el resutado)

!     fopt valor dado por CURVIF (usado internamente)

!     eps criterio de convergencia (por ejemplo 1.d-7)

!     fx es el valor de la funcion modificada para buscar minimos globales

!    ibound:  parametro tal que si
!             0 es un problema sin restricciones
!             1 es un problema con restricciones
!
!    jbound:  vector de dimension n que define la clase de restriccion
!             para cada variable (solo se susa si ibound.ne.0).
!             jbound(i) = 0 si la ith variable no tiene restricciones
!                         1 si la ith variable solo tiene cotas superiores
!                         2 si la ith variable solo tiene cotas inferiores
!                         3 si la ith variable tiene cotas inferiores y
!                           superiores
!
!        bl:  vector de cotas inferiores (no se usa si ibound=0).
!
!        bu:  vector de cotas superiores (no se usa si ibound=0).
!
!        Para mantener constante la variable i definir:
!
!             jbound(i) = 3
!             bl(i) = bu(i) = constante
! 
!        wa:  vector de dimension (ver output)
!             9*n+n*(n+1)/2+n*n+max(7*n-n*(n+1)/2,0) 
!
!       nfu:  maximo numero de evaluaciones de f(x).Si es igual a 
!             cero, se usa 5000*n  
!
!     idiff:  Elige diferencias simples o dobles.  Las simples 
!             requieren menos evaluaciones de f y deben usarse si f(x)
!             es "suave". Las dobles dan mejor precision y
!             deben usarse en los casos mas dificiles
!             idiff = 1  diferencias simples
!             idiff = 2  diferencias dobles
!
!     kmax:   kmax define cada cuantas iteraciones se recalcula una
!             aproximacion al hessiano 
!             Recomendamos kmax = 3 a menos que el problema sea dificil
!             en cuyo caso usamos kmax = 1 o 2.
!----------------------------------------------------------------------
!    Output:
!
!         x:  mejor punto calculado

!       fopt:  valor de la funcion en el optimo
!
!       nfu:   numero de evaluaciones de la funcion
!
!       nit:   numero de iteraciones.
!
!        wa:   contiene informacion sobre el gradiente (ver CURVIF)
!
!       ier:   0 obtuvo convergencia.
!              1 excedio el numero maximo de evaluaciones de f(x)
!              2 no convergio
!              3 input equivocado en un problema con restricciones
!----------------------------------------------------------------------

! ======================================================================

! ============= Ejemplo de rutina que define la funcion a optimizar




!     Bartels-Conn
!     Global optimum: f(x*)=1  for  x*(1)=x*(2)=0, x0(i) en [-50.50] 

!  	  subroutine f(n,x,f)                                              
!      implicit real*8 (a-h,o-z)                                         
!      dimension x(1)   

!      DEFINIR f(x)
	  	                                             
!      f=dabs(x(1)**2+x(2)**2+x(1)*x(2)) +dabs(dsin(x(1))) +dabs(dcos(x(2)))   

                                    
!      return                                                            
!      end   

! ======= Ejemplo de llamada para minimizar la funcion de Bartels-Conn -----



!     n=2          ! numero de variables                                                     
                                                      
!     x(1)=1.0     ! Punto inicial
!	  x(2)=-1.0

!	  ibound=1     ! indica que es un problema con restricciones
     
!	  do ii=1,n
!			jbound(ii)=3 ! indica que las dos variables tienen cotas inferiores
			             ! y superiores
!			bl(ii)=-2.0  ! cotas inferiores
!			bu(ii)=2.0   ! cotas superiores
!	  end do

!	  nfu=200            ! numero maximo de evaluaciones de la funcion
                                              
 
!     call curvifgr_wrap(f,n,x,fx,eps,ibound,jbound,bl,bu,wa,nfu,nit,idiff,kmax,ier)

!  =============== Sigue la rutina =================


 	  implicit real*8 (a-h,o-z)
	  real*8 lambda,lambdaL

	  parameter(nx=100)   ! dimension para funciones de hasta 100 variables
      !parameter(nx=n)   ! dimension para funciones de hasta 100 variables

	  dimension y(nx), wa(9*nx+nx*(nx+1)/2+nx*nx+max(7*nx-nx*(nx+1)/2,0))

	  dimension x(1), bl(1), bu(1), jbound(1)
 
!	  dimension xstar(nx),x(nx),e(2*nx,2*nx),y(nx),bl(nx),bu(nx),&
!	            wa(9*nx+nx*(nx+1)/2+nx*nx+max(7*nx-nx*(nx+1)/2,0)),jbound(1)


      common/blk1/xstar(nx),e(2*nx,2*nx),q,fxstar,curvifgr_metodo
      common /blk2/curvifgr_xglobal(nx),curvifgr_fglobal

	  external fu,filled


!write(4,*) 'ouch!!', n

	  call fu_curviFGR(n,x,fopt)
      do i=1,n
 		curvifgr_xglobal(i)=x(i)
	  end do
	  curvifgr_fglobal = fopt

!	  write(4,*) '-----------------------------------'
!	  write(4,*) '--BEFORE CURVIFGR-------------------'
!	  write(4,*) 'fopt: ', fopt
!	  write(4,*) 'x: ', x(1:n)

	  call curvifgr(fu_curviFGR,n,x,fopt,eps,ibound,jbound,bl,bu,wa,nfu,nit,idiff,kmax,ier)

	  write(4,*) '-----------------------------------'
	  write(4,*) '--AFTER CURVIFGR-------------------'
	  write(4,*) 'fopt: ', fopt
	  write(4,*) 'x: ', x(1:n)

	  call fu_curviFGR(n,x,fopt)

      do i=1,n
		x(i)=curvifgr_xglobal(i)
	  end do
	  fopt = curvifgr_fglobal

!	  write(4,*) '-----------------------------------'
!	  write(4,*) '--AFTER fu evaluation--------------'
!	  write(4,*) 'fopt: ', fopt
!	  write(4,*) 'x: ', x(1:n)

contains

	subroutine fu_curviFGR(n,theta,fGoal)


		implicit none

		!******************************************************************************************
		! Input parameters
		integer n								! Cantidad de variables
		real*8 theta(*)							! Punto en donde evaluar la función
		real*8 fGoal							! Valor de la funcion a minimizar
		!******************************************************************************************

		integer i
		
		call fu(n, theta, fGoal)

		if(fGoal.lt.curvifgr_fglobal)then
			curvifgr_fglobal=fGoal
			do i=1,n
				curvifgr_xglobal(i)=theta(i)
			end do
		end if

		if(curvifgr_metodo.eq.1)call filled(n,theta,fGoal)
		return                                                            
	end subroutine fu_CurviFGR

end subroutine                                                          
