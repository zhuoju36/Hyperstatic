# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:36:52 2018

@author: Dell
"""

import numpy as np

from .Node import Node

class FEModel:
    def __init__(self):
        self.__nodes={}
        self.__beams={}
        self.__quads={}
                
        self.__index=[]
        self.__dof=None
        #without restraint
        self.__K=None
        self.__M=None
        self.__C=None
        self.__f=None
        self.__d=None
        #with restraint
        self.__K_bar=None
        self.__M_bar=None
        self.__C_bar=None
        self.__f_bar=None
        self.__d_bar=None
        
        self.is_solved=False
        
    @property
    def node_count(self):
        return len(self.__nodes.items())

    @property
    def beam_count(self):
        return len(self.__beams.items())
    
    @property
    def quad_count(self):
        return len(self.__quads.items())

    @property
    def is_assembled(self):
        return self.__dof != None
        
    @property 
    def index(self):
        return self.__index

    @property
    def DOF(self):
        return self.__dof
    
    @property
    def K(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__K
    @property
    def M(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__M    
    @property
    def f(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__f
    @property
    def d(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__d
    @property
    def K_(self):
        if not self.is_assembled:
            raise Exception('The model has to be assembled first.')
        return self.__K_bar
    @property
    def M_(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__M_bar
    @property
    def f_(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__f_bar
    @property
    def d_(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__d_bar
        
    def add_node(self,node,tol=1e-6):
        """
        add node to model
        if node already exits, node will not be added.
        return: node hidden id
        """
#        res=self.find(list(self.__nodes.values()),node)
        res=[a.hid for a in self.__nodes.values() if abs(a.x-node.x)+abs(a.y-node.y)+abs(a.z-node.z)<1e-6]
        if res==[]:
            res=len(self.__nodes)
            node.hid=res
            self.__nodes[res]=node
        else:
            res=res[0]
        return res
        
    def add_beam(self,beam):
        """
        add beam to model
        if beam already exits, beam will not be added.
        return: beam hidden id
        """
        res=[a.hid for a in self.__beams.values() 
            if (a.nodes[0]==beam.nodes[0] and a.nodes[1]==beam.nodes[1]) 
            or (a.nodes[0]==beam.nodes[1] and a.nodes[1]==beam.nodes[0])]
        if res==[]:
            res=len(self.__beams)
            beam.hid=res
            self.__beams[res]=beam
        else:
            res=res[0]
        return res
        
    def assemble_KM(self):
        """
        Assemble integrated stiffness matrix and mass matrix.
        """
        n_nodes=self.node_count
        self.__K = np.zeros((n_nodes*6, n_nodes*6))
        self.__M = np.zeros((n_nodes*6, n_nodes*6))       
        #Beam load and displacement, and reset the index   
        for beam in self.__beams.values():
            i = beam.nodes[0].hid
            j = beam.nodes[1].hid
            T=beam.transform_matrix
            Tt = T.transpose()

            #Static condensation to consider releases
            beam.static_condensation()
            Kij=beam.Ke_
            Mij=beam.Me_
            
            #Assemble Total Stiffness Matrix
            Ke = np.dot(np.dot(Tt,Kij),T)
            Keii = Ke[:6,:6]
            Keij = Ke[:6,6:]
            Keji = Ke[6:,:6]
            Kejj = Ke[6:,6:]
            self.__K[i*6:i*6+6, i*6:i*6+6] += Keii
            self.__K[i*6:i*6+6, j*6:j*6+6] += Keij
            self.__K[j*6:j*6+6, i*6:i*6+6] += Keji
            self.__K[j*6:j*6+6, j*6:j*6+6] += Kejj
            
            #Assembel Mass Matrix        
            Me = np.dot(np.dot(Tt,Mij),T)
            Meii = Me[:6,:6]
            Meij = Me[:6,6:]
            Meji = Me[6:,:6]
            Mejj = Me[6:,6:]
            self.__M[i*6:i*6+6, i*6:i*6+6] += Meii
            self.__M[i*6:i*6+6, j*6:j*6+6] += Meij
            self.__M[j*6:j*6+6, i*6:i*6+6] += Meji
            self.__M[j*6:j*6+6, j*6:j*6+6] += Mejj
        #### other elements

    def assemble_f(self):
        """
        Assemble load vector and displacement vector.
        """
        n_nodes=self.node_count
        self.__f = np.zeros((n_nodes*6,1))
        #Beam load and displacement, and reset the index
        for node in self.__nodes.values():
            T=node.transform_matrix.transpose()
            self.__f[node.hid*6:node.hid*6+6]=np.dot(T,node.fn)        
            
        for beam in self.__beams.values():
            i = beam.nodes[0].hid
            j = beam.nodes[1].hid 
            #Transform matrix
            Vl=np.matrix(beam.local_csys.transform_matrix)
            V=np.zeros((6, 6))
            V[:3,:3] =V[3:,3:]= Vl
            Vt = V.transpose()
            #Assemble nodal force vector
            self.__f[i*6:i*6+6] += np.dot(Vt,beam.re[:6])
            self.__f[j*6:j*6+6] += np.dot(Vt,beam.re[6:])
        #### other elements

    def assemble_boundary(self):
#        Logger.info('Eliminating matrix...')
        self.__K_bar=self.K.copy()
        self.__M_bar=self.M.copy()
        self.__f_bar=self.f.copy()
        self.__dof=self.node_count*6
        for node in self.__nodes.values():
            i=node.hid
            for j in range(6):
                if node.dn[j]!= None:
                    self.__K_bar[i*6+j,i*6+j]*=1e10
                    self.__M_bar[i*6+j,i*6+j]*=1e10
                    self.__f_bar[i*6+j]=self.__K_bar[i*6+j,i*6+j]*node.dn[j]
                    self.__dof-=1
        
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

import scipy.sparse as sp
from scipy import linalg as sl 

def solve_linear(model):
    K_,f_=model.K_,model.f_
    #sparse matrix solution
    delta =np.dot(sl.pinv(K_),f_)
    model.is_solved=True
    return delta