# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 19:09:47 2017

@author: Dell
"""

class loadcase(object):
    def __init__(self,name,load_type='static',option='linar',plc=None):
        """
        load_type: static, modal, buckling, time-history
        option: linear, p-delta, large-deform
        """
        self.__name=name
        
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self,name):
        self.__name=name

