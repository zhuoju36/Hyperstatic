# # -*- coding: utf-8 -*-
# import pytest

# import numpy as np

# from structengpy.fe_model.node import Node
# from structengpy.fe_model.quad.membrane import Membrane4
# from structengpy.fe_model.model import Model as FEModel
# from structengpy.fe_solver.static import solve_linear

# class TestMem4System():

#     def test_shear(self):
#         model=FEModel()
#         n1=Node(0,0,0)
#         n2=Node(0,0,5)
#         n3=Node(5,0,5)
#         n4=Node(10,0,5)
#         n5=Node(10,0,0)
#         n6=Node(5,0,0)
        
#         a1=Membrane4(n1,n2,n3,n6,0.25,2e11,0.3,7849)
#         a2=Membrane4(n3,n4,n5,n6,0.25,2e11,0.3,7849)
        
#         model.add_node(n1)
#         model.add_node(n2)
#         model.add_node(n3)
#         model.add_node(n4)
#         model.add_node(n5)
#         model.add_node(n6)

#         model.add_membrane4(a1)
#         model.add_membrane4(a2)

#         n3.fn=(0,0,-100000,0,0,0)
#         n1.dn=n2.dn=n4.dn=n5.dn=[0]*6
#         n3.dn=n6.dn=[0,0,None,0,0,0]
        
#         model.assemble_KM()
#         model.assemble_f()
#         model.assemble_boundary()
#         res=solve_linear(model)

#         np.set_printoptions(precision=6,suppress=True)
#         print(res)
#         print(r"correct answer should be ???")

#     def test_pseudo_cantilever(self):
#         """
#         This is a cantilever beam with 50x10
#         l,h: division on l and h direction
#         """
#         l=25
#         h=5
#         model=FEModel()
#         nodes=[]
#         model=FEModel()
#         nodes=[]
#         for i in range(h+1):
#             for j in range(l+1):
#                 nodes.append(Node(j*50/l,0,i*10/h))
#                 model.add_node(nodes[-1])
                
#         for i in range(h):
#             for j in range(l):
#                 area=Membrane4(nodes[i*(l+1)+j],
#                             nodes[i*(l+1)+j+1],
#                             nodes[(i+1)*(l+1)+j+1],
#                             nodes[(i+1)*(l+1)+j+1],
#                             0.25,2e11,0.3,7849)
#                 if j==0:
#                     nodes[i*(l+1)+j].dn=[0]*6
#                     nodes[(i+1)*(l+1)+j].dn=[0]*6

#                 model.add_membrane4(area)

#         nodes[(l+1)*(h+1)-1].fn=(0,0,-100000,0,0,0)
        
#         model.assemble_KM()
#         model.assemble_f()
#         model.assemble_boundary()
#         res=solve_linear(model)

#         np.set_printoptions(precision=6,suppress=True)
#         print(res[(l+1)*(h+1)*6-6:])
#         print(r"correct answer should be ???")