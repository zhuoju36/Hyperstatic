# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 19:52:26 2018

@author: HZJ
@E-mail: zhuoju36@hotmail.com
"""
import os
import shutil
import time
import uuid

from sqlalchemy import create_engine
import sqlalchemy.orm as o
from sqlalchemy.sql import and_,or_
import ezdxf

from datetime import datetime

from .orm import *

from object_model.frame_section import Pipe,Circle,HollowBox,ISection

from fe_model import Model as FEModel

from fe_solver.static import solve_linear
from fe_solver.dynamic import solve_modal

import logger as log

class Model():
    def __init__(self):
        self.locked=False
        self.fe_model=FEModel()

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
        self.add_frame_section('1-L-H400x200x14x20','Q345B','I',[0.4,0.2,0.014,0.02])
        
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
            self.create(database)
        operate_db=database[:-4]+'.op'
        shutil.copy(database,operate_db)
        engine=create_engine('sqlite:///'+operate_db) #should be run in memory in the future
        Session=o.sessionmaker(bind=engine)
        self.session=Session()
        self.__operate_db=operate_db
        self.__storage_db=database
        
        
    def scale(self):
        """
        returns the scale factor of current model.
        """
        config=self.session.query(Config).first()
        scale={}
        if config.unit=='N_m_C':
            scale['F']=1
            scale['L']=1
            scale['T']=1
        elif config.unit=='N_mm_C':
            scale['F']=1
            scale['L']=1e-3
            scale['T']=1
        elif config.unit=='kN_m_C':
            scale['F']=1e3
            scale['L']=1
            scale['T']=1
        elif config.unit=='kN_mm_C':
            scale['F']=1e3
            scale['L']=1e-3
            scale['T']=1        
        return scale
        
    def save(self):
        self.session.commit()
        shutil.copy(self.__operate_db,self.__storage_db)
        
    def close(self):
        self.session.close()
        if os.path.exists(self.__operate_db):
            os.remove(self.__operate_db)
            
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
            log.info(e)
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
            log.info(e)
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
            log.info(e)
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
            config.description=description
            self.session.add(config)
            return True
        except Exception as e:
            log.info(e)
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
            log.info(e)
            return False  
        
            
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
            log.info(e)
            return False
    
    def add_material_quick(self,code):
        pass
    
    def set_material_isotropic_elastic(self,name,E,mu):
        pass
        
    
    def add_frame_section(self,name,material,type,size):
        """
        Add frame section to model, if the name already exists, an exception will be raised.
        
        param:
            name: str. name of the section.
            material: str, name of material.
            type:
                'O':pipe,
                'o':circle
                'I':I-profile
                'B':hollow-box
                'L':angle
                'T':T-profile
                'C':C-profile
                'Z':Z-profile
            size:
            if type is 'O', the following parameters are available:
                d: float, diameter in current unit
                t: float, wall thickness in current unit
            if type is 'o', the following parameters are available:
                d: float, diameter in current unit
            if type is 'I', the following parameters are available:
                h,b,tw,tf: float in current unit
            if type is 'B', the following parameters are available:
                h,b,tw,tf: float in current unit
            if type is 'L', the following parameters are available:
                h,b,tw,tf: float in current unit
            if type is 'T', the following parameters are available:
                h,b,tw,tf: float in current unit
            if type is 'C', the following parameters are available:
                h,b,tw,tf: float in current unit
            if type is 'Z', the following parameters are available:
                h,b,tw,tf: float in current unit
        return:
            boolean, status of success.
        """
        try:
            assert(type in 'OoIBLTCZ' and len(type)==1)
            scale=self.scale()
            if self.session.query(FrameSection).filter_by(name=name).first()!=None:
                raise Exception('Name already exists!')
            frmsec=FrameSection()
            frmsec.name=name
            frmsec.uuid=str(uuid.uuid1())
            frmsec.material_name=material
            frmsec.type=type
            sec=None
            if type=='o':
                assert len(size)==1
                frmsec.size_0=size[0]*scale['L']
                sec=Circle(None,frmsec.size_0)
            elif type=='O':
                assert len(size)==2
                frmsec.size_0=size[0]*scale['L']
                frmsec.size_1=size[1]*scale['L']
                sec=Pipe(None,frmsec.size_0,frmsec.size_1)
            elif type=='I':
                assert len(size)==4
                frmsec.size_0=size[0]*scale['L']
                frmsec.size_1=size[1]*scale['L']
                frmsec.size_2=size[0]*scale['L']
                frmsec.size_3=size[1]*scale['L']
                sec=ISection(None,frmsec.size_0,frmsec.size_1,frmsec.size_2,frmsec.size_3)
            elif type=='L':####should be refined!!
                assert len(size)==4
                frmsec.size_0=size[0]*scale['L']
                frmsec.size_1=size[1]*scale['L']
                frmsec.size_2=size[0]*scale['L']
                frmsec.size_3=size[1]*scale['L']
                sec=HollowBox(None,frmsec.size_0,frmsec.size_1,frmsec.size_2,frmsec.size_3)
            frmsec.A=sec.A
            frmsec.J=sec.J
    #        frmsec.S2=sec.S2
    #        frmsec.S3=sec.S3
            frmsec.I2=sec.I22
            frmsec.I3=sec.I33
            self.session.add(frmsec)
            return True  
        except Exception as e:
            log.info(str(e))
            return False
            
    def add_frame_section_SD(self):
        pass
    
    def add_frame_section_variate(self):
        pass
    
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
            if self.session.query(AeraSection).filter_by(name=name).first()!=None:
                raise Exception('Name already exists!')
            areasec=AreaSection()
            areasec.name=name
            areasec.uuid=str(uuid.uuid1())
            areasec.material_name=material
            areasec.type=type
            areasec.t=t*scale['L']
            return True
        except Exception as e:
            log.info(str(e))
            return False
            
    def add_area_section_layered(self,name):
        pass
    
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
            log.info(str(e))
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

    def __add_point(self,x,y,z):
        """
        Add point object to model, if the name already exists, an exception will be raised.
        if a point in same location exists, the name of the point will be returned.
        
        param:
            x,y,z: float-like, coordinates in SI.
            [name]: str, name, optional.
        return:
            str, the new point's name.
        """
        try:
            pt=Point()
            pt.x=x
            pt.y=y
            pt.z=z
            pt.uuid=str(uuid.uuid1())
            pt.name=pt.uuid
            self.session.add(pt)
            return pt.name
        except Exception as e:
            log.info(e)
            return False
            
    def set_point_restraint_batch(self,points,restraints):
        """
        params:
            point: list of str, name of point
            restraints: bool, list of 6 to set restraints
        return:
            status of success
        """
        try:
            assert len(restraints)==6
            reses=[]
            for point in points:
                res=PointRestraint()
                res.point_name=point
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
            log.info(e)
            return False     
              
    def set_point_restraint(self,point,restraints):
        """
        params:
            point: str, name of point
            restraints: bool, list of 6 to set restraints
        return:
            status of success
        """
        try:
            assert len(restraints)==6
            pt=self.session.query(Point).filter_by(name=point).first()
            if pt is None:
                raise Exception("Point doesn't exists.")
            res=self.session.query(PointRestraint).filter_by(point_name=point).first()
            if res is None:
                res=PointRestraint()
                res.point_name=point
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
            log.info(str(e))
            return False
                
    def set_point_load(self,point,loadcase,load):
        """
        params:
            point: str, name of point.
            loadcase: str, name of loadcase. 
            load: float, list of 6 to set restraints.
        return:
            status of success.
        """
        try:
            assert len(load)==6
            pt=self.session.query(Point).filter_by(name=point).first()
            if pt is None:
                raise Exception("Point doesn't exists.")
            ld=self.session.query(PointLoad).filter_by(point_name=point,loadcase_name=loadcase).first()
            if ld is None:
                ld=PointLoad()
            scale=self.scale()
            ld.point_name=point
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
            log.info(str(e))
            return False
        
    def set_point_coordinate(self,name,x,y,z):
        """
        Set point coordinate.
        if a point in same location exists, the name of the point will be returned.
                
        param:
            x,y,z: float-like, coordinates in current unit.
            [name]: str, name, optional.
        return:
            str, the new point's name.
        """
        try:
            pt=self.session.query(Point).filter_by(name=name).first()
            if pt is None:
                raise Exception("Point doesn't exists.")
            scale=self.scale()
            pt.x=x*scale['L']
            pt.y=y*scale['L']
            pt.z=z*scale['L']
            self.session.add(pt)
            return True
        except Exception as e:
            log.info(str(e))
            return False
            
    def set_point_mass(self,name,u1,u2,u3,r1,r2,r3):
        try:
            pt=self.session.query(Point).filter_by(name=name).first()
            if pt is None:
                raise Exception("Point doesn't exists.")
            scale=self.scale()
            pass
            return True
        except Exception as e:
            log.info(str(e))
            return False
            
    def set_mass_sources(self,source):
        try:
            pass
        except Exception as e:
            log.info(str(e))
            return False
            
    def get_point_names(self):
        """
        Get all the name of points in the database
        
        returns:
            point list satisfies the coordiniates
        """
        try:
            pts=self.session.query(Point)
            names=[pt.name for pt in pts.all()]
            return names
        except Exception as e:
            log.info(str(e))
            return False
        
    def get_point_name_by_coor(self,x=None,y=None,z=None):
        """
        Get the name of points in the database
        
        params:
            name: str
            x,y,z: coordinates
        returns:
            point list satisfies the coordiniates
        """
        try:
            tol=self.session.query(Config).first().tolerance
            pts=self.session.query(Point)
            scale=self.scale()
            if x is not None:
                pts=pts.filter(and_((Point.x-x*scale['L'])<tol,(x-Point.x*scale['L'])<tol))
            if y is not None:
                pts=pts.filter(and_((Point.y-y*scale['L'])<tol,(y-Point.y*scale['L'])<tol))
            if z is not None:
                pts=pts.filter(and_((Point.z-z*scale['L'])<tol,(z-Point.z*scale['L'])<tol))
            names=[pt.name for pt in pts.all()]
            return names
        except Exception as e:
            log.info(str(e))
            return False
    
    def merge_points(self,tol=1e-3):
        """
        merge points within certain tolerance.
        
        params:
            tol: float, tolerance in in current unit.
        return:
            status of success.
        """
        try:
            pts=self.session.query(Point).order_by(Point.x,Point.y,Point.z).all()
            pt_map=dict([(pt.name,pt.name) for pt in pts])
            pts_to_rmv=[]
            for pti,ptj in zip(pts[:-1],pts[1:]):
                if (ptj.x-pti.x)**2+(ptj.y-pti.y)**2+(ptj.z-pti.z)**2<(tol*scale['L'])**2:
    #                pti.point_restraint.point_name=ptj.name
    #                pti.point_load.point_name=ptj.name
    #                pti.point_disp.point_name=ptj.name
    #                pti.point_mass.point_name=ptj.name
    #                pti.point_restraint+=ptj.point_restraint
    #                pti.point_load+=ptj.point_load
    #                pti.point_disp+=ptj.point_disp
    #                pti.point_mass+=ptj.point_mass
                    pt_map[ptj.name]=pt_map[pti.name]
                    pts_to_rmv.append(ptj)
                    
            frames=self.session.query(Frame).all()
            areas=self.session.query(Area).all()
            log.info(len(pts_to_rmv))
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
            pts=self.session.query(Point).all()
            log.info('merge elements %d'%len(pts))
            return True
        except Exception as e:
            log.info(str(e))
            return False
            
        
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
        frm=Frame()
        scale=self.scale()
        tol=self.session.query(Config).first().tolerance
        pt0=self.session.query(Point).filter(and_(
                    (Point.x-pt0_coor[0]*scale['L'])<tol,(pt0_coor[0]*scale['L']-Point.x)<tol,
                     (Point.y-pt0_coor[1]*scale['L'])<tol,(pt0_coor[1]*scale['L']-Point.y)<tol,
                      (Point.z-pt0_coor[2]*scale['L'])<tol,(pt0_coor[2]*scale['L']-Point.z)<tol)).first()
        if pt0==None:
            pt0_name=self.__add_point(pt0_coor[0]*scale['L'],pt0_coor[1]*scale['L'],pt0_coor[2]*scale['L'])
        else:
            pt0_name=pt0.name
            
        pt1=self.session.query(Point).filter(and_(
                    (Point.x-pt1_coor[0])<tol,(pt1_coor[0]-Point.x)<tol,
                     (Point.y-pt1_coor[1])<tol,(pt1_coor[1]-Point.y)<tol,
                      (Point.z-pt1_coor[2])<tol,(pt1_coor[2]-Point.z)<tol)).first()
        if pt1==None:
            pt1_name=self.__add_point(pt1_coor[0],pt1_coor[1],pt1_coor[2])
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
        
    def add_frame_batch(self,pt0_coors,pt1_coors,section):
        """
        Add batch of frame objects to model..
        param:
            pt0_coor: list of tuple, coordinate of the end point 0.
            pt1_coor: list of tuple, coordinate of the end point 1.
        return:
            list of str, the new frame's names.
        """
        assert(len(pt0_coors)==len(pt1_coors))
        names=[]
        frm_ends=[]
        scale=self.scale()
        for pt0,pt1 in zip(pt0_coors,pt1_coors):
            pt0_name=self.__add_point(pt0[0]*scale['L'],pt0[1]*scale['L'],pt0[2]*scale['L'])
            pt1_name=self.__add_point(pt1[0]*scale['L'],pt1[1]*scale['L'],pt1[2]*scale['L'])
            frm_ends.append((pt0_name,pt1_name))
        tol=self.session.query(Config).first().tolerance
        pts=self.session.query(Point).order_by(Point.x,Point.y,Point.z).all()
        pt_map=dict([(pt.name,pt.name) for pt in pts])
        pts_to_rmv=[]
        for pti,ptj in zip(pts[:-1],pts[1:]):
            if (ptj.x-pti.x)**2+(ptj.y-pti.y)**2+(ptj.z-pti.z)**2<tol**2:
                pt_map[ptj.name]=pt_map[pti.name]
                pts_to_rmv.append(ptj)
        log.info('rmv %d pts'%len(pts_to_rmv))
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
        self.session.flush()
        return names
        
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
            log.info(str(e))
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
            log.info(str(e))
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
            log.info(str(e))
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
            assert (len(load)==6 and (strain<=1 and strain>=0))
            frm=self.session.query(Frame).filter_by(name=frame).first()
            if frm is None:
                raise Exception("Frame doesn't exists.")
            ld=self.session.query(FrameLoadStrain).filter_by(frame_name=frame,loadcase_name=loadcase).first()
            if ld is None:
                ld=FrameLoadStrain()
            ld.frame_name=frame
            ld.loadcase_name=loadcase
            ld.strain=strain
            ld.loc=loc
            self.session.add(ld)
            return True
        except Exception as e:
            log.info(str(e))
            return False
            
    def set_frame_load_temperature(self,frame,loadcase,temperature):
        """
        params:
            point: str, name of point.
            loadcase: str, name of loadcase. 
            temperature: float, temperature in 1-1 axis.
        return:
            status of success.
        """
        try:
            assert (len(load)==6 and (strain<=1 and strain>=0))
            frm=self.session.query(Frame).filter_by(name=frame).first()
            if frm is None:
                raise Exception("Frame doesn't exists.")
            ld=self.session.query(FrameLoadTemperature).filter_by(frame_name=frame,loadcase_name=loadcase).first()
            if ld is None:
                ld=FrameLoadTemperature()
            ld.frame_name=frame
            ld.loadcase_name=loadcase
            ld.T=temperature
            ld.loc=loc
            self.session.add(ld)
            return True
        except Exception as e:
            log.info(str(e))
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
            frame name list.
        """
        try:
            frms=self.session.query(Frame).all()
            return [frm.name for frm in frms]
        except Exception as e:
            log.info(str(e))
            return False
    
    def get_frame_section(self,name):
        """
        params:
            name: str
        returns:
            frame section object if exist
        """
        pass
    
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
            area=Area()
            scale=self.scale()
            tol=self.session.query(Config).first().tolerance
            
            pt0=self.session.query(Point).filter(and_(
                        (Point.x-pt0_coor[0]*scale['L'])<tol,(pt0_coor[0]*scale['L']-Point.x)<tol,
                         (Point.y-pt0_coor[1]*scale['L'])<tol,(pt0_coor[1]*scale['L']-Point.y)<tol,
                          (Point.z-pt0_coor[2]*scale['L'])<tol,(pt0_coor[2]*scale['L']-Point.z)<tol)).first()
            if pt0==None:
                pt0_name=self.__add_point(pt0_coor[0],pt0_coor[1],pt0_coor[2])
            else:
                pt0_name=pt0.name
                
            pt1=self.session.query(Point).filter(and_(
                        (Point.x-pt1_coor[0]*scale['L'])<tol,(pt1_coor[0]*scale['L']-Point.x)<tol,
                         (Point.y-pt1_coor[1]*scale['L'])<tol,(pt1_coor[1]*scale['L']-Point.y)<tol,
                          (Point.z-pt1_coor[2]*scale['L'])<tol,(pt1_coor[2]*scale['L']-Point.z)<tol)).first()
            if pt1==None:
                pt1_name=self.__add_point(pt1_coor[0],pt1_coor[1],pt1_coor[2])
            else:
                pt1_name=pt1.name
                
            pt2=self.session.query(Point).filter(and_(
                        (Point.x-pt2_coor[0]*scale['L'])<tol,(pt2_coor[0]*scale['L']-Point.x)<tol,
                         (Point.y-pt2_coor[1]*scale['L'])<tol,(pt2_coor[1]*scale['L']-Point.y)<tol,
                          (Point.z-pt2_coor[2]*scale['L'])<tol,(pt2_coor[2]*scale['L']-Point.z)<tol)).first()
            if pt2==None:
                pt2_name=self.__add_point(pt2_coor[0],pt2_coor[1],pt2_coor[2])
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
                    pt3_name=self.__add_point(pt0_coor[0],pt0_coor[1],pt0_coor[2])
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
                area.name=frm.uuid
            self.session.add(area)
            return area.name
        except Exception as e:
            log.info(e)
            return False

    def mesh(self):
        femodel=self.fe_model
        points=self.session.query(Point).all()
        frames=self.session.query(Frame).all()
        areas=self.session.query(Area).all()
        pn_map={} #item-item map, one point to one node
        fb_map={} #item-list map, one frame can be meshed to many beams
        am_map={} #item-list map, one area can be meshed to many membranes
        ap_map={} #item-list map, one area can be meshed to many plates
        as_map={} #item-list map, one area can be meshed to many shells
        
        for pt in points:
            res=femodel.add_node(pt.x,pt.y,pt.z)
            pn_map[pt.name]=res
        for frm in frames:
            
            node0=pn_map[frm.pt0_name]
            node1=pn_map[frm.pt1_name]
            E=frm.section.material.isotropic_elastic.E
            mu=frm.section.material.isotropic_elastic.mu
            A=frm.section.A
            J=frm.section.J
            I2=frm.section.I2
            I3=frm.section.I3
            rho=frm.section.material.rho
            
            if frm.order=='01':
                res=femodel.add_beam(node0,node1,E, mu, A, I2, I3, J, rho)
            elif frm.order=='10':
                res=femodel.add_beam(node1,node0,E, mu, A, I2, I3, J, rho)
            fb_map[frm.name]=[res]
        for area in areas:
            am_map=None
            ap_map=None
            as_map=None
            pass
        
        restraints=self.session.query(PointRestraint).all()
        for res in restraints:
            disp=[0 if res.u1 else None,
                  0 if res.u2 else None,
                  0 if res.u3 else None,
                  0 if res.r1 else None,
                  0 if res.r2 else None,
                  0 if res.r3 else None]
            femodel.set_node_displacement(pn_map[res.point_name],disp)
                
        self.pn_map=pn_map
        self.fb_map=fb_map
        self.am_map=am_map
        self.ap_map=ap_map
        self.as_map=as_map

    def apply_load(self,lc):        
        pn_map=self.pn_map
        fb_map=self.fb_map
        am_map=self.am_map
        ap_map=self.ap_map
        as_map=self.as_map

        loadcase=self.session.query(LoadCase).filter_by(name=lc).first()
        
        point_loads=self.session.query(PointLoad).filter_by(loadcase_name=lc).all()
        frame_load_distributeds=self.session.query(FrameLoadDistributed).filter_by(loadcase_name=lc).all()
        frame_load_concentrateds=self.session.query(FrameLoadConcentrated).filter_by(loadcase_name=lc).all()
        frame_load_strains=self.session.query(FrameLoadStrain).filter_by(loadcase_name=lc).all()
        frame_load_temperatures=self.session.query(FrameLoadTemperature).filter_by(loadcase_name=lc).all()  
        area_load_to_frames=self.session.query(AreaLoadToFrame).filter_by(loadcase_name=lc).all()
        
        for load in point_loads:
            self.fe_model.set_node_force(pn_map[load.point_name],
                                         [load.u1,
                                          load.u2,
                                          load.u3,
                                          load.r1,
                                          load.r2,
                                          load.r3],append=True)
        
        for load in frame_load_distributeds:
            pass
        
        for load in frame_load_concentrateds:
            pass
        
        for load in frame_load_strains:
            pass
        
        for load in frame_load_temperatures:
            pass
        
        for load in area_load_to_frames:
            pass
        
        #self weight
        for beam in self.fe_model.beams.values():
            f=-beam.mass*9.81/2*loadcase.weight_factor
            self.fe_model.set_node_force(beam.nodes[0].hid,[0,0,f,0,0,0],append=True)
            self.fe_model.set_node_force(beam.nodes[1].hid,[0,0,f,0,0,0],append=True)
            
    def run(self,lcs):
        """
        Run the model with loadcases
        params:
            lcs: list of str, specify load cases to run.
        return:
            None.
        """
        if not self.fe_model.is_assembled:
            log.info('Mesh model...')
            self.mesh()
            self.fe_model.assemble_KM()
            self.fe_model.assemble_boundary(mode='KM')
        try:
            for lc in lcs:
                loadcase=self.session.query(LoadCase).filter_by(name=lc).first()
                if loadcase.case_type=='static-linear':
                    log.info('Solving static linear case %s...'%lc)
                    self.apply_load(lc)
                    self.fe_model.assemble_f()
                    self.fe_model.assemble_boundary(mode='f')
                    solve_linear(self.fe_model)
                    #write disp
                    for pt in self.session.query(Point).all():
                        hid=self.pn_map[pt.name]
                        rst=ResultPointDisplacement()
                        rst.point_name=pt.name
                        rst.loadcase_name=lc
                        disp=self.fe_model.resolve_node_disp(hid)
                        (rst.u1,rst.u2,rst.u3,rst.r1,rst.r2,rst.r3)=tuple(disp)
                        self.session.add(rst)
                    #write reaction
                    for res in self.session.query(PointRestraint).all():
                        hid=self.pn_map[res.point_name]
                        rst=ResultPointReaction()
                        rst.point_name=res.point_name
                        rst.loadcase_name=lc
                        reac=self.fe_model.resolve_node_reaction(hid)
                        (rst.p1,rst.p2,rst.p3,rst.m1,rst.m2,rst.m3)=tuple(reac)
                        self.session.add(rst)
                    #write beam force
                    for frm in self.session.query(Frame).all():
                        hids=self.fb_map[frm.name]
                        for i in range(len(hids)):
                            hid=hids[i]
                            rst=ResultFrameForce()
                            rst.frame_name=frm.name
                            rst.loadcase_name=lc
                            rst.segment=i
                            f=self.fe_model.resolve_beam_force(hid)
                            (rst.p01,rst.p02,rst.p03,rst.m01,rst.m02,rst.m03)=tuple(f[:6])
                            (rst.p11,rst.p12,rst.p13,rst.m11,rst.m12,rst.m13)=tuple(f[6:])
                            self.session.add(rst)
                    self.session.commit()
                    log.info('Finished case %s.'%lc)
                elif loadcase.case_type=='modal':
                    log.info('Solving modal case %s...'%lc)
                    solve_modal(self.fe_model,k=loadcase.loadcase_modal_setting.modal_num)
                    #write period
                    _order=1
                    for omega in self.fe_model.omega_:
                        rst=ResultModalPeriod()
                        rst.order=_order
                        rst.loadcase_name=lc
                        rst.omega=omega
                        rst.period=2*3.1415926535897932384626/omega
                        rst.frequency=1/(2*3.1415926535897932384626/omega)
                        self.session.add(rst)
                        _order+=1

                    #write disp
                    for pt in self.session.query(Point).all():
                        for o in range(1,_order):
                            hid=self.pn_map[pt.name]
                            rst=ResultModalDisplacement()
                            rst.point_name=pt.name
                            rst.loadcase_name=lc
                            rst.order=o
                            disp=self.fe_model.resolve_modal_displacement(hid,o)
                            (rst.u1,rst.u2,rst.u3,rst.r1,rst.r2,rst.r3)=tuple(disp)
                            self.session.add(rst)
                        
                    self.session.commit()
                    log.info('Finished case %s.'%lc)
                else:
                    pass
        except Exception as e:
            log.info(str(e))
            self.session.close()
            
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
        
    def import_dxf(self,dxf_file,layers=[]):
        """
        Import geometry model from dxf file.
        
        params:
            dxf_file: str, file name with path to import.
            layers: list-like, str, layers to import. not available now.
        return:
            list of name of imported members.
        """
        try:
            assert(dxf_file[-4:]=='.dxf')
            dwg = ezdxf.readfile(dxf_file)
            pt0=[]
            pt1=[]
            frm_sec=self.session.query(FrameSection).first()
            modelspace = dwg.modelspace()
            for e in modelspace:
                if e.dxftype() == 'LINE':
                    pt0.append(e.dxf.start)
                    pt1.append(e.dxf.end)
            frames=self.add_frame_batch(pt0,pt1,frm_sec.name)
            log.info("Imported %d frames from file %s"%(len(frames),dxf_file))
            return frames
        except Exception as e:
            log.info(str(e))
            return False
        
    def export_dxf(self,path,filename,overwrite=False):
        """
        Export geometry model from dxf file.
        
        params:
            path: str, path to export.
            filename: str, filename to save.
            [overwrite]: optional, bool, if True, will overwrite the exist file.
        return:
            list of name of imported members.
        """
        assert(os.path.exists(path) and filename[-4:]=='.dxf')
        dxf_file=os.path.join(path,filename)
        if os.path.exists(dxf_file) and overwrite==False:
            raise Exception('File already exists, please use another name or set overwrite to True.')
        dwg = ezdxf.new('R2010')
        modelspace = dwg.modelspace()
        frames=self.session.query(Frame).all()
        scale=self.scale()
        for frm in frames:
            pt0=frm.pt0
            pt1=frm.pt1
            modelspace.add_line((pt0.x/scale['L'],pt0.y/scale['L'],pt0.z/scale['L']), (pt1.x,pt1.y,pt1.z))  # add a LINE entity
        dwg.saveas(os.path.join(path,dxf_file))
        
