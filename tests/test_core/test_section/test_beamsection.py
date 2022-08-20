import pytest
from pytest import approx,raises
import numpy as np

import logging
import sys
import os

from hyperstatic.core.fe_model.section.beam_section import *

class TestBeamSection():
    def test_box(self):
        box=BoxSection('box',None,400,200,14,20)
        assert box.A==18080
        assert 2.742e8*0.99<=box.J<=2.742e8*1.01 #J error
        assert 3.979e8*0.99<=box.I33<=3.979e8*1.01
        assert 1.140e8*0.99<=box.I22<=1.140e8*1.01
        assert box.As2==11200
        assert box.As3==8000

    def test_pipe(self):
        pipe=PipeSection('pipe',None,400,20)
        assert 23876.104*0.99<= pipe.A<=23876.104*1.01
        assert 8.643e8*0.99<=pipe.J<=8.643e8*1.01
        assert 4.322e8*0.99<=pipe.I33<=4.322e8*1.01
        assert 4.322e8*0.99<=pipe.I22<=4.322e8*1.01
        assert 11960.078*0.99<=pipe.As2<=11960.078*1.01
        assert 11960.078*0.99<=pipe.As3<=11960.078*1.01

    def test_I(self):
        Isection=ISection('Isection',None,400,200,14,20)
        assert 13040*0.99<=Isection.A<=13040*1.01
        assert 1320679.3*0.99<=Isection.J<=1320679.3*1.01
        assert 3.435e8*0.99<=Isection.I33<=3.435e8*1.01
        assert 26748987*0.99<=Isection.I22<=26748987*1.01
        assert 5600*0.99<=Isection.As2<=5600*1.01
        assert 6666.6667*0.99<=Isection.As3<=6666.6667*1.01

    def test_circ(self):
        circle=CircleSection('circle',None,400)
        assert 125663.71*0.99<=circle.A<=125663.71*1.01
        assert 2.513e9*0.99<=circle.J<=2.513e9*1.01
        assert 1.257e9*0.99<=circle.I33<=1.257e9*1.01
        assert 1.257e9*0.99<=circle.I22<=1.257e9*1.01
        assert 113097.34*0.99<=circle.As2<=113097.34*1.01
        assert 113097.34*0.99<=circle.As3<=113097.34*1.01

    def test_rect(self):
        rectangle=RectangleSection('rectangle',None,400,200)
        assert 80000*0.99<=rectangle.A<=80000*1.01
        assert 7.324e8*0.99<=rectangle.J<=7.324e8*1.01 #error
        assert 1.067e9*0.99<=rectangle.I33<=1.067e9*1.01
        assert 2.667e8*0.99<=rectangle.I22<=2.667e8*1.01
        assert 66666.67*0.99<=rectangle.As2<=66666.67*1.01
        assert 66666.67*0.99<=rectangle.As3<=66666.67*1.01