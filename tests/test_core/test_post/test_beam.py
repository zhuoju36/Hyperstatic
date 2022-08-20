# -*- coding: utf-8 -*-
from pydoc import resolve
import pytest
from pytest import approx,raises
import numpy as np

import logging
import sys
import os

from hyperstatic.core.fe_model.assembly import Assembly
from hyperstatic.core.fe_model.model import Model
from hyperstatic.core.fe_model.load.pattern import LoadPattern
from hyperstatic.core.fe_model.load.loadcase import ModalCase, StaticCase
from hyperstatic.core.fe_solver.dynamic import ModalSolver
from hyperstatic.core.fe_post.beam import BeamResultResolver
from hyperstatic.core.fe_solver.static import StaticSolver


class TestBeamResult():
    def test_cantilever(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_simple_beam("A","1","2",E=1.999e11,mu=0.3,A=4.265e-3,I3=6.572e-5,I2=3.301e-6,J=9.651e-8,rho=7849.0474)

        patt1=LoadPattern("pat1")
        patt1.set_nodal_load("2",0,0,-1e4,0,0,0)

        lc=StaticCase("case1")
        lc.add_pattern(patt1,1.0)
        lc.set_nodal_restraint("1",True,True,True,True,True,True)
        asb=Assembly(model,[lc])
        asb.save(path,"test.asb")
        solver=StaticSolver(path,"test.asb")
        solver.solve_linear("case1")
        
        resolver=BeamResultResolver(path,"test.asb")
        d=resolver.resolve_beam_deformation("A",1,"case1")
        assert d[1]==approx(-0.05519,rel=2e-2)
        assert d[4]==approx(-0.0137,rel=2e-2)
        d=resolver.resolve_beam_deformation("A",0.5,"case1")
        assert d[1]==approx(-0.0173,rel=2e-2)
        assert d[4]==approx(-0.01027,rel=2e-2)




        