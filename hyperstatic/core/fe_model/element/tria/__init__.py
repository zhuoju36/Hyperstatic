import numpy as np
from hyperstatic.common.csys import Cartesian
from hyperstatic.core.fe_model.node import Node
from hyperstatic.core.fe_model.element import Element
from hyperstatic.common.tolerance import Tolerance

class Tria(Element):
    def __init__(self,name,node_i:Node,node_j:Node,node_k:Node,dof):
        self._nodes=[node_i,node_j,node_k]
        #Initialize local CSys
        o=[(node_i.x+node_j.x+node_k.x)/3,
            (node_i.y+node_j.y+node_k.y)/3,
            (node_i.z+node_j.z+node_k.z)/3]
        vec1=node_i.loc-node_j.loc
        vec2=node_j.loc-node_k.loc
        n=np.cross(vec1,vec2)
        n=n/np.linalg.norm(n)
        tol=Tolerance.abs_tol()
        if np.linalg.norm(n-np.array([0,0,1]))<tol:
            csys = Cartesian.create_by_normal(o, n, guide=[0,1,0])
        else:
            csys = Cartesian.create_by_normal(o, n)
        super(Tria,self).__init__(name,[node_i,node_j,node_k],2,dof,csys)
        self.__area=0.5*np.linalg.det(np.array([[1,1,1],
                                    [node_j.x-node_i.x,node_j.y-node_i.y,node_j.z-node_i.z],
                                    [node_k.x-node_i.x,node_k.y-node_i.y,node_k.z-node_i.z]]))

    @property
    def area(self):
        return self.__area
