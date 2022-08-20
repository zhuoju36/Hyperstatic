import numpy as np
import scipy.sparse as spr
from hyperstatic.core.fe_model.meta.membranes.GQ12 import get_binary_BDB
from hyperstatic.core.fe_model.node import Node
from hyperstatic.core.fe_model.element.tria import Tria
from hyperstatic.core.fe_model.section.shell_section import ShellSection
import quadpy

class T9(Tria):
    def __init__(self,name:str,section:ShellSection,node_i:Node, node_j:Node, node_k:Node):
        self.__section=section
        super(T9,self).__init__(name,node_i, node_j, node_k, 9)

    def integrate_K(self):
        BDB=get_binary_BDB()
        X=np.array([
            self.nodes[0].loc,
            self.nodes[1].loc,
            self.nodes[2].loc]
            )
        X_=X-self.local_csys.origin #not necessary
        X_=X_.dot(self.local_csys.transform_matrix.T)[:,:2]
        # assert X[0,2]==X[1,2]==X[2,2]==0
        E=self.__section.E
        mu=self.__section.mu
        t=self.__section.t
        K=t*self.area*BDB(E,mu,t,*tuple(X_.reshape(X_.size)))
        return spr.csr_matrix(K)

    @property
    def transform_matrix(self):
        T=np.zeros((12,12))
        T[:3,:3]=T[3:6,3:6]=T[6:9,6:9]=T[9:,9:]=self.local_csys.transform_matrix
        return spr.csr_matrix(T)

if __name__=='__main__':
    from hyperstatic.core.fe_model.node import Node
    from hyperstatic.core.fe_model.material.isotropy import IsotropicMaterial
    from hyperstatic.core.fe_model.section.shell_section import ShellSection
    from hyperstatic.core.fe_model.node import Node

    n1=Node("1",10,-10,0)
    n2=Node("2",10,10,0)
    n3=Node("3",-10,10,0)
    n4=Node("4",-10,-10,0)

    steel=IsotropicMaterial('mat',7.849e3,2e11,0.3,1.17e-5) #Q345
    section=ShellSection('sec',steel,0.25,'membrane')
    ele=T9("ele",section,n1,n2,n3)
    K=ele.integrate_K()
    assert K.shape==(12,12)
    print(K[0,:]/1e10)
