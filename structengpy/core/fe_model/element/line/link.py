# -*- coding: utf-8 -*-

import numpy as np
import scipy as sp
import scipy.sparse as spr
import scipy.interpolate as interp
import quadpy

from structengpy.core.fe_model.element.line import Line

class Link(Line):
    def __init__(self,node_i, node_j, E, A, rho, name=None, mass='conc', tol=1e-6):
        """
        params:
            node_i,node_j: ends of link.
            E: elastic modulus
            A: section area
            rho: mass density
            mass: 'coor' as coordinate matrix or 'conc' for concentrated matrix
            tol: tolerance
        """
        super(Link,self).__init__(node_i,node_j,A,rho,6,name,mass)
        l=self._length
        K_data=(
            (E*A/l,(0,0)),
            (-E*A/l,(0,1)),
            (-E*A/l,(1,0)),
            (E*A/l,(1,1)),
        )
        m_data=(
            (1,(0,0)),
            (1,(1,1))*rho*A*l/2
        )
        data=[k[0] for k in K_data]
        row=[k[1][0] for k in K_data]
        col=[k[1][1] for k in K_data]
        self._Ke = spr.csr_matrix((data,(row,col)),shape=(12, 12))
        self._Me=spr.eye(2)*rho*A*l/2
        #force vector
        self._re =np.zeros((2,1))

    def _N(self,s):
        """
        params:
            Lagrange's interpolate function
            s:natural position of evalue point.
        returns:
            3x(3x2) shape function matrix.
        """
        N1=(1-s)/2
        N2=(1+s)/2
        N=np.array([[N1,0,0,N2,0,0],
                    [0,N1,0,0,N2,0],
                    [0,0,N1,0,0,N2]])
        return N
