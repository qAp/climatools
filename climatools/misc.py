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



def Fortran_subroutine_to_dict(fortran_subroutine):
    '''
    Returns a dictionary where the only key is the name of
    subroutine, and the value is a list of nested subroutines,
    one-level down. This applies to only ONE subroutine.
    INPUT:
    fortran_subroutine --- string. Fortran subroutine.
    OUTPUT:
    dict of {name of subroutine: list of nested subroutines}
    '''
    name = get_Fortran_subroutine_name(fortran_subroutine)
    childs = get_called_Fortran_subroutine_names(fortran_subroutine)
    return {name: list(childs)}



def Fortran_subroutine_childs_dict(subr_childs_list):
    '''
    INPUT:
    subr_childs_list --- a list of dictionaries of subroutines and their child subroutines
    OUTPUT:
    subr_childs_dict --- dictionary of subroutines and their child subroutines
    '''
    subr_childs_dict = {}
    [subr_childs_dict.update(subr) for subr in subr_childs_list]
    return subr_childs_dict



def Fortran_subroutine_parents_dict(subr_childs_dict):
    '''
    INPUT:
    subr_childs_dict --- dictionary of subroutines and their child subroutines
    OUTPUT:
    subr_parents_dict --- dictionary of subroutines and their parent subroutines
    '''
    subr_parents_dict = {}
    for name in subr_childs_dict.keys():
        subr_parents_dict[name] = []
        for potential_parent, childs in subr_childs_dict.items():
            if name in childs:
                subr_parents_dict[name].append(potential_parent)
    return subr_parents_dict



def Fortran_subroutine_parents_childs_dict(childs = None, parents = None):
    '''
    INPUT:
    childs --- dictionary of subroutines and their child subroutines
    parents --- dictionary of subroutines and their parent subroutines
    OUTPUT:
    d --- dictionary of subroutines and their child and parent subroutines
    '''
    d = {name: {'childs': childs[name] if name in childs else [],
                'parents': parents[name] if name in parents else []}\
         for name in (set(childs.keys()) | set(parents.keys()))}
    return d



def read_subroutines_from_file(fpath):
    '''
    Returns a list of strings each of which is the Fortran for a subroutine
    defined in the Fortran file at FPATH
    INPUT:
    fpath --- file path to Fortran file
    OUTPUT:
    subroutines --- list of strings each of which is the Fortran for a subroutine
    defined in the Fortran file at FPATH
    '''
    with open(fpath, mode = 'r', encoding = 'utf-8') as file:
        code = file.read()
    subroutines = get_subroutine_bodies_from_Fortran(code)
    return subroutines


def get_subroutines_from_file(fpath):
    '''
    Returns a list of dictionaries, one for each subroutine in FPATH.
    Each dictionary contains a list of child subroutines.
    INPUT:
    fpath --- file path to Fortran file
    OUTPUT:
    list of dictionaries each of which corresponds to a subroutine, and whose value
    is a list of child subroutines for that subroutine.
    '''
    subroutines = read_subroutines_from_file(fpath)
    return [Fortran_subroutine_to_dict(subr) for subr in subroutines]



def Fortran_subroutine_relations_from_files(paths_fortran = None):
    '''
    INPUT:
    paths_fortran --- list of file paths of fortran files
    OUTPUT:
    d_subr_childs_parents --- dictionary of subroutines in all input fortran files
                              and their child and parent subroutines
    '''
    list_subrs = []
    for fpath in paths_fortran:
        list_subrs.extend(get_subroutines_from_file(fpath))
        
        d_subr_childs = Fortran_subroutine_childs_dict(list_subrs)
        d_subr_parents = Fortran_subroutine_parents_dict(d_subr_childs)
        d_subr_childs_parents = Fortran_subroutine_parents_childs_dict(childs = d_subr_childs,
                                                                       parents = d_subr_parents)
    return d_subr_childs_parents
