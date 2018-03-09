# -*- coding: utf-8 -*-
import numpy as np
import scipy.sparse as spr
from Modeler.Node import Node
from Modeler.Element import Beam,Membrane3,Membrane4
from Modeler.Material import IsotropyElastic
from Modeler.Section import AreaSection
from Modeler.FEModel import FEModel,solve_linear
   
def shear_test():
    model=FEModel()
    n1=Node(0,0,0)
    n2=Node(0,0,5)
    n3=Node(5,0,5)
    n4=Node(10,0,5)
    n5=Node(10,0,0)
    
    a1=Membrane4(n1,n2,n3,n5,0.25,2e11,0.3,7849)
    a2=Membrane3(n3,n4,n5,0.25,2e11,0.3,7849)
    
    model.add_node(n1)
    model.add_node(n2)
    model.add_node(n3)
    model.add_node(n4)
    model.add_node(n5)

    model.add_tri_membrane(a1)
    model.add_tri_membrane(a2)
    model.add_tri_membrane(a3)

    n3.fn=(0,0,-100000,0,0,0)
    n1.dn=[0,0,0,0,0,0]
    n2.dn=[0,0,0,0,0,0]
    n3.dn=[0,0,None,0,0,0]
    n4.dn=[0,0,0,0,0,0]
    n5.dn=[0,0,0,0,0,0]

    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    res=solve_linear(model)
        
    print(res)

np.set_printoptions(precision=6,suppress=True)
shear_test()
#    from random import random
#    model=FEModel()
#    for i in range(333):
#        model.add_node(Node(random(),random(),random()))
#    print(model.add_node(Node(1,2,3)))
#    for i in range(333):
#        model.add_node(Node(random(),random(),random()))
#    print(model.add_node(Node(1,2,3)))