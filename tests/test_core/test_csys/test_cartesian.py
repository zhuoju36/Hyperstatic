import pytest
from pytest import approx,raises

import numpy as np
import numpy.linalg as nl

from hyperstatic.common.csys import Cartesian

class TestCartesian():
    def test_vec(self):
        csys=Cartesian((0,0,1),(1,1,0),(0,1,0))
        assert csys.origin==approx((0,0,1))
        assert nl.norm(csys.x,2)==approx(1,rel=1e-8)
        assert nl.norm(csys.y,2)==approx(1,rel=1e-8)
        assert nl.norm(csys.z,2)==approx(1,rel=1e-8)

    def test_T(self):
        csys=Cartesian((0,0,0),(1,1,0),(0,1,0))
        assert csys.transform_matrix[0,0]==approx(2**0.5/2,rel=1e-3)

    def test_inline(self):
        with pytest.raises(Exception):
            csys=Cartesian((10,10,0),(1,1,0),(2,2,0))

    def test_rotate(self):
        csys=Cartesian((0,0,0),(1,0,0),(0,1,0))
        csys.rotate_about_z(np.pi/4)
        assert csys.transform_matrix[0,0]==approx(2**0.5/2,rel=1e-3)
        assert csys.transform_matrix[1,0]==approx(-2**0.5/2,rel=1e-3)
        csys=Cartesian((0,0,0),(1,0,0),(0,1,0))
        csys.rotate_about_x(np.pi/2)
        assert csys.transform_matrix[1]==approx(np.array([0,0,1]),rel=1e-3)
        assert csys.transform_matrix[2]==approx(np.array([0,-1,0]),rel=1e-3)