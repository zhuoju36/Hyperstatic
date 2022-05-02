# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 11:50:46 2018

@author: Dell
"""

import numpy as np
from sympy import symbols,Matrix
from fe_model.node import Node
from fe_model.element import Beam,Membrane3,Membrane4
from fe_model import Model as FEModel
from fe_solver.static import solve_linear
from fe_solver.dynamic import solve_modal

"""
Membrane4 tests
"""

def Membrane4_contruction_test():
    n1=Node(0,0,0)
    n2=Node(0,1,0)
    n3=Node(1,1,0)
    n4=Node(1,0,0)
    
    m=Membrane4(n1,n2,n3,n4,0.001,2e11,0.2,7845)
    
    print(m._Ke)