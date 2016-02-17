

subroutine modal_aero_sw(pcols, &
     mass, specmmr, dgnumwet, qaerwat, &
     specdens, specrefindex, &
     extpsw, abspsw, asmpsw, &
     refrtabsw, refitabsw, crefwsw, &
     tauxar, wa, ga, fa)

   ! calculates aerosol sw radiative properties

  integer, parameter :: pver = 30
  integer, parameter :: ntot_amode = 3  ! there are 3 modes in MAM3
  integer, parameter :: nspec_amode(ntot_amode) = (/ 6, 3, 3 /) ! number of species in each mode in MAM3
  integer, parameter :: nspec_max = 6   ! maximum number of aerosol species in a mode
  integer, parameter :: ncoef = 5
  integer, parameter :: prefr = 7
  integer, parameter :: prefi = 10
  integer, parameter :: nswbands = 14 ! number of spectral bands in RRTMG-SW

  
  integer, intent(in) :: pcols                                      ! number of columns
   real(kind=8), intent(in) :: mass(pcols,pver)                          ! layer mass
   real(kind=8), intent(in) :: specmmr(nspec_max,ntot_amode, pcols, pver) ! species mass mixing ratio
   real(kind=8), intent(in) :: dgnumwet(pcols,pver,ntot_amode)            ! number mode diameter
   real(kind=8), intent(in) :: qaerwat(pcols,pver,ntot_amode)             ! aerosol water (g/g)
   real(kind=8), intent(in) :: specdens(nspec_max,ntot_amode)            ! species density (kg/m3)
   real(kind=8), intent(in) :: specrefindex(nspec_max,ntot_amode,nswbands)        ! species refractive index
   real(kind=8), intent(in) :: extpsw(ncoef,prefr,prefi,ntot_amode,nswbands)      ! specific extinction
   real(kind=8), intent(in) :: abspsw(ncoef,prefr,prefi,ntot_amode,nswbands)      ! specific absorption
   real(kind=8), intent(in) :: asmpsw(ncoef,prefr,prefi,ntot_amode,nswbands)      ! asymmetry factor
   real(kind=8), intent(in) :: refrtabsw(prefr,nswbands)        ! table of real refractive indices for aerosols visible
   real(kind=8), intent(in) :: refitabsw(prefi,nswbands)        ! table of imag refractive indices for aerosols visible
   complex, intent(in) :: crefwsw(nswbands) ! complex refractive index for water visible
   
   real(kind = 8), intent(out) :: tauxar(pcols,0:pver,nswbands) ! layer extinction optical depth
   real(kind = 8), intent(out) :: wa(pcols,0:pver,nswbands)     ! layer single-scatter albedo
   real(kind = 8), intent(out) :: ga(pcols,0:pver,nswbands)     ! asymmetry factor
   real(kind = 8), intent(out) :: fa(pcols,0:pver,nswbands)     ! forward scattered fraction

   ! Local variables
   integer :: i, isw, k, l, m, nc, ns

   real(kind = 8) :: radsurf(pcols,pver,ntot_amode)    ! aerosol surface mode radius
   real(kind = 8) :: logradsurf(pcols,pver,ntot_amode)    ! log(aerosol surface mode radius)
   real(kind = 8) :: cheb(ncoef,ntot_amode,pcols,pver)

   complex  :: crefin(pcols)   ! complex refractive index
   real(kind = 8) :: refr(pcols)     ! real part of refractive index
   real(kind = 8) :: refi(pcols)     ! imaginary part of refractive index

   real(kind = 8) :: vol(pcols)      ! volume concentration of aerosol specie (m3/kg)
   real(kind = 8) :: dryvol(pcols)   ! volume concentration of aerosol mode (m3/kg)
   real(kind = 8) :: watervol(pcols) ! volume concentration of water in each mode (m3/kg)
   real(kind = 8) :: wetvol(pcols)   ! volume concentration of wet mode (m3/kg)

   integer  :: itab(pcols), jtab(pcols)
   real(kind = 8) :: ttab(pcols), utab(pcols)
   real(kind = 8) :: cext(pcols,ncoef), cabs(pcols,ncoef), casm(pcols,ncoef)
   real(kind = 8) :: pext(pcols)     ! parameterized specific extinction (m2/kg)
   real(kind = 8) :: specpext(pcols) ! specific extinction (m2/kg)
   real(kind = 8) :: dopaer(pcols)   ! aerosol optical depth in layer
   real(kind = 8) :: pabs(pcols)     ! parameterized specific absorption (m2/kg)
   real(kind = 8) :: pasm(pcols)     ! parameterized asymmetry factor
   real(kind = 8) :: palb(pcols)     ! parameterized single scattering albedo

   !----------------------------------------------------------------------------

   ncol = pcols

   ! calc size parameter for all columns
   call modal_size_parameters(ncol, dgnumwet, radsurf, logradsurf, cheb)

   ! initialize output variables
   tauxar(:ncol,:,:) = 0.
   wa(:ncol,:,:)     = 0.
   ga(:ncol,:,:)     = 0.
   fa(:ncol,:,:)     = 0.

   ! zero'th layer does not contain aerosol
   tauxar(1:ncol,0,:)  = 0.
   wa(1:ncol,0,:)      = 0.925
   ga(1:ncol,0,:)      = 0.850
   fa(1:ncol,0,:)      = 0.7225


   ! loop over all aerosol modes
   do m = 1, ntot_amode

      do isw = 1, nswbands


         do k = 1, pver

            ! form bulk refractive index
            crefin(:ncol) = 0.
            dryvol(:ncol) = 0.

            ! aerosol species loop
            do l = 1, nspec_amode(m)
               do i = 1, ncol
                  vol(i)      = specmmr(l,m,i,k)/specdens(l,m)
                  dryvol(i)   = dryvol(i) + vol(i)
                  crefin(i)   = crefin(i) + vol(i)*specrefindex(l,m,isw)
               end do

            end do ! species loop


            do i = 1, ncol
               watervol(i) = qaerwat(i,k,m)/rhoh2o
               wetvol(i) = watervol(i) + dryvol(i)
               if (watervol(i) < 0.) then
                  watervol(i) = 0.
                  wetvol(i) = dryvol(i)
               end if

               ! volume mixing
               crefin(i) = crefin(i) + watervol(i)*crefwsw(isw)
               crefin(i) = crefin(i)/max(wetvol(i),1.e-60)
               refr(i)   = real(crefin(i))
               refi(i)   = abs(aimag(crefin(i)))
            end do

            ! call t_startf('binterp')

            ! interpolate coefficients linear in refractive index
            ! first call calcs itab,jtab,ttab,utab
            itab(:ncol) = 0
            call binterp(extpsw(:,:,:,m,isw), ncol, ncoef, prefr, prefi, &
                         refr, refi, refrtabsw(:,isw), refitabsw(:,isw), &
                         itab, jtab, ttab, utab, cext)
            call binterp(abspsw(:,:,:,m,isw), ncol, ncoef, prefr, prefi, &
                         refr, refi, refrtabsw(:,isw), refitabsw(:,isw), &
                         itab, jtab, ttab, utab, cabs)
            call binterp(asmpsw(:,:,:,m,isw), ncol, ncoef, prefr, prefi, &
                         refr, refi, refrtabsw(:,isw), refitabsw(:,isw), &
                         itab, jtab, ttab, utab, casm)

            ! call t_stopf('binterp')

            ! parameterized optical properties
            do i=1,ncol

               if (logradsurf(i,k,m) .le. xrmax) then
                  pext(i) = 0.5*cext(i,1)
                  do nc = 2, ncoef
                     pext(i) = pext(i) + cheb(nc,m,i,k)*cext(i,nc)
                  enddo
                  pext(i) = exp(pext(i))
               else
                  pext(i) = 1.5/(radsurf(i,k,m)*rhoh2o) ! geometric optics
               endif

               ! convert from m2/kg water to m2/kg aerosol
               specpext(i) = pext(i)
               pext(i) = pext(i)*wetvol(i)*rhoh2o
               pabs(i) = 0.5*cabs(i,1)
               pasm(i) = 0.5*casm(i,1)
               do nc = 2, ncoef
                  pabs(i) = pabs(i) + cheb(nc,m,i,k)*cabs(i,nc)
                  pasm(i) = pasm(i) + cheb(nc,m,i,k)*casm(i,nc)
               enddo
               pabs(i) = pabs(i)*wetvol(i)*rhoh2o
               pabs(i) = max(0.,pabs(i))
               pabs(i) = min(pext(i),pabs(i))

               palb(i) = 1.-pabs(i)/max(pext(i),1.e-40)
               palb(i) = 1.-pabs(i)/max(pext(i),1.e-40)

               dopaer(i) = pext(i)*mass(i,k)
            end do

            do i=1,ncol
               tauxar(i,k,isw) = tauxar(i,k,isw) + dopaer(i)
               wa(i,k,isw)     = wa(i,k,isw)     + dopaer(i)*palb(i)
               ga(i,k,isw)     = ga(i,k,isw)     + dopaer(i)*palb(i)*pasm(i)
               fa(i,k,isw)     = fa(i,k,isw)     + dopaer(i)*palb(i)*pasm(i)*pasm(i)
            end do

         end do ! pver

      end do ! sw bands

   end do ! ntot_amode





