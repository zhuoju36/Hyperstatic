# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 21:50:29 2016

@author: HZJ
"""
import uuid

import numpy as np

from csys import Cartisian

class Node(object):
    def __init__(self,x,y,z,name=None):
        self.__name=uuid.uuid1() if name==None else str(name)
        self.__hid=None #hidden id
        self.__loc=np.array([x,y,z])
        o=[x,y,z]
        pt1=[x+1,y,z]
        pt2=[x,y+1,z]
        self.__local_csys=Cartisian(o,pt1,pt2)
        
        # self.__disp=np.array([None,None,None,None,None,None]).reshape((6,1))
        # self.__load=np.zeros((6,1))
        
    @property
    def name(self):
        return self.__name
        
    @property
    def hid(self):
        return self.__hid

    @hid.setter
    def hid(self,hid):
        assert type(hid)==int
        self.__hid=hid

    @property
    def loc(self):
        return self.__loc

    @property
    def x(self):
        return self.__loc[0]
    
    @property
    def y(self):
        return self.__loc[1]
    
    @property
    def z(self):
        return self.__loc[2]
        
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
        self.__local_csys.align_with_global()

    # @property
    # def fn(self):
    #     return self.__load

    # @fn.setter
    # def fn(self,load):
    #     assert(len(load)==6)
    #     self.__load=np.array(load).reshape((6,1))

    # @property
    # def dn(self):
    #     return self.__disp
    # @dn.setter
    # def dn(self,disp):
    #     assert(len(disp)==6)
    #     self.__disp=disp
        
        

    