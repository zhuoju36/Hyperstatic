# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:32:16 2016

@author: HZJ
"""
import uuid
import math
from . import Material

class Section(object):
    def __init__(self,mat:Material.Material,A,J,I33,I22,W33,W22,name=None):
        """
        mat: material
        A: area
        J: Torsional constant
        I33,I22: Iteria momentum
        W33,W22: Bending modulus
        """        
        self.__mat=mat
        self.__A=A
        self.__J=J
        self.__I33=I33
        self.__I22=I22
        self.__W33=W33
        self.__W22=W22
        self.__name=uuid.uuid1() if name==None else name
        
    @property
    def name(self):
        return self.__name

    @property
    def A(self):
        return self.__A
        
    @property
    def J(self):
        return self.__J
        
    @property
    def I33(self):
        return self.__I33
    
    @property
    def I22(self):
        return self.__I22
        
    @property
    def W33(self):
        return self.__W33
        
    @property
    def W22(self):
        return self.__W22
        
    @property
    def i33(self):
        return math.sqrt(self.__I33/self.__A)

    @property  
    def i22(self):
        return math.sqrt(self.__I22/self.__A)
        
    @property
    def material(self):
        return self.__mat
        
        
class Rectangle(Section):
    def __init__(self,mat,h,b,name=None):
        """
        h - height\n
        b - width\n
        """
        self.h=h
        self.b=b
        A=h*b
        I33=b*h**3/12
        I22=h*b**3/12
        W33=I33/h*2
        W22=I22/b*2
        super().__init__(mat,A,I33,I22,W33,W22,name)
#        self.gamma33=1.05
#        self.gamma22=1.05


class Rircle(Section):
    def __init__(self,mat,d,name=None):
        """
        d - diameter
        """
        self.d=d
        A=math.pi*d**2/4
        I33=math.pi*d**4/64
        I22=I33
        W33=I33/d*2
        W22=W33
        super().__init__(mat,A,I33,I22,W33,W22,name)
#        self.gamma33=1.15
#        self.gamma22=1.15
        
class Pipe(Section):
    def __init__(self,mat,d,t,fab='r',name=None):
        """
        d - diameter\n
        t - thickness of wall\n
        fab - fabrication\n
            'r' - rolled\n
            'w' - welded\n
        """
        self.d=d
        self.t=t
        A=math.pi*d**2/4-math.pi*(d-2*t)**2/4
        I33=math.pi*d**4/64*(1-((d-2*t)/d)**4)
        I22=I33
        W33=I33/d*2
        W22=W33
        super().__init__(mat,A,I33,I22,W33,W22,name)
        self.gamma33=1.15
        self.gamma22=1.15
        if fab=='r':
            self.cls33='b'
            self.cls22='b'
        elif fab=='w':
            self.cls33='c'
            self.cls22='c'
        else:
            raise ValueError('wrong fabrication!')

class HollowBox(Section):
    def __init__(self,mat,h,b,tw,tf,fab='r',name=None):
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
        I33=b*h**3/12-(b-2*tw)*(h-2*tf)**3/12
        I22=h*b**3/12-(h-2*tf)*(b-2*tw)**3/12
        W33=I33/h*2
        W22=I22/b*2
        super().__init__(mat,A,I33,I22,W33,W22,name)
        self.gamma33=1.05
        self.gamma22=1.05
        self.cls33='c'
        self.cls22='c'
        

class ISection(Section):
    def __init__(self,mat,h,b,tw,tf,fab='r',name=None):
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
        super().__init__(mat,A,J,I33,I22,W33,W22,name)
        self.gamma33=1.05
        self.gamma22=1.2
        self.cls33='c'
        self.cls22='c'
        
class ISection2(Section):
    def __init__(self,mat,h,b1,tf1,tw,b2,tf2,fab='r',name=None):
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
        
        I33=tw*hw**3/12
        I33+=b1*tf1**3/12+b1*tf1*(hw/2+tf1/2)**2
        I33+=b2*tf2**3/12+b2*tf2*(hw/2+tf2/2)**2
        I33-=A*(y0-h/2)**2
        
        I22=b1**3*tf1/12+b2**3*tf2/12+tw**3*hw/12
        W33=I33/max([y0,h-y0])
        W22=I22/max([b1/2,b2/2])
        super().__init__(mat,A,I33,I22,W33,W22,name)
        self.gamma33=1.05
        self.gamma22=1.2
        self.cls33='c'
        self.cls22='c'
        
class TSection(Section):
    pass

class CSection(Section):
    pass

class LSection(Section):
    pass

class AreaSection(object):
    def __init__(self,mat,t):
        self.__mat=mat
        self.t=t
    
    @property
    def material(self):
        return self.__mat
   
if __name__=='__main__':
    pass