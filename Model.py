# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:32:57 2016

@author: HZJ
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sl
from scipy import linalg
import Material,Section,Node,Element

class fem_model:
    def __init__(self,path):
        self.__path=path
        self.__materials=[]
        self.__sections=[]
        self.__nodes=[]
        self.__beams=[]
        self.__quads=[]
        self.__is_solved=False
        
    def save(self):
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
            
    def save_result(self):    
        f=open(self.__path+'/result','w+')
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
        
    def add_material(self,mat:Material.material):
        self.__materials.append(mat)
        
    def add_section(self,sec:Section.section):
        self.__sections.append(sec)
        
    def add_node(self,node:Node.node):
        self.__nodes.append(node)
        
    def add_beam(self,beam:Element.beam):
        self.__beams.append(beam)
        
    def add_quad(self,quad):
        self.__quads.append(quad)
        
    def set_beam_distributed(self,idx,qi,qj):
        self.__beams[idx].loadI=qi
        self.__beams[idx].loadJ=qj
        
    def set_node_force(self,idx,P):
        self.__nodes[idx].load=P
        
    def set_node_restraint(self,idx,res):
        self.__nodes[idx].restraint=res
        
        
    def assemble(self):
        """
        Assemble matrix
        """
        # Dynamic space allocate
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

            disp = np.array(node.load)
            self.__Dvec[nid * 6: nid * 6 + 6] = np.dot(node.transform_matrix.transpose(),disp)
#                for i in range(6):
#                    if node.disp[i] != 0:
#                        self.__Dvec[nid * 6 + i] = node.disp[i]
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
            Kij=sp.bsr_matrix((12, 12))
            Mij=sp.bsr_matrix((12, 12))
            rij=sp.bsr_matrix((12))

            Kij, rij, Mij = beam.static_condensation(Kij, rij, Mij)

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
        

    @property
    def is_assembled(self):
        if self.__Kmat == None:
            return False
        return True
        
    @property
    def is_solved(self):
        return self.__is_solved
        
    @is_solved.setter
    def is_solved(self,solved):
        self.__is_solved=solved

    @property
    def K(self):
        return self.__Kmat

    @property
    def F(self):
        return self.__Fvec
        
    @property
    def D(self):
        return self.__Dvec

    def eliminate_matrix(self, mass=False):
        """
        return 
        K_bar: sparse matrix
        F_bar: sparse matrix
        M_bar: sparse matrix
        index: vector
        """
        if mass==False:
            k = self.K
            f = self.F
            Id=np.arange(len(f))
            for i in range(self.node_count-1,-1,-1):
                for j in range(5,-1,-1):
                    if self.nodes[i].restraint[j] == True or self.nodes[i].disp[j] != 0:
                        k=np.delete(k,i*6+j,axis=0)
                        k=np.delete(k,i*6+j,axis=1)
                        f=np.delete(f,i*6+j)
                        Id=np.delete(Id,i*6+j)

            K_bar = k
            F_bar = f
            index = Id
            for i in F_bar:
                print(i)
            return K_bar,F_bar,index
        else:
            k = self.__Kmat
            m = self.__Mmat
            f = self.__Fvec
            Id=np.arange(len(f))
            for i in range(self.node_count-1,-1,-1):
                for j in range(5,-1,-1):
                    if self.nodes[i].restraint[j] == True or self.nodes[i].disp[j] != 0:
                        k=np.delete(k,i*6+j,axis=0)
                        k=np.delete(k,i*6+j,axis=1)
                        m=np.delete(m,i*6+j,axis=0)
                        m=np.delete(m,i*6+j,axis=1)
                        f=np.delete(f,i*6+j)
                        Id=np.delete(Id,i*6+j)
            K_bar = k
            M_bar = m
            F_bar = f
            index = Id
            return K_bar,M_bar,F_bar,index
            
    def write_result(self,delta):
        
        for node in self.__nodes:
            node.res_disp=np.dot(node.transform_matrix,delta[node.hid*6:node.hid*6+6])
         
        #calculate element displacement and forces     
        for beam in self.__beams:
            Kij_bar=np.zeros((12, 12))
            rij_bar=np.zeros((12,1))
            Kij_bar,rij_bar=beam.static_condensation(Kij_bar, rij_bar)
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
        
        
if __name__=='__main__':        
    m=fem_model('d:/fem_model')
    steel=Material.linear_elastic(2.000E11, 0.3, 7849.0474, 1.17e-5)#Q345
    #i_section=Section.I_section(steel, 200,150,8,10)#H200x150x8x10
    i_section=Section.section(steel,4.265e-3,9.651e-8,6.572e-5,3.301e-6,4.313e-4,5.199e-5)
    m.add_material(steel)
    m.add_section(i_section)
    
#simple-supported beam
    m.add_node(Node.node(0, 0, 0))
    m.add_node(Node.node(14.28,0,0))
    m.add_node(Node.node(20,0,0))
    m.add_beam(Element.beam(m.nodes[0], m.nodes[1], i_section))
    m.add_beam(Element.beam(m.nodes[1], m.nodes[2], i_section))
    qi=(0,-10000,0,0,0,0)
    qj=(0,-10000,0,0,0,0)
    m.set_beam_distributed(0,qi,qj)
    m.set_beam_distributed(1,qi,qj)
    res1=[True,True,True,False,False,False]
    res2=[True,True,True,True,False,False]
    m.set_node_restraint(0,res1)
    m.set_node_restraint(2,res2)

##cantilever beam
#    m.add_node(Node.node(0, 0, 0))
#    m.add_node(Node.node(5,0,0))
#    m.add_beam(Element.beam(m.nodes[0], m.nodes[1], i_section))
#    qi=(0,0,-100,0,0,0)
#    qj=(0,0,-100,0,0,0)
#    m.set_beam_distributed(0,qi,qj)
#    res=[True]*6
#    m.set_node_restraint(0,res)
    m.save()
    m.assemble() 

    import Solver    
    #omegas,d=Solver.solve_modal(m,3)
#    m.write_result(d[0])
    d=Solver.solve_linear(m)
    m.write_result(d)
    if m.is_solved:
        m.save_result()
        
#            f=open('d:/fem_model/K_o','w+')
#            K=Ke
#            for i in range(K.shape[0]):
#                for j in range(K.shape[1]):
#                    f.write('%10.0f '%K[i,j])
#                f.write('\n')
#            f.close()