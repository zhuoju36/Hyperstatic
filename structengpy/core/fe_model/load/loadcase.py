# -*- coding: utf-8 -*-
import numpy as np
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load.pattern import Pattern
from structengpy.core.fe_model.load import LoadCase

class StaticCase(LoadCase):
    def __init__(self,name:str,order=1):
        super().__init__(name)
        self.__order=1
        self.__preloadcase=None
        self.__pattern={} #to save pattern objects
        self.__loadfactor={} #to assign load factor

    @property
    def order(self):
        return self.__order

    @order.setter
    def order(self,val):
        assert val in [1,2,3]
        self.__order=val

    def add_pattern(self,pattern:Pattern,factor:float):
        self.__pattern[pattern.name]=pattern
        self.__loadfactor[pattern.name]=factor

    def set_pattern_factor(self,name,factor):
        self.__loadfactor[name]=factor

    def get_nodal_load_vector(self,name):
        fn=np.zeros(6)
        for patname,factor in self.__loadfactor.items():
            pat=self.__pattern[patname]
            f=pat.get_nodal_load(name)
            if f is None:
                continue
            fn+=f*factor   
        return fn

    def get_beam_load_vector(self,name):
        fe=np.zeros(12)
        for patname,factor in self.__loadfactor.items():
            pat=self.__pattern[patname]
            f=pat.get_beam_distributed(name)
            if f is None:
                continue
            fn+=f*factor
            ###TODO transfer to end force
        return fe

class ModalCase(LoadCase):
    pass

class SpectrumCase(LoadCase):
    pass

class TimeHistoryCase(LoadCase):
    pass

        