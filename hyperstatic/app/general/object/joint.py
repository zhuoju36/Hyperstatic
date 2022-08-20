# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 10:14:07 2018

@author: Dell
"""
import uuid

from sqlalchemy.sql import and_

from hyperstatic.app.general.orm import Config,Joint,Frame,Area,JointLoad,JointRestraint
import logging

def add_joint(self,x,y,z):
    """
    Add joint object to model, if the name already exists, an exception will be raised.
    if a joint in same location exists, the name of the joint will be returned.
    
    param:
        x,y,z: float-like, coordinates in SI.
        [name]: str, name, optional.
    return:
        str, the new joint's name.
    """
    try:
        pt=Joint()
        pt.x=x
        pt.y=y
        pt.z=z
        pt.uuid=str(uuid.uuid1())
        pt.name=pt.uuid
        self.session.add(pt)
        return pt.name
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return False
        
def set_joint_restraint_batch(self,joints,restraints):
    """
    params:
        joint: list of str, name of joint
        restraints: bool, list of 6 to set restraints
    return:
        status of success
    """
    try:
        assert len(restraints)==6
        reses=[]
        for joint in joints:
            res=JointRestraint()
            res.joint_name=joint
            res.u1=restraints[0]
            res.u2=restraints[1]
            res.u3=restraints[2]
            res.r1=restraints[3]
            res.r2=restraints[4]
            res.r3=restraints[5]
            reses.append(res)
        self.session.add_all(reses)
        return True
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return False     
          
def set_joint_restraint(self,joint,restraints):
    """
    params:
        joint: str, name of joint
        restraints: bool, list of 6 to set restraints
    return:
        status of success
    """
    try:
        assert len(restraints)==6
        pt=self.session.query(Joint).filter_by(name=joint).first()
        if pt is None:
            raise Exception("Joint doesn't exists.")
        res=self.session.query(JointRestraint).filter_by(joint_name=joint).first()
        if res is None:
            res=JointRestraint()
            res.joint_name=joint
            res.u1=restraints[0]
            res.u2=restraints[1]
            res.u3=restraints[2]
            res.r1=restraints[3]
            res.r2=restraints[4]
            res.r3=restraints[5]
            self.session.add(res)
        elif not (restraints[0] or restraints[1] or restraints[2] or\
                    restraints[3] or restraints[4] or restraints[5]):
            self.session.delete(res)
        else:
            res.u1=restraints[0]
            res.u2=restraints[1]
            res.u3=restraints[2]
            res.r1=restraints[3]
            res.r2=restraints[4]
            res.r3=restraints[5]
            self.session.add(res)
        return True
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return False
            
def set_joint_load(self,joint,loadcase,load):
    """
    params:
        joint: str, name of joint.
        loadcase: str, name of loadcase. 
        load: float, list of 6 to set restraints.
    return:
        status of success.
    """
    try:
        assert len(load)==6
        pt=self.session.query(Joint).filter_by(name=joint).first()
        if pt is None:
            raise Exception("Joint doesn't exists.")
        ld=self.session.query(JointLoad).filter_by(joint_name=joint,loadcase_name=loadcase).first()
        if ld is None:
            ld=JointLoad()
        scale=self.scale()
        ld.joint_name=joint
        ld.loadcase_name=loadcase
        ld.p1=load[0]*scale['F']
        ld.p2=load[1]*scale['F']
        ld.p3=load[2]*scale['F']
        ld.m1=load[3]*scale['F']*scale['L']
        ld.m2=load[4]*scale['F']*scale['L']
        ld.m3=load[5]*scale['F']*scale['L']
        self.session.add(ld)
        return True
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return False
    
def set_joint_coordinate(self,name,x,y,z):
    """
    Set joint coordinate.
    if a joint in same location exists, the name of the joint will be returned.
            
    param:
        x,y,z: float-like, coordinates in current unit.
        [name]: str, name, optional.
    return:
        str, the new joint's name.
    """
    try:
        pt=self.session.query(Joint).filter_by(name=name).first()
        if pt is None:
            raise Exception("Joint doesn't exists.")
        scale=self.scale()
        pt.x=x*scale['L']
        pt.y=y*scale['L']
        pt.z=z*scale['L']
        self.session.add(pt)
        return True
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return False
        
def set_joint_mass(self,name,u1,u2,u3,r1,r2,r3):
    try:
        pt=self.session.query(Joint).filter_by(name=name).first()
        if pt is None:
            raise Exception("Joint doesn't exists.")
        scale=self.scale()
        pass
        return True
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return False
        
def set_mass_sources(self,source):
    try:
        pass
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return False
        
def get_joint_names(self):
    """
    Get all the name of joints in the database
    
    returns:
        joint list satisfies the coordiniates if successful or None if failed.
    """
    try:
        pts=self.session.query(Joint)
        names=[pt.name for pt in pts.all()]
        return names
    except Exception as e:
        logging.info(str(e))
        return None
    
def get_joint_name_by_coor(self,x=None,y=None,z=None):
    """
    Get the name of joints in the database
    
    params:
        name: str
        x,y,z: coordinates in current_unit
    returns:
        joint list satisfies the coordiniates if successful or None if failed.
    """
    try:
        tol=self.session.query(Config).first().tolerance
        pts=self.session.query(Joint)
        scale=self.scale()
        if x is not None:
            pts=pts.filter(and_((Joint.x-x*scale['L'])<tol,(x-Joint.x*scale['L'])<tol))
        if y is not None:
            pts=pts.filter(and_((Joint.y-y*scale['L'])<tol,(y-Joint.y*scale['L'])<tol))
        if z is not None:
            pts=pts.filter(and_((Joint.z-z*scale['L'])<tol,(z-Joint.z*scale['L'])<tol))
        names=[pt.name for pt in pts.all()]
        return names
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return None
        
def get_joint_coordinate(self,name):
    """
    Get joint coordinate.
            
    param:
        name: str, name, optional.
    return:
        status of success, and tuple of joint's coordinate if or None if failed.
    """
    try:
        pt=self.session.query(Joint).filter_by(name=name).first()
        if pt is None:
            raise Exception("Joint doesn't exists.")
        scale=self.scale()
        x=pt.x/scale['L']
        y=pt.y/scale['L']
        z=pt.z/scale['L']
        return x,y,z
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return None

def merge_joints(self,tol=1e-3):
    """
    merge joints within certain tolerance.
    
    params:
        tol: float, tolerance in in current unit.
    return:
        status of success.
    """
    try:
        pts=self.session.query(Joint).order_by(Joint.x,Joint.y,Joint.z).all()
        pt_map=dict([(pt.name,pt.name) for pt in pts])
        pts_to_rmv=[]
        scale=self.scale()
        for pti,ptj in zip(pts[:-1],pts[1:]):
            if (ptj.x-pti.x)**2+(ptj.y-pti.y)**2+(ptj.z-pti.z)**2<(tol*scale['L'])**2:
#                pti.joint_restraint.joint_name=ptj.name
#                pti.joint_load.joint_name=ptj.name
#                pti.joint_disp.joint_name=ptj.name
#                pti.joint_mass.joint_name=ptj.name
#                pti.joint_restraint+=ptj.joint_restraint
#                pti.joint_load+=ptj.joint_load
#                pti.joint_disp+=ptj.joint_disp
#                pti.joint_mass+=ptj.joint_mass
                pt_map[ptj.name]=pt_map[pti.name]
                pts_to_rmv.append(ptj)
                
        frames=self.session.query(Frame).all()
        areas=self.session.query(Area).all()
        logging.info(len(pts_to_rmv))
        for frm in frames:
            if (frm.pt0_name in pts_to_rmv) or (frm.pt1_name in pts_to_rmv):
                if pt_map[frm.pt0_name]<pt_map[frm.pt1_name]:
                    frm.pt0_name=pt_map[frm.pt0_name]
                    frm.pt1_name=pt_map[frm.pt1_name]
                    frm.order='01'
                    self.session.add(frm)
                elif pt_map[frm.pt0_name]>pt_map[frm.pt1_name]:
                    frm.pt0_name=pt_map[frm.pt1_name]
                    frm.pt1_name=pt_map[frm.pt0_name]
                    frm.order='10'  
                    self.session.add(frm)
                else:
                    self.session.delete(frm)
                
        for area in areas:
            area.pt0_name=pt_map[area.pt0_name]
            area.pt1_name=pt_map[area.pt1_name]
            area.pt2_name=pt_map[area.pt2_name]
            area.pt3_name=pt_map[area.pt3_name]
            self.session.add(area)       

        for pt in pts_to_rmv:
            self.session.delete(pt) 
                
        self.session.flush()
        pts=self.session.query(Joint).all()
        logging.info('merge elements %d'%len(pts))
        return True
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return False
    
def set_joint_name(self,name):
    try:
        pt=self.session.query(Joint).filter_by(name=name)
        if pt is None:
            raise Exception("Joint doen't exist!")
        pt.name=name
        self.session.add(pt)
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return False
    
def delete_joint(self,name):
    try:
        pt=self.session.query(Joint).filter_by(name=name)
        if pt is None:
            raise Exception("Joint doen't exist!")
        self.session.delete(pt)
    except Exception as e:
        logging.info(str(e))
        self.session.rollback()
        return False