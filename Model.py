# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:32:57 2016

@author: HZJ
"""

import numpy as np
import scipy.sparse as sp
from Modeler import Material,Section,Load,Loadcase,LoadCombination,Node,Element
import Logger

class fem_model:
    def __init__(self,path):
        self.__version='0.0.1'
        self.__path=path
        self.__materials=[]
        self.__sections=[]
        self.__quad_sections=[]
        self.__loadcases=[]
        self.__combinations=[]
        
        self.__nodes=[]
        self.__beams=[]
        self.__quads=[]
        
        self.__load_point_concentrate=[]
        self.__load_beam_concentrate=[]
        self.__load_beam_distributed=[]
        self.__load_beam_strain=[]
        self.__load_beam_temperatrue=[]
        self.__load_quad_distributed=[]    
        self.__load_quad_to_beam=[]
        
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
    def version(self):
        return self.__version
        
    @property
    def loadcases(self):
        return self.__loadcases
        
    def save(self):  
        Logger.info('save document to %s/model'%self.__path)
        f=open(self.__path+'/model','w+')
        try:            
            f.write('!!!nodes!!!\n')
            for node in self.__nodes:
                f.write('%s,%s,%s,%s\n'%(node.name,node.x,node.y,node.z))
            f.write('!!!beams!!!\n')
            for beam in self.__beams:
                f.write('%s,%s,%s\n'%(beam.name,beam.nodeI.name,beam.nodeJ.name))
        except:
            pass
        finally:
            f.close()
        if not self.is_solved:
            return
            
    def save_result(self,lc):
        Logger.info('save document to %s/result'%self.__path)    
        f=open(self.__path+'/result_%s'%lc,'w+')
        try:
            f.write('!!!node disp!!!!\n')
            for node in self.__nodes:
                d=np.dot(node.transform_matrix.T,node.res_disp)                
                f.write('%s,%s,%s,%s,%s,%s,%s\n'%(node.name,d[0],d[1],d[2],d[3],d[4],d[5]))
            f.write('!!!beam disp!!!\n')
            for beam in self.__beams:
                d=np.dot(beam.transform_matrix.T,beam.res_disp)
                v=np.array([beam.nodeJ.x-beam.nodeI.x,beam.nodeJ.y-beam.nodeI.y,beam.nodeJ.z-beam.nodeI.z])
                loc=np.zeros(6)
                
                [phi,theta,psi]=d[3:6]    
                Ax=[[1,            0,           0],
                    [0,  np.cos(phi), np.sin(phi)],
                    [0, -np.sin(phi), np.cos(phi)]]
                Ay=[[np.cos(theta), 0, -np.sin(theta)],
                    [0,             1,              0],
                    [np.sin(theta), 0,  np.cos(theta)]]
                Az=[[ np.cos(psi), np.sin(psi), 0],
                    [-np.sin(psi), np.cos(psi), 0],
                    [           0,           0, 1]]             
                A=np.dot(np.dot(Az,Ay),Ax)
                loc[:3]=np.dot(v,A)
                
                [phi,theta,psi]=d[9:12]
                Ax=[[1,            0,           0],
                    [0,  np.cos(phi), np.sin(phi)],
                    [0, -np.sin(phi), np.cos(phi)]]
                Ay=[[np.cos(theta), 0, -np.sin(theta)],
                    [0,             1,              0],
                    [np.sin(theta), 0,  np.cos(theta)]]
                Az=[[ np.cos(psi), np.sin(psi), 0],
                    [-np.sin(psi), np.cos(psi), 0],
                    [           0,           0, 1]]
                A=np.dot(np.dot(Az,Ay),Ax)
                loc[3:]=np.dot(v,A)
                f.write('%s,%s,%s,%s,%s,%s,%s\n'%(beam.name,loc[0],loc[1],loc[2],loc[3],loc[4],loc[5]))
                #f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'%(beam.name,d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9],d[10],d[11]))
                #d=np.dot(beam.transform_matrix.T,beam.res_force)
                #f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'%(beam.name,d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9],d[10],d[11]))
        except:
            pass
        finally:
            f.close()           
    
    @property
    def node_count(self):
        return len(self.__nodes)

    @property
    def beam_count(self):
        return len(self.__beams)
    
    @property
    def quad_count(self):
        return len(self.__quads)
        
    @property
    def nodes(self):
        return self.__nodes
        
    @property
    def beams(self):
        return self.__beams
        
    @property
    def quads(self):
        return self.__quads

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
    @property
    def D_(self):
        if not self.is_assembled:
            return None
        return self.__D_bar
        
    def add_material(self,mat:Material.material):
        self.__materials.append(mat)
        
    def add_section(self,sec:Section.section):
        self.__sections.append(sec)
        
    def add_loadcase(self,lc: Loadcase.loadcase):
        self.__loadcases.append(lc)
        
    def add_combination(self,lc: Loadcase.loadcase):
        self.__combinations.append(lc)
        
    def add_node(self,node:Node.node):
        self.__nodes.append(node)
        
    def add_beam(self,beam:Element.beam):
        self.__beams.append(beam)
        
    def add_quad(self,quad):
        self.__quads.append(quad)
        
#    def set_beam_distributed(self,idx,qi,qj):
#        self.__beams[idx].loadI=qi
#        self.__beams[idx].loadJ=qj
#        
#    def set_node_force(self,idx,P):
#        self.__nodes[idx].load=P
#        
    def set_node_restraint(self,idx,res):
        self.__nodes[idx].restraint=res
        
    def add_point_concentrate(self,load):
        self.__load_point_concentrate.append(load)
        
    def add_beam_concentrate(self,load):
        self.__load_beam_concentrate.append(load)
        
    def add_beam_distributed(self,load):
        self.__load_beam_distributed.append(load)
        
    def add_load_beam_strain(self,load):
        self.__load_beam_strain.append(load)
        
    def add_beam_temperature(self,load):
        self.__load_beam_temperature.append(load)
        
    def add_quad_distributed(self,load):
        self.__load_quad_distributed.append(load)
        
    def add_quad_to_beam(self,load):
        self.__load_quad_to_beam.append(load)      
        
    def assemble(self):      
        
        Logger.info("Assembling %d nodes, %d beams and %d quads..."%(self.node_count,self.beam_count,self.quad_count))
        
        n_nodes=self.node_count
        self.__Kmat = np.zeros((n_nodes*6, n_nodes*6))
        self.__Mmat = np.zeros((n_nodes*6, n_nodes*6))
        self.__Fvec = np.zeros(n_nodes*6)
        self.__Dvec = np.zeros(n_nodes*6)

        #Nodal load and displacement, and reset the index
        nid = 0
        for node in self.nodes:
            node.hid = nid                
            load = np.array(node.load)
            self.__Fvec[nid * 6: nid * 6 + 6] = np.dot(node.transform_matrix.transpose(),load)

            disp = np.array(node.disp)
            self.__Dvec[nid * 6: nid * 6 + 6] = np.dot(node.transform_matrix.transpose(),disp)
            nid+=1
        
        #Beam load and displacement, and reset the index
        nid = 0    
        for beam in self.beams:
            beam.Id = nid
            i = beam.nodeI.hid
            j = beam.nodeJ.hid
            T=beam.transform_matrix
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
            
            nid+=1
        self.eliminate_matrix()

    def eliminate_matrix(self):
        """
        return 
        K_bar: sparse matrix
        F_bar: sparse matrix
        M_bar: sparse matrix
        index: vector
        """
        Logger.info('Eliminating matrix...')
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
            
    def assemble2(self,lc):
        """
        lc: name of the loadcase to be assemble.
        """
        Logger.info("Assembling %d nodes, %d beams and %d quads..."%(self.node_count,self.beam_count,self.quad_count))
        for load in self.__load_beam_concentrate:
            if load.lc!=lc:
                continue
            pass
        for load in self.__load_beam_distributed:
            if load.lc!=lc:
                continue
            for i in load.targets:
                self.beams[i].load_distributed(load.values_i,load.values_j)
        for load in self.__load_beam_strain:
            if load.lc!=lc:
                continue
            pass
        for load in self.__load_beam_temperatrue:
            if load.lc!=lc:
                continue
            pass
        for load in self.__load_point_concentrate:
            if load.lc!=lc:
                continue
            pass
        for load in self.__load_quad_distributed:
            if load.lc!=lc:
                continue
            pass
        for load in self.__load_quad_to_beam:
            if load.lc!=lc:
                continue
            pass
        
        to_rmv=[]
        Id=np.arange(self.node_count*6)
        for i in range(self.node_count-1,-1,-1):
            for j in range(5,-1,-1):
                if self.nodes[i].restraint[j] == True or self.nodes[i].disp[j] != 0:
                    to_rmv.append(i*6+j)

        self.__index=np.delete(Id,to_rmv)
        id_dic={}
        for i in self.__index:
           id_dic[i]=len(id_dic.keys()) 
        
        dof=self.__dof=len(self.__index)#degree of freedom
        self.__K_bar = np.zeros((dof, dof))
        self.__M_bar = np.zeros((dof, dof))
        self.__F_bar = np.zeros(dof)
        self.__Dvec = np.zeros(self.node_count*6)

        #Nodal load and displacement, and reset the index
        nid = 0
        for node in self.nodes:
            node.hid = nid                
            load = np.array(node.load)
            disp = np.array(node.disp)
            Fn=np.dot(node.transform_matrix.transpose(),load)
            Dn=np.dot(node.transform_matrix.transpose(),disp)
            for i in range(6):
                if nid*6+i in id_dic.keys():
                    v=id_dic[nid*6+i]
                    self.__F_bar[v]=Fn[i]
            self.__Dvec[nid * 6: nid * 6 + 6] = Dn
            nid+=1
        
        #Beam load and displacement, and reset the index
        nid = 0    
        for beam in self.beams:
            beam.Id = nid
            i = beam.nodeI.hid
            j = beam.nodeJ.hid
            T=beam.transform_matrix
            Tt = T.transpose()

            #Transform matrix
            Vl=np.matrix(beam.local_csys.transform_matrix)
            V=np.zeros((6, 6))
            V[:3,:3] =V[3:,3:]= Vl
            Vt = V.transpose()

            Kij, Mij, rij = beam.static_condensation()

            Ke = np.dot(np.dot(Tt,Kij),T)
            Keii = Ke[:6,:6]
            Keij = Ke[:6,6:]
            Keji = Ke[6:,:6]
            Kejj = Ke[6:,6:]
            
            Me = np.dot(np.dot(Tt,Mij),T)
            Meii = Me[:6,:6]
            Meij = Me[:6,6:]
            Meji = Me[6:,:6]
            Mejj = Me[6:,6:]
            
            for k in range(6):
                if i*6+k in id_dic.keys():
                    v=id_dic[i*6+k]
                    self.__F_bar[v] += np.dot(Vt,rij[:6])[k]
                if j*6+k in id_dic.keys():
                    v=id_dic[j*6+k]
                    self.__F_bar[v] += np.dot(Vt,rij[:6])[k]
                
            for k in range(6):
                for r in range(6):
                    if i*6+k in id_dic.keys() and i*6+r in id_dic.keys():
                        u=id_dic[i*6+k]
                        v=id_dic[i*6+r]
                        self.__K_bar[u, v] += Keii[k,r]
                        self.__M_bar[u, v] += Meii[k,r]
                    
                    if j*6+k in id_dic.keys() and j*6+r in id_dic.keys(): 
                        u=id_dic[j*6+k]
                        v=id_dic[j*6+r]
                        self.__K_bar[u, v] += Kejj[k,r]
                        self.__M_bar[u, v] += Mejj[k,r]
                
                    if i*6+k in id_dic.keys() and j*6+r in id_dic.keys():
                        u=id_dic[i*6+k]
                        v=id_dic[j*6+r]
                        self.__K_bar[u, v] += Keij[k,r]
                        self.__M_bar[u, v] += Meij[k,r]       
                    if j*6+k in id_dic.keys() and i*6+r in id_dic.keys():
                        u=id_dic[j*6+k]
                        v=id_dic[i*6+r]
                        self.__K_bar[u, v] += Keji[k,r]
                        self.__M_bar[u, v] += Meji[k,r] 
            nid+=1
        
    def clear_result(self):
        for node in self.__nodes:
            node.clear_result()
        for beam in self.__beams:
            beam.clear_result()
        self.is_solved=False
            
    def resolve_result(self,delta):      
        for node in self.__nodes:
            node.res_disp=np.dot(node.transform_matrix,delta[node.hid*6:node.hid*6+6])
         
        #calculate element displacement and forces     
        for beam in self.__beams:
            Kij_bar,Mij_bar_,rij_bar=beam.static_condensation()
            uij=np.zeros(12)
            fij=np.zeros(12)
            
            i=0
            for node in self.nodes:
                if node is beam.nodeI:
                    iend=i
                i+=1
            i=0
            for node in self.nodes:
                if node is beam.nodeJ:
                    jend=i
                i+=1
            
            uij[:6]=delta[iend*6:iend*6+6]
            uij[6:]=delta[jend*6:jend*6+6]
            uij = np.dot(beam.transform_matrix,uij)#set to local coordinate
            beam.res_disp=uij
            
            fij = np.dot(Kij_bar,uij) + beam.nodal_force
            for i in range(6):
                if beam.releaseI[i] == True:
                    fij[i] = 0
                if beam.releaseJ[i] == True:
                    fij[i + 6] = 0
            beam.res_force=fij
#            #beam.ID
#            f=np.zeros(len(self.beams)*12)
#            i=0
#            for b in self.__beams:
#                if beam is b:
#                    bid=i
#                i+=1
#            f[bid*12:bid*12+12] = fij

    def SetMass(self):
        for beam in self.beams:
            beam.nodeI.mass += beam.section.A*beam.section.material.gamma*beam.Length() / 2
            beam.nodeJ.mass += beam.section.A*beam.section.material.gamma*beam.Length() / 2
        return False
        
        
#if __name__=='__main__':   
#    from Solver import Static     
#    m=fem_model('d:/fem_model')
#    steel=Material.linear_elastic(2.000E11, 0.3, 7849.0474, 1.17e-5)#Q345
#    #i_section=Section.I_section(steel, 200,150,8,10)#H200x150x8x10
#    i_section=Section.section(steel,4.265e-3,9.651e-8,6.572e-5,3.301e-6,4.313e-4,5.199e-5)
#    m.add_material(steel)
#    m.add_section(i_section)
#    m.add_loadcase(Loadcase.loadcase('D'))
##simple-supported beam
#    m.add_node(Node.node(0, 0, 0))
#    m.add_node(Node.node(14.28,0,0))
#    m.add_node(Node.node(20,0,0))
#    m.add_beam(Element.beam(m.nodes[0], m.nodes[1], i_section))
#    m.add_beam(Element.beam(m.nodes[1], m.nodes[2], i_section))
#    qi=(0,-10000,0,0,0,0)
#    qj=(0,-10000,0,0,0,0)
#    m.add_beam_distributed(Load.beam_distributed(0,qi,qj))
#    m.add_beam_distributed(Load.beam_distributed(1,qi,qj))
#    res1=[True,True,True,False,False,False]
#    res2=[True,True,True,True,False,False]
#    m.set_node_restraint(0,res1)
#    m.set_node_restraint(2,res2)
#
###cantilever beam
##    m.add_node(Node.node(0, 0, 0))
##    m.add_node(Node.node(5,0,0))
##    m.add_beam(Element.beam(m.nodes[0], m.nodes[1], i_section))
##    qi=(0,0,-100,0,0,0)
##    qj=(0,0,-100,0,0,0)
##    m.set_beam_distributed(0,qi,qj)
##    res=[True]*6
##    m.set_node_restraint(0,res)
#    m.save()
#    m.assemble() 
#
##    T,d=Solver.solve_modal(m,6)
##    print(T)
##    m.write_result(d[0])
#    d=Static.solve_linear(m)
#    m.write_result(d)
#    if m.is_solved:
#        m.save_result()
#        
##            f=open('d:/fem_model/K_o','w+')
##            K=Ke
##            for i in range(K.shape[0]):
##                for j in range(K.shape[1]):
##                    f.write('%10.0f '%K[i,j])
##                f.write('\n')
##            f.close()