import numpy as np
import scipy as sp

from structengpy.core.fe_model.element.tri import Tri
class Membrane3(Tri):
    def __init__(self,node_i, node_j, node_k, t, E, mu, rho, name=None):
        """
        params:
            node_i,node_j,node_k: Node, corners of triangle.
            t: float, thickness
            E: float, elastic modulus
            mu: float, Poisson ratio
            rho: float, mass density
        """
        super(Membrane3,self).__init__(node_i,node_j,node_k,t,E,mu,rho,6,name)

        x0=np.array([(node.x,node.y,node.z) for node in self._nodes])
        V=self.local_csys.transform_matrix
        o=self.local_csys.origin
        self._x0=(x0-np.array(o)).dot(V.T)[:,:2]
        
        D=self._D

        #calculate strain matrix
        abc0=self._abc(1,2)
        abc1=self._abc(2,0)
        abc2=self._abc(0,1)
        B0= np.array([[abc0[1],      0],
                      [      0,abc0[2]],
                      [abc0[2],abc0[1]]])
        B1= np.array([[abc1[1],     0],
                      [      0,abc1[2]],
                      [abc1[2],abc1[1]]])
        B2= np.array([[abc2[1],      0],
                      [      0,abc2[2]],
                      [abc2[2],abc2[1]]])
        self._B=np.hstack([B0,B1,B2])/2/self.area

        _Ke_=np.dot(np.dot(self._B(0).T,D),self._B(0))*self.area*self._t

        row=[a for a in range(0*2,0*2+2)]+\
            [a for a in range(1*2,1*2+2)]+\
            [a for a in range(2*2,2*2+2)]
        col=[a for a in range(0*6,0*6+2)]+\
            [a for a in range(1*6,1*6+2)]+\
            [a for a in range(2*6,2*6+2)]
        elm_node_count=3
        elm_dof=2
        data=[1]*(elm_node_count*elm_dof)
        G=sp.sparse.csr_matrix((data,(row,col)),shape=(elm_node_count*elm_dof,elm_node_count*6))
        self._Ke=G.transpose()*_Ke_*G

        #Concentrated mass matrix, may be wrong
        self._Me=np.eye(18)*rho*self.area*t/3
        
        self._re =np.zeros((18,1))
                
    def _abc(self,j,m):
        """
        conversion constant.
        """
        x,y=self._x0[:,0],self._x0[:,1]
        a=x[j]*y[m]-x[m]*y[j]
        b=y[j]-y[m]
        c=-x[j]+x[m]
        return np.array([a,b,c])

    def _N(self,x):
        """
        interpolate function.
        return: 3x1 array represent x,y
        """
        x,y=x[0],x[1]
        L=np.array((3,1))
        L[0]=self._abc(1,2).dot(np.array([1,x,y]))/2/self._area
        L[1]=self._abc(2,0).dot(np.array([1,x,y]))/2/self._area
        L[2]=self._abc(0,1).dot(np.array([1,x,y]))/2/self._area
        return L.reshape(3,1)
    
    def _x(self,L):
        """
        convert csys from L to x
        return: 2x1 array represent x,y
        """
        return np.dot(np.array(L).reshape(1,3),self._x0).reshape(2,1)
