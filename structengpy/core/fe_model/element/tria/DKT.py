import numpy as np
import scipy.sparse as spr

from structengpy.core.fe_model.meta.plates import metaDKT
from structengpy.core.fe_model.meta.membranes import T9

from structengpy.core.fe_model.node import Node
from structengpy.core.fe_model.element.tria import Tria
from structengpy.core.fe_model.section.shell_section import ShellSection
import quadpy

class DKT(Tria):
    def __init__(self,name:str,section:ShellSection,node_i:Node, node_j:Node, node_k:Node):
        self.__section=section
        super(DKT,self).__init__(name,node_i, node_j, node_k, 9)

    def integrate_K(self):
        bBDBp=metaDKT.get_binary_BDB()
        X=np.array([
            self.nodes[0].loc,
            self.nodes[1].loc,
            self.nodes[2].loc]
            )
        X_=X.dot(self.local_csys.transform_matrix.T)[:,:2]
        E=self.__section.E
        mu=self.__section.mu
        t=self.__section.t
        def func(x):
            res=[]
            for xi,eta in zip(x[0],x[1]):
                res.append(bBDBp(E,mu,t,xi,eta,*tuple(X_.reshape(X_.size))))
            return np.stack(res,axis=2)
        scheme = quadpy.c2.get_good_scheme(2)
        Kp = scheme.integrate(
            func,
            quadpy.c2.rectangle_points([-1.0, 1.0], [-1.0, 1.0]),
        )
        bBDBm=T9.get_binary_BDB()
        Km = t*self.area*bBDBm(E,mu,t,*tuple(X_.reshape(X_.size)))
        
        K=np.zeros((18,18))
        for i in range(3):
            for j in range(3):
                K[i*6+2:i*6+5,j*6+2:j*6+5]=Kp[i*3:i*3+3,j*3:j*3+3]
                K[  i*6:i*6+2,  j*6:j*6+2]=Km[i*2:i*2+2,j*2:j*2+2]
                # K[  i*6:i*6+2,  j*6:j*6+2]=Km[i*3:i*3+2,j*3:j*3+2]
                # K[      i*6+5,  j*6:j*6+2]=Km[    i*3+2,j*3:j*3+2]
                # K[  i*6:i*6+2,      j*6+5]=Km[i*3:i*3+2,    j*3+2]
                # K[      i*6+5,      j*6+5]=Km[    i*3+2,    j*3+2]
        # KK=bBDBm(E,mu,t,*tuple(X_.reshape(X_.size)))
        # for i in range(KK.shape[0]):
        #     for j in range(KK.shape[1]):
        #         print("%4.2fe9 "%(KK[i,j]/1e9),end="")
        #     print("\n")
        return spr.csr_matrix(K)

    @property
    def transform_matrix(self):
        T=np.zeros((18,18))
        for i in range(6):
            T[3*i:3*i+3,3*i:3*i+3]=self.local_csys.transform_matrix
        return spr.csr_matrix(T)
if __name__=='__main__':
    from structengpy.core.fe_model.node import Node
    from structengpy.core.fe_model.material.isotropy import IsotropicMaterial
    from structengpy.core.fe_model.node import Node
    from time import time 
    n1=Node("1",1,-1,0)
    n2=Node("2",1,1,0)
    n3=Node("3",-1,1,0)

    # n1=Node("1",-1,-1,0)
    # n2=Node("2",1,-1,0)
    # n3=Node("3",1,1,0)
    # n4=Node("4",-1,1,0)

    steel=IsotropicMaterial('mat',7.849e3,2e11,0.3,1.17e-5) #Q345
    section=ShellSection('sec',steel,0.25)
    ele=DKT("ele",section,n1,n2,n3)
    beg=time()
    K=ele.integrate_K()
    print(time()-beg)
    assert K.shape==(12,12)
    i=1
    print(K.toarray()[3*i,:]/1e8)

