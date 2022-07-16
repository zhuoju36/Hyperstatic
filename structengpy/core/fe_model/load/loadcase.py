# -*- coding: utf-8 -*-
import numpy as np
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load.pattern import LoadPattern
from structengpy.core.fe_model.load import LoadCase

class StaticCase(LoadCase):
    def __init__(self,name:str,order=1,base_case=None):
        super().__init__(name)
        self.__order=1
        self.__base_case=base_case

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

    def get_settings(self)->dict:
        return {
            'order':self.__order,
            'base_case':self.__base_case
        }

class ModalCase(LoadCase):
    def __init__(self,name:str,n_modes:int=3,base_case=None):
        super().__init__(name)
        self.__mass_source="mass"
        self.__use_load_as_mass=False
        self.__n_modes=n_modes
        self.__base_case=base_case
        self.__algorithm="eigen"

    @property
    def use_load_as_mass(self):
        return self.__use_load_as_mass

    @property
    def n_modes(self):
        return self.__n_modes

    @use_load_as_mass.setter
    def use_load_as_mass(self,val:bool):
        self.__use_load_as_mass=val

    def add_pattern(self,pattern:LoadPattern,factor:float):
        super().add_pattern(pattern,factor)

    def set_pattern_factor(self,name,factor):
        super().set_pattern_factor(name,factor)

    def set_nodal_restraint(self,name:str,u1:bool=False,u2:bool=False,u3:bool=False,r1:bool=False,r2:bool=False,r3:bool=False):
        super().set_nodal_restraint(name,u1,u2,u3,r1,r2,r3)

    def get_nodal_restraint_dict(self):
        return super().get_nodal_restraint_dict()

    def get_settings(self)->dict:
        return {
            'mass_source':self.__mass_source,
            'use_load_as_mass':self.__use_load_as_mass,
            'n_modes':self.__n_modes,
            'base_case':self.__base_case,
            'algorithm':self.__algorithm,
        }

class ResponseSpectrumCase(LoadCase):
    def __init__(self,name:str,modal_case:str,spectrum:np.array,mode_combo='srss',dir_combo='cqc'):
        super().__init__(name)
        self.__modal_case=modal_case
        self.__spectrum=spectrum
        self.__mode_combo=mode_combo
        self.__dir_combo=dir_combo

    def set_nodal_restraint(self,name:str,u1:bool=False,u2:bool=False,u3:bool=False,r1:bool=False,r2:bool=False,r3:bool=False):
        super().set_nodal_restraint(name,u1,u2,u3,r1,r2,r3)

    def get_nodal_restraint_dict(self):
        return super().get_nodal_restraint_dict()

    def get_settings(self):
        return {
            'modal_case':self.__modal_case,
            'spectrum':self.__spectrum,
            'mode_combo':self.__mode_combo,
            'dir_combo':self.__dir_combo
        }

class TimeHistoryCase(LoadCase):
    def __init__(self,name:str,base_case=None):
        super().__init__(name)
        self.__base_case=base_case
        self.__algorithm=None
        self.__param={}

    def use_modal_decomposition(self,modal_case:str,):
        self.__algorithm="modal_decomposition"
        self.__param={
            "modal_case":modal_case,
        }

    def use_direct_time_integration(self,step_size:float):
        self.__algorithm="direct_time_integration"
        self.__param={
            "step_size":step_size,
        }

    def add_pattern(self,pattern:LoadPattern,factor:float,curve:np.array):
        self.__load_factor[pattern.name]=curve
        self.__load_curve[pattern.name]=curve
        super().add_pattern(pattern,factor)

    def set_pattern_factor(self,name,factor):
        super().set_pattern_factor(name,factor)

    def set_nodal_restraint(self,name:str,u1:bool=False,u2:bool=False,u3:bool=False,r1:bool=False,r2:bool=False,r3:bool=False):
        super().set_nodal_restraint(name,u1,u2,u3,r1,r2,r3)

    def get_nodal_restraint_dict(self):
        return super().get_nodal_restraint_dict()

    def get_nodal_f_time_history(self,name:str)->np.array:
        return super().get_nodal_f_time_history(name)

    def get_nodal_f_dict(self):
        return super().get_nodal_f_dict()

    def get_nodal_d_dict(self):
        return super().get_nodal_d_dict()

    def get_beam_f(self,name,l):
        return super().get_beam_f(name,l)

    def get_beam_f_dict(self,ldict):
        return super().get_beam_f_dict(ldict)

    def set_nodal_restraint(self,name:str,u1:bool=False,u2:bool=False,u3:bool=False,r1:bool=False,r2:bool=False,r3:bool=False):
        super().set_nodal_restraint(name,u1,u2,u3,r1,r2,r3)

    def get_nodal_restraint_dict(self):
        return super().get_nodal_restraint_dict()

    def get_settings(self):
        return {
            'curve':self.__curve,
            'base_case':self.__base_case,
            'algorithm':self.__algorithm,
            'param':self.__param
        }

        