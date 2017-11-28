



def inspect_attrs(param, overlap):
    '''
    Check that given parameters are compatible with
    the overlap option.

    Parameters
    ----------
    param:
    overlap:
    '''
    names = param.keys()

    if overlap == False:
        assert isinstance(param['molecule'], list) == False
        assert 'ng_refs' in names
        assert 'ref_pts' in names
        assert 'wgt' in names
        assert 'w_diffuse' in names
        assert 'klin' in names

    if overlap == True:
        assert isinstance(param['molecule'], list) == True





def pipeline_fortran2ipynb2git(params=None, setup=None):
    '''
    Run Fortran code, followed by analysis notebook, then
    commit the analysis notebook to Git depository for 
    a given list of cases.

    Parameters
    ----------
    params: list-like
        List of dictionaries.  One dictionary for each set
        of lblnew input values.    
    overlap: boolean.  (Default: False)
             True for the overlap calculation.
             False for the best-fitting calculation for a single gas.
    gprocs: list
            List of subprocesses for the Git commit of each given case.
    '''
    from setup import run_fortran, analyse_case, git_addcommit

    print('Submitting radiation calculation for cases')
    procs = [run_fortran(param) for param in params]
    print()

    print('Submitting analysis for cases')
    aprocs = {}
    all_being_analysed = False
    while not all_being_analysed:
        
        for proc, param in zip(procs, params):
            if proc.poll() is None:
                continue
            else:
                if proc.pid in aprocs:
                    continue
                else:
                    aproc = analyse_case(param)
                    aprocs[proc.pid] = (aproc, param)
                
        if len(aprocs) == len(procs):
            all_being_analysed = True   
            [proc.kill() for proc in procs]
            break
            
        time.sleep(5)
    print()

    print('Committing analysis to Git repository for cases')
    gprocs = {}
    all_been_committed = False
    while not all_been_committed:
        
        for _, (aproc, param) in aprocs.items():
            if aproc.poll() is None:
                continue
            else:
                if aproc.pid in gprocs:
                    continue
                else:
                    gproc = git_addcommit(param)
                    out, err = gproc.communicate()
                    gprocs[aproc.pid] = (gproc, param)
                
        if len(gprocs) == len(aprocs):
            all_been_committed = True
            for _, (aproc, param) in aprocs.items():
                out, err = aproc.communicate()
                print('Jupyter notebook process stdout and stderr')
                print(out)
                print(err)
                print()
            break
            
        time.sleep(10)
    print()

    return gprocs





def test_lblnew_bestfit():
    import climatools.lblnew.setup_bestfit as setup
    params = [{}, {}, ...]
    git_procs3 = pipeline_fortran2ipynb2git(params, setup=setup)
#    git_procs2 = pipeline_ipynb2git(params)
#    git_procs1 = pipeline_fortran2ipynb(params)
    


def test_lblnewoverlap():
    import climatools.lblnew.setup_overlap as setup
    params = [{}, {}, ...]
    git_procs3 = pipeline_fortran2ipynb2git(params, setup=setup)



if __name__ == '__main__':
    pass




    
    
    
