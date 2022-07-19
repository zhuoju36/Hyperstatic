# -*- coding: utf-8 -*-
from typing import Dict
import numpy as np

from scipy.sparse import linalg as sl
from structengpy.common.tolerance import Tolerance

from structengpy.core.fe_model.node import Node
from structengpy.core.fe_model.material import Material
from structengpy.core.fe_model.material.isotropy import IsotropicMaterial
from structengpy.core.fe_model.section.beam_section import *
from structengpy.core.fe_model.element.line.simple_beam import SimpleBeam
from structengpy.core.fe_model.element.line.beam import Beam

from structengpy.core.fe_model.element.tri.membrane import Membrane3
from structengpy.core.fe_model.element.quad.membrane4 import Membrane4

import logging

class Model:
    def __init__(self):
        self.__nodes:Dict[str,Node]={}
        self.__nodal_restraints:Dict[str,list]={} 
        self.__material:Dict[str,Material]={}
        self.__beam_section:Dict[str,BeamSection]={}
        self.__beams:Dict[str,Beam]={}
        self.__tria={}
        self.__quad={}

        self.__hid:Dict[str,Dict[str,int]]={}
        self.__hid['node']={}
        self.__hid['beam']={}
        self.__hid['tria']={}
        self.__hid['quad']={}
                
        # self.__index=[]
        # self.__dof=None

        # self.__pattern={}
        # self.__loadcase={}
        
    @property
    def node_count(self):
        return len(self.__nodes.items())

    @property
    def beam_count(self):
        return len(self.__beams.items())
    
    # @property
    # def nodes(self):
    #     return self.__nodes
    
    # @property
    # def beams(self):
    #     return self.__beams
    
    # @property
    # def membrane3s(self):
    #     return self.__membrane3s

    # @property
    # def membrane4s(self):
    #     return self.__membrane4s
        
    # @property 
    # def index(self):
    #     return self.__index
        
    def add_node(self,name:str,x:float,y:float,z:float,check_dup=False)->int:
        node=Node(name,x,y,z)
        if check_dup:
            tol=Tolerance.abs_tol()
            res=[a for a in self.__nodes.values() if np.linalg.norm(a.loc-np.array([x,y,z]))<tol]
        else:
            res=[]
        if res==[]:
            res=len(self.__nodes) #hid
            self.__hid['node'][name]=res
            self.__nodes[name]=node
        else:
            dup_name=res[0].name
            res=self.__hid['node'][dup_name]
        return res

    def set_nodal_restraint(self,name,u1:bool,u2:bool,u3:bool,r1:bool,r2:bool,r3:bool)->bool:
        if name not in self.__nodes.keys():
            logging.warning("Node name %s is not defined, nodal restraint setting is aborted."%name)
            return False
        self.__nodal_restraints[name]=np.array([u1,u2,u3,r1,r2,r3])
        return True

    def get_nodal_restraint_dict(self):
        res={}
        for k,v in self.__nodal_restraints.items():
            res[k]=np.array(v)
        return res

    def set_nodal_mass(self,name:str,u1:float,u2:float,u3:float,r1:float,r2:float,r3:float):
        self.__nodes[name].mass=np.array([u1,u2,u3,r1,r2,r3])

    def add_isotropic_material(self,name:str,rho:float,E:float,mu:float,a:float)->bool:
        mat=IsotropicMaterial(name,rho,E,mu,a)
        self.__material[name]=mat

    def add_beam_section_general(self,name:str,material:str,A,As2,As3,I22,I33,J,W22,W33):
        mat=self.__material[material]
        sec=BeamSection(name,mat,'general',[],A,As2,As3,J,I22,I33,W22,W33)
        self.__beam_section[name]=sec

    def add_beam_section_rectangle(self,name:str,material:str,h,b):
        mat=self.__material[material]
        sec=RectangleSection(name,mat,h,b)
        self.__beam_section[name]=sec

    def add_beam_section_I(self,name:str,material:str,h,b,tw,tf):
        mat=self.__material[material]
        sec=ISection(name,mat,h,b,tw,tf)
        self.__beam_section[name]=sec

    def add_beam_section_box(self,name:str,material:str,h,b,tw,tf):
        mat=self.__material[material]
        sec=BoxSection(name,mat,h,b,tw,tf)
        self.__beam_section[name]=sec

    def add_beam_section_circle(self,name:str,material:str,d):
        mat=self.__material[material]
        sec=CircleSection(name,mat,d)
        self.__beam_section[name]=sec

    def add_beam_section_pipe(self,name:str,material:str,d,t):
        mat=self.__material[material]
        sec=PipeSection(name,mat,d,t)
        self.__beam_section[name]=sec

    def add_beam(self,name:str,start:str,end:str,section:str,check_dup=False):
        node0=self.__nodes[start]
        node1=self.__nodes[end]
        section=self.__beam_section[section]
        beam=Beam(name,node0,node1,section)
        if check_dup:
            tol=Tolerance.abs_tol()
            res=[b for b in self.__beams.values() 
                if (np.linalg.norm(b.start-node0.loc)<tol and np.linalg.norm(b.end-node1.loc)<tol)
                or (np.linalg.norm(b.end-node0.loc)<tol and np.linalg.norm(b.start-node1.loc)<tol)]
        else:
            res=[]
        if res==[]:
            res=len(self.__beams)
            self.__hid["beam"][name]=res
            self.__beams[name]=beam
        else:
            res=self.__hid["beam"][res[0].name]
        return res
        
    def add_simple_beam(self,name:str,start:str,end:str,E:float, mu:float, A:float, I2:float, I3:float, J:float, rho:float,check_dup=False):
        node0=self.__nodes[start]
        node1=self.__nodes[end]
        beam=SimpleBeam(name,node0,node1,E, mu, A, I2, I3, J, rho)
        if check_dup:
            tol=Tolerance.abs_tol()
            res=[b for b in self.__beams.values() 
                if (np.linalg.norm(b.start-node0.loc)<tol and np.linalg.norm(b.end-node1.loc)<tol)
                or (np.linalg.norm(b.end-node0.loc)<tol and np.linalg.norm(b.start-node1.loc)<tol)]
        else:
            res=[]
        if res==[]:
            res=len(self.__beams)
            self.__hid["beam"][name]=res
            self.__beams[name]=beam
        else:
            res=self.__hid["beam"][res[0].name]
        return res
    
    def set_beam_rotation(self,name:str,rotation:float):
        """
        set beams axis.
        
        params:
            beam: hid of beam
            x,y,z coordinate of reference vector.
        """
        beam=self.__beams[name]
        pass
    
    def set_beam_releases(self,name:str,
        u1i=False,u2i=False,u3i=False,r1i=False,r2i=False,r3i=False,
        u1j=False,u2j=False,u3j=False,r1j=False,r2j=False,r3j=False):
        self.beams[name].releases=np.array([u1i,u2i,u3i,r1i,r2i,r3i,u1j,u2j,u3j,r1j,r2j,r3j])

    def get_beam_reaction(self,name:str,
        u1i:float,u2i:float,u3i:float,r1i:float,r2i:float,r3i:float,
        u1j:float,u2j:float,u3j:float,r1j:float,r2j:float,r3j:float):
        d=np.array([u1i,u2i,u3i,r1i,r2i,r3i,u1j,u2j,u3j,r1j,r2j,r3j])
        return self.beams[name].f(d)

    def get_node_names(self):
        return list(self.__nodes.keys())

    def get_node_location(self,name):
        return self.__nodes[name].loc

    def get_nodal_mass(self,name:str):
        return self.__nodes[name].mass

    def get_beam_names(self):
        return list(self.__beams.keys())

    def get_beam_connection(self,name:str):
        return self.__beams[name].nodes[0].name,self.__beams[name].nodes[1].name

    def get_node_hid(self,name:str):
        return self.__hid['node'][name]

    def get_beam_hid(self,name:str):
        return self.__hid['beam'][name]

    def get_beam_node_hids(self,name:str):
        beam=self.__beams[name]
        nodes=beam.get_node_names()
        return [self.get_node_hid(name) for name in nodes]

    def get_beam_length(self,name:str):
        return self.__beams[name].length

    def get_node_transform_matrix(self,name:str):
        node=self.__nodes[name]
        return node.transform_matrix

    def get_node_M(self,name:str):
        node=self.__nodes[name]
        return node.integrate_M()

    def get_beam_transform_matrix(self,name:str):
        beam=self.__beams[name]
        return beam.transform_matrix

    def get_beam_K(self,name:str):
        beam=self.__beams[name]
        return beam.integrate_K()     

    def get_beam_M(self,name:str):
        beam=self.__beams[name]
        return beam.integrate_M()

    def get_beam_shape_function(self,name:str):
        beam=self.__beams[name]
        return beam.get_shape_function()

    def get_beam_interpolate(self,name:str,loc:float):
        beam=self.__beams[name]
        return beam.interpolate(loc)\

    def get_beam_interpolate1(self,name:str,loc:float):
        beam=self.__beams[name]
        return beam.interpolate1(loc)

    def get_beam_condensated_matrix(self,name:str,KMC):
        beam=self.__beams[name]
        return beam.static_condensate(KMC)

    def get_beam_condensated_f(self,name:str,re):
        beam=self.__beams[name]
        K=beam.integrate_K()
        return beam.static_condensate_f(re,K)
        
    def add_membrane3(self,node0, node1, node2, t, E, mu, rho, name=None):
        """
        add membrane to model
        if membrane already exits, it will not be added.
        return: membrane hidden id
        """
        node0=self.nodes[node0]
        node1=self.nodes[node1]
        node2=self.nodes[node2]
        elm=Membrane3(node0, node1, node2, t, E, mu, rho, name)
        res=len(self.__membrane3s)
        elm.hid=res
        self.__membrane3s[res]=elm
        return res
    
    def add_membrane4(self,node0, node1, node2, node3, t, E, mu, rho, name=None):
        """
        add membrane to model
        if membrane already exits, it will not be added.
        return: membrane hidden id
        """
        node0=self.nodes[node0]
        node1=self.nodes[node1]
        node2=self.nodes[node2]
        node3=self.nodes[node3]
        elm=Membrane4(node0, node1, node2, node3, t, E, mu, rho, name)
        res=len(self.__membrane4s)
        elm.hid=res
        self.__membrane4s[res]=elm
        return res             

    def find(self,nodes,target,tol=1e-6):
        """
        binary search target in nodes.
        nodes；node list to search
        target: node to find
        [tol]: tolerance
        return: node id or False
        """
        if len(nodes)==0:
            return False
        if len(nodes)==1:
            dist=abs(nodes[0].x-target.x)+abs(nodes[0].y-target.y)+abs(nodes[0].z-target.z)
            if dist<tol:
                return nodes[0].hid
            else:
                return False
        mid=len(nodes)//2
        A=nodes[:mid]
        B=nodes[mid:]
        return self.find(A,target) or self.find(B,target)
