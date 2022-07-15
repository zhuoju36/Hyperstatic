
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
from vedo import Points, Line, Lines, Arrows, Plotter, Cone,Text2D
from vedo.pyplot import histogram
import os

class Viewer():
    def __init__(self,workpath,filename):
        self.__workpath=workpath
        filename=os.path.join(workpath,filename)
        self.__api:Api=Api.load(workpath,filename)
        self.__pts={}
        self.__lines={}
        self.__vnodes:Points=None
        self.__vnodeload:Arrows=None
        self.__vnodeNames=None
        self.__vnode_restraints=[]
        self.__vbeams:Lines=None
        self.__vbeamNames=None
        self.__vbeamReleases=None
        self.__plt=Plotter()

        self.setup_gui()
        self.init_nodes()
        self.__scale=self.__scene_radius()
        self.init_nodal_load()
        self.init_beams()

    def setup_gui(self):
        plt=self.__plt
        self.__btn_node=plt.addButton(
            self.toggle_node,
            bc=("b6","r6"),
            pos=(0.6,0.05),
            states=("show_node","hide_node"),
            font="san-serif",
            size=12,
        )
        self.__btn_nodal_load=plt.addButton(
            self.toggle_nodal_load,
            bc=("b6","r6"),
            pos=(0.85,0.05),
            states=("show_nodal_load","hide_nodal_load"),
            font="san-serif",
            size=12,
        )
        
        # self.__scale_slider=plt.addSlider2D(
        #     self.slide_scale,
        #     # pos="bottom-left",
        #     pos=[(0.65,0.15),(0.95,0.15)],
        #     # titleSize=0.5,
        #     xmin=0,
        #     xmax=100,
        #     title="label scale"
        # )

    def slide_scale(self,widget,event):
        self.__scale=widget.GetRepresentation().GetValue()

    def toggle_node(self):
        if self.__btn_node.status()=="hide_node":
            self.__vnodes.off()
        else:
            self.__vnodes.on()
        self.__btn_node.switch()    


    def toggle_node_name(self):
        self.reset()

    def toggle_node_csys(self):
        self.reset()

    def toggle_nodal_load(self):
        if self.__btn_nodal_load.status()=="hide_nodal_load":
            self.__vnodeload.off()
            self.__vnodeload.scalarbar.VisibilityOff()
        else:
            self.__vnodeload.on()
            self.__vnodeload.scalarbar.VisibilityOn()
        self.__btn_nodal_load.switch() 

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

    def init_nodes(self):
        api=self.__api
        pts=self.__pts
        for n in api.get_node_names():
            x,y,z=api.get_node_location(n)
            pts[n]=(x,y,z)
        
        self.__vnodes = Points(list(pts.values()), r=8, c="blue5")
        self.__vnodes.off()
        # self.__vnodeload=Arrows(arrow_starts,arrow_ends,s=0.5,res=3)
        # #"jet", "PuOr", "viridis"
        # self.__vnodeload.cmap('PuOr', f_value).addScalarBar(title="Nodal load(N)",pos=(0.8,0.5))
        # self.__vnodeload.off()
        # self.__vnodeload.scalarbar.VisibilityOff()

    def init_nodal_load(self):
        api=self.__api
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
        scale=self.__scale/max(f_scals)*0.1
        for e,l in zip(arrow_ends,loads):
            arrow_starts.append((e[0]-l[0]*scale,e[1]-l[1]*scale,e[2]-l[2]*scale))

        self.__vnodeload=Arrows(arrow_starts,arrow_ends,s=0.5,res=3)
        self.__vnodeload.cmap('viridis', f_value).addScalarBar(title="Nodal load(N)",pos=(0.8,0.4)) #"jet", "PuOr", "viridis"
        self.__vnodeload.off()
        self.__vnodeload.scalarbar.VisibilityOff()

    def __scene_radius(self):
        xs=[i[0] for i in self.__pts.values()]
        ys=[i[1] for i in self.__pts.values()]
        zs=[i[2] for i in self.__pts.values()]
        maxx,minx=max(xs),min(xs)
        maxy,miny=max(ys),min(ys)
        maxz,minz=max(zs),min(zs)
        cx,cy,cz=maxx/2+minx/2,maxy/2+miny/2,maxz/2+minz/2
        rx,ry,rz=maxx/2-minx/2,maxy/2-miny/2,maxz/2-minz/2
        r=max(rx,ry,rz)
        return r

    def init_beams(self):
        api=self.__api
        lines=self.__lines
        pts=self.__pts
        for b in api.get_beam_names():
            s,e=api.get_beam_node_names(b)
            lines[b]=([pts[s],pts[e]])
        self.__vbeams=Lines(list(lines.values()),c='k')
    
    def reset_view(self):
        xs=[i[0] for i in self.__pts.values()]
        ys=[i[1] for i in self.__pts.values()]
        zs=[i[2] for i in self.__pts.values()]
        maxx,minx=max(xs),min(xs)
        maxy,miny=max(ys),min(ys)
        maxz,minz=max(zs),min(zs)
        cx,cy,cz=maxx/2+minx/2,maxy/2+miny/2,maxz/2+minz/2
        rx,ry,rz=maxx/2-minx/2,maxy/2-miny/2,maxz/2-minz/2
        r=max(rx,ry,rz)
        self.__calculate_size()
        self.__plt.show(
            self.__vnodes, 
            self.__vbeams, 
            *tuple(self.__vnode_restraints),
            viewup="z", 
            axes=4,
            camera={'pos':(cx-r*5,cy-r*5,cz+r*5),'focalPoint':(cx,cy,cz)},
            resetcam=True)

    def reset(self):
        self.__plt.show(
            self.__vnodes, 
            self.__vbeams, 
            *tuple(self.__vnode_restraints),
            viewup="z", 
            axes=4,
            # camera=self.__plt.camera,
            resetcam=False)
        

    def run(self):
        logo=Text2D("ModelViz", pos=(.05, .95), c='k', s=1)
        workpath = Text2D(self.__workpath, pos=(.05, .90), c='k', s=0.5)
        time = Text2D(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pos=(.05, .875), c='k', s=0.5)
        info = Text2D('Powered by StructEngPy', pos=(.05, .85), c='k', s=0.5)
        xs=[i[0] for i in self.__pts.values()]
        ys=[i[1] for i in self.__pts.values()]
        zs=[i[2] for i in self.__pts.values()]
        maxx,minx=max(xs),min(xs)
        maxy,miny=max(ys),min(ys)
        maxz,minz=max(zs),min(zs)
        cx,cy,cz=maxx/2+minx/2,maxy/2+miny/2,maxz/2+minz/2
        rx,ry,rz=maxx/2-minx/2,maxy/2-miny/2,maxz/2-minz/2
        r=max(rx,ry,rz)
        plt=self.__plt     
        plt.show(
            self.__vnodes, 
            self.__vnodeload,
            self.__vbeams, 
            *tuple(self.__vnode_restraints),
            logo,workpath,time,info,
            viewup="z", 
            axes=4,
            camera={'pos':(cx-r*5,cy-r*5,cz+r*5),'focalPoint':(cx,cy,cz)},
            resetcam=True,
            title="ModelViz",
            )
        plt.interactive().close()
        


