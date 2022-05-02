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


def planar_frame_test():
    #FEModel Test
    model=FEModel()
    n1=Node(0,0,0)
    n2=Node(0,0,5)
    n3=Node(5,0,5)
    n4=Node(10,0,5)
    n5=Node(10,0,0)
    b1=Beam(n1,n2,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
    b2=Beam(n2,n3,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
    b3=Beam(n3,n4,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
    b4=Beam(n4,n5,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
    
    model.add_node(n1)
    model.add_node(n2)
    model.add_node(n3)
    model.add_node(n4)
    model.add_node(n5)

    model.add_beam(b1)
    model.add_beam(b2)
    model.add_beam(b3)
    model.add_beam(b4)

    n2.fn=(100000,0,0,0,0,0)
    n3.fn=(0,0,-100000,0,0,0)
    n1.dn=[0,0,0,0,0,0]
    n5.dn=[0,0,0,0,0,0]

    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    res=solve_linear(model)
    
    print(res)