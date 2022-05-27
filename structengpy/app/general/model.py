# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 19:52:26 2018

@author: HZJ
@E-mail: zhuoju36@hotmail.com
"""

from types import MethodType

from .orm import Config,LoadCase,Point,Frame,Area,\
PointLoad,PointRestraint,\
FrameLoadDistributed,FrameLoadConcentrated,FrameLoadTemperature,FrameLoadStrain,\
AreaLoadToFrame,\
ResultModalPeriod,ResultPointDisplacement,ResultPointReaction,ResultFrameForce,ResultModalDisplacement

from fe_model import Model as FEModel

from fe_solver.static import solve_linear
from fe_solver.dynamic import solve_modal
from model_io import dxf
from . import db
from . import project
from . import material
from . import frame_section
from . import area_section
from . import loadcase
from . import combination
from . import point
from . import frame
from . import area
from . import curve
from . import result

import logger

class Model():
    def __init__(self):
        self.locked=False
        self.session=None
        self.fe_model=FEModel()
        
        #database
        self.open=MethodType(db.open,self)
        self.create=MethodType(db.create,self)
        self.save=MethodType(db.save,self)
        self.close=MethodType(db.close,self)
        
        #project configuration
        self.get_project_name=MethodType(project.get_project_name,self)
        self.get_author=MethodType(project.get_author,self)
        self.get_description=MethodType(project.get_description,self)    
        self.get_tolerance=MethodType(project.get_tolerance,self)
        self.get_unit=MethodType(project.get_unit,self)
        self.set_project_name=MethodType(project.set_project_name,self)
        self.set_author=MethodType(project.set_author,self)
        self.set_description=MethodType(project.set_description,self)    
        self.set_tolerance=MethodType(project.set_tolerance,self)
        self.set_unit=MethodType(project.set_unit,self)
        
        #material
        self.add_material=MethodType(material.add_material,self)
        self.add_material_quick=MethodType(material.add_material_quick,self)
        self.get_material_names=MethodType(material.get_material_names,self)
        self.get_material_isotropic_elastic=None
        self.set_material_name=MethodType(material.set_material_name,self)
        self.set_material_isotropic_elastic=MethodType(material.set_material_isotropic_elastic,self)
        self.delete_material=MethodType(material.delete_material,self)
        
        #point
        self.add_point=MethodType(point.add_point,self)
        self.get_point_coordinate=MethodType(point.get_point_coordinate,self)
        self.get_point_name_by_coor=MethodType(point.get_point_name_by_coor,self)
        self.get_point_names=MethodType(point.get_point_names,self)
        self.set_point_name=MethodType(point.set_point_name,self)
        self.set_point_coordinate=MethodType(point.set_point_coordinate,self)
        self.set_mass_sources=MethodType(point.set_mass_sources,self)
        self.set_point_load=MethodType(point.set_point_load,self)
        self.set_point_mass=MethodType(point.set_point_mass,self)
        self.set_point_restraint=MethodType(point.set_point_restraint,self)
        self.set_point_restraint_batch=MethodType(point.set_point_restraint_batch,self)
        self.delete_point=MethodType(point.delete_point,self)
        
        #frame section
        self.add_frame_section=MethodType(frame_section.add_frame_section,self)
        self.add_frame_section_SD=MethodType(frame_section.add_frame_section_SD,self)
        self.add_frame_section_variate=MethodType(frame_section.add_frame_section_variate,self)
        self.get_frame_section_names=MethodType(frame_section.get_frame_section_names,self)
        self.get_frame_section_SD=None
        self.get_frame_section_variate=None
        self.set_frame_section_name=None
        self.set_frame_section_SD=None
        self.set_frame_section_variate=None
        self.delete_frame_section=MethodType(frame_section.delete_frame_section,self)
        
        #area section
        self.add_area_section=MethodType(area_section.add_area_section,self)
        self.add_area_section_layered=MethodType(area_section.add_area_section_layered,self)
        self.get_area_section_names=MethodType(area_section.get_area_section_names,self)
        self.get_area_section_layered=None
        self.set_area_section_name=None
        self.set_area_section_layered=None
        self.delete_area_section=MethodType(area_section.delete_area_section,self)
        
        #curve for loadcase
        self.add_curve=None
        self.add_spectrum=None
        self.set_curve=None
        self.set_spectrum=None
        self.delete_curve=None
        self.delete_spectrum=None
        
        #loadcase
        self.add_loadcase=MethodType(loadcase.add_loadcase,self)
        self.get_loadcase_names=MethodType(loadcase.get_loadcase_names,self)
        self.get_loadcase_2nd=None
        self.get_loadcase_2nd=None
        self.get_loadcase_buckling=None
        self.get_loadcase_modal=None
        self.get_loadcase_response_spectrum=None
        self.get_loadcase_static_linear=None
        self.get_loadcase_time_history=None
        self.set_loadcase_2nd=MethodType(loadcase.set_loadcase_2nd,self)
        self.set_loadcase_3rd=MethodType(loadcase.set_loadcase_3rd,self)
        self.set_loadcase_buckling=MethodType(loadcase.set_loadcase_buckling,self)
        self.set_loadcase_modal=MethodType(loadcase.set_loadcase_modal,self)
        self.set_loadcase_response_spectrum=MethodType(loadcase.set_loadcase_response_spectrum,self)
        self.set_loadcase_static_linear=MethodType(loadcase.set_loadcase_static_linear,self)
        self.set_loadcase_time_history=MethodType(loadcase.set_loadcase_time_history,self)
        self.delete_loadcase=MethodType(loadcase.delete_loadcase,self)
        
        #combination
        self.add_combination=None
        self.set_combination=None
        self.get_combination=None
        self.delete_combinataion=None
        
        #frame
        self.add_frame=MethodType(frame.add_frame,self)
        self.add_frame_batch=MethodType(frame.add_frame_batch,self)
        self.get_frame_end_coors=MethodType(frame.get_frame_end_coors,self)
        self.get_frame_end_names=MethodType(frame.get_frame_end_names,self)
        self.get_frame_names=MethodType(frame.get_frame_names,self)
        self.get_frame_names_by_points=MethodType(frame.get_frame_names_by_points,self)
        self.get_frame_section_attribute=MethodType(frame.get_frame_section_attribute,self)
        self.get_frame_dir_by_rotation=None
        self.get_frame_dir_by_vector=None
        self.get_frame_dir_by_point=None
        self.set_frame_name=None
        self.set_frame_section_attribute=None
        self.set_frame_dir_by_rotation=None
        self.set_frame_dir_by_vector=None
        self.set_frame_dir_by_point=None
        self.set_frame_mesh=None
        self.delete_frame=MethodType(frame.delete_frame,self)
        
        #area
        self.add_area=MethodType(area.add_area,self)
        self.add_area_batch=MethodType(area.add_area_batch,self)
        self.delete_area=MethodType(area.delete_area,self)
        
        #result
        self.add_result_point_displacement=None
        self.add_result_point_reaction=None
        self.add_result_frame_force=None
        self.add_result_period=None
        self.add_result_modal_mass=None
        self.add_result_modal_participate_factor=None
        self.get_result_point_displacement=MethodType(result.get_result_point_displacement,self)
        self.get_result_point_reaction=MethodType(result.get_result_point_reaction,self)
        self.get_result_frame_force=MethodType(result.get_result_frame_force,self)
        self.get_result_area_stress=None
        self.get_result_period=MethodType(result.get_result_period,self)
        self.combine_result_point_displacement=None
        self.combine_result_frame_force=None
        self.combine_result_area_stress=None
        self.clear_all_result=None
        
        #design/checking
        self.set_global_steel_check_settings=None
        self.set_global_concrete_rebar_settings=None
        self.set_frame_steel_check_settings=None
        self.set_frame_concrete_rebar_settings=None
        self.set_area_concrete_rebar_settings=None
        self.set_concrete_check_settings=None
        self.set_frame_check_settings=None
        self.set_frame_rebar_settings=None
        
        #io
        self.import_dxf=MethodType(dxf.import_dxf,self)
        self.export_dxf=MethodType(dxf.export_dxf,self)
        self.import_s2k=None
        self.export_s2k=None

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
        for _area in areas:
            nodes={
            0:pn_map[_area.pt0_name],
            1:pn_map[_area.pt1_name],
            2:pn_map[_area.pt2_name],
            3:pn_map[_area.pt3_name],
            }
            t=_area.section.t
            rho=_area.section.material.rho
            order=_area.order
            if len(order)==3:
                res=femodel.add_membrane3(nodes[eval(order[0])], nodes[eval(order[1])], nodes[eval(order[2])], t, E, mu, rho,)
                am_map[_area.name]=[res]
            if len(order)==4:
                res=femodel.add_membrane4(nodes[eval(order[0])], nodes[eval(order[1])], nodes[eval(order[2])],nodes[eval(order[3])], t, E, mu, rho,)
                am_map[_area.name]=[res]
        
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
                                         [load.u1 if load.u1!=None else 0,
                                          load.u2 if load.u2!=None else 0,
                                          load.u3 if load.u3!=None else 0,
                                          load.r1 if load.r1!=None else 0,
                                          load.r2 if load.r2!=None else 0,
                                          load.r3 if load.r3!=None else 0],append=True)
        
        for load in frame_load_distributeds:
#            self.fe_model.set_beam_force_by_frame_distributed()
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
            logger.info('Mesh model...')
            self.mesh()
            self.fe_model.assemble_KM()
            self.fe_model.assemble_boundary(mode='KM')
        try:
            for lc in lcs:
                loadcase=self.session.query(LoadCase).filter_by(name=lc).first()
                if loadcase is None:
                    raise Exception("Loadcase doen't exist!")
                if loadcase.case_type=='static-linear':
                    logger.info('Solving static linear case %s...'%lc)
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
                    logger.info('Finished case %s.'%lc)
                elif loadcase.case_type=='modal':
                    logger.info('Solving modal case %s...'%lc)
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
                        for od in range(1,_order):
                            hid=self.pn_map[pt.name]
                            rst=ResultModalDisplacement()
                            rst.point_name=pt.name
                            rst.loadcase_name=lc
                            rst.order=od
                            disp=self.fe_model.resolve_modal_displacement(hid,od)
                            (rst.u1,rst.u2,rst.u3,rst.r1,rst.r2,rst.r3)=tuple(disp)
                            self.session.add(rst)
                        
                    self.session.commit()
                    logger.info('Finished case %s.'%lc)
                else:
                    pass
        except Exception as e:
            logger.info(str(e))
            self.session.rollback()
            self.session.close()

        
