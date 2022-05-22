# -*- coding: utf-8 -*-

import numpy as np
import scipy as sp
import scipy.sparse as spr
import scipy.interpolate as interp
import quadpy

from structengpy.core.fe_model.element.line import Line
from structengpy.common.tolerance import Tolerance

class Beam(Line):
    def __init__(self,name,node_i, node_j, E, mu, A, I2, I3, J, rho):
        """
        params:
            node_i,node_j: ends of beam.
            E: elastic modulus
            mu: Possion ratio        
            A: section area
            I2: inertia about 2-2
            I3: inertia about 3-3
            J: torsianl constant
            rho: mass density
            mass: 'coor' as coordinate matrix or 'conc' for concentrated matrix
        """
        tol=Tolerance.abs_tol()
        super(Beam,self).__init__(name,node_i,node_j,12)
        self.__releases=[[False,False,False,False,False,False],
                         [False,False,False,False,False,False]]
        self.__E=E
        self.__mu=mu
        self.__A=A
        self.__I2=I2
        self.__I3=I3
        self.__J=J
        self.__rho=rho

    @property
    def rotation(self,theta):
        self.local_csys.rotate_about_x(theta)

    @property
    def releases(self):
        return self.__releases

    @property
    def start(self):
        return super().start

    @property
    def end(self):
        return super().end
    
    @releases.setter
    def releases(self,rls):
        if len(rls)!=12:
            raise ValueError('rls must be a 12 boolean array')
        self.__releases=np.array(rls).reshape((2,6))

    @property
    def length(self):
        return super().length

    @property
    def transform_matrix(self):
        return super().transform_matrix

    def integrate_K(self):
        #Initialize local matrices
        #form the stiffness matrix:
        E=self.__E
        mu=self.__mu
        A=self.__A
        I2=self.__I2
        I3=self.__I3
        J=self.__J

        l=self.length
        G=E/2/(1+mu)

        K_data=(
        (E*A / l,(0, 0)),
        (-E*A / l,(0, 6)),
        (-E*A / l,(6, 0)),
        
        (12 * E*I3 / l / l / l,(1, 1)),
        (6 * E*I3 / l / l,(1, 5)),
        (6 * E*I3 / l / l,(5, 1)),
        (-12 * E*I3 / l / l / l,(1, 7)),
        (-12 * E*I3 / l / l / l,(7, 1)),
        (6 * E*I3 / l / l,(1, 11)),
        (6 * E*I3 / l / l,(11, 1)),

        (12 * E*I2 / l / l / l,(2, 2)),
        (-6 * E*I2 / l / l,(2, 4)),
        (-6 * E*I2 / l / l,(4, 2)),
        (-12 * E*I2 / l / l / l,(2, 8)),
        (-12 * E*I2 / l / l / l,(8, 2)),
        (-6 * E*I2 / l / l,(2, 10)),
        (-6 * E*I2 / l / l,(10, 2)),

        (G*J / l,(3, 3)),
        (-G*J / l,(3, 9)),
        (-G*J / l,(9, 3)),

        (4 * E*I2 / l,(4, 4)),
        (6 * E*I2 / l / l,(4, 8)),
        (6 * E*I2 / l / l,(8, 4)),
        (2 * E*I2 / l,(4, 10)),
        (2 * E*I2 / l,(10, 4)),

        (4 * E*I3 / l,(5, 5)),
        (-6 * E*I3 / l / l,(5, 7)),
        (-6 * E*I3 / l / l,(7, 5)),
        (2 * E*I3 / l,(5, 11)),
        (2 * E*I3 / l,(11, 5)),

        (E*A / l,(6, 6)),

        (12 * E*I3 / l / l / l,(7, 7)),
        (-6 * E*I3 / l / l,(7, 11)),
        (-6 * E*I3 / l / l,(11, 7)),

        (12 * E*I2 / l / l / l,(8, 8)),
        (6 * E*I2 / l / l,(8, 10)),
        (6 * E*I2 / l / l,(10, 8)),

        (G*J / l,(9, 9)),

        (4 * E*I2 / l,(10, 10)),

        (4 * E*I3 / l,(11, 11)),
        )
        data=[k[0] for k in K_data]
        row=[k[1][0] for k in K_data]
        col=[k[1][1] for k in K_data]
        _Ke = spr.csr_matrix((data,(row,col)),shape=(12, 12))
        return _Ke

    def integrate_M(self,mass='conc'):
        #Initialize local matrices
        #form the stiffness matrix:
        E=self.__E
        mu=self.__mu
        A=self.__A
        I2=self.__I2
        I3=self.__I3
        J=self.__J
        rho=self.__rho
        l=self.length
        if mass=='coor':#Coordinated mass matrix
            _Me=np.zeros((12,12))
            _Me[0, 0]=140
            _Me[0, 6]=70
    
            _Me[1, 1]=156
            _Me[1, 5]=_Me[5, 1]=22 * l
            _Me[1, 7]=_Me[7, 1]=54
            _Me[1, 11]=_Me[11, 1]=-13 * l
    
            _Me[2, 2]=156
            _Me[2, 4]=_Me[4, 2]=-22 * l
            _Me[2, 8]=_Me[8, 2]=54
            _Me[2, 10]=_Me[10, 2]=13 * l
    
            _Me[3, 3]=140 * J / A
            _Me[3, 9]=_Me[9, 3]=70 * J / A
    
            _Me[4, 4]=4 * l *l
            _Me[4, 8]=_Me[8, 4]=-13 * l
            _Me[4, 10]=_Me[10, 4]=-3 * l*l
    
            _Me[5, 5]=4 * l*l
            _Me[5, 7]=_Me[7, 5]=13 * l
            _Me[5, 11]=_Me[11, 5]=-3 * l*l
    
            _Me[6, 6]=140
    
            _Me[7, 7]=156
            _Me[7, 11]=_Me[11, 7]=-22 * l
    
            _Me[8, 8]=156
            _Me[8, 10]=_Me[10, 8]=22 * l
    
            _Me[9, 9]=140 * J / A
    
            _Me[10, 10]=4 * l*l
    
            _Me[11, 11]=4 * l*l
    
            _Me*= (rho*A*l / 420)
            _Me = spr.csc_matrix(_Me)
        
        elif mass=='conc':#Concentrated mass matrix
            _Me=spr.eye(12).tocsr()*rho*A*l/2
        
        return _Me
        
    def _N(self,s):
        """
        params:
            Hermite's interpolate function
            s:natural position of evalue point.
        returns:
            3x(3x4) shape function matrix.
        """
        N1=1-3*s**2+2*s**3
        N2=  3*s**2-2*s**3
        N3=s-2*s**2+s**3
        N4=   -s**2+s**3
        N=np.hstack([np.eye(3)*N1,np.eye(3)*N2,np.eye(3)*N3,np.eye(3)*N4])
        return N
        
    def static_condensation(self,Ke,Me,re:np.array):
        """
        Perform static condensation.
        """
        releaseI=self.__releases[0]
        releaseJ=self.__releases[1]
        kij=Ke
        mij=Me
        rij=re
        kij_ = Ke.copy()
        mij_ = Me.copy()
        rij_ = re.copy()
        for n in range(0,6):
            if releaseI[n] == True:
                for i in range(12):
                    for j in range(12):
                        kij_[i, j] = kij[i, j] - kij[i, n]* kij[n, j] / kij[n, n]
                        mij_[i, j] = mij[i, j] - mij[i, n]* mij[n, j] / mij[n, n]
                    rij_[i] = rij[i] - rij[n] * kij[n, i] / kij[n, n]
            if releaseJ[n] == True:
                for i in range(12):
                    for j in range(12):
                        kij_[i, j] = kij[i, j] - kij[i, n + 6]* kij[n + 6, j] / kij[n + 6, n + 6]
                        mij_[i, j] = mij[i, j] - mij[i, n + 6]* mij[n + 6, j] / mij[n + 6, n + 6]
                    rij_[i] = rij[i] - rij[n + 6] * kij[n + 6, i] / kij[n + 6, n + 6]
        return kij_,mij_,rij_ #condensated Ke_,Me_,re_
