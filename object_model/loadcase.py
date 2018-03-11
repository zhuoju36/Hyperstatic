# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 19:09:47 2017

@author: Dell
"""

class LoadCase(object):
    def __init__(self,name):
        """
        name: name of load case
        """
        self._name=name
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self,name):
        assert type(name)==str and len(name)<20
        self._name=name
        
class StaticLinear(LoadCase):
    def __init__(self,name):
        pass

class Statc2nd(LoadCase):
    def __init__(self,name,plc):
        pass

class Static3nd(LoadCase):
    def __init__(self,name,plc):
        pass

class Modal(LoadCase):
    def __init__(self,name,method='eigen'):
        pass

class Spectrum(LoadCase):
    def __init__(self,name,curve):
        pass

class TimeHistory(LoadCase):
    def __init__(self,name,curve):
        pass

class Buckling(LoadCase):
    def __init__(self,name,k):
        pass
