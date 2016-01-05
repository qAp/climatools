subroutine modal_aero_sw(state, pbuf, nnite, idxnite, &
                         tauxar, wa, ga, fa)

   ! calculates aerosol sw radiative properties

   type(physics_state), intent(in) :: state          ! state variables
   type(pbuf_fld),      intent(in) :: pbuf(:)        ! physics buffer
   integer,             intent(in) :: nnite          ! number of night columns
   integer,             intent(in) :: idxnite(nnite) ! local column indices of night columns

   real(r8), intent(out) :: tauxar(pcols,0:pver,nswbands) ! layer extinction optical depth
   real(r8), intent(out) :: wa(pcols,0:pver,nswbands)     ! layer single-scatter albedo
   real(r8), intent(out) :: ga(pcols,0:pver,nswbands)     ! asymmetry factor
   real(r8), intent(out) :: fa(pcols,0:pver,nswbands)     ! forward scattered fraction

   ! Local variables
   integer :: i, ifld, isw, k, l, m, nc, ns
   integer :: lchnk                    ! chunk id
   integer :: ncol                     ! number of active columns in the chunk

   real(r8), pointer :: dgnumwet(:,:,:)     ! number mode diameter
   real(r8), pointer :: qaerwat(:,:,:)      ! aerosol water (g/g)

   real(r8) :: mass(pcols,pver)        ! layer mass
   real(r8) :: air_density(pcols,pver) ! (kg/m3)

   type(r_ptr2d_t), allocatable :: specmmr(:,:) ! species mass mixing ratio
   real(r8),        allocatable :: specdens(:,:) ! species density (kg/m3)
   type(c_ptr1d_t), allocatable :: specrefindex(:,:) ! species refractive index

   real(r8), pointer :: radsurf(:,:,:)    ! aerosol surface mode radius
   real(r8), pointer :: logradsurf(:,:,:) ! log(aerosol surface mode radius)
   real(r8), pointer :: cheb(:,:,:,:)

   complex  :: crefin(pcols)   ! complex refractive index
   real(r8) :: refr(pcols)     ! real part of refractive index
   real(r8) :: refi(pcols)     ! imaginary part of refractive index

   real(r8) :: vol(pcols)      ! volume concentration of aerosol specie (m3/kg)
   real(r8) :: dryvol(pcols)   ! volume concentration of aerosol mode (m3/kg)
   real(r8) :: watervol(pcols) ! volume concentration of water in each mode (m3/kg)
   real(r8) :: wetvol(pcols)   ! volume concentration of wet mode (m3/kg)

   integer  :: itab(pcols), jtab(pcols)
   real(r8) :: ttab(pcols), utab(pcols)
   real(r8) :: cext(pcols,ncoef), cabs(pcols,ncoef), casm(pcols,ncoef)
   real(r8) :: pext(pcols)     ! parameterized specific extinction (m2/kg)
   real(r8) :: specpext(pcols) ! specific extinction (m2/kg)
   real(r8) :: dopaer(pcols)   ! aerosol optical depth in layer
   real(r8) :: pabs(pcols)     ! parameterized specific absorption (m2/kg)
   real(r8) :: pasm(pcols)     ! parameterized asymmetry factor
   real(r8) :: palb(pcols)     ! parameterized single scattering albedo

   ! Diagnostics output for visible band only
   real(r8) :: extinct(pcols,pver)
   real(r8) :: absorb(pcols,pver)
   real(r8) :: aodvis(pcols)               ! extinction optical depth
   real(r8) :: aodabs(pcols)               ! absorption optical depth
   real(r8) :: ssavis(pcols)
   real(r8) :: dustvol(pcols)              ! volume concentration of dust in aerosol mode (m3/kg)
   real(r8), pointer :: aodmode(:,:)
   real(r8), pointer :: dustaodmode(:,:)   ! dust aod in aerosol mode
   real(r8), pointer :: burden(:,:)
   real(r8), pointer :: colext(:,:)

   logical :: savaervis ! true if visible wavelength (0.55 micron)

   ! debug output
   integer, parameter :: nerrmax_dopaer=1000
   integer  :: nerr_dopaer = 0
   real(r8) :: volf            ! volume fraction of insoluble aerosol
   character(len=*), parameter :: subname = 'modal_aero_sw'
   !----------------------------------------------------------------------------

   lchnk = state%lchnk
   ncol  = state%ncol

   ! allocate local storage
   allocate( &
      radsurf(pcols,pver,ntot_amode),    &
      logradsurf(pcols,pver,ntot_amode), &
      cheb(ncoef,ntot_amode,pcols,pver), &
      aodmode(pcols,ntot_amode),         &
      dustaodmode(pcols,ntot_amode),     &
      burden(pcols,ntot_amode),          &
      colext(pcols,ntot_amode))

   ! pointers to physics buffer
   ifld = pbuf_get_fld_idx('DGNUMWET')
   dgnumwet => pbuf(ifld)%fld_ptr(1,:,:,lchnk,:)

   ifld = pbuf_get_fld_idx('QAERWAT')
   if (associated(pbuf(ifld)%fld_ptr)) then
      qaerwat => pbuf(ifld)%fld_ptr(1,:,:,lchnk,:)
   else
      call endrun(subname//': pbuf for QAERWAT not allocated')
   end if

   ! calc size parameter for all columns
   call modal_size_parameters(ncol, dgnumwet, radsurf, logradsurf, cheb)

   ! initialize output variables
   tauxar(:ncol,:,:) = 0._r8
   wa(:ncol,:,:)     = 0._r8
   ga(:ncol,:,:)     = 0._r8
   fa(:ncol,:,:)     = 0._r8

   ! zero'th layer does not contain aerosol
   tauxar(1:ncol,0,:)  = 0._r8
   wa(1:ncol,0,:)      = 0.925_r8
   ga(1:ncol,0,:)      = 0.850_r8
   fa(1:ncol,0,:)      = 0.7225_r8

   mass(:ncol,:)        = state%pdeldry(:ncol,:)*rga
   air_density(:ncol,:) = state%pmid(:ncol,:)/(rair*state%t(:ncol,:))


   ! access the mixing ratio and properties of the modal species
   allocate( &
      specmmr(nspec_max,ntot_amode),     &
      specdens(nspec_max,ntot_amode),    &
      specrefindex(nspec_max,ntot_amode) )

   do m = 1, ntot_amode
      do l = 1, nspec_amode(m)
         call rad_cnst_get_aer_mmr(0, spec_idx(l,m),  state, pbuf, specmmr(l,m)%val)
         call rad_cnst_get_aer_props(0, spec_idx(l,m), density_aer=specdens(l,m), &
                                     refindex_aer_sw=specrefindex(l,m)%val)
      end do
   end do

   ! loop over all aerosol modes
   do m = 1, ntot_amode

      do isw = 1, nswbands


         do k = 1, pver

            ! form bulk refractive index
            crefin(:ncol) = 0._r8
            dryvol(:ncol) = 0._r8
            dustvol(:ncol) = 0._r8

            ! aerosol species loop
            do l = 1, nspec_amode(m)
               do i = 1, ncol
                  vol(i)      = specmmr(l,m)%val(i,k)/specdens(l,m)
                  dryvol(i)   = dryvol(i) + vol(i)
                  crefin(i)   = crefin(i) + vol(i)*specrefindex(l,m)%val(isw)
               end do

            end do ! species loop


            do i = 1, ncol
               watervol(i) = qaerwat(i,k,m)/rhoh2o
               wetvol(i) = watervol(i) + dryvol(i)
               if (watervol(i) < 0._r8) then
                  if (abs(watervol(i)) .gt. 1.e-1*wetvol(i)) then
                     write(iulog,'(a,4e10.2,a)') 'watervol,wetvol=', &
                        watervol(i), wetvol(i), ' in '//subname
                     !  call endrun()
                  end if
                  watervol(i) = 0._r8
                  wetvol(i) = dryvol(i)
               end if

               ! volume mixing
               crefin(i) = crefin(i) + watervol(i)*crefwsw(isw)
               crefin(i) = crefin(i)/max(wetvol(i),1.e-60_r8)
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
                  pext(i) = 0.5_r8*cext(i,1)
                  do nc = 2, ncoef
                     pext(i) = pext(i) + cheb(nc,m,i,k)*cext(i,nc)
                  enddo
                  pext(i) = exp(pext(i))
               else
                  pext(i) = 1.5_r8/(radsurf(i,k,m)*rhoh2o) ! geometric optics
               endif

               ! convert from m2/kg water to m2/kg aerosol
               specpext(i) = pext(i)
               pext(i) = pext(i)*wetvol(i)*rhoh2o
               pabs(i) = 0.5_r8*cabs(i,1)
               pasm(i) = 0.5_r8*casm(i,1)
               do nc = 2, ncoef
                  pabs(i) = pabs(i) + cheb(nc,m,i,k)*cabs(i,nc)
                  pasm(i) = pasm(i) + cheb(nc,m,i,k)*casm(i,nc)
               enddo
               pabs(i) = pabs(i)*wetvol(i)*rhoh2o
               pabs(i) = max(0._r8,pabs(i))
               pabs(i) = min(pext(i),pabs(i))

               palb(i) = 1._r8-pabs(i)/max(pext(i),1.e-40_r8)
               palb(i) = 1._r8-pabs(i)/max(pext(i),1.e-40_r8)

               dopaer(i) = pext(i)*mass(i,k)
            end do



            do i = 1, ncol

               if ((dopaer(i) <= -1.e-10) .or. (dopaer(i) >= 30.)) then

                  write(iulog,*) 'dopaer(', i, ',', k, ',', m, ',', lchnk, ')=', dopaer(i)
                  ! write(iulog,*) 'itab,jtab,ttab,utab=',itab(i),jtab(i),ttab(i),utab(i)
                  write(iulog,*) 'k=', k, ' pext=', pext(i), ' specext=', specpext(i)
                  write(iulog,*) 'wetvol=', wetvol(i), ' dryvol=', dryvol(i), ' watervol=', watervol(i)
                  ! write(iulog,*) 'cext=',(cext(i,l),l=1,ncoef)
                  ! write(iulog,*) 'crefin=',crefin(i)
                  write(iulog,*) 'nspec_amode(m)=', nspec_amode(m)
                  ! write(iulog,*) 'cheb=', (cheb(nc,m,i,k),nc=2,ncoef)
                  do l = 1, nspec_amode(m)
                     volf = specmmr(l,m)%val(i,k)/specdens(l,m)
                     write(iulog,*) 'l=', l, 'vol(l)=', volf
                     write(iulog,*) 'isw=', isw, 'specrefindex(isw)=', specrefindex(l,m)%val(isw)
                     write(iulog,*) 'specdens=', specdens(l,m)
                  end do

                  nerr_dopaer = nerr_dopaer + 1
                  if (nerr_dopaer >= nerrmax_dopaer) then
                     ! write(iulog,*) '*** halting in '//subname//' after nerr_dopaer =', nerr_dopaer
                     ! call endrun('exit from '//subname)
                  end if

               end if
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



   ! deallocate local storage
   deallocate( &
      radsurf,     &
      logradsurf,  &
      cheb,        &
      aodmode,     &
      dustaodmode, &
      burden,      &
      colext)

   deallocate( &
      specmmr,    &
      specdens,   &
      specrefindex)

end subroutine modal_aero_sw
