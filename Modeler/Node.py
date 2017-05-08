# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 21:50:29 2016

@author: HZJ
"""
import uuid
import numpy as np
from Modeler import CoordinateSystem

class node(object):
    def __init__(self,x,y,z,name=None):
        self.__x=x
        self.__y=y
        self.__z=z
        o=[x,y,z]
        pt1=[x+1,y,z]
        pt2=[x,y+1,z]
        self.__local_csys=CoordinateSystem.cartisian(o,pt1,pt2)
        self.__restraint=[False]*6
        self.__load=[0]*6
        self.__disp=[0]*6
        self.__name=uuid.uuid1() if name==None else name
        self.__hid=None #hidden id
        
        #results
        self.__res_disp=None
        self.__res_force=None
        
    @property
    def name(self):
        return self.__name
        
    @property
    def hid(self):
        return self.__hid
    @hid.setter
    def hid(self,hid):
        self.__hid=hid
        
    @property
    def x(self):
        return self.__x
    
    @property
    def y(self):
        return self.__y
    
    @property
    def z(self):
        return self.__z
        
    @property
    def local_csys(self):
        return self.__local_csys
    
    @property
    def transform_matrix(self):
        V=self.__local_csys.transform_matrix
        V_=np.zeros((6,6))
        V_[:3,:3]=V_[3:,3:]=V
        return V_

    def initialize_csys(self):
        self.__local_csys.align_with_global();

    @property
    def load(self):
        return self.__load
    @load.setter
    def load(self,load):
        """
        load: a number vector indicates a nodal load.
        """
        self.__load=load

    @property
    def disp(self):
        return self.__disp
    @disp.setter
    def disp(self,disp):
        """
        disp: a boolean vector indicates a nodal displacement.
        """
        self.__disp=disp   
        
    @property
    def restraint(self):
        return self.__restraint
        
    @restraint.setter
    def restraint(self,res):
        """
        res: a boolean vector indicates a nodal restraint.
        """
        self.__restraint=res
    
            
    def clear_result(self):
        self.__res_disp=None
        self.__res_force=None
        
    @property
    def res_disp(self):
        return self.__res_disp
    
    @res_disp.setter
    def res_disp(self,disp):
        self.__res_disp=disp
        
    @property
    def res_force(self):
        return self.__res_force
    
    @res_force.setter
    def res_force(self,force):
        self.__res_force=force
        

    