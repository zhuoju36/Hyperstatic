# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 12:04:56 2016

@author: huan
"""
import numpy as np

class Section:
    def __init__(self,A,I33,I22,W33,W22):
        """
        A   - [mm]\n
        I33 - [mm]\n
        I22 - [mm]\n
        W33 - [mm]\n
        W22 - [mm]\n
        """
        self.A=A
        self.I33=I33
        self.I22=I22
        self.W33=W33
        self.W22=W22
        self.i33=np.sqrt(self.I33/self.A)
        self.i22=np.sqrt(self.I22/self.A)
        
class Rectangle(Section):
    def __init__(self,h,b):
        """
        h - [mm]\n
        b - [mm]\n
        """
        self.h=h
        self.b=b
        A=h*b
        I33=b*h**3/12
        I22=h*b**3/12
        W33=I33/h*2
        W22=I22/b*2
        Section.__init__(self,A,I33,I22,W33,W22)
#        self.gamma33=1.05
#        self.gamma22=1.05


class Circle(Section):
    def __init__(self,d):
        """
        d - [mm]
        """
        self.d=d
        A=np.pi*d**2/4
        I33=np.pi*d**4/64
        I22=I33
        W33=I33/d*2
        W22=W33
        Section.__init__(self,A,I33,I22,W33,W22)
#        self.gamma33=1.15
#        self.gamma22=1.15
        
class Tube(Section):
    def __init__(self,d,t,fab='r'):
        """
        d - [mm]\n
        t - [mm]\n
        fab - fabrication\n
            'r' - rolled\n
            'w' - welded\n
        """
        self.d=d
        self.t=t
        A=np.pi*d**2/4-np.pi*(d-2*t)**2/4
        I33=np.pi*d**4/64*(1-((d-2*t)/d)**4)
        I22=I33
        W33=I33/d*2
        W22=W33
        Section.__init__(self,A,I33,I22,W33,W22)
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
    def __init__(self,h,b,tw,tf,fab='r'):
        """
        h - [mm]\n
        b - [mm]\n
        tw- [mm]\n
        tf- [mm]\n
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
        Section.__init__(self,A,I33,I22,W33,W22)
        self.gamma33=1.05
        self.gamma22=1.05
        self.cls33='c'
        self.cls22='c'
        
class IProfile(Section):
    def __init__(self,h,b,tw,tf,fab='r'):
        """
        h - [mm]\n
        b - [mm]\n
        tw- [mm]\n
        tf- [mm]\n
        fab - fabrication\n
            'r' - rolled\n
            'w' - welded\n
        """
        self.h=h
        self.b=b
        self.tw=tw
        self.tf=tf
        A=b*tf*2+tw*(h-2*tf)
        I33=b*h**3/12-(b-tw)*(h-2*tf)**3/12
        I22=2*tf*b**3/12+(h-2*tf)*tw**3/12
        W33=I33/h*2
        W22=I22/b*2
        Section.__init__(self,A,I33,I22,W33,W22)
        self.gamma33=1.05
        self.gamma22=1.2
        self.cls33='c'
        self.cls22='c'