# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 11:01:58 2016

@author: HZJ
"""
import numpy as np
from scipy import linalg
from scipy import sparse as spr
import scipy.sparse.linalg as sl

from fe_model import Model
import logger as log

def solve_linear(model):
    log.info('solving problem with %d DOFs...'%model.DOF)
    K_,f_=model.K_,model.f_
#    M_x = lambda x: sl.spsolve(P, x)
#    M = sl.LinearOperator((n, n), M_x)
    delta,info=sl.lgmres(K_,f_.toarray())
    model.is_solved=True
    log.info('Done!')
    model.d_=delta.reshape((model.node_count*6,1))
    model.r_=model.K*model.d_
    
def solve_2nd(model):
    pass

def solve_3rd(model):
    pass

def solve_push_over(model):
    pass

def solve_buckling():
    pass
    