from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class MyComponent(component):
    
    def RunScript(self, name, rho,E,mu):
        """General sotropic material for StructEngPy
            Inputs:
                name: (str) name
                rho: (float) desity
                E: (float) elastic modulus
                mu: (float) Poisson ratio
            Output:
                material: The a output variable"""
        
        __author__ = "Zhuoju Huang"
        __version__ = "2022.07.12"
        
        class IsotropicMaterial():
            def __init__(self,name,rho,E,mu):
                self.name=name
                self.rho=rho
                self.E=E
                self.mu=mu
                
        material=IsotropicMaterial(str(name),
            float(rho),
            float(E),
            float(mu),
            )
        
        # return outputs if you have them; here I try it for you:
        return material
