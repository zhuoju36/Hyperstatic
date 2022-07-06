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

    def resolve_beam_displacement(self,name,casename:str,step:int=1,loc=0.5):
        path=self.__path
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


        

