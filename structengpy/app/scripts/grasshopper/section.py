from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class MyComponent(component):
    
    def RunScript(self, name, E, mu, A, I2, I3, J):
        """Provides a scripting component.
            Inputs:
                name: (str) name
                E: (float) Elastic modulus
                mu: (float) Poisson ratio
                A: (float) Cross section area
                I2: (float) moment of inertia around 2 axis
                I3: (float) moment of inertia around 3 axis
                J: (float) Torsion constaint
            Output:
                section: The a output variable"""
        
        __author__ = "Zhuoju Huang"
        __version__ = "2022.07.12"
        
        import rhinoscriptsyntax as rs
        
        class Section():
            def __init__(self,name,E,mu,A,I2,I3,J):
                self.name=name
                self.E=E
                self.mu=mu
                self.A=A
                self.I2=I2
                self.I3=I3
                self.J=J
        
        section=Section(name,E,mu,A,I2,I3,J)
        
        # return outputs if you have them; here I try it for you:
        return section
