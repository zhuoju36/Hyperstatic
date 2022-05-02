# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 10:09:59 2018

@author: Dell
"""

import uuid

from sqlalchemy.sql import and_

from .orm import Config, AreaSection, Point, Area
import logger

def add_area(self,pt0_coor,pt1_coor,pt2_coor,pt3_coor,section,name=None):
    """
    Add area object to model, if the name already exists, an exception will be raised.
    param:
        pt0_coor: tuple, coordinate of the end point 0.
        pt1_coor: tuple, coordinate of the end point 1.
        pt2_coor: tuple, coordinate of the end point 2.
        pt3_coor: tuple, coordinate of the end point 3. if the area is a triagle, set it be None
        [name]: str, name, optional.
    return:
        str, the new area's name.
    """
    try:
        assert(len(pt0_coor)==3 and len(pt1_coor)==3 and len(pt2_coor)==3)
        if name and self.session.query(Area).filter_by(name=name).first()!=None:
            raise Exception('Name already exist!')
        if self.session.query(AreaSection).filter_by(name=section).first() is None:
            raise Exception("Area section doesn't exits!")
        area=Area()
        scale=self.scale()
        tol=self.session.query(Config).first().tolerance
        
        pt0=self.session.query(Point).filter(and_(
                    (Point.x-pt0_coor[0]*scale['L'])<tol,(pt0_coor[0]*scale['L']-Point.x)<tol,
                     (Point.y-pt0_coor[1]*scale['L'])<tol,(pt0_coor[1]*scale['L']-Point.y)<tol,
                      (Point.z-pt0_coor[2]*scale['L'])<tol,(pt0_coor[2]*scale['L']-Point.z)<tol)).first()
        if pt0==None:
            pt0_name=self._add_point(pt0_coor[0],pt0_coor[1],pt0_coor[2])
        else:
            pt0_name=pt0.name
            
        pt1=self.session.query(Point).filter(and_(
                    (Point.x-pt1_coor[0]*scale['L'])<tol,(pt1_coor[0]*scale['L']-Point.x)<tol,
                     (Point.y-pt1_coor[1]*scale['L'])<tol,(pt1_coor[1]*scale['L']-Point.y)<tol,
                      (Point.z-pt1_coor[2]*scale['L'])<tol,(pt1_coor[2]*scale['L']-Point.z)<tol)).first()
        if pt1==None:
            pt1_name=self._add_point(pt1_coor[0],pt1_coor[1],pt1_coor[2])
        else:
            pt1_name=pt1.name
            
        pt2=self.session.query(Point).filter(and_(
                    (Point.x-pt2_coor[0]*scale['L'])<tol,(pt2_coor[0]*scale['L']-Point.x)<tol,
                     (Point.y-pt2_coor[1]*scale['L'])<tol,(pt2_coor[1]*scale['L']-Point.y)<tol,
                      (Point.z-pt2_coor[2]*scale['L'])<tol,(pt2_coor[2]*scale['L']-Point.z)<tol)).first()
        if pt2==None:
            pt2_name=self._add_point(pt2_coor[0],pt2_coor[1],pt2_coor[2])
        else:
            pt2_name=pt2.name
            
        if pt3_coor is not None: 
            pt3=self.session.query(Point).filter(and_(
                    (Point.x-pt2_coor[0]*scale['L'])<tol,(pt2_coor[0]*scale['L']-Point.x)<tol,
                     (Point.y-pt2_coor[1]*scale['L'])<tol,(pt2_coor[1]*scale['L']-Point.y)<tol,
                      (Point.z-pt2_coor[2]*scale['L'])<tol,(pt2_coor[2]*scale['L']-Point.z)<tol)).first()

            pt3=self.session.query(Point).filter(and_(
                        (Point.x-pt3_coor[0]*scale['L'])<tol,(pt3_coor[0]*scale['L']-Point.x)<tol,
                         (Point.y-pt3_coor[1]*scale['L'])<tol,(pt3_coor[1]*scale['L']-Point.y)<tol,
                          (Point.z-pt3_coor[2]*scale['L'])<tol,(pt3_coor[2]*scale['L']-Point.z)<tol)).first()
            if pt3==None:
                pt3_name=self._add_point(pt0_coor[0],pt0_coor[1],pt0_coor[2])
            else:
                pt3_name=pt0.name
        
        if pt3_coor is not None:
            name_dict={pt0_name:'0',pt1_name:'1',pt2_name:'2',pt3_name:'3'}
            sorted_key=sorted(list(name_dict))
            area.pt0_name=name_dict[sorted_key[0]]
            area.pt1_name=name_dict[sorted_key[1]]
            area.pt2_name=name_dict[sorted_key[2]]
            area.pt3_name=name_dict[sorted_key[3]]
            area.order=str.join(sorted_key)
        else:
            name_dict={pt0_name:'0',pt1_name:'1',pt2_name:'2'}
            sorted_key=sorted(list(name_dict))
            area.pt0_name=name_dict[sorted_key[0]]
            area.pt1_name=name_dict[sorted_key[1]]
            area.pt2_name=name_dict[sorted_key[2]]
            area.order=str.join(sorted_key)
            
        area.section_name=section
        area.uuid=str(uuid.uuid1())
        if name:
            area.name=name
        else:
            area.name=area.uuid
        self.session.add(area)
        return area.name
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False
        
def add_area_batch(self,pt_coors,section):
    """
    Add batch of frame objects to model..
    param:
        pt_coors: list of float tuples as ((pt0.x,pt0.y,pt0.z),(pt1.x,pt1.y,pt1.z),(pt2.x,pt2.y,pt2.z),(pt3.x,pt3.y,pt3.z) or None)
    return:
        list of str, the new frame's names.
    """
    try:
        assert(len(pt_coors[0][0])==len(pt_coors[0][1]))
        if self.session.query(AreaSection).filter_by(name=section).first() is None:
            raise Exception("Area section doesn't exits!")
        names=[]
        area_ends=[]
        scale=self.scale()
        for pt0,pt1,pt2,pt3 in pt_coors:
            pt0_name=self._add_point(pt0[0]*scale['L'],pt0[1]*scale['L'],pt0[2]*scale['L'])
            pt1_name=self._add_point(pt1[0]*scale['L'],pt1[1]*scale['L'],pt1[2]*scale['L'])
            pt2_name=self._add_point(pt2[0]*scale['L'],pt2[1]*scale['L'],pt2[2]*scale['L'])
            if pt3 is not None:
                pt3_name=self._add_point(pt2[0]*scale['L'],pt2[1]*scale['L'],pt2[2]*scale['L'])
                area_ends.append((pt0_name,pt1_name,pt2_name,pt3_name))
            else:
                area_ends.append((pt0_name,pt1_name,pt2_name,None))
        tol=self.session.query(Config).first().tolerance
        pts=self.session.query(Point).order_by(Point.x,Point.y,Point.z).all()
        pt_map=dict([(pt.name,pt.name) for pt in pts])
        pts_to_rmv=[]
        for pti,ptj in zip(pts[:-1],pts[1:]):
            if (ptj.x-pti.x)**2+(ptj.y-pti.y)**2+(ptj.z-pti.z)**2<tol**2:
                pt_map[ptj.name]=pt_map[pti.name]
                pts_to_rmv.append(ptj)
        for (pt0_name,pt1_name,pt2_name,pt3_name) in area_ends:
            area=Area()
            if pt3_name is not None:
                name_dict={pt0_name:'0',pt1_name:'1',pt2_name:'2',pt3_name:'3'}
                sorted_key=sorted(list(name_dict))
                area.pt0_name=name_dict[sorted_key[0]]
                area.pt1_name=name_dict[sorted_key[1]]
                area.pt2_name=name_dict[sorted_key[2]]
                area.pt3_name=name_dict[sorted_key[3]]
                area.order=sorted_key[0]+sorted_key[1]+sorted_key[2]+sorted_key[3]
            else:
                name_dict={pt0_name:'0',pt1_name:'1',pt2_name:'2'}
                sorted_key=sorted(list(name_dict))
                area.pt0_name=name_dict[sorted_key[0]]
                area.pt1_name=name_dict[sorted_key[1]]
                area.pt2_name=name_dict[sorted_key[2]]
                area.order=sorted_key[0]+sorted_key[1]+sorted_key[2]
            area.section_name=section
            area.uuid=str(uuid.uuid1())
            area.name=area.uuid
            names.append(area.name)
        for pt in pts_to_rmv:
            self.session.delete(pt)
        self.session.commit()
        return True, names
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False
        
def get_area_names(self):
    """
    Get all the name of points in the database
    
    returns:
        frame name list.
    """
    try:
        areas=self.session.query(Area).all()
        return [area.name for area in areas]
    except Exception as e:
        logger.info(str(e))
        self.session.rollback()
        return False
    
def delete_area(self,name):
    try:
        area=self.session.query(Area).filter_by(name=name)
        if area is None:
            raise Exception("Area section doen't exist!")
        self.session.delete(area)
    except Exception as e:
        log.info(str(e))
        self.session.rollback()
        return False