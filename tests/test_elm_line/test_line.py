# -*- coding: utf-8 -*-
import pytest
from pytest import approx,raises

import numpy as np
from structengpy.fe_model.node import Node
from structengpy.fe_model.element.line import Line

class TestBeam():
    def test_construction(self):
        n1=Node("1",0,0,0)
        n2=Node("2",1,0,0)
        l=Line("myLine",n1,n2,12)
        assert l.length==approx(1,rel=1e-9)