# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 19:19:33 2017

@author: Dell
"""
import uuid

from sqlalchemy.sql import and_

from .orm import Config, AreaSection, Point, Area
import logger

class Combination(object):
    def __init__(self,name,lc_factor,method='linear_add'):
        """
        name: name of the combination
        lc_factor: a dictionary about lc:factor
        method: linear_add, enveloped
        """
        self.__name=name
        self.__method=method
        self.__loadcase={}
        
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self,name):
        self.__name=name
        
    @property
    def method(self):
        return self.__method
        
    def add_load(self,load,factor):
        self.__loadcase[load]=factor
