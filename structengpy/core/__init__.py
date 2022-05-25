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
        """向模型中添加三维结点

        Args:
            name (str): 结点名称
            x (float): 坐标
            y (float): 坐标
            z (float): 坐标

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.add_node(name,x,y,z)
            return True
        except:
            logging.warning("exception")
            return False

    def set_nodal_restraint(self,case:str,node:str,
            u1:bool=False,u2:bool=False,u3:bool=False,
            r1:bool=False,r2:bool=False,r3:bool=False,)->bool:
        """设置结点约束

        Args:
            case (str): 工况名
            node (str): 结点名
            u1 (bool, optional): 自由度. 默认为False.
            u2 (bool, optional): 自由度. 默认为False.
            u3 (bool, optional): 自由度. 默认为False.
            r1 (bool, optional): 自由度. 默认为False.
            r2 (bool, optional): 自由度. 默认为False.
            r3 (bool, optional): 自由度. 默认为False.

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__loadcases[case].set_nodal_restraint(node,u1,u2,u3,r1,r2,r3)
            return True
        except:
            logging.warning("exception")
            return False

    def set_nodal_mass(self,name:str,
            u1:float=0,u2:float=0,u3:float=0,
            r1:float=0,r2:float=0,r3:float=0,)->bool:
        """设置结点质量

        Args:
            name (str): 结点名
            u1 (float, optional): 自由度. 默认为0.
            u2 (float, optional): 自由度. 默认为0.
            u3 (float, optional): 自由度. 默认为0.
            r1 (float, optional): 自由度. 默认为0.
            r2 (float, optional): 自由度. 默认为0.
            r3 (float, optional): 自由度. 默认为0.

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.set_nodal_mass(name,u1,u2,u3,r1,r2,r3)
            return True
        except:
            logging.warning("exception")
            return False

    def add_beam(self,name:str,start:str,end:str,
            E:float,mu:float,
            A:float,I2:float,I3:float,J:float,rho:float)->bool:
        """向模型中添加梁

        Args:
            name (str): 梁名
            start (str): 起始点
            end (str): 终结点
            E (float): 弹性模量
            mu (float): 泊松比
            A (float): 轴压面积
            I2 (float): 2轴惯性矩
            I3 (float): 3轴惯性矩
            J (float): 抗扭惯性矩
            rho (float): 密度

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.add_beam(name,start,end,E,mu,A,I2,I3,J,rho)
            return True
        except:
            logging.warning("exception")
            return False

    def add_loadpattern(self,name:str)->bool:
        """向模型中添加荷载样式

        Args:
            name (str): 样式名

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__loadpatterns[name]=LoadPattern(name)
            return True
        except:
            logging.warning("exception")
            return False

    def set_nodal_force(self,pattern:str,node:str,
            f1:float=0,f2:float=0,f3:float=0,
            m1:float=0,m2:float=0,m3:float=0)->bool:
        """向荷载样式中添加结点荷载

        Args:
            pattern (str): 样式名
            node (str): 结点名
            f1 (float, optional): 结点力. 默认为0.
            f2 (float, optional): 结点力. 默认为0.
            f3 (float, optional): 结点力. 默认为0.
            m1 (float, optional): 结点弯矩. 默认为0.
            m2 (float, optional): 结点弯矩. 默认为0.
            m3 (float, optional): 结点弯矩. 默认为0.

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__loadpatterns[pattern].set_nodal_force(node,f1,f2,f3,m1,m2,m3)
            return True
        except:
            logging.warning("Error when setting nodal load")
            return False

    def add_beam_concentration(self)->bool:
        """_summary_

        Returns:
            bool: _description_
        """
        try:
            #TODO
            return True
        except:
            logging.warning("exception")
            return False

    def add_beam_distribution(self)->bool:
        """_summary_

        Returns:
            bool: _description_
        """
        try:
            #TODO
            return True
        except:
            logging.warning("exception")
            return False

    def add_static_case(self,name:str)->bool:
        """向模型中添加静力工况

        Args:
            name (str): 工况名

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__loadcases[name]=StaticCase(name)
            return True
        except:
            logging.warning("exception")
            return False

    def add_case_pattern(self,case:str,pattern:str,factor:float)->bool:
        """_summary_

        Args:
            case (str): 向工况中添加荷载样式和系数
            pattern (str): 样式名
            factor (float): 系数

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            lc=self.__loadcases[case]
            pat=self.__loadpatterns[pattern]
            lc.add_pattern(pat,factor)
            return True
        except:
            logging.warning("exception")
            return False

    def set_beam_release(self,name,
        u1i=False,u2i=False,u3i=False,r1i=False,r2i=False,r3i=False,
        u1j=False,u2j=False,u3j=False,r1j=False,r2j=False,r3j=False)->bool:
        """设置梁端自由度释放

        Args:
            name (_type_): 梁名
            u1i (bool, optional): 起始端自由度. 默认为False.
            u2i (bool, optional): 起始端自由度. 默认为False.
            u3i (bool, optional): 起始端自由度. 默认为False.
            r1i (bool, optional): 起始端自由度. 默认为False.
            r2i (bool, optional): 起始端自由度. 默认为False.
            r3i (bool, optional): 起始端自由度. 默认为False.
            u1j (bool, optional): 终结端自由度. 默认为False.
            u2j (bool, optional): 终结端自由度. 默认为False.
            u3j (bool, optional): 终结端自由度. 默认为False.
            r1j (bool, optional): 终结端自由度. 默认为False.
            r2j (bool, optional): 终结端自由度. 默认为False.
            r3j (bool, optional): 终结端自由度. 默认为False.

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.set_beam_releases(name,u1i,u2i,u3i,r1i,r2i,r3i,u1j,u2j,u3j,r1j,r2j,r3j)
            return True
        except:
            logging.warning("exception")
            return False

    def solve_static(self,casename:str)->bool:
        """求解静力工况

        Args:
            casename (str): 工况名

        Returns:
            bool: 成功操作返回True，反之为False
        """
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

    def result_get_nodal_displacement(self,case:str,node:str)->np.array:
        """获取结点位移结果

        Args:
            case (str): 工况名
            node (str): 结点名

        Returns:
            np.array: 成功则返回局部坐标系下的位移array，否则返回None
        """
        try:
            workpath=self.__workpath
            hid=self.__model.get_node_hid(node)
            resolver=NodeResultResolver(workpath)
            res=resolver.get_nodal_displacement(case,hid)
            return res
        except:
            logging.warning("Error when resolving nodal displacement")
            return None
        