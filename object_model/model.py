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
PointLoad

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
        engine=create_engine('sqlite://'+database)
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
        engine=create_engine('sqlite:///'+operate_db)
        Session=o.sessionmaker(bind=engine,autoflush=False)
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
        frm=FrameSection()
        frm.name=name
        frm.type=type
        if type=='o':
            assert len(size)==1
        elif type=='O':
            assert len(size)==2
        else:
            assert len(size)==4
        frm.size=size
        self.session.add(frm)
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
        return True

    def add_point(self,name,x,y,z):
        """
        Add point object to model, if the name already exists, an exception will be raised.
        if a point in same location exists, the name of the point will be returned.
        param:
            x,y,z: float-like, coordinates.
        return:
            Point name as index in the object model.
        """
        if self.session.query(LoadCase).filter_by(name=name).first()!=None:
            raise Exception('Name already exists!')
        pt=Point()
        pt.x=x
        pt.y=y
        pt.z=z
        self.session.add(pt)
        return(True)
        
        
    def add_frame(self,frame):
        """
        Add frame object to model, if the name already exists, an exception will be raised.
        if a frame connecting same points exists, the name of the point will be returned.
        param:
            frame: Frame object.
        return:
            Frame name as index in the object model.
        """
        if frame.name in self.__frames.keys():
            raise Exception('Name already exist!')
        res=[a.hid for a in self.__frames.values() 
            if (a.points[0]==frame.points[0] and a.points[1]==frame.points[1]) 
            or (a.points[0]==frame.points[1] and a.points[1]==frame.points[0])]
        if res==[]:
            self.__frames[frame.name]=frame
            res=frame.name
        else:
            res=res[0]
        return res

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
        
    def set_point_restraint(self,name,restraint):
        assert len(restraint)==6
        self.__points[name].restraints=restraint
        
    def set_point_load(self,name,load):
        assert type(load)==LoadPt
    
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
    
    def save(path):
        pass
    
    def import_model():
        pass
    
    def import_dxf():
        pass

     
#    def add_material(self,material):
#        """
#        Add material to model, if the name already exists, an exception will be raised
#        param:
#            material: Material object.
#        return:
#            material name as index in the object model.
#        """
#        if material.name in self.__materials.keys():
#            raise Exception('Name already exists!')
#        self.__materials[material.name]=material
#        return material.name  
#    
#    def add_frame_section(self,section):
#        """
#        Add frame section to model, if the name already exists, an exception will be raised.
#        param:
#            section: FrameSection object.
#        return:
#            frame section name as index in the object model.
#        """
#        if section.name in self.__frame_sections.keys():
#            raise Exception('Name already exists!')
#        self.__frame_sections[section.name]=section
#        return section.name    
#    
#    def add_area_section(self):
#        pass
#    
#    def add_loadcase(self,loadcase):
#        """
#        Add frame section to model, if the name already exists, an exception will be raised.
#        param:
#            section: FrameSection object.
#        return:
#            frame section name as index in the object model.
#        """
#        if loadcase.name in self.__loadcases.keys():
#            raise Exception('Name already exists!')
#        self.__loadcases[loadcase.name]=loadcase
#        return loadcase.name     
#
#    def add_point(self,pt):
#        """
#        Add point object to model, if the name already exists, an exception will be raised.
#        if a point in same location exists, the name of the point will be returned.
#        param:
#            point: Point object.
#        return:
#            Point name as index in the object model.
#        """
#        tol=self.__tolarence
#        if pt.name in self.__points.keys():
#            raise Exception('Name already exists!')
#        res=[a.name for a in self.__points.values() 
#                        if abs(a.x-pt.x)+abs(a.y-pt.y)+abs(a.z-pt.z)<tol*3]
#        if res==[]:
#            self.__points[pt.name]=pt
#            res=pt.name
#        else:
#            res=res[0]
#        return res
#        
#    def add_frame(self,frame):
#        """
#        Add frame object to model, if the name already exists, an exception will be raised.
#        if a frame connecting same points exists, the name of the point will be returned.
#        param:
#            frame: Frame object.
#        return:
#            Frame name as index in the object model.
#        """
#        if frame.name in self.__frames.keys():
#            raise Exception('Name already exist!')
#        res=[a.hid for a in self.__frames.values() 
#            if (a.points[0]==frame.points[0] and a.points[1]==frame.points[1]) 
#            or (a.points[0]==frame.points[1] and a.points[1]==frame.points[0])]
#        if res==[]:
#            self.__frames[frame.name]=frame
#            res=frame.name
#        else:
#            res=res[0]
#        return res
#
#    def get_point(self,name):
#        """
#        params:
#            name: str
#        returns:
#            point object if exist
#        """
#        return self.__points[name]
#    
#    def get_frame(self,name):
#        """
#        params:
#            name: str
#        returns:
#            frame object if exist
#        """
#        return self.__frames[name]
#    
#    def get_frame_section(self,name):
#        """
#        params:
#            name: str
#        returns:
#            frame section object if exist
#        """
#        return self.__frame_sections[name]
#        
#    def set_point_restraint(self,name,restraint):
#        assert len(restraint)==6
#        self.__points[name].restraints=restraint
#        
#    def set_point_load(self,name,load):
#        assert type(load)==LoadPt
#    
#    def run(self,lcs):
#        """
#        Run the model with loadcases
#        params:
#            lcs: list of str, specify load cases to run.
#        return:
#            None.
#        """
#        model=self.__femodel
#        model.assemble_KM()
#        for lc in lcs:
#            if type(self.__load[lc])==StaticLinear:
#                log.info('Solving LoadCase %s'%lc)
#                self.__apply_load(lc)
#                model.assemble_f()
#                model.assemble_boundary()
#                res=solve_linear(model)
#                print(res,6)
#            else:
#                pass
#    
#    def save(path):
#        pass
#    
#    def import_model():
#        pass
#    
#    def import_dxf():
#        pass
