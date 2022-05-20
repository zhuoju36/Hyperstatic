import numpy as np
from structengpy.common.csys import Cartisian
from structengpy.core.fe_model.element import Element

class Tri(Element):
    def __init__(self,node_i,node_j,node_k,t,E,mu,rho,dof,name=None,tol=1e-6):
        
        self._nodes=[node_i,node_j,node_k]
        #Initialize local CSys
        o=[(node_i.x+node_j.x+node_k.x)/3,
            (node_i.y+node_j.y+node_k.y)/3,
            (node_i.z+node_j.z+node_k.z)/3]
        pt1 = [ node_j.x, node_j.y, node_j.z ]
        pt2 = [ node_i.x, node_i.y, node_i.z ]
        csys = Cartisian(o, pt1, pt2)
        super(Tri,self).__init__(2,dof,csys,name)

        self._area=0.5*np.linalg.det(np.array([[1,1,1],
                                    [node_j.x-node_i.x,node_j.y-node_i.y,node_j.z-node_i.z],
                                    [node_k.x-node_i.x,node_k.y-node_i.y,node_k.z-node_i.z]]))
        self._t=t
        self._E=E
        self._mu=mu

        E=self._E
        mu=self._mu
        D0=E/(1-mu**2)
        self._D=np.array([[1,mu,0],
                    [mu,1,0],
                    [0,0,(1-mu)/2]])*D0
        #3D to local 2D
        V=self.local_csys.transform_matrix
        x3D=np.array([[node_i.x,node_i.y,node_i.z],
                    [node_j.x,node_j.y,node_j.z],
                    [node_k.x,node_k.y,node_k.z]])
        x2D=np.dot(x3D,V.T)
        self._x2D=x2D[:,:2]

    @property
    def area(self):
        return self._area

    @property
    def local_csys(self):
        return super().local_csys

    @property
    def transform_matrix(self):
        return super().transform_matrix
