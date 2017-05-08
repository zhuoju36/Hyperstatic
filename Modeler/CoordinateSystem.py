# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 21:57:50 2016

@author: HZJ
"""
import numpy as np
import uuid

class cartisian(object):
    def __init__(self,origin, pt1, pt2, name=None):
        """
        origin: 3x1 vector
        pt1: 3x1 vector
        pt2: 3x1 vector
        """
        self.__origin=origin    
        vec1 = np.array([pt1[0] - origin[0] , pt1[1] - origin[1] , pt1[2] - origin[2]])
        vec2 = np.array([pt2[0] - origin[0] , pt2[1] - origin[1] , pt2[2] - origin[2]])
        cos = np.dot(vec1, vec2)/np.linalg.norm(vec1)/np.linalg.norm(vec2)
        if  cos == 1 or cos == -1:
            raise Exception("Three points should not in a line!!")        
        self.__x = vec1/np.linalg.norm(vec1)
        z = np.cross(vec1, vec2)
        self.__z = z/np.linalg.norm(z)
        self.__y = np.cross(self.z, self.x)
        self.__name=uuid.uuid1() if name==None else name
        
    @property
    def name(self):
        return self.__name
        
    @property
    def origin(self):
        return self.__origin
        
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
    def transform_matrix(self):
        x=self.x
        y=self.y
        z=self.z
        V=np.array([[x[0],y[0],z[0]],
                  [x[1],y[1],z[1]],
                  [x[2],y[2],z[2]]])
        return V.transpose()
    
    def set_by_3pts(self,origin, pt1, pt2):
        """
        origin: tuple 3
        pt1: tuple 3
        pt2: tuple 3
        """
        self.origin=origin    
        vec1 = np.array([pt1[0] - origin[0] , pt1[1] - origin[1] , pt1[2] - origin[2]])
        vec2 = np.array([pt2[0] - origin[0] , pt2[1] - origin[1] , pt2[2] - origin[2]])
        cos = np.dot(vec1, vec2)/np.linalg.norm(vec1)/np.linalg.norm(vec2)
        if  cos == 1 or cos == -1:
            raise Exception("Three points should not in a line!!")        
        self.x = vec1/np.linalg.norm(vec1)
        z = np.cross(vec1, vec2)
        self.z = z/np.linalg.norm(z)
        self.y = np.cross(self.z, self.x)
    
    def set_origin(self,x, y, z):
        """
        origin: tuple 3
        pt1: tuple 3
        pt2: tuple 3
        """
        self.origin = (x,y,z)
    
    def align_with_global(self):
        self.x=np.array([1,0,0])
        self.y=np.array([0,1,0])
        self.z=np.array([0,0,1])

if __name__=='__main__':
    csys=cartisian((0,0,0),(1,1,0),(0,1,0))
    csys.align_with_global()