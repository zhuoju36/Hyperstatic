# -*- coding: utf-8 -*-

import sys
import pytest
from pytest import approx,raises

import numpy as np
import numpy.linalg as nl

from structengpy.core import Api

class TestApi():
    def test_cantilever_beam(self):
        path="./test"
        if sys.platform=="win32":
            path="c:\\test"

        api=Api(path)
        api.add_node("A",0,0,0)
        api.add_node("B",6,0,0)
        api.add_beam("b","A","B",E=2e11,mu=0.3,A=0.0188,I2=4.023e-5,I3=4.771e-4,J=4.133e-6,rho=7.85e10)

        api.add_loadpattern("pat1")
        api.set_nodal_force("pat1","B",f3=-1e4)

        api.add_static_case("case1")
        api.add_case_pattern("case1","pat1",1.0)

        api.set_nodal_restraint("case1","A",True,True,True,True,True,True)


        api.solve_static("case1")
        d=api.result_get_nodal_displacement("case1","B")

        assert d[2]==approx(-0.00764,rel=5e-2)
        assert d[4]==approx(0.00189,rel=5e-2)