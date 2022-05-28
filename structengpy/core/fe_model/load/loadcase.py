# -*- coding: utf-8 -*-
import numpy as np
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load.pattern import LoadPattern
from structengpy.core.fe_model.load import LoadCase

class StaticCase(LoadCase):
    def __init__(self,name:str,order=1):
        super().__init__(name)
        self.__order=1

    @property
    def order(self):
        return self.__order

    @order.setter
    def order(self,val):
        assert val in [1,2,3]
        self.__order=val

    def add_pattern(self,pattern:LoadPattern,factor:float):
        super().add_pattern(pattern,factor)

    def set_pattern_factor(self,name,factor):
        super().set_pattern_factor(name,factor)

    def set_nodal_restraint(self,name:str,u1:bool=False,u2:bool=False,u3:bool=False,r1:bool=False,r2:bool=False,r3:bool=False):
        super().set_nodal_restraint(name,u1,u2,u3,r1,r2,r3)

    def get_nodal_restraint_dict(self):
        return super().get_nodal_restraint_dict()

    def get_nodal_f(self,name):
        return super().get_nodal_f(name)

    def get_nodal_f_dict(self):
        return super().get_nodal_f_dict()

    def get_nodal_d_dict(self):
        return super().get_nodal_d_dict()

    def get_beam_f(self,name,l):
        return super().get_beam_f(name,l)

    def get_beam_f_dict(self,ldict):
        return super().get_beam_f_dict(ldict)

class ModalCase(LoadCase):
    pass

class SpectrumCase(LoadCase):
    pass

class TimeHistoryCase(LoadCase):
    pass

        