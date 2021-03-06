                                                                                                                             
                                                                                                                             
!----------------------------------------------------------------------
subroutine modal_aero_wateruptake_sub(                &
     pcols,                         &
     cldn, relative_humidity,      &
     raer, qaerwat,           &
     dgncur_awet, wetdens             )
  
  
  
  implicit none
  
  
  integer, parameter :: pver  = 30
  
  real (kind = 8), parameter :: pi = 3.14159265 
  real (kind = 8), parameter :: rhoh2o = 1000.  ! density of water = 1000 kg/m3
  
  integer, parameter :: ntot_amode = 3   ! 3 modes in MAM3
  integer, parameter :: nspec_amode(ntot_amode) = (/ 6, 3, 3 /) ! number of species in each mode in MAM3
  integer, parameter :: max_nspec_amode = 6 ! maximum number of species in a mode
  real(kind = 8), parameter :: rhdeliques_amode(ntot_amode) = (/ 0.800, 0.800, 0.800 /) ! from modal_aero_data.F90
  real(kind = 8), parameter :: rhcrystal_amode(ntot_amode)  = (/ 0.350, 0.350, 0.350 /) ! from modal_aero_data.F90
  real(kind = 8), parameter :: sigmag_amode(ntot_amode) = (/ 1.800, 1.600, 1.800 /) ! from modal_aero_data.F90
  real(kind = 8), parameter :: dgnum_amode(ntot_amode)   = (/ 0.1100e-6, 0.0260e-6, 2.000e-6 /)  
  
  ! material density of aerosol (from physprop)
  real(kind = 8), dimension(ntot_amode, max_nspec_amode), parameter :: & 
       specdens_amode = reshape((/ 1770.0, 1000.0, 1000.0, 1700.0, 2600.0, 1900.0, &
       1770.0, 1000.0, 1900.0, -9999., -9999., -9999., &
       2600.0, 1900.0, 1770.0, -9999., -9999., -9999. /), &
       (/ ntot_amode, max_nspec_amode /), &
       (/-9999., -9999./), &
       (/2, 1/))
  
  ! hygroscopicity of aerosol (from physprop)
  real(kind = 8), dimension(ntot_amode, max_nspec_amode), parameter :: &
       spechygro = reshape((/ 0.507, 0.10000000010000001, 0.14, 1.000000013351432e-10, 0.068, 1.16, &
       0.507, 0.14, 1.16, -9999., -9999., -9999., &
       0.068, 1.16, 0.507, -9999., -9999., -9999. /), &
       (/ ntot_amode, max_nspec_amode /), &
       (/-9999., -9999./), &
       (/2, 1/))
  
  real(kind = 8) :: alnsg_amode(ntot_amode)
  
  
  
  integer,  intent(in)  :: pcols               ! number of columns
  real(kind = 8), intent(in)  :: cldn(pcols,pver)   ! layer cloud fraction (0-1)
  real(kind = 8), intent(in)  :: raer(pcols,pver,ntot_amode,max_nspec_amode)   ! aerosol species MRs (kg/kg and #/kg)
  real(kind = 8), intent(in) :: relative_humidity(pcols,pver)        ! relative humidity (0-1)

  real(kind = 8), intent(out)   :: qaerwat(pcols,pver,ntot_amode)
  real(kind = 8), intent(out)   :: dgncur_awet(pcols,pver,ntot_amode)
  real(kind = 8), intent(out)   :: wetdens(pcols,pver,ntot_amode)
  
  
  !     local variables
  
  integer i,k,m
  integer icol_diag
  integer l ! species index
  
  real(kind = 8) density_water                   ! density of water (kg/m3)
  real(kind = 8) drydens(ntot_amode)   ! dry particle density  (kg/m^3)
  real(kind = 8) drymass(ntot_amode)   ! single-particle-mean dry mass  (kg)
  real(kind = 8) dryrad(pcols,pver,ntot_amode) ! dry volume mean radius of aerosol (m)
  real(kind = 8) dryvol(ntot_amode)    ! single-particle-mean dry volume (m3)
  real(kind = 8) dryvolmr(ntot_amode)  ! volume MR for aerosol mode (m3/kg)
  real(kind = 8) duma, dumb
  real(kind = 8) hygro(ntot_amode)     ! volume-weighted mean hygroscopicity (--)
  real(kind = 8) hystfac(ntot_amode)   ! working variable for hysteresis
  real(kind = 8) pi43
  real(kind = 8) qwater                ! aerosol water MR
  real(kind = 8) :: rh(pcols,pver)        ! relative humidity (0-1)
  real(kind = 8) third
  real(kind = 8) v2ncur_a(pcols,pver,ntot_amode)
  real(kind = 8) wtrvol(ntot_amode)    ! single-particle-mean water volume in wet aerosol (m3)
  real(kind = 8) wetvol(ntot_amode)    ! single-particle-mean wet volume (m3)
  
  real(kind = 8) :: maer(pcols,pver,ntot_amode)
  ! aerosol wet mass MR (including water) (kg/kg-air)
  real(kind = 8) :: naer(pcols,pver,ntot_amode)
  ! aerosol number MR (bounded!) (#/kg-air)
  real(kind = 8) :: wetrad(pcols,pver,ntot_amode)  
  ! wet radius of aerosol (m)

  real(kind = 8) :: dgncur_a(pcols,pver,ntot_amode)
  
  !-----------------------------------------------------------------------
  
  
  rh(:, :) = relative_humidity(:, :)  
  
  alnsg_amode = log(sigmag_amode)
  third=1./3.
  pi43 = pi*4.0/3.0
  density_water = rhoh2o   ! is (kg/m3)
  
  
  do i = 1, pcols
     do k = 1, pver
        dgncur_a(i, k, :) = dgnum_amode(:)
     end do
  end do
  


  do m=1,ntot_amode
     hystfac(m) = 1.0 / max( 1.0e-5,   &
          (rhdeliques_amode(m)-rhcrystal_amode(m)) )
  enddo
  
  ! main loops over i, k

  
  do k=1,pver
     do i=1,pcols
        
        rh(i,k) = max(rh(i,k),0.0)
        rh(i,k) = min(rh(i,k),0.98)
        if (cldn(i,k) .lt. 1.0) then
           rh(i,k) = (rh(i,k) - cldn(i,k)) / (1.0 - cldn(i,k))  ! clear portion
        end if
        rh(i,k) = max(rh(i,k),0.0)
        
        
        !     compute dryvolmr, maer, naer for each mode
        do m=1,ntot_amode
           
           maer(i,k,m)=0.
           dryvolmr(m)=0.
           hygro(m)=0.
           do l = 1, nspec_amode(m)
              duma = raer(i,k,m,l)
              maer(i,k,m) = maer(i,k,m) + duma
              dumb = duma/specdens_amode(m,l)
              dryvolmr(m) = dryvolmr(m) + dumb
              hygro(m) = hygro(m) + dumb*spechygro(m,l)
           enddo
           if (dryvolmr(m) > 1.0e-30) then
              hygro(m) = hygro(m)/dryvolmr(m)
           else
              hygro(m) = spechygro(m,1)
           end if
           
           !     naer = aerosol number (#/kg)
           !     the new v2ncur_a replaces old coding here
           v2ncur_a(i,k,m) = 1. / ( (pi/6.)*                            &
                (dgncur_a(i,k,m)**3.)*exp(4.5*alnsg_amode(m)**2.) )
           naer(i,k,m) = dryvolmr(m)*v2ncur_a(i,k,m)
        enddo   !m=1,ntot_amode
        
        !     compute mean (1 particle) dry volume and mass for each mode
        !     old coding is replaced because the new (1/v2ncur_a) is equal to
        !        the mean particle volume
        !     also moletomass forces maer >= 1.0e-30, so (maer/dryvolmr)
        !        should never cause problems (but check for maer < 1.0e-31 anyway)
        do m=1,ntot_amode
           if (maer(i,k,m) .gt. 1.0e-31) then
              drydens(m) = maer(i,k,m)/dryvolmr(m)
           else
              drydens(m) = 1.0
           end if
           dryvol(m) = 1.0/v2ncur_a(i,k,m)
           drymass(m) = drydens(m)*dryvol(m)
           dryrad(i,k,m) = (dryvol(m)/pi43)**third
        enddo
        
        !     compute wet radius for each mode
        do m=1,ntot_amode
           call modal_aero_kohler(                          &
                dryrad(i,k,m), hygro(m), rh(i,k),        &
                wetrad(i,k,m), 1, 1                      )
           
           wetrad(i,k,m)=max(wetrad(i,k,m),dryrad(i,k,m))
           dgncur_awet(i,k,m) = dgncur_a(i,k,m)*   &
                (wetrad(i,k,m)/dryrad(i,k,m))
           wetvol(m) = pi43*wetrad(i,k,m)*wetrad(i,k,m)*wetrad(i,k,m)
           wetvol(m) = max(wetvol(m),dryvol(m))
           wtrvol(m) = wetvol(m) - dryvol(m)
           wtrvol(m) = max( wtrvol(m), 0.0 )

           !     apply simple treatment of deliquesence/crystallization hysteresis
           !     for rhcrystal < rh < rhdeliques, aerosol water is a fraction of
           !     the "upper curve" value, and the fraction is a linear function of rh
           if (rh(i,k) < rhcrystal_amode(m)) then
              wetrad(i,k,m) = dryrad(i,k,m)
              wetvol(m) = dryvol(m)
              wtrvol(m) = 0.0
           else if (rh(i,k) < rhdeliques_amode(m)) then
              wtrvol(m) = wtrvol(m)*hystfac(m)   &
                   *(rh(i,k) - rhcrystal_amode(m))
              wtrvol(m) = max( wtrvol(m), 0.0 )
              wetvol(m) = dryvol(m) + wtrvol(m)
              wetrad(i,k,m) = (wetvol(m)/pi43)**third
           end if
           
           !     compute aer. water tendency = (new_water - old_water)/deltat
           !     [ either (kg-h2o/kg-air/s) or (mol-h2o/mol-air/s) ]
           !           lwater = lwaterptr_amode(m) - loffset
           duma = 1.0
           qwater = density_water*naer(i,k,m)*wtrvol(m)*duma
           
           !     old_water (after modal_aero_calcsize) is 
           !           qwater_old = raer(i,k,lwater) + raertend(i,k,lwater)*deltat
           !     and water tendency is
           !           raertend(i,k,lwater) = raertend(i,k,lwater)   &
           !                                + (qwater - qwater_old)/deltat
           !     which is equivalent to
           !           raertend(i,k,lwater) = (qwater - raer(i,k,lwater))/deltat
           qaerwat(i,k,m) = qwater
           
           !     compute aerosol wet density (kg/m3)
           if (wetvol(m) > 1.0e-30) then
              wetdens(i,k,m) = (drymass(m) + density_water*wtrvol(m))/wetvol(m)
           else
              wetdens(i,k,m) = specdens_amode(m,1)
           end if
           
        enddo
        
        
     end do   ! "i=1,pcols"
  end do   ! "k=1,pver"
  
  
  
  return
end subroutine modal_aero_wateruptake_sub


!-----------------------------------------------------------------------
subroutine modal_aero_kohler(   &
     rdry_in, hygro, s, rwet_out, im, imx )
  
  ! calculates equlibrium radius r of haze droplets as function of
  ! dry particle mass and relative humidity s using kohler solution
  ! given in pruppacher and klett (eqn 6-35)
  
  ! for multiple aerosol types, assumes an internal mixture of aerosols
  
  implicit none
  
  ! arguments
  integer :: im         ! number of grid points to be processed
  integer :: imx        ! dimensioned number of grid points
  real(kind = 8) :: rdry_in(imx)    ! aerosol dry radius (m)
  real(kind = 8) :: hygro(imx)      ! aerosol volume-mean hygroscopicity (--)
  real(kind = 8) :: s(imx)          ! relative humidity (1 = saturated)
  real(kind = 8) :: rwet_out(imx)   ! aerosol wet radius (m)
  
  ! local variables
  integer, parameter :: imax=200
  integer :: i, n, nsol
  
  real(kind = 8) :: a, b
  real(kind = 8) :: p40(imax),p41(imax),p42(imax),p43(imax) ! coefficients of polynomial
  real(kind = 8) :: p30(imax),p31(imax),p32(imax) ! coefficients of polynomial
  real(kind = 8) :: p
  real(kind = 8) :: r3, r4
  real(kind = 8) :: r(imx)        ! wet radius (microns)
  real(kind = 8) :: rdry(imax)    ! radius of dry particle (microns)
  real(kind = 8) :: ss            ! relative humidity (1 = saturated)
  real(kind = 8) :: slog(imax)    ! log relative humidity
  real(kind = 8) :: vol(imax)     ! total volume of particle (microns**3)
  real(kind = 8) :: xi, xr
  
  complex(kind = 8) :: cx4(4,imax),cx3(3,imax)
  
  real(kind = 8), parameter :: eps = 1.e-4
  real(kind = 8), parameter :: mw = 18.
  real(kind = 8), parameter :: pi = 3.14159
  real(kind = 8), parameter :: rhow = 1.
  real(kind = 8), parameter :: surften = 76.
  real(kind = 8), parameter :: tair = 273.
  real(kind = 8), parameter :: third = 1./3.
  real(kind = 8), parameter :: ugascon = 8.3e7
  
  
  !     effect of organics on surface tension is neglected
  a=2.e4*mw*surften/(ugascon*tair*rhow)
  
  do i=1,im
     rdry(i) = rdry_in(i)*1.0e6   ! convert (m) to (microns)
     vol(i) = rdry(i)**3          ! vol is r**3, not volume
     b = vol(i)*hygro(i)
     
     !          quartic
     ss=min(s(i),1.-eps)
     ss=max(ss,1.e-10)
     slog(i)=log(ss)
     p43(i)=-a/slog(i)
     p42(i)=0.
     p41(i)=b/slog(i)-vol(i)
     p40(i)=a*vol(i)/slog(i)
     !          cubic for rh=1
     p32(i)=0.
     p31(i)=-b/a
     p30(i)=-vol(i)
  end do
  
  
  do 100 i=1,im
     
     !       if(vol(i).le.1.e-20)then
     if(vol(i).le.1.e-12)then
        r(i)=rdry(i)
        go to 100
     endif
     
     p=abs(p31(i))/(rdry(i)*rdry(i))
     if(p.lt.eps)then
        !          approximate solution for small particles
        r(i)=rdry(i)*(1.+p*third/(1.-slog(i)*rdry(i)/a))
     else
        call makoh_quartic(cx4(1,i),p43(i),p42(i),p41(i),p40(i),1)
        !          find smallest real(r8) solution
        r(i)=1000.*rdry(i)
        nsol=0
        do n=1,4
           xr=real(cx4(n,i))
           xi=imag(cx4(n,i))
           if(abs(xi).gt.abs(xr)*eps) cycle  
           if(xr.gt.r(i)) cycle  
           if(xr.lt.rdry(i)*(1.-eps)) cycle  
           if(xr.ne.xr) cycle  
           r(i)=xr
           nsol=n
        end do
        if(nsol.eq.0)then
           write(*,*)   &
                'ccm kohlerc - no real(r8) solution found (quartic)'
           write(*,*)'roots =', (cx4(n,i),n=1,4)
           write(*,*)'p0-p3 =', p40(i), p41(i), p42(i), p43(i)
           write(*,*)'rh=',s(i)
           write(*,*)'setting radius to dry radius=',rdry(i)
           r(i)=rdry(i)
           !             stop
        endif
     endif
     
     if(s(i).gt.1.-eps)then
        !          save quartic solution at s=1-eps
        r4=r(i)
        !          cubic for rh=1
        p=abs(p31(i))/(rdry(i)*rdry(i))
        if(p.lt.eps)then
           r(i)=rdry(i)*(1.+p*third)
        else
           call makoh_cubic(cx3,p32,p31,p30,im)
           !             find smallest real(r8) solution
           r(i)=1000.*rdry(i)
           nsol=0
           do n=1,3
              xr=real(cx3(n,i))
              xi=imag(cx3(n,i))
              if(abs(xi).gt.abs(xr)*eps) cycle  
              if(xr.gt.r(i)) cycle  
              if(xr.lt.rdry(i)*(1.-eps)) cycle  
              if(xr.ne.xr) cycle  
              r(i)=xr
              nsol=n
           end do
           if(nsol.eq.0)then
              write(*,*)   &
                   'ccm kohlerc - no real(r8) solution found (cubic)'
              write(*,*)'roots =', (cx3(n,i),n=1,3)
              write(*,*)'p0-p2 =', p30(i), p31(i), p32(i)
              write(*,*)'rh=',s(i)
              write(*,*)'setting radius to dry radius=',rdry(i)
              r(i)=rdry(i)
              !                stop
           endif
        endif
        r3=r(i)
        !          now interpolate between quartic, cubic solutions
        r(i)=(r4*(1.-s(i))+r3*(s(i)-1.+eps))/eps
     endif
     
100  continue
     
  ! bound and convert from microns to m
  do i=1,im
     r(i) = min(r(i),30.) ! upper bound based on 1 day lifetime
     rwet_out(i) = r(i)*1.e-6
  end do
     
  return
end subroutine modal_aero_kohler
   
   
   !-----------------------------------------------------------------------
subroutine makoh_cubic( cx, p2, p1, p0, im )
     !
     !     solves  x**3 + p2 x**2 + p1 x + p0 = 0
     !     where p0, p1, p2 are real
     !
     integer, parameter :: imx=200
     integer :: im
     real(kind = 8) :: p0(imx), p1(imx), p2(imx)
     complex(kind = 8) :: cx(3,imx)
     
     integer :: i
     real(kind = 8) :: eps, q(imx), r(imx), sqrt3, third
     complex(kind = 8) :: ci, cq, crad(imx), cw, cwsq, cy(imx), cz(imx)
     
     save eps
     data eps/1.e-20/
     
     third=1./3.
     ci=dcmplx(0.,1.)
     sqrt3=sqrt(3.)
     cw=0.5*(-1+ci*sqrt3)
     cwsq=0.5*(-1-ci*sqrt3)
     
     do i=1,im
        if(p1(i).eq.0.)then
           !        completely insoluble particle
           cx(1,i)=(-p0(i))**third
           cx(2,i)=cx(1,i)
           cx(3,i)=cx(1,i)
        else
           q(i)=p1(i)/3.
           r(i)=p0(i)/2.
           crad(i)=r(i)*r(i)+q(i)*q(i)*q(i)
           crad(i)=sqrt(crad(i))
           
           cy(i)=r(i)-crad(i)
           if (abs(cy(i)).gt.eps) cy(i)=cy(i)**third
           cq=q(i)
           cz(i)=-cq/cy(i)
           
           cx(1,i)=-cy(i)-cz(i)
           cx(2,i)=-cw*cy(i)-cwsq*cz(i)
           cx(3,i)=-cwsq*cy(i)-cw*cz(i)
        endif
     enddo
     
     return
end subroutine makoh_cubic
   
   
   !-----------------------------------------------------------------------
subroutine makoh_quartic( cx, p3, p2, p1, p0, im )
     
     !     solves x**4 + p3 x**3 + p2 x**2 + p1 x + p0 = 0
     !     where p0, p1, p2, p3 are real
     !
     integer, parameter :: imx=200
     integer :: im
     real(kind = 8) :: p0(imx), p1(imx), p2(imx), p3(imx)
     complex(kind = 8) :: cx(4,imx)
     
     integer :: i
     real(kind = 8) :: third, q(imx), r(imx)
     complex(kind = 8) :: cb(imx), cb0(imx), cb1(imx),   &
          crad(imx), cy(imx), czero
     
     
     czero=cmplx(0.0,0.0)
     third=1./3.
     
     do 10 i=1,im
        
        q(i)=-p2(i)*p2(i)/36.+(p3(i)*p1(i)-4*p0(i))/12.
        r(i)=-(p2(i)/6)**3+p2(i)*(p3(i)*p1(i)-4*p0(i))/48.   &
             +(4*p0(i)*p2(i)-p0(i)*p3(i)*p3(i)-p1(i)*p1(i))/16
        
        crad(i)=r(i)*r(i)+q(i)*q(i)*q(i)
        crad(i)=sqrt(crad(i))
        
        cb(i)=r(i)-crad(i)
        if(cb(i).eq.czero)then
           !        insoluble particle
           cx(1,i)=(-p1(i))**third
           cx(2,i)=cx(1,i)
           cx(3,i)=cx(1,i)
           cx(4,i)=cx(1,i)
        else
           cb(i)=cb(i)**third
           
           cy(i)=-cb(i)+q(i)/cb(i)+p2(i)/6
           
           cb0(i)=sqrt(cy(i)*cy(i)-p0(i))
           cb1(i)=(p3(i)*cy(i)-p1(i))/(2*cb0(i))
           
           cb(i)=p3(i)/2+cb1(i)
           crad(i)=cb(i)*cb(i)-4*(cy(i)+cb0(i))
           crad(i)=sqrt(crad(i))
           cx(1,i)=(-cb(i)+crad(i))/2.
           cx(2,i)=(-cb(i)-crad(i))/2.
           
           cb(i)=p3(i)/2-cb1(i)
           crad(i)=cb(i)*cb(i)-4*(cy(i)-cb0(i))
           crad(i)=sqrt(crad(i))
           cx(3,i)=(-cb(i)+crad(i))/2.
           cx(4,i)=(-cb(i)-crad(i))/2.
        endif
10      continue
        
        return
end subroutine makoh_quartic
      
      !----------------------------------------------------------------------
      



