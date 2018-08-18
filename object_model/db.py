# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 13:38:23 2018

@author: Dell
"""
import os,shutil
from datetime import datetime

from sqlalchemy import create_engine
import sqlalchemy.orm as o

from .orm import Base,Config
import logger

def create(self,database):
    """
    params:
        database: str. Database to be created. The path should be included
    """
    assert(database[-4:]=='.mdo')
    #initialize
    engine=create_engine('sqlite:///'+database)
    Base.metadata.create_all(engine)
    Session=o.sessionmaker(bind=engine)
    self.session=Session()
    
    #configurations
    config=Config()
    config.project_name='dev'
    config.author='HZJ'
    config.program_version='0.0.1'
    config.unit='N_m_C'
    config.create_time=datetime.now()                 
    self.session.add(config)
    self.session.commit()
    
    #default material and sections
    self.add_material('Q345',7849,'isotropic_elastic',E=2e11,mu=0.3)
    self.add_material('C35',2500,'isotropic_elastic',E=2e10,mu=0.2)
    self.add_frame_section('1-L-H400x200x14x20','Q345','I',[0.4,0.2,0.014,0.02])
    self.add_area_section('A-M120','C35','m',0.12)
    
    #default loadcase
    self.add_loadcase('S','static-linear',1.)
    self.session.commit()
    self.session.close()
    
def open(self,database):
    """
    params:
        database: str. Database to be opered. The path should be included
    """
    assert(database[-4:]=='.mdo')
    if not os.path.exists(database):
        self._create(database)
    operate_db=database[:-4]+'.op'
    shutil.copy(database,operate_db)
#        engine=create_engine('sqlite:///:memory:')
    engine=create_engine('sqlite:///'+operate_db) #should be run in memory in the future
    Session=o.sessionmaker(bind=engine)
    self.session=Session()
    self.__operate_db=operate_db
    self.__storage_db=database
    
def save(self):
    self.session.commit()
    shutil.copy(self.__operate_db,self.__storage_db)
    
def close(self):
    self.session.close()
    if os.path.exists(self.__operate_db):
        os.remove(self.__operate_db)