# -*- coding: utf-8 -*-

__all__=['static','dynamic']

import pickle

class Solver(object):
    def __init__(self,workpath:str):
        self.__workpath=workpath
        with open(workpath) as f:
            self.__assembly=pickle.load(f)

    @property
    def assembly(self):
        return self.__assembly

    @property
    def workpath(self):
        return self.__workpath



