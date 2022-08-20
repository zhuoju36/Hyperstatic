# -*- coding: utf-8 -*-
import pytest
from pytest import approx
from hyperstatic.core.fe_model.node import Node
from hyperstatic.core.fe_model.material.isotropy import IsotropicMaterial
from hyperstatic.core.fe_model.section.beam_section import BeamSection
from hyperstatic.core.fe_model.node import Node

from hyperstatic.core.fe_model.element.line.beam import Beam

class TestBeam():
    def test_construction(self):
        n1=Node("1",0,0,0)
        n2=Node("2",1,0,0)
        steel=IsotropicMaterial('mat',7.85e3,2e6,0.2,1e-7)
        section=BeamSection('sec',steel,'general',[],100,20,20,3e8,4e8,4e8,3e8,3e8)
        b=Beam("myBeam",n1,n2,section)
        assert id(b._Element__nodes[0])==id(n1) #identity check
        assert b.length==approx(1,rel=1e-9)
        assert b.dim==1
        assert b.dof==12

    def test_K(self):
        n1=Node("1",0,0,0)
        n2=Node("2",1,0,0)
        steel=IsotropicMaterial('mat',7.85e3,2e6,0.2,1e-7)
        section=BeamSection('sec',steel,'general',[],100,20,20,3e8,4e8,4e8,3e8,3e8)
        b=Beam("myBeam",n1,n2,section)
        b.integrate_K()

    def test_M(self):
        n1=Node("1",0,0,0)
        n2=Node("2",1,0,0)
        steel=IsotropicMaterial('mat',7.85e3,2e6,0.2,1e-7)
        section=BeamSection('sec',steel,'general',[],100,20,20,3e8,4e8,4e8,3e8,3e8)
        b=Beam("myBeam",n1,n2,section)
        b.integrate_M()

