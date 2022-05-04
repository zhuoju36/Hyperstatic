import numpy as np


class Pattern(object):
    def __init__(self,name:str):
        self.__name=name
        self.__hid=None
        self.__nodal_load={}
        self.__nodal_disp={}
        self.__beam_distribute={}
        self.__beam_concentrate={}
        self.__srf_distribute={}

    @property
    def name(self):
        return self.__name

    @property
    def hid(self):
        return self.__hid

    @hid.setter
    def hid(self,val):
        assert type(val)==int
        self.__hid=val

    def add_nodal_load(self,name,f1,f2,f3,m1,m2,m3):
        self.__nodal_load[name]=np.array([f1,f2,f3,m1,m2,m3])

    def add_nodal_disp(self,name,u1,u2,u3,r1,r2,r3):
        self.__nodal_load[name]=np.array([u1,u2,u3,r1,r2,r3])

    def add_beam_distribute(self,name,fi1,fi2,fi3,mi1,mi2,mi3,fj1,fj2,fj3,mj1,mj2,mj3):
        self.__beam_distribute[name]=np.array([fi1,fi2,fi3,mi1,mi2,mi3,fj1,fj2,fj3,mj1,mj2,mj3]) 

    def get_nodal_load(self,name):
        return self.__nodal_load[name]

    def get_nodal_disp(self,name):
        return self.__nodal_load[name]

    def get_beam_distribute(self,name):
        return self.__beam_distribute[name]
        