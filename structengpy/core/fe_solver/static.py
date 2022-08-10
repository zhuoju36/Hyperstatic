# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 11:01:58 2016

@author: HZJ
"""

import os
import time

import numpy as np
from scipy import linalg
from scipy import sparse as spr
import scipy.sparse.linalg as sl

from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load.loadcase import StaticCase
from structengpy.core.fe_solver import Solver
# import pypardiso

import logging

logging.basicConfig(format="%(asctime)s|%(levelname)s|:%(message)s",level=logging.INFO)

class StaticSolver(Solver):
    def __init__(self,workpath:str,filename:str):
        super().__init__(workpath,filename)

    @property
    def workpath(self):
        return super().workpath

    def solve_linear(self,casename,precase=None)->bool:
        assembly=super().assembly
        logging.info('Solving STATIC case with %d DOFs...'%assembly.DOF)
        
        if precase==None:
            base_case="0"
            path=os.path.join(self.workpath,base_case+'.k') #path of the stiff matrix
            if os.path.exists(path):
                K=np.load(path)
            else:
                K=assembly.assemble_K()
                np.save(path,K)
            
        f=assembly.assemble_f(casename)
        K_ =assembly.assemble_boundary(casename,K)
        f_ =assembly.assemble_boundary(casename,f)

        def icholesky(a):
            n = a.shape[0]
            for k in range(n): 
                a[k,k] = np.sqrt(a[k,k])
                for i in range(k+1,n):
                   if (a[i,k] !=0):
                       a[i,k] = a[i,k]/a[k,k]
                for j in range(k+1,n):  
                    for i in range(j,n):
                       if (a[i,j]!=0):
                           a[i,j] = a[i,j]-a[i,k]*a[j,k]    
            return spr.csr_matrix(a)
        

        # M=spr.diags([1/K_[i,i] for i in range(K_.shape[0])])

        logging.info('Start solving linear equations!')
        begin=time.time()

        delta,info=sl.cg(K_,f_,atol='legacy') #using cg algorithm, can also be cgs, bicg, bicgstab, gmres, lgmres, etc.
        # delta=sl.spsolve(K_,f_,use_umfpack=True) #using cg algorithm, can also be cgs, bicg, bicgstab, gmres, lgmres, etc.
        # delta= pypardiso.spsolve(K_,f_)

        logging.info('Done!'+"time="+str(time.time()-begin))
        restraintDOF=assembly.restraintDOF(casename) #case restraint first, then model
        if len(restraintDOF)==0:
            restraintDOF=assembly.restraintDOF()

        restraintDOF.sort()
        delta=list(delta)
        d=[]
        for i in range(assembly.node_count*6):
            if restraintDOF!=[] and i==restraintDOF[0]:
                restraintDOF.pop(0)
                d.append(0)
            else:
                d.append(delta.pop(0))

        d_=np.array(d).reshape((1,assembly.node_count*6)) #row-first, d_ contains all the displacements including the restraint DOFs

        path=os.path.join(self.workpath,casename+'.d')
        np.save(path,d_)
        return True
   
    def solve_2nd_order(self,casename,precase=None)->bool:
        assembly=super().assembly
        logging.info('Solving STATIC case with %d DOFs...'%assembly.DOF)
        
        if precase==None:
            base_case="0"
            path=os.path.join(self.workpath,base_case+'.k') #path of the stiff matrix
            if os.path.exists(path):
                K=np.load(path)
            else:
                K=assembly.assemble_K()
                np.save(path,K)
            
        f=assembly.assemble_f(casename)
        K_ =assembly.assemble_boundary(casename,K)
        f_ =assembly.assemble_boundary(casename,f)

        logging.info('Start solving 2nd order equations considered P-Δ effects')
        begin=time.time()

        delta,info=sl.cg(K_,f_,atol='legacy')

        logging.info('Done!'+"time="+str(time.time()-begin))
        restraintDOF=assembly.restraintDOF(casename) #case restraint first, then model
        if len(restraintDOF)==0:
            restraintDOF=assembly.restraintDOF()
        for i in restraintDOF: 
            delta=np.insert(delta,i,0,0)

        d_=delta.reshape((1,assembly.node_count*6)) #row-first, d_ contains all the displacements including the restraint DOFs

        path=os.path.join(self.workpath,casename+'.d')
        np.save(path,d_)
        return True

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
    N=10000
    for i in range(N+1):
        model.add_node(str(i),6/N*i,0,0)
    for i in range(N):
        model.add_simple_beam(str(i),str(i),str(i+1),E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

    patt1=LoadPattern("pat1")
    # patt1.set_beam_load_conc("A",M2=1e4,r=0.75)
    patt1.set_nodal_load(str(N),f3=-1e5)
    lc=StaticCase("case1")
    lc.add_pattern(patt1,1.0)
    lc.set_nodal_restraint("0",True,True,True,True,True,True,)
    
    asb=Assembly(model,[lc])
    asb.save(path,"test.asb")

    solver=StaticSolver(path,"test.asb")
    solver.solve_linear("case1")
    d=np.load(os.path.join(path,"case1.d.npy")).T
    print(d[-6:])