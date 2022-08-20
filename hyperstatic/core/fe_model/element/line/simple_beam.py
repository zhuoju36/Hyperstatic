# -*- coding: utf-8 -*-

import numpy as np
import scipy as sp
import scipy.sparse as spr

from hyperstatic.core.fe_model.element.line import Line
from hyperstatic.common.tolerance import Tolerance

class SimpleBeam(Line):
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
        super(SimpleBeam,self).__init__(name,node_i,node_j,12)
        self.__releases=np.array([False,False,False,False,False,False,False,False,False,False,False,False])
        self.__E=E
        self.__mu=mu
        self.__A=A
        self.__I2=I2
        self.__I3=I3
        self.__J=J
        self.__rho=rho
        self.__rotation=0
        self.__offset=np.zeros(2)

    @property
    def releases(self):
        return self.__releases
    
    @releases.setter
    def releases(self,rls):
        self.__releases=np.array(rls)

    @property
    def rotation(self):
        return self.__rotation

    @rotation.setter
    def rotation(self,radian:float):
        self.__rotation=radian
        super().local_csys.rotate_about_x(radian)

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

        K_data=np.array((
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
        ),dtype=object)
        data=K_data[:,0].tolist()
        rc=np.array([*K_data[:,1]])
        row=rc[:,0].tolist()
        col=rc[:,1].tolist()
        Ke = spr.csr_matrix((data,(row,col)),shape=(12, 12))
        return Ke

    def integrate_M(self,consistent=False):
        #Initialize local matrices
        A=self.__A
        J=self.__J
        rho=self.__rho
        l=self.length
        if consistent:#Coordinated mass matrix
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
            _Me = spr.csr_matrix(_Me)
        
        else:#Lumped mass matrix
            _Me=spr.eye(12).tocsr()*rho*A*l/2
            for i in [3,4,5,9,10,11]:
                _Me[i,i]=1e-12 #will be singular if zero
        return _Me

    def get_shape_function(self):
        Na1=lambda xi: 0.5*(1-xi)
        Na2=lambda xi: 0.5*(1+xi)
        Nb1=lambda xi: 1-3*xi**2+2*xi**3
        Nb2=lambda xi: (xi-2*xi**2+xi**3)*self.length
        Nb3=lambda xi: 3*xi**2-2*xi**3
        Nb4=lambda xi: (xi**3-xi**2)*self.length
        Nt1=lambda xi: 0.5*(1-xi)
        Nt2=lambda xi: 0.5*(1+xi)
        return [Na1,Na2,Nb1,Nb2,Nb3,Nb4,-Nb1,Nb2,-Nb3,Nb4,Nt1,Nt2]

    
    def interpolate(self,loc):
        xi=loc
        Na1=0.5*(1-xi)
        Na2=0.5*(1+xi)
        Nb1=1-3*xi**2+2*xi**3
        Nb2=(xi-2*xi**2+xi**3)*self.length
        Nb3=3*xi**2-2*xi**3
        Nb4=(xi**3-xi**2)*self.length
        Nt1=0.5*(1-xi)
        Nt2=0.5*(1+xi)
        return np.array([Na1,Na2,Nb1,Nb2,Nb3,Nb4,-Nb1,Nb2,-Nb3,Nb4,Nt1,Nt2])

    def interpolate1(self,loc):
        xi=loc
        Na1=-0.5
        Na2=0.5
        Nb1=-6*xi+6*xi**2
        Nb2=(1-4*xi+3*xi**2)*self.length
        Nb3=6*xi-6*xi**2
        Nb4=(3*xi**2-2*xi)*self.length
        Nt1=-0.5*xi
        Nt2=0.5*xi
        return np.array([Na1,Na2,Nb1,Nb2,Nb3,Nb4,-Nb1,Nb2,-Nb3,Nb4,Nt1,Nt2])*(1/self.length) #dxi/dx

    def static_condensate(self,Ke):
        k=Ke
        k_ = Ke.copy()
        for n in np.arange(12):
            if self.__releases[n] == True:
                k_ = k - k[:,n]* k[n,:] / k[n, n]
        return k_

    def static_condensate_f(self,re,Ke):
        k=Ke
        r=re
        r_ = re.copy()
        for n in np.arange(12):
            if self.__releases[n] == True:
                r_ = r - r[n] * k[n, :].toarray() / k[n, n]
        return r_.reshape(12)

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