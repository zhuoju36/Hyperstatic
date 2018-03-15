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

#from .orm import Base,Config,\
#Material,IsotropicElastic,\
#Point,Frame,Area,\
#FrameSection,\
#LoadCase,LoadCaseStaticLinearSetting,LoadCase\
#PointRestraint,PointLoad,FrameLoadDistributed,FrameLoadConcentrated,FrameLoadStrain,FrameLoadTemperature
from .orm import *

from object_model.frame_section import Pipe,Circle,HollowBox,ISection

from fe_model import Model as FEModel
from fe_model.node import Node
from fe_model.element import Beam

from fe_solver.static import solve_linear

import logger as log

class Model():
    def __init__(self):
        self.locked=False

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
        
        
    def scale(self):
        """
        returns the scale factor of current model.
        """
        config=self.session.query(Config).first()
        scale={}
        if config.unit=='N_m_C':
            scale['F']=1
            scale['L']=1
            scale['T']=1
        elif config.unit=='N_mm_C':
            scale['F']=1
            scale['L']=1e-3
            scale['T']=1
        elif config.unit=='kN_m_C':
            scale['F']=1e3
            scale['L']=1
            scale['T']=1
        elif config.unit=='kN_mm_C':
            scale['F']=1e3
            scale['L']=1e-3
            scale['T']=1        
        return scale
        
    def save(self):
        self.session.commit()
        shutil.copy(self.__operate_db,self.__storage_db)
        
    def close(self):
        self.session.close()
        if os.path.exists(self.__operate_db):
            os.remove(self.__operate_db)
            
    def set_project_name(self,name):
        """
        params:
            name: str, project name, no more than 32 chars
        """
        assert(type(name)==str and len(name)<32)
        config=self.session.query(Config).first()
        config.project_name=name
        self.session.add(config)
        self.session.commit()
    
    def set_author(self,author):
        """
        params:
            author: str, project name, no more than 32 chars
        """
        assert(type(author)==str and len(author)<32)
        config=self.session.query(Config).first()
        config.author=author
        self.session.add(config)
        self.session.commit()
    
    def set_unit(self,unit):
        """
        params:
            unit: str, should be 'N_m_C','N_mm_C','kN_m_C' or 'kN_mm_C'
        """
        assert(unit in ['N_m_C','N_mm_C','kN_m_C','kN_mm_C'])
        config=self.session.query(Config).first()
        config.unit=unit
        self.session.add(config)
        self.session.commit()
    
    def set_description(self,text):
        """
        params:
            text: str, description.
        """
        assert(type(text)==str)
        config=self.session.query(Config).first()
        config.description=description
        self.session.add(config)
        self.session.commit()
            
    def add_material(self,name,rho,mat_type,**kwargs):
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
        mat.rho=rho
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
            if type is 'O', the following parameters are available:
                d: float, diameter
                t: float, wall thickness
            if type is 'o', the following parameters are available:
                d: float, diameter
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
        assert(type in 'OoIBLTCZ' and len(type)==1)
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
        elif type=='L':####should be refined!!
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
    
    def add_loadcase(self,name,case_type,weight_factor=0,**kwargs):
        """
        Add material to model, if the name already exists, an exception will be raised
        param:
            name: name of material.
            type: 'static-linear','2nd','3rd','modal','response-spectrum','time-history','buckling'
        return:
            boolean, status of success.
        optional:
            [weight_factor]: factor of self weight.
        **kwargs:
            if type is '1st', the following parameters are available:
                E: float, elastic modulus
                mu: float, Poisson ratio
        """
        if self.session.query(LoadCase).filter_by(name=name).first()!=None:
            raise Exception('Name already exists!')
        lc=LoadCase()
        lc.name=name
        lc.case_type=case_type
        lc.weight_factor=weight_factor
        if case_type=='static-linear':
            setting=LoadCaseStaticLinearSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='2nd':
            setting=LoadCase2ndSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='3nd':
            setting=LoadCase3ndSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='modal':
            setting=LoadCaseModalSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='response-spectrum':
            setting=LoadCaseResponseSpectrumSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='time-history':
            setting=LoadCaseTimeHistorySetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='buckling':
            setting=LoadCaseBucklingSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        self.session.add(lc)
        self.session.commit()
        return True
        
    def set_loadcase_static_linear(self):
        pass
    
    def set_loadcase_2nd(self):
        pass

    def set_loadcase_3rd(self):
        pass
    
    def set_loadcase_modal(self):
        pass
    
    def set_loadcase_response_spectrum(self):
        pass
    
    def set_loadcase_time_history(self):
        pass
    
    def set_loadcase_buckling(self):
        pass

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
        
    def set_point(self,name,x,y,z):
        pass
        
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
        
    def set_frame_section(self,name,section):
        pass
    
    def set_frame_mesh(self,frame):
        pass
    
    
    def get_point(self,name):
        """
        params:
            name: str
        returns:
            point object if exist
        """
        pass
    
    def get_frame(self,name):
        """
        params:
            name: str
        returns:
            frame object if exist
        """
        pass
    
    def get_frame_section(self,name):
        """
        params:
            name: str
        returns:
            frame section object if exist
        """
        pass
        
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
        scale=self.scale()
        
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
            res=femodel.add_node(Node(pt.x*scale['L'],pt.y*scale['L'],pt.z*scale['L']))
            pn_map[pt.name]=res
        for frm in frames:
            node0=femodel.nodes[pn_map[frm.pt0_name]]
            node1=femodel.nodes[pn_map[frm.pt1_name]]
            E=frm.section.material.isotropic_elastic.E*(scale['F']*scale['L']**-2)
            mu=frm.section.material.isotropic_elastic.mu
            A=frm.section.A*(scale['L']**2)
            J=frm.section.J*(scale['L']**4)
            I2=frm.section.I2*(scale['L']**4)
            I3=frm.section.I3*(scale['L']**4)
            rho=frm.section.material.rho*(scale['F']*scale['L']**-4)
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
        scale=self.scale()
        
        pn_map=self.pn_map
        fb_map=self.fb_map
        am_map=self.am_map
        ap_map=self.ap_map
        as_map=self.as_map

        loadcase=self.session.query(LoadCase).filter_by(name=lc).first()
        
        point_loads=self.session.query(PointLoad).filter_by(loadcase_name=lc).all()
        frame_load_distributeds=self.session.query(FrameLoadDistributed).filter_by(loadcase_name=lc).all()
        frame_load_concentrateds=self.session.query(FrameLoadConcentrated).filter_by(loadcase_name=lc).all()
        frame_load_strains=self.session.query(FrameLoadStrain).filter_by(loadcase_name=lc).all()
        frame_load_temperatures=self.session.query(FrameLoadTemperature).filter_by(loadcase_name=lc).all()  
        
        for load in point_loads:
            self.fe_model.set_node_force(pn_map[load.point_name],
                                         [load.u1*scale['F'],
                                          load.u2*scale['F'],
                                          load.u3*scale['F'],
                                          load.r1*scale['F']*scale['L'],
                                          load.r2*scale['F']*scale['L'],
                                          load.r3*scale['F']*scale['L']],append=True)
        
        for load in frame_load_distributeds:
            pass
        
        for load in frame_load_concentrateds:
            pass
        
        for load in frame_load_strains:
            pass
        
        for load in frame_load_temperatures:
            pass
        
        #self weight
        for beam in self.fe_model.beams.values():
            f=-beam.mass*9.81*scale['F']/2*loadcase.weight_factor
            self.fe_model.set_node_force(beam.nodes[0].hid,[0,0,f,0,0,0],append=True)
            self.fe_model.set_node_force(beam.nodes[1].hid,[0,0,f,0,0,0],append=True)
            

