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
    def test_T9(self):
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
        # model.set_nodal_restraint("%d-%d"%(N,N),True,True,True,True,True,True)
        model.set_nodal_restraint("0-%d"%N,True,True,True,True,True,True)

        for i in range(N):
            for j in range(N):
                model.add_shell("S%d-%d-A"%(i,j),'section',"%d-%d"%(i,j),"%d-%d"%(i+1,j),"%d-%d"%(i+1,j+1))
                model.add_shell("S%d-%d-B"%(i,j),'section',"%d-%d"%(i+1,j+1),"%d-%d"%(i,j+1),"%d-%d"%(i,j))

        patt1=LoadPattern("pat1")
        patt1.set_nodal_load("%d-%d"%(N,N),1,0,0,0,0,0)

        lc=StaticCase("case1")
        lc.add_pattern(patt1,1.0)
        asb=Assembly(model,[lc])
        asb.save(path,"test.asb")
        solver=StaticSolver(path,"test.asb")
        solver.solve_linear("case1")
        d=np.load(os.path.join(path,"case1.d.npy")).T
        
        d3=d[-6:].reshape((1,6))
        benchmark=np.array([3.671e-10,-1.999e-10,0,0,0,-6.775e-9]).reshape((1,6))
        # assert np.allclose(d3,benchmark,rtol=1e-2)
        assert d3==approx(benchmark,rel=1e-3)