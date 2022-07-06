# -*- coding: utf-8 -*-

import sys
import pytest
from pytest import approx,raises

import numpy as np
import numpy.linalg as nl

from structengpy.core import Api
import logging

class TestApi():
    def test_cantilever_beam(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        api=Api(path)
        api.add_node("A",0,0,0)
        api.add_node("B",6,0,0)
        api.add_beam("b","A","B",E=1.999e11,mu=0.3,A=4.265e-3,I3=6.572e-5,I2=3.301e-6,J=9.651e-8,rho=7849.0474)

        api.add_loadpattern("pat1")
        api.set_nodal_load("pat1","B",f3=-1e4)

        api.add_static_case("case1")
        api.add_case_pattern("case1","pat1",1.0)

        api.set_nodal_restraint("case1","A",True,True,True,True,True,True)

        api.assemble()

        api.solve_static("case1")
        d=api.result_get_nodal_displacement("B","case1")

        assert d[2]==approx(-0.05519,rel=5e-2)
        assert d[4]==approx(0.0137,rel=5e-2)
        
        d=api.result_get_beam_deformation("b",1,"case1")
        assert d[1]==approx(-0.05519,rel=2e-2)
        assert d[4]==approx(-0.0137,rel=2e-2)
        d=api.result_get_beam_deformation("b",0.5,"case1")
        assert d[1]==approx(-0.0173,rel=2e-2)
        assert d[4]==approx(-0.01027,rel=2e-2)

    def test_cantilever_beam_with_distributed_load(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        api=Api(path)
        api.add_node("A",0,0,0)
        api.add_node("B",6,0,0)
        api.add_beam("b","A","B",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

        api.add_loadpattern("pat1")
        api.set_beam_load_distributed("pat1","b",qi2=-1e4)

        api.add_static_case("case1")
        api.add_case_pattern("case1","pat1",1.0)

        api.set_nodal_restraint("case1","A",True,True,True,True,True,True)

        api.assemble()
        api.solve_static("case1")
        d=api.result_get_nodal_displacement("B","case1")

        assert d[2]==approx(-0.0046,rel=5e-2)

    def test_cantilever_beam_with_concentrated_load(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        api=Api(path)
        api.add_node("A",0,0,0)
        api.add_node("B",6,0,0)
        api.add_beam("b","A","B",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

        api.add_loadpattern("pat1")
        api.set_beam_load_concentrated("pat1","b",M3=1e4,r=0.75)

        api.add_static_case("case1")
        api.add_case_pattern("case1","pat1",1.0)

        api.set_nodal_restraint("case1","A",True,True,True,True,True,True)

        api.assemble()

        api.solve_static("case1")
        d=api.result_get_nodal_displacement("B","case1")
        assert d[2]==approx(0.0018,rel=5e-2)
