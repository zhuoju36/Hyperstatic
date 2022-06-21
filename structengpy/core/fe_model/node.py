# -*- coding: utf-8 -*-

import numpy as np
from structengpy.common.csys import Cartesian
import scipy.sparse as spr

class Node(object):
    def __init__(self,name:str,x:float,y:float,z:float):
        self.__name=name
        o=[x,y,z]
        pt1=[x+1,y,z]
        pt2=[x,y+1,z]
        self.__local_csys=Cartesian(o,pt1,pt2)
        self.__mass=np.zeros(6)
        
        # self.__disp=np.array([None,None,None,None,None,None]).reshape((6,1))
        # self.__load=np.zeros((6,1))
        
    @property
    def name(self):
        return self.__name
        
    # @property
    # def hid(self):
    #     return self.__hid

    # @hid.setter
    # def hid(self,hid):
    #     assert type(hid)==int
    #     self.__hid=hid

    @property
    def loc(self):
        return self.__local_csys.origin

    @property
    def x(self):
        return self.loc[0]
    
    @property
    def y(self):
        return self.loc[1]
    
    @property
    def z(self):
        return self.loc[2]
        
    @property
    def local_csys(self):
        return self.__local_csys

    @property
    def mass(self):
        return self.__mass

    @mass.setter
    def mass(self,val:np.ndarray):
        self.__mass = val
    
    @property
    def transform_matrix(self)->np.ndarray:
        """获取结点的变换矩阵

        Returns:
            np.ndarray: 6x6变换矩阵
        """
        V=self.__local_csys.transform_matrix
        V_=np.zeros((6,6))
        V_[:3,:3]=V_[3:,3:]=V
        return V_

    def initialize_csys(self):
        self.__local_csys.align_with_global()
    
    def rotate_about_1axis(self,theta):
        self.__local_csys.rotate_about_x(theta)

    def rotate_about_2axis(self,theta):
        self.__local_csys.rotate_about_y(theta)

    def rotate_about_3axis(self,theta):
        self.__local_csys.rotate_about_z(theta)

    def integrate_M(self)->spr.coo_matrix:
        return spr.diags(self.mass,format="coo")

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
        
        

    