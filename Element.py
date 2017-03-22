# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 22:17:28 2016

@author: HZJ
"""
import uuid
import numpy as np
import scipy as sp
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
        self.__releaseI=[False]*6
        self.__releaseJ=[False]*6
        self.__section=sec
        self.__rotation=0
        
        self.__load_d=[] #distributed
        self.__load_c=[] #concentrated
        self.__load_s=[] #strain
        self.__load_t=[] #temperature
        
        tol = 1E-6
        #results
        self.__res_force=None
        self.__res_disp=None
        self.__measure=[] #result measure locations
        self.__ms_forces=[]
        self.__ms_disps=[]
        
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
        self.__Mij_=np.zeros((12,12))
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
        #Coordinated mass matrix
        self.__Mij_[0, 0]=140
        self.__Mij_[0, 6]=70

        self.__Mij_[1, 1]=156
        self.__Mij_[1, 5]=self.__Mij_[5, 1]=22 * l
        self.__Mij_[1, 7]=self.__Mij_[7, 1]=54
        self.__Mij_[1, 11]=self.__Mij_[11, 1]=-13 * l

        self.__Mij_[2, 2]=156
        self.__Mij_[2, 4]=self.__Mij_[4, 2]=-22 * l
        self.__Mij_[2, 8]=self.__Mij_[8, 2]=54
        self.__Mij_[2, 10]=self.__Mij_[10, 2]=13 * l

        self.__Mij_[3, 3]=140 * J / A
        self.__Mij_[3, 9]=self.__Mij_[9, 3]=70 * J / A

        self.__Mij_[4, 4]=4 * l *l
        self.__Mij_[4, 8]=self.__Mij_[8, 4]=-13 * l
        self.__Mij_[4, 10]=self.__Mij_[10, 4]=-3 * l*l

        self.__Mij_[5, 5]=4 * l*l
        self.__Mij_[5, 7]=self.__Mij_[7, 5]=13 * l
        self.__Mij_[5, 11]=self.__Mij_[11, 5]=-3 * l*l

        self.__Mij_[6, 6]=140

        self.__Mij_[7, 7]=156
        self.__Mij_[7, 11]=self.__Mij_[11, 7]=-22 * l

        self.__Mij_[8, 8]=156
        self.__Mij_[8, 10]=self.__Mij_[10, 8]=22 * l

        self.__Mij_[9, 9]=140 * J / A

        self.__Mij_[10, 10]=4 * l*l

        self.__Mij_[11, 11]=4 * l*l

        self.__Mij_*= (rho*A*l / 420)

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
    
    @property
    def section(self):
        return self.__section
        
    @property
    def releaseI(self):
        return self.__releaseI
        
    @property
    def releaseJ(self):
        return self.__releaseJ

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

    def static_condensation(self, coor_mass=False):
        """
        kij_bar: 12x12 matrix
        rij_bar: 12x1 vector
        mij_bar: 12x12 matrix
        """
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
        return kij_bar, mij_bar, rij_bar

    def elm_force(self,uij,fij):
        """
        uij,fij: 12x1 sparse vector
        """
#        fij = np.zeros(12)
#        Kij = sp.csc_matrix(12, 12)
#        rij = sp.csc_matrix(12,1)
        Kij, Mij, rij = self.static_condensation()
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
        
    #result force
    @property
    def res_force(self):
        return self.__res_force
    
    @res_force.setter
    def res_force(self,force):
        self.__res_force=force
        
#class quad(element):
#    def __init__(self,sec,node_i, node_j, node_k, node_l, name=None):
#        self.__node_i=node_i
#        self.__node_j=node_j
#        self.__node_k=node_k
#        self.__node_l=node_l
#
#        self.load_i=[0]*6
#        self.load_j=[0]*6
#        self.load_k=[0]*6
#        self.load_l=[0]*6
#        
#        self.__section=sec
#        self.__rotation=0
#        
#        self.__load_d=[]
#        self.__load_c=[]
#        self.__load_s=[]
#        self.__load_t=[]
#        
#        center=np.mean([node_i,node_j,node_k,node_l])
#        pt1=np.mean([node_i,node_j])
#        pt2=np.mean([node_j,node_k])
#        self.local_csys = CoordinateSystem.cartisian(center,pt1,pt2)
#        
#        self.__alpha=[]#the angle between edge and local-x, to be added
#        self.__alpha.append(angle(node_i,node_j,self.local_csys.x))
#        self.__alpha.append(angle(node_j,node_k,self.local_csys.x))
#        self.__alpha.append(angle(node_k,node_l,self.local_csys.x))
#        self.__alpha.append(angle(node_l,node_i,self.local_csys.x))
#        
#        #interpolate function
#        self.__N=[]
#        self.__N.append((1-r)*(1-s)/4)
#        self.__N.append((1+r)*(1-s)/4)
#        self.__N.append((1+r)*(1+s)/4)
#        self.__N.append((1-r)*(1+s)/4)
#        self.__N.append((1-r**2)*(1-s)/2)
#        self.__N.append((1+r)*(1-s**2)/2)
#        self.__N.append((1-r**2)*(1+s)/2)
#        self.__N.append((1-r)*(1-s**2)/2)
#        
#        self.__K=np.zeros((24,24))
#        
#    def angle(node_i,node_j,x):
#        v=np.array([node_j.X-node_i.X,node_j.Y-node_i.Y,node_j.Z-node_i.Z])
#        L1=np.sqrt(v.dot(v))
#        L2=np.sqrt(x.dot(x))
#        return np.arccos(v.dot(x)/L1/L2)
#        
#    def plate_to_integrate(self,r,s):
#        """
#        bT-D-b
#        """
#        alpha=self.__alpha
#                    
#        #derivation
#        dNdr=[-(1-s)/4]
#        dNdr.append((1-s)/4)
#        dNdr.append((1+s)/4)
#        dNdr.append(-(1+s)/4)
#        dNdr.append(-(1-s)*r)
#        dNdr.append((1-s*s)/2)
#        dNdr.append(-(1+s)*r)
#        dNdr.append(-(1-s*s)/2)
#        
#        dNds=[-(1-r)/4]
#        dNds.append(-(1+r)/4)
#        dNds.append((1+r)/4)
#        dNds.append((1-r)/4)
#        dNds.append(-(1-r*r)/2)
#        dNds.append(-(1+r)*s)
#        dNds.append((1+r*r)/2)
#        dNds.append(-(1-r)*s)
#        
#        dNdr=np.array(dNdr)
#        dNds=np.array(dNds)
#        
#        #Jacobi matrix
#        dxdr=sum(dNdr*x)
#        dydr=sum(dNdr*y)
#        dxds=sum(dNds*x)
#        dyds=sum(dNds*y)
#        J=[[dxdr,dydr],
#           [dxds,dyds]]
#        
#        #dx/dr=1/(dr/dx)?
#        dNdx=[]
#        dNdy=[]
#        for i in range(8): 
#            dNdx.append(dNdr[i]/dxdr+dNds[i]/dxds)
#            dNdy.append(dNdr[i]/dydr+dNds[i]/dyds)
#            
#        N=self.__N
#        Mx=[]
#        Mx.append(N[4]*np.sin(alpha[0]))
#        Mx.append(N[5]*np.sin(alpha[1]))
#        Mx.append(N[6]*np.sin(alpha[2]))
#        Mx.append(N[7]*np.sin(alpha[3]))
#        My=[]
#        My.append(-N[4]*np.cos(alpha[0]))
#        My.append(-N[5]*np.cos(alpha[1]))
#        My.append(-N[6]*np.cos(alpha[2]))
#        My.append(-N[7]*np.cos(alpha[3]))
#        
#        #derivation
#        dMxdr=[]
#        dMxdr.append(-(1-s)*r)*np.sin(alpha[0])
#        dMxdr.append((1-s*s)/2)*np.sin(alpha[1])
#        dMxdr.append(-(1+s)*r)*np.sin(alpha[2])
#        dMxdr.append(-(1-s*s)/2)*np.sin(alpha[3])
#        dMydr=[]
#        dMydr.append((1-s)*r)*np.cos(alpha[0])
#        dMydr.append(-(1-s*s)/2)*np.cos(alpha[1])
#        dMydr.append((1+s)*r)*np.cos(alpha[2])
#        dMydr.append((1-s*s)/2)*np.cos(alpha[3])
#        
#        dMxds=[]
#        dMxds.append(-(1-r)/4*np.sin(alpha[0]))
#        dMxds.append(-(1+r)/4*np.sin(alpha[1]))
#        dMxds.append((1+r)/4*np.sin(alpha[2]))
#        dMxds.append((1-r)/4*np.sin(alpha[3]))
#        dMyds=[]
#        dMyds.append((1-r*r)/2*np.cos(alpha[0]))
#        dMyds.append((1+r)*s*np.cos(alpha[1]))
#        dMyds.append(-(1+r*r)/2*np.cos(alpha[2]))
#        dMyds.append((1-r)*s*np.cos(alpha[3]))
#        
#        dMxdr=np.array(dMxdr)
#        dMydr=np.array(dMxdr)
#        dMxds=np.array(dMyds)
#        dMyds=np.array(dMyds)
#                
#        #dx/dr=1/(dr/dx)?
#        dMxdx=[]
#        dMxdy=[]
#        dMydx=[]
#        dMydy=[]
#        for i in range(4): 
#            dMxdx.append(dMxdr[i]/dxdr+dMxds[i]/dxds)
#            dMxdy.append(dMxdr[i]/dxdr+dMxds[i]/dyds)
#            dMydx.append(dMydr[i]/dxdr+dMyds[i]/dxds)
#            dMydy.append(dMydr[i]/dydr+dMyds[i]/dyds)
#        
#        D=[np.cos(alpha[0])*.np.sin(alpha[3])-np.sin(alpha[0])*.np.cos(alpha[3]),
#           np.cos(alpha[1])*.np.sin(alpha[0])-np.sin(alpha[1])*.np.cos(alpha[0]),
#           np.cos(alpha[2])*.np.sin(alpha[1])-np.sin(alpha[2])*.np.cos(alpha[1]),
#           np.cos(alpha[3])*.np.sin(alpha[2])-np.sin(alpha[3])*.np.cos(alpha[2])]
#        
#        b=[[       0,       0,       0,       0,dNdx[0],dNdx[1],dNdx[2],dNdx[3],0,0,0,0,        dMydx[0],        dMydx[1],        dMydx[2],        dMydx[3]],
#           [ dNdy[0], dNdy[1], dNdy[2], dNdy[3],      0,      0,      0,      0,0,0,0,0,        dMxdy[0],        dMxdy[1],        dMxdy[2],        dMxdy[3]],
#           [-dNdx[0],-dNdx[1],-dNdx[2],-dNdx[3],dNdy[0],dNdy[1],dNdy[2],dNdy[3],0,0,0,0,dMydy[0]-dMxdx[0],dMydy[1]-dMxdx[1],dMydy[2]-dMxdx[2],dMydy[3]-dMxdx[3]],
#           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
#           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
#           
#        for i in range(4):
#            gamma_e[i]=1/L()
#           
##        detJ=J[1,1]*J[2,2]-J[1,2]*J[2,1]
##        
##        a=[[z,0,0,0,0],
##           [0,z,0,0,0],
##           [0,0,z,0,0],
##           [0,0,0,1,0],
##           [0,0,0,0,1]]
##           
##        gamma=np.zeros((4,4))
##        for i in range(4):
##            for j in range(4):
##                gamma[i,j]=1/L*()
##      
##        
##        M1dx,M2dx,M3dx,M4dx=N1dy,N2dy,N3dy,N4dy
##        M1dy,M2dy,M3dy,M4dy=N1dy,N2dy,N3dy,N4dy
##        
##        if sec.Material.type=='Iso':
##            D11=D22=E*h**3/(12*(1-mu**2))
##            D12=D21=mu*E*h**3/(12*(1-mu**2))
##            D44=D55=5*E*h**3/(12*(1+mu))
##            D=[[D11,D12,0,  0,  0],
##               [D21,D22,0,  0,  0],
##               [  0,  0,0,  0,  0],
##               [  0,  0,0,D44,  0],
##               [  0,  0,0,  0,D55]]
##
##           
##        k=sp.integrate.dblquad(
##                       func,-1,1
##                       )
##           
##        
##        #Calculate edge shear
##        alpha[0,1]=-alpha[1,0]
##        alpha[1,2]=-alpha[2,1]
##        alpha[2,3]=-alpha[3,2]
##        alpha[3,0]=-alpha[0,3]
##        
##        gamma_e=[]
##        for i in range(4):
##            gamma.append()
#        
#    def membrane_to_integrate(self,r,s):
#        """
#        bT-D-b
#        """
#        alpha=[]
#        for i in range(4):
#            alpha.append("the angle between edge i and x")
#        
#        #derivation
#        dNdr=[-(1-s)/4]
#        dNdr.append((1-s)/4)
#        dNdr.append((1+s)/4)
#        dNdr.append(-(1+s)/4)
#        dNdr.append(-(1-s)*r)
#        dNdr.append((1-s*s)/2)
#        dNdr.append(-(1+s)*r)
#        dNdr.append(-(1-s*s)/2)
#        
#        dNds=[-(1-r)/4]
#        dNds.append(-(1+r)/4)
#        dNds.append((1+r)/4)
#        dNds.append((1-r)/4)
#        dNds.append(-(1-r*r)/2)
#        dNds.append(-(1+r)*s)
#        dNds.append((1+r*r)/2)
#        dNds.append(-(1-r)*s)
#        
#        dNdr=np.array(dNdr)
#        dNds=np.array(dNds)
#        
#        #Jacobi matrix
#        dxdr=sum(dNdr*x)
#        dydr=sum(dNdr*y)
#        dxds=sum(dNds*x)
#        dyds=sum(dNds*y)
#        J=[[dxdr,dydr],
#           [dxds,dyds]]
#        
#        #dx/dr=1/(dr/dx)?
#        dNdx=[]
#        dNdy=[]
#        for i in range(8): 
#            dNdx.append(dNdr[i]/dxdr+dNds[i]/dxds)
#            dNdy.append(dNdr[i]/dydr+dNds[i]/dyds)
#            
#        N=self.__N
#        Mx=[]
#        Mx.append(N[4]*np.sin(alpha[0]))
#        Mx.append(N[5]*np.sin(alpha[1]))
#        Mx.append(N[6]*np.sin(alpha[2]))
#        Mx.append(N[7]*np.sin(alpha[3]))
#        My=[]
#        My.append(-N[4]*np.cos(alpha[0]))
#        My.append(-N[5]*np.cos(alpha[1]))
#        My.append(-N[6]*np.cos(alpha[2]))
#        My.append(-N[7]*np.cos(alpha[3]))
#        
#        #derivation
#        dMxdr=[]
#        dMxdr.append(-(1-s)*r)*np.sin(alpha[0])
#        dMxdr.append((1-s*s)/2)*np.sin(alpha[1])
#        dMxdr.append(-(1+s)*r)*np.sin(alpha[2])
#        dMxdr.append(-(1-s*s)/2)*np.sin(alpha[3])
#        dMydr=[]
#        dMydr.append((1-s)*r)*np.cos(alpha[0])
#        dMydr.append(-(1-s*s)/2)*np.cos(alpha[1])
#        dMydr.append((1+s)*r)*np.cos(alpha[2])
#        dMydr.append((1-s*s)/2)*np.cos(alpha[3])
#        
#        dMxds=[]
#        dMxds.append(-(1-r)/4*np.sin(alpha[0]))
#        dMxds.append(-(1+r)/4*np.sin(alpha[1]))
#        dMxds.append((1+r)/4*np.sin(alpha[2]))
#        dMxds.append((1-r)/4*np.sin(alpha[3]))
#        dMyds=[]
#        dMyds.append((1-r*r)/2*np.cos(alpha[0]))
#        dMyds.append((1+r)*s*np.cos(alpha[1]))
#        dMyds.append(-(1+r*r)/2*np.cos(alpha[2]))
#        dMyds.append((1-r)*s*np.cos(alpha[3]))
#        
#        dMxdr=np.array(dMxdr)
#        dMydr=np.array(dMxdr)
#        dMxds=np.array(dMyds)
#        dMyds=np.array(dMyds)
#                
#        #dx/dr=1/(dr/dx)?
#        dMxdx=[]
#        dMxdy=[]
#        dMydx=[]
#        dMydy=[]
#        for i in range(4): 
#            dMxdx.append(dMxdr[i]/dxdr+dMxds[i]/dxds)
#            dMxdy.append(dMxdr[i]/dxdr+dMxds[i]/dyds)
#            dMydx.append(dMydr[i]/dxdr+dMyds[i]/dxds)
#            dMydy.append(dMydr[i]/dydr+dMyds[i]/dyds)
#        
#        B=[[ dNdx[0],dNdx[1],dNdx[2],dNdx[3],      0,      0,      0,      0,         dMxdx[0],         dMxdx[1],         dMxdx[2],         dMxdx[3]],
#           [       0,      0,      0,      0,dNdy[0],dNdy[1],dNdy[2],dNdy[3],         dMydy[0],         dMydy[1],         dMydy[2],         dMydy[3]],
#           [ dNdx[0],dNdx[1],dNdx[2],dNdx[3],dNdy[0],dNdy[1],dNdy[2],dNdy[3],dMxdy[0]+dMydx[0],dMxdy[1]+dMydx[1],dMxdy[2]+dMydx[2],dMxdy[3]+dMydx[3]]]
#
#        return B.T.dot(D).dot(B)
#
#    
#    
#
#    def cartisian_to_area(x1,y1):    
#        a[0]=x[0]*y[2]-x[2]*y[0]
#        b[0]=y[1]-y[2]
#        c[0]=-x[1]+x[2]
#        
#        a[1]=x[1]*y[0]-x[0]*y[1]
#        b[1]=y[2]-y[0]
#        c[1]=-x[2]+x[0]
#        
#        a[2]=x[2]*y[1]-x[1]*y[2]
#        b[2]=y[0]-y[1]
#        c[2]=-x[0]+x[1]
#        
#        for i in range(3):
#            L[i]=(a[i]+b[i]*x1+c[i]*y1)
#            
#    def area_to_cartisian(L):
#        x2=0
#        y2=0
#        for i in range(3):
#            x2+=x[i]*L[i]
#            y2+=y[i]*L[i]
#            
#    L1,L2,L3=L[1],L[2],L[0]
#    a1,a2,a3=a[1],a[2],a[0]
#    b1,b2,b3=b[1],b[2],b[0]
#    c1,c2,c3=c[1],c[2],c[0]
#    
#    N[1]=[
#    L1+L1**2*L2+L1**2*L3-L1*L2**2-L1*L3**2,
#    b2*(L3*L1**2+L1*L2*L3/2)-b3*(L1**2*L2+L1*L2*L3/2),
#    c2*(L3*L1**2+L1*L2*L3/2)-c3*(L1**2*L2+L1*L2*L3/2)
#    ]
#    
#    L1,L2,L3=L[2],L[0],L[1]
#    a1,a2,a3=a[2],a[0],a[1]
#    b1,b2,b3=b[2],b[0],b[1]
#    c1,c2,c3=c[2],c[0],c[1]
#    
#    N[2]=[
#    L1+L1**2*L2+L1**2*L3-L1*L2**2-L1*L3**2,
#    b2*(L3*L1**2+L1*L2*L3/2)-b3*(L1**2*L2+L1*L2*L3/2),
#    c2*(L3*L1**2+L1*L2*L3/2)-c3*(L1**2*L2+L1*L2*L3/2)
#    ]
#    
#    L1,L2,L3=L[0],L[1],L[2]
#    a1,a2,a3=a[0],a[1],a[2]
#    b1,b2,b3=b[0],b[1],b[2]
#    c1,c2,c3=c[0],c[1],c[2]
#    
#    N[0]=[
#    L1+L1**2*L2+L1**2*L3-L1*L2**2-L1*L3**2,
#    b2*(L3*L1**2+L1*L2*L3/2)-b3*(L1**2*L2+L1*L2*L3/2),
#    c2*(L3*L1**2+L1*L2*L3/2)-c3*(L1**2*L2+L1*L2*L3/2)
#    ]
    
        
if __name__=='__main__':
    import Node
    import Material
    import Section
    m = Material.material(2.000E11, 0.3, 7849.0474, 1.17e-5)
    s = Section.section(m, 4.800E-3, 1.537E-7, 3.196E-5, 5.640E-6)
    n1=Node.node(1,2,3)
    n2=Node.node(2,3,4)
    b=beam(n1,n2,s)