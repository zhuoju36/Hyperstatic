# -*- coding: utf-8 -*-
import numpy as np

from scipy.sparse import linalg as sl
from structengpy.common.tolerance import Tolerance

from structengpy.core.fe_model.node import Node
from structengpy.core.fe_model.element.line.beam import Beam
from structengpy.core.fe_model.element.tri.membrane import Membrane3
from structengpy.core.fe_model.element.quad.membrane import Membrane4

class Model:
    def __init__(self):
        self.__nodes={}
        self.__beams={}
        self.__membrane3s={}
        self.__membrane4s={}

        self.__hid={}
        self.__hid['node']={}
        self.__hid['beam']={}
        self.__hid['membrane3s']={}
        self.__hid['membrane4s']={}
                
        self.__index=[]
        self.__dof=None
        # #without restraint
        # self.__K=None
        # self.__M=None
        # self.__C=None
        # self.__f=None
        # self.__d=None
        # #with restraint
        # self.__K_=None
        # self.__M_=None
        # self.__C_=None
        # self.__f_=None
        
        # #results
        # self.__d_=None
        # self.__r_=None
        # self.__omega_=None
        # self.__mode_=None
        
        # self.is_solved=False
        self.__pattern={}
        self.__loadcase={}
        
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
    def membrane3s(self):
        return self.__membrane3s

    @property
    def membrane4s(self):
        return self.__membrane4s

    # @property
    # def is_assembled(self):
    #     return self.__dof != None
        
    @property 
    def index(self):
        return self.__index

    # @property
    # def DOF(self):
    #     return self.__dof
    
    # @property
    # def K(self):
    #     return self.__K
    # @property
    # def M(self):
    #     return self.__M 
    # @property
    # def C(self):
    #     return self.__C   
    # @property
    # def f(self):
    #     return self.__f
    # @property
    # def d(self):
    #     return self.__d
    # @property
    # def K_(self):
    #     if not self.is_assembled:
    #         raise Exception('The model has to be assembled first.')
    #     return self.__K_
    # @property
    # def M_(self):
    #     if not self.is_assembled:
    #         raise Exception('The model has to be assembled first.')
    #     return self.__M_
    # @property
    # def C_(self):
    #     if not self.is_assembled:
    #         raise Exception('The model has to be assembled first.')
    #     return self.__C_
    # @property
    # def f_(self):
    #     if not self.is_assembled:
    #         raise Exception('The model has to be assembled first.')
    #     return self.__f_
    
    # @property
    # def d_(self):
    #     return self.__d_
    # @d_.setter
    # def d_(self,d):
    #     assert(d.shape==(self.node_count*6,1))
    #     self.__d_=d
        
    # @property
    # def r_(self):
    #     return self.__r_
    # @r_.setter
    # def r_(self,r):
    #     assert(r.shape==(self.node_count*6,1))
    #     self.__r_=r
        
    # @property
    # def omega_(self):
    #     return self.__omega_
    # @omega_.setter
    # def omega_(self,omega):
    #     self.__omega_=omega
    
    # @property    
    # def mode_(self):
    #     return self.__mode_
    # @mode_.setter
    # def mode_(self,mode):
    #     self.__mode_=mode
    
    # @property
    # def period(self):
    #     return 2*np.pi/(self.omega_)
        
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
            
    # def set_node_restraint(self,node,restraint):
    #     """
    #     set node restraint to model.
    #     params:
    #         node: int, hid of node
    #         force: list of 6 of nodal force
    #         append: bool, if True, the input force will be additional on current force.
    #     return:
    #         bool, status of success
    #     """
    #     assert(len(restraint)==6)
    #     disp=[]
    #     for i in range(6):
    #         if restraint[i]:
    #             disp.append(0)
    #         else:
    #             disp.append(self.__nodes[node].dn[i])
    #     self.__nodes[node].dn=np.array(disp).reshape((6,1))
        
    def add_beam(self,name:str,start:str,end:str,E:float, mu:float, A:float, I2:float, I3:float, J:float, rho:float,check_dup=False):
        node0=self.__nodes[start]
        node1=self.__nodes[end]
        beam=Beam(name,node0,node1,E, mu, A, I2, I3, J, rho)
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
    
    def set_beam_releases(self,name:str,r1:str,r2:str):
        """
        set beams axis.
        
        params:
            beam: hid of beam
            r1: list-like, 6 bool of frame's i-end distributed
            r1: list-like, 6 bool of frame's i-end distributed
        """
        assert(len(r1)==6)
        assert(len(r2)==6)
        self.beams[name].releases=list(r1)+list(r2)

    def get_node_names(self):
        return list(self.__nodes.keys())

    def get_beam_names(self):
        return list(self.__beams.keys())

    def get_node_hid(self,name):
        return self.__hid['node'][name]

    def get_beam_hid(self,name):
        return self.__hid['beam'][name]

    def get_beam_node_hids(self,name):
        beam=self.__beams[name]
        nodes=beam.get_node_names()
        return [self.get_node_hid(name) for name in nodes]

    def get_node_transform_matrix(self,name):
        node=self.__nodes[name]
        return node.transform_matrix

    def get_beam_transform_matrix(self,name):
        beam=self.__beams[name]
        return beam.transform_matrix

    def get_beam_K(self,name):
        beam=self.__beams[name]
        return beam.integrate_K()


        
    # def set_beam_force_by_frame_distributed(self,beam,q_i,q_j):
    #     """
    #     set beam force to model
        
    #     params:
    #         beam: int, hid of node
    #         q_i: list-like, 6 floats of frame's i-end distributed
    #         q_j: list-like, 6 floats of frame's j-end distributed
    #     return:
    #         bool, status of success
    #     """
    #     pass
    
    # def set_beam_force_by_frame_concentrated(self,beam,force,loc):
    #     """
    #     set beam force to model
        
    #     params:
    #         beam: int, hid of node
    #         force: list-like, 6 floats of frame's concentrated
    #         loc: location of load
    #     return:
    #         bool, status of success
    #     """
    #     pass
    
    # def set_beam_force_by_area_to_frame(self,area,pressure):
    #     pass
        
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
