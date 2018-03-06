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
        self.__forces={}
        self.__restraints={}
        self.__displacements={}
        
        self.__is_solved=False
        
        self.__index=[]
        self.__dof=None
        #without restraint
        self.__K=self.__M=self.__C=None
        self.__F=self.__D=None
        #with restraint
        self.__K_bar=self.__M_bar=self.__C_bar=None
        self.__F_bar=self.__D_bar=None
        
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
        if self.__dof == None:
            return False
        return True
        
    @property 
    def index(self):
        return self.__index
        
    @property
    def is_solved(self):
        return self.__is_solved
        
    @is_solved.setter
    def is_solved(self,solved):
        self.__is_solved=solved

    @property
    def DOF(self):
        return self.__dof
    @property
    def K(self):
        if not self.is_assembled:
            return None
        return self.__Kmat
    @property
    def M(self):
        if not self.is_assembled:
            return None
        return self.__Mmat        
    @property
    def F(self):
        if not self.is_assembled:
            return None
        return self.__Fvec        
    @property
    def D(self):
        if not self.is_assembled:
            return None
        return self.__Dvec
    @property
    def K_(self):
        if not self.is_assembled:
            return None
        return self.__K_bar
    @property
    def M_(self):
        if not self.is_assembled:
            return None
        return self.__M_bar
    @property
    def F_(self):
        if not self.is_assembled:
            return None
        return self.__F_bar
        
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
        
    def add_force(self,hid,load):
        if hid not in self.__forces.keys():
            self.__forces[hid]=np.zeros((6,1))
        self.__forces[hid]+=np.array(load).reshape(6,1)
            
    def add_restraint(self,hid,res):
        for i in range(6):
            if type(res[i])!=bool:
                raise(ValueError('restraint must be a 6 bool array.'))
        self.__restraints[hid]=res
        
        
    
        
    def assemble(self):      
        
#        Logger.info("Assembling %d nodes, %d beams and %d quads..."%(self.node_count,self.beam_count,self.quad_count))
        
        n_nodes=self.node_count
        self.__Kmat = np.zeros((n_nodes*6, n_nodes*6))
        self.__Mmat = np.zeros((n_nodes*6, n_nodes*6))
        self.__Fvec = np.zeros((n_nodes*6,1))
        self.__Dvec = np.zeros((n_nodes*6,1))

        for force in self.__forces.items():
            nid=force[0]
            self.__Fvec[nid * 6: nid * 6 + 6] = force[1].reshape(6,1)
#            self.__Dvec[nid * 6: nid * 6 + 6] = np.dot(node.transform_matrix.transpose(),disp)
        
        #Beam load and displacement, and reset the index   
        for beam in self.__beams.values():
            i = beam.nodes[0].hid
            j = beam.nodes[1].hid
            T=beam.T
            Tt = T.transpose()

            #Transform matrix
            Vl=np.matrix(beam.local_csys.transform_matrix)
            V=np.zeros((6, 6))
            V[:3,:3] =V[3:,3:]= Vl
            Vt = V.transpose()

            #Static condensation to consider releases
#            Kij=sp.bsr_matrix((12, 12))
#            Mij=sp.bsr_matrix((12, 12))
#            rij=sp.bsr_matrix((12))

            Kij, Mij, rij = beam.static_condensation()

            #Assemble nodal force vector
            self.__Fvec[i*6:i*6+6] += np.dot(Vt,rij[:6])
            self.__Fvec[j*6:j*6+6] += np.dot(Vt,rij[6:])

            #Assemble Total Stiffness Matrix
            Ke = np.dot(np.dot(Tt,Kij),T)
            Keii = Ke[:6,:6]
            Keij = Ke[:6,6:]
            Keji = Ke[6:,:6]
            Kejj = Ke[6:,6:]
            self.__Kmat[i*6:i*6+6, i*6:i*6+6] += Keii
            self.__Kmat[i*6:i*6+6, j*6:j*6+6] += Keij
            self.__Kmat[j*6:j*6+6, i*6:i*6+6] += Keji
            self.__Kmat[j*6:j*6+6, j*6:j*6+6] += Kejj
            
            #Assembel Mass Matrix        
            Me = np.dot(np.dot(Tt,Mij),T)
            Meii = Me[:6,:6]
            Meij = Me[:6,6:]
            Meji = Me[6:,:6]
            Mejj = Me[6:,6:]
            self.__Mmat[i*6:i*6+6, i*6:i*6+6] += Meii
            self.__Mmat[i*6:i*6+6, j*6:j*6+6] += Meij
            self.__Mmat[j*6:j*6+6, i*6:i*6+6] += Meji
            self.__Mmat[j*6:j*6+6, j*6:j*6+6] += Mejj

        self.eliminate_matrix()

    def eliminate_matrix(self):
        """
        return 
        K_bar: sparse matrix
        F_bar: sparse matrix
        M_bar: sparse matrix
        index: vector
        """
#        Logger.info('Eliminating matrix...')
        k = self.K
        m=self.M
        f = self.F
        to_rmv=[]
        Id=np.arange(len(f))
        for i in range(self.node_count-1,-1,-1):
            for j in range(5,-1,-1):
                if self.nodes[i].restraint[j] == True or self.nodes[i].disp[j] != 0:
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