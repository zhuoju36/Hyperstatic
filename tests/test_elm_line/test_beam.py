# -*- coding: utf-8 -*-
import pytest
from pytest import approx,raises

import numpy as np
from structengpy.core.fe_model.node import Node
from structengpy.core.fe_model.element.line.beam import Beam

class TestBeam():
    def test_construction(self):
        n1=Node("1",0,0,0)
        n2=Node("2",1,0,0)
        b=Beam("myBeam",n1,n2,2e6,0.2,100,3e8,4e8,4e8,7.85e3)
        assert id(b._Element__nodes[0])==id(n1) #identity check
        assert b.length==approx(1,rel=1e-9)
        assert b.dim==1
        assert b.dof==12

    def test_K(self):
        n1=Node("1",0,0,0)
        n2=Node("2",1,0,0)
        b=Beam("myBeam",n1,n2,2e6,0.2,100,3e8,4e8,4e8,7.85e3)
        b.integrate_K()

    def test_M(self):
        n1=Node("1",0,0,0)
        n2=Node("2",1,0,0)
        b=Beam("myBeam",n1,n2,2e6,0.2,100,3e8,4e8,4e8,7.85e3)
        b.integrate_M()