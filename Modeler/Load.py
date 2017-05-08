# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 13:21:57 2017

@author: zhuoj
"""

class load(object):
    def __init__(self,lc,targets):
        self.__lc=lc
        self.__targets=targets
        
    @property
    def lc(self):
        return self.__lc
    
    @lc.setter
    def lc(self,lc):
        self.__lc=lc
        
    @property
    def targets(self):
        return self.__targets

class point_load(load):
    def __init__(self,lc,targets,values):
        self.__values=values
        super().__init__(lc,targets)

class beam_concentrate(load):
    def __init__(self,lc,targets,values,loc):
        self.__values=values
        self.__loc=loc
        super().__init__(lc,targets)

class beam_distributed(load):
    def __init__(self,lc,targets,values_i,values_j):
        self.__values_i=values_i
        self.__values_j=values_j
        super().__init__(lc,targets)
        
    @property
    def values_i(self):
        return self.__values_i
    @property
    def values_j(self):
        return self.__values_j

class beam_strain(load):
    def __init__(self,lc,targets,values):
        self.__values=values
        super().__init__(lc,targets)

class beam_temperatrue(load):
    def __init__(self,lc,targets,values):
        self.__values=values
        super().__init__(lc,targets)

class quad_distributed(load):
    def __init__(self,lc,targets,values_1,values_2,values_3,values4):
        pass
        super().__init__(lc,targets)
        
class quad_to_beam(load):
    def __init__(self,lc,targets,values_1,values_2,values_3,values4):
        pass
        super().__init__(lc,targets)

