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
from structengpy.core.fe_model.load.loadcase import ModalCase
from structengpy.core.fe_solver.dynamic import ModalSolver

class TestModalSolver():
    def test_mass_eigen(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_beam("A","1","2",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)
        # model.set_nodal_mass("2",1,1,1,1,1,1)

        lc=ModalCase("eigen")
        lc.use_load_as_mass=False
        lc.set_nodal_restraint("1",True,True,True,True,True,True)
        asb=Assembly(model,[lc])
        asb.save(path,"test.asb")
        solver=ModalSolver(path,"test.asb")
        solver.solve_eigen("eigen",3)
        d=np.load(os.path.join(path,"eigen.o.npy"))
        assert d==approx(-0.00764,rel=5e-2)
        # assert d[10]==approx(0.00189,rel=5e-2)

   