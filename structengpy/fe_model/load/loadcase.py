import numpy as np
from structengpy.fe_model.model import Model
from structengpy.fe_model.load.pattern import Pattern

class LoadCase(object):
    def __init__(self,name:str):
        self.__name=name
        self.__hid

    @property
    def name(self):
        return self.__name

    @property
    def hid(self):
        return self.__hid

    @hid.setter
    def hid(self,val):
        assert type(val)==int
        self.__hid=val

class StaticCase(LoadCase):
    def __init__(self,name:str,order=1):
        super().__init__(name)
        self.__order=1
        self.__pattern={}
        self.__loadfactor={}

    @property
    def order(self):
        return self.__hid

    @order.setter
    def order(self,val):
        assert val in [1,2,3]
        self.__order=val   

    def add_pattern(self,pattern:Pattern,factor:float):
        self.__pattern_factor[pattern.name]=factor

    def get_nodal_load_vector(self,name):
        fn=np.zeros(6)
        for patname,factor in self.__loadfactor.items:
            pat=self.__pattern[patname]
            fn+=pat.get_nodal_load(name)*factor   
        return fn

    def get_beam_load_vector(self,name):
        fe=np.zeros(12)
        for patname,factor in self.__loadfactor.items:
            pat=self.__pattern[patname]
            fe+=pat.get_beam_distributed(name)*factor
            ###TODO transfer to end force
            re=fe
        return re

class ModalCase(LoadCase):
    pass

class SpectrumCase(LoadCase):
    pass

class TimeHistoryCase(LoadCase):
    pass

        