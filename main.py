# -*- coding: utf-8 -*-
#import test.membrane3_test as mt3
#import test.membrane4_test as mt4
#import test.beam_test as bt
#import Logger as log
#
#mt3.pseudo_cantilever_test(25,5)
##bt.simple_supported_beam_test()
#  

from object_model import Model
from object_model.quick_material import GB_Q345
from object_model.frame_section import Pipe
from object_model.object import Point,Frame
from object_model.loadcase import StaticLinear


if __name__=='__main__':
    model=Model()
    
    q345=model.add_material(GB_Q345())
    sec=model.add_frmsec(Pipe(q345,0.4,0.02,'1-L-O400x20'))
    
    l1=model.add_loadcase(StaticLinear('S'))
    l2=model.add_loadcase(StaticLinear('D'))
    l3=model.add_loadcase(StaticLinear('L'))

    pt1=model.add_pt(Point(0,0,0))
    pt2=model.add_pt(Point(5,5,5))
    f1=model.add_frame(
            Frame(
                    model.points[pt1],
                    model.points[pt1],
                    model.frame_sections[sec]
                    )
            )
    
    model.nodes[pt1].restraint=[True]*6
    model.nodes[pt2].load_pt=[0,0,-100000,0,0,0]
    
    model.run()

    
    