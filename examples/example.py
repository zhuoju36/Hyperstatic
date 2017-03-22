# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 09:56:44 2016

@author: HZJ
"""
import sys
sys.path.append('..')

import Material,Section,Node,Element,Loadcase,LoadCombination,Load
from Model import fem_model
from Solver import Static

#step 1: construct a fem_model object.
m=fem_model('d:/fem_model')

#step 2: construct material objects and add them to the model.
steel=Material.linear_elastic(2.000E11, 0.3, 7849.0474, 1.17e-5)#Q345
m.add_material(steel)

#step 3: construct section objects and add them to the model.
#i_section=Section.I_section(steel, 200,150,8,10)#H200x150x8x10
i_section=Section.section(steel,4.265e-3,9.651e-8,6.572e-5,3.301e-6,4.313e-4,5.199e-5)
m.add_section(i_section)

#step 4: construct load case and load combination objects and add them to the model.
lc1=Loadcase.loadcase('S') #self-weight
lc2=Loadcase.loadcase('D') #superimposed deadload
lc3=Loadcase.loadcase('L') #live load
comb1=LoadCombination.combination('SLS:S+D+L',{'S':1.0,'D':1.0,'L':1.0})
comb2=LoadCombination.combination('ULS:1.35SD+0.98L',{'S':1.35,'D':1.35,'L':0.98})
comb3=LoadCombination.combination('SLS:1.2SD+1.4L',{'S':1.2,'D':1.2,'L':1.4})
m.add_loadcase(lc1)
m.add_loadcase(lc2)
m.add_loadcase(lc3)
m.add_combination

#step 5: construct nodes and elements and add them to the model.
#simple-supported beam
m.add_node(Node.node(0, 0, 0))
m.add_node(Node.node(14.28,0,0))
m.add_node(Node.node(20,0,0))
m.add_beam(Element.beam(m.nodes[0], m.nodes[1], i_section))
m.add_beam(Element.beam(m.nodes[1], m.nodes[2], i_section))

#step 6: construct loads objects and add them to the model.
m.add_beam_distributed(Load.beam_distributed('S',[0,1],[0,-10000,0,0,0,0],[0,-10000,0,0,0,0]))
m.add_beam_distributed(Load.beam_distributed('D',[0,1],[0,-50000,0,0,0,0],[0,-50000,0,0,0,0]))
m.add_beam_distributed(Load.beam_distributed('L',[0,1],[0,-25000,0,0,0,0],[0,-25000,0,0,0,0]))

#step 7:apply boundary conditions.
res1=[True,True,True,False,False,False]
res2=[True,True,True,True,False,False]
m.set_node_restraint(0,res1)
m.set_node_restraint(2,res2)

#step 8: save model
m.save()

#step 9: for each load case, solve the model
for loadcase in m.loadcases:
    lc=loadcase.name
    m.assemble2(lc) 
    d=Static.solve_linear2(m)
    m.resolve_result(d)
    if m.is_solved:
        m.save_result(lc)