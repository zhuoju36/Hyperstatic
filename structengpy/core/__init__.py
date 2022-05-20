# -*- coding: utf-8 -*-
from structengpy.core.fe_model.assembly import Assembly
from structengpy.core.fe_model.model import Model
from structengpy.core.fe_model.load import LoadCase
from structengpy.core.fe_solver.static import StaticSolver
from structengpy.common.csys import Cartisian


class Core(object):
    def __init__(self):
        csys=Cartisian()
        assembly:Assembly

    def add_node():
        pass

    def set_nodal_restraint():
        pass

    def set_nodal_mass():
        pass

    def add_beam():
        pass

    def add_loadcase():
        pass

    def add_loadpattern():
        pass

    def add_nodal_load():
        pass

    def add_beam_concentration():
        pass

    def add_beam_distribution():
        pass

    def set_beam_release():
        pass