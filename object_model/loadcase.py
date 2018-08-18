# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 19:09:47 2017

@author: Dell
"""
import uuid

from .orm import LoadCase,LoadCaseStaticLinearSetting,LoadCase2ndSetting,LoadCase3ndSetting,\
LoadCaseModalSetting,LoadCaseResponseSpectrumSetting,LoadCaseTimeHistorySetting,LoadCaseBucklingSetting
import logger

def add_loadcase(self,name,case_type,weight_factor=0,**kwargs):
    """
    Add material to model, if the name already exists, an exception will be raised
    
    param:
        name: name of material.
        type: 'static-linear','2nd','3rd','modal','response-spectrum','time-history','buckling'
    return:
        boolean, status of success.
    optional:
        [weight_factor]: factor of self weight.
    **kwargs:
        if type is '1st', the following parameters are available:
            E: float, elastic modulus
            mu: float, Poisson ratio
    """
    try:
        if self.session.query(LoadCase).filter_by(name=name).first()!=None:
            raise Exception('Name already exists!')
        lc=LoadCase()
        lc.name=name
        lc.uuid=str(uuid.uuid1())
        lc.case_type=case_type
        lc.weight_factor=weight_factor
        if case_type=='static-linear':
            setting=LoadCaseStaticLinearSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='2nd':
            setting=LoadCase2ndSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='3nd':
            setting=LoadCase3ndSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='modal':
            setting=LoadCaseModalSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='response-spectrum':
            setting=LoadCaseResponseSpectrumSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='time-history':
            setting=LoadCaseTimeHistorySetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        if case_type=='buckling':
            setting=LoadCaseBucklingSetting()
            setting.loadcase_name=lc.name
            self.session.add(setting)
        self.session.add(lc)
        return lc.name
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False
    
def set_loadcase_static_linear(self):
    pass

def set_loadcase_2nd(self):
    pass

def set_loadcase_3rd(self):
    pass

def set_loadcase_modal(self,loadcase_name):
    pass

def set_loadcase_response_spectrum(self):
    pass

def set_loadcase_time_history(self):
    pass

def set_loadcase_buckling(self):
    pass

def get_loadcase_names(self):
    """
    Get all the name of loadcases in the database
    
    returns:
        boolean, status of success, and list of loadcase names if successful.
    """
    try:
        lcs=self.session.query(LoadCase)
        names=[lc.name for lc in lcs.all()]
        return names
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False

def delete_loadcase(self,name):
    try:
        lc=self.session.query(LoadCase).filter_by(name=name)
        if lc is None:
            raise Exception("Loadcase section doen't exist!")
        self.session.delete(lc)
    except Exception as e:
        log.info(str(e))
        self.session.rollback()
        return False