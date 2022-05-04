    def resolve_node_disp(self,node_id):
        if not self.is_solved:
            raise Exception('The model has to be solved first.')
        if node_id in self.__nodes.keys():
            node=self.__nodes[node_id]
            T=node.transform_matrix
            return T.dot(self.d_[node_id*6:node_id*6+6]).reshape(6)
        else:
            raise Exception("The node doesn't exists.")
    
    def resolve_node_reaction(self,node_id):
        if not self.is_solved:
            raise Exception('The model has to be solved first.')
        if node_id in self.__nodes.keys():
            node=self.__nodes[node_id]
            T=node.transform_matrix
            return T.dot(self.r_[node_id*6:node_id*6+6,0]).reshape(6)
        else:
            raise Exception("The node doesn't exists.")       
    
    def resolve_beam_force(self,beam_id):
        if not self.is_solved:
            raise Exception('The model has to be solved first.')
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
        else:
            raise Exception("The element doesn't exists.")       

    def resolve_modal_displacement(self,node_id,k): 
        """
        resolve modal node displacement.
        
        params:
            node_id: int.
            k: order of vibration mode.
        return:
            6-array of local nodal displacement.
        """
        if not self.is_solved:
            raise Exception('The model has to be solved first.')
        if node_id in self.__nodes.keys():
            node=self.__nodes[node_id]
            T=node.transform_matrix
            return T.dot(self.mode_[node_id*6:node_id*6+6,k-1]).reshape(6)
        else:
            raise Exception("The node doesn't exists.")
    
    def resolve_membrane3_stress(self,membrane_id):
        pass
    
    def resolve_membrane4_stress(self,membrane_id):
        pass