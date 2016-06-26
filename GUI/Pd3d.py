# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 11:25:18 2016

@author: HZJ
"""

from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.task import Task
from panda3d.core import lookAt
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import Texture, GeomNode
from panda3d.core import PerspectiveLens
from panda3d.core import CardMaker
from panda3d.core import Light, Spotlight
from panda3d.core import TextNode
from panda3d.core import LVector3
import sys
import os
import Elements

class MyTapper(DirectObject):

    def __init__(self):
        self.testTexture = loader.loadTexture("maps/envir-reeds.png")
#        self.accept("1", self.toggleTex)
#        self.accept("2", self.toggleLightsSide)
#        self.accept("3", self.toggleLightsUp)

        self.LightsOn = False
        self.LightsOn1 = False
        slight = Spotlight('slight')
        slight.setColor((1, 1, 1, 1))
        lens = PerspectiveLens()
        slight.setLens(lens)
        self.slnp = render.attachNewNode(slight)
        self.slnp1 = render.attachNewNode(slight)

    def toggleTex(self):
        global cube
        if cube.hasTexture():
            cube.setTextureOff(1)
        else:
            cube.setTexture(self.testTexture)

    def toggleLightsSide(self):
        global cube
        self.LightsOn = not self.LightsOn

        if self.LightsOn:
            render.setLight(self.slnp)
            self.slnp.setPos(cube, 10, -400, 0)
            self.slnp.lookAt(10, 0, 0)
        else:
            render.setLightOff(self.slnp)

    def toggleLightsUp(self):
        global cube
        self.LightsOn1 = not self.LightsOn1

        if self.LightsOn1:
            render.setLight(self.slnp1)
            self.slnp1.setPos(cube, 10, 0, 400)
            self.slnp1.lookAt(10, 0, 0)
        else:
            render.setLightOff(self.slnp1)


class Animator(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
 
        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)
 
        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
 
#        # Load and transform the panda actor.
#        self.pandaActor = Actor("models/panda-model",
#                                {"walk": "models/panda-walk4"})
#        self.pandaActor.setScale(0.005, 0.005, 0.005)
#        self.pandaActor.reparentTo(self.render)
#        # Loop its animation.
#        self.pandaActor.loop("walk")
 
    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont

base = ShowBase()
##base.disableMouse()
#base.camera.setPos(10, -10, 0)

h=400/100
b1=b2=200/100
tw=16/100
tf1=tf2=20/100
l=1
snode = GeomNode('square')
snode.addGeom(MakeISection(h,b1,tf1,tw,b2,tf2,l))

cube = render.attachNewNode(snode)
#cube.hprInterval(1.5, (360, 360, 360)).loop()

# OpenGl by default only draws "front faces" (polygons whose vertices are
# specified CCW).
cube.setTwoSided(True)

title = OnscreenText(text="This is the view of the structural model",
                     style=1, fg=(1, 1, 1, 1), pos=(-0.1, 0.1), scale=.07,
                     parent=base.a2dBottomRight, align=TextNode.ARight)
                     
t = MyTapper()
base.run()