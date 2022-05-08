# -*- coding: utf-8 -*-
import pytest
from pytest import approx,raises

import numpy as np
from structengpy.fe_model.node import Node
from structengpy.fe_model.line.beam import Beam

class TestBeam():
    def test_construction(self):
        n1=Node("1",0,0,0)
        n2=Node("2",1,0,0)
        l=Beam("myBeam",n1,n2,2e6,100,2e8,3e8,4e8,7.85e3)
        assert l.length==approx(1,ref=1e-9)