# -*- coding: utf-8 -*-

import os
import numpy as np


class ElementResultResolver(object):
    def __init__(self,path:str):
        self.__path=path

    def resolve_beam_force(self,beam_id):
        if beam_id in self.__beams.keys():
            beam=self.__beams[beam_id]
            i=beam.nodes[0].hid
            j=beam.nodes[1].hid
            T=beam.transform_matrix
            ue=np.vstack([
                        self.d_[i*6:i*6+6],
                        self.d_[j*6:j*6+6]
                        ])   
            return (beam.Ke_.dot(T.dot(ue))+beam.re_).reshape(12)

    
