# -*- coding: utf-8 -*-
import pytest
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

class TestStaticSolver():
    def test_case(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

        patt1=LoadPattern("pat1")
        patt1.set_nodal_load("2",0,0,-1e4,0,0,0)
        # patt1.set_nodal_disp("1",0,0,0,0,0,0)

        lc=StaticCase("case1")
        lc.add_pattern(patt1,1.0)
        lc.set_nodal_restraint("1",True,True,True,True,True,True)
        asb=Assembly(model,[lc])
        asb.save(path,"test.asb")
        solver=StaticSolver(path,"test.asb")
        solver.solve_linear("case1")
        d=np.load(os.path.join(path,"case1.d.npy")).reshape(12)
        assert d[8]==approx(-0.00764,rel=5e-2)
        assert d[10]==approx(0.00189,rel=5e-2)

        patt1=LoadPattern("pat1")
        patt1.set_nodal_load("2",0,1e4,0,0,0,0)
        lc=StaticCase("case1")
        lc.add_pattern(patt1,1.0)
        lc.set_nodal_restraint("1",True,True,True,True,True,True)
        asb=Assembly(model,[lc])
        asb.save(path,"test.asb")
        solver=StaticSolver(path,"test.asb")
        solver.solve_linear("case1")
        d=np.load(os.path.join(path,"case1.d.npy")).reshape(12)
        assert d[7]==approx(0.0896,rel=5e-2)

    def test_cantilever_beam(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.0226667e-5,I3=4.771e-4,J=4.132867e-6,rho=7.85e10) #H400x200x20x30
        
        inp=[
            (1e4,1e4,0,0,0,0,0,0), #uniform axial
            (1e6,    0,0,0,0,0,0), #triangulte axial
            (1e5,2e5,0,0,0,0,0,0), #trapzoid axial
            (0,0,-1e4,-1e4,0,0,0,0), #uniform bending 2
            (0,0,-1e4,0,0,0,0,0), #triangulate bending 2
            (0,0,-1e4,-2e4,0,0,0,0), #trapzoid bending 2
            (0,0,0,0,1e4,1e4,0,0), #uniform bending 3
            (0,0,0,0,1e4,0,0,0), #triangulate bending 3
            (0,0,0,0,1e4,2e4,0,0), #trapzoid bending 3
            (0,0,0,0,0,0,1e4,1e4), #uniform torsion
            (0,0,0,0,0,0,1e4,0), #triangulate torsion
            (0,0,0,0,0,0,1e4,2e4), #trapzoid torsion
        ]
        oup=[
            (6,4.787e-5), #DOF,displacement
            (6,0.0015957),
            (6,0.0007979),
            (8,-0.0173),
            (8,-0.0046),
            (8,-0.0294),
            (7,-0.2016),
            (7,-0.0538),
            (7,-0.349),
            (9,0.56619),
            (9,0.18873),
            (9,0.94365)
        ]
        for i,o in zip(inp,oup):
            #uniform load axial
            patt1=LoadPattern("pat1")
            patt1.set_beam_load_dist("A",*i)
            lc=StaticCase("case1")
            lc.add_pattern(patt1,1.0)
            lc.set_nodal_restraint("1",True,True,True,True,True,True)
            asb=Assembly(model,[lc])
            asb.save(path,"test.asb")
            solver=StaticSolver(path,"test.asb")
            solver.solve_linear("case1")
            d=np.load(os.path.join(path,"case1.d.npy")).reshape(12)
            assert d[o[0]]==approx(o[1],rel=5e-2)

    def test_cantilever_brace(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,6,3)
        model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.0226667e-5,I3=4.771e-4,J=4.132867e-6,rho=7.85e10)
        
        inp=[
            (0,0,1e4,2e4,1e4,1e4,0,0),
            (0,0,1e4,2e4,1e4,1e4,0,0),
        ]
        oup=[
            (7,-0.7208),
            (6,0.6857),
        ]
        for i,o in zip(inp,oup):
            #uniform load axial
            patt1=LoadPattern("pat1")
            patt1.set_beam_load_dist("A",*i)
            lc=StaticCase("case1")
            lc.add_pattern(patt1,1.0)
            lc.set_nodal_restraint("1",True,True,True,True,True,True)
            asb=Assembly(model,[lc])
            asb.save(path,"test.asb")
            solver=StaticSolver(path,"test.asb")
            solver.solve_linear("case1")
            d=np.load(os.path.join(path,"case1.d.npy")).reshape(12)
            assert d[o[0]]==approx(o[1],rel=5e-2)

    def test_simply_supported_beam(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_node("3",12,0,0)
        model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)
        model.add_beam("B","2","3",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

        inp=[
            (1e4,1e4,0,0,0,0,0,0), #uniform axial
            (1e5,2e5,0,0,0,0,0,0), #trapzoid axial
            (0,0,-1e4,-1e4,0,0,0,0), #uniform bending 2
            (0,0,1e4,2e4,0,0,0,0), #trapzoid bending 2
            (0,0,0,0,1e4,1e4,0,0), #uniform bending 3
            (0,0,0,0,1e4,2e4,0,0), #trapzoid bending 3
            (0,0,0,0,0,0,1e4,1e4), #uniform torsion
            (0,0,0,0,0,0,1e4,2e4), #trapzoid torsion
        ]
        oup=[
            (6,4.787e-5), #DOF,displacement
            (6,0.0007181),
            (8,-0.0283),
            (8,0.0424),
            (7,-0.3356),
            (7,-0.5034),
            (9,0.56619),
            (9,0.84929)
        ]
        for i,o in zip(inp,oup):
            #uniform load axial
            patt1=LoadPattern("pat1")
            patt1.set_beam_load_dist("A",*i)
            patt1.set_beam_load_dist("B",*i)

            lc=StaticCase("case1")
            lc.add_pattern(patt1,1.0)
            lc.set_nodal_restraint("1",True,True,True,True)
            lc.set_nodal_restraint("3",True,True,True,True)
            asb=Assembly(model,[lc])
            asb.save(path,"test.asb")
            solver=StaticSolver(path,"test.asb")
            solver.solve_linear("case1")
            d=np.load(os.path.join(path,"case1.d.npy")).reshape(18)
            assert d[o[0]]==approx(o[1],rel=5e-2)

    def test_simply_supported_beam_concentrated(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_node("3",12,0,0)
        model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)
        model.add_beam("B","2","3",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

        inp=[
            (1e6,0,0,0,0,0,0.75), #P
            (0,1e4,0,0,0,0,0.75), #V2
            (0,0,1e4,0,0,0,0.75), #V3
            (0,0,0,1e4,0,0,0.75), #T
            (0,0,0,0,1e4,0,0.75), #M2
            (0,0,0,0,0,1e4,0.75), #M3
        ]
        oup=[
            (6,5.984e-4),
            (8,0.0034),
            (7,-0.0409),
            (9,0.07077),
            (7,0.0049),
            (8,4.126e-4),
        ]
        for i,o in zip(inp,oup):
            #uniform load axial
            patt1=LoadPattern("pat1")
            patt1.set_beam_load_conc("A",*i)
            lc=StaticCase("case1")
            lc.add_pattern(patt1,1.0)
            lc.set_nodal_restraint("1",True,True,True,True)
            lc.set_nodal_restraint("3",True,True,True,True)
            asb=Assembly(model,[lc])
            asb.save(path,"test.asb")
            solver=StaticSolver(path,"test.asb")
            solver.solve_linear("case1")
            d=np.load(os.path.join(path,"case1.d.npy")).reshape(18)
            assert d[o[0]]==approx(o[1],rel=5e-2)

    def test_cantilever_beam_concentrated(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

        inp=[
            (1e6,0,0,0,0,0,0.75), #P
            (0,1e4,0,0,0,0,0.75), #V2
            (0,0,1e4,0,0,0,0.75), #V3
            (0,0,0,1e4,0,0,0.75), #T
            (0,0,0,0,1e4,0,0.75), #M2
            (0,0,0,0,0,1e4,0.75), #M3
        ]
        oup=[
            (6,0.0012),
            (8,0.0048),
            (7,-0.0566),
            (9,0.14155),
            (7,0.021),
            (8,0.0018),
        ]
        for i,o in zip(inp,oup):
            #uniform load axial
            patt1=LoadPattern("pat1")
            patt1.set_beam_load_conc("A",*i)
            lc=StaticCase("case1")
            lc.add_pattern(patt1,1.0)
            lc.set_nodal_restraint("1",True,True,True,True,True,True)
            asb=Assembly(model,[lc])
            asb.save(path,"test.asb")
            solver=StaticSolver(path,"test.asb")
            solver.solve_linear("case1")
            d=np.load(os.path.join(path,"case1.d.npy")).reshape(12)
            assert d[o[0]]==approx(o[1],rel=5e-2)