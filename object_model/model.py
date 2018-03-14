# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 19:52:26 2018

@author: HZJ
@E-mail: zhuoju36@hotmail.com
"""
import os
import shutil
import time

from .orm import Base,Config,\
Material,IsotropicElastic,\
Point,Frame,\
FrameSection,\
LoadCase,LoadCaseStaticLinearSetting,\
PointRestraint,PointLoad

from object_model.frame_section import Pipe,Circle,HollowBox,ISection

from fe_model import Model as FEModel
from fe_model.node import Node
from fe_model.element import Beam

from sqlalchemy import create_engine
import sqlalchemy.orm as o
from datetime import datetime

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
            
    def add_material(self,name,gamma,type,**kwargs):
        """
        Add material to model, if the name already exists, an exception will be raised
        param:
            name: name of material.
            gamma: density.
            type: 'isoelastic','...'
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
        mat.type=type
        if type=='isoelastic':
            iso_elastic=IsotropicElastic()
            iso_elastic.material=mat.name
            iso_elastic.E=kwargs['E']
            iso_elastic.mu=kwargs['mu']
        self.session.add(mat)
        self.session.commit()
        return True
    
    def add_frame_section(self,name,type,size):
        """
        Add frame section to model, if the name already exists, an exception will be raised.
        param:
            name: str. Name of the section.
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
        frmsec.type=type
        sec=None
        if type=='o':
            assert len(size)==1
            sec=Circle(None,size[0])
        elif type=='O':
            assert len(size)==2
            sec=Pipe(None,size[0],size[1])
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
    
    def add_loadcase(self,name,type,**kwargs):
        """
        Add material to model, if the name already exists, an exception will be raised
        param:
            name: name of material.
            type: '1st','2nd','3rd','modal','spectrum','th','buckle'
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
        lc.type=type
        if type=='1st':
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
            frm.point_0=pt1
            frm.point_1=pt2
            frm.order=order
        elif pt1>pt2:
            order='10'
            frm.point_0=pt2
            frm.point_1=pt1
            frm.order=order
        else:
            raise Exception('Two points should not be the same!')
        frm.section=section
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
        res=self.session.query(PointRestraint).filter_by(point=point).first()
        if res is None:
            res=PointRestraint()
        res.point=point
        res.res_r1=restraints[0]
        res.res_r2=restraints[1]
        res.res_r3=restraints[2]
        res.res_u1=restraints[3]
        res.res_u2=restraints[4]
        res.res_u3=restraints[5]
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
        ld=self.session.query(PointLoad).filter_by(pt_name=point,lc_name=loadcase).first()
        if ld is None:
            ld=PointLoad()
        ld.pt_name=point
        ld.lc_name=loadcase
        ld.r1=load[0]
        ld.r2=load[1]
        ld.r3=load[2]
        ld.u1=load[3]
        ld.u2=load[4]
        ld.u3=load[5]
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
        model=self.__femodel
        model.assemble_KM()
        for lc in lcs:
            if type(self.__load[lc])==StaticLinear:
                log.info('Solving LoadCase %s'%lc)
                self.__apply_load(lc)
                model.assemble_f()
                model.assemble_boundary()
                res=solve_linear(model)
                print(res,6)
            else:
                pass
    
    def mesh(self):
        femodel=FEModel()
        points=self.session.query(Point).all()
        frames=self.session.query(Frame).all()
        pn_map={}
        for pt in points:
            res=femodel.add_node(Node(pt.x,pt.y,pt.z))
            pn_map[pt.name]=res
        for frm in frames:
            node0=femodel.nodes[pn_map[frm.point_0]]
            node1=femodel.nodes[pn_map[frm.point_1]]
            E=frm.frame_section.material.isotropic_elastic.E
            mu=frm.frame_section.material.mu
            A=frm.frame_section.A
            J=frm.frame_section.J
            I2=frm.frame_section.I2
            I3=frm.frame_section.I3
            J=frm.frame_section.J
            rho=frm.frame_section.material.rho
            if frm.order=='01':
                res=femodel.add_beam(Beam(node0,node1,E, mu, A, I2, I3, J, rho))
            elif frm.order=='10':
                res=femodel.add_beam(Beam(node1,node0,E, mu, A, I2, I3, J, rho))
            print(femodel.beams[-1])

    def import_model():
        pass
    
    def import_dxf():
        pass
