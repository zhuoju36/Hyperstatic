import pytest

from structengpy.csys import Cartisian

class TestCartesian():
    def test_T():
        csys=Cartisian((0,0,0),(1,1,0),(0,1,0))
        assert csys.transform_matrix==csys.transform_matrix

    def test_inline():
        pass