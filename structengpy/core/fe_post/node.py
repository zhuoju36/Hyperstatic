# -*- coding: utf-8 -*-

import os
import numpy as np


class NodeResultResolver(object):
    def __init__(self,path:str):
        self.__path=path

    def resolve_nodal_displacement(self,casename:str,step:int=1,hid:int=None):
        """_summary_

        Args:
            casename (str): name of load case
            step (int, optional): _description_. Defaults to 1.
            hid (int, optional): if None all the result will be returned as dictionary. Defaults to None.

        Returns:
            np.array: 
        """
        path=self.__path
        d=np.load(os.path.join(path,casename+".d.npy"))[step-1,:] # row-first
        if hid==None:
            return d.reshape(d.size//6,6)
        else:
            return d[hid*6:hid*6+6]
