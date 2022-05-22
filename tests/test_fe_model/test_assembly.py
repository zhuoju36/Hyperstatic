# -*- coding: utf-8 -*-
import pytest
from pytest import approx,raises

import numpy as np
from structengpy.core.fe_model.assembly import Assembly
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load.pattern import Pattern
from structengpy.core.fe_model.load.loadcase import StaticCase

class TestAssembly():
    def test_case(self):
        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",1,0,0)
        model.add_beam("A","1","2",2e6,0.2,1,2,3,4,7.85e10)

        patt1=Pattern("pat1")
        patt1.set_nodal_load("2",1,2,3,4,5,6)
        patt1.set_nodal_disp("1",0,0,0,0,0,0)

        lc=StaticCase("case1")
        lc.add_pattern(patt1,1.0)

        asb=Assembly(model,lc)
        asb.assemble_K()
        asb.assemble_f("case1")
        asb.save("D:\\test","test.sep")
        