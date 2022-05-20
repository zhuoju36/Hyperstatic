# -*- coding: utf-8 -*-
import os
import pickle
import numpy as np
from structengpy.common import logger
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load import LoadCase


class Assembly(object):
    def __init__(self,model:Model,load:LoadCase):
        self.__model=model
        self.__load=load


    def assemble_K(self):
        """
        Assemble integrated stiffness matrix.
        Meanwhile, The force vector will be initialized.
        """
        logger.info('Assembling K and M..')
        n_nodes=self.__model.node_count
        __K = spr.csr_matrix((n_nodes*6, n_nodes*6))
        __f = np.zeros((n_nodes*6, 1))
        #Beam load and displacement, and reset the index 
        row_k=[]
        col_k=[]
        data_k=[]
        for elm in self.__model.get_beam_names():
            i,j=self.__model.get_beam_node_hids()
            T=self.__model.get_beam_transform_matrix()
            Tt = T.transpose()

            #Static condensation to consider releases
            Ke=self.__model.get_beam_K()

            re=np.zeros(12)
            # Ke,Me,re=elm.static_condensation(Ke,Ke,re)

            Ke_ = (Tt*Ke*T).tocoo()
            
            data_k.extend(Ke_.data)
            row_k.extend([i*6+r if r<6 else j*6+r-6 for r in Ke_.row])
            col_k.extend([i*6+c if c<6 else j*6+c-6 for c in Ke_.col])
                      
        __K=spr.coo_matrix((data_k,(row_k,col_k)),shape=(n_nodes*6, n_nodes*6)).tocsr()
        
        # for elm in self.__membrane3s.values():
        #     i = elm.nodes[0].hid
        #     j = elm.nodes[1].hid
        #     k = elm.nodes[2].hid
            
        #     T=elm.transform_matrix
        #     Tt = T.transpose()

        #     Ke=elm.integrate_K()
        #     Me=elm.integrate_M()
            
        #     #expand
        #     row=[a for a in range(0*6,0*6+6)]+\
        #         [a for a in range(1*6,1*6+6)]+\
        #         [a for a in range(2*6,2*6+6)]

        #     col=[a for a in range(i*6,i*6+6)]+\
        #         [a for a in range(j*6,j*6+6)]+\
        #         [a for a in range(k*6,k*6+6)]
        #     elm_node_count=elm.node_count
        #     data=[1]*(elm_node_count*6)
        #     G=spr.csr_matrix((data,(row,col)),shape=(elm_node_count*6,n_nodes*6))
            
        #     Ke_ = spr.csr_matrix(np.dot(np.dot(Tt,Ke),T))
        #     __K+=G.transpose()*Ke_*G #sparse matrix use * as dot.
            
        # for elm in self.__membrane4s.values():
        #     i = elm.nodes[0].hid
        #     j = elm.nodes[1].hid
        #     k = elm.nodes[2].hid
        #     l = elm.nodes[3].hid
            
        #     T=elm.transform_matrix
        #     Tt = T.transpose()

        #     Ke=elm.Ke
            
        #     #transform
        #     Ke_ = spr.csr_matrix(Tt.dot(Ke).dot(T))
            
        #     #expand
        #     row=[a for a in range(0*6,0*6+6)]+\
        #         [a for a in range(1*6,1*6+6)]+\
        #         [a for a in range(2*6,2*6+6)]+\
        #         [a for a in range(3*6,3*6+6)]

        #     col=[a for a in range(i*6,i*6+6)]+\
        #         [a for a in range(j*6,j*6+6)]+\
        #         [a for a in range(k*6,k*6+6)]+\
        #         [a for a in range(l*6,l*6+6)]
        #     elm_node_count=elm.node_count
        #     data=[1]*(elm_node_count*6)
            
        #     G=spr.csr_matrix((data,(row,col)),shape=(elm_node_count*6,n_nodes*6))
        #     #assemble
        #     __K+=G.transpose()*Ke_*G #sparse matrix use * as dot.
        return __K

    def assemble_KM(self):
        """
        Assemble integrated stiffness matrix and mass matrix.
        Meanwhile, The force vector will be initialized.
        """
        logger.info('Assembling K and M..')
        n_nodes=self.node_count
        __K = spr.csr_matrix((n_nodes*6, n_nodes*6))
        __M = spr.csr_matrix((n_nodes*6, n_nodes*6))
        __C = spr.eye(n_nodes*6).tocsr()*0.05
        __f = np.zeros((n_nodes*6, 1))
        #Beam load and displacement, and reset the index 
        row_k=[]
        col_k=[]
        data_k=[]
        row_m=[]
        col_m=[]
        data_m=[]
        for elm in self.__beams.values():
            i = elm.nodes[0].hid
            j = elm.nodes[1].hid
            T=elm.transform_matrix
            Tt = T.transpose()

            #Static condensation to consider releases
            Ke=elm.integrate_K()
            Me=elm.integrate_M()
            re=np.zeros(12)
            Ke,Me,re=elm.static_condensation(Ke,Me,re)

            Ke_ = (Tt*Ke*T).tocoo()
            Me_ = (Tt*Me*T).tocoo()
            
            data_k.extend(Ke_.data)
            row_k.extend([i*6+r if r<6 else j*6+r-6 for r in Ke_.row])
            col_k.extend([i*6+c if c<6 else j*6+c-6 for c in Ke_.col])
            
            data_m.extend(Me_.data)
            row_m.extend([i*6+r if r<6 else j*6+r-6 for r in Me_.row])
            col_m.extend([i*6+c if c<6 else j*6+c-6 for c in Me_.col])
