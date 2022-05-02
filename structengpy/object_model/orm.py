# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 16:20:13 2018

@author: HZJ
@E-mail: zhuoju36@hotmail.com
"""

import uuid
from sqlalchemy import create_engine,\
Column,Integer,Float,String,Boolean,Text,DateTime,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,backref

Base=declarative_base()

class Config(Base):
    __tablename__='configs'
    project_name=Column('project_name',String(64),primary_key=True)
    discription=Column('discription',Text)
    author=Column('author',String(64))
    program_version=('program_version',String(8))
    unit=Column('unit',String(10),default='N_m_C')
    tolerance=Column('tolerance',Float(),default=1e-6)
    create_time=Column('create_time',DateTime())
    modify_time=Column('modify_time',DateTime())
    
class Material(Base):
    __tablename__='materials'
    name=Column('name',String(32),primary_key=True)
    rho=Column('rho',Float())
    type=Column('type',String(32))
    
    #other types...
    uuid=Column('uuid',String(32),nullable=False)
    #1 to 1
    isotropic_elastic=relationship('IsotropicElastic',
                                   backref=backref('material',uselist=False),uselist=False) #1 to 1
    #1 to many
    frame_sections=relationship('FrameSection',backref='material')
    area_sections=relationship('AreaSection',backref='material')

class IsotropicElastic(Base):
    __tablename__='isotropic_elastics'
    material_name=Column('material_name',ForeignKey('materials.name'),primary_key=True)
    E=Column('E',Float())
    mu=Column('mu',Float())
    
#other material...

class FrameSection(Base):
    __tablename__='frame_sections'
    name=Column('name',String(32),primary_key=True)
    shape=Column('shape',String(32))
    material_name=Column('material_name',String(32),ForeignKey('materials.name'))
    size_0=Column('size_0',Float())
    size_1=Column('size_1',Float())
    size_2=Column('size_2',Float())
    size_3=Column('size_3',Float())
    size_4=Column('size_4',Float())
    size_5=Column('size_5',Float())
    size_6=Column('size_6',Float())
    size_7=Column('size_7',Float())
    A=Column('A',Float())
    J=Column('J',Float())
    S2=Column('S2',Float())
    S3=Column('S3',Float())
    I2=Column('I2',Float())
    I3=Column('I3',Float())
    uuid=Column('uuid',String(32),nullable=False)
    
    #1 to many
    frames=relationship('Frame',backref='section')
    
class SDSection(Base):
    __tablename__='SD_sections'
    frame_section=Column('frame_section',
                         ForeignKey('frame_sections.name'),
                         primary_key=True)
    material=('material',ForeignKey('materials.name'))   

class AreaSection(Base):
    __tablename__='area_sections'
    name=Column('name',String(32),primary_key=True)
    material_name=Column('material_name',String(32),ForeignKey('materials.name'))
    type=Column('type',String(8))
    t=Column('t',Float())
    uuid=Column('uuid',String(32),nullable=False)
    
    #1 to many
    areas=relationship('Area',backref='section')

class LoadCase(Base):
    __tablename__='loadcases'
    name=Column('name',String(32),primary_key=True)
    case_type=Column('case_type',String(16))
    weight_factor=Column('weight_factor',Float,default=0)
    uuid=Column('uuid',String(32),nullable=False)
    
    #1 to 1
    static_linear_setting=relationship('LoadCaseStaticLinearSetting',backref=backref('loadcase',uselist=False),uselist=False)
    loadcase_modal_setting=relationship('LoadCaseModalSetting',backref=backref('loadcase',uselist=False),uselist=False)
    loadcase_2nd_setting=relationship('LoadCase2ndSetting',backref=backref('loadcase',uselist=False),uselist=False)
    loadcase_3nd_setting=relationship('LoadCase3ndSetting',backref=backref('loadcase',uselist=False),uselist=False)
    loadcase_response_spectrum_setting=relationship('LoadCaseResponseSpectrumSetting',backref=backref('loadcase',uselist=False),uselist=False)
    loadcase_time_history_setting=relationship('LoadCaseTimeHistorySetting',backref=backref('loadcase',uselist=False),uselist=False)

    #1 to many    
    point_load=relationship('PointLoad',backref='loadcase')
    point_disp=relationship('PointDisp',backref='loadcase')
    frame_load_distributed=relationship('FrameLoadDistributed',backref='loadcase')
    frame_load_concentrated=relationship('FrameLoadConcentrated',backref='loadcase')
    frame_load_strain=relationship('FrameLoadStrain',backref='loadcase')
    frame_load_temperature=relationship('FrameLoadTemperature',backref='loadcase')
    area_load_to_frame=relationship('AreaLoadToFrame',backref='loadcase')
    area_load_distributed=relationship('AreaLoadDistributed',backref='loadcase')
    area_load_strain=relationship('AreaLoadStrain',backref='loadcase')
    area_load_temperature=relationship('AreaLoadTemperature',backref='loadcase')
    
    result_point_displacement=relationship('ResultPointDisplacement',backref='loadcase')
    result_point_reaction=relationship('ResultPointReaction',backref='loadcase')
    result_frame_force=relationship('ResultFrameForce',backref='loadcase')
    result_area_stress=relationship('ResultAreaStress',backref='loadcase')
    result_modal_displacement=relationship('ResultModalDisplacement',backref='loadcase')
    

class LoadCaseStaticLinearSetting(Base):
    __tablename__='laodcase_static_linear_settings'
    loadcase_name=Column('loadcase_name',ForeignKey('loadcases.name'),primary_key=True)


class LoadCaseModalSetting(Base):
    __tablename__='loadcase_modal_settings'
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    method=Column('method',String(8))
    modal_num=Column('modal_num',Integer(),default=12)
    tolerance=Column('tolerance',Float,default=1e-6)
    iteration=Column('iteration',Integer(),default=99)

class LoadCase2ndSetting(Base):
    __tablename__='loadcase_2nd_settings'
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    method=Column('method',String(8))
    
#    plc_name=Column('plc',String(32),ForeignKey('loadcases.name'))
#    plc=relationship("LoadCase", foreign_keys=[plc_name])

class LoadCase3ndSetting(Base):
    __tablename__='loadcase_3nd_settings'
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    method=Column('method',String(8))
    
#    plc_name=Column('plc',String(32),ForeignKey('loadcases.name'))
#    plc=relationship("LoadCase", foreign_keys=[plc_name])

class LoadCaseResponseSpectrumSetting(Base):
    __tablename__='loadcase_response_spectrum_settings'
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    method=Column('method',String(8))

class LoadCaseTimeHistorySetting(Base):
    __tablename__='loadcase_time_history_settings'
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    method=Column('method',String(8))
    
class LoadCaseBucklingSetting(Base):
    __tablename__='loadcase_buckling_settings'
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    method=Column('method',String(8))
    
class Combination(Base):
    __tablename__='combinations'
    name=Column('name',String(32),primary_key=True)
    combination_type=Column('combination_type',String(16))
    uuid=Column('uuid',String(32),nullable=False)
    
    #1 to many
    combination_cases=relationship('CombinationCase',backref='combination')
    
class CombinationCase(Base):
    __tablename__='combination_cases'
    combination_name=Column('combination_name',String(32),ForeignKey('combinations.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    method=Column('method',String(8))
    
class Point(Base):
    __tablename__='points'
    name=Column('name',String(32),primary_key=True)
    x=Column('x',Float)
    y=Column('y',Float)
    z=Column('z',Float)
    uuid=Column('uuid',String(32),nullable=False)
    
    #1 to 1
    point_restraint=relationship('PointRestraint',backref=backref('point',uselist=False))
    point_load=relationship('PointLoad',backref=backref('point',uselist=False))
    point_disp=relationship('PointDisp',backref=backref('point',uselist=False))
    point_mass=relationship('PointMass',backref=backref('point',uselist=False))
    
    def __repr__(self):
        return '%s<%r>'%(self.__class__.__name__,self.name)
    
class PointRestraint(Base):
    __tablename__='point_restraints'
    point_name=Column('point_name',String(32),ForeignKey('points.name'),primary_key=True)
    u1=Column('u1',Boolean())
    u2=Column('u2',Boolean())
    u3=Column('u3',Boolean())
    r1=Column('r1',Boolean())
    r2=Column('r2',Boolean())
    r3=Column('r3',Boolean())

class PointLoad(Base):
    __tablename__='pointloads'
    point_name=Column('point_name',String(32),ForeignKey('points.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    u1=Column('p1',Float())
    u2=Column('p2',Float())
    u3=Column('p3',Float())
    r1=Column('m1',Float())
    r2=Column('m2',Float())
    r3=Column('m3',Float())
    
class PointDisp(Base):
    __tablename__='point_disps'
    point_name=Column('point_name',String(32),ForeignKey('points.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    u1=Column('u1',Float())
    u2=Column('u2',Float())
    u3=Column('u3',Float())
    r1=Column('r1',Float())
    r2=Column('r2',Float())
    r3=Column('r3',Float())

class PointMass( Base):
    __tablename__='point_masses'
    point_name=Column('point_name',String(32),ForeignKey('points.name'),primary_key=True)
    u1=Column('u1',Float())
    u2=Column('u2',Float())
    u3=Column('u3',Float())
    r1=Column('r1',Float())
    r2=Column('r2',Float())
    r3=Column('r3',Float())

class PointSpring(Base):
    __tablename__='point_springs'
    point_name=Column('point_name',String(32),ForeignKey('points.name'),primary_key=True)
    u1=Column('u1',Float())
    u2=Column('u2',Float())
    u3=Column('u3',Float())
    r1=Column('r1',Float())
    r2=Column('r2',Float())
    r3=Column('r3',Float())
    
class Curve(Base):
    __tablename__='curves'
    curve_name=Column('curve_name',String(32),primary_key=True)
    t=Column('t',Float())
    value=Column('value',Float())
    
class Spectrum(Base):
    __tablename__='spectrums'
    spectrum_name=Column('spectrum_name',String(32),primary_key=True)
    code=Column('code',String(32))
    param0=Column('param0',Float())
    param1=Column('param1',Float())
    param2=Column('param2',Float())
    param3=Column('param3',Float())
    param4=Column('param4',Float())
    param5=Column('param5',Float())
    param6=Column('param6',Float())
    param7=Column('param7',Float())
    param8=Column('param8',Float())
    param9=Column('param9',Float())
    param10=Column('param10',Float())
    param11=Column('param11',Float())

class Frame(Base):
    __tablename__='frames'
    name=Column('name',String(32),primary_key=True)
    section_name=Column('section_name',String(32),ForeignKey('frame_sections.name'))
    
    pt0_name=Column('pt0_name',String(32),ForeignKey('points.name'),nullable=False)
    pt1_name=Column('pt1_name',String(32),ForeignKey('points.name'),nullable=False)
    pt0 = relationship("Point", foreign_keys=[pt0_name])
    pt1 = relationship("Point", foreign_keys=[pt1_name])
    
    order=Column('order',String(2),default='01')
    uuid=Column('uuid',String(32),nullable=False)
    
    #1 to 1
    frame_axis=relationship('FrameAxis',backref=backref('frame',uselist=False))
    frame_release=relationship('FrameRelease',backref=backref('frame',uselist=False))
    frame_load_distributed=relationship('FrameLoadDistributed',backref=backref('frame',uselist=False))
    frame_load_concentrated=relationship('FrameLoadConcentrated',backref=backref('frame',uselist=False))
    frame_load_strain=relationship('FrameLoadStrain',backref=backref('frame',uselist=False))
    frame_load_temperature=relationship('FrameLoadTemperature',backref=backref('frame',uselist=False))
    
    def __repr__(self):
        return '%s<%r>'%(self.__class__.__name__,self.name)

class FrameAxis(Base):
    __tablename__='frame_axis'
    frame_name=Column('frame_name',String(32),ForeignKey('frames.name'),primary_key=True)
    x=Column('x',Float())
    y=Column('y',Float())
    z=Column('z',Float())
    
class FrameRelease(Base):
    __tablename__='frame_releases'
    frame_name=Column('frame_name',String(32),ForeignKey('frames.name'),primary_key=True)
    u01=Column('u01',Float())
    u02=Column('u02',Float())
    u03=Column('u03',Float())
    r01=Column('r01',Float())
    r02=Column('r02',Float())
    r03=Column('r03',Float())
    u11=Column('u11',Float())
    u12=Column('u12',Float())
    u13=Column('u13',Float())
    r11=Column('r11',Float())
    r12=Column('r12',Float())
    r13=Column('r13',Float())

class FrameLoadDistributed(Base):
    __tablename__='frame_load_distributeds'
    frame_name=Column('frame_name',String(32),ForeignKey('frames.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    p01=Column('p01',Float())
    p02=Column('p02',Float())
    p03=Column('p03',Float())
    m01=Column('m01',Float())
    m02=Column('m02',Float())
    m03=Column('m03',Float())
    p11=Column('p11',Float())
    p12=Column('p12',Float())
    p13=Column('p13',Float())
    m11=Column('m11',Float())
    m12=Column('m12',Float())
    m13=Column('m13',Float())

class FrameLoadConcentrated(Base):
    __tablename__='frame_load_concentrated'
    frame_name=Column('frame_name',String(32),ForeignKey('frames.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    loc=Column('loc',Float())
    p1=Column('p1',Float())
    p2=Column('p2',Float())
    p3=Column('p3',Float())
    m1=Column('m1',Float())
    m2=Column('m2',Float())
    m3=Column('m3',Float())

class FrameLoadStrain(Base):
    __tablename__='frame_load_strain'
    frame_name=Column('frame_name',String(32),ForeignKey('frames.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    strain=Column('strain',Float())
    
class FrameLoadTemperature(Base):
    __tablename__='frame_laod_teamperature'
    frame_name=Column('frame_name',String(32),ForeignKey('frames.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    T=Column('T',Float())

class Area(Base):
    __tablename__='areas'
    name=Column('name',String(32),primary_key=True)
    section_name=Column('section_name',String(32),ForeignKey('area_sections.name'))

    pt0_name=Column('pt0_name',String(32),ForeignKey('points.name'),nullable=False)
    pt1_name=Column('pt1_name',String(32),ForeignKey('points.name'),nullable=False)
    pt2_name=Column('pt2_name',String(32),ForeignKey('points.name'),nullable=False)
    pt3_name=Column('pt3_name',String(32),ForeignKey('points.name'),nullable=False)
    pt0 = relationship("Point", foreign_keys=[pt0_name])
    pt1 = relationship("Point", foreign_keys=[pt1_name])    
    pt2 = relationship("Point", foreign_keys=[pt2_name])
    pt3 = relationship("Point", foreign_keys=[pt3_name])  
    
    uuid=Column('uuid',String(32),nullable=False)   
    
    #1 to 1
    area_axis=relationship('AreaAxis',backref=backref('area',uselist=False))
    area_load_to_frame=relationship('AreaLoadToFrame',backref=backref('area',uselist=False))
    area_load_distributed=relationship('AreaLoadDistributed',backref=backref('area',uselist=False))
    area_load_strain=relationship('AreaLoadStrain',backref=backref('area',uselist=False))
    area_load_temperature=relationship('AreaLoadTemperature',backref=backref('area',uselist=False))
    
class AreaAxis(Base):
    __tablename__='area_axis'
    area_name=Column('area_name',String(32),ForeignKey('areas.name'),primary_key=True)
    x0=Column('x0',Float())
    y0=Column('y0',Float())
    z0=Column('z0',Float())
    x1=Column('x1',Float())
    y1=Column('y1',Float())
    z1=Column('z1',Float())
    
class AreaLoadToFrame(Base):
    __tablename__='area_load_to_frame'
    area_name=Column('area_name',String(32),ForeignKey('areas.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    p1=Column('p1',Float())
    p2=Column('p2',Float())
    p3=Column('p3',Float())
    
class AreaLoadDistributed(Base):
    __tablename__='area_load_distributeds'
    area_name=Column('area_name',String(32),ForeignKey('areas.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    pass

class AreaLoadStrain(Base):
    __tablename__='area_load_strains'
    area_name=Column('area_name',String(32),ForeignKey('areas.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    pass

class AreaLoadTemperature(Base):
    __tablename__='area_laod_teamperature'
    area_name=Column('area_name',String(32),ForeignKey('areas.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    T=Column('T',Float())

class RunLoadCase(Base):
    __tablename__='run_loadcase'
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    run=Column('run',Boolean())

class ResultPointDisplacement(Base):
    __tablename__='result_point_displacement'
    point_name=Column('point_name',String(32),ForeignKey('points.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    u1=Column('u1',Float())
    u2=Column('u2',Float())
    u3=Column('u3',Float())
    r1=Column('r1',Float())
    r2=Column('r2',Float())
    r3=Column('r3',Float())


class ResultPointReaction(Base):
    __tablename__='result_point_reactions'
    point_name=Column('point_name',String(32),ForeignKey('points.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    p1=Column('p1',Float())
    p2=Column('p2',Float())
    p3=Column('p3',Float())
    m1=Column('m1',Float())
    m2=Column('m2',Float())
    m3=Column('m3',Float())


class ResultFrameForce(Base):
    __tablename__='result_frame_forces'
    frame_name=Column('frame_name',String(32),ForeignKey('frames.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    segment=Column('segment',Integer(),primary_key=True)
    p01=Column('p01',Float())
    p02=Column('p02',Float())
    p03=Column('p03',Float())
    m01=Column('m01',Float())
    m02=Column('m02',Float())
    m03=Column('m03',Float())
    p11=Column('p11',Float())
    p12=Column('p12',Float())
    p13=Column('p13',Float())
    m11=Column('m11',Float())
    m12=Column('m12',Float())
    m13=Column('m13',Float())

class ResultAreaStress(Base):
    __tablename__='result_area_stresses'
    area_name=Column('area_name',String(32),ForeignKey('frames.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    s11=Column('s11',Float())
    s12=Column('s12',Float())
    s21=Column('s21',Float())
    s22=Column('s22',Float())
    t12=Column('t12',Float())
    t21=Column('t21',Float())
    
class ResultModalPeriod(Base):
    __tablename__='result_modal_period'
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    order=Column('order',Integer(),primary_key=True)
    omega=Column('omega',Float())
    period=Column('period',Float())
    frequency=Column('frequency',Float())

class ResultModalDisplacement(Base):
    __tablename__='result_modal_displacement'
    point_name=Column('point_name',String(32),ForeignKey('points.name'),primary_key=True)
    loadcase_name=Column('loadcase_name',String(32),ForeignKey('loadcases.name'),primary_key=True)
    order=Column('order',Integer(),primary_key=True)
    u1=Column('u1',Float())
    u2=Column('u2',Float())
    u3=Column('u3',Float())
    r1=Column('r1',Float())
    r2=Column('r2',Float())
    r3=Column('r3',Float())
    
#class DesignSteelSetting(Base):
#    __tablename__='design_steel_settings'
#
#
#class DesignSteelMemberSetting(Base):
#    __tablename__='design_steel_member_settings'
#
#
#class DesignResult(Base):
#    __tablename__='design_results'


