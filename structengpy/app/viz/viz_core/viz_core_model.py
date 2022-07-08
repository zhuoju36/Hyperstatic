
import pickle
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
from vedo import Points, Line, Lines, Arrows, Plotter
import os

class Viewer():
    def __init__(self,workpath,filename):
        self.__workpath=workpath
        filename=os.path.join(workpath,filename)
        self.__api:Api=Api.load(workpath,filename)
        self.__pts={}
        self.__lines={}
        self.__vnodes:Points=None
        self.__vnodeNames=None
        self.__vnodeRestraints=None
        self.__vbeams={}
        self.__vbeamNames=None
        self.__vbeamReleases=None
        self.__plt=Plotter()

        self.__scale=1
        self.setup_gui()
        self.init_nodes()
        self.init_beams()

    def setup_gui(self):
        plt=self.__plt
        self.__btn_deform=plt.addButton(
            self.show_result_deformation,
            bc=("b6","r6"),
            states=("deform","reset"),
            font="san-serif",
            size=12,
        )
        self.__scale_slider=plt.addSlider2D(
            self.slide_scale,
            pos="bottom-left",
            xmin=0,
            xmax=100,
            title="scale"
        )

    def slide_scale(self,widget,event):
        self.__scale=widget.GetRepresentation().GetValue()

    def show_result_deformation(self):
        scale=self.__scale
        api=self.__api
        pts=self.__pts.copy()
        lines=self.__lines.copy()
        if self.__btn_deform.status()=="deform": 
            d=api.result_get_all_nodal_displacement("case1")
            for k,v in d.items():
                o=pts[k]
                pts[k]=(o[0]+v[0]*scale,o[1]+v[1]*scale,o[2]+v[2]*scale)
        for b in api.get_beam_names():
            s,e=api.get_beam_node_names(b)
            lines[b]=([pts[s],pts[e]])
            b:Line=self.__vbeams[b]
            b.points((pts[s],pts[e]))
        self.__vnodes.points(list(pts.values()))
        self.__btn_deform.switch()
        

    def init_nodes(self):
        api=self.__api
        pts=self.__pts
        for n in api.get_node_names():
            x,y,z=api.get_node_location(n)
            pts[n]=(x,y,z)
        self.__vnodes = Points(list(pts.values()), r=8, c="blue5")

    def init_beams(self):
        api=self.__api
        lines=self.__lines
        pts=self.__pts
        for b in api.get_beam_names():
            s,e=api.get_beam_node_names(b)
            # lines[b]=([pts[s],pts[e]])
        # self.__vbeams=Lines(list(lines.values()))
            self.__vbeams[b]=Line(pts[s],pts[e])
            


    def run(self):
        plt=self.__plt     
        plt.show(
            self.__vnodes, 
            *tuple(self.__vbeams.values()), 
            viewup="z", 
            axes=2,
            camera={'pos':(100,100,100)},
            resetcam=True)
        plt.interactive().close()





path="c:\\test"

# api=Api(path)
# api.add_node("A",0,0,0)
# api.add_node("B",6,0,0)
# api.add_node("C",12,0,0)
# api.add_node("D",18,0,0)
# E=1.999e11
# mu=0.3
# A=4.265e-3
# I3=6.572e-5
# I2=3.301e-6
# J=9.651e-8
# rho=7849.0474
# api.add_beam('b1',"A","B",E,mu,A,I2,I3,J,rho)
# api.add_beam('b2',"B","C",E,mu,A,I2,I3,J,rho)
# api.add_beam('b3',"C","D",E,mu,A,I2,I3,J,rho)
# # api.add_beam('b4',"D","A",E,mu,A,I2,I3,J,rho)



# api.add_loadpattern("pat1")
# api.set_nodal_load("pat1","D",f3=-1e4)

# api.add_static_case("case1")
# api.add_case_pattern("case1","pat1",1.0)

# api.set_nodal_restraint("case1","A",True,True,True,True,True,True)

# api.assemble()

# api.solve_static("case1")

# api.save("model")




# ###############################################

# # show model
# pts={}
# for n in api.get_node_names():
#     x,y,z=api.get_node_location(n)
#     pts[n]=(x,y,z)
# vpts = Points(list(pts.values()), r=8, c="blue5")

# lines=[]
# for b in api.get_beam_names():
#     s,e=api.get_beam_node_names(b)
#     lines.append([pts[s],pts[e]])
# vlines=Lines(lines)

# plt = Plotter()
# plt.show(vpts, vlines, viewup="z")

# plt.interactive().close()

###############################################

# show result
# pts={}
# nodeMap={}
# for n in api.get_node_names():
#     x,y,z=api.get_node_location(n)
#     nodeMap[n]=len(pts)
#     pts[n]=(x,y,z)

# d=api.result_get_all_nodal_displacement("case1")
# scale=100
# for k,v in d.items():
#     o=pts[k]
#     pts[k]=(o[0]+v[0]*scale,o[1]+v[1]*scale,o[2]+v[2]*scale)

# vpts = Points(list(pts.values), r=8, c="blue5")

# lines=[]
# for b in api.get_beam_names():
#     s,e=api.get_beam_node_names(b)
#     lines.append((pts[s],pts[e]))
# vlines=Lines(lines)

# plt = Plotter()
# plt.show(vpts, vlines, viewup="z")

# plt.interactive().close()

viewer=Viewer(path,"model")
viewer.run()
        

        