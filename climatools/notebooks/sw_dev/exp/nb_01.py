
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/01_lblnew-bestfit-sw_setup.ipynb

from pathlib import *

SRC = Path('/chia_cluster/home/jackyu/radiation/crdnew-sw/')

FNAMES = ['lblnew-bestfit-sw.f', 'lblcom.f']

COMPILE_COMMAND = ("ifort -CB -g -traceback -fpe0 -warn unused -r8 "
                   "lblcom.f lblnew-bestfit-sw.f -o lblnew-bestfit-sw.exe")