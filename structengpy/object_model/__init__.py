# -*- coding: utf-8 -*-
import sys
import os
curdir=os.path.dirname(__file__)
parentdir=os.path.dirname(curdir)
sys.path.append(parentdir)

import uuid 

from structengpy.fe_model.structure import Model
import logger

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
    
class FrameCrossSection(StructuralObject):
    def __init__(self,mat,A,J,I33,I22,W33,W22,name=None):
        """
        mat: material
        A: area
        J: Torsional constant
        I33,I22: Iteria momentum
        W33,W22: Bending modulus
        """        
        super(FrameCrossSection,self).__init__(name)
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

