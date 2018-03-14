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
from sqlalchemy.orm import relationship

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
    __obj_id=uuid.uuid1()
    uuid=Column('uuid',String(32),default=__obj_id,primary_key=True)
    name=Column('name',String(32),default=__obj_id)
    gamma=Column('gamma',Float())
    type=Column('type',String(32))
    isotripic_elastic=relationship('IsotropicElastic',backref='materials')

class IsotropicElastic(Base):
    __tablename__='isotropic_elastics'
    material=Column('material',ForeignKey('materials.uuid'),primary_key=True)
    E=Column('E',Float())
    mu=Column('mu',Float())

class FrameSection(Base):
    __tablename__='frame_sections'
    __obj_id=uuid.uuid1()
    uuid=Column('uuid',String(32),default=__obj_id,primary_key=True)
    name=Column('name',String(32),default=__obj_id)
    shape=Column('shape',String(32))
    material=('material',ForeignKey('materials.name'))
    size_0=Column('size_0',Float())
    size_1=Column('size_1',Float())
    size_2=Column('size_2',Float())
    size_3=Column('size_3',Float())
    size_4=Column('size_4',Float())
    size_5=Column('size_5',Float())
    size_6=Column('size_6',Float())
    size_7=Column('size_7',Float())
    
class SDSection(Base):
    __tablename__='SD_sections'
    frame_section=Column('frame_section',
                         ForeignKey('frame_sections.uuid'),
                         primary_key=True)
    material=('material',ForeignKey('materials.uuid'))   

class AreaSection(Base):
    __tablename__='area_sections'
    __obj_id=uuid.uuid1()
    uuid=Column('uuid',String(32),default=__obj_id,primary_key=True)
    name=Column('name',String(32),default=__obj_id)
    material=('material',ForeignKey('materials.uuid'))
    size_0=Column('size_0',Float())
    size_1=Column('size_1',Float())
    size_2=Column('size_2',Float())

class LoadCase(Base):
    __tablename__='loadcases'
    __obj_id=uuid.uuid1()
    uuid=Column('uuid',String(32),default=__obj_id,primary_key=True)
    name=Column('name',String(32),default=__obj_id)
    case_type=Column('case_type',String(16))
    static_linear_setting=relationship('LoadCaseStaticLinearSetting',backref='loadcase')

class LoadCaseStaticLinearSetting(Base):
    __tablename__='laodcase_static_linear_settings'
    lc=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)

class LoadCaseModalSetting(Base):
    __tablename__='loadcase_modal_settings'
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    method=Column('method',String(8))
    modal_num=Column('modal_num',Integer())
    tolerance=Column('tolerance',Float)
    iteration=Column('iteration',Integer())

class LoadCase2ndSetting(Base):
    __tablename__='loadcase_2nd_settings'
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    method=Column('method',String(8))
    plc=Column('plc',ForeignKey('loadcases.uuid'))

class LoadCase3ndSetting(Base):
    __tablename__='loadcase_3nd_settings'
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    method=Column('method',String(8))
    plc=Column('plc',ForeignKey('loadcases.uuid'))
    
class LoadCaseResponseSpectrumSetting(Base):
    __tablename__='loadcase_response_spectrum_settings'
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    method=Column('method',String(8))

class LoadCaseTimeHistorySetting(Base):
    __tablename__='loadcase_time_history_settings'
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    method=Column('method',String(8))
    
class Point(Base):
    __tablename__='points'
    __obj_id=uuid.uuid1()
    uuid=Column('uuid',String(32),default=__obj_id,primary_key=True)
    name=Column('name',String(32),default=__obj_id)
    x=Column('x',Float)
    y=Column('y',Float)
    z=Column('z',Float)

class PointRestraint(Base):
    __tablename__='point_restraints'
    point=Column('point',ForeignKey('points.uuid'),primary_key=True)
    res_u1=Column('res_u1',Boolean())
    res_u2=Column('res_u2',Boolean())
    res_u3=Column('res_u3',Boolean())
    res_r1=Column('res_r1',Boolean())
    res_r2=Column('res_r2',Boolean())
    res_r3=Column('res_r3',Boolean())

