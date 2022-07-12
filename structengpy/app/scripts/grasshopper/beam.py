from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class MyComponent(component):
    
    def RunScript(self, crvs, section):
        """Provides a scripting component.
            Inputs:
                crvs: list of crvs to wrapped as beams
                section: beam section object
            Output:
                beams: list of beam objects"""
        
        __author__ = "Zhuoju Huang"
        __version__ = "2022.07.12"
        
        import rhinoscriptsyntax as rs
        
        class Beam():
            def __init__(self,name,crv,section):
                self.name=name
                self.curve=crv
                self.section=section
                
        names=range(len(crvs))
        beams=[Beam(name,crv,section) for crv,name in zip(crvs,names)]
        
        # return outputs if you have them; here I try it for you:
        return beams
