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

class TestDKT():
    def test_DKT(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        N=10
        l=2
        for i in range(N+1):
            for j in range(N+1):
                model.add_node("%d-%d"%(i,j),i/N*l,j/N*l,0)
                model.set_nodal_restraint("%d-%d"%(i,j),r3=True)
                
        model.add_isotropic_material('steel',7.849e3,2e11,0.3,1.17e-5)
        model.add_shell_section('section','steel',0.25,"shell")
        model.set_nodal_restraint("0-0",True,True,True,True,True,True)
        model.set_nodal_restraint("%d-0"%N,True,True,True,True,True,True)
        # model.set_nodal_restraint("%d-%d"%(N,N),True,True,False,True,True,True)
        model.set_nodal_restraint("0-%d"%N,True,True,True,True,True,True)

        for i in range(N):
            for j in range(N):
                model.add_shell("S%d-%d-A"%(i,j),'section',"%d-%d"%(i,j),"%d-%d"%(i+1,j),"%d-%d"%(i+1,j+1))
                model.add_shell("S%d-%d-B"%(i,j),'section',"%d-%d"%(i+1,j+1),"%d-%d"%(i,j+1),"%d-%d"%(i,j))

        patt1=LoadPattern("pat1")
        patt1.set_nodal_load("%d-%d"%(N,N),1,0,1,0,0,0)

        lc=StaticCase("case1")
        lc.add_pattern(patt1,1.0)
        asb=Assembly(model,[lc])
        asb.save(path,"test.asb")
        solver=StaticSolver(path,"test.asb")
        solver.solve_linear("case1")
        d=np.load(os.path.join(path,"case1.d.npy")).T

        assert d[-6]==approx(1.753e-10,rel=1e-2)
        assert d[-5]==approx(-8.45e-11,rel=1e-2)
        assert d[-4]==approx(5.92e-9,rel=1e-2)
        assert d[-3]==approx(3.595e-9,rel=1e-2)
        assert d[-2]==approx(-3.595e-9,rel=1e-2)
        assert d[-1]==approx(0,rel=1e-2)