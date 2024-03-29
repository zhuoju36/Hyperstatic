
from datetime import datetime
import pickle
import numpy as np

from hyperstatic.core import Api
from random import uniform as u
from vedo import Points, Line, Lines, Arrows, Plotter, Cone,Text2D,Mesh
from vedo.pyplot import histogram
import os
from hyperstatic.app.viz.viz_core import ViewerBase

class BasicViewer(ViewerBase):
    def __init__(self,workpath,filename,qtWidget=None):
        super(BasicViewer, self).__init__(workpath,filename,qtWidget)
        self.setup_gui()
        self.__scale=1

##GUI
    def setup_gui(self):
        plt=self.plotter
        self.__btn_node=plt.addButton(
            self.toggle_node,
            bc=("b6","r6"),
            pos=(0.6,0.15),
            states=("show_node","hide_node"),
            font="Normografo",
            size=12,
        )
        self.__btn_beam=plt.addButton(
            self.toggle_beam,
            bc=("r6","b6"),
            pos=(0.6,0.1),
            states=("hide_beam","show_beam"),
            font="Normografo",
            size=12,
        )
        self.__btn_shell=plt.addButton(
            self.toggle_shell,
            bc=("r6","b6"),
            pos=(0.6,0.05),
            states=("hide_shell","show_shell"),
            font="Normografo",
            size=12,
        )

    def slide_scale(self,widget,event):
        self.__scale=widget.GetRepresentation().GetValue()

    def toggle_node(self):
        if not self.vnodes==None:
            if self.__btn_node.status()=="hide_node":
                self.vnodes.off()
            else:
                self.vnodes.on()
        self.__btn_node.switch() 

    def toggle_beam(self):
        if not self.vbeams==None:
            if self.__btn_beam.status()=="hide_beam":
                
                self.vbeams.off()
            else:
                self.vbeams.on()
        self.__btn_beam.switch() 

    def toggle_shell(self):
        if not self.vshells==None:
            if self.__btn_shell.status()=="hide_shell":
                self.vshells.off()
            else:
                self.vshells.on()
        self.__btn_shell.switch()    

    def toggle_node_name(self):
        self.reset()

    def toggle_node_csys(self):
        self.reset()

    def toggle_beam_name(self):
        self.reset()

    def toggle_beam_release(self):
        self.reset()

    def toggle_beam_section(self):
        self.reset()

    def toggle_beam_csys(self):
        self.reset()

    def toggle_beam_load(self):
        self.reset()

    def init_nodal_load(self):
        api=self.api
        arrow_starts=[]
        arrow_ends=[]
        loads=[]
        f_scals=[]
        m_scals=[]
        f_value=[]
        m_value=[]
        load_dict=api.get_all_nodal_load("pat1")
        for n in api.get_node_names():
            if n in api.get_all_nodal_load("pat1").keys():
                x,y,z=api.get_node_location(n)
                f1,f2,f3,m1,m2,m3=tuple(load_dict[n])
                f=(f1**2+f2**2+f3**2)**0.5
                [f_value.append(f) for i in range(16)]
                m_value.append((m1**2+m2**2+m3**2)**0.5)
                f_scals.append(f)
                loads.append([f1,f2,f3,m1,m2,m3])
                arrow_ends.append((x,y,z))
        scale=self.scale/max(f_scals)*0.1
        for e,l in zip(arrow_ends,loads):
            arrow_starts.append((e[0]-l[0]*scale,e[1]-l[1]*scale,e[2]-l[2]*scale))

        self.__vnodeload=Arrows(arrow_starts,arrow_ends,s=0.5,res=3)
        self.__vnodeload.cmap('viridis', f_value).addScalarBar(title="Nodal load(N)",pos=(0.8,0.4)) #"jet", "PuOr", "viridis"
        self.__vnodeload.off()
        self.__vnodeload.scalarbar.VisibilityOff()
        self.actors+=[self.__vnodeload]
        
if __name__=="__main__":
    path=r"C:\Users\HZJ\Desktop\ghdev\analysis"
    viewer=BasicViewer(path,"assembly")
    viewer.run()
