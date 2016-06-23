# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:30:59 2016

@author: HZJ
"""

class Material:
    def __init__(self,E,mu,gamma,alpha):
        self.E = E
        self.mu = mu
        self.gamma = gamma
        self.alpha = alpha
        self.shearModulus = E / 2 / (1 + mu)

    def G(self):
        return self.shearModulus