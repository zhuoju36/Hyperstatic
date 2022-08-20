# -*- coding: utf-8 -*-

import os
from token import DEDENT
import numpy as np
from hyperstatic.core.fe_model.assembly import Assembly
from hyperstatic.core.fe_post import ResultResolver

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

    def resolve_beam_deformation(self,name:str,loc:float,casename:str,step:int=1)->np.array:
        """Resolve beam deformation

        Args:
            name (str): name of beam
            loc (float): relative location, between [0,1]
            casename (str): name of loadcase
            step (int, optional): step. Defaults to 1.

        Returns:
            np.array: [x,w2,w3,theta]
        """
        path=self.__workpath
        d=np.load(os.path.join(path,casename+".d.npy"))[step-1,:] # row-first
        hids=self.__assembly.get_beam_node_hids(name)
        mask=[]
        for i in hids:
            mask.extend(list(range(i*6,i*6+6)))
        N=self.__assembly.get_beam_interpolate(name,loc)
        N_=self.__assembly.get_beam_interpolate1(name,loc)
        dd=d[np.in1d(range(len(d)),mask)]
        T=self.__assembly.get_beam_transform_matrix(name)
        dd=T.dot(dd)
        axial=dd[np.in1d(range(12),[0,6])]
        shear2bend3=dd[np.in1d(range(12),[1,5,7,11])]
        shear3bend2=dd[np.in1d(range(12),[2,4,8,10])]
        bend3=dd[np.in1d(range(12),[5,11])]
        bend2=dd[np.in1d(range(12),[4,10])]
        torsion=dd[np.in1d(range(12),[3,9])]
        x=np.dot(N[:2],axial)
        w2=np.dot(N[2:6],shear2bend3)
        w3=np.dot(N[6:10],shear3bend2)
        theta=np.dot(N[10:],torsion)
        phi2=np.dot(N_[2:6],shear2bend3)
        phi3=np.dot(N_[6:10],shear3bend2)
        print(N_[2:6])   
        print(shear2bend3[2:])     
        return np.array([x,w2,w3,theta,phi2,phi3])
         
if __name__=="__main__":
    import logging
    import sys
    import os

    from hyperstatic.core.fe_model.assembly import Assembly
    from hyperstatic.core.fe_model.model import Model
    from hyperstatic.core.fe_model.load.pattern import LoadPattern
    from hyperstatic.core.fe_model.load.loadcase import ModalCase, StaticCase
    from hyperstatic.core.fe_solver.dynamic import ModalSolver
    from hyperstatic.core.fe_solver.static import StaticSolver
    path="./test"
    if sys.platform=="win32":
        path="c:\\test"

    model=Model()
    model.add_node("1",0,0,0)
    model.add_node("2",6,0,0)
    model.add_simple_beam("A","1","2",E=1.999e11,mu=0.3,A=4.265e-3,I3=6.572e-5,I2=3.301e-6,J=9.651e-8,rho=7849.0474)

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
    d=resolver.resolve_beam_deformation("A",0.75,"case1")
    print(d)
    


        

