# -*- coding: utf-8 -*-

from Modeler.Material import IsotropyElastic
from Modeler.Section import AreaSection
from Modeler.Node import Node
from Modeler.Element import TriMembrane

if __name__=='__main__':
    
    n1=Node(0,0,0)
    n2=Node(3,0,0)
    n3=Node(0,4,0)
    steel=IsotropyElastic(7849.0474,2.000E5,0.2,1.17e-5)#Q345
    tri=TriMembrane(n1,n2,n3,AreaSection(steel,1))
    print(tri.K[:3,:3]/8681)
