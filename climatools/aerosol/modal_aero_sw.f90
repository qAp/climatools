subroutine modal_aero_sw(state, pbuf, &
                         tauxar, wa, ga, fa)

   ! calculates aerosol sw radiative properties

  integer, parameter :: pcols = 1
  integer, parameter :: ncol = 1
  integer, parameter :: pver = 30
  integer, parameter :: ncoef = 5
  integer, parameter :: prefr = 7
  integer, parameter :: prefi = 10
  integer, parameter :: nswbands = 14 ! number of spectral bands in RRTMG-SW

   real(kind=8), intent(in) :: mass(pcols,pver)                          ! layer mass
   real(kind=8), intent(in) :: specmmr(nspec_max,ntot_amode, ncol, pver) ! species mass mixing ratio
   real(kind=8), intent(in) :: dgnumwet(ncol,pver,ntot_amode)            ! number mode diameter
   real(kind=8), intent(in) :: qaerwat(ncol,pver,ntot_amode)             ! aerosol water (g/g)
   real(kind=8), intent(in) :: specdens(nspec_max,ntot_amode)            ! species density (kg/m3)
   real(kind=8), intent(in) :: specrefindex(nspec_max,ntot_amode)        ! species refractive index

   real(kind = 8), intent(out) :: tauxar(pcols,0:pver,nswbands) ! layer extinction optical depth
   real(kind = 8), intent(out) :: wa(pcols,0:pver,nswbands)     ! layer single-scatter albedo
   real(kind = 8), intent(out) :: ga(pcols,0:pver,nswbands)     ! asymmetry factor
   real(kind = 8), intent(out) :: fa(pcols,0:pver,nswbands)     ! forward scattered fraction

   ! Local variables
   integer :: i, isw, k, l, m, nc, ns

   real(kind = 8), intent(in) :: radsurf(pcols,pver,ntot_amode)    ! aerosol surface mode radius
   real(kind = 8), intent(in) :: logradsurf(pcols,pver,ntot_amode)    ! log(aerosol surface mode radius)
   real(kind = 8), intent(in) :: cheb(ncoef,ntot_amode,pcols,pver)

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




   ! access the mixing ratio and properties of the modal species
   allocate( &
      ,     &
      specdens(nspec_max,ntot_amode),    &
      specrefindex(nspec_max,ntot_amode) )


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
                  crefin(i)   = crefin(i) + vol(i)*specrefindex(l,m)%val(isw)
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
