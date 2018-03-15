# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 10:36:12 2016

@author: HZJ
"""

__all__=['CoordinateSystem','Element','Load','Loadcase','LoadCombination','Material','Node']

import numpy as np

import scipy.sparse as spr
from scipy.sparse import linalg as sl
import logger as log

class Model:
    def __init__(self):
        self.__nodes={}
        self.__beams={}
        self.__membrane3s={}
        self.__membrane4s={}
                
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
    def nodes(self):
        return self.__nodes
    
    @property
    def beams(self):
        return self.__beams
    
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
        
    def set_node_force(self,node,force,append=False):
        """
        add node force to model.
        params:
            node: int, hid of node
            force: list of 6 of nodal force
            append: bool, if True, the input force will be additional on current force.
        return:
            bool, status of success
        """
        assert(len(force)==6)
        if append:
            self.__nodes[node].fn+=np.array(force).reshape((6,1))
        else:
            self.__nodes[node].fn=np.array(force).reshape((6,1))
    
    def set_node_displacement(self,node,disp,append=False):
        """
        add node displacement to model
        params:
            node: int, hid of node
            disp: list of 6 of nodal displacement
            append: bool, if True, the input displacement will be additional on current displacement.
        return:
            bool, status of success
        """
        assert(len(disp)==6)
        if append:
            self.__nodes[node].dn+=np.array(disp).reshape((6,1))
        else:
            self.__nodes[node].dn=np.array(disp).reshape((6,1))
        
    def add_beam(self,beam):
        """
        add beam to model
        if beam already exits, it will not be added.
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
        
    def set_beam_force(self,beam,force):
        pass
        
    def add_membrane3(self,elm):
        """
        add membrane to model
        if membrane already exits, it will not be added.
        return: membrane hidden id
        """
        res=len(self.__membrane3s)
        elm.hid=res
        self.__membrane3s[res]=elm
        return res
    
    def add_membrane4(self,elm):
        """
        add membrane to model
        if membrane already exits, it will not be added.
        return: membrane hidden id
        """
        res=len(self.__membrane4s)
        elm.hid=res
        self.__membrane4s[res]=elm
        return res
        
    def assemble_KM(self):
        """
        Assemble integrated stiffness matrix and mass matrix.
        Meanwhile, The force vector will be initialized.
        """
        log.info('Assembling K and M..')
        n_nodes=self.node_count
        self.__K = spr.csr_matrix((n_nodes*6, n_nodes*6))
        self.__M = spr.csr_matrix((n_nodes*6, n_nodes*6))
        self.__f = np.zeros((n_nodes*6, 1))
        #Beam load and displacement, and reset the index 
        for elm in self.__beams.values():
            i = elm.nodes[0].hid
            j = elm.nodes[1].hid
            T=elm.transform_matrix
            Tt = T.transpose()

            #Static condensation to consider releases
            elm.static_condensation()
            Ke=elm.Ke_
            Me=elm.Me_

            row=[a for a in range(0*6,0*6+6)]+[a for a in range(1*6,1*6+6)]
            col=[a for a in range(i*6,i*6+6)]+[a for a in range(j*6,j*6+6)]
            data=[1]*(2*6)
            G=spr.csr_matrix((data,(row,col)),shape=(2*6,n_nodes*6))
            
            Ke_ = spr.csr_matrix(np.dot(np.dot(Tt,Ke),T))
            Me_ = spr.csr_matrix(np.dot(np.dot(Tt,Me),T))
            self.__K+=G.transpose()*Ke_*G #sparse matrix use * as dot.
            self.__M+=G.transpose()*Me_*G #sparse matrix use * as dot.
        
        for elm in self.__membrane3s.values():
            i = elm.nodes[0].hid
            j = elm.nodes[1].hid
            k = elm.nodes[2].hid
            
            T=elm.transform_matrix
            Tt = T.transpose()

            Ke=elm.Ke
            Me=elm.Me
            
            #expand
            row=[a for a in range(0*6,0*6+6)]+\
                [a for a in range(1*6,1*6+6)]+\
                [a for a in range(2*6,2*6+6)]

            col=[a for a in range(i*6,i*6+6)]+\
                [a for a in range(j*6,j*6+6)]+\
                [a for a in range(k*6,k*6+6)]
            elm_node_count=elm.node_count
            data=[1]*(elm_node_count*6)
            G=spr.csr_matrix((data,(row,col)),shape=(elm_node_count*6,n_nodes*6))
            
            Ke_ = spr.csr_matrix(np.dot(np.dot(Tt,Ke),T))
            Me_ = spr.csr_matrix(np.dot(np.dot(Tt,Me),T))

            self.__K+=G.transpose()*Ke_*G #sparse matrix use * as dot.
            self.__M+=G.transpose()*Me_*G #sparse matrix use * as dot.
            
        for elm in self.__membrane4s.values():
            i = elm.nodes[0].hid
            j = elm.nodes[1].hid
            k = elm.nodes[2].hid
            l = elm.nodes[3].hid
            
            T=elm.transform_matrix
            Tt = T.transpose()

            Ke=elm.Ke
            Me=elm.Me
            
            #transform
            Ke_ = spr.csr_matrix(Tt.dot(Ke).dot(T))
            Me_ = spr.csr_matrix(Tt.dot(Me).dot(T))
            
            #expand
            row=[a for a in range(0*6,0*6+6)]+\
                [a for a in range(1*6,1*6+6)]+\
                [a for a in range(2*6,2*6+6)]+\
                [a for a in range(3*6,3*6+6)]

            col=[a for a in range(i*6,i*6+6)]+\
                [a for a in range(j*6,j*6+6)]+\
                [a for a in range(k*6,k*6+6)]+\
                [a for a in range(l*6,l*6+6)]
            elm_node_count=elm.node_count
            data=[1]*(elm_node_count*6)
            
            G=spr.csr_matrix((data,(row,col)),shape=(elm_node_count*6,n_nodes*6))
            #assemble
            self.__K+=G.transpose()*Ke_*G #sparse matrix use * as dot.
            self.__M+=G.transpose()*Me_*G #sparse matrix use * as dot.
