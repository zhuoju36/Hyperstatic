from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class MyComponent(component):
    
    def RunScript(self, nodes, DOF):
        """Provides a scripting component.
            Inputs:
                nodes: node objects
                DOF: list of 6 bool represents the degrees of freedom, True if fixed.
            Output:
                node_restraints: The restraint object"""
                        
        __author__ = "Zhuoju Huang"
        __version__ = "2022.07.12"
                        
        import rhinoscriptsyntax as rs
                        
        class NodeRestraint():
            def __init__(self,node, res):
                self.node=node
                self.restraints=res
                        
        node_restraints=[NodeRestraint(node,DOF) for node in nodes]
                        
                
        
        # return outputs if you have them; here I try it for you:
        return node_restraints
