
from datetime import datetime
import pickle
import numpy as np

from structengpy.core import Api
# from structengpy.core.fe_model.model import Model
# from structengpy.core.fe_model.load.pattern import LoadPattern
# from structengpy.core.fe_model.load.loadcase import ModalCase, StaticCase
# from structengpy.core.fe_solver.dynamic import ModalSolver
# from structengpy.core.fe_post.beam import BeamResultResolver
# from structengpy.core.fe_solver.static import StaticSolver


# path="./test"
# if sys.platform=="win32":
#     path="c:\\test"
from random import uniform as u
from vedo import Points, Line, Lines, Arrows, Plotter, Cone,Text2D,Mesh
from vedo.pyplot import histogram
import os
class ViewerBase():
    def __init__(self,workpath,filename,qtWidget=None):
        self.workpath=workpath
        filename=os.path.join(workpath,filename)
        self.api:Api=Api.load(workpath,filename)
        self.pts={}
        self.lines={}
        self.faces={}
        self.vnodes:Points=None
        self.vnodeload:Arrows=None
        self.vnodeNames=None
        self.vnode_restraints=[]
        self.vbeams:Lines=None
        self.vbeamNames=None
        self.vbeamReleases=None
        self.vshells:Mesh=None
        if qtWidget!=None:
            self.plotter=Plotter(qtWidget=qtWidget)
        else:
            self.plotter=Plotter()
        self.pt_id_map={}

        self.actors={}

        self.init_nodes()
        self.init_beams()
        self.init_shells()
        self.scale=self.scene_radius()
        self.init_restraints()
        

    def setup_gui(self):
        raise NotImplementedError

    def init_nodes(self):
        api=self.api
        pts=self.pts
        nodes=api.get_node_names()
        if nodes==None:
            return
        for n in nodes:
            x,y,z=api.get_node_location(n)
            self.pt_id_map[n]=len(pts)
            pts[n]=(x,y,z)
        self.vnodes = Points(list(pts.values()), r=8, c="blue5")
        self.vnodes.off()
        self.actors["node"]=self.vnodes

    def init_restraints(self):
        api=self.api
        scale=self.scale/100
        restraints=api.get_node_restraints()
        if restraints==None:
            return
        for k,v in restraints.items():
            pt=self.pts[k]
            if v[0]:
                c=Cone(pos=(pt[0]-1*scale,pt[1],pt[2]),r=1*scale,height=2*scale,res=4,axis=(1,0,0))
                self.vnode_restraints.append(c)
            if v[1]:
                c=Cone(pos=(pt[0],pt[1]-1*scale,pt[2]),r=1*scale,height=2*scale,res=4,axis=(0,1,0))
                self.vnode_restraints.append(c)
            if v[2]:
                c=Cone(pos=(pt[0],pt[1],pt[2]-1*scale),r=1*scale,height=2*scale,res=4,axis=(0,0,1))
                self.vnode_restraints.append(c)
            if v[3]:
                c1=Cone(pos=(pt[0]+1*scale,pt[1],pt[2]),c='r3',r=1*scale,height=2*scale,res=4,axis=(-1,0,0))
                # c2=Cone(pos=(pt[0]+2*scale,pt[1],pt[2]),c='r3',r=1*scale,height=2*scale,res=4,axis=(-1,0,0))
                self.vnode_restraints.append(c1)
                # self.vnode_restraints.append(c2)
            if v[4]:
                c1=Cone(pos=(pt[0],pt[1]+1*scale,pt[2]),c='r3',r=1*scale,height=2*scale,res=4,axis=(0,-1,0))
                # c2=Cone(pos=(pt[0],pt[1]+2*scale,pt[2]),c='r3',r=1*scale,height=2*scale,res=4,axis=(0,-1,0))
                self.vnode_restraints.append(c1)
                # self.vnode_restraints.append(c2)
            if v[5]:
                c1=Cone(pos=(pt[0],pt[1],pt[2]+1*scale),c='r3',r=1*scale,height=2*scale,res=4,axis=(0,0,-1))
                # c2=Cone(pos=(pt[0],pt[1],pt[2]+2*scale),c='r3',r=1*scale,height=2*scale,res=4,axis=(0,0,-1))
                self.vnode_restraints.append(c1)
                # self.vnode_restraints.append(c2)
        for c in self.vnode_restraints:
            c.wireframe() 
            c.off()#default off
        self.actors["restraints"]=self.vnode_restraints

    def toggle_restraints(self,on:bool):
        if on:
            for c in self.vnode_restraints:
                c.on() #default off
        else:
            for c in self.vnode_restraints:
                c.off() #default off

    def init_beams(self):
        api=self.api
        lines=self.lines
        pts=self.pts
        beams=api.get_beam_names()
        if beams==None:
            return
        for b in beams:
            s,e=api.get_beam_node_names(b)
            lines[b]=([pts[s],pts[e]])
        self.vbeams=Lines(list(lines.values()),c='k')
        self.actors["beams"]=self.vbeams

    def init_shells(self):
        api=self.api
        pts=self.pts
        pt_id_map=self.pt_id_map
        shells=api.get_shell_names()
        if shells==[] or shells==None:
            return
        for s in shells:
            n1,n2,n3,n4=api.get_shell_node_names(s)
            verts=list(pts.values())
            f=(pt_id_map[n1],pt_id_map[n2],pt_id_map[n3],pt_id_map[n4])
            self.faces[s]=f
        self.vshells=Mesh([verts,list(self.faces.values())])
        self.vshells.color('lightsteelblue').backColor('slateblue').lineColor('tomato').lineWidth(1)
        self.actors["shells"]=self.vshells

    def scene_radius(self):
        xs=[i[0] for i in self.pts.values()]
        ys=[i[1] for i in self.pts.values()]
        zs=[i[2] for i in self.pts.values()]
        maxx,minx=max(xs),min(xs)
        maxy,miny=max(ys),min(ys)
        maxz,minz=max(zs),min(zs)
        cx,cy,cz=maxx/2+minx/2,maxy/2+miny/2,maxz/2+minz/2
        rx,ry,rz=maxx/2-minx/2,maxy/2-miny/2,maxz/2-minz/2
        r=max(rx,ry,rz)
        return r
        
    def reset_view(self):
        xs=[i[0] for i in self.pts.values()]
        ys=[i[1] for i in self.pts.values()]
        zs=[i[2] for i in self.pts.values()]
        maxx,minx=max(xs),min(xs)
        maxy,miny=max(ys),min(ys)
        maxz,minz=max(zs),min(zs)
        cx,cy,cz=maxx/2+minx/2,maxy/2+miny/2,maxz/2+minz/2
        rx,ry,rz=maxx/2-minx/2,maxy/2-miny/2,maxz/2-minz/2
        r=max(rx,ry,rz)
        self.calculate_size()
        self.plotter.show(
            *tuple(self.actors.values()),
            viewup="z", 
            axes=4,
            camera={'pos':(cx-r*5,cy-r*5,cz+r*5),'focalPoint':(cx,cy,cz)},
            resetcam=True,
            q=True,
            )

    def reset(self):
        self.plotter.show(
            *tuple(self.actors.values()),
            viewup="z", 
            axes=4,
            # camera=self.plotter.camera,
            resetcam=False,
            q=True,
            )
        
    def run(self):
        logo=Text2D("ModelViz", pos=(.05, .95), c='k', s=1)
        workpath = Text2D(self.workpath, pos=(.05, .90), c='k', s=0.5)
        time = Text2D(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pos=(.05, .875), c='k', s=0.5)
        info = Text2D('Powered by StructEngPy', pos=(.05, .85), c='k', s=0.5)
        xs=[i[0] for i in self.pts.values()]
        ys=[i[1] for i in self.pts.values()]
        zs=[i[2] for i in self.pts.values()]
        maxx,minx=max(xs),min(xs)
        maxy,miny=max(ys),min(ys)
        maxz,minz=max(zs),min(zs)
        cx,cy,cz=maxx/2+minx/2,maxy/2+miny/2,maxz/2+minz/2
        rx,ry,rz=maxx/2-minx/2,maxy/2-miny/2,maxz/2-minz/2
        r=max(rx,ry,rz)
        plt=self.plotter     
        plt.show(
            *tuple(self.actors.values()),
            logo,workpath,time,info,
            viewup="z", 
            axes=4,
            camera={'pos':(cx-r*5,cy-r*5,cz+r*5),'focalPoint':(cx,cy,cz)},
            resetcam=True,
            title="ModelViz",
            q=True,
            )
        plt.interactive().close()

    def show(self):
        logo=Text2D("ModelViz", pos=(.05, .95), c='k', s=1)
        workpath = Text2D(self.workpath, pos=(.05, .90), c='k', s=0.5)
        time = Text2D(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pos=(.05, .875), c='k', s=0.5)
        info = Text2D('Powered by StructEngPy', pos=(.05, .85), c='k', s=0.5)
        xs=[i[0] for i in self.pts.values()]
        ys=[i[1] for i in self.pts.values()]
        zs=[i[2] for i in self.pts.values()]
        maxx,minx=max(xs),min(xs)
        maxy,miny=max(ys),min(ys)
        maxz,minz=max(zs),min(zs)
        cx,cy,cz=maxx/2+minx/2,maxy/2+miny/2,maxz/2+minz/2
        rx,ry,rz=maxx/2-minx/2,maxy/2-miny/2,maxz/2-minz/2
        r=max(rx,ry,rz)
        plt=self.plotter   
        plt.show(
            *tuple(self.actors.values()),
            logo,workpath,time,info,
            viewup="z", 
            axes=4,
            camera={'pos':(cx-r*5,cy-r*5,cz+r*5),'focalPoint':(cx,cy,cz)},
            resetcam=True,
            title="ModelViz",
            mode='interactive'
            )
        
        
if __name__=="__main__":
    path=r"C:\Users\HZJ\Desktop\ghdev\analysis"
    viewer=ViewerBase(path,"assembly")
    viewer.run()


        

        