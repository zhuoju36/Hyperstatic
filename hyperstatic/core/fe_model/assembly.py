# -*- coding: utf-8 -*-
import os
import pickle
import numpy as np
from typing import Dict,List
import scipy.sparse as spr
import logging
from hyperstatic.core.fe_model.load.loadcase import ModalCase, ResponseSpectrumCase
from hyperstatic.core.fe_model.model import Model
from hyperstatic.core.fe_model.load import LoadCase
import logging
class Assembly(object):
    def __init__(self,model:Model,loadcases:List[LoadCase]):
        self.__model:Model=model
        restraints=model.get_nodal_restraint_dict()
        self.__loadcase:Dict[str,LoadCase]={}
        for lc in loadcases:
            self.__loadcase[lc.name]=lc            
        self.__dof:int=self.node_count*6
        self.__fixed_dof=[]
        for node in restraints.keys():
            i=self.__model.get_node_hid(node)
            for j in range(6):
                if restraints[node][j]:
                    self.__fixed_dof.append(i*6+j)
                    self.__dof-=1
        
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

    def get_loadcase_setting(self,casename:str):
        loadcase=self.__loadcase[casename]
        return loadcase.get_settings()

    def get_max_min_step(self,casename:str):
        loadcase=self.__loadcase[casename]
        return loadcase.get_max_min_step()

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

        # for elm in self.__model.get_beam_names():
        #     i,j=self.__model.get_beam_node_hids(elm)
        #     row=np.arange(12)
        #     col=np.arange(12)
        #     col[:6]+=i*6
        #     col[6:]+=j*6-6
        #     data=np.ones(2*6)#[1]*(2*6)
        #     G=spr.csr_matrix((data,(row,col)),shape=(2*6,n_nodes*6))
        #     T=self.__model.get_beam_transform_matrix(elm)
        #     Ke=self.__model.get_beam_K(elm)
        #     Ke_ = T.T*Ke*T
        #     __K+=G.T*Ke_*G #sparse matrix use * as dot.

        # def preproc(elm):
        #     i,j=self.__model.get_beam_node_hids(elm)
        #     T=self.__model.get_beam_transform_matrix(elm)
        #     Ke=self.__model.get_beam_K(elm)
        #     Ke=self.__model.get_beam_condensated_matrix(elm,Ke)#Static condensation to consider releases
        #     Ke_ = (T.T*Ke*T).tocoo()
        #     data=Ke_.data
        #     row=Ke_.row
        #     col=Ke_.col
        #     row[:6]+=i*6
        #     col[:6]+=j*6-6
        #     return np.array([data,col,row])
        # drc=np.hstack(list(map(preproc,self.__model.get_beam_names())))
        # __K=spr.coo_matrix((drc[0],(drc[1],drc[2])),shape=(n_nodes*6, n_nodes*6))

        for elm in self.__model.get_beam_names():
            i,j=self.__model.get_beam_node_hids(elm)
            T=self.__model.get_beam_transform_matrix(elm)
            Ke=self.__model.get_beam_K(elm)
            Ke=self.__model.get_beam_condensated_matrix(elm,Ke)#Static condensation to consider releases
            Ke_ = (T.T*Ke*T).tocoo()
            data_k.extend(Ke_.data)
            row_k.extend([i*6+r if r<6 else j*6+r-6 for r in Ke_.row])
            col_k.extend([i*6+c if c<6 else j*6+c-6 for c in Ke_.col])
        for elm in self.__model.get_shell_names():
            hids=self.__model.get_shell_node_hids(elm)
            T=self.__model.get_shell_transform_matrix(elm)
            Ke=self.__model.get_shell_K(elm)
            Ke_ = (T.T*Ke*T).tocoo()            
            row=[]
            col=[]
            if len(hids)==4:
                i,j,k,l=hids
                for r in Ke_.row: #24x24
                    if r<6:
                        row.append(i*6+r%6)
                    elif r<12:
                        row.append(j*6+r%6)
                    elif r<18:
                        row.append(k*6+r%6)
                    else:
                        row.append(l*6+r%6)
                for c in Ke_.col:
                    if c<6:
                        col.append(i*6+c%6)
                    elif c<12:
                        col.append(j*6+c%6)
                    elif c<18:
                        col.append(k*6+c%6)
                    else:
                        col.append(l*6+c%6)
            elif len(hids)==3:
                i,j,k=hids
                for r in Ke_.row: #18x18
                    if r<6:
                        row.append(i*6+r%6)
                    elif r<12:
                        row.append(j*6+r%6)
                    else:
                        row.append(k*6+r%6)
                for c in Ke_.col:
                    if c<6:
                        col.append(i*6+c%6)
                    elif c<12:
                        col.append(j*6+c%6)
                    else:
                        col.append(k*6+c%6)
            data_k.extend(Ke_.data)
            row_k.extend(row)
            col_k.extend(col)
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

    def assemble_f(self,casename:str,time_step=0):
        n_nodes=self.__model.node_count
        data_f=[]
        row_f=[]
        col_f=[]
        loadcase=self.__loadcase[casename]
        for node in self.__model.get_node_names():
            T=self.__model.get_node_transform_matrix(node)
            Tt=T.transpose()
