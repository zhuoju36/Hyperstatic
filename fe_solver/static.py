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
import Logger as log

def solve_linear(model):
    log.info('solving problem with %d DOFs...'%model.DOF)
    K_,f_=model.K_,model.f_
    delta,info=sl.gmres(K_,f_.toarray())
    model.is_solved=True
    log.info('Done!')
    return delta.reshape((model.node_count*6,1))

def solve_modal(model,k:int):
    """
    model: FEModel.
    k: number of modes to extract.
    """
    log.info('Solving eigen modes...')
    K_,M_=model.K_,model.M_
    omega2s,modes = sl.eigsh(K_,k,M_,which='SM')
    periods=2*np.pi/np.sqrt(omega2s)
    delta = modes/np.sum(modes,axis=0)
    model.is_solved=True
    log.info('Done!')
    return periods.reshape((k,1)),delta
    
def solve_2nd(model):
    pass

def solve_3rd(model):
    pass

def solve_push_over(model):
    pass

def solve_buckling():
    pass
    