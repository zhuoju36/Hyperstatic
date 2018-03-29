# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 10:22:39 2018

@author: Dell
"""

from .orm import ResultPointDisplacement,ResultPointReaction,ResultFrameForce,ResultModalPeriod

def get_result_point_displacement(self,name,loadcase):
    """
    Get the result in the database.
    
    params:
        name: str, name of point
        loadcase: str, name of loadcase
    return: list of float, displacement u1,u2,u3,r1,r2,r3
    """
    res=self.session.query(ResultPointDisplacement).filter_by(point_name=name,loadcase_name=loadcase).first()
    if res==None:
        return None
    else:
        scale=self.scale()
        return [res.u1/scale['L'],res.u2/scale['L'],res.u3/scale['L'],
                res.r1,res.r2,res.r3]
        
def get_result_point_reaction(self,name,loadcase):
    """
    Get the result in the database.
    
    params:
        name: str, name of point
        loadcase: str, name of loadcase
    return: list of float, reaction in u1,u2,u3,r1,r2,r3
    """
    res=self.session.query(ResultPointReaction).filter_by(point_name=name,loadcase_name=loadcase).first()
    if res==None:
        return None
    else:
        scale=self.scale()
        return [res.p1/scale['F'],res.p2/scale['F'],res.p3/scale['F'],
                res.m1/scale['F']/scale['L'],res.m2/scale['F']/scale['L'],res.m3/scale['F']/scale['L']]
        
def get_result_frame_force(self,name,loadcase):
    """
    Get the result in the database.
    
    params:
        name: str, name of frame
        loadcase: str, name of loadcase
    return: list of float, forces in both ends.
    """
    reses=self.session.query(ResultFrameForce).filter_by(frame_name=name,loadcase_name=loadcase).all()
    if len(reses)==0:
        return None
    else:
        scale=self.scale()
        forces=[]
        for res in reses:
            forces.append([res.p01/scale['F'],res.p02/scale['F'],res.p03/scale['F'],
                           res.m01/scale['F']/scale['L'],res.m02/scale['F']/scale['L'],res.m03/scale['F']/scale['L'],
                           res.p11/scale['F'],res.p12/scale['F'],res.p13/scale['F'],
                           res.m11/scale['F']/scale['L'],res.m12/scale['F']/scale['L'],res.m13/scale['F']/scale['L']])
        return forces
    
def get_result_period(self,loadcase,order='all'):
    """
    Get the result in the database.
    
    params:
        loadcase: str, name of loadcase
        order: 'all' or int. order to find.  
    return: list of period
    """
    res=self.session.query(ResultModalPeriod).filter_by(loadcase_name=loadcase)
    if order=='all':
        return [r.period for r in res.all()]
    elif type(order)==int:
        res=res.filter_by(order=order).all()
        return [r.period for r in res.all()]