end subroutine modal_aero_sw



subroutine modal_size_parameters(ncol, dgnumwet, radsurf, logradsurf, cheb)

  integer, parameter :: ntot_amode = 3  ! there are 3 modes in MAM3
  real(kind = 8), parameter :: sigmag_amode(ntot_amode) = (/ 1.800, 1.600, 1.800 /) ! from modal_aero_data.F90

   integer,  intent(in)  :: ncol
   real(kind=8), intent(in)  :: dgnumwet(:,:,:)   ! aerosol wet number mode diameter (m)
   real(kind=8), intent(out) :: radsurf(:,:,:)    ! aerosol surface mode radius
   real(kind=8), intent(out) :: logradsurf(:,:,:) ! log(aerosol surface mode radius)
   real(kind=8), intent(out) :: cheb(:,:,:,:)

   integer  :: m, i, k, nc
   real(kind=8) :: explnsigma
   real(kind=8) :: xrad(ncol) ! normalized aerosol radius

  real(kind = 8) :: alnsg_amode(ntot_amode)


  alnsg_amode = log(sigmag_amode)

   do m = 1, ntot_amode

      explnsigma = exp(2.0*alnsg_amode(m)*alnsg_amode(m))

      do k = 1, pver
         do i = 1, ncol
            ! convert from number mode diameter to surface area
            radsurf(i,k,m) = 0.5*dgnumwet(i,k,m)*explnsigma
            logradsurf(i,k,m) = log(radsurf(i,k,m))
            ! normalize size parameter
            xrad(i) = max(logradsurf(i,k,m),xrmin)
            xrad(i) = min(xrad(i),xrmax)
            xrad(i) = (2.*xrad(i)-xrmax-xrmin)/(xrmax-xrmin)
            ! chebyshev polynomials
            cheb(1,m,i,k) = 1.
            cheb(2,m,i,k) = xrad(i)
            do nc = 3, ncoef
               cheb(nc,m,i,k) = 2.*xrad(i)*cheb(nc-1,m,i,k)-cheb(nc-2,m,i,k)
            end do
         end do
      end do

   end do

