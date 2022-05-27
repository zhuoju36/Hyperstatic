# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 21:03:19 2018

@author: Dell
"""
import os

import ezdxf

import logger

def import_dxf(self,dxf_file,layers=[],types='fa',frm_sec=None,area_sec=None):
    """
    Import geometry self from dxf file.
    
    params:
        self: object self object
        dxf_file: str, file name with path to import.
        layers: list-like, str, layers to import. if an empty list is given, all layers will be imported.
        types: str, of f: frames, a:areas
        [frm_sec]: str, optional, default frame section
        [area_sec]: str, optional, default area section
    return:
        boolean, status of success, and list of name of imported members if successful.
    """
    try:
        assert(dxf_file[-4:]=='.dxf')
        dwg = ezdxf.readfile(dxf_file)
        frame_pts=[]
        area_pts=[]
        frm_sec=self.get_frame_section_names()[0] if frm_sec==None else frm_sec
        area_sec=self.get_area_section_names()[0] if area_sec==None else area_sec
        modelspace = dwg.modelspace()
        for e in modelspace:
            if layers!=[] and e.dxf.layer not in layers:
                continue
            if e.dxftype() == 'LINE' and 'f' in types:
                frame_pts.append((e.dxf.start,e.dxf.end))
            if e.dxftype() == '3DFACE' and 'a' in types:
                vtx0=e.dxf.vtx0
                vtx1=e.dxf.vtx1
                vtx2=e.dxf.vtx2
                vtx3=e.dxf.vtx3
                if vtx2!=vtx3:
                    area_pts.append((vtx0,vtx1,vtx2,vtx3))
                else:
                    area_pts.append((vtx0,vtx1,vtx2,None))
        result={}
        if len(frame_pts)!=0:
            res,frames=self.add_frame_batch(frame_pts,frm_sec)
            logger.info("Imported %d frames from file %s"%(len(frames),dxf_file))
            result['frames']=frames
        if len(area_pts)!=0:
            res,areas=self.add_area_batch(area_pts,area_sec)
            logger.info("Imported %d areas from file %s"%(len(areas),dxf_file))
            result['areas']=areas
        return True, result
    except Exception as e:
        logger.info(str(e))
        return False
    
def export_dxf(self,path,filename,overwrite=False):
    """
    Export geometry self from dxf file.
    
    params:
        self: object self object
        path: str, path to export.
        filename: str, filename to save.
        [overwrite]: optional, bool, if True, will overwrite the exist file.
    return:
        list of name of imported members.
    """
    try:
        assert(os.path.exists(path) and filename[-4:]=='.dxf')
        dxf_file=os.path.join(path,filename)
        if os.path.exists(dxf_file) and overwrite==False:
            raise Exception('File already exists, please use another name or set overwrite to True.')
        dwg = ezdxf.new('R2010')
        modelspace = dwg.modelspace()
        frames=self.get_frame_names()
        coors=[self.get_frame_end_coors(frm) for frm in frames]
        for coor in coors:
            modelspace.add_line(coor[:3], coor[3:])  # add a LINE entity
        dwg.saveas(os.path.join(path,dxf_file))
        return True
    except Exception as e:
        logger.info(str(e))
        return False 