# -*- coding: utf-8 -*-

import os
import numpy as np


class NodeResultResolver(object):
    def __init__(self,path:str):
        self.__path=path

    def get_nodal_displacement(self,casename,hid):
        path=self.__path
        d=np.load(os.path.join(path,casename+".d.npy"))
        return d[hid*6:hid*6+6]

    def resolve_node_disp(self,node_id):
        node=self.__nodes[node_id]
        T=node.transform_matrix
        return T.dot(self.d_[node_id*6:node_id*6+6]).reshape(6)
    
    def resolve_node_reaction(self,node_id):
        node=self.__nodes[node_id]
        T=node.transform_matrix
        return T.dot(self.r_[node_id*6:node_id*6+6,0]).reshape(6)

    def resolve_modal_displacement(self,node_id,k): 
        if not self.is_solved:
            raise Exception('The model has to be solved first.')
        if node_id in self.__nodes.keys():
            node=self.__nodes[node_id]
            T=node.transform_matrix
            return T.dot(self.mode_[node_id*6:node_id*6+6,k-1]).reshape(6)
        else:
            raise Exception("The node doesn't exists.")