end subroutine modal_size_parameters

!===============================================================================

subroutine binterp(table,ncol,km,im,jm,x,y,xtab,ytab,ix,jy,t,u,out)

  !     bilinear interpolation of table
  !
  implicit none
  integer im,jm,km,ncol
  real(kind=8) table(km,im,jm),xtab(im),ytab(jm),out(ncol,km)
  integer i,ix(ncol),ip1,j,jy(ncol),jp1,k,ic
  real(kind=8) x(ncol),dx,t(ncol),y(ncol),dy,u(ncol), &
       tu(ncol),tuc(ncol),tcu(ncol),tcuc(ncol)
  
  if(ix(1).gt.0)go to 30
  if(im.gt.1)then
     do ic=1,ncol
        do i=1,im
           if(x(ic).lt.xtab(i))go to 10
        enddo
10      ix(ic)=max0(i-1,1)
        ip1=min(ix(ic)+1,im)
        dx=(xtab(ip1)-xtab(ix(ic)))
        if(abs(dx).gt.1.e-20)then
           t(ic)=(x(ic)-xtab(ix(ic)))/dx
        else
           t(ic)=0.
        endif
     end do
  else
     ix(:ncol)=1
     t(:ncol)=0.
  endif
  if(jm.gt.1)then
     do ic=1,ncol
        do j=1,jm
           if(y(ic).lt.ytab(j))go to 20
        enddo
20      jy(ic)=max0(j-1,1)
        jp1=min(jy(ic)+1,jm)
        dy=(ytab(jp1)-ytab(jy(ic)))
        if(abs(dy).gt.1.e-20)then
           u(ic)=(y(ic)-ytab(jy(ic)))/dy
        else
           u(ic)=0.
        endif
     end do
  else
     jy(:ncol)=1
     u(:ncol)=0.
  endif
30 continue
  do ic=1,ncol
     tu(ic)=t(ic)*u(ic)
     tuc(ic)=t(ic)-tu(ic)
     tcuc(ic)=1.-tuc(ic)-u(ic)
     tcu(ic)=u(ic)-tu(ic)
     jp1=min(jy(ic)+1,jm)
     ip1=min(ix(ic)+1,im)
     do k=1,km
        out(ic,k)=tcuc(ic)*table(k,ix(ic),jy(ic))+tuc(ic)*table(k,ip1,jy(ic))   &
             +tu(ic)*table(k,ip1,jp1)+tcu(ic)*table(k,ix(ic),jp1)
     end do
  enddo
  return
end subroutine binterp
