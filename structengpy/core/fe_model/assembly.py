# -*- coding: utf-8 -*-
import os
import pickle
import numpy as np
from typing import Dict
import scipy.sparse as spr
import logging
from structengpy.core.fe_model.load.loadcase import ModalCase
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load import LoadCase

class Assembly(object):
    def __init__(self,model:Model,loadcases:list):
        self.__model:Model=model
        self.__loadcase={}
        for lc in loadcases:
            self.__loadcase[lc.name]=lc
        self.__dof:int=self.node_count*6

    @property
    def DOF(self):
        return self.__dof

    @property
    def node_count(self):
        return self.__model.node_count

    def get_node_hid(self,node:str):
        return self.__model.get_node_hid(node)

    def get_node_transform_matrix(self,node:str):
        return self.__model.get_node_hid(node)

    def get_beam_hid(self,elm:str):
        return self.__model.get_beam_hid(elm)

    def get_beam_node_hids(self,beam:str):
        return self.__model.get_beam_node_hids(beam)

    def get_beam_transform_matrix(self,elm:str):
        return self.__model.get_beam_transform_matrix(elm)

    def get_beam_K(self,elm:str):
        return self.__model.get_beam_K(elm)

    # def get_static_case_setting(self,case:str):
    #     if not type(self.__loadcase) is StaticCase:
    #         raise Exception("Loadcase %s not static case"%case)
    #     setting={}
    #     lc:StaticCase=self.__loadcase
    #     return setting

    # def get_modal_case_setting(self,case:str):
    #     if not type(self.__loadcase) is ModalCase:
    #         raise Exception("Loadcase %s not modal case"%case)
    #     setting={}
    #     lc:ModalCase=self.__loadcase
    #     setting["num"]=lc.num
    #     setting["isRitz"]=lc.isRitz
    #     return setting

    def assemble_K(self):
        # logging.info('Assembling K and M..')
        n_nodes=self.__model.node_count
        __K = spr.csr_matrix((n_nodes*6, n_nodes*6))
        #Beam load and displacement, and reset the index 
        row_k=[] 
        col_k=[]
        data_k=[]
        for elm in self.__model.get_beam_names():
            i,j=self.__model.get_beam_node_hids(elm)
            T=self.__model.get_beam_transform_matrix(elm)
            Tt = T.transpose()
            #Static condensation to consider releases
            Ke=self.__model.get_beam_K(elm)
            Ke=self.__model.get_beam_condensated_matrix(elm,Ke)

            Ke_ = (Tt*Ke*T).tocoo()

            data_k.extend(Ke_.data)
            row_k.extend([i*6+r if r<6 else j*6+r-6 for r in Ke_.row])
            col_k.extend([i*6+c if c<6 else j*6+c-6 for c in Ke_.col])

        __K=spr.coo_matrix((data_k,(row_k,col_k)),shape=(n_nodes*6, n_nodes*6)).tocsr()
        return __K

    def assemble_M(self,casename:str=None):
        n_nodes=self.__model.node_count
        __M = spr.csr_matrix((n_nodes*6, n_nodes*6))
        row_m=[] 
        col_m=[]
        data_m=[]

        if casename!=None and self.__loadcase[casename].use_load_as_mass:
            return spr.diags(self.assemble_f(casename),format="csr")/9.81
        
        for node in self.__model.get_node_names():
            i=self.__model.get_node_hid(node)
            T=self.__model.get_node_transform_matrix(node)
            Tt=T.transpose
            Mn=self.__model.get_node_M(node)
            if len(Mn.data)!=0:
                data_m.extend(Mn.data)
                row_m.extend([i*6+r for r in Mn.row])
                col_m.extend([i*6+c for c in Mn.col])

        for elm in self.__model.get_beam_names():
            i,j=self.__model.get_beam_node_hids(elm)
            T=self.__model.get_beam_transform_matrix(elm)
            Tt = T.transpose()
            #Static condensation to consider releases
            Me=self.__model.get_beam_M(elm)
            Me=self.__model.get_beam_condensated_matrix(elm,Me)

            Me_ = (Tt*Me*T).tocoo()

            data_m.extend(Me_.data)
            row_m.extend([i*6+r if r<6 else j*6+r-6 for r in Me_.row])
            col_m.extend([i*6+c if c<6 else j*6+c-6 for c in Me_.col])

        __M=spr.coo_matrix((data_m,(row_m,col_m)),shape=(n_nodes*6, n_nodes*6)).tocsr()
        return __M

    def assemble_KM(self):
        """
        Assemble integrated stiffness matrix and mass matrix.
        Meanwhile, The force vector will be initialized.
        """
        logging.info('Assembling K and M..')
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

    def assemble_f(self,casename:str):
        """
        Assemble load vector and displacement vector.
        """
        logging.info('Assembling f..')
        n_nodes=self.__model.node_count
