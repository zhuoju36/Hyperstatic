import numpy as np
import scipy.sparse as spr
from hyperstatic.core.fe_model.meta.membranes import GQ12
from hyperstatic.core.fe_model.meta.plates import metaDKQ
from hyperstatic.core.fe_model.node import Node
from hyperstatic.core.fe_model.element.quad import Quad
from hyperstatic.core.fe_model.section.shell_section import ShellSection
import quadpy

class DKGQ(Quad):
    def __init__(self,name:str,section:ShellSection,node_i:Node, node_j:Node, node_k:Node, node_l:Node):
        self.__section=section
        super(DKGQ,self).__init__(name,node_i, node_j, node_k, node_l,24)

    def integrate_K(self):
        X=np.array([
            self.nodes[0].loc,
            self.nodes[1].loc,
            self.nodes[2].loc,
            self.nodes[3].loc]
            )
        X_=X-self.local_csys.origin #not necessary
        X_=X_.dot(self.local_csys.transform_matrix.T)[:,:2]
        E=self.__section.E
        mu=self.__section.mu
        t=self.__section.t
        Km=np.zeros((12,12))
        Kp=np.zeros((12,12))
        if self.__section.ele_type=="membrane" or self.__section.ele_type=="shell":
            BDB=GQ12.get_binary_BDB()
            def func_m(x):
                res=[]
                for xi,eta in zip(x[0],x[1]):
                    res.append(BDB(E,mu,t,xi,eta,*tuple(X_.reshape(X_.size))))
                res=np.stack(res,axis=2)
                return res
            scheme = quadpy.c2.get_good_scheme(2)
            Km = scheme.integrate(
                func_m,
                quadpy.c2.rectangle_points([-1.0, 1.0], [-1.0, 1.0]),
            ) #12x12     

        if self.__section.ele_type=="plate" or self.__section.ele_type=="shell":
            bBDB=metaDKQ.get_binary_BDB()
            def func_p(x):
                res=[]
                for xi,eta in zip(x[0],x[1]):
                    res.append(bBDB(E,mu,t,xi,eta,*tuple(X_.reshape(X_.size))))
                return np.stack(res,axis=2)
            scheme = quadpy.c2.get_good_scheme(2)
            Kp = scheme.integrate(
                func_p,
                quadpy.c2.rectangle_points([-1.0, 1.0], [-1.0, 1.0]),
            )

        K=np.zeros((24,24))
        for i in range(4):
            for j in range(4):
                K[i*6+2:i*6+5,j*6+2:j*6+5]=Kp[i*3:i*3+3,j*3:j*3+3]
                K[  i*6:i*6+2,  j*6:j*6+2]=Km[i*3:i*3+2,j*3:j*3+2]
                K[      i*6+5,  j*6:j*6+2]=Km[    i*3+2,j*3:j*3+2]
                K[  i*6:i*6+2,      j*6+5]=Km[i*3:i*3+2,    j*3+2]
                K[      i*6+5,      j*6+5]=Km[    i*3+2,    j*3+2]
        return spr.csr_matrix(K)

    @property
    def transform_matrix(self):
        T=np.zeros((24,24))
        for i in range(8):
            T[3*i:3*i+3,3*i:3*i+3]=self.local_csys.transform_matrix
        return spr.csr_matrix(T)

if __name__=='__main__':
    from hyperstatic.core.fe_model.node import Node
    from hyperstatic.core.fe_model.material.isotropy import IsotropicMaterial
    from hyperstatic.core.fe_model.section.shell_section import ShellSection
    from hyperstatic.core.fe_model.node import Node

    # n1=Node("1",1,-1,0)
    # n2=Node("2",1,1,0)
    # n3=Node("3",-1,1,0)
    # n4=Node("4",-1,-1,0)

    n1=Node("1",-1,-1,0)
    n2=Node("2",1,-1,0)
    n3=Node("3",1,1,0)
    n4=Node("4",-1,1,0)

    steel=IsotropicMaterial('mat',7.849e3,2e11,0.3,1.17e-5) #Q345
    section=ShellSection('sec',steel,0.25,'shell')
    ele=DKGQ("ele",section,n1,n2,n3,n4)
    K=ele.integrate_K()
    assert K.shape==(24,24)
    i=2
    j=2
    print(K[i*6+2,j*6:j*6+6 ]/1e8)

