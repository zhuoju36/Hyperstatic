import numpy as np
import scipy as sp
import scipy.sparse as spr
import quadpy

from structengpy.core.fe_model.element.quad import Quad

class Membrane4(Quad):
    def __init__(self,node_i, node_j, node_k, node_l, t, E, mu, rho, name=None):
        """
        node_i,node_j,node_k: corners of triangle.
        t: thickness
        E: elastic modulus
        mu: Poisson ratio
        rho: mass density
        """
        super(Membrane4,self).__init__(node_i,node_j,node_k,node_l,t,E,mu,rho,8)
        self._t=t
        self._E=E
        self._mu=mu
        self._rho=rho

        elm_node_count=4
        node_dof=2
        
        scheme=quadpy.c2.get_good_scheme(7)
        Ke = scheme.integrate(
            lambda s: self._BtDB(s[0],s[1])*np.linalg.det(self._J(s[0],s[1])),
            quadpy.c2.rectangle_points([-1.0, 1.0], [-1.0, 1.0]),
            )
        Ke=sp.sparse.csr_matrix(Ke)
        row=[]
        col=[]
        for i in range(elm_node_count):
            row+=[a for a in range(i*node_dof,i*node_dof+node_dof)]
            col+=[a for a in range(i*6,i*6+node_dof)]
        data=[1]*(elm_node_count*node_dof)
        G=sp.sparse.csr_matrix((data,(row,col)),shape=(elm_node_count*node_dof,elm_node_count*6))
        self._Ke=G.transpose()*Ke*G
        #Concentrated mass matrix, may be wrong
        self._Me=G.transpose()*np.eye(node_dof*elm_node_count)*G*rho*self._area*t/4
        
        self._re =np.zeros((elm_node_count*6,1))
        
    @property
    def area(self):
        return self._area
        
    def _N(self,s,r):
        """
        Lagrange's interpolate function
        params:
            s,r:natural position of evalue point.2-array.
        returns:
            2x(2x4) shape function matrix.
        """
        la1=(1-s)/2
        la2=(1+s)/2
        lb1=(1-r)/2
        lb2=(1+r)/2
        N1=la1*lb1
        N2=la1*lb2
        N3=la2*lb1
        N4=la2*lb2

        N=np.hstack(N1*np.eye(2),N2*np.eye(2),N3*np.eye(2),N4*np.eye(2))
        return N

    def _J(self,s,r):
        """
        Jacobi matrix of Lagrange's interpolate function
        Lagrange's interpolate function
        params:
            s,r:natural position of evalue point.2-array.
        returns:
            2x2 Jacobi matrix.
        """
        J=np.zeros((2,2,s.shape[0]))
        #coordinates on local catesian system
        x2D=self._x2D
        x1,y1=x2D[0,0],x2D[0,1]
        x2,y2=x2D[1,0],x2D[1,1]
        x3,y3=x2D[2,0],x2D[2,1]
        x4,y4=x2D[3,0],x2D[3,1]
        J[0,0]=-x1*(-s/2 + 1/2)/2 + x2*(-s/2 + 1/2)/2 - x3*(s/2 + 1/2)/2 + x4*(s/2 + 1/2)/2
        J[1,0]=-x1*(-r/2 + 1/2)/2 - x2*(r/2 + 1/2)/2 + x3*(-r/2 + 1/2)/2 + x4*(r/2 + 1/2)/2
        J[0,1]=-y1*(-s/2 + 1/2)/2 + y2*(-s/2 + 1/2)/2 - y3*(s/2 + 1/2)/2 + y4*(s/2 + 1/2)/2
        J[1,1]=-y1*(-r/2 + 1/2)/2 - y2*(r/2 + 1/2)/2 + y3*(-r/2 + 1/2)/2 + y4*(r/2 + 1/2)/2
        return J.transpose(2,0,1)
    
    def _B(self,s,r):
        """
        strain matrix, which is derivative of intepolate function
        params:
            s,r:natural position of evalue point.2-array.
        returns:
            3x(2x4) Jacobi matrix.
        """
        
        B=np.zeros((3,8,s.shape[0])) #vectorized
        B[0,0]=B[2,1]=s/4 - 1/4
        B[1,1]=B[2,0]=r/4 - 1/4
        B[0,2]=B[2,3]=-s/4 + 1/4
        B[1,3]=B[2,2]=-r/4 - 1/4
        B[0,4]=B[2,5]=-s/4 - 1/4
        B[1,5]=B[2,4]=-r/4 + 1/4
        B[0,6]=B[2,7]=s/4 + 1/4
        B[1,7]=B[2,6]=r/4 + 1/4
        return B
    
    def _BtDB(self,s,r):
        """
        dot product of B^T, D, B
        params:
            s,r:natural position of evalue point.2-array.
        returns:
            3x3 matrix.
        """
        print(self._B(s,r).transpose(2,0,1).shape)
        print(
            np.matmul(
                np.dot(self._B(s,r).T,self._D),
                self._B(s,r).transpose(2,0,1)).shape
            )
        print(self._D.shape)
       
        
        return np.matmul(np.dot(self._B(s,r).T,self._D),self._B(s,r).transpose(2,0,1)).transpose(1,2,0)
    
    def _S(self,s,r):
        """
        stress matrix
        """
        return np.dot(self._D,self._B(s,r))