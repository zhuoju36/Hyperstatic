# -*- coding: utf-8 -*-
from pytest import approx,raises

import numpy as np
from structengpy.core.fe_model.load.loadcase import LoadCase,LoadPattern
from structengpy.common.curve import Curve

class TestBasic():
    def test_loadcase(self):
        lc=LoadCase("lc")
        lp1=LoadPattern("lp1")
        lp2=LoadPattern("lp2")
        lp1.set_nodal_load("1",1,1,1,0,0,0)
        lp2.set_nodal_load("1",2,2,2,0,0,0)
        lc.add_pattern(lp1,1)
        lc.add_pattern(lp2,2)
        f=lc.get_nodal_f("1")
        assert f[0]==5
        assert f[2]==5

    def test_time_history(self):
        lc=LoadCase("lc")
        lp1=LoadPattern("lp1")
        lp2=LoadPattern("lp2")
        lp1.set_nodal_load("1",1,2,3,0,0,0)
        lp2.set_nodal_load("1",2,2,2,0,0,0)
        c1=Curve.sin("sine",1,1,0,0.2,100).to_array()
        c2=Curve.sin("sine",1,2,0,0.2,100).to_array()
        lc.add_pattern_time_history(lp1,1,c1)
        lc.add_pattern_time_history(lp2,1,c2)
        f=lc.get_nodal_f_time_history("1")
        assert f[10,2]==1.2142872898611885
    