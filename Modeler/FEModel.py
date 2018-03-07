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
        self.__restraints={}
                
        self.__index=[]
        self.__dof=None
        #without restraint
        self.__K=self.__M=self.__C=None
        self.__F=self.__D=None
        #with restraint
        self.__K_bar=self.__M_bar=self.__C_bar=None
        self.__F_bar=self.__D_bar=None
        
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
    def F(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__F
    @property
    def D(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__D
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
    def F_(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__F_bar
    @property
    def D_(self):
        if not self.is_assembled:
            Exception('The model has to be assembled first.')
        return self.__D_bar
        
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
            
    def add_restraint(self,hid,res):
        for i in range(6):
            if type(res[i])!=bool:
                raise(ValueError('Restraint must be a 6 bool array.'))
        self.__restraints[hid]=res
        
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
            T=beam.T
            Tt = T.transpose()

            #Static condensation to consider releases
            Kij=beam.Ke
            Mij=beam.Me
            
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

    def assemble_FD(self):
        """
        Assemble load vector and displacement vector.
        """
        n_nodes=self.node_count
        self.__F = np.zeros((n_nodes*6,1))
        self.__D = np.zeros((n_nodes*6,1))        
        #Beam load and displacement, and reset the index
        for node in self.__nodes.values():
            T=node.transform_matrix.transpose()
            self.__F[node.hid*6:node.hid*6+6]=np.dot(T,node.Fn)
            self.__D[node.hid*6:node.hid*6+6]=np.dot(T,node.Dn)
            
        for beam in self.__beams.values():
            i = beam.nodes[0].hid
            j = beam.nodes[1].hid 
            #Transform matrix
            Vl=np.matrix(beam.local_csys.transform_matrix)
            V=np.zeros((6, 6))
            V[:3,:3] =V[3:,3:]= Vl
            Vt = V.transpose()
            #Assemble nodal force vector
            self.__F[i*6:i*6+6] += np.dot(Vt,beam.Re[:6])
            self.__F[j*6:j*6+6] += np.dot(Vt,beam.Re[6:])
        #### other elements

    def eliminate_matrix(self):
        """
        return 
        K_bar: sparse matrix
        F_bar: sparse matrix
        M_bar: sparse matrix
        index: vector
        """
#        Logger.info('Eliminating matrix...')
        k = self.__K
        m=self.__M
        f = self.__F
        to_rmv=[]
        Id=np.arange(len(f))
        for i in range(self.node_count-1,-1,-1):
            for j in range(5,-1,-1):
                if self.__nodes[i].restraint[j] == True or self.__nodes[i].Dn[j] != 0:
                    to_rmv.append(i*6+j)
        k=np.delete(k,to_rmv,axis=0)
        k=np.delete(k,to_rmv,axis=1)
        m=np.delete(m,to_rmv,axis=0)
        m=np.delete(m,to_rmv,axis=1)
        f=np.delete(f,to_rmv)
        Id=np.delete(Id,to_rmv)
        
        self.__K_bar = k
        self.__M_bar = m
        self.__F_bar = f
        self.__index = Id
        self.__dof=len(Id)
        
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
from scipy.sparse import linalg as sl        
def solve_linear(model):
    K_bar,F_bar,index=model.K_,model.F_,model.index
    D=model.D
    n_nodes=model.node_count
    
    #sparse matrix solution
    delta_ = sl.spsolve(sp.csr_matrix(K_bar),F_bar)
    
    delta = delta_
    #fill original displacement vector
    prev = 0
    for idx in index:
        gap=idx-prev
        if gap>0:
            delta=np.insert(delta,prev,[0]*gap)
        prev = idx + 1               
        if idx==index[-1] and idx!=n_nodes-1:
            delta = np.insert(delta,prev, [0]*(n_nodes*6-prev))
    delta=delta.reshape((n_nodes*6,1))
    delta += D
    
    model.is_solved=True
    return delta