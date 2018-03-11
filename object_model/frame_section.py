# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:32:16 2016

@author: HZJ
"""
import uuid
import numpy as np

class Section(object):
    def __init__(self,mat,A,J,I33,I22,W33,W22,name=None):
        """
        mat: material
        A: area
        J: Torsional constant
        I33,I22: Iteria momentum
        W33,W22: Bending modulus
        """        
        self._mat=mat
        self._A=A
        self._J=J
        self._I33=I33
        self._I22=I22
        self._W33=W33
        self._W22=W22
        self._name=uuid.uuid1() if name==None else name
        
    @property
    def name(self):
        return self._name

    @property
    def A(self):
        return self._A
        
    @property
    def J(self):
        return self._J
        
    @property
    def I33(self):
        return self._I33
    
    @property
    def I22(self):
        return self._I22
        
    @property
    def W33(self):
        return self._W33
        
    @property
    def W22(self):
        return self._W22
        
    @property
    def i33(self):
        return np.sqrt(self._I33/self.__A)

    @property  
    def i22(self):
        return np.sqrt(self._I22/self.__A)
        
    @property
    def material(self):
        return self._mat
        
        
class Rectangle(Section):
    def __init__(self,mat,h,b,name=None):
        """
        h - height\n
        b - width\n
        """
        self.h=h
        self.b=b
        A=h*b
        J=h*b**3/3 #WRONG!!!
        I33=b*h**3/12
        I22=h*b**3/12
        W33=I33/h*2
        W22=I22/b*2
        super(Rectangle,self).__init__(mat,A,J,I33,I22,W33,W22,name)
#        self.gamma33=1.05
#        self.gamma22=1.05


class Circle(Section):
    def __init__(self,mat,d,name=None):
        """
        d - diameter
        """
        self.d=d
        A=np.pi*d**2/4
        J=np.pi*d**4/32
        I33=np.pi*d**4/64
        I22=I33
        W33=I33/d*2
        W22=W33
        super(Circle,self).__init__(mat,A,J,I33,I22,W33,W22,name)
#        self.gamma33=1.15
#        self.gamma22=1.15
        
class Pipe(Section):
    def __init__(self,mat,d,t,name=None):
        """
        d - diameter\n
        t - thickness of wall\n
        fab - fabrication\n
            'r' - rolled\n
            'w' - welded\n
        """
        self.d=d
        self.t=t
        A=np.pi*d**2/4-np.pi*(d-2*t)**2/4
        J=np.pi*(d-t)/t*2*A
        I33=np.pi*d**4/64*(1-((d-2*t)/d)**4)
        I22=I33
        W33=I33/d*2
        W22=W33
        super(Pipe,self).__init__(mat,A,J,I33,I22,W33,W22,name)
        
#        self.gamma33=1.15
#        self.gamma22=1.15
#        if fab=='r':
#            self.cls33='b'
#            self.cls22='b'
#        elif fab=='w':
#            self.cls33='c'
#            self.cls22='c'
#        else:
#            raise ValueError('wrong fabrication!')

class HollowBox(Section):
    def __init__(self,mat,h,b,tw,tf,name=None):
        """
        h - height\n
        b - width\n
        tw - thickness of web\n
        tf - thickness of flange\n
        fab - fabrication\n
            'r' - rolled\n
            'w' - welded\n
        """
        self.h=h
        self.b=b
        self.tw=tw
        self.tf=tf
        A=h*b-(h-2*tf)*(b-2*tw)
        J=(2*tw*(h-tf)/tw+2*tf*(b-tw)/tf)*2*A
        I33=b*h**3/12-(b-2*tw)*(h-2*tf)**3/12
        I22=h*b**3/12-(h-2*tf)*(b-2*tw)**3/12
        W33=I33/h*2
        W22=I22/b*2
        super(HollowBox,self).__init__(mat,A,J,I33,I22,W33,W22,name)
        
#        self.gamma33=1.05
#        self.gamma22=1.05
#        self.cls33='c'
#        self.cls22='c'
        

class ISection(Section):
    def __init__(self,mat,h,b,tw,tf,name=None):
        """
        h - height\n
        b - width\n
        tw - thickness of web\n
        tf - thickness of flange\n
        fab - fabrication\n
            'r' - rolled\n
            'w' - welded\n
        """
        self.h=h
        self.b=b
        self.tw=tw
        self.tf=tf
        A=b*tf*2+tw*(h-2*tf)
        J=(b*tf**3*2+(h-tf)*tw**3)/3 #should be confirm!!!!!!!!!!
        I33=b*h**3/12-(b-tw)*(h-2*tf)**3/12
        I22=2*tf*b**3/12+(h-2*tf)*tw**3/12
        W33=I33/h*2
        W22=I22/b*2
        super(ISection,self).__init__(mat,A,J,I33,I22,W33,W22,name)
        
#        self.gamma33=1.05
#        self.gamma22=1.2
#        self.cls33='c'
#        self.cls22='c'
        
class ISection2(Section):
    def __init__(self,mat,h,b1,tf1,tw,b2,tf2,name=None):
        """
        h - height\n
        b1,b2 - width\n
        tw - thickness of web\n
        tf1,tf2 - thickness of flange\n
        fab - fabrication\n
            'r' - rolled\n
            'w' - welded\n
        """
        self.h=h
        self.b1=b1
        self.b2=b2
        self.tw=tw
        self.tf1=tf1
        self.tf2=tf2
        hw=h-tf1-tf2
        A=b1*tf1+b2*tf2+tw*hw
        self.y0=y0=(b1*tf1*(h-tf1/2)+b2*tf2*tf2/2+hw*tw*(hw/2+tf2))/A
        
        J=(b1*tf1**3+b2*tf2**3+(h-tf1/2-tf2/2)*tw**3)/3 #should be confirm!!!!!!!!!!

        I33=tw*hw**3/12
        I33+=b1*tf1**3/12+b1*tf1*(hw/2+tf1/2)**2
        I33+=b2*tf2**3/12+b2*tf2*(hw/2+tf2/2)**2
        I33-=A*(y0-h/2)**2
        
        I22=b1**3*tf1/12+b2**3*tf2/12+tw**3*hw/12
        W33=I33/max([y0,h-y0])
        W22=I22/max([b1/2,b2/2])
        super(ISection2,self).__init__(mat,A,J,I33,I22,W33,W22,name)
        
#        self.gamma33=1.05
#        self.gamma22=1.2
#        self.cls33='c'
#        self.cls22='c'
        
class TSection(Section):
    pass

class CSection(Section):
    pass

class LSection(Section):
    pass
   
if __name__=='__main__':
    pass