import numpy as np
import scipy.sparse as spr

from structengpy.csys import Cartisian
from structengpy.fe_model.node import Node
from structengpy.fe_model.element import Element
from structengpy.fe_model.common import Tolerance

class Line(Element):
    def __init__(self,name,node_i:Node,node_j:Node,dof:int):        
        #Initialize local CSys
        tol=Tolerance.abs_tol()
        o = node_i.loc
        pt1 = node_j.loc
        pt2 = node_i.loc
        if abs(node_i.x - node_j.x) < tol and abs(node_i.y - node_j.y) < tol:
            pt2[0] += 1
        else:
            pt2[2] += 1
        super(Line,self).__init__([node_i,node_j],1,dof,Cartisian(o, pt1, pt2),name)

    @property
    def length(self):
        A=self.nodes[0].loc
        B=self.nodes[1].loc
        return np.linalg.norm(A-B)

    @property
    def transform_matrix(self):
        T=np.zeros((12,12))
        V=super(Line,self).local_csys.transform_matrix
        T[:3,:3]=T[3:6,3:6]=T[6:9,6:9]=T[9:,9:]= V
        return spr.csr_matrix(T)

if __name__=="__main__":
    n1=Node(0,1,0)
    n2=Node(1,1,0)
    l=Line(n1,n2,6)
    print(l.length)
    print(l.transform_matrix)
