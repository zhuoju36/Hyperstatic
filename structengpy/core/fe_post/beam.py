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

    def resolve_beam_end_force(self,casename:str,step:int=1,name=None):
        path=self.__path
        d=np.load(os.path.join(path,casename+".d.npy"))[step-1,:] # row-first
        K=self.__assembly.get_beam_K(name)
        hids=self.__assembly.get_beam_node_hids(name)
        dd=[d[i] for i in hids]
        res = K*dd
        return res

    
