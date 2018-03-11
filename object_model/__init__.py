# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 14:07:55 2018

@author: Dell
"""
from fe_model import Model as FEModel

class Model():
    def __init__(self):
        #configurations
        self.__tolarence=1e-6
        self.__unit='N_m_C'
        self.__version='0.0.1'
        
        #materials
        self.__materials={}
        
        #sections
        self.__frame_sec={}
        self.__area_sec={}
        
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
        self.femodel=FEModel()
        
    def add_material(self):
        pass
    
    def add_frmsec(self):
        pass
    
    def add_areasec(self):
        pass

    def add_point(self,pt):
        """
        add node to model
        if node already exits, node will not be added.
        return: node hidden id
        """
        tol=self.__tolarence
        res=[a.name for a in self.__points.values() if abs(a.x-pt.x)+abs(a.y-pt.y)+abs(a.z-pt.z)<tol*3]
        if pt in self.__points.keys():
            raise Exception('Name already exist!')
        if res==[]:
            self.__nodes[pt.name]=pt
        else:
            res=res[0]
        return res
        
    def add_frame(self,frame):
        """
        add beam to model
        if beam already exits, it will not be added.
        return: beam hidden id
        """
        res=[a.hid for a in self.__frames.values() 
            if (a.nodes[0]==beam.nodes[0] and a.nodes[1]==beam.nodes[1]) 
            or (a.nodes[0]==beam.nodes[1] and a.nodes[1]==beam.nodes[0])]
        if res==[]:
            res=len(self.__beams)
            beam.hid=res
            self.__beams[res]=beam
        else:
            res=res[0]
        return res

        
    def run(lcs):
        pass
    
    def save(path):
        pass
    
    def import_model():
        pass
    
    def import_dxf():
        pass