#        ##pythonic code, not finished
#        Ke=self._Ke.copy()
#        Me=self._Me.copy()
#        re=self._re.copy()
#        n_rls=0
#        i=0
#        idx=[]
#        for rls in self._releases[0]+self.releases[1]:
#            if rls:
#                n_rls+=1
#                Ke[[i,-n_rls],:]=Ke[[-n_rls,i],:]
#                Ke[:,[i,-n_rls]]=Ke[:,[-n_rls,i]]
#                Me[[i,-n_rls],:]=Me[[-n_rls,i],:]
#                Me[:,[i,-n_rls]]=Me[:,[-n_rls,i]]
#                re[[i,-n_rls],:]=re[[-n_rls,i],:]
#                idx.append(i)
#            i+=1
#
#        if n_rls==0:
#            self._Ke_,self._Me_,self._re_=Ke,Me,re
#            return 
#        n0=12-n_rls
#        Ke_=Ke[:n0,:n0]-Ke[:n0,n0:].dot(np.mat(Ke[n0:,n0:]).I).dot(Ke[n0:,:n0])
#        Me_=Me[:n0,:n0]-Me[:n0,n0:].dot(np.mat(Ke[n0:,n0:]).I).dot(Me[n0:,:n0])
#        re_=re[:n0]-Ke[:n0,n0:].dot(np.mat(Ke[n0:,n0:]).I).dot(re[:n0])
#        for i in idx:
#            Ke_=np.insert(Ke_,i,0,axis=0)
#            Ke_=np.insert(Ke_,i,0,axis=1)
#            Me_=np.insert(Me_,i,0,axis=0)
#            Me_=np.insert(Me_,i,0,axis=1)
#            re_=np.insert(re_,i,0,axis=0)
#        self._Ke_,self._Me_,self._re_=Ke_,Me_,re_

#code here should be revised
    def resolve_element_force(self,Ke,Me,re,ue):
        """
        compute beam forces with 
        """
        fe=np.zeros((12,1))
        
        releaseI=self.__releases[0]
        releaseJ=self.__releases[1]
        Ke_ = Ke.copy()
        Me_ = Me.copy()
        re_ = re.copy()
        for n in range(0,6):
            if releaseI[n] == True:
                for i in range(12):
                    for j in range(12):
                        Ke_[i, j] = Ke[i, j] - Ke[i, n]* Ke[n, j] / Ke[n, n]
                        Me_[i, j] = Me[i, j] - Me[i, n]* Me[n, j] / Me[n, n]
                    re_[i] = re[i] - re[n] * Ke[n, i] / Ke[n, n]
            if releaseJ[n] == True:
                for i in range(12):
                    for j in range(12):
                        Ke_[i, j] = Ke[i, j] - Ke[i, n + 6]* Ke[n + 6, j] / Ke[n + 6, n + 6]
                        Me_[i, j] = Me[i, j] - Me[i, n + 6]* Me[n + 6, j] / Me[n + 6, n + 6]
                    re_[i] = re[i] - re[n + 6] * Ke[n + 6, i] / Ke[n + 6, n + 6]
        Ke_,Me_,re_=self.static_condensation(Ke,Me,re)
        fe=self._Ke_*ue+self._re_
        return fe
