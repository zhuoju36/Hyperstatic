# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 14:07:55 2018

@author: Dell
"""
import uuid 
import sqlalchemy

from fe_model import Model as FEModel
import logger as log

class Model():
    def __init__(self):
        #configurations
        self.__tolarence=1e-6
        self.__unit='N_m_C'
        self.__version='0.0.1'
        
        #materials
        self.__materials={}
        
        #sections
        self.__frame_sections={}
        self.__area_sections={}
        
        #members
        self.__points={}
        self.__cables={}
        self.__frames={}
        self.__areas={}
        
        #group
        self.__groups={}
        
        #loadcase and combinations
        self.__loadcases={}
        self.__combinations={}
        
        #member loads
        self.__load_pt={}
        self.__load_frm_distrib={}
        self.__load_frm_pt={}
        self.__load_frm_tmpt={}
        self.__load_frm_strain={}
        self.__load_area_distrb={}
        self.__load_area_tmpt={}
        self.__load_area_strain={}
        
        #structure
        self.__curves={}
        self.__load_spectrum={}
        self.__load_time_history={}
        
        #femodel
        self.__femodel=FEModel()
                
    def add_material(self,material):
        """
        Add material to model, if the name already exists, an exception will be raised
        param:
            material: Material object.
        return:
            material name as index in the object model.
        """
        if material.name in self.__materials.keys():
            raise Exception('Name already exists!')
        self.__materials[material.name]=material
        return material.name  
    
    def add_frame_section(self,section):
        """
        Add frame section to model, if the name already exists, an exception will be raised.
        param:
            section: FrameSection object.
        return:
            frame section name as index in the object model.
        """
        if section.name in self.__frame_sections.keys():
            raise Exception('Name already exists!')
        self.__frame_sections[section.name]=section
        return section.name    
    
    def add_area_section(self):
        pass
    
    def add_loadcase(self,loadcase):
        """
        Add frame section to model, if the name already exists, an exception will be raised.
        param:
            section: FrameSection object.
        return:
            frame section name as index in the object model.
        """
        if loadcase.name in self.__loadcases.keys():
            raise Exception('Name already exists!')
        self.__loadcases[loadcase.name]=loadcase
        return loadcase.name     

    def add_point(self,pt):
        """
        Add point object to model, if the name already exists, an exception will be raised.
        if a point in same location exists, the name of the point will be returned.
        param:
            point: Point object.
        return:
            Point name as index in the object model.
        """
        tol=self.__tolarence
        if pt.name in self.__points.keys():
            raise Exception('Name already exists!')
        res=[a.name for a in self.__points.values() 
                        if abs(a.x-pt.x)+abs(a.y-pt.y)+abs(a.z-pt.z)<tol*3]
        if res==[]:
            self.__points[pt.name]=pt
            res=pt.name
        else:
            res=res[0]
        return res
        
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

class StructuralObject(object):
    def __init__(self,name):
        self._uuid=uuid.uuid1()
        self._name=self._uuid if name==None else name
        self._hid=[]
        
    @property
    def name(self):
        return self._name
    
    @property
    def hid(self):
        return self._hid

    @property
    def local_csys(self):
        return self._local_csys

class LoadCase(StructuralObject):
    def __init__(self,name):
        """
        name: name of load case
        """
        super(LoadCase,self).__init__(name)
        
class Material(object):
    def __init__(self,gamma,name=None):
        """
        gamma: density.
        name: optional, an uuid is given by default.
        """
        self._gamma = gamma
        self._name=uuid.uuid1() if name==None else name
    
    @property
    def name(self):
        return self._name
        
    @property
    def gamma(self):
        return self._gamma
    
class FrameSection(StructuralObject):
    def __init__(self,mat,A,J,I33,I22,W33,W22,name=None):
        """
        mat: material
        A: area
        J: Torsional constant
        I33,I22: Iteria momentum
        W33,W22: Bending modulus
        """        
        super(FrameSection,self).__init__(name)
        self._mat=mat
        self._A=A
        self._J=J
        self._I33=I33
        self._I22=I22
        self._W33=W33
        self._W22=W22

    @property
    def A(self):
        return self._A
        
    @property
    def J(self):
        return self._J
        
    @property
    def I33(self):
        return self._I33
    
    @property
    def I22(self):
        return self._I22
        
    @property
    def W33(self):
        return self._W33
        
    @property
    def W22(self):
        return self._W22
        
    @property
    def i33(self):
        return (self._I33/self._A)**0.5

    @property  
    def i22(self):
        return (self._I22/self. _A)**0.5
        
    @property
    def material(self):
        return self._mat

