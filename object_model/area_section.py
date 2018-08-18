# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:32:16 2016

@author: HZJ
"""
import uuid

from .orm import AreaSection
import logger

def add_area_section(self,name,material,type,t):
    """
    Add area section to model, if the name already exists, an exception will be raised.
    
    param:
        name: str. name of the section.
        material: str, name of material.
        type:
            'm':membrane,
            'p':plate
            's':shell
            'n':none
        t: thickness of area in current unit.
    return:
        boolean, status of success.
    """
    try:
        assert(type in 'mpsn' and len(type)==1)
        scale=self.scale()
        if self.session.query(AreaSection).filter_by(name=name).first()!=None:
            raise Exception('Name already exists!')
        areasec=AreaSection()
        areasec.name=name
        areasec.uuid=str(uuid.uuid1())
        areasec.material_name=material
        areasec.type=type
        areasec.t=t*scale['L']
        self.session.add(areasec)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False
        
def add_area_section_layered(self,name):
    pass

def get_area_section_names(self):
    """
    Get all the name of area sections in the database
    
    returns:
        str list of area names
    """
    try:
        sections=self.session.query(AreaSection)
        names=[i.name for i in sections.all()]
        return names
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False
    
def delete_area_section(self,name):
    try:
        sec=self.session.query(AreaSection).filter_by(name=name)
        if sec is None:
            raise Exception("Area section doen't exist!")
        self.session.delete(sec)
    except Exception as e:
        log.info(str(e))
        self.session.rollback()
        return False