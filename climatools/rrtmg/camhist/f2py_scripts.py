'''
Here f2py3 compiles Fortran files into Python modules
'''
import os


COMMAND_COMPILE = 'f2py3 -c {file_fortran} -m {module_python}'

LIST_MODULES = [dict(file_fortran='modal_aero_wateruptake.F90',
                     module_python='aerowateruptake'),
                dict(file_fortran='modal_aero_sw.f90',
                     module_python='modal_aero_sw')]


def build_python_modules():
    for module in LIST_MODULES:
        command = COMMAND_COMPILE\
                  .format(file_fortran=module['file_fortran'],
                          module_python=module['module_python'])
        assert os.system(command) == 0



if __name__ == '__main__':
    build_python_modules()

