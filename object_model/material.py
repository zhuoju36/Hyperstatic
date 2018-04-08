# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:30:59 2016

@author: HZJ
"""
import uuid

from .orm import Material,IsotropicElastic
from .. import logger

def add_material(self,name,rho,mat_type,**kwargs):
    """
    Add material to model, if the name already exists, an exception will be raised

    param:
        name: str, name of material.
        gamma: float, density in current unit.
        mat_type: str, 'isotropic_elastic','...'
    **kwargs:
        if type is 'isoelastic', the following parameters are available:
        E: float, elastic modulus in current unit
        mu: float, Poisson ratio in current unit
    return:
        boolean, status of success.
    """
    try:
        if self.session.query(Material).filter_by(name=name).first()!=None:
            raise Exception('Name already exists!')
        scale=self.scale()
        mat=Material()
        mat.name=name
        mat.uuid=str(uuid.uuid1())
        mat.rho=rho*(scale['F']*scale['L']**-4)
        mat.type=mat_type
        if mat_type=='isotropic_elastic':
            iso_elastic=IsotropicElastic()
            iso_elastic.material_name=mat.name
            iso_elastic.E=kwargs['E']*(scale['F']*scale['L']**-2)
            iso_elastic.mu=kwargs['mu']
            self.session.add(iso_elastic)
        self.session.add(mat)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False

def add_material_quick(self,code):
    try:
        pass
    except Exception as e:
        log.info(str(e))
        self.session.rollback()
        return False

def set_material_isotropic_elastic(self,name,E,mu):
    try:
        pass
    except Exception as e:
        log.info(str(e))
        self.session.rollback()
        return False

def get_material_names(self):
    try:
        materials=self.session.query(Material).all()
        return [m.name for m in materials]
    except Exception as e:
        log.info(str(e))
        self.session.rollback()
        return False

def set_material_name(self,name):
    try:
        material=self.session.query(Material).filter_by(name=name).first()
        if material is None:
            raise Exception("Material name doen't exist!")
        material.name=name
        self.session.add(material)
    except Exception as e:
        log.info(str(e))
        self.session.rollback()
        return False

def delete_material(self,name):
    try:
        material=self.session.query(Material).filter_by(name=name).first()
        if material is None:
            raise Exception("Material name doen't exist!")
        self.session.delete(material)
    except Exception as e:
        log.info(str(e))
        self.session.rollback()
        return False
        
    