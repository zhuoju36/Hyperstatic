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

    def set_nodal_restraint(self,name:str,u1:bool,u2:bool,u3:bool,r1:bool,r2:bool,r3:bool):
        super().set_nodal_restraint(name,u1,u2,u3,r1,r2,r3)

    def get_nodal_restraint_dict(self):
        return super().get_nodal_restraint_dict()

    def get_nodal_f(self,name):
        return super().get_nodal_f(name)

    def get_nodal_load_dict(self):
        return super().get_nodal_load_dict()

    def get_nodal_disp_dict(self):
        return super().get_nodal_disp_dict()

    def get_beam_load(self,name):
        return super().get_beam_load(name)

    def get_beam_load_dict(self):
        return super().get_beam_load_dict()

class ModalCase(LoadCase):
    pass

class SpectrumCase(LoadCase):
    pass

class TimeHistoryCase(LoadCase):
    pass

        