#            self.__f[node.hid*6:node.hid*6+6,0]=np.dot(Tt,node.fn) 
            fn=loadcase.get_nodal_f(node,time_step)
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
        __f=spr.coo_matrix((data_f,(row_f,col_f)),shape=(n_nodes*6,1)).tocsr()
        return __f

    def assemble_boundary(self,casename:str,array):
        loadcase:LoadCase=self.__loadcase[casename]
        rest=loadcase.get_nodal_restraint_dict()
        fixed=[]
        if rest=={}:
            fixed=self.__fixed_dof
        else:
            for node in rest.keys():
                i=self.__model.get_node_hid(node)
                for j in range(6):
                    if rest[node][j]:
                        fixed.append(i*6+j)
        A=array.copy()
        if A.shape[0]==1 or A.shape[1]==1:
            A=self.__drop_vector_dof(A,fixed).toarray()
        else:
            A=self.__drop_matrix_dof(A,fixed).tocsr()
        return A
 
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

    def __drop_vector_dof(self,V:spr.coo_matrix, indices:list)->np.array:
        keep = ~np.in1d(np.arange(V.shape[0]), indices)
        return V[keep].copy()

    def restraintDOF(self,casename:str=None):
        rest={}
        if casename is None:
            rest=self.__model.get_nodal_restraint_dict()
        else:
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
    # def drop_vector_dof(V:np.array, indices:list):
    #     keep = ~np.in1d(np.arange(V.shape[0]), indices)
    #     return V[keep].copy()

    # def __drop_matrix_dof(M:spr.coo_matrix, indices:list)->spr.coo_matrix:
    #     C = M
    #     keepr = ~np.in1d(C.row, indices)
    #     keepc = ~np.in1d(C.col, indices)
    #     keep=keepr*keepc
    #     data, row, col = C.data[keep], C.row[keep], C.col[keep]
    #     row2=row.copy()
    #     col2=col.copy()
    #     logging.info("start!")
    #     for i in reversed(sorted(indices)):
    #         row=[k-1 if k>i else k for k in row ]
    #         col=[k-1 if k>i else k for k in col ]
    #     logging.info("end!")

        
    #     logging.info("start!")
    #     k=1
    #     for i in reversed(sorted(indices)):
    #         row2[row2>i]-=k
    #         col2[col2>i]-=k
    #         # k+=1
    #     logging.info("end!")
    #     print(sorted(indices),C.row[keep],row,row2)
            
    #     A=spr.coo_matrix((data,(row,col)),shape=(C.shape[0]-len(indices),C.shape[1]-len(indices)))
    #     return A

    # A=np.array(range(25)).reshape(5,5)
    # A[1,1]=A[2,2]=0
    # A=spr.coo_matrix(A)
    # __drop_matrix_dof(A,[1,2])
    
    import sys
    from hyperstatic.core.fe_model.model import Model
    from hyperstatic.core.fe_model.load.pattern import LoadPattern
    from hyperstatic.core.fe_model.load.loadcase import StaticCase
    import time

    path="./test"
    if sys.platform=="win32":
        path="c:\\test"
    model=Model()
    N=10000
    l=6
    for i in range(N+1):
        model.add_node(str(i),l/N*i,0,0)
    for i in range(N):
        model.add_simple_beam("B"+str(i),str(i),str(i+1),E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

    patt1=LoadPattern("pat1")
    # patt1.set_beam_load_conc("A",M2=1e4,r=0.75)
    patt1.set_nodal_load(str(N),f3=1)
    lc=StaticCase("case1")
    lc.add_pattern(patt1,1.0)
    lc.set_nodal_restraint("0",False,False,True,True,True,False)
    
    asb=Assembly(model,[lc])
    beg=time.time()
    asb.assemble_K()
    end=time.time()
    print(end-beg)