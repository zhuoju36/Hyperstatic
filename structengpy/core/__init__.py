# -*- coding: utf-8 -*-
import os
import logging
from typing import Dict
import numpy as np

from typing import Pattern
from structengpy.core.fe_model.assembly import Assembly
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load.pattern import LoadPattern
from structengpy.core.fe_model.load import LoadCase
from structengpy.core.fe_model.load.loadcase import StaticCase
from structengpy.core.fe_solver.static import StaticSolver
from structengpy.common.csys import Cartisian
from structengpy.core.fe_post.node import NodeResultResolver


class Api(object):
    def __init__(self,workpath:str):
        self.__csys=Cartisian((0,0,0),(1,0,0),(0,1,0),"Global")
        self.__model=Model()
        self.__loadcases:Dict[str,LoadCase]={}
        self.__loadpatterns:Dict[str,LoadPattern]={}
        # self.__nodal_restraint:Dict[str,np.ndarray]={}
        self.__workpath=workpath
        if not os.path.exists(workpath):
            try:
                os.mkdir(workpath)
            except:
                logging.info("Error creating workpath "+ workpath)
                self=None
        

    def add_node(self,name:str,x:float,y:float,z:float)->bool:
        try:
            self.__model.add_node(name,x,y,z)
            return True
        except:
            logging.warning("exception")
            return False

    def set_nodal_restraint(self,case:str,node:str,
            u1:bool=False,u2:bool=False,u3:bool=False,
            r1:bool=False,r2:bool=False,r3:bool=False,)->bool:
        try:
            self.__loadcases[case].set_nodal_restraint(node,u1,u2,u3,r1,r2,r3)
            return True
        except:
            logging.warning("exception")
            return False

    def set_nodal_mass(self,name:str,
            u1:float=0,u2:float=0,u3:float=0,
            r1:float=0,r2:float=0,r3:float=0,)->bool:
        try:
            self.__model.set_nodal_mass(name,u1,u2,u3,r1,r2,r3)
            return True
        except:
            logging.warning("exception")
            return False

    def add_beam(self,name:str,start:str,end:str,
            E:float,mu:float,
            A:float,I2:float,I3:float,J:float,rho:float)->bool:
        try:
            self.__model.add_beam(name,start,end,E,mu,A,I2,I3,J,rho)
            return True
        except:
            logging.warning("exception")
            return False

    def add_loadpattern(self,name:str)->bool:
        try:
            self.__loadpatterns[name]=LoadPattern(name)
            return True
        except:
            logging.warning("exception")
            return False

    def set_nodal_force(self,pattern:str,node:str,
            f1:float=0,f2:float=0,f3:float=0,
            m1:float=0,m2:float=0,m3:float=0)->bool:
        try:
            self.__loadpatterns[pattern].set_nodal_force(node,f1,f2,f3,m1,m2,m3)
            return True
        except:
            logging.warning("Error when setting nodal load")
            return False

    def add_beam_concentration(self)->bool:
        try:
            #TODO
            return True
        except:
            logging.warning("exception")
            return False

    def add_beam_distribution(self)->bool:
        try:
            #TODO
            return True
        except:
            logging.warning("exception")
            return False

    def add_static_case(self,name)->bool:
        try:
            self.__loadcases[name]=StaticCase(name)
            return True
        except:
            logging.warning("exception")
            return False

    def add_case_pattern(self,case:str,pattern:str,factor:float)->bool:
        try:
            lc=self.__loadcases[case]
            pat=self.__loadpatterns[pattern]
            lc.add_pattern(pat,factor)
            return True
        except:
            logging.warning("exception")
            return False

    def set_beam_release(self,name,r1i=False,r2i=False,r3i=False,m1i=False,m2i=False,m3i=False,r1j=False,r2j=False,r3j=False,m1j=False,m2j=False,m3j=False)->bool:
        try:
            res=np.array([r1i,r2i,r3i,m1i,m2i,m3i,r1j,r2j,r3j,m1j,m2j,m3j])
            self.__model.set_beam_releases(name,)
            return True
        except:
            logging.warning("exception")
            return False

    def solve_static(self,casename):
        try:
            workpath=self.__workpath
            model=self.__model
            lc=self.__loadcases[casename]
            asb=Assembly(model,lc)
            asb.save(workpath,".asb")
            solver=StaticSolver(workpath,".asb")
            solver.solve_linear(casename)
            logging.info("solution finished")
            return True
        except:
            logging.warning("solution error")
            return False

    def result_get_nodal_displacement(self,case:str,node:str):
        try:
            workpath=self.__workpath
            hid=self.__model.get_node_hid(node)
            resolver=NodeResultResolver(workpath)
            res=resolver.get_nodal_displacement(case,hid)
            return res
        except:
            logging.warning("Error when resolving nodal displacement")
            return False
        