

      subroutine curvifgr(fu,n,x,fopt,eps,ibound,&
      jbound,bl,bu,wa,nfu,nit,idiff,kmax,ier)


	  implicit real*8 (a-h,o-z)
	  real*8 lambda,lambdaL


integer, parameter :: out_unit=20

	  parameter(nx=100)   ! dimension para funciones de hasta 100 variables
	 
	  dimension y(nx), wa(9*nx+nx*(nx+1)/2+nx*nx+max(7*nx-nx*(nx+1)/2,0))
	  dimension x(1),bl(1),bu(1),jbound(1)

!	  dimension xstar(100),x(100),e(200,200),y(100),bl(100),bu(100),wa(13450),jbound(1)

      common/blk1/xstar(nx),e(2*nx,2*nx),q,fxstar,curvifgr_metodo
      common /blk2/curvifgr_xglobal(nx),curvifgr_fglobal

!      common/blk1/xstar,e,q,fxstar,metodo
 !     common /blk2/xglobal(nx),fglobal

	  external fu,filled

! ***************************************************************************

!  open (unit=out_unit,file="results.txt",status="old", position="append", action="write")
!  write (out_unit,*) "The product of",5," and",6
!  write (out_unit,*) "is",5*6
!  close (out_unit)


!!	  write(4,*) '-----------------------------------'

 if(ibound.eq.1)call ajusta(x,n,bl,bu)

      do i = 1,n
	    xstar(i) = x(i)
	  end do
	  !xstar=x
	  nfuoriginal=nfu
	  nfutotal=0

!      xstar=x
	  mejoray=0

      call curvif(fu,n,xstar,fxstar,eps,ibound,&
         jbound,bl,bu,wa,nfu,nit,idiff,kmax, ier)


!  open (unit=out_unit,file="results.txt",status="old", position="append", action="write")
!	  write(out_unit,*) '-----------------------------------'
!	  write(out_unit,*) '--INSIDE CURVIFGR------------------'
!	  write(out_unit,*) '----AFTER FIRST CURVIF CALL--------'
!	  write(out_unit,*) 'fxstar: ', fxstar
!	  write(out_unit,*) 'xstar: ', xstar(1:n)
!  close (out_unit)

!     Perturbamos xstar para definir x
      
!	  result = DRAND (0) 
	  result = RAND (0) 

              a=0.9999d0
              b=1.0001d0

	  q=1.d-10
	  lambdaL=2.d-10

	  do i=1,n

!         x(i)=xstar(i)*(a+(b-a)*DRAND(1))
         x(i)=xstar(i)*(a+(b-a)*RAND(1))
	  
	  end do	  

!  open (unit=out_unit,file="results.txt",status="old", position="append", action="write")
!	  write(out_unit,*) '--before ajusta--'
!  close (out_unit)
	  
         if(ibound.eq.1)call ajusta(x,n,bl,bu)

!  open (unit=out_unit,file="results.txt",status="old", position="append", action="write")
!	  write(out_unit,*) '--call ajusta--'
!  close (out_unit)
		    
	  metodo=0   
 
      call fu(n,x,f)

!  open (unit=out_unit,file="results.txt",status="old", position="append", action="write")
!	  write(out_unit,*) '--call fu--'
!  close (out_unit)

	  ! NO SE USA
	  t=f-fxstar


!     Define las direcciones

	  e=0.d0

	  if(n.eq.2)then
 
                        KD=8
						e(1,1)=0.d0
						e(2,1)=1.d0
						e(1,2)=1.d0
						e(2,2)=0.d0
						e(1,3)=0.d0
						e(2,3)=-1.d0
						e(1,4)=1.d0
						e(2,4)=0.d0
						e(1,5)=-1.d0
						e(2,5)=1.d0
						e(1,6)=1.d0
						e(2,6)=-1.d0
						e(1,7)=1.d0
						e(2,7)=1.d0
						e(1,8)=-1.d0
						e(2,8)=-1.d0         
		 go to 1

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


1   continue
		     
!   ========  Fin del seteo de direcciones ==============

      k=0
	  igual=0

! *****************************************************************


10     continue

      k=k+1

      if(k.gt.2*KD)go to 40

      do i = 1,n
	    xstar(i) = x(i)
	  end do

!      xstar=x

      if(ibound.eq.1)call ajusta(xstar,n,bl,bu)
      
	  metodo=0
      nfu=nfuoriginal

      call curvif(fu,n,xstar,fxstar,eps,ibound,&
         jbound,bl,bu,wa,nfu,nit,idiff,kmax, ier)

