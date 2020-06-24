

      subroutine curvifgr(fu,n,x,fopt,eps,ibound,&
      jbound,bl,bu,wa,nfu,nit,idiff,kmax,ier)

!     ===== Rutina para calcular minimos globales ====
!           Hugo D.Scolnik - Octubre 2018 

!     fu debe ser llamada como call fu(n,x,f)
!        Ver ejemplo

!     n es el numero de variables

!     x vector inicial

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
!    xglobal:  mejor punto ; esta en common /blk2/xglobal(100),fglobal
!
!    fglobal:  valor de la funcion en xglobal
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

!         SIEMPRE INCLUIR LAS DOS LINEAS SIGUIENTES    
   
!	  common/blk1/xstar,e,q,fnueva,fxstar,metodo 
!	  common /blk2/xglobal(100),fglobal

!      DEFINIR f(x)
	  	                                             
!      f=dabs(x(1)**2+x(2)**2+x(1)*x(2)) +dabs(dsin(x(1))) +dabs(dcos(x(2)))   


!      SIEMPRE INCLUIR LAS SIGUIENTES INSTRUCCIONES
	  
!	  if(f.lt.fglobal)then
!	    fglobal=f
!		do i=1,n
!		  xglobal(i)=x(i)
!		end do
!	  end if
	  	  
!	  if(metodo.eq.1)call filled(n,x,fa)                                      
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
                                              
 
 !     call curvifgr(f,n,x,fx,eps,ibound,jbound,bl,bu,wa,nfu,nit,idiff,kmax,ier)


!  ---->   *****  Los resultados estan en xglobal(n) y fglobal


!   ===== Sigue la rutina CURVIFGR =====


	  implicit real*8 (a-h,o-z)
	  real*8 lambda,lambdaL
	  dimension xstar(100),x(100),e(100,200),y(100),bl(100),bu(100),wa(13450)
      common/blk1/xstar,e,q,f,fxstar,metodo
	  common /blk2/xglobal(100),fglobal
	  external fu,filled

      xstar=x
	  nfuoriginal=nfu

      call curvif(fu,n,xstar,fxstar,eps,ibound,&
         jbound,bl,bu,wa,nfu,nit,idiff,kmax, ier)

!     Perturbamos xstar para definir x
      
!	  result = DRAND (0) 
	  result = RAND (0) 
      a=0.99d0
	  b=1.01d0

	  q=1.d-10
	  lambdaL=2.d-10

	  do i=1,n

!         x(i)=xstar(i)*(a+(b-a)*DRAND(1))
         x(i)=xstar(i)*(a+(b-a)*RAND(1))
	  
	  end do	  
	  
	  metodo=0   
 
      call fu(n,x,f)

	  t=f-fxstar

!     Define las direcciones

	  e=0.d0

	  if(n.eq.2)then
	     KD=6*n
		 pi=4.d0*datan(1.d0)

		 do i=1,KD
		   a=2.d0*pi*(i-1)/KD
		   e(1,i)=dcos(a)
		   e(2,i)=dsin(a)
		 end do

      else

	     KD=2*n

	  end if

 
 ! usaremos KD direcciones

	  do i=1,n
	   
		  e(i,i)=1.d0
         
	  end do
	  
	  		 
		do i=n+1,KD

		  e(i,i)=-1.d0
		   
		end do


		     
!   ========  Fin del seteo de direcciones ==============

1     continue

      metodo=0

      xstar=x

      nfu=nfuoriginal

      call curvif(fu,n,xstar,fxstar,eps,ibound,&
         jbound,bl,bu,wa,nfu,nit,idiff,kmax, ier)

!     --------------------------------------

      L=1
	  lambda=1.d0

10    if(L.le.KD)then                ! Step 3(a)

20         if(lambda.ge.lambdaL)then   ! Step 3(b)
		    
			do i=1,n
			  y(i)=x(i)+lambda*e(i,L)
			end do

			ioutbounds=0             ! Step 3(c)

			do i=1,n
			  if(y(i).lt.bl(i).or.y(i).gt.bu(i))ioutbounds=1
			end do

           
! =================================================================
			if(ioutbounds.eq.1)then

			   lambda=lambda/2.d0   ! ---> usar linesearch

			   go to 20             ! vuelve a 3(b) por out of bounds
			end if

			else
               
			   L=L+1

			   go to 10
			end if
! =================================================================

			   metodo=0
			   call fu(n,y,fy)

			   if(fy.lt.fxstar)then

			      x=y
			  	  t=fy-fxstar

				  GO TO 1

               else

                  metodo=1
		          nfu=nfuoriginal
				  		  
                  call curvif(fu,n,y,fy,eps,ibound,&
                     jbound,bl,bu,wa,nfu,nit,idiff,kmax, ier)

                  if(fy.lt.fxstar)then
				      x=y
					  go to 1

                  else

					  L=L+1
					  
					  lambda=1.d0
					  
					  GO TO 10
				  end if
           end if

           else  ! caso cuando L > KD
		    
			    x=xstar

		   end if


				return

				end


            subroutine filled(n,x,f)
		   
		        implicit real*8(a-h,o-z)

	            dimension xstar(100),x(100),e(100,200)
                common/blk1/xstar,e,q,fnueva,fxstar,metodo

	            t=fnueva-fxstar
				
				if(t.ge.0.d0)W=1.d0

				if(t.gt.-q.and.t.lt.0.d0)then
					  a=t/q
					  W=-2.d0*a**3-3.d0*a**2+1.d0
				 end if

				 if(t.le.-q)W=0.d0    

				xnorm=0.d0

				do i=1,n
					xnorm=xnorm+(x(i)-xstar(i))**2
				end do

				f=W/(1.d0+xnorm)

			return
			end