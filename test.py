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
    
def simply_supported_beam_test():
    #FEModel Test
    model=FEModel()

    E=1.999e11
    mu=0.3
    A=4.265e-3
    J=9.651e-8
    I3=6.572e-5
    I2=3.301e-6
    rho=7849.0474
    
    model.add_node(0,0,0)
    model.add_node(0.5,1,0.5)
    model.add_node(1,2,1)
    
    model.add_beam(0,1,E,mu,A,I2,I3,J,rho)
    model.add_beam(1,2,E,mu,A,I2,I3,J,rho)

    model.set_node_force(1,(0,0,-1e6,0,0,0))
    model.set_node_restraint(2,[False,False,True]+[False]*3)
    model.set_node_restraint(0,[True]*3+[False]*3)

    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    solve_linear(model)
    print(np.round(model.d_,6))
    print("The result of node 1 should be about [0.00796,0.00715,-0.02296,-0.01553,-0.03106,-0.01903]")
     
def simply_released_beam_test():
    #FEModel Test
    model=FEModel()

    E=1.999e11
    mu=0.3
    A=4.265e-3
    J=9.651e-8
    I3=6.572e-5
    I2=3.301e-6
    rho=7849.0474
    
    model.add_node(0,0,0)
    model.add_node(0.5,1,0.5)
    model.add_node(1,2,1)
    
    model.add_beam(0,1,E,mu,A,I2,I3,J,rho)
    model.add_beam(1,2,E,mu,A,I2,I3,J,rho)

    model.set_node_force(1,(0,0,-1e6,0,0,0))
    model.set_node_restraint(2,[True]*6)
    model.set_node_restraint(0,[True]*6)
    
    model.set_beam_releases(0,[True]*6,[False]*6)
    model.set_beam_releases(1,[False]*6,[True]*6)
    
    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    solve_linear(model)
    print(np.round(model.d_,6))
    print("The result of node 1 should be about [0.00445,0.00890,-0.02296,-0.01930,-0.03860,-0.01930]")
   
simply_released_beam_test()

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
    
def diff_inference():
    
    r,s=symbols('r,s')
    
    la1,la2,lb1,lb2=symbols('l^a_1,l^a_2,l^b_1,l^b_2')
    
    la1=(1-s)/2
    la2=(1+s)/2
    lb1=(1-r)/2
    lb2=(1+r)/2
    N1=la1*lb1
    N2=la1*lb2
    N3=la2*lb1
    N4=la2*lb2
    
    N=Matrix([[N1,0,N2,0,N3,0,N4,0],
              [0,N1,0,N2,0,N3,0,N4]])


"""
Membrane3 tests
"""
def shear_test():
    model=FEModel()
    n1=Node(0,0,0)
    n2=Node(0,0,5)
    n3=Node(5,0,5)
    n4=Node(10,0,5)
    n5=Node(10,0,0)
    
    a1=Membrane3(n1,n2,n3,0.25,2e11,0.3,7849)
    a2=Membrane3(n3,n4,n5,0.25,2e11,0.3,7849)
    a3=Membrane3(n1,n3,n5,0.25,2e11,0.3,7849)
    
    model.add_node(n1)
    model.add_node(n2)
    model.add_node(n3)
    model.add_node(n4)
    model.add_node(n5)

    model.add_membrane3(a1)
    model.add_membrane3(a2)
    model.add_membrane3(a3)

    n3.fn=(0,0,-100000,0,0,0)
    n1.dn=n2.dn=n4.dn=n5.dn=[0,0,0,0,0,0]

    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    res=solve_linear(model)
        
    np.set_printoptions(precision=6,suppress=True)
    print(res)
    print(r"correct answer should be about ???")
    
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
    
def pseudo_cantilever_test4(l=25,h=5):
    """
    This is a cantilever beam with 50x10
    l,h: division on l and h direction
    """
    model=FEModel()
    nodes=[]
    model=FEModel()
    nodes=[]
    for i in range(h+1):
        for j in range(l+1):
            nodes.append(Node(j*50/l,0,i*10/h))
            model.add_node(nodes[-1])
            
    for i in range(h):
        for j in range(l):
            area=Membrane4(nodes[i*(l+1)+j],
                           nodes[i*(l+1)+j+1],
                           nodes[(i+1)*(l+1)+j+1],
                           nodes[(i+1)*(l+1)+j+1],
                           0.25,2e11,0.3,7849)
            if j==0:
                nodes[i*(l+1)+j].dn=[0]*6
                nodes[(i+1)*(l+1)+j].dn=[0]*6

            model.add_membrane4(area)

    nodes[(l+1)*(h+1)-1].fn=(0,0,-100000,0,0,0)
    
    model.assemble_KM()
    model.assemble_f()
    model.assemble_boundary()
    res=solve_linear(model)

    np.set_printoptions(precision=6,suppress=True)
    print(res[(l+1)*(h+1)*6-6:])
    print(r"correct answer should be ???")