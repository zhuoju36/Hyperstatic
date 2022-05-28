# -*- coding: utf-8 -*-
from typing import Dict
import numpy as np
from structengpy.core.fe_model.load.pattern import LoadPattern
class LoadCase(object):
    def __init__(self,name:str):
        self.__name=name
        self.__preloadcase=None
        self.__pattern:Dict[str,LoadPattern]={} #to save pattern objects
        self.__loadfactor:Dict[str,float]={} #to assign load factor
        self.__restraint:Dict[str,np.array]={}

    @property
    def name(self):
        return self.__name

    def add_pattern(self,pattern:LoadPattern,factor:float):
        self.__pattern[pattern.name]=pattern
        self.__loadfactor[pattern.name]=factor

    def set_pattern_factor(self,name,factor):
        self.__loadfactor[name]=factor

    def set_nodal_restraint(self,name:str,u1:bool,u2:bool,u3:bool,r1:bool,r2:bool,r3:bool):
        self.__restraint[name]=np.array([u1,u2,u3,r1,r2,r3])

    def get_nodal_restraint_dict(self):
        res={}
        for k,v in self.__restraint.items():
            res[k]=np.array(v)
        return res

    def get_nodal_f(self,name):
        fn=np.zeros(6)
        for patname,factor in self.__loadfactor.items():
            pat=self.__pattern[patname]
            f=pat.get_nodal_f(name)
            if f is None:
                continue
            fn+=f*factor   
        return fn

    def get_nodal_f_dict(self):
        res={}
        for patname,pat in self.__pattern.items():
            d=pat.get_nodal_f_dict()
            for node,load in d.items():
                if node in res.keys():
                    res[node]+=load*self.__loadfactor[patname]
                else:
                    res[node]=np.zeros(6)
        return res

    def get_nodal_d_dict(self):
        res={}
        for patname,pat in self.__pattern.items():
            d=pat.get_nodal_d_dict()
            for node,load in d.items():
                if node in res.keys():
                    res[node]+=load*self.__loadfactor[patname]
                else:
                    res[node]=np.zeros(6)
        return res


    def get_beam_f(self,name,l):
        fe=np.zeros(12)
        for patname,factor in self.__loadfactor.items():
            pat=self.__pattern[patname]
            f=pat.get_beam_f(name,l)
            if f is None:
                continue
            fe+=f*factor
        return fe

    def get_beam_f_dict(self,ldict):
        res={}
        for patname,pat in self.__pattern.items():
            d=pat.get_beam_f_dict(ldict)
            for beam,load in d.items():
                if beam in res.keys():
                    res[beam]+=load*self.__loadfactor[patname]
                else:
                    res[beam]=np.zeros(6)
        return res