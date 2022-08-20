# -*- coding: utf-8 -*-
from pytest import approx,raises

import numpy as np
from hyperstatic.core.fe_model.load.pattern import LoadPattern

class TestBeam():
    def test_beam_distributed(self):
        load=LoadPattern("test")
            #fi,qi2,qi3, ti,mi2,mi3; fj,qj2,qj3, tj,mj2,mj3;
        inp=np.array([
            [1,  1,  0,  0,  0,  0,  0,  0,  ],
            [0,  0,  1,  1,  0,  0,  0,  0,  ],
            [0,  0,  0,  0,  1,  1,  0,  0,  ],
            [0,  0,  0,  0,  0,  0,  1,  1,  ],
            ])
        oup=np.array([
            [ 1/2, 0,  0,  0,  0,  0, 1/2, 0, 0,  0,  0,  0],
            [0, 0.5, 0, 0, 0, 1/12, 0, 0.5, 0, 0, 0, -1/12],
            [0, 0, 0.5, 0, -1/12, 0, 0, 0, 0.5, 0, 1/12, 0],
            [0, 0,  0, 1/2,  0,  0,  0, 0, 0, 1/2,  0,  0],
            ])
        for i,o in zip(inp,oup):
            load.set_beam_load_dist("1",*tuple(i))
            fd=load.get_beam_f("1",1)
            assert np.allclose(fd[:6],o[:6]) == True
            assert np.allclose(fd[6:],o[6:]) == True

    def test_beam_concentrated(self):
        load=LoadPattern("test")
            #P,F2,F3,T,M2,M3,ratio;
        inp=np.array([
            [1,  0,  0,  0,  0,  0,  0.5,  ],
            [0,  1,  0,  0,  0,  0,  0.5,  ],
            [0,  0,  1,  0,  0,  0,  0.5,  ],
            [0,  0,  0,  1,  0,  0,  0.5,  ],
            [0,  0,  0,  0,  1,  0,  0.5,  ],
            [0,  0,  0,  0,  0,  1,  0.5,  ],
            ])
        oup=np.array([
            [1/2, 0,  0,  0,  0,  0, 1/2, 0, 0,  0,  0,  0],
            [0, 1/2, 0, 0, 0, 1/8, 0, 1/2, 0, 0, 0, -1/8],
            [0, 0, 1/2, 0, -1/8, 0, 0, 0, 1/2, 0, 1/8, 0],
            [0, 0,  0, 1/2,  0,  0,  0, 0, 0, 1/2,  0,  0],
            [0, 0, 3/2, 0, -1/4, 0, 0, 0, -3/2, 0, -1/4, 0], #
            [0, -3/2, 0, 0, 0, -1/4, 0,3/2, 0, 0, 0, -1/4],
            ])
        for i,o in zip(inp,oup):
            load.set_beam_load_conc("1",*tuple(i))
            fd=load.get_beam_f("1",1)
            assert np.allclose(fd[:6],o[:6]) == True
            assert np.allclose(fd[6:],o[6:]) == True
            # assert np.allclose(fd,o) == True