# -*- coding: utf-8 -*-

__all__=['static','dynamic']

import pickle

class Solver(object):
    def __init__(self,workpath:str):
        self.__workpath=workpath
        with open(workpath) as f:
            self.__model=pickle.load()

    @property
    def model(self):
        return self.__model

    @property
    def workpath(self):
        return self.__workpath



