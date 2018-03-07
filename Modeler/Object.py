# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 14:07:55 2018

@author: Dell
"""
import uuid

import numpy as np

from . import CoordinateSystem,Section
from .Node import Node
from .Element import Beam, TriMembrane

class Point(object):
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
        self.__node=None
        self.__hid=None
        
        #results
        self.__res_disp=None
        self.__res_force=None
        
    @property
    def name(self):
        return self.__name
        
    @property
    def hid(self):
        return self.__hid
        
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
    def T(self):
        """
        point local-global csys transform matrix.
        """
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
        
    def mesh(self,model):
        """
        mesh to nodes
        model: FEModel warpped in list.
        """
        node=Node(self.x,self.y,self.z)
        self.__hid=model[0].add_node(node)
        
    def load_to_mesh(self,model,locase):
        """
        add certain loads and displacements to mesh.
        model: FEModel warpped in list.
        """
        if self.__hid==None:
            raise Exception('The object must be meshed first!')
        model[0].add_nodal_force(self.__hid,self.__load)
        model[0].add_nodal_displacement(self.__hid,self.__displacement)        

class Frame(object):
    def __init__(self,pt_i,pt_j,sec:Section.Section):
        self.__pt_i=pt_i
        self.__pt_j=pt_j
        self.__loadI=[0]*6
        self.__loadJ=[0]*6
        self.__releaseI=[False]*6
        self.__releaseJ=[False]*6
        self.__section=sec
        self.__rotation=0
        
        self.__load_d=[] #distributed
        self.__load_c=[] #concentrated
        self.__load_s=[] #strain
        self.__load_t=[] #temperature

        #results
        self.__res_force=None
        self.__res_disp=None
        self.__measure=[] #result measure locations
        self.__ms_forces=[]
        self.__ms_disps=[]

    def initialize_csys(self):
        node_i=self.__nodes[0]
        node_j=self.__nodes[1]
        o = np.array([node_i.x, node_i.y, node_i.z])
        pt1 = np.array([node_j.x, node_j.y, node_j.z])
        pt2 = np.array([0,0,0])
        if node_i.x != node_j.x and node_i.y != node_j.y:
            pt2[2] = 1
        else:
            pt2[0] = 1
        self.local_csys.set_by_3pts(o, pt1, pt2)
        
    @property
    def length(self):
        nodeI=self.__pt_i
        nodeJ=self.__pt_j
        return np.sqrt((nodeI.x - nodeJ.x)*(nodeI.x - nodeJ.x) + (nodeI.y - nodeJ.y)*(nodeI.y - nodeJ.y) + (nodeI.z - nodeJ.z)*(nodeI.z - nodeJ.z))
        
    def elm_force(self,uij,fij):
        """
        uij,fij: 12x1 sparse vector
        """
#        fij = np.zeros(12)
#        Kij = sp.csc_matrix(12, 12)
#        rij = sp.csc_matrix(12,1)
        Kij, Mij, rij = self.static_condensation()
        fij = Kij * uij + self.nodal_force
        return fij
        
    def clear_result(self):
        self.__res_force=None
        
    #result force
    @property
    def res_force(self):
        return self.__res_force
    
    @res_force.setter
    def res_force(self,force):
        self.__res_force=force
        
    @property
    def nodeI(self):
        return self.__nodeI
    
    @property
    def nodeJ(self):
        return self.__nodeJ
    
    @property
    def section(self):
        return self.__section
        
    @property
    def releaseI(self):
        return self.__releaseI
        
    @property
    def releaseJ(self):
        return self.__releaseJ
        
    @property
    def nodal_force(self):
        l = self.length
        loadI=self.loadI
        loadJ=self.loadJ
        #recheck!!!!!!!!!!!!
        #i
        v=np.zeros(12)
        v[0]=(loadI[0] + loadJ[0]) * l / 2#P
        v[1]=(loadI[1] * 7 / 20 + loadJ[1] * 3 / 20) * l#V2
        v[2]=(loadI[2] * 7 / 20 + loadJ[2] * 3 / 20) * l#V3
        v[3]=loadI[3] - loadJ[3]#T
        v[4]=(loadI[2] / 20 + loadJ[2] / 30) * l * l + loadI[4]#M22
        v[5]=(loadI[1] / 20 + loadJ[1] / 30) * l * l + loadI[5]#M33
        #j
        v[6]=(loadJ[0] + loadI[0]) * l / 2#P
        v[7]=(loadJ[1] * 7 / 20 + loadI[1] * 3 / 20) * l#V2
        v[8]=(loadJ[2] * 7 / 20 + loadI[2] * 3 / 20) * l#V3
        v[9] = loadJ[3] - loadI[3]#T
        v[10] = -(loadJ[2] / 20 + loadI[2] / 30) * l * l + loadJ[4]#M22
        v[11] = -(loadJ[1] / 20 + loadI[1] / 30) * l * l + loadJ[5]#M33
        return v
        
        #to be revised
    def load_distributed(self,qi, qj):
        """
        qi,qj: 6x1 vector
        """
        self.loadI=qi
        self.loadJ=qj
        
    def mesh(self,model):
        """
        mesh to beams
        model: FEModel warpped in list.
        """
        E = self.section.material.E
        A = self.section.A
        J = self.section.J
        mu = self.section.material.mu
        I2 = self.section.I22
        I3 = self.section.I33
        rho = self.section.material.gamma
        nid_i=self.__pt_i.hid
        nid_j=self.__pt_j.hid
        if nid_i is None or nid_j is None:
            raise Exception("Relative point object must be meshed!")
        node_i=model.node[nid_i]
        node_j=model.node[nid_j]
        beam=Beam(node_i, node_j, E, mu, A, I2, I3, J, rho, name=None)
        model.add_beam(beam)
        
    def attribute_load(self,model,locase):
        """
        add certain loads and displacements to mesh.
        model: FEModel warpped in list.
        """
        if self.__hid==None:
            raise Exception('The object must be meshed first!')
        #convert beam force to nodal force
        model[0].add_nodal_force(self.__hid,self.__load)
        l = self.Length()
        loadI=self.loadI
        loadJ=self.loadJ
        #recheck!!!!!!!!!!!!
        #i
        v=np.zeros(12)
        v[0]=(loadI[0] + loadJ[0]) * l / 2#P
        v[1]=(loadI[1] * 7 / 20 + loadJ[1] * 3 / 20) * l#V2
        v[2]=(loadI[2] * 7 / 20 + loadJ[2] * 3 / 20) * l#V3
        v[3]=loadI[3] - loadJ[3]#T
        v[4]=(loadI[2] / 20 + loadJ[2] / 30) * l * l + loadI[4]#M22
        v[5]=(loadI[1] / 20 + loadJ[1] / 30) * l * l + loadI[5]#M33
        #j
        v[6]=(loadJ[0] + loadI[0]) * l / 2#P
        v[7]=(loadJ[1] * 7 / 20 + loadI[1] * 3 / 20) * l#V2
        v[8]=(loadJ[2] * 7 / 20 + loadI[2] * 3 / 20) * l#V3
        v[9] = loadJ[3] - loadI[3]#T
        v[10] = -(loadJ[2] / 20 + loadI[2] / 30) * l * l + loadJ[4]#M22
        v[11] = -(loadJ[1] / 20 + loadI[1] / 30) * l * l + loadJ[5]#M33
        return v
        
class Area(Object):
    pass