#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 13:14:15 2018

@author: hzj
"""

from .material import Metal,Concrete

class GB_Q345(Metal):
    def __init__(self):
        name='GB_Q345'
        gamma=7849
        E=2e11
        mu=0.3
        alpha=1.17e-5
        fy=345e6
        super(GB_Q345,self).__init__(gamma,E,mu,alpha,fy,name)
        #design_properties
        self.fd={16:315,35:295} #according to thickness
        