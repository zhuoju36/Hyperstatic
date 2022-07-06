# -*- coding: utf-8 -*-

import os
import numpy as np
from structengpy.core.fe_model.assembly import Assembly
from structengpy.core.fe_post import ResultResolver

class BeamResultResolver(ResultResolver):
    def __init__(self,workpath:str,filename:str):
        super().__init__(workpath,filename)
        self.__workpath=super().workpath
        self.__assembly:Assembly=super().assembly
    
    @property
    def workpath(self):
        return super().workpath

    def resolve_beam_end_force(self,name,casename:str,step:int=1):
        path=self.__path
        d=np.load(os.path.join(path,casename+".d.npy"))[step-1,:] # row-first
        K=self.__assembly.get_beam_K(name)
        hids=self.__assembly.get_beam_node_hids(name)
        dd=[d[i] for i in hids]
        res = K*dd
        return res

    def resolve_beam_displacement(self,name,loc,casename:str,step:int=1):
        path=self.__workpath
        d=np.load(os.path.join(path,casename+".d.npy"))[step-1,:] # row-first
        hids=self.__assembly.get_beam_node_hids(name)
        dd=[d[i] for i in hids]
        N=self.__assembly.interpolate(name,loc)
        axial=dd[~np.in1d(range(12),[0,6])]
        shearbend2=dd[~np.in1d(range(12),[1,7,4,10])]
        shearbend3=dd[~np.in1d(range(12),[2,8,3,6])]
        torsion=dd[~np.in1d(range(12),[3,9])]
        a=N[:1]*axial
        b=N[2:6]*shearbend2
        c=N[6:10]*shearbend3
        d=N[10:]*torsion
        return np.array([
            a[0],b[0],c[0],d[0],b[1],c[1],
            a[1],b[2],c[2],d[1],b[3],c[3]
        ])
if __name__=="__main__":
    import logging
    import sys
    import os

    from structengpy.core.fe_model.assembly import Assembly
    from structengpy.core.fe_model.model import Model
    from structengpy.core.fe_model.load.pattern import LoadPattern
    from structengpy.core.fe_model.load.loadcase import ModalCase, StaticCase
    from structengpy.core.fe_solver.dynamic import ModalSolver
    from structengpy.core.fe_solver.static import StaticSolver
    path="./test"
    if sys.platform=="win32":
        path="c:\\test"

    model=Model()
    model.add_node("1",0,0,0)
    model.add_node("2",6,0,0)
    model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

    patt1=LoadPattern("pat1")
    patt1.set_nodal_load("2",0,0,-1e4,0,0,0)

    lc=StaticCase("case1")
    lc.add_pattern(patt1,1.0)
    lc.set_nodal_restraint("1",True,True,True,True,True,True)
    asb=Assembly(model,[lc])
    asb.save(path,"test.asb")
    solver=StaticSolver(path,"test.asb")
    solver.solve_linear("case1")
    
    resolver=BeamResultResolver(path,"test.asb")
    d=resolver.resolve_beam_displacement("A",0.5,"case1")
    print(d)
    


        

