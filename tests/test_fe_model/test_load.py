# -*- coding: utf-8 -*-
import pytest
from pytest import approx,raises

import numpy as np
from structengpy.core.fe_model.node import Node
from structengpy.core.fe_model.element.line.beam import Beam
from structengpy.core.fe_model.load.pattern import Pattern
from structengpy.core.fe_model.load.loadcase import StaticCase

class TestLoad():
    def test_pattern(self):
        patt=Pattern("pat1")
        patt.set_nodal_load("a",1,2,3,4,5,6)
        v=patt.get_nodal_load("a")
        assert v.shape==(6,)
        assert v[2]==3
        patt.set_nodal_disp("b",6,5,4,3,2,1)
        v=patt.get_nodal_disp("b")
        assert v.shape==(6,)
        assert v[2]==4

    def test_case(self):
        patt1=Pattern("pat1")
        patt1.set_nodal_load("a",1,2,3,4,5,6)
        patt1.set_nodal_disp("b",6,5,4,3,2,1)
        patt2=Pattern("pat2")
        patt2.set_nodal_load("a",1,1,1,0,0,0)
        patt2.set_nodal_disp("b",0,0,0,1,1,1)
        lc=StaticCase("case1")
        lc.add_pattern(patt1,1.0)
        lc.add_pattern(patt2,2.0)
        r=lc.get_nodal_load_vector("a")

        assert r==approx(np.array([3,4,5,4,5,6]).reshape(6),rel=1e-9)







        