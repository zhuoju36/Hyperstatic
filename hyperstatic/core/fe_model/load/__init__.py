# -*- coding: utf-8 -*-
from typing import Dict
import numpy as np
from hyperstatic.common.curve import Curve
from hyperstatic.core.fe_model.load.pattern import LoadPattern
class LoadCase(object):
    def __init__(self,name:str):
        self.__name=name
        self.__base_case=None
        self.__pattern:Dict[str,LoadPattern]={} #to save pattern objects
        self.__load_factor:Dict[str,float]={} #to assign load factor
        self.__load_curve:Dict[str,np.array]={} #to assign load curve
        self.__restraint:Dict[str,np.array]={}

    @property
    def name(self):
        return self.__name

    def add_pattern(self,pattern:LoadPattern,factor:float,curve:np.array=None):
        self.__pattern[pattern.name]=pattern
        self.__load_factor[pattern.name]=factor
        if curve is None:
            self.__load_curve[pattern.name]=np.array([[0,1],[1,1]])
        else:
            self.__load_curve[pattern.name]=curve

    def add_pattern_time_history(self,pattern:LoadPattern,factor:float,curve:np.array):
        self.__pattern[pattern.name]=pattern
        self.__load_factor[pattern.name]=factor
        self.__load_curve[pattern.name]=curve

    def set_pattern_factor(self,name,factor):
        self.__load_factor[name]=factor

    def set_nodal_restraint(self,name:str,u1:bool,u2:bool,u3:bool,r1:bool,r2:bool,r3:bool):
        self.__restraint[name]=np.array([u1,u2,u3,r1,r2,r3])

    def get_nodal_restraint_dict(self):
        res={}
        for k,v in self.__restraint.items():
            res[k]=np.array(v)
        return res

    def get_max_min_step(self):
        ma=0
        mi=1e20
        for v in self.__load_curve.values():
            ma=max(ma,v.shape[1])
            mi=min(mi,v.shape[1])
        return ma,mi
        

    # def get_nodal_f(self,name):
    #     fn=np.zeros(6)
    #     for patname,factor in self.__load_factor.items():
    #         pat=self.__pattern[patname]
    #         f=pat.get_nodal_f(name)
    #         if f is None:
    #             continue
    #         fn+=f*factor   
    #     return fn

    def get_nodal_f(self,name,time_step=0):
        fn=np.zeros(6)
        for patname,factor in self.__load_factor.items():
            pat=self.__pattern[patname]
            f=pat.get_nodal_f(name)
            if f is None:
                continue
            fn+=f*factor*self.__load_curve[patname][1,time_step]
        return fn

    def get_nodal_f_time_history(self,name):
        max_length=0
        for patname,curve in self.__load_curve.items():
            l=curve.shape[1]
            max_length=max(l,max_length)

        fn=np.zeros((max_length,6))
        for patname in self.__load_factor.keys():
            pat=self.__pattern[patname]
            factor=self.__load_factor[patname]
            curve=self.__load_curve[patname]
            f=pat.get_nodal_f(name)
            if f is None:
                continue
            crv=curve[1,:]
            fn+=crv.reshape(crv.size,1).dot(f.reshape(1,6))*factor
        return fn

    def get_nodal_f_dict(self):
        res={}
        for patname,pat in self.__pattern.items():
            d=pat.get_nodal_f_dict()
            for node,load in d.items():
                if node in res.keys():
                    res[node]+=load*self.__load_factor[patname]
                else:
                    res[node]=np.zeros(6)
        return res

    def get_nodal_f_time_history_dict(self,name):
        max_length=0
        for patname,curve in self.__load_curve.keys():
            l=curve.shape[1]
            max_length=max(l,max_length)
        res={}
        for patname in self.__load_factor.keys():
            pat=self.__pattern[patname]
            factor=self.__load_factor[patname]
            curve=self.__load_curve[patname]
            d=pat.get_nodal_f_dict()
            for node,load in d.items():
                if node in res.keys():
                    crv=curve[1,:]
                    fn+=crv.reshape(crv.size,1).dot(f.reshape(1,6))*factor
                else:
                    res[node]=np.zeros((max_length,6))
        return res

    def get_nodal_d_dict(self):
        res={}
        for patname,pat in self.__pattern.items():
            d=pat.get_nodal_d_dict()
            for node,load in d.items():
                if node in res.keys():
                    res[node]+=load*self.__load_factor[patname]
                else:
                    res[node]=np.zeros(6)
        return res


    def get_beam_f(self,name,l):
        fe=np.zeros(12)
        for patname,factor in self.__load_factor.items():
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
                    res[beam]+=load*self.__load_factor[patname]
                else:
                    res[beam]=np.zeros(6)
        return res

    def get_settings(self)->dict:
        raise NotImplementedError

if __name__ == '__main__':    
    lc=LoadCase("lc")
    lp1=LoadPattern("lp1")
    lp2=LoadPattern("lp2")
    lp1.set_nodal_load("1",1,1,1,0,0,0)
    lp2.set_nodal_load("1",2,2,2,0,0,0)
    lc.add_pattern(lp1,1)
    lc.add_pattern(lp2,2)
    f=lc.get_nodal_f("1")
    assert f[0]==5
    assert f[2]==5

    lc=LoadCase("lc")
    lp1=LoadPattern("lp1")
    lp2=LoadPattern("lp2")
    lp1.set_nodal_load("1",1,2,3,0,0,0)
    lp2.set_nodal_load("1",2,2,2,0,0,0)
    c1=Curve.sin("sine",1,1,0,0.2,100).to_array()
    c2=Curve.sin("sine",1,2,0,0.2,100).to_array()
    lc.add_pattern_time_history(lp1,1,c1)
    lc.add_pattern_time_history(lp2,1,c2)
    f=lc.get_nodal_f_time_history("1")
    assert f[10,2]==1.2142872898611885