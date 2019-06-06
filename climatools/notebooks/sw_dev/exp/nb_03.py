
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/03_analysis.ipynb

from exp.nb_00 import *
from exp.nb_01 import *
from exp.nb_02 import *
import os
import shutil
import pickle
import re
import subprocess
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import numpy as np
from climatools.lblnew.export import vector_to_F77

class LBLnewBestfitSWAnalysis(object):
    def __init__(self, path, runner):
        self.path = Path(path)
        self.runner = runner
        self.path.mkdir(exist_ok=True, parents=True)

    def input_params(self):
        with open('analysis_-_lblnew-bestfit-sw.ipynb') as f:  # Need to set to stored absolute path
            nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
        nb['cells'][2]['source'] = f'''PARAM = LBLnewBestfitSWParam(**{vars(self.runner.param)})'''
        nb['cells'][3]['source'] = f'''PATH = Path("{self.runner.path}")'''
        return nb

    def run(self):
        nb = self.input_params()
        ep = ExecutePreprocessor(timeout=600)
        ep.preprocess(nb, {})
        with open(self.path/'analysis_-_lblnew-bestfit-sw.ipynb', mode='w', encoding='utf-8') as f:
            nbformat.write(nb, f)

    def gitcommit(self):
        cwd = os.getcwd()
        os.chdir(self.path)
        try:
            proc = subprocess.Popen(['git', 'add', 'analysis_-_lblnew-bestfit-sw.ipynb'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            print('Git-add', out.decode(), err.decode())
            title = f"band{self.runner.param.band:02d} {self.runner.param.molecule} {self.runner.param.atmpro} cosz={self.runner.param.cosz} nf_refs={self.runner.param.ng_refs}"
            body = '\n'.join(sorted(f"{n} {v}" for n, v in vars(self.runner.param).items()))
            proc = subprocess.Popen(f'''git commit -m "{title}" -m "{body}"''', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return proc
        finally: os.chdir(cwd)

    def nbviewer_url(self, gitname):
        '''
        gitname: str
            Git repository name.
        '''
        pre_url = Path('https://nbviewer.jupyter.org/github/qap')
        spath = str(self.path)
        if gitname in spath:
            _, suf = spath.split(gitname)
        else:
            suf = spath
        suf = ('blob/master' + suf).strip('/')
        return pre_url/gitname/suf/'analysis_-_lblnew-bestfit-sw.ipynb'