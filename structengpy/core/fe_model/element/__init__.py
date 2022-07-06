# -*- coding: utf-8 -*-

import uuid
import scipy.sparse as spr
from structengpy.common.csys import Cartesian

class Element(object):
    def __init__(self,name,nodes:list,dim:int,dof:int,csys:Cartesian):  
        self.__name = name      
        self.__dim = dim #dimension
        self.__dof = dof #degree of freedom
        self.__nodes=nodes #list of nodes

        # self.__D=None
        # self.__L=None
        # self.__mass=None
        
        # self._T=None
        # self._Ke=None
        # self._Me=None
        # self._re=None

        self.__local_csys=csys
               
    @property
    def name(self):
        return self.__name
        
    # @property
    # def hid(self):
    #     return self.__hid
    # @hid.setter
    # def hid(self,hid:int):
    #     assert type(hid)==int
    #     self.__hid=hid
        
    @property
    def nodes(self):
        return self.__nodes
    
    @property
    def node_count(self):
        return len(self.__nodes)

    @property
    def dof(self):
        return self.__dof

    @property
    def dim(self):
        return self.__dim

    @property
    def local_csys(self):
        return self.__local_csys

    @property
    def mass(self):
        raise NotImplementedError()

    @property
    def transform_matrix(self):
        raise NotImplementedError()

    def get_node_names(self):
        names=[node.name for node in self.__nodes]
        return names

    def integrate_K(self):
        raise NotImplementedError()

    def integrate_M(self):
        raise NotImplementedError()

    def get_shape_function(self):
        raise NotImplementedError()

    def interpolate(self,loc):
        raise NotImplementedError()

if __name__=="__main__":
    csys=Cartesian((0,0,0),(1,0,0),(0,1,0))
    ele=Element([],2,6,csys)
    print(ele.transform_matrix)
