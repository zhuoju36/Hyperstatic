import numpy as np
from sympy import symbols,Matrix
from fe_model.node import Node
from fe_model.element import Beam,Membrane3,Membrane4
from fe_model import Model as FEModel
from fe_solver.static import solve_linear
from fe_solver.dynamic import solve_modal
    
def shear_test4():
    model=FEModel()
    n1=Node(0,0,0)
    n2=Node(0,0,5)
    n3=Node(5,0,5)
    n4=Node(10,0,5)
    n5=Node(10,0,0)
    n6=Node(5,0,0)
    
    a1=Membrane4(n1,n2,n3,n6,0.25,2e11,0.3,7849)
    a2=Membrane4(n3,n4,n5,n6,0.25,2e11,0.3,7849)
    
    model.add_node(n1)
    model.add_node(n2)
    model.add_node(n3)
    model.add_node(n4)
    model.add_node(n5)
    model.add_node(n6)

    model.add_membrane4(a1)
    model.add_membrane4(a2)

    n3.fn=(0,0,-100000,0,0,0)
    n1.dn=n2.dn=n4.dn=n5.dn=[0]*6
    n3.dn=n6.dn=[0,0,None,0,0,0]
    
    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    res=solve_linear(model)

    np.set_printoptions(precision=6,suppress=True)
    print(res)
    print(r"correct answer should be ???")