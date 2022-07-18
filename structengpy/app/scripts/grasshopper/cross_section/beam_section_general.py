from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class MyComponent(component):
    
    def RunScript(self, name, material, A, As2, As3, J, I2, I3):
        """General Section for StructEngPy
            Inputs:
                name: (str) name
                material: (obj): material object
                A: (float) cross section area
                As2: (float) shear area of 2 axis
                As3: (float) shear area of 3 axis
                J: (float) torsion constaint
                I2: (float) moment of inertia around 2 axis
                I3: (float) moment of inertia around 3 axis
            Output:
                section: The a output variable"""
        
        __author__ = "Zhuoju Huang"
        __version__ = "2022.07.12"
        class Section():
            def __init__(self,name,mat,A,As2,As3,J,I2,I3):
                self.name=name
                self.shape="general"
                self.material=mat
                self.rho=material.rho
                self.E=material.E
                self.mu=material.mu
                self.A=A
                self.As2=As2
                self.As3=As3
                self.J=J
                self.I2=I2
                self.I3=I3
                
        section=Section(str(name),
            material,
            float(A),
            float(As2),
            float(As3),
            float(J),
            float(I2),
            float(I3)
            )
        
        # return outputs if you have them; here I try it for you:
        return section
