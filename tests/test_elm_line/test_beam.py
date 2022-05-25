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

    # def test_static_condensation(self):
    #     n1=Node("1",0,0,0)
    #     n2=Node("2",1,0,0)
    #     b=Beam("myBeam",n1,n2,2e6,0.2,100,3e8,4e8,4e8,7.85e3)
    #     b.releases[5]=True
    #     Ke=b.integrate_K()
    #     fe=np.arange(12)
    #     Ke_,fe_=b.static_condensation(Ke,fe)
    #     Ke_2,fe_2=b.static_condensation2(Ke,fe)
    #     assert np.allclose(Ke_.todense(),Ke_2.todense())==True
    #     assert np.allclose(fe_,fe_2)

