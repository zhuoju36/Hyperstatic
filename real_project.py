#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 22:57:37 2018

@author: hzj
"""

from object_model.model import Model
import ezdxf

dwg = ezdxf.readfile("test.dxf")

model=Model()

model.create('mydev.db')
model.open('mydev.db')
model.set_unit('N_m_C')

model.add_material('Q345B',7849,'isotropic_elastic',
                        E=2e11,mu=0.3)
#model.add_frame_section('1-L-O400x20','Q345B','O',[0.4,0.02])
model.add_frame_section('1-L-H400x200x14x20','Q345B','I',[0.4,0.2,0.014,0.02])

model.add_loadcase('S','static-linear',1.)
model.add_loadcase('D','static-linear',0)
model.add_loadcase('L','static-linear',0)
model.add_loadcase('Modal','modal',0)

frames=[]

modelspace = dwg.modelspace()
for e in modelspace:
    if e.dxftype() == 'LINE':
        frames.append(model.add_frame(e.dxf.start,e.dxf.end,'1-L-H400x200x14x20'))

pts_to_restraint=model.get_point_name(z=0)

for pt in pts_to_restraint:
    model.set_point_restraint(pt,[True]*6)
#model.set_point_load(pt1,'D',[0,0,-100000,0,0,0])
#model.set_point_load(pt1,'L',[0,0,0,0,0,0])

#model.save()
model.mesh()
model.run(['S','D','L','Modal'])

#print(model.get_result_point_reaction(pt0,'D'))
#print(model.get_result_frame_force(f1,'D')[0][:6])
print(model.get_result_period('Modal'))

#model.save()

#import test.beam_test as bt
#bt.cantilever_beam_test()
