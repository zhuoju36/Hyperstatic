import numpy as np

from structengpy.core.fe_model.meta.plates.TMQ import bBDBb,bBDBs
from structengpy.core.fe_model.node import Node
from structengpy.core.fe_model.element.quad import Quad
from structengpy.core.fe_model.section.shell_section import ShellSection
import quadpy

# from quadpy import Quadpy

class TMQ(Quad):
    def __init__(self,name:str,section:ShellSection,node_i:Node, node_j:Node, node_k:Node, node_l:Node):
        self.__section=section
        super(TMQ,self).__init__(name,node_i, node_j, node_k, node_l,12)

    def integrate_K(self):
        X=np.array([
            self.nodes[0].loc,
            self.nodes[1].loc,
            self.nodes[2].loc,
            self.nodes[3].loc]
            )
        X_=X.dot(self.local_csys.transform_matrix.T)[:,:2]
        def func(x):
            E=self.__section.E
            mu=self.__section.mu
            t=self.__section.t
            res=[]
            for xi,eta in zip(x[0],x[1]):
                res.append(bBDBb(E,mu,t,xi,eta,*tuple(X_.reshape(X_.size))))
            return np.stack(res,axis=2)
        scheme = quadpy.c2.get_good_scheme(2)
        Kb = scheme.integrate(
            func,
            quadpy.c2.rectangle_points([-1.0, 1.0], [-1.0, 1.0]),
        )
        def func(x):
            E=self.__section.E
            mu=self.__section.mu
            t=self.__section.t
            res=[]
            for xi,eta in zip(x[0],x[1]):
                res.append(bBDBs(E,mu,t,xi,eta,*tuple(X_.reshape(X_.size))))
            return np.stack(res,axis=2)
        scheme = quadpy.c2.get_good_scheme(2)
        Ks = scheme.integrate(
            func,
            quadpy.c2.rectangle_points([-1.0, 1.0], [-1.0, 1.0]),
        )
        return Kb+Ks

from structengpy.core.fe_model.material.isotropy import IsotropicMaterial

n1=Node("1",0,0,0)
n2=Node("2",1,0,0)
n3=Node("3",1,1,1)
n4=Node("4",0,1,1)
mat=IsotropicMaterial("mat",1,2,3,1e-7)
section=ShellSection("sec",mat,1)
m=TMQ("m1",section,n1,n2,n3,n4)
res=m.integrate_K()

print(res.shape)