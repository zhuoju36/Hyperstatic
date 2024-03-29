import numpy as np
from sympy import re     
from hyperstatic.core.fe_model.material.isotropy import IsotropicMaterial

class ShellSection(object):
    def __init__(self,name:str,material:IsotropicMaterial,t:float,ele_type:str="shell"):
        self.__name=name
        self.__material=material
        self.__t=t
        self.__ele_type=ele_type

    @property
    def name(self):
        return self.__name

    @property
    def material(self):
        return self.__material.name

    @property
    def rho(self):
        return self.__material.rho

    @property
    def E(self):
        return self.__material.E

    @property
    def mu(self):
        return self.__material.mu

    @property
    def G(self):
        return self.__material.G

    @property
    def t(self):
        return self.__t

    @property
    def ele_type(self):
        return self.__ele_type
