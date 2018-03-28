#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 22:57:37 2018

@author: hzj
"""

from object_model.model import Model
import logger as log
import ezdxf

model=Model()

model.open('szds0.mdo')
model.set_unit('N_mm_C')
model.set_tolerance(10.)

dwg = ezdxf.readfile('test.dxf')
for layer in dwg.layers:
    print(layer.dxf.name)
    if layer.dxf.name != '0' and layer.dxf.name != 'defpoints' and layer.dxf.name[0] != 'A':
        sec_name=layer.dxf.name
        material=layer.dxf.name.split('-')[0]
        sec_type=layer.dxf.name.split('-')[2][0]
        sizes=[eval(v) for v in layer.dxf.name.split('-')[2][1:].split('x')]
        model.add_frame_section(layer.dxf.name,'Q345',sec_type,sizes)
        model.import_dxf(r'D:\结构设计\1713-德州会展中心\test.dxf',layers=[layer.dxf.name],types='f',frm_sec=sec_name)
    if layer.dxf.name != '0' and layer.dxf.name != 'defpoints' and layer.dxf.name[0] == 'A':
        sec_name=layer.dxf.name
        material='Q345'
        sec_type='m'
        t=0.01
#        model.add_area_section(layer.dxf.name,'Q345',sec_type,t)
        model.import_dxf(r'D:\结构设计\1713-德州会展中心\test.dxf',layers=[layer.dxf.name],types='a',area_sec=sec_name)

model.add_loadcase('D','static-linear',0)
model.add_loadcase('L','static-linear',0)
model.add_loadcase('Modal','modal',0)

pts_to_restraint=[pt for pt in model.get_point_names() if abs(model.get_point_coordinate(pt)[2]-13900)<10]

model.set_point_restraint_batch(pts_to_restraint,[True,True,True,True,True,True])
#model.set_point_load(pt1,'D',[0,0,-100000,0,0,0])
#model.set_point_load(pt1,'L',[0,0,0,0,0,0])

#model.save()
model.run(['Modal'])

#print(model.get_result_point_reaction(pt0,'D'))
#print(model.get_result_frame_force(f1,'D')[0][:6])
#print(model.get_result_period('Modal'))

#model.export_dxf('./','exported_model.dxf',True)

#model.save()

#import test.beam_test as bt
#bt.cantilever_beam_test()
