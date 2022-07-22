
from datetime import datetime
import pickle
import numpy as np

from structengpy.core import Api
from random import uniform as u
from vedo import Points, Mesh, Lines, Arrows, Plotter, Cone,Text2D
from vedo.pyplot import histogram
import os
from structengpy.app.viz.viz_core import ViewerBase

class ResultViewer(ViewerBase):
    def __init__(self,workpath,filename):
        super(ResultViewer,self).__init__(workpath,filename)
        self.__deform_scale=1
        self.setup_gui()
        self.toggle_restraints(False)

    def setup_gui(self):
        plt=self.plotter
        self.__btn_node=plt.addButton(
            self.toggle_node,
            bc=("b6","r6"),
            states=("show nodes","hide nodes"),
            font="san-serif",
            pos=(0.58,0.05),
            size=12,
        )

        self.__btn_deform_x=plt.addButton(
            self.show_result_deformation_X,
            bc=("b6","r6"),
            states=("deformX","reset"),
            font="san-serif",
            pos=(0.7,0.05),
            size=12,
        )
        self.__btn_deform_y=plt.addButton(
            self.show_result_deformation_Y,
            bc=("b6","r6"),
            pos=(0.8,0.05),
            states=("deformY","reset"),
            font="san-serif",
            size=12,
        )
        self.__btn_deform_z=plt.addButton(
            self.show_result_deformation_Z,
            bc=("b6","r6"),
            pos=(0.9,0.05),
            states=("deformZ","reset"),
            font="san-serif",
            size=12,
        )
        self.__scale_slider=plt.addSlider2D(
            self.slide_scale,
            # pos="bottom-left",
            pos=[(0.65,0.15),(0.95,0.15)],
            # titleSize=0.5,
            xmin=0,
            xmax=100,
            title="scale"
        )

    def slide_scale(self,widget,event):
        self.__deform_scale=widget.GetRepresentation().GetValue()

    def toggle_node(self):
        if self.__btn_node.status()=="hide nodes":
            self.vnodes.off()
        else:
            self.vnodes.on()
        self.__btn_node.switch() 

    def show_result_deformation_X(self):
        pts=self.pts.copy()
        lines=self.lines.copy()
        if "deform" in self.__btn_deform_x.status(): 
            self.__show_result_deformation(pts,lines,dir="x")
        else:
            self.__reset_deformation(pts,lines)
        self.__btn_deform_x.switch()
        for btn in [self.__btn_deform_z,self.__btn_deform_y]:
            if "reset" in btn.status():
                btn.switch()
        self.reset()

    def show_result_deformation_Y(self):
        pts=self.pts.copy()
        lines=self.lines.copy()
        if "deform" in self.__btn_deform_y.status(): 
            self.__show_result_deformation(pts,lines,dir="y")
        else:
            self.__reset_deformation(pts,lines)
        self.__btn_deform_y.switch()
        for btn in [self.__btn_deform_x,self.__btn_deform_z]:
            if "reset" in btn.status():
                btn.switch()
        self.reset()

    def show_result_deformation_Z(self):
        pts=self.pts.copy()
        lines=self.lines.copy()
        if "deform" in self.__btn_deform_z.status(): 
            self.__show_result_deformation(pts,lines,dir="z")
        else:
            self.__reset_deformation(pts,lines)
        self.__btn_deform_z.switch()
        for btn in [self.__btn_deform_x,self.__btn_deform_y]:
            if "reset" in btn.status():
                btn.switch()
        self.reset()

    def __reset_deformation(self,pts,lines):
        self.plotter.remove(self.vnodes)
        self.plotter.remove(self.vbeams)
        self.plotter.remove(self.vshells)
        self.vnodes=Points(list(pts.values()), r=8, c="blue5").off()
        self.vbeams=Lines(list(lines.values()))
        self.vshells=Mesh([list(pts.values()),list(self.faces.values())])
        self.vshells.color('b5').backColor('violet').lineColor('tomato').lineWidth(1)
        self.actors["nodes"]=self.vnodes
        self.actors["beams"]=self.vbeams
        self.actors["shells"]=self.vshells
        
        if self.__btn_node.status()=="show nodes":
            self.vnodes.off()

    def __show_result_deformation(self,pts,lines,casename="case1",dir="z"):
        scale=self.__deform_scale
        api=self.api
        disp={}
        #scale bar
        scals = np.zeros(len(pts))
        d=api.result_get_all_nodal_displacement(casename)
        for k,v in d.items():
            o=pts[k]
            pts[k]=(o[0]+v[0]*scale,o[1]+v[1]*scale,o[2]+v[2]*scale)
            if dir=="x":
                disp[k]=v[0]
            elif dir=="y":
                disp[k]=v[1]
            elif dir=="z":
                disp[k]=v[2]
        #scale bar
        scals = tuple(disp.values())
        vmax,vmin=max(scals),min(scals)
        vmax=max(abs(vmax),abs(vmin))
        vmin=-vmax
        
        lscals=[]
        self.plotter.remove(self.vnodes)
        self.vnodes=Points(tuple(pts.values()), r=8, c="blue5")
        if self.__btn_node.status()=="show nodes":
            self.vnodes.off()

        self.vnodes.cmap('PuOr', scals, vmax=vmax,vmin=vmin) #"jet", "PuOr", "viridis"
        self.vnodes.addScalarBar(title="Deformation(m)",pos=(0.8,0.4))
        self.plotter.remove(self.vbeams)
        for b in api.get_beam_names():
            s,e=api.get_beam_node_names(b)
            lines[b]=([pts[s],pts[e]])
            lscals.append(disp[s])
            lscals.append(disp[e])
        self.vbeams=Lines(tuple(lines.values()),c='k')
        self.vbeams.cmap('PuOr', lscals, vmax=vmax,vmin=vmin)

        self.plotter.remove(self.vshells)
        shells=api.get_shell_names()
        if shells==None:
            return
        self.vshells=Mesh([list(pts.values()),list(self.faces.values())])
        self.vshells.cmap('PuOr', scals, vmax=vmax,vmin=vmin).lineColor('tomato').lineWidth(1)

        self.actors["nodes"]=self.vnodes
        self.actors["beams"]=self.vbeams
        self.actors["shells"]=self.vshells

if __name__=="__main__":
    # path=r"G:\testghsep"
    path=r"C:\Users\HZJ\Desktop\ghdev\analysis"
    viewer=ResultViewer(path,"assembly")
    viewer.run()