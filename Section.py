# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:32:16 2016

@author: HZJ
"""

class Section:
    def __init__(self,mat, A, J, I33, I22):
        self.material = mat
        self.A = A
        self.J = J
        self.I33 = I33
        self.I22 = I22