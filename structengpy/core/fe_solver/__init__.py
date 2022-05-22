# -*- coding: utf-8 -*-

__all__=['static','dynamic']

import os
import pickle

class Solver(object):
    def __init__(self,workpath:str,filename:str):
        self.__workpath=workpath
        filename=os.path.join(workpath,filename)
        with open(filename,"rb") as f:
            self.__assembly=pickle.load(f)

    @property
    def assembly(self):
        return self.__assembly

    @property
    def workpath(self):
        return self.__workpath



