# -*- coding: utf-8 -*-
import pytest
from pytest import approx,raises

import numpy as np
from structengpy.core.fe_model.node import Node
from structengpy.core.fe_model.element.line import Line

class TestLine():
    def test_construction(self):
        n1=Node("1",0,0,0)
        n2=Node("2",1,0,0)
        l=Line("myLine",n1,n2,12)
        assert l.length==approx(1,rel=1e-9)

    def test_direction(self):
        n1=Node("1",0,0,0)
        n2=Node("2",1,0,0)
        l=Line("myLine",n1,n2,12)
        assert l.local_csys.x==approx(np.array([1,0,0]),rel=1e-6)
        assert l.local_csys.y==approx(np.array([0,0,1]),rel=1e-6)
        assert l.local_csys.z==approx(np.array([0,-1,0]),rel=1e-6)

        n1=Node("1",0,0,0)
        n2=Node("2",0,0,1)
        l=Line("myLine",n1,n2,12)
        assert l.local_csys.x==approx(np.array([0,0,1]),rel=1e-6)
        assert l.local_csys.y==approx(np.array([1,0,0]),rel=1e-6)
        assert l.local_csys.z==approx(np.array([0,1,0]),rel=1e-6)