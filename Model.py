# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:32:57 2016

@author: HZJ
"""
import numpy as np
import scipy.sparse as sp
from scipy import linalg
import Material
import Section
import Node
import Beam

class Model:
    def __init__(self,file):
#        DBParser dp
#        dp.OpenDataBase(file.c_str())
#        dp.GetModel(materials, sections, nodes, beams)
#        dp.CloseDataBase()
        #*************************************************Modeling**************************************************/
        #Q345
        self.materials=[]
        self.sections=[]
        self.nodes=[]
        self.beams=[]
        
        self.materials.append(Material.Material(2.000E11, 0.3, 7849.0474, 1.17e-5))
        #H200x150x8x10
        self.sections.append(Section.Section(self.materials[0], 4.800E-3, 1.537E-7, 3.196E-5, 5.640E-6))
        self.nodes.append(Node.Node(0, 0, 0))
        self.nodes.append(Node.Node(5, 0, 0))
        for i in range(len(self.nodes)-1):
            self.beams.append(Beam.Beam(self.nodes[i], self.nodes[i+1], self.sections[0]))
        #loads
        #double f[6] = { 0,0,-100000,0,0,0 }
        qi=(0,0,-10,0,0,0)
        qj=(0,0,-10,0,0,0)
        #double d[6] = { 1,0,0,0,0,0 }
        self.beams[0].SetLoadDistributed(qi, qj)
        #beams[3].SetLoadDistributed(qi, qj)
        #nodes[3].SetLoad(f)
        #nodes[0].SetDisp(d)
        #supports
        res1 = [True]*6
        res2 = [False]*6
        res3 = [False,True, True, True, True, True ]
        self.nodes[0].SetRestraints(res1)
        self.nodes[1].SetRestraints(res2)
        #nodes[5].SetRestraints(res1)
        #releases
        #beams[3].releaseJ[4] = True
#        self.beams[3].releaseJ[5] = True
        #*************************************************Modeling**************************************************/

    def Assemble(self):
        """
        Assemble matrix
        Writing the matrix to the disk
        """
        nid = 0
        # Dynamic space allocate
        self.Kmat = np.zeros((len(self.nodes)*6, len(self.nodes)*6))
        self.Mmat = np.zeros((len(self.nodes)*6, len(self.nodes)*6))
        self.Fvec = np.zeros(len(self.nodes)*6)
        self.Dvec = np.zeros(len(self.nodes)*6)

        #Nodal load and displacement, and reset the index
        for node in self.nodes:
            node.id = nid
            load = np.array(node.load)
            self.Fvec[nid * 6: nid * 6 + 6] = np.dot(node.TransformMatrix().transpose(),load)
            for i in range(6):
                if node.disp[i] != 0:
                    self.Dvec[nid * 6 + i] = node.disp[i]
            nid+=1
        nid = 0
        #Beam load and displacement, and reset the index
        for beam in self.beams:
            beam.Id = nid
            i = beam.nodeI.id
            j = beam.nodeJ.id
            T=np.matrix(beam.TransformMatrix())
            Tt = T.transpose()

            #Transform matrix
            Vl=np.matrix(beam.localCsys.TransformMatrix())
            V=np.zeros((6, 6))
            V[:3,:3] =V[3:,3:]= Vl
            Vt = V.transpose()

            #Static condensation to consider releases
            Kij=sp.bsr_matrix((12, 12))
            Mij=sp.bsr_matrix((12, 12))
            rij=sp.bsr_matrix((12))
            Kij, rij, Mij = beam.StaticCondensation(Kij, rij, Mij)

            #Assemble nodal force vector
            self.Fvec[i*6:i*6+6] += np.dot(Vt,rij[:6])
            self.Fvec[j*6:j*6+6] += np.dot(Vt,rij[6:])

            #Assemble Total Stiffness Matrix
            Ke = Tt*Kij*T
            Keii = Ke[:6,:6]
            Keij = Ke[:6,6:]
            Keji = Ke[6:,:6]
            Kejj = Ke[6:,6:]
            self.Kmat[i*6:i*6+6, i*6:i*6+6] += Keii
            self.Kmat[i*6:i*6+6, j*6:j*6+6] += Keij
            self.Kmat[j*6:j*6+6, i*6:i*6+6] += Keji
            self.Kmat[j*6:j*6+6, j*6:j*6+6] += Kejj

            #Assembel Mass Matrix        
            Me = Tt*Mij*T
            Meii = Me[:6,:6]
            Meij = Me[:6,6:]
            Meji = Me[6:,:6]
            Mejj = Me[6:,6:]
            self.Mmat[i*6:i*6+6, i*6:i*6+6] += Meii
            self.Mmat[i*6:i*6+6, j*6:j*6+6] += Meij
            self.Mmat[j*6:j*6+6, i*6:i*6+6] += Meji
            self.Mmat[j*6:j*6+6, j*6:j*6+6] += Mejj

            nid+=1

    def isAssembled(self):
        if self.Kmat == None:
            return False
        return True

    def K(self):
        return self.Kmat

    def F(self):
        return self.Fvec

    def EliminateMatrix(self, mass=None):
        """
        return 
        K_bar: sparse matrix
        F_bar: sparse matrix
        M_bar: sparse matrix
        index: vector
        """
        if mass==None:
            k = self.Kmat
            f = self.Fvec
            Id=np.arange(len(f))
            nRemoved=0
            i=0
            for node in self.nodes:
                for j in range(6):
                    if node.restraints[j] == True or node.disp[j] != 0:
                        k=np.delete(k,i*6+j-nRemoved,axis=0)
                        k=np.delete(k,i*6+j-nRemoved,axis=1)
                        f=np.delete(f,i*6+j-nRemoved)
                        Id=np.delete(Id,i*6+j-nRemoved)
                        nRemoved+=1
                i+=1
            K_bar = k
            F_bar = f
            index = Id
            return K_bar,F_bar,index
        else:
            k = self.Kmat
            m = self.Mmat
            f = self.Fvec
            Id=np.arange(len(f))
            nRemoved = 0
            for node in self.nodes:
                i = node.Id
                for j in range(6):
                    if node.restraints[j] == True or node.disp[j]!=0:
                        k=np.delete(k,i * 6 + j - nRemoved,axis=0)
                        k=np.delete(k,i * 6 + j - nRemoved,axis=1)
                        f=np.delete(f,i * 6 + j - nRemoved)
                        m=np.delete(m,i * 6 + j - nRemoved,axis=0)
                        m=np.delete(m,i * 6 + j - nRemoved,axis=1)
                        Id=np.delete(Id,i * 6 + j - nRemoved)
                        nRemoved+=1
            K_bar = k
            M_bar = m
            F_bar = f
            index = Id
            return K_bar,M_bar,F_bar,index

    def SolveLinear(self):
        self.Assemble()
        K_bar,F_bar,index = self.EliminateMatrix()
        try:
            #sparse matrix solution            
            print(K_bar.shape)
            print(F_bar.shape)
            delta_bar = linalg.inv(K_bar).dot(F_bar)
            
            delta = delta_bar
            f=np.zeros(len(self.beams)*12)
           
            #fill original displacement vector
            print(index)
            prev = 0
            for idx in index:
                gap=idx-prev
                if gap>0:
                    delta=np.insert(delta,prev,[0]*gap)
                prev = idx + 1               
                if idx==index[-1] and idx!=len(self.nodes)-1:
                    delta = np.insert(delta,prev, [0]*(len(self.nodes)*6-prev))
            print(delta)
            delta += self.Dvec

            #calculate element displacement and forces
            for beam in self.beams:
                Kij_bar=np.zeros((12, 12))
                rij_bar=np.zeros((12,1))
                Kij_bar,rij_bar=beam.StaticCondensation(Kij_bar, rij_bar)
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
                uij = np.dot(beam.TransformMatrix(),uij)
                
                fij = np.dot(Kij_bar,uij) + beam.NodalForce()
                for i in range(6):
                    if beam.releaseI[i] == True:
                        fij[i] = 0
                    if beam.releaseJ[i] == True:
                        fij[i + 6] = 0
                i=0
                for b in self.beams:
                    if beam is b:
                        bid=i
                    i+=1
                f[bid*12:bid*12+12] = fij
                print('I am here!!!')
            for n in range(len(self.nodes)):
                print("Disp of node "+str(n)+':')
                for i in range(n * 6,n * 6 + 6):
                   print("delta[%d"%(i - n * 6) +"]=%f"%delta[i])

            for n in range(len(self.beams)):
                print("Force of beam " +str(n)+ ':')
                for i in range(n*12,n*12+12):
                    print("f[%d"%(i - n * 12)+"]=%f"%f[i])
        except Exception as e:
            print(e)
            return False
        return True

#    def SolveModal(self)
#    {
#        self.Assemble()
#        sp_mat K_bar = sp_mat()
#        sp_mat M_bar = sp_mat()
#        vec F_bar = vec()
#        vec index = vec()
#        EliminateMatrix(K_bar, M_bar, F_bar, index)
#
#        try
#        {
#            #general eigen solution, should be optimized later!!
#            mat A(K_bar)
#            mat B(M_bar)
#            mat P = chol(B)
#            sp_mat S(P.i().t()*K_bar*P.i())
#            vec omega2
#            mat mode
#
#            ##############TEST##############
#            mat k = B
#            #cout.setf(ios::scientific)
#            for (int i = 0 i < k.n_rows i++)
#            {
#                for (int j = 0 j < k.n_cols j++)
#                {
#                    cout.width(6)
#                    cout.precision(4)
#                    cout.setf(ios::right)
#                    cout << k(i, j) << "  "
#                }
#                cout << endl
#            }
#            cout << endl
#            ##############TEST##############
#
#
#            cx_vec oega2 = eig_pair(A, B)
#            #eigs_sym(omega2, mode, S, 1,"sm")
#            #omega.for_each([](mat::elem_type& val) { std::sqrt(val) })
#            for (vec::iterator it = omega2.end() it != omega2.begin() it--)
#                cout << 2 * 3.14 / sqrt(*it) << endl
#
#            #extract vibration mode
#            vec delta_bar = normalise(mode.col(0))
#            vec delta(delta_bar)
#            vec f(self.beams.size() * 12, 1, fill::zeros)
#
#            #fill original displacement vector
#            int prev = 0
#            for (vec::iterator it = index.begin() it != index.end())
#            {
#                int gap = int(*it) - prev
#                if (gap > 0)
#                    delta.insert_rows(prev, gap)
#                prev = int(*it) + 1
#                it++
#                if (it == index.end() and *it != nodes.size() - 1)
#                    delta.insert_rows(prev, nodes.size() * 6 - prev)
#            }
#            delta += *Dvec
#
#            #calculate element displacement and forces
#            for (vector<Beam*>::iterator it = beams.begin() it != beams.end() it++)
#            {
#                sp_mat Kij_bar(12, 12)
#                sp_vec rij_bar(12)
#                (*it).StaticCondensation(Kij_bar, rij_bar)
#                vec::fixed<12> uij(fill::zeros)
#                vec::fixed<12> fij(fill::zeros)
#                int iend = (*it).nodeI.id
#                int jend = (*it).nodeJ.id
#                uij[0, 0, SizeMat(6, 1)) = delta.subvec(iend * 6, iend * 6 + 5)
#                uij[6, 0, SizeMat(6, 1)) = delta.subvec(jend * 6, jend * 6 + 5)
#                uij = (*it).TransformMatrix()*uij
#
#                fij = Kij_bar * uij + (*it).NodalForce()
#                for (int i = 0 i < 6 i++)
#                {
#                    if ((*it).releaseI[i] == True)
#                        fij(i) = 0
#                    if ((*it).releaseJ[i] == True)
#                        fij(i + 6) = 0
#                }
#                f.subvec((*it).id * 12, (*it).id * 12 + 11) = fij
#            }
#            for (int n = 0 n < nodes.size() n++)
#            {
#                cout << "Disp of node " << n << ':' << endl
#                for (int i = n * 6 i < n * 6 + 6 i++)
#                    cout << "delta[" << i - n * 6 << "]=" << delta[i] << endl
#                cout << endl
#            }
#
#            for n in range(len(beams))
#                cout << "Force of beam " << n << ':' << endl
#                for (int i = n * 12 i < n * 12 + 12 i++)
#                    cout << "f[" << i - n * 12 << "]=" << f[i] << endl
#                cout << endl
#        except Exception as e
#            return False
#        return True
#    }

    def SetMass(self):
        for beam in self.beams:
            beam.nodeI.mass += beam.section.A*beam.section.material.gamma*beam.Length() / 2
            beam.nodeJ.mass += beam.section.A*beam.section.material.gamma*beam.Length() / 2
        return False
        
if __name__=='__main__':        
    m=Model(1)
    m.Assemble()
    m.SolveLinear()