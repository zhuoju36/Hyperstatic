# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 11:01:58 2016

@author: HZJ
"""

import os

import numpy as np
from scipy import linalg
from scipy import sparse as spr
import scipy.sparse.linalg as sl

from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load.loadcase import StaticCase
from structengpy.core.fe_solver import Solver

from structengpy.common import logger

class StaticSolver(Solver):
    def __init__(self,workpath:str,filename:str):
        super().__init__(workpath,filename)

    @property
    def workpath(self):
        return super().workpath

    def solve_linear(self,casename):
        assembly=super().assembly
        logger.info('solving problem with %d DOFs...'%assembly.DOF)
        
        K=assembly.assemble_K()
        f=assembly.assemble_f(casename)
        K_,f_ =assembly.assemble_boundary(casename,K,f)

        delta,info=sl.lgmres(K_,f_.toarray())
        logger.info('Done!')
        d_=delta.reshape((assembly.node_count*6,1))
        path=os.path.join(self.workpath,casename+'.d')
        np.save(path,d_)
   
    def solve_2nd(self):
        pass

    def solve_3rd(self):
        pass

    def solve_push_over(self):
        pass

    def solve_buckling():
        pass
    