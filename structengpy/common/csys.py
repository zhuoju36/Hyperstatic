# -*- coding: utf-8 -*-
import numpy as np
import uuid

from structengpy.common.tolerance import Tolerance
from scipy.spatial.transform import Rotation as R

class Cartisian(object):
    def __init__(self,O:tuple, A:tuple, B:tuple, name:str=None):
        """_summary_

        Args:
            O (tuple): array-like
            A (tuple): array-like
            B (tuple): array-like
            name (str, optional):  Defaults to None.

        Raises:
            Exception: _description_
        """
        tol=Tolerance.abs_tol()
        self.__O=np.array(O)    
        OA = np.array(A)-np.array(O)
        OB = np.array(B)-np.array(O)
        if np.max(np.abs(np.cross(OA,OB)))<tol:
            raise Exception("Three points should not be in a line!!")        
        x = OA/np.linalg.norm(OA)
        z = np.cross(OA, OB)
        z = z / np.linalg.norm(z)
        y = np.cross(z, x)
        self.__T=np.array([x,y,z])
        self.__name=uuid.uuid1() if name==None else name
        
    @property
    def name(self):
        return self.__name
        
    @property
    def origin(self):
        return self.__O
        
    @property
    def x(self):
        return self.__T[0,:]
    
    @property
    def y(self):
        return self.__T[1,:]
    
    @property
    def z(self):
        return self.__T[2,:]
        
    @property
    def transform_matrix(self):
        return self.__T

    def rotate_about_external_x(self,theta:float):
        r=R.from_quat([1*np.sin(theta/2),0,0,np.cos(theta/2)])
        self.__T=r.apply(self.__T)

    def rotate_about_external_y(self,theta:float):
        r=R.from_quat([0,1*np.sin(theta/2),0,np.cos(theta/2)])
        self.__T=r.apply(self.__T)

    def rotate_about_external_z(self,theta:float):
        r=R.from_quat([0,0,1*np.sin(theta/2),np.cos(theta/2)])
        self.__T=r.apply(self.__T)

    def rotate_about_x(self,theta:float):
        x,y,z=self.__T[0,:]
        r=R.from_quat([x*np.sin(theta/2),y*np.sin(theta/2),z*np.sin(theta/2),np.cos(theta/2)])
        self.__T=r.apply(self.__T)

    def rotate_about_y(self,theta:float):
        x,y,z=self.__T[1,:]
        r=R.from_quat([x*np.sin(theta/2),y*np.sin(theta/2),z*np.sin(theta/2),np.cos(theta/2)])
        self.__T=r.apply(self.__T)

    def rotate_about_z(self,theta:float):
        x,y,z=self.__T[2,:]
        r=R.from_quat([x*np.sin(theta/2),y*np.sin(theta/2),z*np.sin(theta/2),np.cos(theta/2)])
        self.__T=r.apply(self.__T)

    def rotate_about_vec(self,x:float,y:float,z:float,theta:float):
        """绕给定轴线旋转

        Args:
            x (float): 旋转轴x分量
            y (float): 旋转轴y分量
            z (float): 旋转轴z分量
            theta (float): 旋转角
        """
        l=np.linalg.norm(np.array([x,y,z]))
        r=R.from_quat([x/l*np.sin(theta/2),y/l*np.sin(theta/2),z/l*np.sin(theta/2),np.cos(theta/2)])
        self.__T=r.apply(self.__T)
    
    def set_by_3pts(self,O:tuple, A:tuple, B:tuple):
        """以三点设定坐标系方向

        Args:
            O (tuple): array-like
            A (tuple): array-like
            B (tuple): array-like
            name (str, optional):  Defaults to None.

        Raises:
            Exception: _description_
        """
        tol=1e-8
        self.__O=O    
        OA = np.array(A)-np.array(O)
        OB = np.array(B)-np.array(O)
        cos = np.dot(OA, OB)/np.linalg.norm(OA)/np.linalg.norm(OB)
        if  np.abs(np.abs(cos)-1.)<tol:
            raise Exception("Three points should not in a line!!")        
        self.__x = OA/np.linalg.norm(OA)
        z = np.cross(OA, OB)
        self.__z = z/np.linalg.norm(z)
        self.__y = np.cross(self.z, self.x)
    
    @origin.setter
    def origin(self,x:float, y:float, z:float):
        self.__O = (x,y,z)
    
    def align_with_global(self):
        """对齐绝对坐标系
        """
        self.__T=np.array([[1,0,0],[0,1,0],[0,0,1]])

if __name__=='__main__':
    #basic
    csys=Cartisian((0,0,0),(1,0,0),(0,1,0))
    print(csys.transform_matrix)

    #rotate pi/4
    csys=Cartisian((0,0,0),(1,1,0),(0,1,0))
    print(csys.transform_matrix)

    #rotate pi/4 with eular angle
    csys=Cartisian((0,0,0),(1,0,0),(0,1,0))
    csys.rotate_about_external_z(np.pi/4)
    print(csys.transform_matrix)

    #rotate pi/4 with quaterion
    csys=Cartisian((0,0,0),(1,0,0),(0,1,0))
    csys.rotate_about_vec(0,0,1,np.pi/4)
    print(csys.transform_matrix)

    #rotate pi/3 with quaterion
    csys=Cartisian((0,0,0),(1,0,0),(0,1,0))
    csys.rotate_about_vec(1,1,1,np.pi/3)
    print(csys.transform_matrix)
    csys.rotate_about_z(np.pi/4)
    print(csys.transform_matrix)

    #co-line
    csys=Cartisian((0,0,0),(1,2,0),(2,4,0))
    print(csys.transform_matrix)
    
