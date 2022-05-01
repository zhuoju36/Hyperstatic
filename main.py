 # -*- coding: utf-8 -*-

from object_model.model import Model

model=Model()
model.create('mydev4.mdo')
model.open('mydev4.mdo')
model.set_unit('N_m_C')

model.add_material('Q345B',7849,'isotropic_elastic',
                        E=2e11,mu=0.3)
#model.add_frame_section('1-L-O400x20','Q345B','O',[0.4,0.02])
model.add_frame_section('1-L-H400x200x14x20','Q345B','I',[0.4,0.2,0.014,0.02])

model.add_loadcase('S','static-linear',1.)
model.add_loadcase('D','static-linear',0)
model.add_loadcase('L','static-linear',0)
model.add_loadcase('Modal','modal',0)

f1=model.add_frame((0,0,0),(5,5,5),'1-L-H400x200x14x20')
f2=model.add_frame((5,5,0),(5,5,5),'1-L-H400x200x14x20')
f3=model.add_frame((5,5,5),(10,0,5),'1-L-H400x200x14x20')

#model.merge_point(6)

model.get_point_name_by_coor(z=0)
pt0=model.get_point_name_by_coor(0,0,0)[0]
pt1=model.get_point_name_by_coor(10,0,5)[0]

model.set_point_restraint(pt0,[True]*6)
model.set_point_load(pt1,'D',[0,0,-100000,0,0,0])
model.set_point_load(pt1,'L',[0,0,-50000,0,0,0])

#model.save()
model.mesh()
model.run(['S','D','L'])
 
#print(model.get_result_point_reaction(pt0,'D'))
#print(model.get_result_frame_force(f1,'D')[0][:6])
print(model.get_result_period('Modal'))

#model.save()
#model.close()

#import test.beam_test as bt
#bt.cantilever_beam_test()
