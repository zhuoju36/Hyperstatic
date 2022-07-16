# -*- coding: utf-8 -*-

# 导入包
import sys
from structengpy.core import Api

# 工作路径
path="./wkdir"
if sys.platform=="win32":
    path="c:\\wkdir"

# 初始化API
api=Api(path)

# 定义结点
api.add_node("A",0,0,0)
api.add_node("B",10,0,0)

# 定义单元
api.add_simple_beam("b","A","B",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

# 定义荷载样式
api.add_loadpattern("pat1")

# 指定结点荷载到样式
api.set_nodal_force("pat1","B",f3=-1e4)

# 定义静力荷载工况
api.add_static_case("case1")

# 向工况添加荷载样式及乘数
api.add_case_pattern("case1","pat1",1.0)

# 向工况添加结点约束
api.set_loadcase_nodal_restraint("case1","A",True,True,True,True,True,True)

# 集成求解数据
api.assemble()

# 求解静力工况
api.solve_static("case1")

# 解析位移结果
d=api.result_get_nodal_displacement("B","case1")
print("Deflection at node B is %4.6f m"%d[2])