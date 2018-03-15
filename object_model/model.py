# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 19:52:26 2018

@author: HZJ
@E-mail: zhuoju36@hotmail.com
"""
import os
import shutil
import time

from sqlalchemy import create_engine
import sqlalchemy.orm as o
from datetime import datetime

from .orm import Base,Config,\
Material,IsotropicElastic,\
Point,Frame,Area,\
FrameSection,\
LoadCase,LoadCaseStaticLinearSetting,\
PointRestraint,PointLoad,FrameLoadDistributed,FrameLoadConcentrated,FrameLoadStrain,FrameLoadTemperature

from object_model.frame_section import Pipe,Circle,HollowBox,ISection

from fe_model import Model as FEModel
from fe_model.node import Node
from fe_model.element import Beam

from fe_solver.static import solve_linear

import logger as log

class Model():
    def __init__(self):
        pass
#        #materials
#        self.__materials={}
#        
#        #sections
#        self.__frame_sections={}
#        self.__area_sections={}
#        
#        #members
#        self.__points={}
#        self.__cables={}
#        self.__frames={}
#        self.__areas={}
#        
#        #group
#        self.__groups={}
#        
#        #loadcase and combinations
#        self.__loadcases={}
#        self.__combinations={}
#        
#        #member loads
#        self.__load_pt={}
#        self.__load_frm_distrib={}
#        self.__load_frm_pt={}
#        self.__load_frm_tmpt={}
#        self.__load_frm_strain={}
#        self.__load_area_distrb={}
#        self.__load_area_tmpt={}
#        self.__load_area_strain={}
#        
#        #structure
#        self.__curves={}
#        self.__load_spectrum={}
#        self.__load_time_history={}

    def create(self,database):
        """
        params:
            database: str. Database to be created. The path should be included
        """
        assert(database[-3:]=='.db')
        #initialize
        engine=create_engine('sqlite:///'+database)
        Base.metadata.create_all(engine)
        Session=o.sessionmaker(bind=engine)
        session=Session()
        
        #configurations
        config=Config()
        config.project_name='dev'
        config.author='HZJ'
        config.program_version='0.0.1'
        config.create_time=datetime.now()
        
        session.add(config)
        session.commit()
        
    def open(self,database):
        """
        params:
            database: str. Database to be opered. The path should be included
        """
        assert(database[-3:]=='.db')
        operate_db=database[:-3]+'_op.db'
        shutil.copy(database,operate_db)
        engine=create_engine('sqlite:///'+operate_db) #should be run in memory in the future
        Session=o.sessionmaker(bind=engine)
        self.session=Session()
        self.__operate_db=operate_db
        self.__storage_db=database
        
    def save(self):
        self.session.commit()
        shutil.copy(self.__operate_db,self.__storage_db)
        
    def close(self):
        self.session.close()
        if os.path.exists(self.__operate_db):
            os.remove(self.__operate_db)
            
    def add_material(self,name,gamma,mat_type,**kwargs):
        """
        Add material to model, if the name already exists, an exception will be raised
        param:
            name: name of material.
            gamma: density.
            mat_type: 'isotropic_elastic','...'
        return:
            boolean, status of success.
        optional:
            if type is 'isoelastic', the following parameters are available:
            E: float, elastic modulus
            mu: float, Poisson ratio
        """
        if self.session.query(Material).filter_by(name=name).first()!=None:
            raise Exception('Name already exists!')
        mat=Material()
        mat.name=name
        mat.gamma=gamma
        mat.type=mat_type
        if mat_type=='isotropic_elastic':
            iso_elastic=IsotropicElastic()
            iso_elastic.material_name=mat.name
            iso_elastic.E=kwargs['E']
            iso_elastic.mu=kwargs['mu']
            self.session.add(iso_elastic)
        self.session.add(mat)
        self.session.commit()
        return True
    
    def add_frame_section(self,name,material,type,size):
        """
        Add frame section to model, if the name already exists, an exception will be raised.
        param:
            name: str. name of the section.
            material: str, name of material.
            type:
                'O':pipe,
                'o':circle
                'I':I-profile
                'B':hollow-box
                'L':angle
                'T':T-profile
                'C':C-profile
                'Z':Z-profile
            size:
            if type is 'p', the following parameters are available:
                d: float, diameter
                t: float, wall thickness
            if type is 'I', the following parameters are available:
                h,b,tw,tf: float
            if type is 'B', the following parameters are available:
                h,b,tw,tf: float
            if type is 'L', the following parameters are available:
                h,b,tw,tf: float
            if type is 'T', the following parameters are available:
                h,b,tw,tf: float
            if type is 'C', the following parameters are available:
                h,b,tw,tf: float
            if type is 'Z', the following parameters are available:
                h,b,tw,tf: float
        return:
            boolean, status of success.
        """
        if self.session.query(FrameSection).filter_by(name=name).first()!=None:
            raise Exception('Name already exists!')
        frmsec=FrameSection()
        frmsec.name=name
        frmsec.material_name=material
        frmsec.type=type
        sec=None
        if type=='o':
            assert len(size)==1
            sec=Circle(None,size[0])
        elif type=='O':
            assert len(size)==2
            sec=Pipe(None,size[0],size[1])
        elif type=='I':
            assert len(size)==4
            sec=ISection(None,size[0],size[1],size[2],size[3])
        else:####should be refined!!
            assert len(size)==4
            sec=HollowBox(None,size[0],size[1])
        
        frmsec.size=size
        frmsec.A=sec.A
        frmsec.J=sec.J
#        frmsec.S2=sec.S2
#        frmsec.S3=sec.S3
        frmsec.I2=sec.I22
        frmsec.I3=sec.I33
        self.session.add(frmsec)
        self.session.commit()
        return True  
    
    def add_area_section(self):
        pass
    
    def add_loadcase(self,name,case_type,**kwargs):
        """
        Add material to model, if the name already exists, an exception will be raised
        param:
            name: name of material.
            type: 'static-linear','2nd','3rd','modal','spectrum','th','buckle'
        return:
            boolean, status of success.
        optional:
            if type is '1st', the following parameters are available:
            E: float, elastic modulus
            mu: float, Poisson ratio
        """
        if self.session.query(LoadCase).filter_by(name=name).first()!=None:
            raise Exception('Name already exists!')
        lc=LoadCase()
        lc.name=name
        lc.case_type=case_type
        if case_type=='1st':
            setting=LoadCaseStaticLinearSetting
            setting.lc=lc.name
        self.session.add(lc)
        self.session.commit()
        return True

    def add_point(self,name,x,y,z):
        """
        Add point object to model, if the name already exists, an exception will be raised.
        if a point in same location exists, the name of the point will be returned.
        param:
            x,y,z: float-like, coordinates.
        return:
            bool, status of success
        """
        if self.session.query(LoadCase).filter_by(name=name).first()!=None:
            raise Exception('Name already exists!')
        pt=Point()
        pt.name=name
        pt.x=x
        pt.y=y
        pt.z=z
        self.session.add(pt)
        self.session.commit()
        return(True)
        
        
    def add_frame(self,name,pt1,pt2,section):
        """
        Add frame object to model, if the name already exists, an exception will be raised.
        if a frame connecting same points exists, the name of the point will be returned.
        param:
            pt1,pt2: name of the end points.
        return:
            bool, status of success.
        """
        if self.session.query(Frame).filter_by(name=name).first()!=None:
            raise Exception('Name already exist!')
        frm=Frame()
        if pt1<pt2:
            order='01'
            frm.pt0_name=pt1
            frm.pt1_name=pt2
            frm.order=order
        elif pt1>pt2:
            order='10'
            frm.pt0_name=pt2
            frm.pt1_name=pt1
            frm.order=order
        else:
            raise Exception('Two points should not be the same!')
        frm.section_name=section
        frm.name=name
        self.session.add(frm)
        self.session.commit()
        return True

    def get_point(self,name):
        """
        params:
            name: str
        returns:
            point object if exist
        """
        return self.__points[name]
    
    def get_frame(self,name):
        """
        params:
            name: str
        returns:
            frame object if exist
        """
        return self.__frames[name]
    
    def get_frame_section(self,name):
        """
        params:
            name: str
        returns:
            frame section object if exist
        """
        return self.__frame_sections[name]
        
    def set_point_restraint(self,point,restraints):
        """
        params:
            point: str, name of point
            restraints: bool, list of 6 to set restraints
        return:
            status of success
        """
        assert len(restraints)==6
        res=self.session.query(PointRestraint).filter_by(point_name=point).first()
        if res is None:
            res=PointRestraint()
        res.point_name=point
        res.u1=restraints[0]
        res.u2=restraints[1]
        res.u3=restraints[2]
        res.r1=restraints[3]
        res.r2=restraints[4]
        res.r3=restraints[5]
        self.session.add(res)
        self.session.commit()
        return True
                
    def set_point_load(self,point,loadcase,load):
        """
        params:
            point: str, name of point.
            loadcase: str, name of loadcase. 
            load: float, list of 6 to set restraints.
        return:
            status of success.
        """
        assert len(load)==6
        ld=self.session.query(PointLoad).filter_by(point_name=point,loadcase_name=loadcase).first()
        if ld is None:
            ld=PointLoad()
        ld.point_name=point
        ld.loadcase_name=loadcase
        ld.u1=load[0]
        ld.u2=load[1]
        ld.u3=load[2]
        ld.r1=load[3]
        ld.r2=load[4]
        ld.r3=load[5]
        self.session.add(ld)
        self.session.commit()
        return True
        
    def run(self,lcs):
        """
        Run the model with loadcases
        params:
            lcs: list of str, specify load cases to run.
        return:
            None.
        """
        self.fe_model.assemble_KM()
        self.fe_model.assemble_boundary(mode='KM')
        for lc in lcs:
            loadcase=self.session.query(LoadCase).filter_by(name=lc).first()
            if loadcase.case_type=='static-linear':
                log.info('Solving static linear case %s...'%lc)
                self.apply_load(lc)
                self.fe_model.assemble_f()
                self.fe_model.assemble_boundary(mode='f')
                res=solve_linear(self.fe_model)
                print(res)
                log.info('Finished case %s.'%lc)
            else:
                pass
    
    def mesh(self):
        femodel=FEModel()
        points=self.session.query(Point).all()
        frames=self.session.query(Frame).all()
        areas=self.session.query(Area).all()
        pn_map={} #item-item map, one point to one node
        fb_map={} #item-list map, one frame can be meshed to many beams
        am_map={} #item-list map, one area can be meshed to many membranes
        ap_map={} #item-list map, one area can be meshed to many plates
        as_map={} #item-list map, one area can be meshed to many shells
        
        for pt in points:
            res=femodel.add_node(Node(pt.x,pt.y,pt.z))
            pn_map[pt.name]=res
        for frm in frames:
            node0=femodel.nodes[pn_map[frm.pt0_name]]
            node1=femodel.nodes[pn_map[frm.pt1_name]]
            E=frm.section.material.isotropic_elastic.E
            mu=frm.section.material.isotropic_elastic.mu
            A=frm.section.A
            J=frm.section.J
            I2=frm.section.I2
            I3=frm.section.I3
            J=frm.section.J
            rho=frm.section.material.gamma ####should be revised
            if frm.order=='01':
                res=femodel.add_beam(Beam(node0,node1,E, mu, A, I2, I3, J, rho))
            elif frm.order=='10':
                res=femodel.add_beam(Beam(node1,node0,E, mu, A, I2, I3, J, rho))
            fb_map[frm.name]=[res]
        for area in areas:
            am_map=None
            ap_map=None
            as_map=None
            pass
        
        restraints=self.session.query(PointRestraint).all()
        for res in restraints:
            disp=[0 if res.u1 else None,
                  0 if res.u2 else None,
                  0 if res.u3 else None,
                  0 if res.r1 else None,
                  0 if res.r2 else None,
                  0 if res.r3 else None]
            femodel.set_node_displacement(pn_map[res.point_name],disp)
                
        self.fe_model=femodel
        self.pn_map=pn_map
        self.fb_map=fb_map
        self.am_map=am_map
        self.ap_map=ap_map
        self.as_map=as_map

    def apply_load(self,lc):
        pn_map=self.pn_map
        fb_map=self.fb_map
        am_map=self.am_map
        ap_map=self.ap_map
        as_map=self.as_map

        point_loads=self.session.query(PointLoad).filter_by(loadcase_name=lc).all()
        frame_load_distributeds=self.session.query(FrameLoadDistributed).filter_by(loadcase_name=lc).all()
        frame_load_concentrateds=self.session.query(FrameLoadConcentrated).filter_by(loadcase_name=lc).all()
        frame_load_strains=self.session.query(FrameLoadStrain).filter_by(loadcase_name=lc).all()
        frame_load_temperatures=self.session.query(FrameLoadTemperature).filter_by(loadcase_name=lc).all()
        for load in point_loads:
            self.fe_model.set_node_force(pn_map[load.point_name],
                                         [load.u1,load.u2,load.u3,load.r1,load.r2,load.r3])
        
        for load in frame_load_distributeds:
            pass
        
        for load in frame_load_concentrateds:
            pass
        
        for load in frame_load_strains:
            pass
        
        for load in frame_load_temperatures:
            pass
            
        
    def import_model():
        pass
    
    def import_dxf():
        pass
