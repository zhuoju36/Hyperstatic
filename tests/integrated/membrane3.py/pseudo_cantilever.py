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
    
def pseudo_cantilever_test(l=25,h=5):
    """
    This is a cantilever beam with 50x10
    l,h: division on l and h direction
    """
    model=FEModel()
    nodes=[]
    for i in range(h+1):
        for j in range(l+1):
            nodes.append(Node(j*50/l,0,i*10/h))
            model.add_node(nodes[-1])
            
    for i in range(h):
        for j in range(l):
            area1=Membrane3(nodes[i*(l+1)+j],
                           nodes[i*(l+1)+j+1],
                           nodes[(i+1)*(l+1)+j+1],
                           0.25,2e11,0.3,7849)
            area2=Membrane3(nodes[i*(l+1)+j],
                           nodes[(i+1)*(l+1)+j+1],
                           nodes[(i+1)*(l+1)+j],
                           0.25,2e11,0.3,7849)
            if j==0:
                nodes[i*(l+1)+j].dn=[0]*6
                nodes[(i+1)*(l+1)+j].dn=[0]*6

            model.add_membrane3(area1)
            model.add_membrane3(area2)

    nodes[(l+1)*(h+1)-1].fn=(0,0,-100000,0,0,0)
    
    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    res=solve_linear(model)

    np.set_printoptions(precision=6,suppress=True)
    print(res[(l+1)*(h+1)*6-6:])
    print(r"correct answer should be ???")