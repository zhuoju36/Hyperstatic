# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 10:48:18 2016

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



# You can't normalize inline so this is a helper function
def normalized(*args):
    myVec = LVector3(*args)
    myVec.normalize()
    return myVec

#ISection
def MakeISection(h,b1,tf1,tw,b2,tf2,l):
    """
    """
    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData('ISection', format, Geom.UHDynamic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    vertex.addData3(0,-b1/2, h/2)
    vertex.addData3(0,    0, h/2)
    vertex.addData3(0, b1/2, h/2)
    vertex.addData3(0,-b2/2,-h/2)
    vertex.addData3(0,    0,-h/2)
    vertex.addData3(0, b1/2,-h/2)
    vertex.addData3(l,-b1/2, h/2)
    vertex.addData3(l,    0, h/2)
    vertex.addData3(l, b1/2, h/2)
    vertex.addData3(l,-b2/2,-h/2)
    vertex.addData3(l,    0,-h/2)
    vertex.addData3(l, b1/2,-h/2)

    for i in range(6):
        normal.addData3(normalized(1,0,0))

    # adding different colors to the vertex for visibility
    color.addData4f(1.0, 0.0, 0.0, 1.0)
    color.addData4f(0.0, 1.0, 0.0, 1.0)
    color.addData4f(0.0, 0.0, 1.0, 1.0)
    color.addData4f(1.0, 0.0, 1.0, 1.0)
    color.addData4f(0.0, 0.0, 1.0, 1.0)
    color.addData4f(1.0, 0.0, 1.0, 1.0)
    color.addData4f(1.0, 0.0, 0.0, 1.0)
    color.addData4f(0.0, 1.0, 0.0, 1.0)
    color.addData4f(0.0, 0.0, 1.0, 1.0)
    color.addData4f(1.0, 0.0, 1.0, 1.0)
    color.addData4f(0.0, 0.0, 1.0, 1.0)
    color.addData4f(1.0, 0.0, 1.0, 1.0)

    for i in range(6):
        texcoord.addData2f(1.0, 0.0)

    # Quads aren't directly supported by the Geom interface
    # you might be interested in the CardMaker class if you are
    # interested in rectangle though
    tris = GeomTriangles(Geom.UHDynamic)
    tris.addVertices(0, 7, 6)
    tris.addVertices(0, 1, 7)
    tris.addVertices(1, 8, 7)
    tris.addVertices(1, 2, 8)
    tris.addVertices(3,10, 9)
    tris.addVertices(3, 4,10)
    tris.addVertices(4, 5,11)
    tris.addVertices(4,11,10)
    tris.addVertices(1, 4,10)
    tris.addVertices(1,10, 7)

    ISecion = Geom(vdata)
    ISecion.addPrimitive(tris)
    return ISecion