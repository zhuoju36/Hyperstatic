# -*- coding: utf-8 -*-
import pytest
from pytest import approx,raises

import numpy as np
from structengpy.core.fe_model.node import Node
from structengpy.core.fe_model.element.line.beam import Beam
from structengpy.core.fe_model.model import Model


class TestModel():
    def test_construction(self):
        model=Model()
        assert model.add_node("1",0,0,0)==0
        assert model.add_node("2",1,0,0)==1
        assert model.add_beam("A","1","2",2e6,0.2,1,2,3,4,7.85e10,False)==0
        assert model.get_node_hid("1")==0
        assert model.get_node_hid("2")==1
        assert model.get_beam_hid("A")==0

    def test_add_dup_node(self):
        model=Model()
        assert model.add_node("1",0,0,0,check_dup=True)==0
        assert model.add_node("2",0,0,0,check_dup=True)==0 #fail to add
        assert model.node_count==1
        assert model.get_node_hid("1")==0

    def test_dup_beam(self):
        model=Model()
        model.add_node("1",0,0,0)
        model.add_node("2",1,0,0)
        model.add_node("3",1,1,0)==1
        assert model.add_beam("A","1","2",2e6,0.2,1,2,3,4,7.85e10,False)==0
        assert model.add_beam("B","2","1",2e6,0.2,1,2,3,4,7.85e10,check_dup=True)==0 #fail to add
        assert model.add_beam("C","1","3",2e6,0.2,1,2,3,4,7.85e10,check_dup=True)==1

        assert model.get_beam_hid("C")==1