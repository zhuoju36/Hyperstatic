# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:30:59 2016

@author: HZJ
"""
import uuid
import numpy as np

#class material(object):
#    def __init__(self,E,mu,gamma,alpha,name=None):
#        self.E = E
#        self.mu = mu
#        self.gamma = gamma
#        self.alpha = alpha
#        self.shearModulus = E / 2 / (1 + mu)
#        self.__name=uuid.uuid1() if name==None else name
#        
#    @property
#    def name(self):
#        return self.__name
#
#    @property
#    def G(self):
#        return self.shearModulus
#    
#class linear_elastic(material):
#    def __init__(self,E,mu,gamma,alpha,name=None):
#        super().__init__(E,mu,gamma,alpha,name)
        
class material(object):
    def __init__(self,gamma,name=None):
        """
        gamma: density.
        name: optional, an uuid is given by default.
        """
        self.__gamma = gamma
        self.__name=uuid.uuid1() if name==None else name
    
    @property
    def name(self):
        return self.__name
        
    @property
    def gamma(self):
        return self.__gamma
        
class elastic(material):
    def __init__(self,gamma,C,alpha,name=None):
        """
        gamma: density.
        C: flexity matrix, 6x6 matrix.
        alpha: expansion coefficient, 1x6 vector.
        name: optional, an uuid is given by default.
        """
        self.__C=C
        self.__alpha=alpha
        self.__E=np.linalg.inv(C)
        super().__init__(gamma,name)
        
    @property
    def C_matrix(self):
        """
        flexity matrix.
        """
        return self.__C
        
    @property
    def alpha_vector(self):
        """
        expansion conefficient vector.
        """
        return self.__alpha
        
    @property
    def E_matrix(self):
        """
        stiffness matrix.
        """
        return self.__E
        
    def d(self,f,dT):
        return self.__C.dot(f)+dT*self.__alpha
        
    def f0(self,dT):
        return -dT*self.__E.dot(self.alpha)
        
    def f(self,d,dT):
        return self.__E.dot(d)+self.f0(dT)
        
class orthogonal_elastic(elastic):
    pass
        
class isotropy_elastic(elastic):
    def __init__(self,gamma,E,mu,alpha,name=None):
        """
        gamma: density.
        E: Elastic modulus.
        mu: possion ratio.
        alpha: expansion coefficient.
        name: optional, an uuid is given by default.
        """
        self.__G=E/2/(1+mu)
        G=self.__G
        C=np.array([[  1/E,-mu/E,-mu/E,  0,  0,  0],
                    [-mu/E,  1/E,-mu/E,  0,  0,  0],
                    [-mu/E,-mu/E,  1/E,  0,  0,  0],
                    [    0,    0,    0,1/G,  0,  0],
                    [    0,    0,    0,  0,1/G,  0],
                    [    0,    0,    0,  0,  0,1/G]])
        alpha=alpha*np.array([1,1,1,0,0,0])
        super().__init__(gamma,C,alpha,name)
    
    @property
    def G(self):
        return self.__G
    
    @property
    def E(self):
        return 1/self.C_matrix[1,1]
        
if __name__=='__main__':
    steel=isotropy_elastic(7849.0474,2.000E11,0.3,1.17e-5)#Q345
        
    