# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:30:59 2016

@author: HZJ
"""
import uuid
import numpy as np
        
class Material(object):
    def __init__(self,gamma,name=None):
        """
        gamma: density.
        name: optional, an uuid is given by default.
        """
        self._gamma = gamma
        self._name=uuid.uuid1() if name==None else name
    
    @property
    def name(self):
        return self._name
        
    @property
    def gamma(self):
        return self._gamma
        
class Elastic(Material):
    def __init__(self,gamma,C,alpha,name=None):
        """
        gamma: density.
        C: flexity matrix, 6x6 matrix.
        alpha: expansion coefficient, 6x1 vector.
        name: optional, an uuid is given by default.
        """
        super(Elastic,self).__init__(gamma,name)
        self._C=C
        self._alpha=alpha
        self._E=np.linalg.inv(C)
        
    @property
    def C(self):
        """
        flexity matrix.
        """
        return self._C
        
    @property
    def alpha(self):
        """
        expansion conefficient vector.
        """
        return self._alpha
        
    @property
    def E(self):
        """
        stiffness matrix.
        """
        return self._E
        
    def d(self,f,dT):
        return self._C.dot(f)+dT*self._alpha
        
    def f0(self,dT):
        return -dT*self._E.dot(self._alpha)
        
    def f(self,d,dT):
        return self._E.dot(d)+self.f0(dT)
        
class OrthogonalElastic(Material):
    pass
        
class IsotropyElastic(Elastic):
    def __init__(self,gamma,E,mu,alpha,name=None):
        """
        gamma: density.
        E: Elastic modulus.
        mu: possion ratio.
        alpha: expansion coefficient.
        name: optional, an uuid is given by default.
        """
        self._G=E/2/(1+mu)
        self._Emod=E #Young's Modulus
        self._mu=mu
        alpha=alpha*np.array([1,1,1,0,0,0])
        
        G=self._G
        C=np.array([[  1/E,-mu/E,-mu/E,  0,  0,  0],
                        [-mu/E,  1/E,-mu/E,  0,  0,  0],
                        [-mu/E,-mu/E,  1/E,  0,  0,  0],
                        [    0,    0,    0,1/G,  0,  0],
                        [    0,    0,    0,  0,1/G,  0],
                        [    0,    0,    0,  0,  0,1/G]])
        super(IsotropyElastic,self).__init__(gamma,C,alpha,name)
        
    @property
    def mu(self):
        return self._mu
    
    @property
    def G(self):
        return self._G
    
    @property                    
    def D(self):
        lamb=self.E*self._mu/(1+self._mu)/(1-2*self._mu)
        G=self.G
        return np.array([[lamb+2*G,lamb,lamb,0,0,0],
                         [lamb,lamb+2*G,lamb,0,0,0],
                         [lamb,lamb,lamb+2*G,0,0,0],
                         [   0,   0,       0,G,0,0],
                         [   0,   0,       0,0,G,0],
                         [   0,   0,       0,0,0,G]])
    
    @property
    def Emod(self):
        return self._Emod

class Metal(IsotropyElastic):
    def __init__(self,gamma,E,mu,alpha,fy,name=None):
        self._fy=fy
        super(Metal,self).__init__(gamma,E,mu,alpha,name) 
    
    @property
    def fy(self):
        return self._fy
    
class Concrete(IsotropyElastic):
    def __init__(self,gamma,E,mu,alpha,fc,ft,name=None):
        self._fc=fc
        self._ft=ft
        super(Concrete,self).__init__(gamma,E,mu,alpha,name) 
    
    @property
    def fc(self):
        return self._fc

    @property
    def ft(self):
        return self._ft
    
class Timber(OrthogonalElastic):
    pass
        
if __name__=='__main__':
    steel=IsotropyElastic(7849.0474,2.000E11,0.3,1.17e-5)#Q345
    print(steel.D)
        
    