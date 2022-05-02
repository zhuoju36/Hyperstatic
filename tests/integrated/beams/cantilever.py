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
Beam tests
"""

def cantilever_beam_test():
    #FEModel Test
    model=FEModel()
    model.add_node(0,0,0)
    model.add_node(2,1,1)
    E=1.999e11
    mu=0.3
    A=4.265e-3
    J=9.651e-8
    I3=6.572e-5
    I2=3.301e-6
    rho=7849.0474
    
    model.add_beam(0,1,E,mu,A,I2,I3,J,rho)
    model.set_node_force(1,(0,0,-1e6,0,0,0))
    model.set_node_restraint(0,[True]*6)
    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    solve_linear(model)
    print(np.round(model.d_,6))
    print("The result of node 1 should be about [0.12879,0.06440,-0.32485,-0.09320,0.18639,0]")