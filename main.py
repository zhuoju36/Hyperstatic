# -*- coding: utf-8 -*-
#import test.membrane3_test as mt3
#import test.membrane4_test as mt4
#import test.beam_test as bt
#import Logger as log
#
#mt3.pseudo_cantilever_test(25,5)
##bt.simple_supported_beam_test()
#  

from object_model.model import Model
from object_model.quick_material import GB_Q345
from object_model.frame_section import Pipe
from object_model.object import Point,Frame
from object_model.loadcase import StaticLinear
from object_model.load import LoadPt

model=Model()
try:
#    model.create('D:/Source/StructEngPy/mydev.db.db')
    model.open('D:/Source/StructEngPy/mydev.db')
    
    model.add_material('Q345B',7849,'isotropic_elastic',
                            E=2e11,mu=0.3)
    model.add_frame_section('Q345','pipe',[400,20])
    
    model.add_loadcase(StaticLinear('S'))
    model.add_loadcase(StaticLinear('D'))
    model.add_loadcase(StaticLinear('L'))

    model.add_point('pt0',0,0,0)
    model.add_point('pt1',5,5,5)
    f1=model.add_frame('frm0','pt0','pt1','Q345')
    
    model.set_point_restraint(pt1,[True]*6)
    model.set_point_load(pt2,
                         LoadPt('D',[0,0,-1000,0,0,0])
                         )
    
    model.run()
except Exception as e:
    print(e)
    model.close()
    
    