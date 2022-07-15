
import numpy as np
from structengpy.core.fe_model.material import Material


class IsotropyMaterial(Material):
    def __init__(self,name,rho,E,mu,a):
        super().__init__(self,name,rho,"isotropy")
        self.__E=E # Elastic modulus
        self.__mu=mu # Possion rato
        self.__a=a #thermo expansion factor

    @property
    def name(self):
        return super().name

    @property
    def rho(self):
        return super().rho

    @property
    def E(self):
        return self.__E

    @property
    def mu(self):
        return self.__E

    @property
    def a(self):
        return self.__a

    @property
    def G(self):
        E=self.__E
        mu=self.__mu
        return E/2/(1+mu) 

    @property
    def lamda(self):
        E=self.__E
        mu=self.__mu
        return E/(1+mu)/(1-2*mu)

    def C(self,exx,eyy,ezz,gxy,gyz,gzx)->np.array:
        return np.array([[exx, gxy/2, gzx/2], 
        [gxy/2, eyy, gyz/2], 
        [gzx/2, gyz/2, ezz]])

    @property
    def D(self,exx,eyy,ezz,gxy,gyz,gzx)->np.array:
        E=self.__E
        nu=self.__m
        return np.array([[E*eyy*nu/((1 - 2*nu)*(nu + 1)) + E*ezz*nu/((1 - 2*nu)*(nu + 1)) + exx*(E*nu/((1 - 2*nu)*(nu + 1)) + E/(nu + 1)), E*gxy/(2*(nu + 1)), E*gzx/(2*(nu + 1))], [E*gxy/(2*(nu + 1)), E*exx*nu/((1 - 2*nu)*(nu + 1)) + E*ezz*nu/((1 - 2*nu)*(nu + 1)) + eyy*(E*nu/((1 - 2*nu)*(nu + 1)) + E/(nu + 1)), E*gyz/(2*(nu + 1))], [E*gzx/(2*(nu + 1)), E*gyz/(2*(nu + 1)), E*exx*nu/((1 - 2*nu)*(nu + 1)) + E*eyy*nu/((1 - 2*nu)*(nu + 1)) + ezz*(E*nu/((1 - 2*nu)*(nu + 1)) + E/(nu + 1))]])


