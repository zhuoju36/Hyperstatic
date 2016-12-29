# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:30:59 2016

@author: HZJ
"""
import uuid

class material(object):
    def __init__(self,E,mu,gamma,alpha,name=None):
        self.E = E
        self.mu = mu
        self.gamma = gamma
        self.alpha = alpha
        self.shearModulus = E / 2 / (1 + mu)
        self.__name=uuid.uuid1() if name==None else name
        
    @property
    def name(self):
        return self.__name

    @property
    def G(self):
        return self.shearModulus
    
class linear_elastic(material):
    def __init__(self,E,mu,gamma,alpha,name=None):
        super().__init__(E,mu,gamma,alpha,name)