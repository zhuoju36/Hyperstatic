# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 11:01:58 2016

@author: HZJ
"""

import tensorflow as tf
import numpy as np
import Model
from scipy import linalg
from scipy import sparse as sp
import scipy.sparse.linalg as sl

def solve_linear(model:Model.fem_model):
    K_bar,F_bar,index=model.eliminate_matrix()
    Dvec=model.D
    n_nodes=model.node_count
    try:
        #sparse matrix solution            
        delta_bar = linalg.solve(K_bar,F_bar)
        for i in delta_bar:
            print(i)
        delta = delta_bar
        #fill original displacement vector
        prev = 0
        for idx in index:
            gap=idx-prev
            if gap>0:
                delta=np.insert(delta,prev,[0]*gap)
            prev = idx + 1               
            if idx==index[-1] and idx!=n_nodes-1:
                delta = np.insert(delta,prev, [0]*(n_nodes*6-prev))
        delta += Dvec
    except Exception as e:
        print(e)
        return None
    model.is_solved=True
    return delta

def solve_modal(model:Model.fem_model,k:int):
    """
    model: FEM model.
    k: number of modes to extract.
    """
    
    K_bar,M_bar,F_bar,index=model.eliminate_matrix(True)
    Dvec=model.D
    n_nodes=model.node_count
    deltas=[]
    try:
        #general eigen solution, should be optimized later!!
        A=sp.csr_matrix(K_bar)
        B=sp.csr_matrix(M_bar)
        
        omega2s,modes = sl.eigsh(A,k,B)
        omegas=[]
        
        for omega2 in omega2s:
            omegas.append(2*3.14/np.sqrt(omega2))
            
        #extract vibration mode
        for mode in modes.T:
            delta_bar = mode/sum(mode)
            delta=delta_bar
            #fill original displacement vector
            prev = 0
            for idx in index:
                gap=idx-prev
                if gap>0:
                    delta=np.insert(delta,prev,[0]*gap)
                prev = idx + 1               
                if idx==index[-1] and idx!=n_nodes-1:
                    delta = np.insert(delta,prev, [0]*(n_nodes*6-prev))
            delta += Dvec
            deltas.append(delta)
        
    except Exception as e:
        print(str(e))
        return None
    model.is_solved=True
    return omegas, deltas

def solve_linear_tf(K,F):
    """
    Linearly solve the structure.
    """
    #Begin a new graph
    if 'sess' in locals() and sess is not None:
        print('Close interactive session')
        sess.close()
    
    with tf.device('/gpu:0'):
        K_ = tf.Variable(K,name="stiffness")
    
        F_ =  tf.Variable(np.array([F]),name="force")
        
    with tf.device('/cpu:0'):
        x=tf.matrix_solve(K_,tf.transpose(F_),name='displacement')
        sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
    sess.run(tf.global_variables_initializer())
    # run the op.
    delta=sess.run(x)
    return delta
    
def solve_2nd(K,F):
    pass

def solve_3rd(K,F):
    pass

def solve_modal_tf(K,F,M):
    pass

def solve_direct_integrate(K,F,M):
    pass


    
    
if __name__=='__main__':
    print(solve_linear())
    