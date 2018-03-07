# -*- coding: utf-8 -*-

from Modeler.Material import IsotropyElastic
from Modeler.Section import AreaSection
from Modeler.Node import Node
from Modeler.Element import Beam,TriMembrane
from Modeler.FEModel import FEModel
#import Logger
from Modeler.FEModel import solve_linear


if __name__=='__main__':
    #FEModel Test
    model=FEModel()
    n1=Node(0,0,0)
    n2=Node(1,0,0)
    n3=Node(2,0,0)
    b1=Beam(n1,n2,2e5,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7.85)
    b2=Beam(n1,n2,2e5,0.3,0.013,2.675e-5,3.435e-4,1.321e-6,7.85)
    model.add_node(n1)
    model.add_node(n2)
    model.add_node(n3)
    model.add_beam(b1)
    model.add_beam(b2)
    n2.Fn=(0,0,-1,0,0,0)
    n1.restraint=[True]*6
    n3.restraint=[True]*6
    model.assemble_KM()
    model.assemble_FD()
    model.eliminate_matrix()
    res=solve_linear(model)
    print(res)
    
    


#    from random import random
#    model=FEModel()
#    for i in range(333):
#        model.add_node(Node(random(),random(),random()))
#    print(model.add_node(Node(1,2,3)))
#    for i in range(333):
#        model.add_node(Node(random(),random(),random()))
#    print(model.add_node(Node(1,2,3)))