class PointLoad(Base):
    __tablename__='pointloads'
    point=Column('point',ForeignKey('points.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    u1=Column('u1',Boolean())
    u2=Column('u2',Boolean())
    u3=Column('u3',Boolean())
    r1=Column('r1',Boolean())
    r2=Column('r2',Boolean())
    r3=Column('r3',Boolean())


class PointDisp(Base):
    __tablename__='point_disps'
    point=Column('point',ForeignKey('points.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    u1=Column('u1',Float())
    u2=Column('u2',Float())
    u3=Column('u3',Float())
    r1=Column('r1',Float())
    r2=Column('r2',Float())
    r3=Column('r3',Float())


class PointMass( Base):
    __tablename__='point_masses'
    point=Column('uuid',ForeignKey('points.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    u1=Column('u1',Float())
    u2=Column('u2',Float())
    u3=Column('u3',Float())
    r1=Column('r1',Float())
    r2=Column('r2',Float())
    r3=Column('r3',Float())

class PointSpring(Base):
    __tablename__='point_springs'
    point=Column('uuid',ForeignKey('points.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    u1=Column('u1',Float())
    u2=Column('u2',Float())
    u3=Column('u3',Float())
    r1=Column('r1',Float())
    r2=Column('r2',Float())
    r3=Column('r3',Float())

class Frame(Base):
    __tablename__='frames'
    __obj_id=uuid.uuid1()
    uuid=Column('uuid',String(32),default=__obj_id,primary_key=True)
    name=Column('name',String(32),default=__obj_id)
    section=Column('section',ForeignKey('frame_sections.uuid'))
    point_0=Column('point_0',ForeignKey('points.uuid'))
    point_1=Column('point_1',ForeignKey('points.uuid'))

class FrameAttribReleas(Base):
    __tablename__='frame_attrib_releases'
    frame=Column('frame',ForeignKey('frames.uuid'),primary_key=True)
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

class FrameLoadDistrib(Base):
    __tablename__='frame_load_distribs'
    frame=Column('frame',ForeignKey('frames.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
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
    frame=Column('frame',ForeignKey('frames.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    loc=Column('loc',Float())
    p1=Column('p1',Float())
    p2=Column('p2',Float())
    p3=Column('p3',Float())
    m1=Column('m1',Float())
    m2=Column('m2',Float())
    m3=Column('m3',Float())

class FrameLoadStrain(Base):
    __tablename__='frame_load_strain'
    frame=Column('frame',ForeignKey('frames.uuid'),primary_key=True)
    T=Column('strain',Float())
    
class FrameLoadTemperature(Base):
    __tablename__='frame_laod_teamperature'
    frame=Column('frame',ForeignKey('frames.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    T=Column('T',Float())

class Area(Base):
    __tablename__='areas'
    __obj_id=uuid.uuid1()
    uuid=Column('uuid',String(32),default=__obj_id,primary_key=True)
    name=Column('name',String(32),default=__obj_id)
    pass

class AreaLoad2Frame(Base):
    __tablename__='area_load_2_frame'
    area=Column('area',ForeignKey('areas.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    p1=Column('p1',Float())
    p2=Column('p2',Float())
    p3=Column('p3',Float())
    
class AreaLoadDistrib(Base):
    __tablename__='area_load_distribs'
    area=Column('area',ForeignKey('areas.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)

    pass

class AreaLoadStrain(Base):
    __tablename__='area_load_strains'
    area=Column('area',ForeignKey('areas.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    pass

class RunLoadCase(Base):
    __tablename__='run_loadcase'
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    run=Column('run',Boolean())

class ResultPointDisplacement(Base):
    __tablename__='result_point_displacement'
    point=Column('point',ForeignKey('points.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    u1=Column('u1',Boolean())
    u2=Column('u2',Boolean())
    u3=Column('u3',Boolean())
    r1=Column('r1',Boolean())
    r2=Column('r2',Boolean())
    r3=Column('r3',Boolean())


class ResultPointReaction(Base):
    __tablename__='result_point_reactions'
    point=Column('uuid',ForeignKey('points.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    u1=Column('u1',Boolean())
    u2=Column('u2',Boolean())
    u3=Column('u3',Boolean())
    r1=Column('r1',Boolean())
    r2=Column('r2',Boolean())
    r3=Column('r3',Boolean())


class ResultFrameForce(Base):
    __tablename__='result_frame_forces'
    frame=Column('frame',ForeignKey('frames.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
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

class ResultAreaStresse(Base):
    __tablename__='result_area_stresses'
    area=Column('area',ForeignKey('frames.uuid'),primary_key=True)
    loadcase=Column('loadcase',ForeignKey('loadcases.uuid'),primary_key=True)
    s11=Column('s11',Float())
    s12=Column('s12',Float())
    s21=Column('s21',Float())
    s22=Column('s22',Float())
    t12=Column('t12',Float())
    t21=Column('t21',Float())

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


