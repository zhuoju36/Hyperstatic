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

import logging

logging.basicConfig(format="%(asctime)s|%(levelname)s|:%(message)s",level=logging.INFO)

class StaticSolver(Solver):
    def __init__(self,workpath:str,filename:str):
        super().__init__(workpath,filename)

    @property
    def workpath(self):
        return super().workpath

    def solve_linear(self,casename,precase=None,use_solver='pcg')->bool:
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

        N=K_.shape[0]
        

        def ilu_precon(A):
            ## incomplete LU decomposition
            lu=sl.spilu(A.tocsc(),drop_tol=1e-12,fill_factor=10)
            Pr = spr.csc_matrix((np.ones(N), (lu.perm_r, np.arange(N))))
            Pc = spr.csc_matrix((np.ones(N), (np.arange(N), lu.perm_c)))
            return Pr.T @ (lu.L @ lu.U) @ Pc.T

        def jacobi_precon(A):
            D=spr.diags(A.diagonal()).tocsr()
            return D

        def nearest_SPD(A):
            N=A.shape[0]
            u,s,vt=sl.svds(A,k=min(32,N-1),which='LM')
            vt[vt<1e-6]=0
            Vt=spr.csc_matrix(vt)
            S=spr.diags(s).tocsc()
            H=Vt.T @ S @ Vt
            XF=(B+H)/2
            return XF

        def cholesky_precon(A:spr.spmatrix):
            try:
                from sksparse import cholmod
                N=A.shape[0]
                B=(A+A.T)/2            
                factor=cholmod.cholesky_AAt(B.tocsc(),beta=0,mode="supernodal",ordering_method='best') #make the preconditioner alway positive determined
                P = spr.csc_matrix((np.ones(N), (np.arange(N), factor.P())))
                L=factor.L()
                ddd=factor(B*f_)
                print(ddd[-6:])
                return P.T*L*L.T*P
            except:
                raise Exception("Must have scikit-sparse and CHOLMOD installed first!")

        logging.info('Start solving linear equations!')
        begin=time.time()
        A=(K_+K_.T)/2
        A=A.tocsc()
        if use_solver=='direct':
            delta=sl.spsolve(A,f_)
        elif use_solver=='pardiso':
            try:
                import pypardiso
                delta= pypardiso.spsolve(K_,f_)
            except:
                raise Exception("Must have pyprdiso installed first!")
        elif use_solver=='cholmod':
            from sksparse import cholmod
            beta=-np.max(np.abs(A.data))*1e-20
            factor=cholmod.cholesky(A,beta,mode="auto",ordering_method='best')
            delta=factor.solve_A(f_).reshape(N,)
        elif use_solver=='pcg':
            logging.info('Preconditioning...')
            P=cholesky_precon(K_)
            M_x = lambda x: sl.spsolve(P, x)
            M = sl.LinearOperator((N,N), M_x)
            delta,info=sl.bicgstab(K_,f_,tol=1e-5,M=M,maxiter=30) #algorithm, can be cg, cgs, bicg, bicgstab, gmres, lgmres, etc.
            if info==0:
                logging.info('Interation solver converged! Sucessfully solved the problem.')
            else:
                logging.warning('NOT converged!')
        else:
            raise Exception("NO such solver as "+str(use_solver))

        logging.info('Done!'+" time cost: "+str(time.time()-begin))
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
    N=200000
    l=6
    for i in range(N+1):
        model.add_node(str(i),l/N*i,0,0)
    for i in range(N):
        model.add_simple_beam("B"+str(i),str(i),str(i+1),E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

    patt1=LoadPattern("pat1")
    # patt1.set_beam_load_conc("A",M2=1e4,r=0.75)
    patt1.set_nodal_load(str(N),f3=1)
    lc=StaticCase("case1")
    lc.add_pattern(patt1,1.0)
    lc.set_nodal_restraint("0",False,False,True,True,True,False)
    
    asb=Assembly(model,[lc])
    asb.save(path,"test.asb")

    solver=StaticSolver(path,"test.asb")
    solver.solve_linear("case1",use_solver='direct')
    d=np.load(os.path.join(path,"case1.d.npy")).T
    print(d[-6:])