if __name__=="__main__":
    path=r"G:\testghsep"
    viewer=Viewer(path,"assembly")
    viewer.run()

#     path="c:\\test"


#     # ## a simple frame building
#     # api=Api(path)
#     # api.add_node("A1",0,0,0)
#     # api.add_node("B1",6,0,0)
#     # api.add_node("C1",6,6,0)
#     # api.add_node("D1",0,6,0)
#     # api.add_node("A2",0,0,4)
#     # api.add_node("B2",6,0,4)
#     # api.add_node("C2",6,6,4)
#     # api.add_node("D2",0,6,4)
#     # api.add_node("A3",0,0,8)
#     # api.add_node("B3",6,0,8)
#     # api.add_node("C3",6,6,8)
#     # api.add_node("D3",0,6,8)
#     # E=1.999e11
#     # mu=0.3
#     # A=4.265e-3
#     # I3=6.572e-5
#     # I2=3.301e-6
#     # J=9.651e-8
#     # rho=7849.0474
#     # api.add_simple_beam('b11',"A2","B2",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('b12',"B2","C2",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('b13',"C2","D2",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('b14',"D2","A2",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('b21',"A3","B3",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('b22',"B3","C3",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('b23',"C3","D3",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('b24',"D3","A3",E,mu,A,I2,I3,J,rho)

#     # api.add_simple_beam('c11',"A1","A2",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('c12',"B1","B2",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('c13',"C1","C2",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('c14',"D1","D2",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('c21',"A2","A3",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('c22',"B2","B3",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('c23',"C2","C3",E,mu,A,I2,I3,J,rho)
#     # api.add_simple_beam('c24',"D2","D3",E,mu,A,I2,I3,J,rho)

#     # api.add_loadpattern("pat1")
#     # api.set_nodal_load("pat1","D3",f2=-1e4)

#     # api.add_static_case("case1")
#     # api.add_case_pattern("case1","pat1",1.0)

#     # api.set_nodal_restraint("case1","A1",True,True,True,True,True,True)
#     # api.set_nodal_restraint("case1","B1",True,True,True,True,True,True)
#     # api.set_nodal_restraint("case1","C1",True,True,True,True,True,True)
#     # api.set_nodal_restraint("case1","D1",True,True,True,True,True,True)

#     # api.assemble()

#     # api.solve_static("case1")

#     # api.save("model")

#     ########show model
#     viewer=Viewer(path,"model")
#     viewer.run()




# # ###############################################

# # pts={}
# # for n in api.get_node_names():
# #     x,y,z=api.get_node_location(n)
# #     pts[n]=(x,y,z)
# # vpts = Points(list(pts.values()), r=8, c="blue5")

# # lines=[]
# # for b in api.get_beam_names():
# #     s,e=api.get_beam_node_names(b)
# #     lines.append([pts[s],pts[e]])
# # vlines=Lines(lines)

# # plt = Plotter()
# # plt.show(vpts, vlines, viewup="z")

# # plt.interactive().close()

# ###############################################

# # show result
# # pts={}
# # nodeMap={}
# # for n in api.get_node_names():
# #     x,y,z=api.get_node_location(n)
# #     nodeMap[n]=len(pts)
# #     pts[n]=(x,y,z)

# # d=api.result_get_all_nodal_displacement("case1")
# # scale=100
# # for k,v in d.items():
# #     o=pts[k]
# #     pts[k]=(o[0]+v[0]*scale,o[1]+v[1]*scale,o[2]+v[2]*scale)

# # vpts = Points(list(pts.values), r=8, c="blue5")

# # lines=[]
# # for b in api.get_beam_names():
# #     s,e=api.get_beam_node_names(b)
# #     lines.append((pts[s],pts[e]))
# # vlines=Lines(lines)

# # plt = Plotter()
# # plt.show(vpts, vlines, viewup="z")

# # plt.interactive().close()


        

        