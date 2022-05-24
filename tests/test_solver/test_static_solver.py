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
        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

        patt1=LoadPattern("pat1")
        patt1.set_nodal_force("2",0,0,-1e4,0,0,0)
        # patt1.set_nodal_disp("1",0,0,0,0,0,0)

        lc=StaticCase("case1")
        lc.add_pattern(patt1,1.0)
        lc.set_nodal_restraint("1",True,True,True,True,True,True)
        
        asb=Assembly(model,lc)

        path="./test"
        if sys.platform=="win32":
            path="c:\\test"
        asb.save(path,"test.sep")

        solver=StaticSolver(path,"test.sep")
        solver.solve_linear("case1")
        d=np.load(os.path.join(path,"case1.d.npy")).reshape(12)
        assert d[8]==approx(-0.00764,rel=5e-2)
        assert d[10]==approx(0.00189,rel=5e-2)
        
