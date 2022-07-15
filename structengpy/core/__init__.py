# -*- coding: utf-8 -*-
from copyreg import pickle
from datetime import datetime, timedelta
import os
import logging
from typing import Dict
import numpy as np
import pickle

from typing import Pattern
from structengpy.core.fe_model.assembly import Assembly
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load.pattern import LoadPattern
from structengpy.core.fe_model.load import LoadCase
from structengpy.core.fe_model.load.loadcase import ModalCase, StaticCase
from structengpy.core.fe_post.beam import BeamResultResolver
from structengpy.core.fe_solver.dynamic import ModalSolver
from structengpy.core.fe_solver.static import StaticSolver
from structengpy.common.csys import Cartesian
from structengpy.core.fe_post.node import NodeResultResolver


class Api(object):
    def __init__(self,workpath:str):
        self.__filename=".asb"
        self.__csys=Cartesian((0,0,0),(1,0,0),(0,1,0),"Global")
        self.__model=Model()
        self.__loadcases:Dict[str,LoadCase]={}
        self.__loadpatterns:Dict[str,LoadPattern]={}
        # self.__nodal_restraint:Dict[str,np.ndarray]={}
        self.__workpath=workpath
        if not os.path.exists(workpath):
            try:
                os.mkdir(workpath)
            except Exception as e :
                logging.info("Error creating workpath "+ workpath +'. Exception: '+str(e))
                self=None
    

    def save(self,filename):
        with open(os.path.join(self.__workpath,filename+'.sep'),'wb+') as f:
            pickle.dump(self,f)
        

    @staticmethod
    def load(workpath,filename):
        with open(os.path.join(workpath,filename+'.sep'),'rb') as f:
            api=pickle.load(f)
        return api

    def clear_workspace(self):
        workpath=self.__workpath
        if not os.path.exists(workpath):
            logging.info("Work path"+ workpath+" does not exist!")
        else:
            try:
                os.remove(workpath)
                os.mkdir(workpath)
            except Exception as e :
                logging.info("Error creating workpath "+ workpath +'. Exception: '+str(e))
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
        except Exception as e:
            logging.warning(str(e)+" when adding node")
            return False

    def get_node_names(self)->list:
        try:
            return self.__model.nodes.keys()
        except Exception as e:
            logging.warning("Error when getting node names. Exception: "+str(e))
            return None

    def get_node_location(self,name:str)->tuple:
        try:
            return self.__model.nodes[name].loc
        except Exception as e:
            logging.warning("Error when getting node location of %s"%name+" Exception: "+str(e))
            return None

    def get_node_restraints(self,casename)->dict:
        try:
            return self.__loadcases[casename].get_nodal_restraint_dict()
        except Exception as e:
            logging.warning("Error when getting node restraints of loadcase%s"%casename+" Exception: "+str(e))
            return None

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
        except Exception as e:
            logging.warning(str(e)+" when setting nodal mass")
            return False

    def add_isotropy_material(self,name:str,E:float,mu:float,a:float)->bool:
        """向模型中添加各向同性材料

        Args:
            name (str): 材料名
            E (float): 弹性模量
            mu (float): 泊松比
            a (float): 热膨胀系数

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.add_isotropy_material(name,E,mu,a)
            return True
        except Exception as e:
            logging.warning(str(e)+" when adding isotropy material")
            return False

    def add_beam_section_general(self,name:str,material:str,A:float,As2:float,As3:float,I22:float,I33:float,J:float,W22:float,W33:float)->bool:
        """向模型中添加一般截面

        Args:
            name (str): 截面名
            material (str): 材料名
            A (float): 截面积
            As2 (float): 2轴抗剪面积
            As3 (float): 3轴抗剪面积
            I22 (float): 绕2轴主惯性矩
            I33 (float): 绕3轴主惯性矩
            J (float): 扭转常数
            W22 (float): 绕2轴抗弯模量
            W33 (float): 绕3轴抗弯模量

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.add_simple_beam_section_general(name,material,A,As2,As3,I22,I33,J,W22,W33)
            return True
        except Exception as e:
            logging.warning(str(e)+" when adding general beam section")
            return False

    def add_beam_section_rectangle(self,name:str,material:str,h:float,b:float)->bool:
        """向模型中添加矩形截面

        Args:
            name (str): 截面名
            material (str): 材料名
            h (float): 高
            b (float): 宽

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.add_simple_beam_section_rectangle(name,material,h,b)
            return True
        except Exception as e:
            logging.warning(str(e)+" when adding rectangle beam section")
            return False

    def add_beam_section_I(self,name:str,material:str,h:float,b:float,tw:float,tf:float)->bool:
        """向模型中添加工字形截面

        Args:
            name (str): 截面名
            material (str): 材料名
            h (float): 高
            b (float): 宽
            tw (float): 腹板厚
            tf (float): 翼缘厚

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.add_simple_beam_section_rectangle(name,material,h,b,tw,tf)
            return True
        except Exception as e:
            logging.warning(str(e)+" when adding I-section")
            return False

    def add_beam_section_box(self,name:str,material:str,h:float,b:float,tw:float,tf:float)->bool:
        """向模型中添加箱型截面

        Args:
            name (str): 截面名
            material (str): 材料名
            h (float): 高
            b (float): 宽
            tw (float): 腹板厚
            tf (float): 翼缘厚

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.add_simple_beam_section_rectangle(name,material,h,b,tw,tf)
            return True
        except Exception as e:
            logging.warning(str(e)+" when adding box section")
            return False

    def add_beam_section_circle(self,name:str,material:str,d:float)->bool:
        """向模型中添加圆截面

        Args:
            name (str): 截面名
            material (str): 材料名
            d (float): 直径

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.add_simple_beam_section_rectangle(name,material,d)
            return True
        except Exception as e:
            logging.warning(str(e)+" when adding circle beam section")
            return False

    def add_beam_section_pipe(self,name:str,material:str,d:float,t:float)->bool:
        """向模型中添加圆管截面

        Args:
            name (str): 截面名
            material (str): 材料名
            d (float): 直径
            t (float): 壁厚

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.add_simple_beam_section_rectangle(name,material,d,t)
            return True
        except Exception as e:
            logging.warning(str(e)+" when adding pipe beam section")
            return False

    def add_beam(self,name:str,start:str,end:str,section:str)->bool:
        """向模型中添加梁

        Args:
            name (str): 梁名
            start (str): 起始点
            end (str): 终结点
            section (str): 截面名

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__model.add_simple_beam(name,start,end,section)
            return True
        except Exception as e:
            logging.warning(str(e)+" when adding beam")
            return False

    def add_simple_beam(self,name:str,start:str,end:str,
            E:float,mu:float,
            A:float,I2:float,I3:float,J:float,rho:float)->bool:
        """向模型中添加简单梁

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
            self.__model.add_simple_beam(name,start,end,E,mu,A,I2,I3,J,rho)
            return True
        except Exception as e:
            logging.warning(str(e)+" when adding beam")
            return False

    def get_beam_names(self)->list:
        """获取梁名

        Returns:
            list: 梁名列表
        """
        try:
            return self.__model.beams.keys()
        except Exception as e:
            logging.warning("Error when getting beam names. Exception: "+str(e))
            return None

    def get_beam_node_names(self,beam_name:str)->tuple:
        """获取梁结点名

        Args:
            beam_name (str): 梁名

        Returns:
            tuple: 梁结点名
        """
        try:
            return tuple(self.__model.beams[beam_name].get_node_names())
        except Exception as e:
            logging.warning("Error when getting beam node names. Exception: "+str(e))
            return None

    def get_beam_location(self,beam_name:str)->tuple:
        """获取梁位置

        Args:
            beam_name (str): 梁名

        Returns:
            tuple: 梁端三维位置
        """
        try:
            return tuple(self.__model.beams[beam_name].start),tuple(self.__model.beams[beam_name].end)
        except Exception as e:
            logging.warning("Error when getting beam node names. Exception: "+str(e))
            return None

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
        except Exception as e:
            logging.warning(str(e)+" when settring beam releases")
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
        except Exception as e:
            logging.warning(str(e)+" when adding load pattern")
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
        except Exception as e:
            logging.warning(str(e)+" when setting nodal restraints")
            return False

    def set_nodal_load(self,pattern:str,node:str,
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
            self.__loadpatterns[pattern].set_nodal_load(node,f1,f2,f3,m1,m2,m3)
            return True
        except Exception as e:
            logging.warning(str(e)+" when setting nodal load")
            return False

    def get_nodal_load(self,pattern:str,node:str)->list:
        """获取荷载样式中的结点荷载

        Args:
            pattern (str): 样式名
            node (str): 结点名

        Returns:
            f1 (float): 结点力. 
            f2 (float): 结点力. 
            f3 (float): 结点力. 
            m1 (float): 结点弯矩. 
            m2 (float): 结点弯矩. 
            m3 (float): 结点弯矩. 
        """
        try:
            return tuple(self.__loadpatterns[pattern].get_nodal_f(node))
        except Exception as e:
            logging.warning(str(e)+" when setting nodal load")
            return None

    def get_all_nodal_load(self,pattern:str)->dict:
        """获取荷载样式中的结点荷载

        Args:
            pattern (str): 样式名
            node (str): 结点名

        Returns:
            load (dict): 包含六个结点荷载荷载的字典.
        """
        try:
            return self.__loadpatterns[pattern].get_nodal_f_dict()
        except Exception as e:
            logging.warning(str(e)+" when setting nodal load")
            return None

    def set_beam_load_distributed(self,pattern:str,beam:str,
        pi:float=0,pj:float=0,qi2:float=0,qj2:float=0,qi3:float=0,qj3:float=0,ti:float=0,tj:float=0)->bool:
        """向荷载样式中添加梁分布荷载

        Args:
            pattern (str): 样式名
            beam (str): 单元名
            pi (float, optional): 起始端轴向力分布值. 默认为0.
            pj (float, optional): 终结端轴向力分布值. 默认为0.
            qi2 (float, optional): 起始端2方向侧向力分布值. 默认为0.
            qj2 (float, optional): 终结端2方向侧向力分布值. 默认为0.
            qi3 (float, optional): 起始端3方向侧向力分布值. 默认为0.
            qj3 (float, optional): 终结端3方向侧向力分布值. 默认为0.
            ti (float, optional): 起始端扭矩分布值. 默认为0.
            tj (float, optional): 终结端扭矩分布值. 默认为0.

        Returns:
            bool: _description_
        """
        try:
            self.__loadpatterns[pattern].set_beam_load_dist(beam,pi,pj,qi2,qj2,qi3,qj3,ti,tj)
            return True
        except Exception as e:
            logging.warning(str(e)+" when setting beam distributed load")
            return False

    def set_beam_load_concentrated(self,pattern:str,beam:str,
        F1:float=0,F2:float=0,F3:float=0,M1:float=0,M2:float=0,M3:float=0,r:float=0.5)->bool:
        """向荷载样式中添加梁集中荷载

        Args:
            pattern (str): 样式名
            beam (str): 单元名
            F1 (float, optional): 1向集中力. 默认为0.
            F2 (float, optional): 2向集中力. 默认为0.
            F3 (float, optional): 3向集中力. 默认为0.
            M1 (float, optional): 1向集中力矩. 默认为0.
            M2 (float, optional): 2向集中力矩. 默认为0.
            M3 (float, optional): 3向集中力矩. 默认为0.
            r (float, optional): 梁上相对位置. 默认为0.5.

        Returns:
            bool: _description_
        """
        try:
            self.__loadpatterns[pattern].set_beam_load_conc(beam,F1,F2,F3,M1,M2,M3,r)
            return True
        except Exception as e:
            logging.warning(str(e)+" when setting beam concentrated load")
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
        except Exception as e:
            logging.warning(str(e)+" when adding static case")
            return False

    def add_modal_case(self,name:str)->bool:
        """向模型中添加模态工况

        Args:
            name (str): 工况名
            isRitz (bool): 计算Ritz模态

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            self.__loadcases[name]=ModalCase(name)
            return True
        except Exception as e:
            logging.warning(str(e)+" when adding modal case")
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
        except Exception as e:
            logging.warning(str(e)+" when adding load pattern to static case")
            return False

    def assemble(self)->bool:
        """集成分析数据

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            workpath=self.__workpath
            model=self.__model
            lc=self.__loadcases.values()
            asb=Assembly(model,lc)
            asb.save(workpath,self.__filename)
            return True
        except Exception as e:
            logging.warning("Error when assembling model and cases. Exception: "+str(e))
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
            solver=StaticSolver(workpath,self.__filename)
            start=datetime.now()
            logging.info("Solution for loadcase %s starts."%casename)
            solver.solve_linear(casename)
            timecost=datetime.now()-start
            logging.info("Solution for loadcase %s is finished. Time cost: %d.%d s"%(casename,timecost.seconds,timecost.microseconds//1000))
            return True
        except Exception as e:
            logging.warning("Error when solving case "+str(casename)+". Exception: "+str(e))
            return False

    def solve_modal(self,casename:str,num:int)->bool:
        """求解模态工况

        Args:
            casename (str): 工况名
            num (int): 提取模态数

        Returns:
            bool: 成功操作返回True，反之为False
        """
        try:
            workpath=self.__workpath
            solver=ModalSolver(workpath,self.__filename)
            solver.solve_eigen(casename,num)
            logging.info("solution finished")
            return True
        except Exception as e:
            logging.warning("Error when solving case "+str(casename)+". Exception: "+str(e))
            return False

    def result_get_structural_reaction(self,case:str)->np.array:
        try:
            workpath=self.__workpath

            pass

        except Exception as e:
            logging.warning("Error when getting structural reaction of "+str(case)+". Exception: "+str(e))
            return False

    def result_get_structural_period(self,case:str)->np.array:
        try:
            workpath=self.__workpath

            pass
        
        except Exception as e:
            logging.warning("Error when getting structural period of "+str(case)+". Exception: "+str(e))
            return False

    def result_get_structural_vibration_mode(self,case:str)->np.array:
        try:
            workpath=self.__workpath

            pass
        
        except Exception as e:
            logging.warning("Error when getting structural vibration mode of "+str(case)+". Exception: "+str(e))
            return False

    def result_get_nodal_reaction(self,node:str,case:str)->np.array:
        """获取结点反力结果

        Args:
            node (str): 结点名
            case (str): 工况名

        Returns:
            np.array: 成功则返回局部坐标系下的反力array，否则返回None
        """
        try:
            workpath=self.__workpath
            resolver=NodeResultResolver(workpath)
            res=resolver.resolve_nodal_reaction(node,case,step=1)
            return res
        except Exception as e:
            logging.warning("Error when getting nodal reaction of "+str(case)+". Exception: "+str(e))
            return None

    def result_get_nodal_displacement(self,node:str,case:str)->np.array:
        """获取结点位移结果

        Args:
            node (str): 结点名
            case (str): 工况名

        Returns:
            np.array: 成功则返回局部坐标系下的位移array，否则返回None
        """
        try:
            workpath=self.__workpath
            resolver=NodeResultResolver(workpath,self.__filename)
            res=resolver.resolve_nodal_displacement(node,case,step=1)
            return res
        except Exception as e:
            logging.warning(str(e)+" when getting nodal displacement of "+str(case))
            return None

    def result_get_all_nodal_displacement(self,case:str)->dict:
        """一次获取所有结点位移结果

        Args:
            case (str): 工况名

        Returns:
            dict: 成功则返回局部坐标系下的位移array字典，否则返回None
        """
        try:
            workpath=self.__workpath
            resolver=NodeResultResolver(workpath,self.__filename)
            res={}
            for node in self.get_node_names():
                res[node]=resolver.resolve_nodal_displacement(node,case,step=1)
            return res
        except Exception as e:
            logging.warning(str(e)+" when getting nodal displacement of "+str(case))
            return None

    def result_get_beam_end_force(self,beam:str,case:str)->np.array:
        """获取梁端力结果

        Args:
            beam (str): 梁名
            case (str): 工况名

        Returns:
            np.array: 成功则返回局部坐标系下的梁端力array，否则返回None
        """
        try:
            workpath=self.__workpath
            resolver=BeamResultResolver(workpath,self.__filename)
            res=resolver.resolve_beam_end_force(beam,case,step=1)
            return res 
        except Exception as e:
            logging.warning("Error when getting beam stress of "+str(case)+". Exception: "+str(e))
            return None

    def result_get_beam_deformation(self,beam:str,loc:float,case:str)->np.array:
        """获取梁位移结果

        Args:
            beam (str): 梁名
            loc (float): 相对位置，0~1之间
            case (str): 工况名

        Returns:
            np.array: 成功则返回局部坐标系下的包含6个梁位移的array，否则返回None
        """
        try:
            workpath=self.__workpath
            resolver=BeamResultResolver(workpath,self.__filename)
            res=resolver.resolve_beam_deformation(beam,loc,case,step=1)
            return res 
        except Exception as e:
            logging.warning("Error when getting beam deformation of "+str(case)+". Exception: "+str(e))
            return None

    # def result_get_beam_force(self,beam:str,loc:float,case:str)->np.array:
    #     try:
    #         workpath=self.__workpath
    #         hid=self.__model.get_beam_hid(beam)

    #         pass

        
    #     except Exception as e:
    #         logging.warning("Error when getting beam stress of "+str(case)+". Exception: "+str(e))
    #         return False

    # def result_get_beam_stress(self,beam:str,loc:float,case:str)->np.array:
    #     try:
    #         workpath=self.__workpath
    #         hid=self.__model.get_beam_hid(beam)

    #         pass

        
        # except Exception as e:
        #     logging.warning("Error when getting beam stress of "+str(case)+". Exception: "+str(e))
        #     return False
        