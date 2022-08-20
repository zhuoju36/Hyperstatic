# -*- coding: utf-8 -*-

import os
import numpy as np
import pickle
from hyperstatic.core.fe_model.assembly import Assembly

class ResultResolver(object):
    def __init__(self,workpath:str,filename:str):
        self.__workpath=workpath
        filename=os.path.join(workpath,filename)
        with open(filename,"rb") as f:
            self.__assembly:Assembly=pickle.load(f)

    @property
    def workpath(self):
        return self.__workpath

    @property
    def assembly(self):
        return self.__assembly