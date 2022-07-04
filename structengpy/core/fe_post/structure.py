# -*- coding: utf-8 -*-

import os
import numpy as np

from structengpy.core.fe_post import ResultResolver


class StructureResultResolver(ResultResolver):
    def __init__(self,workpath:str,filename:str):
        super().__init__(workpath,filename)
        self.__workpath=super().workpath
        self.__assembly=super().assembly

    def resolve_modal_frequency(self,casename:str)->dict:
        path=self.__workpath
        omega=np.load(os.path.join(path,casename+".o.npy"))
        T=2*np.pi/omega
        f=1/T
        return {
            "omega":omega.reshape(omega.size),
            "f":f.reshape(omega.size),
            "T":T.reshape(omega.size)
            }

    def resolve_structural_reaction(self,casename:str)->float:
        path=self.__workpath
        k=np.load(os.path.join(path,casename+".k.npy"))
        d=np.load(os.path.join(path,casename+".d.npy"))
        f=np.dot(k,d)
        restraints=self.__assembly.restraintDOF(casename)
        res=0
        for i in restraints:
            res+=f[i]
        return res
        

if __name__=="__main__":
    resolver=StructureResultResolver("c:\\test")
    res=resolver.get_modal_frequency("eigen")
    print(res)
