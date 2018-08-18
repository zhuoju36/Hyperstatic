# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 13:43:53 2018

@author: Dell
"""
from .orm import Config
import logger

def get_project_name(self):
    """
    return:
        status of success.
    """
    try:
        config=self.session.query(Config).first()
        return config.project_name
    except Exception as e:
        logger.info(str(e))
        return None 
        
def get_author(self):
    """
    return:
        status of success.
    """
    try:
        config=self.session.query(Config).first()
        return config.author
    except Exception as e:
        logger.info(str(e))
        return False 

def get_unit(self):
    """
    return:
        status of success.
    """
    try:
        config=self.session.query(Config).first()
        return config.unit
    except Exception as e:
        logger.info(str(e))
        return False 

def get_description(self):
    """
    return:
        status of success.
    """
    try:
        config=self.session.query(Config).first()
        return config.description
    except Exception as e:
        logger.info(str(e))
        return False  
    
def get_tolerance(self):
    """
    return:
        status of success.
    """
    try:
        scale=self.scale()
        config=self.session.query(Config).first()
        return config.tolerance/scale['L']
    except Exception as e:
        logger.info(str(e))
        return False  
        
def set_project_name(self,name):
    """
    params:
        name: str, project name, no more than 32 chars
    return:
        status of success.
    """
    try:
        assert(type(name)==str and len(name)<32)
        config=self.session.query(Config).first()
        config.project_name=name
        self.session.add(config)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False 
        
def set_author(self,author):
    """
    params:
        author: str, project name, no more than 32 chars
    return:
        status of success.
    """
    try:
        assert(type(author)==str and len(author)<32)
        config=self.session.query(Config).first()
        config.author=author
        self.session.add(config)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False 

def set_unit(self,unit):
    """
    params:
        unit: str, should be 'N_m_C','N_mm_C','kN_m_C' or 'kN_mm_C'
    return:
        status of success.
    """
    try:
        assert(unit in ['N_m_C','N_mm_C','kN_m_C','kN_mm_C'])
        config=self.session.query(Config).first()
        config.unit=unit
        self.session.add(config)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False 

def set_description(self,text):
    """
    params:
        text: str, description.
    return:
        status of success.
    """
    try:
        assert(type(text)==str)
        config=self.session.query(Config).first()
        config.description=text
        self.session.add(config)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False  
    
def set_tolerance(self,tol):
    """
    Set model tolerance, related to current unit configuration
    
    params:
        tol: float, tolerance.
    return:
        status of success.
    """
    try:
        assert(type(tol)==float)
        scale=self.scale()
        config=self.session.query(Config).first()
        config.tolerance=tol*scale['L']
        self.session.add(config)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False  