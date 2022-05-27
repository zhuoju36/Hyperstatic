#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 13:14:15 2018

@author: hzj
"""

from .material import Metal,Concrete

def quick_material(name):
    """
    Get params of common materials.
    
    params:
        name: str, name of material.
    return:
        dictionary of material parameters. 
    """
    if name=='GB_Q345':
        return{
            'gamma':7849,
            'E':2e11,
            'mu':0.3,
            'alpha':1.17e-5,
            'fy':345e6
            }
    elif name=='GB_Q235':
        pass
        