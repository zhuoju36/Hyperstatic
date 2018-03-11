# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 19:09:47 2017

@author: Dell
"""

from . import LoadCase
        
class StaticLinear(LoadCase):
    def __init__(self,name):
        super(StaticLinear,self).__init__(name)

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