!  open (unit=out_unit,file="results.txt",status="old", position="append", action="write")
!	  write(out_unit,*) '-----------------------------------'
!	  write(out_unit,*) '--INSIDE CURVIFGR------------------'
!	  write(out_unit,*) '----AFTER SECOND CURVIF CALL--------'
!	  write(out_unit,*) 'fxstar: ', fxstar
!	  write(out_unit,*) 'xstar: ', xstar(1:n)
!  close (out_unit)


      nfutotal= nfutotal+nfu

      nfu=nfuoriginal

      do i = 1,n
	    x(i) = xstar(i)
	  end do
      !x=xstar
!     --------------------------------------

      L=1
	  rlambda=1.d0


20    if(L.le.KD.and.igual.le.KD)then                ! Step 3(a)

30         continue

        if(ibound.eq.1)call ajusta(x,n,bl,bu)
			  

			do i=1,n
			  y(i)=x(i)+rlambda*e(i,L)
     		end do
        
		    if(ibound.eq.1)call ajusta(y,n,bl,bu)

!				     
           
! =================================================================

			   metodo=0
			   call fu(n,y,fy)

               nfutotal= nfutotal+1

			   
			   if(fy.lt.fxstar)then
			     do i = 1,n
	               x(i) = y(i)
	             end do
      			 !x=y
				 fxstar=fy
				 mejoray=mejoray+1
     			 go to 10
			   else

               metodo=1
		          nfu=nfuoriginal

                  f=fy
		    
			if(ibound.eq.1)call ajusta(y,n,bl,bu)	

					  		  
                call curvif(fu,n,y,fy,eps,ibound,&
                     jbound,bl,bu,wa,nfu,nit,idiff,kmax, ier)
	
!  open (unit=out_unit,file="results.txt",status="old", position="append", action="write")
!	  write(out_unit,*) '-----------------------------------'
!	  write(out_unit,*) '--INSIDE CURVIFGR------------------'
!	  write(out_unit,*) '----AFTER CURVIF CALL--------'
!	  write(out_unit,*) 'fxstar: ', fxstar
!	  write(out_unit,*) 'xstar: ', xstar(1:n)
!  close (out_unit)
	 		    
				  metodo=0

			      call fu(n,y,fy)
                  nfutotal= nfutotal+nfu+1

                  if(fy.lt.fxstar)then
					do i = 1,n
					  x(i) = y(i)
					end do
! 				      x=y
					  				 mejoray=mejoray+1
					  xstar=y
					  fxstar=fy
					  go to 10
                  else

                      test= dabs(fy-fxstar)
			          test1=1.d0+dabs(fxstar)
			          if(test/test1.lt.1.d-8)then
			          igual=igual+1

			   end if

					  L=L+1
					  
					  GO TO 20
				  end if

               	end if

				end if
	
! =================================================================

		    
	

 40            nfu=nfutotal

!               write(6,60)mejoray
!               write(1,60)mejoray
!60             format(/,' ***** Mejoray = ',i3,/)
               

				return

				end


            subroutine filled(n,x,f)
		   
		     implicit real*8(a-h,o-z)

	          parameter(nx=100)   ! dimension para funciones de hasta 100 variables
	 
	          ! No se usan en filled
			  !dimension y(nx), wa(9*nx+nx*(nx+1)/2+nx*nx+max(7*nx-nx*(nx+1)/2,0))
			  
			  !dimension x(1),bl(1),bu(1),jbound(1)
        dimension x(1)
			  
!	            dimension xstar(100),x(100),e(100,200)
                common/blk1/xstar(nx),e(2*nx,2*nx),q,fxstar,curvifgr_metodo
                !common/blk1/xstar,e,q,fxstar,metodo

	            t=f-fxstar
				
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

          subroutine ajusta(x,n,bl,bu)
		  implicit real*8(a-h,o-z)
		  dimension x(1),bl(1),bu(1)
		  	    
10			ireduce=0

			do i=1,n

!			  if(x(i).lt.bl(i).or.x(i).gt.bu(i))then

!    	         x(i)=0.9d0*x(i)
!		         ireduce=1
	        
!			  end if
			  if(x(i).lt.bl(i))x(i)=bl(i)+1d-3
              if(x(i).gt.bu(i))x(i)=bu(i)-1.d-3			
			end do

			if(ireduce.eq.1)then

			  go to 10
			else
			  return
			end if

		 end subroutine


			  




!****************************************************************************












