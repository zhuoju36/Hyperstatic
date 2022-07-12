"""Provides a scripting component.
    Inputs:
        name: The x script variable
        E: The y script variable
        mu: The y script variable
        A: The y script variable
        I2: The y script variable
        I3: The y script variable
        J: The y script variable
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