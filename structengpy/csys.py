# -*- coding: utf-8 -*-
import numpy as np
import uuid

class Cartisian(object):
    def __init__(self,O:tuple, A:tuple, B:tuple, name:str=None):
        """
        O: 3x1 vector
        A: 3x1 vector
        B: 3x1 vector
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
        self.__name=uuid.uuid1() if name==None else name
        
    @property
    def name(self):
        return self.__name
        
    @property
    def origin(self):
        return self.__O
        
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
        # V=np.array([[x[0],y[0],z[0]],
        #           [x[1],y[1],z[1]],
        #           [x[2],y[2],z[2]]])
        # return V.transpose()
        return np.array([x,y,z])
    
    def set_by_3pts(self,O:tuple, A:tuple, B:tuple):
        """
        O: tuple 3
        A: tuple 3
        B: tuple 3
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
        self.__x=np.array([1,0,0])
        self.__y=np.array([0,1,0])
        self.__z=np.array([0,0,1])

if __name__=='__main__':
    csys=Cartisian((0,0,0),(1,1,0),(0,1,0))
    print(csys.transform_matrix)
