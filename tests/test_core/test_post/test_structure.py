# -*- coding: utf-8 -*-
from pydoc import resolve
import pytest
from pytest import approx,raises
import numpy as np

import logging
import sys
import os

from structengpy.core.fe_model.assembly import Assembly
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load.pattern import LoadPattern
from structengpy.core.fe_model.load.loadcase import ModalCase
from structengpy.core.fe_solver.dynamic import ModalSolver
from structengpy.core.fe_post.structure import StructureResultResolver


class TestStructureResult():
    def test_frequency(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)
        model.set_nodal_mass("2",1,1,1,1,1,1)

        lc=ModalCase("eigen")
        lc.use_load_as_mass=False
        lc.set_nodal_restraint("1",True,True,True,True,True,True)
        asb=Assembly(model,lc)
        
        asb.save(path,"test.sep")
        solver=ModalSolver(path,"test.sep")
        solver.solve_eigen("eigen",3)

        resolver=StructureResultResolver(path)
        resolver.resolve_modal_frequency("eigen")
