# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 22:17:28 2016

@author: HZJ
"""
import uuid
import numpy as np
import scipy.sparse as sp
import CoordinateSystem
import Section

class element(object):
    def __init__(self,name=None):
        self.__name=uuid.uuid1() if name==None else name
        
    @property
    def name(self):
        return self.__name
        
    @property
    def elm_stiff_matrix(self):
        return self.__Kij

    @property
    def elm_mass_matrix(self):
        return self.__Mij
    
    @property
    def transform_matrix(self):
        T=np.zeros((12,12))
        V=self.local_csys.transform_matrix
        T[:3,:3] =T[3:6,3:6]=T[6:9,6:9]=T[9:,9:]= V
        return T
        
    

class beam(element):
    def __init__(self,i, j, sec:Section.section, name=None):
        self.__nodeI=i
        self.__nodeJ=j
        self.loadI=[0]*6
        self.loadJ=[0]*6
        self.releaseI=[False]*6
        self.releaseJ=[False]*6
        self.section=sec
        tol = 1E-6
        #results
        self.__res_force=None
        
        #Initialize local CSys
        o = [ self.nodeI.x, self.nodeI.y, self.nodeI.z ]
        pt1 = [ self.nodeJ.x, self.nodeJ.y, self.nodeJ.z ]
        pt2 = [ self.nodeI.x, self.nodeI.y, self.nodeI.z ]
        if abs(self.nodeI.x - self.nodeJ.x) < tol and abs(self.nodeI.y - self.nodeJ.y) < tol:
            pt2[0] += 1
        else:
            pt2[2] += 1
        self.local_csys = CoordinateSystem.cartisian(o, pt1, pt2)

        #Initialize local stiffness matrix
        l = self.length
        E = self.section.material.E
        A = self.section.A
        J = self.section.J
        G = self.section.material.G
        I2 = self.section.I22
        I3 = self.section.I33
        rho = self.section.material.gamma

        self.__Kij = np.zeros((12, 12))
        self.__Mij = np.zeros((12, 12))

        #form the stiffness matrix:
        self.__Kij[0, 0]=E*A / l
        self.__Kij[0, 6]=self.__Kij[6, 0]=-E*A / l

        self.__Kij[1, 1]=12 * E*I3 / l / l / l
        self.__Kij[1, 5]=self.__Kij[5, 1]=6 * E*I3 / l / l
        self.__Kij[1, 7]=self.__Kij[7, 1]=-12 * E*I3 / l / l / l
        self.__Kij[1, 11]=self.__Kij[11, 1]=6 * E*I3 / l / l

        self.__Kij[2, 2]=12 * E*I2 / l / l / l
        self.__Kij[2, 4]=self.__Kij[4, 2]=-6 * E*I2 / l / l
        self.__Kij[2, 8]=self.__Kij[8, 2]=-12 * E*I2 / l / l / l
        self.__Kij[2, 10]=self.__Kij[10, 2]=-6 * E*I2 / l / l

        self.__Kij[3, 3]=G*J / l
        self.__Kij[3, 9]=self.__Kij[9, 3]=-G*J / l

        self.__Kij[4, 4]=4 * E*I2 / l
        self.__Kij[4, 8]=self.__Kij[8, 4]=6 * E*I2 / l / l
        self.__Kij[4, 10]=self.__Kij[10, 4]=2 * E*I2 / l

        self.__Kij[5, 5]=4 * E*I3 / l
        self.__Kij[5, 7]=self.__Kij[7, 5]=-6 * E*I3 / l / l
        self.__Kij[5, 11]=self.__Kij[11, 5]=2 * E*I3 / l

        self.__Kij[6, 6]=E*A / l

        self.__Kij[7, 7]=12 * E*I3 / l / l / l
        self.__Kij[7, 11]=self.__Kij[11, 7]=-6 * E*I3 / l / l

        self.__Kij[8, 8]=12 * E*I2 / l / l / l
        self.__Kij[8, 10]=self.__Kij[10, 8]=6 * E*I2 / l / l

        self.__Kij[9, 9]=G*J / l

        self.__Kij[10, 10]=4 * E*I2 / l

        self.__Kij[11, 11]=4 * E*I3 / l

        #form mass matrix    
#        #Coordinated mass matrix
#        self.__Mij[0, 0]=140
#        self.__Mij[0, 6]=70
#
#        self.__Mij[1, 1]=156
#        self.__Mij[1, 5]=self.__Mij[5, 1]=22 * l
#        self.__Mij[1, 7]=self.__Mij[7, 1]=54
#        self.__Mij[1, 11]=self.__Mij[11, 1]=-13 * l
#
#        self.__Mij[2, 2]=156
#        self.__Mij[2, 4]=self.__Mij[4, 2]=-22 * l
#        self.__Mij[2, 8]=self.__Mij[8, 2]=54
#        self.__Mij[2, 10]=self.__Mij[10, 2]=13 * l
#
#        self.__Mij[3, 3]=140 * J / A
#        self.__Mij[3, 9]=self.__Mij[9, 3]=70 * J / A
#
#        self.__Mij[4, 4]=4 * l *l
#        self.__Mij[4, 8]=self.__Mij[8, 4]=-13 * l
#        self.__Mij[4, 10]=self.__Mij[10, 4]=-3 * l*l
#
#        self.__Mij[5, 5]=4 * l*l
#        self.__Mij[5, 7]=self.__Mij[7, 5]=13 * l
#        self.__Mij[5, 11]=self.__Mij[11, 5]=-3 * l*l
#
#        self.__Mij[6, 6]=140
#
#        self.__Mij[7, 7]=156
#        self.__Mij[7, 11]=self.__Mij[11, 7]=-22 * l
#
#        self.__Mij[8, 8]=156
#        self.__Mij[8, 10]=self.__Mij[10, 8]=22 * l
#
#        self.__Mij[9, 9]=140 * J / A
#
#        self.__Mij[10, 10]=4 * l*l
#
#        self.__Mij[11, 11]=4 * l*l
#
#        self.__Mij*= (rho*A*l / 420)

        #Concentrated mass matrix
        for i in range(12):
            self.__Mij[i, i]=1
        self.__Mij*=rho*A*l/2
        super().__init__(name)
    
    @property
    def nodeI(self):
        return self.__nodeI
    
    @property
    def nodeJ(self):
        return self.__nodeJ
        
    def initialize_csys(self):
        nodeI=self.nodeI
        nodeJ=self.nodeJ
        o = np.array([nodeI.x, nodeI.y, nodeI.z])
        pt1 = np.array([nodeJ.x, nodeJ.y, nodeJ.z])
        pt2 = np.array([0,0,0])
        if self.nodeI.x != self.nodeJ.x and self.nodeI.y != self.nodeJ.y:
            pt2[2] = 1
        else:
            pt2[0] = 1
        self.local_csys.set_by_3pts(o, pt1, pt2)

    @property
    def length(self):
        nodeI=self.nodeI
        nodeJ=self.nodeJ
        return np.sqrt((nodeI.x - nodeJ.x)*(nodeI.x - nodeJ.x) + (nodeI.y - nodeJ.y)*(nodeI.y - nodeJ.y) + (nodeI.z - nodeJ.z)*(nodeI.z - nodeJ.z))
    
    @property
    def nodal_force(self):
        l = self.length
        loadI=self.loadI
        loadJ=self.loadJ
        #recheck!!!!!!!!!!!!
        #i
        v=np.zeros(12)
        v[0]=(loadI[0] + loadJ[0]) * l / 2#P
        v[1]=(loadI[1] * 7 / 20 + loadJ[1] * 3 / 20) * l#V2
        v[2]=(loadI[2] * 7 / 20 + loadJ[2] * 3 / 20) * l#V3
        v[3]=loadI[3] - loadJ[3]#T
        v[4]=(loadI[2] / 20 + loadJ[2] / 30) * l * l + loadI[4]#M22
        v[5]=(loadI[1] / 20 + loadJ[1] / 30) * l * l + loadI[5]#M33
        #j
        v[6]=(loadJ[0] + loadI[0]) * l / 2#P
        v[7]=(loadJ[1] * 7 / 20 + loadI[1] * 3 / 20) * l#V2
        v[8]=(loadJ[2] * 7 / 20 + loadI[2] * 3 / 20) * l#V3
        v[9] = loadJ[3] - loadI[3]#T
        v[10] = -(loadJ[2] / 20 + loadI[2] / 30) * l * l + loadJ[4]#M22
        v[11] = -(loadJ[1] / 20 + loadI[1] / 30) * l * l + loadJ[5]#M33
        return v

    def static_condensation(self, kij_bar, rij_bar, mij_bar=None):
        """
        kij_bar: 12x12 matrix
        rij_bar: 12x1 vector
        mij_bar: 12x12 matrix, if mij_bar==None, mass matrix will not be considered
        return???refer????
        """
        if mij_bar is None:
            kij=self.__Kij
            rij=self.nodal_force
            kij_bar = kij
            rij_bar = rij
    
            for n in range(6):
                if self.releaseI[n] == True:
                    for i in range(12):
                        for j in range(12):
                            kij_bar[i, j] = kij[i, j] - kij[i, n]* kij[n, j] / kij[n, n]
                        rij_bar[i] = rij[i] - rij[n] * kij[n, i] / kij[n, n]
                if self.releaseJ[n] == True:
                    for i in range(12):
                        for j in range(12):
                            kij_bar[i, j] = kij[i, j] - kij[i, n + 6]* kij[n + 6, j] / kij[n + 6, n + 6]
                        rij_bar[i] = rij[i] - rij[n + 6] * kij[n + 6, i] / kij[n + 6, n + 6]
            return kij_bar, rij_bar
        else:
            kij=self.__Kij
            mij=self.__Mij
            rij=self.nodal_force
            kij_bar = kij
            mij_bar = mij
            rij_bar = rij
    
            for n in range(0,6):
                if self.releaseI[n] == True:
                    for i in range(12):
                        for j in range(12):
                            kij_bar[i, j] = kij[i, j] - kij[i, n]* kij[n, j] / kij[n, n]
                            mij_bar[i, j] = mij[i, j] - mij[i, n]* mij[n, j] / mij[n, n]
                        rij_bar[i] = rij[i] - rij[n] * kij[n, i] / kij[n, n]
                if self.releaseJ[n] == True:
                    for i in range(12):
                        for j in range(12):
                            kij_bar[i, j] = kij[i, j] - kij[i, n + 6]* kij[n + 6, j] / kij[n + 6, n + 6]
                            mij_bar[i, j] = mij[i, j] - mij[i, n + 6]* mij[n + 6, j] / mij[n + 6, n + 6]
                        rij_bar[i] = rij[i] - rij[n + 6] * kij[n + 6, i] / kij[n + 6, n + 6]
            return kij_bar, rij_bar, mij_bar

    def elm_force(self,uij,fij):
        """
        uij,fij: 12x1 sparse vector
        """
        fij = np.zeros(12)
        Kij = sp.csc_matrix(12, 12)
        rij = sp.csc_matrix(12,1)
        self.static_condensation(Kij, rij)
        fij = Kij * uij + self.nodal_force
        return fij

    #to be revised
    def load_distributed(self,qi, qj):
        """
        qi,qj: 6x1 vector
        """
        self.loadI=qi
        self.loadJ=qj
        
    def clear_result(self):
        self.__res_force=None
        
    @property
    def res_force(self):
        return self.__res_force
    
    @res_force.setter
    def res_force(self,force):
        self.__res_force=force


if __name__=='__main__':
    import Node
    import Material
    import Section
    m = Material.material(2.000E11, 0.3, 7849.0474, 1.17e-5)
    s = Section.section(m, 4.800E-3, 1.537E-7, 3.196E-5, 5.640E-6)
    n1=Node.node(1,2,3)
    n2=Node.node(2,3,4)
    b=beam(n1,n2,s)
    
    