# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 09:56:44 2016

@author: HZJ
"""
import sys
sys.path.append('..')

import Material,Section,Node,Element
from Model import fem_model
from Solver import Static

m=fem_model('d:/fem_model')
steel=Material.linear_elastic(2.000E11, 0.3, 7849.0474, 1.17e-5)#Q345
#i_section=Section.I_section(steel, 200,150,8,10)#H200x150x8x10
i_section=Section.section(steel,4.265e-3,9.651e-8,6.572e-5,3.301e-6,4.313e-4,5.199e-5)
m.add_material(steel)
m.add_section(i_section)

#simple-supported beam
m.add_node(Node.node(0, 0, 0))
m.add_node(Node.node(14.28,0,0))
m.add_node(Node.node(20,0,0))
m.add_beam(Element.beam(m.nodes[0], m.nodes[1], i_section))
m.add_beam(Element.beam(m.nodes[1], m.nodes[2], i_section))
qi=(0,-10000,0,0,0,0)
qj=(0,-10000,0,0,0,0)
m.set_beam_distributed(0,qi,qj)
m.set_beam_distributed(1,qi,qj)
res1=[True,True,True,False,False,False]
res2=[True,True,True,True,False,False]
m.set_node_restraint(0,res1)
m.set_node_restraint(2,res2)

m.save()

m.assemble() 
d=Static.solve_linear(m)
m.write_result(d)
if m.is_solved:
    m.save_result()