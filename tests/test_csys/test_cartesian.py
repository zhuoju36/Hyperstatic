import pytest
from pytest import approx,raises

import numpy.linalg as nl

from structengpy.csys import Cartisian

class TestCartesian():
    def test_vec(self):
        csys=Cartisian((0,0,1),(1,1,0),(0,1,0))
        assert csys.origin==approx((0,0,1))
        assert nl.norm(csys.x,2)==approx(1,rel=1e-8)
        assert nl.norm(csys.y,2)==approx(1,rel=1e-8)
        assert nl.norm(csys.z,2)==approx(1,rel=1e-8)

    def test_T(self):
        csys=Cartisian((0,0,0),(1,1,0),(0,1,0))
        assert csys.transform_matrix[0,0]==approx(2**0.5/2,rel=1e-3)

    def test_inline(self):
        with pytest.raises(Exception):
            csys=Cartisian((10,10,0),(1,1,0),(2,2,0))