# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 10:09:44 2018

@author: Dell
"""

import uuid

from sqlalchemy.sql import and_

from .orm import Config,Point,Frame,FrameSection,FrameLoadDistributed,FrameLoadConcentrated,FrameLoadTemperature,FrameLoadStrain
import logger

def add_frame(self,pt0_coor,pt1_coor,section,name=None):
    """
    Add frame object to model, if the name already exists, an exception will be raised.
    
    param:
        pt0_coor: tuple, coordinate of the end point 0 in current unit.
        pt1_coor: tuple, coordinate of the end point 1 in current unit.
        [name]: str, name, optional.
    return:
        str, the new frame's name.
    """
    assert(len(pt0_coor)==3 and len(pt1_coor)==3)
    if name and self.session.query(Frame).filter_by(name=name).first()!=None:
        raise Exception('Name already exist!')
    if self.session.query(FrameSection).filter_by(name=section).first() is None:
            raise Exception("Frame section doesn't exits!")
    frm=Frame()
    scale=self.scale()
    tol=self.session.query(Config).first().tolerance
    pt0=self.session.query(Point).filter(and_(
                (Point.x-pt0_coor[0]*scale['L'])<tol,(pt0_coor[0]*scale['L']-Point.x)<tol,
                 (Point.y-pt0_coor[1]*scale['L'])<tol,(pt0_coor[1]*scale['L']-Point.y)<tol,
                  (Point.z-pt0_coor[2]*scale['L'])<tol,(pt0_coor[2]*scale['L']-Point.z)<tol)).first()
    if pt0==None:
        pt0_name=self.add_point(pt0_coor[0]*scale['L'],pt0_coor[1]*scale['L'],pt0_coor[2]*scale['L'])
    else:
        pt0_name=pt0.name
        
    pt1=self.session.query(Point).filter(and_(
                (Point.x-pt1_coor[0])<tol,(pt1_coor[0]-Point.x)<tol,
                 (Point.y-pt1_coor[1])<tol,(pt1_coor[1]-Point.y)<tol,
                  (Point.z-pt1_coor[2])<tol,(pt1_coor[2]-Point.z)<tol)).first()
    if pt1==None:
        pt1_name=self.add_point(pt1_coor[0],pt1_coor[1],pt1_coor[2])
    else:
        pt1_name=pt1.name
    
    if pt0_name<pt1_name:
        order='01'
        frm.pt0_name=pt0_name
        frm.pt1_name=pt1_name
        frm.order=order
    elif pt0_name>pt1_name:
        order='10'
        frm.pt0_name=pt1_name
        frm.pt1_name=pt0_name
        frm.order=order
    else:
        raise Exception('Two points should not be the same!')
        
    frm.section_name=section
    frm.uuid=str(uuid.uuid1())
    if name:
        frm.name=name
    else:
        frm.name=frm.uuid
    self.session.add(frm)
    return frm.name
    
def add_frame_batch(self,pt_coors,section):
    """
    Add batch of frame objects to model..
    param:
        pt_coors: list of float tuples as ((pt0.x,pt0.y,pt0.z),(pt1.x,pt1.y,pt1.z))
    return:
        status of success, and list of str, the new frame's names if successful.
    """
    try:
        assert(len(pt_coors[0][0])==len(pt_coors[0][1]))
        if self.session.query(FrameSection).filter_by(name=section).first() is None:
            raise Exception("Frame section doesn't exits!")
        names=[]
        frm_ends=[]
        scale=self.scale()
        for pt0,pt1 in pt_coors:
            pt0_name=self.add_point(pt0[0]*scale['L'],pt0[1]*scale['L'],pt0[2]*scale['L'])
            pt1_name=self.add_point(pt1[0]*scale['L'],pt1[1]*scale['L'],pt1[2]*scale['L'])
            frm_ends.append((pt0_name,pt1_name))
        tol=self.session.query(Config).first().tolerance
        pts=self.session.query(Point).order_by(Point.x,Point.y,Point.z).all()
        pt_map=dict([(pt.name,pt.name) for pt in pts])
        pts_to_rmv=[]
        for pti,ptj in zip(pts[:-1],pts[1:]):
            if (ptj.x-pti.x)**2+(ptj.y-pti.y)**2+(ptj.z-pti.z)**2<tol**2:
                pt_map[ptj.name]=pt_map[pti.name]
                pts_to_rmv.append(ptj)
        for (pt0_name,pt1_name) in frm_ends:
            frm=Frame()
            if pt_map[pt0_name]<pt_map[pt1_name]:
                frm.pt0_name=pt_map[pt0_name]
                frm.pt1_name=pt_map[pt1_name]
                frm.order='01'
            elif pt_map[pt0_name]>pt_map[pt1_name]:
                frm.pt0_name=pt_map[pt1_name]
                frm.pt1_name=pt_map[pt0_name]
                frm.order='10'
            else:
                continue
            frm.section_name=section
            frm.uuid=str(uuid.uuid1())
            frm.name=frm.uuid
            names.append(frm.name)
            self.session.add(frm)
        for pt in pts_to_rmv:
            self.session.delete(pt)
        self.session.commit()
        return True,names
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False

def set_frame_section(self,frame,section):
    """
    Assign a frame section to a frame.
    
    params:
        frame: str, name of frame.
        section: str, name of section.
    """
    try:
        frm=self.session.query(Frame).filter_by(name=frame).first()
        if frm is None:
            raise Exception("Frame doesn't exists.")
        frm.section_name=section
        self.session.add(frm)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False

def set_frame_mesh(self,frame):
    pass

def set_frame_load_distributed(self,frame,loadcase,load):
    """
    params:
        point: str, name of point.
        loadcase: str, name of loadcase. 
        load: float, list of 6 to set restraints.
    return:
        status of success.
    """
    try:
        assert len(load)==12
        frm=self.session.query(Frame).filter_by(name=frame).first()
        if frm is None:
            raise Exception("Frame doesn't exists.")
        ld=self.session.query(FrameLoadDistributed).filter_by(frame_name=frame,loadcase_name=loadcase).first()
        if ld is None:
            ld=FrameLoadDistributed()
        scale=self.scale()
        ld.frame_name=frame
        ld.loadcase_name=loadcase
        ld.p01=load[0]*scale['F']
        ld.p02=load[1]*scale['F']
        ld.p03=load[2]*scale['F']
        ld.m01=load[3]*scale['F']*scale['L']
        ld.m02=load[4]*scale['F']*scale['L']
        ld.m03=load[5]*scale['F']*scale['L']
        ld.p11=load[6]*scale['F']
        ld.p12=load[7]*scale['F']
        ld.p13=load[8]*scale['F']
        ld.m11=load[9]*scale['F']*scale['L']
        ld.m12=load[10]*scale['F']*scale['L']
        ld.m13=load[11]*scale['F']*scale['L']
        self.session.add(ld)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False
        
def set_frame_load_concentrated(self,frame,loadcase,load,loc):
    """
    params:
        point: str, name of point.
        loadcase: str, name of loadcase. 
        load: float, list of 6 to set restraints.
    return:
        status of success.
    """
    try:
        assert (len(load)==6 and (loc<=1 and loc>=0))
        frm=self.session.query(Frame).filter_by(name=frame).first()
        if frm is None:
            raise Exception("Frame doesn't exists.")
        ld=self.session.query(FrameLoadConcentrated).filter_by(frame_name=frame,loadcase_name=loadcase).first()
        if ld is None:
            ld=FrameLoadConcentrated()
        scale=self.scale()
        ld.frame_name=frame
        ld.loadcase_name=loadcase
        ld.p1=load[0]*scale['F']
        ld.p2=load[1]*scale['F']
        ld.p3=load[2]*scale['F']
        ld.m1=load[3]*scale['F']*scale['L']
        ld.m2=load[4]*scale['F']*scale['L']
        ld.m3=load[5]*scale['F']*scale['L']
        ld.loc=loc
        self.session.add(ld)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False
        
def set_frame_load_strain(self,frame,loadcase,strain):
    """
    params:
        point: str, name of point.
        loadcase: str, name of loadcase. 
        strain: float, strain in 1-1 axis.
    return:
        status of success.
    """
    try:
        assert (strain<=1 and strain>=0)
        frm=self.session.query(Frame).filter_by(name=frame).first()
        if frm is None:
            raise Exception("Frame doesn't exists.")
        ld=self.session.query(FrameLoadStrain).filter_by(frame_name=frame,loadcase_name=loadcase).first()
        if ld is None:
            ld=FrameLoadStrain()
        ld.frame_name=frame
        ld.loadcase_name=loadcase
        ld.strain=strain
        self.session.add(ld)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False
        
def set_frame_load_temperature(self,frame,loadcase,temperature):
    """
    params:
        frame: str, name of frame.
        loadcase: str, name of loadcase. 
        temperature: float, temperature in 1-1 axis.
    return:
        status of success.
    """
    try:
        frm=self.session.query(Frame).filter_by(name=frame).first()
        if frm is None:
            raise Exception("Frame doesn't exists.")
        ld=self.session.query(FrameLoadTemperature).filter_by(frame_name=frame,loadcase_name=loadcase).first()
        if ld is None:
            ld=FrameLoadTemperature()
        ld.frame_name=frame
        ld.loadcase_name=loadcase
        ld.T=temperature
        self.session.add(ld)
        return True
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False

def get_frame_names_by_points(self,pt1,pt2):
    """
    params:
        name: str
    returns:
        frame name list satisfies the points
    """
    pass

def get_frame_names(self):
    """
    Get all the name of points in the database
    
    returns:
        frame name list if successful or None if failed.
    """
    try:
        frms=self.session.query(Frame).all()
        return [frm.name for frm in frms]
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return None

def get_frame_end_names(self,frame):
    """
    params:
        frame: str, name of frame.
    return:
        two point names as frames start and end if successful or None if failed
    """
    try:
        frm=self.session.query(Frame).filter_by(name=frame).first()
        if frm is None:
            raise Exception("Frame doesn't exists.")
        return frm.pt0.name,frm.pt1.name
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return None 
        
def get_frame_end_coors(self,frame):
    """
    params:
        frame: str, name of frame.
    return:
        6-list of floats end_coors in current unit if successful or None if failed
    """
    try:
        scale=self.scale()            
        frm=self.session.query(Frame).filter_by(name=frame).first()
        if frm is None:
            raise Exception("Frame doesn't exists.")
        pt0=frm.pt0
        pt1=frm.pt1
        return [pt0.x/scale['L'],pt0.y/scale['L'],pt0.z/scale['L'],pt1.x/scale['L'],pt1.y/scale['L'],pt1.z/scale['L']]
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return None      

def get_frame_section_attribute(self,name):
    """
    params:
        name: str
    returns:
        frame section object if exist
    """
    pass

def delete_frame(self,name):
    try:
        frm=self.session.query(Frame).filter_by(name=name)
        if frm is None:
            raise Exception("Frame doen't exist!")
        self.session.delete(frm)
    except Exception as e:
        log.info(str(e))
        self.session.rollback()
        return False