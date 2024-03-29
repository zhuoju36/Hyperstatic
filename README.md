# Hyperstatic：开放自由的工程结构分析框架

![GitHub](https://img.shields.io/github/license/zhuoju36/hyperstatic) [![codecov](https://codecov.io/gh/zhuoju36/Hyperstatic/branch/master/graph/badge.svg?token=4C6a6QwvKA)](https://codecov.io/gh/zhuoju36/Hyperstatic) ![PyPI](https://img.shields.io/pypi/v/hyperstatic) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hyperstatic)
[![Documentation Status](https://readthedocs.org/projects/hyperstatic/badge/?version=latest)](https://hyperstatic.readthedocs.io/zh_CN/latest/?badge=latest)
## 简介
基于Python语言，采用面向对象方式开发，针对建筑领域特点开发的结构分析框架，提供完全开放的基础结构数值分析，可供高校师生、研究院所参考，也可自由用于相关结构工程设计。

## 当前版本支持功能（v0.2）

- 各向同性单轴材料
- 考虑剪切的梁单元
- 三角形、四边形薄壳，支持平板及薄膜刚度
- 线性静力分析，支持多种稀疏矩阵求解器
- 自振模态分析
- 直接积分法时程分析
- 后处理
- 分析结果的可视化

## 快速开始
### 安装
```bash
pip install -U hyperstatic
```

### Core API使用

10m悬臂梁，A端固定，B端施加10kN竖直向下荷载

```python
# -*- coding: utf-8 -*-

# 导入包
import sys
from hyperstatic.core import Api

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
```

## 留言讨论
- [github](https://github.com/zhuoju36)
