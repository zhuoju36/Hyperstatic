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
from .node import Node
from .element import *

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
        self.__K_=None
        self.__M_=None
        self.__C_=None
        self.__f_=None
        
        #results
        self.__d_=None
        self.__r_=None
        self.__omega_=None
        
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
        return self.__K
    @property
    def M(self):
        return self.__M    
    @property
    def f(self):
        return self.__f
    @property
    def d(self):
        return self.__d
    @property
    def K_(self):
        if not self.is_assembled:
            raise Exception('The model has to be assembled first.')
        return self.__K_
    @property
    def M_(self):
        if not self.is_assembled:
            raise Exception('The model has to be assembled first.')
        return self.__M_
    @property
    def f_(self):
        if not self.is_assembled:
            raise Exception('The model has to be assembled first.')
        return self.__f_
    
    @property
    def d_(self):
        return self.__d_
    @d_.setter
    def d_(self,d):
        assert(d.shape==(self.node_count*6,1))
        self.__d_=d
        
    @property
    def r_(self):
        return self.__r_
    @r_.setter
    def r_(self,r):
        assert(r.shape==(self.node_count*6,1))
        self.__r_=r
        
    @property
    def omega_(self):
        return self.__omega_
    @omega_.setter
    def omega_(self,omega):
        self.__omega_=omega
    @property
    def period(self):
        return 2*np.pi/(self.omega_)
        
    def add_node(self,x,y,z,check_dup=False,tol=1e-6):
        """
        add node to model
        
        params:
            x,y,z: float, coordinate of node.
        if node already exits, node will not be added.
        return: node hidden id
        """
        node=Node(x,y,z)
        if check_dup:
            res=[a.hid for a in self.__nodes.values() if abs(a.x-node.x)+abs(a.y-node.y)+abs(a.z-node.z)<1e-6]
        else:
            res=[]
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
        
    def add_beam(self,node0,node1,E, mu, A, I2, I3, J, rho,check_dup=False):
        """
        add beam to model
        
        params: 
            node0,node1: hid of nodes.
            check_dup: boolean, if True and beam already exits, it will not be added.
        return: 
            beam hidden id
        """
        node0=self.nodes[node0]
        node1=self.nodes[node1]
        beam=Beam(node0,node1,E, mu, A, I2, I3, J, rho)
        if check_dup: #should use a matrix to check, to be revised.
            res=[a.hid for a in self.__beams.values() 
                if (a.nodes[0]==beam.nodes[0] and a.nodes[1]==beam.nodes[1]) 
                or (a.nodes[0]==beam.nodes[1] and a.nodes[1]==beam.nodes[0])]
        else:
            res=[]
        if res==[]:
            res=len(self.__beams)
            beam.hid=res
            self.__beams[res]=beam
        else:
            res=res[0]
        return res
        
    def set_beam_force_by_frame_distributed(self,beam,q_i,q_j):
        """
        set beam force to model
        
        params:
            beam: int, hid of node
            q_i: list-like, 6 floats of frame's i-end distributed
            q_j: list-like, 6 floats of frame's j-end distributed
        return:
            bool, status of success
        """
        pass
    
    def set_beam_force_by_frame_concentrated(self,beam,force,loc):
        """
        set beam force to model
        
        params:
            beam: int, hid of node
            force: list-like, 6 floats of frame's concentrated
            loc: location of load
        return:
            bool, status of success
        """
        pass
    
    def set_beam_force_by_area_to_frame(self,area,pressure):
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
        self.__f = spr.csr_matrix((n_nodes*6,1))
        #Beam load and displacement, and reset the index
        for node in self.__nodes.values():
            Tt=node.transform_matrix.transpose()
            self.__f[node.hid*6:node.hid*6+6,0]=np.dot(Tt,node.fn)        
            
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
            self.__K_=self.K.copy()
        if 'M' in mode:
            self.__M_=self.M.copy()
        if 'f' in mode:
            self.__f_=self.f.copy()
        self.__dof=self.node_count*6
        alpha=1e9
        for node in self.__nodes.values():
            i=node.hid
            for j in range(6):
                if node.dn[j]!= None:
                    if 'K' in mode:
                        self.__K_[i*6+j,i*6+j]*=alpha
                    if 'M' in mode:
                        self.__M_[i*6+j,i*6+j]*=alpha
                    if 'f' in mode:
                        self.__f_[i*6+j]=self.__K_[i*6+j,i*6+j]*node.dn[j]
                    self.__dof-=1
                    
    def resolve_node_disp(self,node_id):
        if not self.is_solved:
            raise Exception('The model has to be solved first.')
        if node_id in self.__nodes.keys():
            node=self.__nodes[node_id]
            T=node.transform_matrix
            return np.dot(T,self.d_[node_id*6:node_id*6+6]).reshape(6)
        else:
            raise Exception("The node doesn't exists.")

    
    def resolve_node_reaction(self,node_id):
        if not self.is_solved:
            raise Exception('The model has to be solved first.')
        if node_id in self.__nodes.keys():
            node=self.__nodes[node_id]
            T=node.transform_matrix
            return T.dot(np.array(self.r_[node_id*6:node_id*6+6,0])).reshape(6)
        else:
            raise Exception("The node doesn't exists.")       
    
    def resolve_beam_force(self,beam_id):
        if not self.is_solved:
            raise Exception('The model has to be solved first.')
        if beam_id in self.__beams.keys():
            beam=self.__beams[beam_id]
            i=beam.nodes[0].hid
            j=beam.nodes[1].hid
            T=beam.transform_matrix
            ue=np.vstack([
                        self.d_[i*6:i*6+6],
                        self.d_[j*6:j*6+6]
                        ])   
            return (np.dot(beam.Ke_,T.dot(ue))+beam.re_).reshape(12)
        else:
            raise Exception("The element doesn't exists.")       


    
    def resolve_membrane3_stress(self,membrane_id):
        pass
    
    def resolve_membrane4_stress(self,membrane_id):
        pass
        
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
