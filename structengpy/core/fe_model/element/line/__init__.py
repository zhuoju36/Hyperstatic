# -*- coding: utf-8 -*-
import numpy as np
import scipy.sparse as spr

from structengpy.common.csys import Cartesian
from structengpy.core.fe_model.node import Node
from structengpy.core.fe_model.element import Element
from structengpy.common.tolerance import Tolerance

class Line(Element):
    def __init__(self,name,start:Node,end:Node,dof:int):        
        #Initialize local CSys
        tol=Tolerance.abs_tol()
        o = (start.loc+end.loc)/2
        pt1 = end.loc
        pt2 = o + np.array([0,0,1])
        if np.max(np.abs((start.loc-end.loc)[:2])) < tol:
            pt2 = o + np.array([1,0,0])
        csys=Cartesian(o, pt1, pt2)
        super().__init__(name,[start,end],1,dof,csys)

    @property
    def start(self):
        return super().nodes[0].loc

    @property
    def end(self):
        return super().nodes[1].loc

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
