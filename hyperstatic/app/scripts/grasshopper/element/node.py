from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class MyComponent(component):
    
    def RunScript(self, pts):
        """Provides a scripting component.
            Inputs:
                pts: list of point objects
            Output:
                nodes: list of wrapped node objects"""
                
        __author__ = "Zhuoju Huang"
        __version__ = "2022.07.12"
                
        import rhinoscriptsyntax as rs
                
        class Node():
            def __init__(self,name, pt):
                self.name=name
                self.point=pt
                
        nodes=[Node(str(i+1),pt) for i,pt in zip(range(len(pts)),pts)]
                
        
        # return outputs if you have them; here I try it for you:
        return nodes
