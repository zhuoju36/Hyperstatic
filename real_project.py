#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 22:57:37 2018

@author: hzj
"""

from object_model.model import Model
import logger as log



model=Model()

model.create('005_dev.mdo')
model.open('005_dev.mdo')
model.set_unit('N_m_C')

model.import_dxf('test.dxf')

model.add_loadcase('D','static-linear',0)
model.add_loadcase('L','static-linear',0)
model.add_loadcase('Modal','modal',0)

pts_to_restraint=model.get_point_name(z=0)
pts_to_restraint+=model.get_point_name(z=11.4)

model.add_point_restraint_batch(pts_to_restraint,[True]*6)
#model.set_point_load(pt1,'D',[0,0,-100000,0,0,0])
#model.set_point_load(pt1,'L',[0,0,0,0,0,0])

#model.save()
model.run(['Modal'])

#print(model.get_result_point_reaction(pt0,'D'))
#print(model.get_result_frame_force(f1,'D')[0][:6])
print(model.get_result_period('Modal'))

model.export_dxf('./','exported_model.dxf')

#model.save()

#import test.beam_test as bt
#bt.cantilever_beam_test()
