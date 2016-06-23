# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 22:17:28 2016

@author: HZJ
"""
import numpy as np
import scipy.sparse as sp
import CoordinateSystem

class Beam:
    def __init__(self,i, j, sec):
        self.nodeI=i
        self.nodeJ=j
        self.section=sec
        tol = 1E-6
        #Initialize local CSys
        o = [ self.nodeI.x, self.nodeI.y, self.nodeI.z ]
        pt1 = [ self.nodeJ.x, self.nodeJ.y, self.nodeJ.z ]
        pt2 = [ self.nodeI.x, self.nodeI.y, self.nodeI.z ]
        if abs(self.nodeI.x - self.nodeJ.x) < tol and abs(self.nodeI.y - self.nodeJ.y) < tol:
            pt2[0] += 1
        else:
            pt2[2] += 1
        self.localCsys = CoordinateSystem.CoordinateSystem(o, pt1, pt2)

        #Initialize local stiffness matrix
        l = self.Length()
        E = self.section.material.E
        A = self.section.A
        J = self.section.J
        G = self.section.material.G()
        I2 = self.section.I22
        I3 = self.section.I33
        rho = self.section.material.gamma

        Kij = np.zeros((12, 12))
        Mij = np.zeros((12, 12))

        #form the stiffness matrix:
        Kij[0, 0]=E*A / l
        Kij[0, 6]=Kij[6, 0]=-E*A / l

        Kij[1, 1]=12 * E*I3 / l / l / l
        Kij[1, 5]=Kij[5, 1]=6 * E*I3 / l / l
        Kij[1, 7]=Kij[7, 1]=-12 * E*I3 / l / l / l
        Kij[1, 11]=Kij[11, 1]=6 * E*I3 / l / l

        Kij[2, 2]=12 * E*I2 / l / l / l
        Kij[2, 4]=Kij[4, 2]=-6 * E*I2 / l / l
        Kij[2, 8]=Kij[8, 2]=-12 * E*I2 / l / l / l
        Kij[2, 10]=Kij[10, 2]=-6 * E*I2 / l / l

        Kij[3, 3]=G*J / l
        Kij[3, 9]=Kij[9, 3]=-G*J / l

        Kij[4, 4]=4 * E*I2 / l
        Kij[4, 8]=Kij[8, 4]=6 * E*I2 / l / l
        Kij[4, 10]=Kij[10, 4]=2 * E*I2 / l

        Kij[5, 5]=4 * E*I3 / l
        Kij[5, 7]=Kij[7, 5]=-6 * E*I3 / l / l
        Kij[5, 11]=Kij[11, 5]=2 * E*I3 / l

        Kij[6, 6]=E*A / l

        Kij[7, 7]=12 * E*I3 / l / l / l
        Kij[7, 11]=Kij[11, 7]=-6 * E*I3 / l / l

        Kij[8, 8]=12 * E*I2 / l / l / l
        Kij[8, 10]=Kij[10, 8]=6 * E*I2 / l / l

        Kij[9, 9]=G*J / l

        Kij[10, 10]=4 * E*I2 / l

        Kij[11, 11]=4 * E*I3 / l

        #form mass matrix    
        ##Coordinated mass matrix
        #Mij[0, 0]=140
        #Mij[0, 6]=70

        #Mij[1, 1]=156
        #Mij[1, 5]=Mij[5, 1]=22 * l
        #Mij[1, 7]=Mij[7, 1]=54
        #Mij[1, 11]=Mij[11, 1]=-13 * l

        #Mij[2, 2]=156
        #Mij[2, 4]=Mij[4, 2]=-22 * l
        #Mij[2, 8]=Mij[8, 2]=54
        #Mij[2, 10]=Mij[10, 2]=13 * l

        #Mij[3, 3]=140 * J / A
        #Mij[3, 9]=Mij[9, 3]=70 * J / A

        #Mij[4, 4]=4 * l *l
        #Mij[4, 8]=Mij[8, 4]=-13 * l
        #Mij[4, 10]=Mij[10, 4]=-3 * l*l

        #Mij[5, 5]=4 * l*l
        #Mij[5, 7]=Mij[7, 5]=13 * l
        #Mij[5, 11]=Mij[11, 5]=-3 * l*l

        #Mij[6, 6]=140

        #Mij[7, 7]=156
        #Mij[7, 11]=Mij[11, 7]=-22 * l

        #Mij[8, 8]=156
        #Mij[8, 10]=Mij[10, 8]=22 * l

        #Mij[9, 9]=140 * J / A

        #Mij[10, 10]=4 * l*l

        #Mij[11, 11]=4 * l*l

        #Mij*= (rho*A*l / 420)

        #Concentrated mass matrix
        for i in range(12):
            Mij[i, i]=1
        Mij*=rho*A*l/2

    def InitializeCsys(self):
        nodeI=self.nodeI
        nodeJ=self.nodeJ
        o = np.array([nodeI.x, nodeI.y, nodeI.z])
        pt1 = np.array([nodeJ.x, nodeJ.y, nodeJ.z])
        pt2 = np.array([0,0,0])
        if self.nodeI.x != self.nodeJ.x and self.nodeI.y != self.nodeJ.y:
            pt2[2] = 1
        else:
            pt2[0] = 1
        self.localCsys.SetBy3Pts(o, pt1, pt2)

    def Length(self):
        nodeI=self.nodeI
        nodeJ=self.nodeJ
        return np.sqrt((nodeI.x - nodeJ.x)*(nodeI.x - nodeJ.x) + (nodeI.y - nodeJ.y)*(nodeI.y - nodeJ.y) + (nodeI.z - nodeJ.z)*(nodeI.z - nodeJ.z))

    #vec NodalForceI()
    #{
    #    l = self.Length()
    #    #recheck!!!!!!!!!!!!
    #    vec v(6, fill::zeros)
    #    v(0) = (loadI[0] + loadJ[0]) * l / 2#P
    #    v(1) = (loadI[1] * 7 / 20 + loadJ[1] * 3 / 20) * l#V2
    #    v(2) = (loadI[2] * 7 / 20 + loadJ[2] * 3 / 20) * l#V3
    #    v(3) = loadI[3] - loadJ[3]#T
    #    v(4) = (loadI[2] / 20 + loadJ[2] / 30) * l * l + loadI[4]#M22
    #    v(5) = (loadI[1] / 20 + loadJ[1] / 30) * l * l + loadI[5]#M33
    #
    #    return v
    #    #l = self.Length()
    #    #mat bij(6, 6,fill::zeros)
    #    #for (int i = 0 i < 6 i++)
    #    #    bij(i, i) = -1
    #    #bij(1, 5) = bij(2, 4) = 1/l
    #    #bij(5, 1) = bij(4, 2) = l
    #    ###############TEST##############
    #    #mat k = NodalForceJ()
    #    ##cout.setf(ios::scientific)
    #    #for (int i = 0 i < k.n_rows i++)
    #    #{
    #    #    for (int j = 0 j < k.n_cols j++)
    #    #    {
    #    #        cout.width(8)
    #    #        cout.precision(4)
    #    #        cout.setf(ios::right)
    #    #        cout << k[i, j] << "  "
    #    #    }
    #    #    cout << endl
    #    #}
    #    #cout << endl
    #    ###############TEST##############
    #    ###############TEST##############
    #    #k = bij
    #    ##cout.setf(ios::scientific)
    #    #for (int i = 0 i < k.n_rows i++)
    #    #{
    #    #    for (int j = 0 j < k.n_cols j++)
    #    #    {
    #    #        cout.width(8)
    #    #        cout.precision(4)
    #    #        cout.setf(ios::right)
    #    #        cout << k[i, j] << "  "
    #    #    }
    #    #    cout << endl
    #    #}
    #    #cout << endl
    #    ###############TEST##############
    #    ###############TEST##############
    #    # k = bij*NodalForceJ()
    #    ##cout.setf(ios::scientific)
    #    #for (int i = 0 i < k.n_rows i++)
    #    #{
    #    #    for (int j = 0 j < k.n_cols j++)
    #    #    {
    #    #        cout.width(8)
    #    #        cout.precision(4)
    #    #        cout.setf(ios::right)
    #    #        cout << k[i, j] << "  "
    #    #    }
    #    #    cout << endl
    #    #}
    #    #cout << endl
    #    ###############TEST##############
    #    #return bij*NodalForceJ()
    #}

    def NodalForce(self):
        l = self.Length()
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

    def LocalStiffnessMatrix(self):
        return self.Kij

    def LocalMassMatrix(self):
        return self.Mij

    def StaticCondensation(self, kij_bar, rij_bar, mij_bar=0):
        """
        kij_bar: 12x12 sparse matrix
        rij_bar: 12x1  sparse vector
        mij_bar: 12x12 sparse matrix, if mij_bar==0, mass matrix will not be considered
        return???refer????
        """
        if mij_bar==0:
            kij=self.Kij
            rij=self.NodalForce()
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
        else:
            kij=self.Kij
            mij=self.Mij
            rij=self.NodalForce()
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
        return True

    def CalculateElmForce(self,uij,fij):
        """
        uij,fij: 12x1 sparse vector
        return???refer????
        """
        fij = np.zeros(12)
        Kij = sp.csc_matrix(12, 12)
        rij = sp.csc_matrix(12,1)
        self.StaticCondensation(Kij, rij)
        fij = Kij * uij + self.NodalForce()
        return fij

    def TransformMatrix(self):
        T=np.zeros((12,12))
        V=self.localCsys.TransformMatrix()
        T[:3,:3] =T[3:6,3:6]=T[6:9,6:9]=T[9:,9:]= V
        return T

    def SetLoadDistributed(self,qi, qj):
        """
        qi,qj: 6x1 vector
        """
        self.loadI=qi
        self.loadJ=qj

import Node
import Material
import Section

m = Material.Material(2.000E11, 0.3, 7849.0474, 1.17e-5)
s = Section.Section(m, 4.800E-3, 1.537E-7, 3.196E-5, 5.640E-6)
n1=Node.Node(1,2,3)
n2=Node.Node(2,3,4)
b=Beam(n1,n2,s)
    
    