#                        
#            row=[a for a in range(0*6,0*6+6)]+[a for a in range(1*6,1*6+6)]
#            col=[a for a in range(i*6,i*6+6)]+[a for a in range(j*6,j*6+6)]
#            data=[1]*(2*6)
#            G=spr.csr_matrix((data,(row,col)),shape=(2*6,n_nodes*6))
#            
#            Ke_ = Tt*Ke*T
#            Me_ = Tt*Me*T
#            self.__K+=G.transpose()*Ke_*G #sparse matrix use * as dot.
#            self.__M+=G.transpose()*Me_*G #sparse matrix use * as dot.
            
        __K=spr.coo_matrix((data_k,(row_k,col_k)),shape=(n_nodes*6, n_nodes*6)).tocsr()
        __M=spr.coo_matrix((data_m,(row_m,col_m)),shape=(n_nodes*6, n_nodes*6)).tocsr()
        
        for elm in self.__membrane3s.values():
            i = elm.nodes[0].hid
            j = elm.nodes[1].hid
            k = elm.nodes[2].hid
            
            T=elm.transform_matrix
            Tt = T.transpose()

            Ke=elm.integrate_K()
            Me=elm.integrate_M()
            
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

            __K+=G.transpose()*Ke_*G #sparse matrix use * as dot.
            __M+=G.transpose()*Me_*G #sparse matrix use * as dot.
            
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
            __K+=G.transpose()*Ke_*G #sparse matrix use * as dot.
            __M+=G.transpose()*Me_*G #sparse matrix use * as dot.
        #### other elements
        return __K,__M

    def assemble_f(self,casename):
        """
        Assemble load vector and displacement vector.
        """
        logger.info('Assembling f..')
        n_nodes=self.__model.node_count
#        self.__f = spr.coo_matrix((n_nodes*6,1))
        #Beam load and displacement, and reset the index
        data_f=[]
        row_f=[]
        col_f=[]
        for node in self.__model.get_node_names():
            Tt=self.__model.get_node_transform_matrix().transpose()
#            self.__f[node.hid*6:node.hid*6+6,0]=np.dot(Tt,node.fn) 
            fn=self.__loadcase[casename].get_nodal_load_vec(node)
            fn_=np.dot(Tt,fn)
            k=0
            for f in fn_.reshape(6):
                if f!=0:
                    hid=self.__model.get_node_hid(node)
                    data_f.append(f)
                    row_f.append(hid*6+k)
                    col_f.append(0)
                k+=1
            
        for beam in self.__model.get_beam_names():
            i,j=self.__model.get_beam_node_hids()
            #Transform matrix
            Vl=np.matrix(self.__model.get_beam_transform_matrix(beam))
            V=np.zeros((12, 12))
            V[:3,:3] =V[3:6,3:6]=V[6:9,6:9]=V[9:,9:]=Vl
            Vt = V.transpose()
            
            re=self.__loadcase[casename].get_beam_load_vec(beam.name)
            re_=np.dot(Vt,re)
            k=0
            for r in re_.reshape(12):
                if r!=0:
                    data_f.append(r)
                    row_f.append(i*6+k if k<6 else j*6+k-6)
                    col_f.append(0)
                k+=1    
#            row=[a for a in range(0*6,0*6+6)]+[a for a in range(1*6,1*6+6)]
#            col=[a for a in range(i*6,i*6+6)]+[a for a in range(j*6,j*6+6)]
#            data=[1]*(2*6)
#            G=spr.csr_matrix((data,(row,col)),shape=(2*6,n_nodes*6))
#            #Assemble nodal force vector
#            self.__f += G.transpose()*np.dot(Vt,beam.re)
        #### other elements
        __f=spr.coo_matrix((data_f,(row_f,col_f)),shape=(n_nodes*6,1)).tocsr()
        return __f

    def assemble_boundary(self,mode='KMCf'):
        """
        assemble boundary conditions,using diagonal element englarging method.
        params:
            mode: 'K','M','C','f' or their combinations
        """
        logger.info('Assembling boundary condition..')
        if 'K' in mode:
            self.__K_=self.K.copy()
        if 'M' in mode:
            self.__M_=self.M.copy()
        if 'C' in mode:
            self.__C_=self.C.copy()
        if 'f' in mode:
            self.__f_=self.f.copy()
        self.__dof=self.node_count*6
        alpha=1e10
        for node in self.__nodes.values():
            i=node.hid
            for j in range(6):
                if node.dn[j]!= None:
                    if 'K' in mode:
                        self.__K_[i*6+j,i*6+j]*=alpha
                    if 'M' in mode:
                        self.__M_[i*6+j,i*6+j]*=alpha
                    if 'C' in mode:
                        self.__C_[i*6+j,i*6+j]*=alpha
                    if 'f' in mode:
                        self.__f_[i*6+j]=self.__K_[i*6+j,i*6+j]*node.dn[j]
                    self.__dof-=1

    def save(self,path,filename):
        with open(os.path.join(path,filename)) as f:
            pickle.dump(self,f)