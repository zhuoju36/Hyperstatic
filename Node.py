# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 21:50:29 2016

@author: HZJ
"""
import numpy as np
import CoordinateSystem

class Node:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        o=[x,y,z]
        pt1=[x+1,y,z]
        pt2=[x,y+1,z]
        self.localCsys=CoordinateSystem.CoordinateSystem(o,pt1,pt2)
        self.restraints=[False]*6
        self.load=[False]*6
        self.disp=[False]*6
        
    def TransformMatrix(self):
        V=self.localCsys.TransformMatrix()
        V_=np.zeros((6,6))
        V_[:3,:3]=V_[3:,3:]=V
        return V_

    def InitializeCsys(self):
        self.localCsys.AlignWithGlobal();

    def SetLoad(self,load):
        """
        load: a number vector indicates a nodal load.
        """
        self.load=load

    def SetDisp(self,disp):
        """
        load: a number vector indicates a nodal displacement.
        """
        self.disp=disp

    def SetRestraints(self,res):
        """
        res: a boolean vector indicates a nodal displacement.
        """
        self.restraints=res