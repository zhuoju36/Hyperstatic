# -*- coding: utf-8 -*-
import pytest
from pytest import approx,raises
import numpy as np

import logging
import sys
import os

from hyperstatic.core.fe_model.assembly import Assembly
from hyperstatic.core.fe_model.model import Model
from hyperstatic.core.fe_model.load.pattern import LoadPattern
from hyperstatic.core.fe_model.load.loadcase import ModalCase
from hyperstatic.core.fe_solver.dynamic import ModalSolver

class TestModalSolver():
    def test_mass_eigen(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_simple_beam("A","1","2",E=1.999e11,mu=0.3,A=4.265e-3,I3=6.572e-5,I2=3.301e-6,J=9.651e-8,rho=7849.0474)
        # model.set_nodal_mass("2",1,1,1,1,1,1)

        lc=ModalCase("eigen",n_modes=3)
        lc.use_load_as_mass=False
        lc.set_nodal_restraint("1",True,True,True,True,True,True)
        asb=Assembly(model,[lc])
        asb.save(path,"test.asb")
        solver=ModalSolver(path,"test.asb")
        solver.solve_eigen("eigen")
        o2=np.load(os.path.join(path,"eigen.o.npy"))
        T=2*np.pi/np.sqrt(o2)
        assert T[0]==approx(0.65770,rel=5e-2)
        assert T[1]==approx(0.14792,rel=5e-2)

        # assert d[10]==approx(0.00189,rel=5e-2)

    def test_mass_eigen2(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",6,0,0)
        model.add_isotropic_material('steel',7849.0474,2e11,0.3,1.17e-5)
        model.add_beam_section_I('H400x200x20x30','steel',0.4,0.2,0.02,0.03)
        model.add_beam("A","1","2",'H400x200x20x30')
        model.set_nodal_restraint("1",True,True,True,True,True,True)

        lc=ModalCase("eigen",3)
        asb=Assembly(model,[lc])
        asb.save(path,"test.asb")
        solver=ModalSolver(path,"test.asb")
        solver.solve_eigen("eigen")
        
        omega2=np.load(os.path.join(path,"eigen.o.npy"))
        d=np.load(os.path.join(path,"eigen.d.npy"))
        T=2*np.pi/np.sqrt(omega2)
        assert T[0]==approx(0.39528,rel=5e-2)
        assert T[1]==approx(0.1148,rel=5e-2)
        assert d[1,2]==approx(-4.7528e-2,rel=1e-2)
        assert d[1,4]==approx(1.1882e-2,rel=1e-2)

   