#        self.__f = spr.coo_matrix((n_nodes*6,1))
        #Beam load and displacement, and reset the index
        data_f=[]
        row_f=[]
        col_f=[]
        loadcase=self.__loadcase[casename]
        for node in self.__model.get_node_names():
            T=self.__model.get_node_transform_matrix(node)
            Tt=T.transpose()
#            self.__f[node.hid*6:node.hid*6+6,0]=np.dot(Tt,node.fn) 
            fn=loadcase.get_nodal_f(node)
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
            i,j=self.__model.get_beam_node_hids(beam)
            l=self.__model.get_beam_length(beam)
            #Transform matrix
            V=self.__model.get_beam_transform_matrix(beam)
            Vt = V.transpose()
            re=loadcase.get_beam_f(beam,l)
            re=self.__model.get_beam_condensated_f(beam,re)
            re_=Vt.dot(re)
            k=0
            for r in re_.reshape(12):
                if r!=0:
                    data_f.append(r)
                    row_f.append(i*6+k if k<6 else j*6+k-6)
                    col_f.append(0)
                k+=1
            # row=[a for a in range(0*6,0*6+6)]+[a for a in range(1*6,1*6+6)]
            # col=[a for a in range(i*6,i*6+6)]+[a for a in range(j*6,j*6+6)]
            # data=[1]*(2*6)
            # G=spr.csr_matrix((data,(row,col)),shape=(2*6,n_nodes*6))
            # #Assemble nodal force vector
            # self.__f += G.transpose()*re_
        #### other elements
        __f=spr.coo_matrix((data_f,(row_f,col_f)),shape=(n_nodes*6,1)).tocsr()
        return __f

    def assemble_boundary(self,casename:str,matrixK:spr.spmatrix,matrixM:spr.spmatrix=None,matrixC:spr.spmatrix=None,vectorF:spr.spmatrix=None):
        logging.info('Assembling boundary condition..')
        loadcase=self.__loadcase[casename]
        K=matrixK.copy()
        if matrixM is not None:
            M=matrixM.copy()
        if matrixC is not None:
            C=matrixC.copy()
        if vectorF is not None:
            f=vectorF.copy()
        alpha=1e10
        rest=loadcase.get_nodal_restraint_dict()
        for node in rest.keys():
            i=self.__model.get_node_hid(node)
            for j in range(6):
                if rest[node][j]:
                    K[i*6+j,i*6+j]*=alpha
                    if matrixM is not None:
                        M[i*6+j,i*6+j]*=alpha
                    if matrixC is not None:
                        C[i*6+j,i*6+j]*=alpha
                    if vectorF is not None:
                        f[i*6+j]=0
                    self.__dof-=1

        # disp=self.__loadcase.get_nodal_disp_dict()
        # for node in disp.keys():
        #     i=self.__model.get_node_hid(node)
        #     for j in range(6):
        #         if disp[node][j]!= None:
        #             K[i*6+j,i*6+j]*=alpha
        #             if vectorF!=None:
        #                 f[i*6+j]=K[i*6+j,i*6+j]*disp[node][j]
        #             self.__dof-=1
        res=[K]
        if matrixM is not None:
            res.append(M)
        if matrixC is not None:
            res.append(C)
        if vectorF is not None:
            res.append(f)
        if len(res)==1:
            return K
        else:
            return tuple(res)

    def restraintDOF(self,casename:str):
        loadcase=self.__loadcase[casename]
        rest=loadcase.get_nodal_restraint_dict()
        dof=[]
        for node in rest.keys():
            i=self.__model.get_node_hid(node)
            for j in range(6):
                if rest[node][j]:
                    dof.append(i*6+j)
        return dof

    def save(self,path,filename):
        if not os.path.exists(path):
            os.mkdir(path)
        with open(os.path.join(path,filename),'wb+') as f:
            pickle.dump(self,f)


if __name__ == '__main__':
    import sys
    from structengpy.core.fe_model.model import Model
    from structengpy.core.fe_model.load.pattern import LoadPattern
    from structengpy.core.fe_model.load.loadcase import StaticCase

    model=Model()
    model.add_node("1",0,0,0)
    model.add_node("2",6,0,0)
    model.add_node("3",12,0,0)
    model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)
    model.add_beam("B","2","3",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

    patt1=LoadPattern("pat1")
    patt1.set_beam_load_dist("A",qi3=-1e4,qj3=-1e4)
    patt1.set_beam_load_dist("B",qi3=-1e4,qj3=-1e4)

    lc=StaticCase("case1")
    lc.add_pattern(patt1,1.0)
    lc.set_nodal_restraint("1",True,True,True,True,True,True)
    lc.set_nodal_restraint("3",True,True,True,True,True,True)
    
    asb=Assembly(model,lc)
    K=asb.assemble_K()
    f=asb.assemble_f("case1")
    K_,f_ =asb.assemble_boundary("case1",K,f)
    print(f)