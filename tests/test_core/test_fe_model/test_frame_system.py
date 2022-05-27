# # -*- coding: utf-8 -*-
# import pytest
# from pytest import approx,raises

# import numpy as np

# from structengpy.fe_model.node import Node
# from structengpy.fe_model.line.beam import Beam
# from structengpy.fe_model.model import Model as FEModel
# from structengpy.fe_solver.static import solve_linear

# class TestFrameSystem():

#     def test_cantilever_beam(self):
#         #FEModel Test
#         model=FEModel()
#         model.add_node(0,0,0)
#         model.add_node(2,1,1)
#         E=1.999e11
#         mu=0.3
#         A=4.265e-3
#         J=9.651e-8
#         I3=6.572e-5
#         I2=3.301e-6
#         rho=7849.0474
        
#         model.add_beam(0,1,E,mu,A,I2,I3,J,rho)
#         model.set_node_force(1,(0,0,-1e6,0,0,0))
#         model.set_node_restraint(0,[True]*6)
#         model.assemble_KM()
#         model.assemble_f()
#         model.assemble_boundary()
#         solve_linear(model)
#         # print(np.round(model.d_,6))
#         # print("The result of node 1 should be about [0.12879,0.06440,-0.32485,-0.09320,0.18639,0]")
#         assert model.d_[0:6]==approx(np.array([0.12879,0.06440,-0.32485,-0.09320,0.18639,0]),1e-5)

#     def test_simply_released_beam(self):
#         #FEModel Test
#         model=FEModel()

#         E=1.999e11
#         mu=0.3
#         A=4.265e-3
#         J=9.651e-8
#         I3=6.572e-5
#         I2=3.301e-6
#         rho=7849.0474
        
#         model.add_node(0,0,0)
#         model.add_node(0.5,1,0.5)
#         model.add_node(1,2,1)
        
#         model.add_beam(0,1,E,mu,A,I2,I3,J,rho)
#         model.add_beam(1,2,E,mu,A,I2,I3,J,rho)

#         model.set_node_force(1,(0,0,-1e6,0,0,0))
#         model.set_node_restraint(2,[True]*6)
#         model.set_node_restraint(0,[True]*6)
        
#         model.set_beam_releases(0,[True]*6,[False]*6)
#         model.set_beam_releases(1,[False]*6,[True]*6)
        
#         model.assemble_KM()
#         model.assemble_f()
#         model.assemble_boundary()
#         solve_linear(model)
#         print(np.round(model.d_,6))
#         print("The result of node 1 should be about [0.00445,0.00890,-0.02296,-0.01930,-0.03860,-0.01930]")

#     def test_simply_supported_beam(self):
#         #FEModel Test
#         model=FEModel()

#         E=1.999e11
#         mu=0.3
#         A=4.265e-3
#         J=9.651e-8
#         I3=6.572e-5
#         I2=3.301e-6
#         rho=7849.0474
        
#         model.add_node(0,0,0)
#         model.add_node(0.5,1,0.5)
#         model.add_node(1,2,1)
        
#         model.add_beam(0,1,E,mu,A,I2,I3,J,rho)
#         model.add_beam(1,2,E,mu,A,I2,I3,J,rho)

#         model.set_node_force(1,(0,0,-1e6,0,0,0))
#         model.set_node_restraint(2,[False,False,True]+[False]*3)
#         model.set_node_restraint(0,[True]*3+[False]*3)

#         model.assemble_KM()
#         model.assemble_f()
#         model.assemble_boundary()
#         solve_linear(model)
#         print(np.round(model.d_,6))
#         print("The result of node 1 should be about [0.00796,0.00715,-0.02296,-0.01553,-0.03106,-0.01903]")

#     def test_2Dframe(self):
#         #FEModel Test
#         model=FEModel()
#         n1=Node(0,0,0)
#         n2=Node(0,0,5)
#         n3=Node(5,0,5)
#         n4=Node(10,0,5)
#         n5=Node(10,0,0)
#         b1=Beam(n1,n2,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
#         b2=Beam(n2,n3,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
#         b3=Beam(n3,n4,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
#         b4=Beam(n4,n5,2e11,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7849)
        
#         model.add_node(n1)
#         model.add_node(n2)
#         model.add_node(n3)
#         model.add_node(n4)
#         model.add_node(n5)

#         model.add_beam(b1)
#         model.add_beam(b2)
#         model.add_beam(b3)
#         model.add_beam(b4)

#         n2.fn=(100000,0,0,0,0,0)
#         n3.fn=(0,0,-100000,0,0,0)
#         n1.dn=[0,0,0,0,0,0]
#         n5.dn=[0,0,0,0,0,0]

#         model.assemble_KM()
#         model.assemble_f()
#         model.assemble_boundary()
#         res=solve_linear(model)
        
#         print(res)