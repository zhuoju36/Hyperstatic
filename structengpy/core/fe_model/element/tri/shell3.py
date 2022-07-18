import numpy as np
from structengpy.core.fe_model.element.quad import Quad
from structengpy.core.fe_model.section.shell_section import ShellSection

class Shell3(Quad):
    def __init__(self,name,node_i, node_j, node_k, node_l, section:ShellSection):
        super().__init__(name,node_i,node_j,node_k,node_l,12)
        self.__releases=np.array([False,False,False,False,False,False,False,False,False,False,False,False])
        self.__rotation=0
        self.__section=section
        self.__offset=np.zeros(2)

    def integrate_K(self):
        pass

    def integrate_M(self):
        pass

    def integrate_C(self):
        pass

    def integrate_f(self):
        pass