#        print(self.__K)
        #### other elements

    def assemble_f(self):
        """
        Assemble load vector and displacement vector.
        """
        log.info('Assembling f..')
        n_nodes=self.node_count
        self.__f = spr.lil_matrix((n_nodes*6,1))
        #Beam load and displacement, and reset the index
        for node in self.__nodes.values():
            T=node.transform_matrix.transpose()
            self.__f[node.hid*6:node.hid*6+6,0]=np.dot(T,node.fn)        
            
        for beam in self.__beams.values():
            i = beam.nodes[0].hid
            j = beam.nodes[1].hid 
            #Transform matrix
            Vl=np.matrix(beam.local_csys.transform_matrix)
            V=np.zeros((12, 12))
            V[:3,:3] =V[3:6,3:6]=V[6:9,6:9]=V[9:,9:]=Vl
            Vt = V.transpose()
            
            row=[a for a in range(0*6,0*6+6)]+[a for a in range(1*6,1*6+6)]
            col=[a for a in range(i*6,i*6+6)]+[a for a in range(j*6,j*6+6)]
            data=[1]*(2*6)
            G=spr.csr_matrix((data,(row,col)),shape=(2*6,n_nodes*6))
            #Assemble nodal force vector
            self.__f += G.transpose()*np.dot(Vt,beam.re)
        #### other elements

    def assemble_boundary(self,mode='KMf'):
        """
        assemble boundary conditions
        params:
            mode: 'K','M','f' or their combinations
        """
        log.info('Assembling boundary condition..')
        if 'K' in mode:
            self.__K_bar=self.K.copy()
        if 'M' in mode:
            self.__M_bar=self.M.copy()
        if 'f' in mode:
            self.__f_bar=self.f.copy()
        self.__dof=self.node_count*6
        for node in self.__nodes.values():
            i=node.hid
            for j in range(6):
                if node.dn[j]!= None:
                    if 'K' in mode:
                        self.__K_bar[i*6+j,i*6+j]*=1e10
                    if 'M' in mode:
                        self.__M_bar[i*6+j,i*6+j]*=1e10
                    if 'f' in mode:
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
