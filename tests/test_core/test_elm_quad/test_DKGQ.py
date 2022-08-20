# -*- coding: utf-8 -*-
from pytest import approx,raises
import numpy as np

import logging
import sys
import os

from structengpy.core.fe_model.assembly import Assembly
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load.pattern import LoadPattern
from structengpy.core.fe_model.load.loadcase import StaticCase
from structengpy.core.fe_solver.static import StaticSolver

class TestDKGQ():
    def test_basic(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        N=10
        l=2
        for i in range(N+1):
            for j in range(N+1):
                model.add_node("%d-%d"%(i,j),i/N*l,j/N*l,0)
                
        model.add_isotropic_material('steel',7.849e3,2e11,0.3,1.17e-5)
        model.add_shell_section('section','steel',0.25,"shell")
        model.set_nodal_restraint("0-0",True,True,True,True,True,True)
        model.set_nodal_restraint("%d-0"%N,True,True,True,True,True,True)
        # model.set_nodal_restraint("%d-%d"%(N,N),True,True,False,True,True,True)
        model.set_nodal_restraint("0-%d"%N,True,True,True,True,True,True)

        for i in range(N):
            for j in range(N):
                model.add_shell("P%d-%d"%(i,j),'section',"%d-%d"%(i,j),"%d-%d"%(i+1,j),"%d-%d"%(i+1,j+1),"%d-%d"%(i,j+1))

        patt1=LoadPattern("pat1")
        patt1.set_nodal_load("%d-%d"%(N,N),1,0,1,0,0,0)

        lc=StaticCase("case1")
        lc.add_pattern(patt1,1.0)
        asb=Assembly(model,[lc])
        asb.save(path,"test.asb")
        solver=StaticSolver(path,"test.asb")
        solver.solve_linear("case1",use_solver='direct')
        d=np.load(os.path.join(path,"case1.d.npy")).T
        assert d[-6]==approx(2.0123e-10,rel=1e-2)
        assert d[-5]==approx(-1.0417e-10,rel=1e-2)
        assert d[-4]==approx(6.74e-9,rel=1e-2)
        assert d[-3]==approx(3.877e-9,rel=1e-2)
        assert d[-2]==approx(-3.877e-9,rel=1e-2)
        assert d[-1]==approx(-4.7921e-10,rel=1e-2)

# path="./test"
# if sys.platform=="win32":
#     path="c:\\test"

# model=Model()

# model.add_node("A",0,0,0)
# model.add_node("B",0,2,0)
# model.add_node("C",2,2,0)
# model.add_node("D",2,0,0)
# model.add_node("E",0.5,0.75,0)
# model.add_node("F",1.25,0.5,0)
# model.add_node("G",1.5,1.25,0)
# model.add_node("H",0.75,1.5,0)

        
# model.add_isotropic_material('steel',7.849e3,2e11,0.3,1.17e-5)
# model.add_shell_section('section','steel',0.25,"shell")
# model.set_nodal_restraint("A",True,True,True,True,True,True)
# model.set_nodal_restraint("B",True,True,True,True,True,True)
# model.set_nodal_restraint("D",True,True,True,True,True,True)


# model.add_shell("P1",'section',"A","B","F","E")
# model.add_shell("P2",'section',"B","C","G","F")
# model.add_shell("P3",'section',"C","D","H","G")
# model.add_shell("P4",'section',"D","A","E","H")
# model.add_shell("P5",'section',"E","F","G","H")

# patt1=LoadPattern("pat1")
# patt1.set_nodal_load("C",1,0,1,0,0,0)

# lc=StaticCase("case1")
# lc.add_pattern(patt1,1.0)
# asb=Assembly(model,[lc])
# asb.save(path,"test.asb")
# solver=StaticSolver(path,"test.asb")
# solver.solve_linear("case1",use_solver='direct')
# d=np.load(os.path.join(path,"case1.d.npy")).T
# print(d[12:18])
# # assert d[-6]==approx(2.0123e-10,rel=1e-2)
# # assert d[-5]==approx(-1.0417e-10,rel=1e-2)
# # assert d[-4]==approx(6.74e-9,rel=1e-2)
# # assert d[-3]==approx(3.877e-9,rel=1e-2)
# # assert d[-2]==approx(-3.877e-9,rel=1e-2)
# # assert d[-1]==approx(-4.7921e-10,rel=1e-2)

# path="./test"
# if sys.platform=="win32":
#     path="c:\\test"

# model=Model()

# model.add_node("A",0,0,0)
# model.add_node("B",0,2,0)
# model.add_node("C",2,2,0)
# model.add_node("D",2,0,0)
# model.add_node("E",0.5,0.75,0)
# model.add_node("F",1.25,0.5,0)
# model.add_node("G",1.5,1.25,0)
# model.add_node("H",0.75,1.5,0)

        
# model.add_isotropic_material('steel',7.849e3,2e11,0.3,1.17e-5)
# model.add_shell_section('section','steel',0.25,"shell")
# model.set_nodal_restraint("A",True,True,True,True,True,True)
# model.set_nodal_restraint("B",True,True,True,True,True,True)
# model.set_nodal_restraint("D",True,True,True,True,True,True)


# model.add_shell("P1",'section',"A","B","F","E")
# model.add_shell("P2",'section',"B","C","G","F")
# model.add_shell("P3",'section',"C","D","H","G")
# model.add_shell("P4",'section',"D","A","E","H")
# model.add_shell("P5",'section',"E","F","G","H")

# patt1=LoadPattern("pat1")
# patt1.set_nodal_load("C",1,0,1,0,0,0)

# lc=StaticCase("case1")
# lc.add_pattern(patt1,1.0)
# asb=Assembly(model,[lc])
# asb.save(path,"test.asb")
# solver=StaticSolver(path,"test.asb")
# solver.solve_linear("case1",use_solver='direct')
# d=np.load(os.path.join(path,"case1.d.npy")).T
# print(d[12:18])
# # assert d[-6]==approx(2.0123e-10,rel=1e-2)
# # assert d[-5]==approx(-1.0417e-10,rel=1e-2)
# # assert d[-4]==approx(6.74e-9,rel=1e-2)
# # assert d[-3]==approx(3.877e-9,rel=1e-2)
# # assert d[-2]==approx(-3.877e-9,rel=1e-2)
# # assert d[-1]==approx(-4.7921e-10,rel=1e-2)

# path="./test"
# if sys.platform=="win32":
#     path="c:\\test"

# model=Model()
# N=2
# l=2
# for i in range(N+1):
#     for j in range(N+1):
#         model.add_node("%d-%d"%(i,j),i/N*l,j/N*l,0)
        
# model.add_isotropic_material('steel',7.849e3,2e11,0.3,1.17e-5)
# model.add_shell_section('section','steel',0.25,"shell")
# model.set_nodal_restraint("0-0",True,True,True,True,True,True)
# model.set_nodal_restraint("%d-0"%N,True,True,True,True,True,True)
# # model.set_nodal_restraint("%d-%d"%(N,N),True,True,False,True,True,True)
# model.set_nodal_restraint("0-%d"%N,True,True,True,True,True,True)

# for i in range(N):
#     for j in range(N):
#         model.add_shell("P%d-%d"%(i,j),'section',"%d-%d"%(i,j),"%d-%d"%(i+1,j),"%d-%d"%(i+1,j+1),"%d-%d"%(i,j+1))

# patt1=LoadPattern("pat1")
# patt1.set_nodal_load("%d-%d"%(N,N),1,0,1,0,0,0)

# lc=StaticCase("case1")
# lc.add_pattern(patt1,1.0)
# asb=Assembly(model,[lc])
# asb.save(path,"test.asb")
# solver=StaticSolver(path,"test.asb")
# solver.solve_linear("case1",use_solver='direct')
# d=np.load(os.path.join(path,"case1.d.npy")).T
# print(d[-6:])

# path="./test"
# if sys.platform=="win32":
#     path="c:\\test"

# model=Model()

# model.add_node("A",0,0,0)
# model.add_node("B",0,2,0)
# model.add_node("C",2,2,0)
# model.add_node("D",2,0,0)
# model.add_node("E",0.667,0,0)
# model.add_node("F",2,0.5,0)
# model.add_node("G",1.333,2,0)
# model.add_node("H",0,1,0)
# model.add_node("O",1.5,1,0)
        
# model.add_isotropic_material('steel',7.849e3,2e11,0.3,1.17e-5)
# model.add_shell_section('section','steel',0.25,"shell")
# model.set_nodal_restraint("A",True,True,True,True,True,True)
# model.set_nodal_restraint("B",True,True,True,True,True,True)
# model.set_nodal_restraint("D",True,True,True,True,True,True)

# model.add_shell("P1",'section',"A","E","O","H")
# model.add_shell("P2",'section',"E","B","F","O")
# model.add_shell("P3",'section',"F","C","G","O")
# model.add_shell("P4",'section',"O","G","D","H")

# patt1=LoadPattern("pat1")
# patt1.set_nodal_load("C",1,0,1,0,0,0)

# lc=StaticCase("case1")
# lc.add_pattern(patt1,1.0)
# asb=Assembly(model,[lc])
# asb.save(path,"test.asb")
# solver=StaticSolver(path,"test.asb")
# solver.solve_linear("case1",use_solver='direct')
# d=np.load(os.path.join(path,"case1.d.npy")).T
# print(d[12:18])
# # assert d[-6]==approx(2.0123e-10,rel=1e-2)
# # assert d[-5]==approx(-1.0417e-10,rel=1e-2)
# # assert d[-4]==approx(6.74e-9,rel=1e-2)
# # assert d[-3]==approx(3.877e-9,rel=1e-2)
# # assert d[-2]==approx(-3.877e-9,rel=1e-2)
# # assert d[-1]==approx(-4.7921e-10,rel=1e-2)

# path="./test"
# if sys.platform=="win32":
#     path="c:\\test"

# model=Model()
# N=2
# l=2
# for i in range(N+1):
#     for j in range(N+1):
#         model.add_node("%d-%d"%(i,j),i/N*l,j/N*l,0)
        
# model.add_isotropic_material('steel',7.849e3,2e11,0.3,1.17e-5)
# model.add_shell_section('section','steel',0.25,"shell")
# model.set_nodal_restraint("0-0",True,True,True,True,True,True)
# model.set_nodal_restraint("%d-0"%N,True,True,True,True,True,True)
# # model.set_nodal_restraint("%d-%d"%(N,N),True,True,False,True,True,True)
# model.set_nodal_restraint("0-%d"%N,True,True,True,True,True,True)

# for i in range(N):
#     for j in range(N):
#         model.add_shell("P%d-%d"%(i,j),'section',"%d-%d"%(i,j),"%d-%d"%(i+1,j),"%d-%d"%(i+1,j+1),"%d-%d"%(i,j+1))

# patt1=LoadPattern("pat1")
# patt1.set_nodal_load("%d-%d"%(N,N),1,0,1,0,0,0)

# lc=StaticCase("case1")
# lc.add_pattern(patt1,1.0)
# asb=Assembly(model,[lc])
# asb.save(path,"test.asb")
# solver=StaticSolver(path,"test.asb")
# solver.solve_linear("case1",use_solver='direct')
# d=np.load(os.path.join(path,"case1.d.npy")).T
# print(d[-6:])



