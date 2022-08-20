# -*- coding: utf-8 -*-

import os
import numpy as np
from hyperstatic.core.fe_post import ResultResolver

class NodeResultResolver(ResultResolver):
    def __init__(self,workpath:str,filename:str):
        super().__init__(workpath,filename)
        self.__workpath=super().workpath
        self.__assembly=super().assembly

    def resolve_nodal_displacement(self,name:str,casename:str,step:int=1):
        """_summary_

        Args:
            name (str): name of the node.
            casename (str): name of load case
            step (int, optional): load step. Defaults to 1.

        Returns:
            np.array: 
        """
        path=self.__workpath
        d=np.load(os.path.join(path,casename+".d.npy"))[step-1,:] # row-first
        hid=self.__assembly.get_node_hid(name)
        return d[hid*6:hid*6+6]

    def resolve_nodal_reaction(self,name:str,casename:str,step:int=1):
        """_summary_

        Args:
            name (str): name of the node.
            casename (str): name of load case
            step (int, optional): _description_. Defaults to 1.

        Returns:
            np.array: 
        """
        path=self.__workpath
        d=np.load(os.path.join(path,casename+".d.npy"))[step-1,:] # row-first
        k=np.load(os.path.join(path,casename+".k.npy"))
        f=np.dot(k,d)
        hid=self.__assembly.get_node_hid(name)
        return f[hid*6:hid*6+6]
