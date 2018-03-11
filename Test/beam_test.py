# -*- coding: utf-8 -*-
import numpy as np
import scipy.sparse as spr
from Modeler.Node import Node
from Modeler.Element import Beam,Membrane3,Membrane4
from Modeler.Material import IsotropyElastic
from Modeler.Section import AreaSection
from Modeler.FEModel import FEModel
from Solver.Static import solve_linear,solve_modal

def cantilever_beam_test():
    #FEModel Test
    model=FEModel()
    n1=Node(0,0,0)
    n2=Node(5,5,5)
    b1=Beam(n1,n2,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
    model.add_node(n1)
    model.add_node(n2)
    model.add_beam(b1)
    n2.fn=(0,0,100000,0,0,100000)
    n1.dn=[0,0,0,0,0,0]
#    b1.releases=[False]*3+[True]*3+[False]*6
#    b2.releases=[False]*6+[False]*3+[True]*3
    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    res=solve_linear(model)
    print(np.round(res,6))
    res=solve_modal(model,3)

def simple_supported_beam_test():
    #FEModel Test
    model=FEModel()
    n1=Node(0,0,0)
    n2=Node(5,0,0)
    n3=Node(10,0,0)
    b1=Beam(n1,n2,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
    b2=Beam(n2,n3,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
    model.add_node(n1)
    model.add_node(n2)
    model.add_node(n3)
    model.add_beam(b1)
    model.add_beam(b2)
    n2.fn=(0,0,-100000,0,0,0)
    n1.dn=[0,0,0,None,None,None]
    n3.dn=[0,0,0,None,None,None]
#    b1.releases=[False]*3+[True]*3+[False]*6
#    b2.releases=[False]*6+[False]*3+[True]*3
    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    res=solve_linear(model)
    print(res)
    res=solve_modal(model,6)
    print('Periods:')
    print(res[0])
    
def simple_released_beam_test():
    #FEModel Test
    model=FEModel()
    n1=Node(0,0,0)
    n2=Node(5,0,0)
    n3=Node(10,0,0)
    b1=Beam(n1,n2,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
    b2=Beam(n2,n3,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
    model.add_node(n1)
    model.add_node(n2)
    model.add_node(n3)
    model.add_beam(b1)
    model.add_beam(b2)
    n2.fn=(0,0,-100000,0,0,0)
    n1.dn=[0,0,0,0,0,0]
    n3.dn=[0,0,0,0,0,0]
    b1.releases=[False]*3+[True]*3+[False]*6
    b2.releases=[False]*6+[False]*3+[True]*3
    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    res=solve_linear(model)
    print(res)
    
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