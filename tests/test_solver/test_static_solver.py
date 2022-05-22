# -*- coding: utf-8 -*-
import pytest
from pytest import approx,raises

from structengpy.core.fe_solver.static import StaticSolver

class TestStaticSolver():
    def test_case(self):
        solver=StaticSolver("D:\\test","test.sep")
        solver.solve_linear("case1")
        