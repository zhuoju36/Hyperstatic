# -*- coding: utf-8 -*-

import os
import numpy as np


class StructureResultResolver(object):
    def __init__(self,path:str):
        self.__path=path

    def resolve_modal_frequency(self,casename):
        path=self.__path
        omega=np.load(os.path.join(path,casename+".o.npy"))
        T=2*np.pi/omega
        f=1/T
        return {
            "omega":omega.reshape(omega.size),
            "f":f.reshape(omega.size),
            "T":T.reshape(omega.size)
            }

    # def resolve_structural_reaction(self,casename):
    #     path=self.__path
    #     pass

if __name__=="__main__":
    resolver=StructureResultResolver("c:\\test")
    res=resolver.get_modal_frequency("eigen")
    print(res)
