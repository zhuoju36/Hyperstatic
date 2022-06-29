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
        K_,f_ =assembly.assemble_boundary(casename,K,vectorF=f)

        delta,info=sl.lgmres(K_,f_.toarray())
        logger.info('Done!')
        d_=delta.reshape((assembly.node_count*6,1)) #d_ contains all the displacements including the restraint DOFs

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
    
if __name__=='__main__':
    import sys
    from structengpy.core.fe_model.assembly import Assembly
    from structengpy.core.fe_model.model import Model
    from structengpy.core.fe_model.load.pattern import LoadPattern
    from structengpy.core.fe_model.load.loadcase import StaticCase

    path="./test"
    if sys.platform=="win32":
        path="c:\\test"
    model=Model()
    model.add_node("1",0,0,0)
    model.add_node("2",6,0,0)
    model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

    patt1=LoadPattern("pat1")
    patt1.set_beam_load_conc("A",M2=1e4,r=0.75)
    lc=StaticCase("case1")
    lc.add_pattern(patt1,1.0)
    lc.set_nodal_restraint("1",True,True,True,True,True,True,)
    
    asb=Assembly(model,lc)
    asb.save(path,"test.sep")

    solver=StaticSolver(path,"test.sep")
    solver.solve_linear("case1")
    d=np.load(os.path.join(path,"case1.d.npy")).reshape(18)
    print(d)