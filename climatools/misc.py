import re
import os
import fnmatch
import filecmp
import subprocess





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



def read_subroutines_from_file(fpath, check_encoding=False):
    '''
    Returns a list of strings each of which is the Fortran for a subroutine
    defined in the Fortran file at FPATH
    INPUT:
    fpath --- file path to Fortran file
    OUTPUT:
    subroutines --- list of strings each of which is the Fortran for a subroutine
    defined in the Fortran file at FPATH
    '''
    if check_encoding:
        proc = subprocess.Popen(['chardetect', fpath],
                                stdout=subprocess.PIPE)
        out = proc.communicate()[0]
        encoding = out.decode('utf-8').split()[1]
    else:
        encoding = 'utf-8'
        
    with open(fpath, mode = 'r', encoding=encoding) as file:
        code = file.read()
    subroutines = get_subroutine_bodies_from_Fortran(code)
    return subroutines


def get_subroutines_from_file(fpath, check_encoding=False):
    '''
    Returns a list of dictionaries, one for each subroutine in FPATH.
    Each dictionary contains a list of child subroutines.
    INPUT:
    fpath --- file path to Fortran file
    OUTPUT:
    list of dictionaries each of which corresponds to a subroutine, and whose value
    is a list of child subroutines for that subroutine.
    '''
    subroutines = read_subroutines_from_file(fpath,
                                             check_encoding=check_encoding)
    return [Fortran_subroutine_to_dict(subr) for subr in subroutines]



def Fortran_subroutine_relations_from_files(paths_fortran=None,
                                            check_encoding=False):
    '''
    INPUT:
    paths_fortran --- list of file paths of fortran files
    OUTPUT:
    d_subr_childs_parents --- dictionary of subroutines in all input fortran files
                              and their child and parent subroutines
    '''
    list_subrs = []
    for fpath in paths_fortran:
        list_subrs.extend(get_subroutines_from_file(fpath,
                                                    check_encoding=check_encoding))
        
        d_subr_childs = Fortran_subroutine_childs_dict(list_subrs)
        d_subr_parents = Fortran_subroutine_parents_dict(d_subr_childs)
        d_subr_childs_parents = Fortran_subroutine_parents_childs_dict(childs = d_subr_childs,
                                                                       parents = d_subr_parents)
    return d_subr_childs_parents



def findalldir(topdir, pattern):
    '''
    find all directories under TOPDIR, whose name matches PATTERN
    '''
    for path, dirnames, filenames in os.walk(topdir):
        for dirname in dirnames:
            if fnmatch.fnmatch(dirname, pattern):
                yield os.path.join(path, dirname)
                


def print_leftright_only(dcmp, leftright = 'left'):
    '''
    Takes a Cmpfile.dircmp object and return all files or directories
    that are under the left (or right) and are not under the right (or left)
    directory in the comparison.
    INPUT:
    dcmp --- Cmpfile.dircmp object that compares two directories
    leftright --- \'left\' (\'right\') to return files and directories
                  that are only found under the left (right) directory of dcmp.
    '''
    if leftright == 'left':
        leftrightonlys = dcmp.left_only
    elif leftright == 'right':
        leftrightonlys = dcmp.right_only
    else:
        raise ValueError('leftright must be either left or right')


    for name in leftrightonlys:
        if leftright == 'left':
            print()
            print('{} found in {} but not in {}'.format(name, dcmp.left, dcmp.right))
        else:
            print()
            print('{} found in {} but not in {}'.format(name, dcmp.right, dcmp.left))


    for sub_dcmp in dcmp.subdirs.values():
        print_leftright_only(sub_dcmp, leftright = leftright)



def print_diff_files(dcmp):
    '''
    Prints out all common files that are different between
    the 2 compared directories of DCMP (filecmp.dircmp)
    INPUT:
    dcmp --- filecmp.dircmp object (that compares two directories)
    '''
    for name in dcmp.diff_files:
        print()
        print('diff_file {} found in {} and {}'.format(name, dcmp.left, dcmp.right))
        
    for sub_dcmp in dcmp.subdirs.values():
        print_diff_files(sub_dcmp)



def list_signposts(readfrom='out.log', label='signpost'):
    '''
    Read and return from a text file at READFROM
    all lines that start with LABEL

    Parameters
    ----------
    readfrom: path to text file to read from
    label: lines starting with this string will be returned
    lines: list of str
    '''
    with open(readfrom, mode='r', encoding='utf-8') as f:
        lines = f.readlines()
        
    lines = [l.strip() for l in lines]
    lines = [l for l in lines if l.startswith(label)]
    return lines



def enumerate_unique_signposts(signposts):
    '''
    Return the ordered and enumerated list of
    unique signposts from SIGNPOSTS

    Parameters
    ----------
    signposts: list of signposts (list of str)
    signposts_enumerated: unique signposts enumerated
                          in the order they appear in
                          SIGNPOSTS
    '''
    set_signs = set(signposts)
    set_ordered = []
    for s in signposts:
        if s in set_signs:
            set_ordered.append(s)
            set_signs.remove(s)
        if not set_signs:
            break
    signposts_enumerated = [(i + 1, s)
                            for i, s in enumerate(set_ordered)]
    return signposts_enumerated
    
    
    
