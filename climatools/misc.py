import re



def any_unique_labels(levels, labels):
    '''
    For 2 lists, levels and labels, of equal lengths whose elements
    correspond to each other, return the unique elements in labels
    and the first corresponding elements in levels.
    '''
    unique_labels = list(set(labels))
    unique_levels = [levels[index]
                     for index in [labels.index(unique_label)
                                   for unique_label in unique_labels]]
    return unique_levels, unique_labels


def print_datatset_longnames(ds):
    '''
    prints variables\' long names against names.
    INPUT:
    ds --- xray Dataset
    '''
    for k, v in ds.items():
        print(k, '----------', v.attrs.get('long_name'))


def get_subroutine_bodies_from_Fortran(fortran):
    '''
    Returns subroutines from a piece of fortran
    INPUT:
    fortran --- string of fortran code
    OUTPUT:
    a list of zero or more strings of subroutines in fortran
    '''
    regex = re.compile(r'''
    \n
    (?: real\(r8\))?
    \s*
    (?: \b function \b | \b subroutine \b)
    ''', re.VERBOSE)
    return regex.split(fortran)[1:]


def get_Fortran_subroutine_name(fortran):
    '''
    Returns name of subroutine in Fortran
    INPUT:
    fortran --- string of Fortran subroutine
    OUTPUT --- subroutine\'s name
    '''
    firstline = fortran.split('\n')[0].strip()
    regex = re.compile(r'''
    (\w+)
    ''', re.VERBOSE)
    match = regex.match(firstline)
    if match:
        return match.groups()[0]
    else:
        return 'None'




def get_called_Fortran_subroutine_names(fortran):
    '''
    Returns name(s) of subroutine(s) called within
    a piece of Fortran
    INPUT:
    fortran  ---- piece of Fortran
    OUTPUT:
    set of names of called subroutines
    '''
    regex = re.compile(r'\n\s*call\s+(\w+)\s*&?\s*\(')
    return set(regex.findall(fortran))
