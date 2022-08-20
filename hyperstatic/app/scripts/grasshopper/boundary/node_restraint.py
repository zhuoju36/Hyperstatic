from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class MyComponent(component):
    
    def RunScript(self, nodes, u1,u2,u3,r1,r2,r3):
        """Nodal restraints for Hyperstatic.
            Inputs:
                nodes: node objects
                u1: (bool) true if fixed.
                u2: (bool) true if fixed.
                u3: (bool) true if fixed.
                r1: (bool) true if fixed.
                r2: (bool) true if fixed.
                r3: (bool) true if fixed.
            Output:
                node_restraints: The restraint object"""
                        
        __author__ = "Zhuoju Huang"
        __version__ = "2022.07.12"
                                                
        class NodeRestraint():
            def __init__(self,node, res):
                self.node=node
                self.restraints=res
        DOF=[bool(u1),bool(u2),bool(u3),bool(r1),bool(r2),bool(r3)]
        node_restraints=[NodeRestraint(node,DOF) for node in nodes]
                        
        # return outputs if you have them; here I try it for you:
        return node_restraints
