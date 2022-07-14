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

    def get_beam_shape_function(self,elm:str):
        return self.__model.get_beam_shape_function(elm)

    def get_beam_interpolate(self,elm:str,loc:float):
        return self.__model.get_beam_interpolate(elm,loc)

    def get_beam_interpolate1(self,elm:str,loc:float):
        return self.__model.get_beam_interpolate1(elm,loc)

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
        logging.info('Assembling K..')
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

        __K=spr.coo_matrix((data_k,(row_k,col_k)),shape=(n_nodes*6, n_nodes*6))
        return __K

    def assemble_M(self,casename:str=None):
        logging.info('Assembling M..')
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

        __M=spr.coo_matrix((data_m,(row_m,col_m)),shape=(n_nodes*6, n_nodes*6))
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
            
        __K=spr.coo_matrix((data_k,(row_k,col_k)),shape=(n_nodes*6, n_nodes*6))
        __M=spr.coo_matrix((data_m,(row_m,col_m)),shape=(n_nodes*6, n_nodes*6))
        
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

    def assemble_boundary(self,casename:str,matrixK:spr.csr_matrix,matrixM:spr.csr_matrix=None,matrixC:spr.csr_matrix=None,vectorF:spr.csr_matrix=None):
        logging.info('Assembling boundary condition..')
        loadcase:LoadCase=self.__loadcase[casename]
        K=matrixK.copy()
        if matrixM is not None:
            M=matrixM.copy()
        if matrixC is not None:
            C=matrixC.copy()
        if vectorF is not None:
            f=vectorF.copy()
        rest=loadcase.get_nodal_restraint_dict()
        fixed=[]
        for node in rest.keys():
            i=self.__model.get_node_hid(node)
            for j in range(6):
                if rest[node][j]:
                    fixed.append(i*6+j)
                    self.__dof-=1
        K=self.__drop_matrix_dof(K,fixed).tocsr()
        if matrixM is not None:
            M=self.__drop_matrix_dof(M,fixed).tocsr()
        if matrixC is not None:
            C=self.__drop_matrix_dof(C,fixed).tocsr()
        if vectorF is not None:
            f=self.__drop_vector_dof(f,fixed).toarray()
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
 
    def __drop_matrix_dof(self,M:spr.coo_matrix, indices:list)->spr.coo_matrix:
        keepr = ~np.in1d(M.row, indices)
        keepc = ~np.in1d(M.col, indices)
        keep=keepr*keepc
        data, row, col = M.data[keep], M.row[keep], M.col[keep] 
        for i in reversed(sorted(indices)):
            row[row>i]-=1
            col[col>i]-=1      
        A=spr.coo_matrix((data,(row,col)),shape=(M.shape[0]-len(indices),M.shape[1]-len(indices)))
        return A

    def __drop_vector_dof(self,V:spr.csr_matrix, indices:list)->np.array:
        keep = ~np.in1d(np.arange(V.shape[0]), indices)
        return V[keep].copy()

    # def assemble_boundary(self,casename:str,matrixK:spr.spmatrix,matrixM:spr.spmatrix=None,matrixC:spr.spmatrix=None,vectorF:spr.spmatrix=None):
    #     logging.info('Assembling boundary condition..')
    #     loadcase=self.__loadcase[casename]
    #     K=matrixK.copy()
    #     if matrixM is not None:
    #         M=matrixM.copy()
    #     if matrixC is not None:
    #         C=matrixC.copy()
    #     if vectorF is not None:
    #         f=vectorF.copy()
    #     alpha=1e10
    #     rest=loadcase.get_nodal_restraint_dict()
    #     for node in rest.keys():
    #         i=self.__model.get_node_hid(node)
    #         for j in range(6):
    #             if rest[node][j]:
    #                 K[i*6+j,i*6+j]*=alpha
    #                 if matrixM is not None:
    #                     M[i*6+j,i*6+j]*=alpha
    #                 if matrixC is not None:
    #                     C[i*6+j,i*6+j]*=alpha
    #                 if vectorF is not None:
    #                     f[i*6+j]=0
    #                 self.__dof-=1

        # disp=self.__loadcase.get_nodal_disp_dict()
        # for node in disp.keys():
        #     i=self.__model.get_node_hid(node)
        #     for j in range(6):
        #         if disp[node][j]!= None:
        #             K[i*6+j,i*6+j]*=alpha
        #             if vectorF!=None:
        #                 f[i*6+j]=K[i*6+j,i*6+j]*disp[node][j]
        #             self.__dof-=1
        # res=[K]
        # if matrixM is not None:
        #     res.append(M)
        # if matrixC is not None:
        #     res.append(C)
        # if vectorF is not None:
        #     res.append(f)
        # if len(res)==1:
        #     return K
        # else:
        #     return tuple(res)

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
    def drop_vector_dof(V:np.array, indices:list):
        keep = ~np.in1d(np.arange(V.shape[0]), indices)
        return V[keep].copy()

    def __drop_matrix_dof(M:spr.coo_matrix, indices:list)->spr.coo_matrix:
        C = M
        keepr = ~np.in1d(C.row, indices)
        keepc = ~np.in1d(C.col, indices)
        keep=keepr*keepc
        data, row, col = C.data[keep], C.row[keep], C.col[keep]
        row2=row.copy()
        col2=col.copy()
        logging.info("start!")
        for i in reversed(sorted(indices)):
            row=[k-1 if k>i else k for k in row ]
            col=[k-1 if k>i else k for k in col ]
        logging.info("end!")

        
        logging.info("start!")
        k=1
        for i in reversed(sorted(indices)):
            row2[row2>i]-=k
            col2[col2>i]-=k
            # k+=1
        logging.info("end!")
        print(sorted(indices),C.row[keep],row,row2)
            
        A=spr.coo_matrix((data,(row,col)),shape=(C.shape[0]-len(indices),C.shape[1]-len(indices)))
        return A

    A=np.array(range(25)).reshape(5,5)
    A[1,1]=A[2,2]=0
    A=spr.coo_matrix(A)
    __drop_matrix_dof(A,[1,2])