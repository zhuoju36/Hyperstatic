# -*- coding: utf-8 -*-
import pytest
from pytest import approx,raises

import numpy as np
from structengpy.core.fe_model.node import Node

class TestNode():
    def test_T(self):
        node=Node("1",0.2,1.3,1.2)
        assert node.transform_matrix[2,2]==1
        assert node.transform_matrix[5,5]==1